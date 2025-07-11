import sqlite3
import re

# ---------- 1. Criação do banco de dados ----------
conn = sqlite3.connect("questoesGerais.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS questoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT,
        enunciado TEXT,
        alternativa_a TEXT,
        alternativa_b TEXT,
        alternativa_c TEXT,
        alternativa_d TEXT,
        fonte TEXT,
        gabarito TEXT
    )
''')

# ---------- 2. Função de leitura do arquivo ----------
def parse_questoes(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        linhas = file.readlines()

    questoes = []
    i = 0
    while i < len(linhas):
        # Número da questão
        numero = linhas[i].strip()
        i += 1

        # Enunciado (até encontrar a alternativa "a)")
        enunciado = ""
        while i < len(linhas) and not linhas[i].strip().lower().startswith("a)"):
            enunciado += linhas[i].strip() + " "
            i += 1

        # Alternativas
        alternativa_a = linhas[i].strip()[3:].strip()
        i += 1
        alternativa_b = linhas[i].strip()[3:].strip()
        i += 1
        alternativa_c = linhas[i].strip()[3:].strip()
        i += 1
        alternativa_d = linhas[i].strip()[3:].strip()
        i += 1

        # Fonte
        fonte = linhas[i].strip()
        i += 1

        # Gabarito
        gabarito_match = re.search(r'Gabarito:\s*[“"]?([a-dA-D])', linhas[i])
        gabarito = gabarito_match.group(1).lower() if gabarito_match else ""
        i += 1

        questoes.append((
            numero, enunciado.strip(), alternativa_a, alternativa_b, alternativa_c, alternativa_d, fonte, gabarito
        ))

    return questoes

# ---------- 3. Leitura e inserção ----------
questoes = parse_questoes("TGE APP 2025 GERAIS.txt")

cursor.executemany('''
    INSERT INTO questoes (numero, enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, fonte, gabarito)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', questoes)

conn.commit()
conn.close()

print("Importação concluída!")