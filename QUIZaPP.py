#QUIZaPP

import sqlite3
import random
import tkinter as tk
from tkinter import ttk, messagebox

# --------------------- Carrega questões dos bancos ---------------------
def carregar_questoes(banco):
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()
    cursor.execute('SELECT id, numero, enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, fonte, gabarito FROM questoes')
    questoes = cursor.fetchall()
    conn.close()
    return questoes

# --------------------- Configuração da janela ---------------------
def configurar_janela(janela, titulo="Quiz TGE APP 2025"):
    # Obter dimensões da tela
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    
    # Calcular dimensões da janela (70% da tela)
    largura_janela = int(largura_tela * 0.7)
    altura_janela = int(altura_tela * 0.7)
    
    # Calcular posição para alinhar à direita
    pos_x = largura_tela - largura_janela
    pos_y = int((altura_tela - altura_janela) / 2)
    
    janela.title(titulo)
    janela.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
    janela.configure(bg="#1e1e1e")
    
    return largura_janela, altura_janela

# --------------------- Tela Inicial ---------------------
class TelaInicial:
    def __init__(self, master):
        self.master = master
        self.largura, self.altura = configurar_janela(master)

        # Container principal centralizado
        main_frame = tk.Frame(master, bg="#1e1e1e")
        main_frame.pack(expand=True, fill='both')
        
        # Container para centralizar conteúdo
        center_frame = tk.Frame(main_frame, bg="#1e1e1e")
        center_frame.pack(expand=True)

        tk.Label(center_frame, text="Quiz TGE APP 2025", font=("Arial", 18, "bold"), 
                bg="#1e1e1e", fg="#ffffff").pack(pady=30)
        
        tk.Label(center_frame, text="Escolha a quantidade de questões:", 
                font=("Arial", 14), bg="#1e1e1e", fg="#cccccc").pack(pady=15)

        self.quantidade = tk.IntVar(value=40)
        opcoes = [10, 20, 30, 40, 50]
        self.dropdown = ttk.Combobox(center_frame, textvariable=self.quantidade, 
                                   values=opcoes, font=("Arial", 12), state="readonly", width=15)
        self.dropdown.pack(pady=15)

        tk.Button(center_frame, text="Iniciar Quiz", font=("Arial", 14, "bold"), 
                 bg="#333333", fg="#ffffff", width=20, height=2, 
                 command=self.iniciar_quiz).pack(pady=30)

    def iniciar_quiz(self):
        total = self.quantidade.get()
        if total <= 0:
            messagebox.showerror("Erro", "Escolha uma quantidade válida.")
            return
        self.master.destroy()
        QuizApp(total)

