import tkinter as tk
from tkinter import messagebox, ttk
import dados
import validacoes


class LojaApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Loja de Roupas")
        self.root.geometry("700x480")

        self.produtos = dados.carregar_produtos()
        self.carrinho = []

        self.criar_interface()
        self.atualizar_tabela_produtos()

    def criar_interface(self):
        # Título
        tk.Label(
            self.root, text="Loja de Roupas", font=("Arial", 16, "bold")
        ).pack(pady=10)

        # Container Principal
        frame_conteudo = tk.Frame(self.root)
        frame_conteudo.pack(fill="both", expand=True, padx=10, pady=5)

        # --- TABELA DE PRODUTOS ---
        frame_produtos = tk.LabelFrame(
            frame_conteudo, text=" Catálogo ", font=("Arial", 10, "bold")
        )
        frame_produtos.pack(side="left", fill="both", expand=True, padx=5)

        colunas = ("id", "nome", "preco", "estoque")
        self.tabela_produtos = ttk.Treeview(
            frame_produtos, columns=colunas, show="headings", height=10
        )
        self.tabela_produtos.heading("id", text="ID")
        self.tabela_produtos.heading("nome", text="Nome")
        self.tabela_produtos.heading("preco", text="Preço (R$)")
        self.tabela_produtos.heading("estoque", text="Estoque")

        self.tabela_produtos.column("id", width=30)
        self.tabela_produtos.column("nome", width=120)
        self.tabela_produtos.column("preco", width=80)
        self.tabela_produtos.column("estoque", width=60)
        self.tabela_produtos.pack(fill="both", expand=True, padx=5, pady=5)

        btn_add = tk.Button(
            frame_produtos,
            text="Adicionar ao Carrinho",
            bg="#28a745",
            fg="white",
            command=self.adicionar_ao_carrinho,
        )
        btn_add.pack(pady=5)

        # --- SEÇÃO CARRINHO ---
        frame_carrinho = tk.LabelFrame(
            frame_conteudo, text=" Carrinho ", font=("Arial", 10, "bold")
        )
        frame_carrinho.pack(side="right", fill="both", expand=True, padx=5)

        self.lista_carrinho = tk.Listbox(frame_carrinho, height=10)
        self.lista_carrinho.pack(fill="both", expand=True, padx=5, pady=5)

        self.lbl_total = tk.Label(
            frame_carrinho,
            text="Total: R$ 0.00",
            font=("Arial", 11, "bold"),
            fg="#007bff",
        )
        self.lbl_total.pack(pady=5)

        btn_finalizar = tk.Button(
            frame_carrinho,
            text="Finalizar Venda",
            bg="#007bff",
            fg="white",
            command=self.finalizar_venda,
        )
        btn_finalizar.pack(pady=5)

    def atualizar_tabela_produtos(self):
        for item in self.tabela_produtos.get_children():
            self.tabela_produtos.delete(item)

        for p in self.produtos:
            self.tabela_produtos.insert(
                "",
                "end",
                values=(p["id"], p["nome"], f"{p['preco']:.2f}", p["estoque"]),
            )

    def adicionar_ao_carrinho(self):
        selecao = self.tabela_produtos.selection()
        if not selecao:
            messagebox.showwarning(
                "Aviso", "Selecione um produto no catálogo."
            )
            return

        item_id = self.tabela_produtos.item(selecao[0])["values"][0]
        produto = next((p for p in self.produtos if p["id"] == item_id), None)

        valido, msg = validacoes.validar_estoque_disponivel(produto)
        if not valido:
            messagebox.showerror("Erro", msg)
            return

        produto["estoque"] -= 1
        self.carrinho.append(produto)

        self.atualizar_tabela_produtos()
        self.atualizar_carrinho()

    def atualizar_carrinho(self):
        self.lista_carrinho.delete(0, tk.END)
        total = 0.0

        for item in self.carrinho:
            self.lista_carrinho.insert(
                tk.END, f"{item['nome']} - R$ {item['preco']:.2f}"
            )
            total += item["preco"]

        self.lbl_total.config(text=f"Total: R$ {total:.2f}")

    def finalizar_venda(self):
        valido, msg = validacoes.validar_carrinho_nao_vazio(self.carrinho)
        if not valido:
            messagebox.showwarning("Aviso", msg)
            return

        dados.salvar_produtos(self.produtos)

        messagebox.showinfo(
            "Sucesso",
            f"Venda realizada com sucesso!\n{self.lbl_total['text']}",
        )

        self.carrinho.clear()
        self.atualizar_carrinho()