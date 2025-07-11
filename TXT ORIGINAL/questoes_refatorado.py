import sqlite3
import re
from pathlib import Path
from typing import List, Tuple, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gerenciador de banco de dados para questões."""
    
    def __init__(self, db_path: str = "questoesGerais.db"):
        self.db_path = db_path
        self.conn = None
        
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()
        return self.conn.cursor()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
                logger.info("Transação commitada com sucesso")
            else:
                self.conn.rollback()
                logger.error(f"Erro na transação: {exc_val}")
            self.conn.close()
    
    def create_table(self):
        """Cria a tabela de questões se não existir."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL,
                enunciado TEXT NOT NULL,
                alternativa_a TEXT NOT NULL,
                alternativa_b TEXT NOT NULL,
                alternativa_c TEXT NOT NULL,
                alternativa_d TEXT NOT NULL,
                gabarito TEXT NOT NULL,
                fonte TEXT,
                UNIQUE(numero, fonte)
            )
        ''')
        logger.info("Tabela de questões criada/verificada")

class QuestaoParser:
    """Parser para extrair questões de arquivos de texto."""
    
    @staticmethod
    def extrair_gabarito(linha: str) -> str:
        """Extrai o gabarito de uma linha usando regex."""
        padroes = [
            r'Gabarito:\s*["""]?([a-dA-D])["""]?',
            r'Gabarito:\s*([a-dA-D])',
            r'([a-dA-D])\s*$'
        ]
        
        for padrao in padroes:
            match = re.search(padrao, linha)
            if match:
                return match.group(1).lower()
        
        logger.warning(f"Gabarito não encontrado na linha: {linha.strip()}")
        return ""
    
    @staticmethod
    def validar_questao(questao: Tuple) -> bool:
        """Valida se uma questão tem todos os campos necessários."""
        numero, enunciado, alt_a, alt_b, alt_c, alt_d, gabarito, fonte = questao
        
        campos_obrigatorios = [numero, enunciado, alt_a, alt_b, alt_c, alt_d, gabarito]
        
        if not all(campo.strip() for campo in campos_obrigatorios):
            logger.warning(f"Questão {numero} tem campos vazios")
            return False
            
        if gabarito.lower() not in ['a', 'b', 'c', 'd']:
            logger.warning(f"Questão {numero} tem gabarito inválido: {gabarito}")
            return False
            
        return True
    
    def parse_questoes(self, file_path: str) -> List[Tuple]:
        """
        Extrai questões do arquivo de texto.
        
        Args:
            file_path: Caminho para o arquivo de texto
            
        Returns:
            Lista de tuplas com dados das questões
        """
        arquivo = Path(file_path)
        
        if not arquivo.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        logger.info(f"Iniciando parse do arquivo: {file_path}")
        
        try:
            with open(arquivo, 'r', encoding='utf-8') as file:
                linhas = [linha.rstrip('\n\r') for linha in file.readlines()]
        except UnicodeDecodeError:
            # Tenta com encoding alternativo
            with open(arquivo, 'r', encoding='latin-1') as file:
                linhas = [linha.rstrip('\n\r') for linha in file.readlines()]
        
        # Remove seções entre separadores antes de processar
        linhas_limpas = self._remover_secoes_separadores(linhas)
        
        questoes = []
        i = 0
        questao_atual = 1
        
        while i < len(linhas_limpas):
            try:
                questao = self._parse_questao_individual(linhas_limpas, i)
                if questao:
                    questao_data, linhas_processadas = questao
                    
                    if self.validar_questao(questao_data):
                        questoes.append(questao_data)
                        logger.debug(f"Questão {questao_atual} processada com sucesso")
                    else:
                        logger.warning(f"Questão {questao_atual} inválida, ignorada")
                    
                    i += linhas_processadas
                    questao_atual += 1
                else:
                    i += 1
            except Exception as e:
                logger.error(f"Erro ao processar questão {questao_atual}: {e}")
                i += 1
        
        logger.info(f"Parse concluído: {len(questoes)} questões válidas encontradas")
        return questoes
    
    def _remover_secoes_separadores(self, linhas: List[str]) -> List[str]:
        """
        Remove todas as seções entre separadores ========== do arquivo.
        
        Args:
            linhas: Lista de linhas do arquivo original
            
        Returns:
            Lista de linhas sem as seções entre separadores
        """
        linhas_limpas = []
        i = 0
        
        while i < len(linhas):
            linha = linhas[i].strip()
            
            # Verifica se é uma linha separadora
            if linha.startswith('=========='):
                # Pula até encontrar a próxima linha separadora ou fim do arquivo
                i += 1
                while i < len(linhas) and not linhas[i].strip().startswith('=========='):
                    i += 1
                # Pula também a linha de fechamento se encontrou
                if i < len(linhas):
                    i += 1
            else:
                # Linha normal, mantém
                linhas_limpas.append(linhas[i])
                i += 1
        
        logger.info(f"Removidas {len(linhas) - len(linhas_limpas)} linhas de seções separadoras")
        return linhas_limpas
    
    def _parse_questao_individual(self, linhas: List[str], inicio: int) -> Optional[Tuple]:
        """
        Processa uma questão individual a partir de uma posição específica.
        
        Args:
            linhas: Lista de linhas do arquivo
            inicio: Índice da linha inicial
            
        Returns:
            Tupla com (dados_questao, linhas_processadas) ou None se inválida
        """
        i = inicio
        
        # Pula linhas vazias
        while i < len(linhas) and not linhas[i].strip():
            i += 1
        
        if i >= len(linhas):
            return None
        
        # Número da questão
        numero = linhas[i].strip()
        if not numero:
            return None
        i += 1
        
        # Enunciado (até encontrar alternativa "a)")
        enunciado_partes = []
        while i < len(linhas) and not self._is_alternativa_a(linhas[i]):
            if linhas[i].strip():
                enunciado_partes.append(linhas[i].strip())
            i += 1
        
        if not enunciado_partes:
            return None
        
        enunciado = " ".join(enunciado_partes)
        
        # Alternativas
        alternativas = []
        for letra in ['a)', 'b)', 'c)', 'd)']:
            if i >= len(linhas):
                return None
            
            linha = linhas[i].strip()
            if not linha.lower().startswith(letra):
                logger.warning(f"Esperada alternativa {letra}, encontrada: {linha}")
                return None
            
            alternativas.append(linha[2:].strip())
            i += 1
        
        # Gabarito
        if i >= len(linhas):
            return None
        
        gabarito = self.extrair_gabarito(linhas[i])
        i += 1
        
        # Fonte (opcional)
        fonte = ""
        if i < len(linhas) and linhas[i].strip():
            fonte = linhas[i].strip()
            i += 1
        
        questao_data = (numero, enunciado, *alternativas, gabarito, fonte)
        linhas_processadas = i - inicio
        
        return questao_data, linhas_processadas
    
    @staticmethod
    def _is_alternativa_a(linha: str) -> bool:
        """Verifica se a linha é uma alternativa 'a)'."""
        return linha.strip().lower().startswith("a)")

class QuestaoImporter:
    """Importador principal de questões."""
    
    def __init__(self, db_path: str = "questoesGerais.db"):
        self.db_manager = DatabaseManager(db_path)
        self.parser = QuestaoParser()
    
    def importar_arquivo(self, file_path: str) -> bool:
        """
        Importa questões de um arquivo para o banco de dados.
        
        Args:
            file_path: Caminho para o arquivo de texto
            
        Returns:
            True se importação foi bem-sucedida
        """
        try:
            questoes = self.parser.parse_questoes(file_path)
            
            if not questoes:
                logger.warning("Nenhuma questão válida encontrada no arquivo")
                return False
            
            with self.db_manager as cursor:
                cursor.executemany('''
                    INSERT OR REPLACE INTO questoes 
                    (numero, enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, gabarito, fonte)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', questoes)
                
                logger.info(f"Importadas {len(questoes)} questões com sucesso")
                return True
                
        except Exception as e:
            logger.error(f"Erro na importação: {e}")
            return False

def main():
    """Função principal."""
    arquivos = [
        "TXT ORIGINAL/TGE APP 2025 GERAIS.txt",
        "TGE APP 2025 GERAIS.txt"
    ]
    
    importer = QuestaoImporter()
    
    for arquivo in arquivos:
        if Path(arquivo).exists():
            logger.info(f"Processando arquivo: {arquivo}")
            
            if importer.importar_arquivo(arquivo):
                print(f"✅ Importação de '{arquivo}' concluída com sucesso!")
            else:
                print(f"❌ Erro na importação de '{arquivo}'")
            break
    else:
        logger.error("Nenhum arquivo encontrado nos caminhos especificados")
        print("❌ Nenhum arquivo encontrado")

if __name__ == "__main__":
    main()