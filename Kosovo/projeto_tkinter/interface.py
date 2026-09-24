import tkinter as tk
from tkinter import messagebox, ttk
import dados
import validacoes


class LojaApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gerenciamento de Loja de Roupas")
        self.root.geometry("850x620")

        # Dados da aplicação
        try:
            self.produtos = dados.carregar_produtos()
        except Exception as e:
            messagebox.showerror("Erro de Inicialização", str(e))
            self.produtos = []

        self.carrinho = []
        self.id_selecionado = None  # Indica se estamos editando um produto
        self.alteracoes_pendentes = False

        self.criar_interface()
        self.atualizar_tabela_e_indicadores()

        # Intercepta o botão de fechar a janela (X)
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar_janela)

    def criar_interface(self):
        # Título Superior
        lbl_titulo = tk.Label(
            self.root,
            text="Sistema de Controle de Estoque e Vendas",
            font=("Arial", 14, "bold"),
        )
        lbl_titulo.pack(pady=5)

        # Container Geral
        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ================= ESQUERDA: FORMULÁRIO E CATALOGO =================
        frame_esquerda = tk.Frame(paned)
        frame_direita = tk.Frame(paned)
        paned.add(frame_esquerda)
        paned.add(frame_direita)

        # --- Subframe Formulário (Cadastro / Edição) ---
        frame_form = tk.LabelFrame(
            frame_esquerda, text=" Cadastro / Edição de Produto "
        )
        frame_form.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(frame_form, text="Nome:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=3
        )
        self.ent_nome = tk.Entry(frame_form, width=30)
        self.ent_nome.grid(row=0, column=1, padx=5, pady=3)
        self.ent_nome.bind("<Key>", self.marcar_alteracao)

        tk.Label(frame_form, text="Preço (R$):").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=3
        )
        self.ent_preco = tk.Entry(frame_form, width=15)
        self.ent_preco.grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)
        self.ent_preco.bind("<Key>", self.marcar_alteracao)

        tk.Label(frame_form, text="Estoque:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=3
        )
        self.ent_estoque = tk.Entry(frame_form, width=15)
        self.ent_estoque.grid(row=2, column=1, sticky=tk.W, padx=5, pady=3)
        self.ent_estoque.bind("<Key>", self.marcar_alteracao)

        # Botões do Formulário
        frame_btn_form = tk.Frame(frame_form)
        frame_btn_form.grid(row=3, column=0, columnspan=2, pady=5)

        self.btn_salvar = tk.Button(
            frame_btn_form, text="Salvar Produto", command=self.salvar_produto
        )
        self.btn_salvar.pack(side=tk.LEFT, padx=3)

        self.btn_limpar = tk.Button(
            frame_btn_form, text="Limpar / Novo", command=self.limpar_formulario
        )
        self.btn_limpar.pack(side=tk.LEFT, padx=3)

        self.btn_excluir = tk.Button(
            frame_btn_form,
            text="Excluir Selecionado",
            command=self.excluir_produto,
        )
        self.btn_excluir.pack(side=tk.LEFT, padx=3)

        # --- Subframe Busca e Pesquisa ---
        frame_busca = tk.Frame(frame_esquerda)
        frame_busca.pack(fill=tk.X, padx=5, pady=3)

        tk.Label(frame_busca, text="Pesquisar (Nome):").pack(
            side=tk.LEFT, padx=3
        )
        self.ent_busca = tk.Entry(frame_busca)
        self.ent_busca.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
        self.ent_busca.bind("<KeyRelease>", lambda e: self.filtrar_produtos())

        # --- Subframe Tabela (Treeview) ---
        frame_tabela = tk.LabelFrame(frame_esquerda, text=" Catálogo de Produtos ")
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        colunas = ("id", "nome", "preco", "estoque")
        self.tree_produtos = ttk.Treeview(
            frame_tabela, columns=colunas, show="headings", selectmode="browse"
        )
        self.tree_produtos.heading("id", text="ID")
        self.tree_produtos.heading("nome", text="Nome do Produto")
        self.tree_produtos.heading("preco", text="Preço (R$)")
        self.tree_produtos.heading("estoque", text="Estoque")

        self.tree_produtos.column("id", width=40, anchor=tk.CENTER)
        self.tree_produtos.column("nome", width=180)
        self.tree_produtos.column("preco", width=80, anchor=tk.E)
        self.tree_produtos.column("estoque", width=70, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(
            frame_tabela,
            orient=tk.VERTICAL,
            command=self.tree_produtos.yview,
        )
        self.tree_produtos.configure(yscroll=scrollbar.set)

        self.tree_produtos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_produtos.bind("<<TreeviewSelect>>", self.carregar_selecao)

        btn_add_carrinho = tk.Button(
            frame_esquerda,
            text="Adicionar ao Carrinho ->",
            command=self.adicionar_ao_carrinho,
        )
        btn_add_carrinho.pack(fill=tk.X, padx=5, pady=3)

        # ================= DIREITA: CARRINHO E INDICADORES =================
        # --- Resumo / Indicadores ---
        frame_resumo = tk.LabelFrame(
            frame_direita, text=" Indicadores do Catálogo "
        )
        frame_resumo.pack(fill=tk.X, padx=5, pady=5)

        self.lbl_ind_total_itens = tk.Label(
            frame_resumo, text="Total de Produtos: 0", anchor=tk.W
        )
        self.lbl_ind_total_itens.pack(fill=tk.X, padx=5, pady=2)

        self.lbl_ind_estoque_total = tk.Label(
            frame_resumo, text="Estoque Total (peças): 0", anchor=tk.W
        )
        self.lbl_ind_estoque_total.pack(fill=tk.X, padx=5, pady=2)

        self.lbl_ind_preco_medio = tk.Label(
            frame_resumo, text="Preço Médio: R$ 0.00", anchor=tk.W
        )
        self.lbl_ind_preco_medio.pack(fill=tk.X, padx=5, pady=2)

        # --- Carrinho de Compras ---
        frame_carrinho = tk.LabelFrame(frame_direita, text=" Carrinho de Venda ")
        frame_carrinho.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.lst_carrinho = tk.Listbox(frame_carrinho)
        self.lst_carrinho.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.lbl_total_carrinho = tk.Label(
            frame_carrinho, text="Total Venda: R$ 0.00", font=("Arial", 10, "bold")
        )
        self.lbl_total_carrinho.pack(pady=5)

        btn_remover_item = tk.Button(
            frame_carrinho,
            text="Remover Item do Carrinho",
            command=self.remover_do_carrinho,
        )
        btn_remover_item.pack(fill=tk.X, padx=5, pady=2)

        btn_finalizar = tk.Button(
            frame_carrinho,
            text="Finalizar Venda",
            command=self.finalizar_venda,
        )
        btn_finalizar.pack(fill=tk.X, padx=5, pady=5)

    # ================= REGRAS DE NEGÓCIO E EVENTOS =================

    def marcar_alteracao(self, event=None):
        """Marca que existem alterações não salvas no formulário."""
        self.alteracoes_pendentes = True

    def atualizar_tabela_e_indicadores(self, lista_exibicao=None):
        """Atualiza a Treeview e recalcula os indicadores coerentes."""
        # Limpa árvore
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)

        dados_tabela = (
            lista_exibicao if lista_exibicao is not None else self.produtos
        )

        for p in dados_tabela:
            self.tree_produtos.insert(
                "",
                tk.END,
                values=(p["id"], p["nome"], f"{p['preco']:.2f}", p["estoque"]),
            )

        # Indicadores gerais (sempre baseados na base completa)
        total_cadastrados = len(self.produtos)
        total_estoque = sum(p["estoque"] for p in self.produtos)
        preco_medio = (
            (sum(p["preco"] for p in self.produtos) / total_cadastrados)
            if total_cadastrados > 0
            else 0.0
        )

        self.lbl_ind_total_itens.config(
            text=f"Total de Produtos: {total_cadastrados}"
        )
        self.lbl_ind_estoque_total.config(
            text=f"Estoque Total (peças): {total_estoque}"
        )
        self.lbl_ind_preco_medio.config(
            text=f"Preço Médio: R$ {preco_medio:.2f}"
        )

    def filtrar_produtos(self):
        """Filtra os registros por nome com base no texto inserido."""
        termo = self.ent_busca.get().strip().lower()
        if not termo:
            self.atualizar_tabela_e_indicadores()
            return

        filtrados = [p for p in self.produtos if termo in p["nome"].lower()]
        self.atualizar_tabela_e_indicadores(lista_exibicao=filtrados)

    def carregar_selecao(self, event=None):
        """Carrega os dados da linha selecionada para o formulário de edição."""
        selecao = self.tree_produtos.selection()
        if not selecao:
            return

        item = self.tree_produtos.item(selecao[0])
        prod_id = item["values"][0]

        produto = next((p for p in self.produtos if p["id"] == prod_id), None)
        if produto:
            self.id_selecionado = produto["id"]
            self.ent_nome.delete(0, tk.END)
            self.ent_nome.insert(0, produto["nome"])

            self.ent_preco.delete(0, tk.END)
            self.ent_preco.insert(0, str(produto["preco"]))

            self.ent_estoque.delete(0, tk.END)
            self.ent_estoque.insert(0, str(produto["estoque"]))

            self.alteracoes_pendentes = False

    def limpar_formulario(self):
        """Limpa as caixas de entrada e reseta o modo de edição."""
        if self.alteracoes_pendentes:
            if not messagebox.askyesno(
                "Confirmação",
                "Existem edições não salvas no formulário. Deseja descartar?",
            ):
                return

        self.id_selecionado = None
        self.ent_nome.delete(0, tk.END)
        self.ent_preco.delete(0, tk.END)
        self.ent_estoque.delete(0, tk.END)

        # Desmarca seleção na tabela se houver
        selecao = self.tree_produtos.selection()
        if selecao:
            self.tree_produtos.selection_remove(selecao[0])

        self.alteracoes_pendentes = False

    def salvar_produto(self):
        """Cadastra um novo produto ou atualiza um existente após validações."""
        valido, res = validacoes.validar_produto_formulario(
            self.ent_nome.get(), self.ent_preco.get(), self.ent_estoque.get()
        )

        if not valido:
            messagebox.showerror("Erro de Validação", res)
            return

        try:
            if self.id_selecionado is None:
                # Novo Cadastro
                novo_id = dados.gerar_proximo_id(self.produtos)
                novo_prod = {
                    "id": novo_id,
                    "nome": res["nome"],
                    "preco": res["preco"],
                    "estoque": res["estoque"],
                }
                self.produtos.append(novo_prod)
                dados.salvar_produtos(self.produtos)
                dados.registrar_evidencia(
                    "cadastro", f"Cadastrado produto ID {novo_id}: {res['nome']}"
                )
                messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            else:
                # Edição de produto existente
                produto = next(
                    (p for p in self.produtos if p["id"] == self.id_selecionado),
                    None,
                )
                if produto:
                    produto["nome"] = res["nome"]
                    produto["preco"] = res["preco"]
                    produto["estoque"] = res["estoque"]
                    dados.salvar_produtos(self.produtos)
                    dados.registrar_evidencia(
                        "edicao",
                        f"Alterado produto ID {self.id_selecionado}: {res['nome']}",
                    )
                    messagebox.showinfo(
                        "Sucesso", "Produto atualizado com sucesso!"
                    )

            self.alteracoes_pendentes = False
            self.limpar_formulario()
            self.atualizar_tabela_e_indicadores()

        except Exception as e:
            messagebox.showerror("Erro ao Salvar", str(e))

    def excluir_produto(self):
        """Exclui o produto selecionado mediante confirmação explícita."""
        if self.id_selecionado is None:
            messagebox.showwarning(
                "Aviso",
                "Selecione um produto no catálogo para poder excluí-lo.",
            )
            return

        produto = next(
            (p for p in self.produtos if p["id"] == self.id_selecionado), None
        )
        if not produto:
            return

        # Requisito: Confirmar antes de excluir
        confirmar = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o produto '{produto['nome']}' (ID: {produto['id']})?\nEsta ação não poderá ser desfeita.",
        )

        if confirmar:
            try:
                self.produtos.remove(produto)
                dados.salvar_produtos(self.produtos)
                dados.registrar_evidencia(
                    "exclusao",
                    f"Excluído produto ID {produto['id']} - {produto['nome']}",
                )

                messagebox.showinfo("Sucesso", "Produto removido com sucesso!")
                self.limpar_formulario()
                self.atualizar_tabela_e_indicadores()
            except Exception as e:
                messagebox.showerror("Erro na Exclusão", str(e))

    # ================= CARRINHO E VENDAS =================

    def adicionar_ao_carrinho(self):
        selecao = self.tree_produtos.selection()
        if not selecao:
            messagebox.showwarning(
                "Aviso", "Selecione um produto na tabela para adicionar ao carrinho."
            )
            return

        item_id = self.tree_produtos.item(selecao[0])["values"][0]
        produto = next((p for p in self.produtos if p["id"] == item_id), None)

        if produto:
            if produto["estoque"] <= 0:
                messagebox.showerror(
                    "Estoque Insuficiente",
                    f"O produto '{produto['nome']}' está esgotado.",
                )
                return

            # Deduz do estoque temporariamente na memória
            produto["estoque"] -= 1
            self.carrinho.append(
                {
                    "id": produto["id"],
                    "nome": produto["nome"],
                    "preco": produto["preco"],
                }
            )

            self.atualizar_tabela_e_indicadores()
            self.atualizar_carrinho_gui()

    def remover_do_carrinho(self):
        selecao = self.lst_carrinho.curselection()
        if not selecao:
            messagebox.showwarning(
                "Aviso", "Selecione um item no carrinho para remover."
            )
            return

        idx = selecao[0]
        item_removido = self.carrinho.pop(idx)

        # Devolve o estoque na memória
        produto = next(
            (p for p in self.produtos if p["id"] == item_removido["id"]), None
        )
        if produto:
            produto["estoque"] += 1

        self.atualizar_tabela_e_indicadores()
        self.atualizar_carrinho_gui()

    def atualizar_carrinho_gui(self):
        self.lst_carrinho.delete(0, tk.END)
        total = 0.0

        for item in self.carrinho:
            self.lst_carrinho.insert(
                tk.END, f"{item['nome']} - R$ {item['preco']:.2f}"
            )
            total += item["preco"]

        self.lbl_total_carrinho.config(text=f"Total Venda: R$ {total:.2f}")

    def finalizar_venda(self):
        valido, msg = validacoes.validar_carrinho_venda(self.carrinho)
        if not valido:
            messagebox.showwarning("Aviso", msg)
            return

        try:
            # Grava alterações permanentes no JSON de dados
            dados.salvar_produtos(self.produtos)

            total = sum(p["preco"] for p in self.carrinho)
            detalhes_venda = f"Venda realizada. Total: R$ {total:.2f}\nItens:\n"
            for item in self.carrinho:
                detalhes_venda += f"- {item['nome']} (R$ {item['preco']:.2f})\n"

            dados.registrar_evidencia("venda", detalhes_venda)

            messagebox.showinfo(
                "Venda Concluída",
                f"Venda finalizada com sucesso!\nTotal: R$ {total:.2f}\nComprovante registrado em 'evidencias/'.",
            )

            self.carrinho.clear()
            self.atualizar_carrinho_gui()

        except Exception as e:
            messagebox.showerror("Erro ao Finalizar Venda", str(e))

    # ================= ENCERRAMENTO COM CONFIRMAÇÃO =================

    def ao_fechar_janela(self):
        """Solicita confirmação antes de sair caso existam alterações pendentes ou itens no carrinho."""
        if self.alteracoes_pendentes or self.carrinho:
            msg = "Existem alterações no formulário ou itens no carrinho que serão perdidos ao fechar.\nDeseja realmente sair?"
            if not messagebox.askyesno("Confirmar Saída", msg):
                return

        self.root.destroy()