# --------------------- Quiz Principal ---------------------
class QuizApp:
    def __init__(self, total_questoes):
        self.total_questoes = total_questoes
        self.acertos = 0
        self.indice = 0
        self.questoes = self.preparar_questoes()
        self.quiz_ativo = True

        self.root = tk.Tk()
        self.largura, self.altura = configurar_janela(self.root, "Quiz TGE APP 2025")
        
        # Configurar o que acontece quando a janela é fechada
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_quiz)

        self.criar_interface()
        self.mostrar_questao()
        self.root.mainloop()

    def criar_interface(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#1e1e1e")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, length=self.largura-100, 
                                      mode='determinate', maximum=len(self.questoes))
        self.progress.pack(pady=20)

        # Label da pergunta
        self.pergunta_label = tk.Label(main_frame, text="", 
                                     wraplength=self.largura-100, 
                                     justify="left", 
                                     font=("Arial", 13), 
                                     bg="#1e1e1e", 
                                     fg="#ffffff")
        self.pergunta_label.pack(pady=30)

        # Frame para os botões
        botoes_frame = tk.Frame(main_frame, bg="#1e1e1e")
        botoes_frame.pack(fill='x', pady=20)

        # Criar botões de alternativas
        self.botoes = {}
        for letra in ['a', 'b', 'c', 'd']:
            btn = tk.Button(botoes_frame, text="", 
                           font=("Arial", 12), 
                           bg="#333333", 
                           fg="#ffffff",
                           wraplength=self.largura-150,
                           justify="left",
                           anchor="w",
                           padx=15,
                           pady=8,
                           command=lambda l=letra: self.responder(l))
            btn.pack(pady=8, padx=30, fill="x")
            self.botoes[letra] = btn

    def preparar_questoes(self):
        especificas = carregar_questoes('questoesEspecificas.db')
        gerais = carregar_questoes('questoesGerais.db')
        random.shuffle(especificas)
        random.shuffle(gerais)

        num_especificas = int(self.total_questoes * 0.6)
        num_gerais = self.total_questoes - num_especificas

        selecionadas = especificas[:num_especificas] + gerais[:num_gerais]
        random.shuffle(selecionadas)
        return selecionadas

    def mostrar_questao(self):
        if not self.quiz_ativo:
            return
            
        if self.indice >= len(self.questoes):
            self.finalizar_quiz()
            return

        questao = self.questoes[self.indice]
        _, numero, enunciado, a, b, c, d, fonte, gabarito = questao
        self.gabarito_correto = gabarito

        self.pergunta_label.config(text=f"Pergunta {self.indice + 1} de {len(self.questoes)}: {enunciado}\n\nFonte: {fonte}")
        
        self.botoes['a'].config(text=f"A) {a}")
        self.botoes['b'].config(text=f"B) {b}")
        self.botoes['c'].config(text=f"C) {c}")
        self.botoes['d'].config(text=f"D) {d}")

        self.progress['value'] = self.indice

    def responder(self, resposta):
        if not self.quiz_ativo:
            return
            
        if resposta == self.gabarito_correto:
            self.acertos += 1
            messagebox.showinfo("Resultado", "✅ Correto!")
        else:
            messagebox.showerror("Resultado", f"❌ Errado. Resposta correta: {self.gabarito_correto}")
        self.proxima_questao()

    def proxima_questao(self):
        if not self.quiz_ativo:
            return
        self.indice += 1
        self.mostrar_questao()

    def finalizar_quiz(self):
        if not self.quiz_ativo:
            return
            
        self.quiz_ativo = False
        
        percentual = (self.acertos / len(self.questoes)) * 100
        resultado = f"Quiz Finalizado!\n\n"
        resultado += f"Você acertou {self.acertos} de {len(self.questoes)} questões.\n"
        resultado += f"Percentual de acerto: {percentual:.1f}%"
        
        if percentual >= 70:
            resultado += "\n\n🎉 Parabéns! Excelente desempenho!"
        elif percentual >= 50:
            resultado += "\n\n👍 Bom trabalho! Continue estudando!"
        else:
            resultado += "\n\n📚 Continue estudando para melhorar!"
        
        # Criar diálogo personalizado com opção de tentar novamente
        self.mostrar_resultado_final(resultado, percentual)

    def mostrar_resultado_final(self, resultado, percentual):
        # Criar janela personalizada para o resultado
        resultado_window = tk.Toplevel(self.root)
        resultado_window.title("Resultado Final")
        resultado_window.configure(bg="#1e1e1e")
        
        # Centralizar a janela de resultado
        largura_resultado = 400
        altura_resultado = 300
        pos_x = (self.root.winfo_screenwidth() - largura_resultado) // 2
        pos_y = (self.root.winfo_screenheight() - altura_resultado) // 2
        resultado_window.geometry(f"{largura_resultado}x{altura_resultado}+{pos_x}+{pos_y}")
        
        # Tornar a janela modal
        resultado_window.transient(self.root)
        resultado_window.grab_set()
        
        # Conteúdo da janela
        tk.Label(resultado_window, text=resultado, font=("Arial", 12), 
                bg="#1e1e1e", fg="#ffffff", justify="center").pack(pady=30)
        
        # Frame para os botões
        botoes_frame = tk.Frame(resultado_window, bg="#1e1e1e")
        botoes_frame.pack(pady=20)
        
        # Botão Tentar Novamente
        tk.Button(botoes_frame, text="Tentar Novamente", font=("Arial", 12, "bold"), 
                 bg="#4CAF50", fg="#ffffff", width=15, height=2,
                 command=lambda: self.tentar_novamente(resultado_window)).pack(side="left", padx=10)
        
        # Botão Sair
        tk.Button(botoes_frame, text="Sair", font=("Arial", 12, "bold"), 
                 bg="#f44336", fg="#ffffff", width=15, height=2,
                 command=lambda: self.sair_aplicacao(resultado_window)).pack(side="right", padx=10)

    def tentar_novamente(self, resultado_window):
        resultado_window.destroy()
        self.fechar_quiz()
        # Reiniciar o aplicativo
        root = tk.Tk()
        app = TelaInicial(root)
        root.mainloop()

    def sair_aplicacao(self, resultado_window):
        resultado_window.destroy()
        self.fechar_quiz()

    def fechar_quiz(self):
        self.quiz_ativo = False
        if self.root:
            self.root.destroy()

# --------------------- Início do Programa ---------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TelaInicial(root)
    root.mainloop()