# QUIZaPP sem timer (refatorado: janela 70% alinhada à direita)

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

# --------------------- Função para posicionar janela 70% direita ---------------------
def centralizar_direita(janela, largura_percent=70, altura_percent=80):
    janela.update_idletasks()
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    largura = int(largura_tela * (largura_percent / 100))
    altura = int(altura_tela * (altura_percent / 100))

    x = largura_tela - largura
    y = int((altura_tela - altura) / 2)

    janela.geometry(f"{largura}x{altura}+{x}+{y}")

# --------------------- Tela Inicial ---------------------
class TelaInicial:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz TGE APP 2025")
        centralizar_direita(self.master, 70, 80)
        self.master.configure(bg="#1e1e1e")

        tk.Label(master, text="Quiz TGE APP 2025", font=("Arial", 16, "bold"), bg="#1e1e1e", fg="#ffffff").pack(pady=20)
        tk.Label(master, text="Escolha a quantidade de questões:", font=("Arial", 12), bg="#1e1e1e", fg="#cccccc").pack(pady=10)

        self.quantidade = tk.IntVar(value=40)
        opcoes = [10, 20, 30, 40, 50]
        self.dropdown = ttk.Combobox(master, textvariable=self.quantidade, values=opcoes, font=("Arial", 11), state="readonly")
        self.dropdown.pack(pady=10)

        tk.Button(master, text="Iniciar Quiz", font=("Arial", 12, "bold"), bg="#333333", fg="#ffffff",
                  width=20, command=self.iniciar_quiz).pack(pady=20)

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

        self.root = tk.Tk()
        self.root.title("Quiz")
        centralizar_direita(self.root, 70, 80)
        self.root.configure(bg="#1e1e1e")

        self.progress = ttk.Progressbar(self.root, length=600, mode='determinate', maximum=len(self.questoes))
        self.progress.pack(pady=15)

        #novo metodo de exibição de perguntas
        self.pergunta_label = tk.Message(self.root, text="", width=800, font=("Arial", 14),
                                 bg="#1e1e1e", fg="#ffffff", justify="left")
        self.pergunta_label.pack(pady=20)

        #metodo antigo das questões, testando o novo
        #self.pergunta_label = tk.Label(self.root, text="", wraplength=650, justify="left", font=("Arial", 12), bg="#1e1e1e", fg="#ffffff")
        #self.pergunta_label.pack(pady=20)

        self.botoes = {}
        for letra in ['a', 'b', 'c', 'd']:
            btn = tk.Button(self.root, text="", width=60, font=("Arial", 11), bg="#333333", fg="#ffffff",
                            command=lambda l=letra: self.responder(l))
            btn.pack(pady=5)
            self.botoes[letra] = btn

        self.mostrar_questao()
        self.root.mainloop()

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
        if self.indice >= len(self.questoes):
            self.finalizar_quiz()
            return

        questao = self.questoes[self.indice]
        _, numero, enunciado, a, b, c, d, fonte, gabarito = questao
        self.gabarito_correto = gabarito

        self.pergunta_label.config(text=f"Pergunta {self.indice + 1}: {enunciado}\nFonte: {fonte}")
        self.botoes['a'].config(text=f"a) {a}")
        self.botoes['b'].config(text=f"b) {b}")
        self.botoes['c'].config(text=f"c) {c}")
        self.botoes['d'].config(text=f"d) {d}")

        self.progress['value'] = self.indice

    def responder(self, resposta):
        if resposta == self.gabarito_correto:
            self.acertos += 1
            messagebox.showinfo("Resultado", "✅ Correto!")
        else:
            messagebox.showerror("Resultado", f"❌ Errado. Resposta correta: {self.gabarito_correto}")
        self.proxima_questao()

    def proxima_questao(self):
        self.indice += 1
        self.mostrar_questao()

    def finalizar_quiz(self):
        messagebox.showinfo("Fim do Quiz", f"Você acertou {self.acertos} de {len(self.questoes)} questões.")
        self.root.destroy()

# --------------------- Início do Programa ---------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TelaInicial(root)
    root.mainloop()
