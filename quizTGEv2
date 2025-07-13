# QUIZaPP sem timer (refatorado: alternativas completas e melhor layout)

import sqlite3
import random
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

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
        centralizar_direita(self.root, 75, 85)  # Aumentei um pouco para mais espaço
        self.root.configure(bg="#1e1e1e")

        self.criar_interface()
        self.mostrar_questao()
        self.root.mainloop()

    def criar_interface(self):
        """Cria a interface principal do quiz."""
        # Barra de progresso
        self.progress = ttk.Progressbar(self.root, length=700, mode='determinate', maximum=len(self.questoes))
        self.progress.pack(pady=15)

        # Frame principal com scroll
        self.main_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Canvas e scrollbar para scroll vertical
        self.canvas = tk.Canvas(self.main_frame, bg="#1e1e1e", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#1e1e1e")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack canvas e scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Contador de questões
        self.contador_label = tk.Label(self.scrollable_frame, text="", font=("Arial", 12, "bold"), 
                                      bg="#1e1e1e", fg="#00ff00")
        self.contador_label.pack(pady=(0, 10))

        # Área da pergunta
        self.pergunta_text = scrolledtext.ScrolledText(
            self.scrollable_frame, 
            height=6, 
            width=80,
            font=("Arial", 12),
            bg="#2d2d2d",
            fg="#ffffff",
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.pergunta_text.pack(pady=(0, 20), fill=tk.X)

        # Frame para as alternativas
        self.alternativas_frame = tk.Frame(self.scrollable_frame, bg="#1e1e1e")
        self.alternativas_frame.pack(fill=tk.X, pady=10)

        # Botões das alternativas (com texto expansível)
        self.botoes = {}
        for i, letra in enumerate(['a', 'b', 'c', 'd']):
            # Frame para cada alternativa
            alt_frame = tk.Frame(self.alternativas_frame, bg="#1e1e1e")
            alt_frame.pack(fill=tk.X, pady=5)

            # Botão da alternativa
            btn = tk.Button(
                alt_frame, 
                text=f"{letra.upper()}", 
                font=("Arial", 11, "bold"),
                bg="#333333", 
                fg="#ffffff",
                width=3,
                command=lambda l=letra: self.responder(l)
            )
            btn.pack(side=tk.LEFT, padx=(0, 10))

            # Texto da alternativa
            texto_alt = tk.Text(
                alt_frame,
                height=2,
                font=("Arial", 11),
                bg="#2d2d2d",
                fg="#ffffff",
                wrap=tk.WORD,
                state=tk.DISABLED,
                cursor="hand2"
            )
            texto_alt.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Permite clicar no texto para selecionar
            texto_alt.bind("<Button-1>", lambda e, l=letra: self.responder(l))

            self.botoes[letra] = {'button': btn, 'text': texto_alt}

        # Bind para scroll com mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Permite scroll com a roda do mouse."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def preparar_questoes(self):
        """Prepara e mistura as questões dos dois bancos."""
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
        """Exibe a questão atual na interface."""
        if self.indice >= len(self.questoes):
            self.finalizar_quiz()
            return

        questao = self.questoes[self.indice]
        _, numero, enunciado, a, b, c, d, fonte, gabarito = questao
        self.gabarito_correto = gabarito

        # Atualiza contador
        self.contador_label.config(text=f"Questão {self.indice + 1} de {len(self.questoes)}")

        # Atualiza pergunta
        pergunta_completa = f"Questão {numero}\n\n{enunciado}\n\nFonte: {fonte}"
        self.pergunta_text.config(state=tk.NORMAL)
        self.pergunta_text.delete(1.0, tk.END)
        self.pergunta_text.insert(1.0, pergunta_completa)
        self.pergunta_text.config(state=tk.DISABLED)

        # Atualiza alternativas
        alternativas = {'a': a, 'b': b, 'c': c, 'd': d}
        for letra, texto in alternativas.items():
            # Atualiza texto da alternativa
            self.botoes[letra]['text'].config(state=tk.NORMAL)
            self.botoes[letra]['text'].delete(1.0, tk.END)
            self.botoes[letra]['text'].insert(1.0, texto)
            self.botoes[letra]['text'].config(state=tk.DISABLED)

            # Ajusta altura do texto baseado no conteúdo
            linhas = len(texto.split('\n'))
            altura = max(2, min(6, linhas + 1))  # Mínimo 2, máximo 6 linhas
            self.botoes[letra]['text'].config(height=altura)

        # Atualiza barra de progresso
        self.progress['value'] = self.indice

        # Volta ao topo da página
        self.canvas.yview_moveto(0)

    def responder(self, resposta):
        """Processa a resposta do usuário."""
        if resposta == self.gabarito_correto:
            self.acertos += 1
            messagebox.showinfo("Resultado", "✅ Correto!")
        else:
            messagebox.showerror("Resultado", f"❌ Errado. Resposta correta: {self.gabarito_correto.upper()}")
        self.proxima_questao()

    def proxima_questao(self):
        """Avança para a próxima questão."""
        self.indice += 1
        self.mostrar_questao()

    def finalizar_quiz(self):
        """Finaliza o quiz e mostra o resultado."""
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
        
        messagebox.showinfo("Fim do Quiz", resultado)
        self.root.destroy()

# --------------------- Início do Programa ---------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TelaInicial(root)
    root.mainloop()