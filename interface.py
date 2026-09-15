"""
Esta camada só trata da apresentação: lê o que o utilizador escreve, converte
para os tipos certos e chama as operações definidas em estruturas.py.

Tratamento de erros: todas as validações levantam ValueError com uma mensagem
já escrita para o utilizador, por isso cada acção só precisa de apanhar
ValueError e mostrar str(e). Erros internos do Python (por exemplo, o texto
"invalid literal for int()") nunca chegam ao ecrã.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from estruturas import (
    ATRIBUTOS,
    FORMATO_DATA,
    ListaProdutos,
    ListaVendas,
    Produto,
    analisar_data,
    formatar_valor,
)

# Fonte nativa do Tk em qualquer sistema operativo (Windows, macOS, Linux).
FONTE_DESTAQUE = ("TkDefaultFont", 11, "bold")


# ---------------------------------------------------------------------------
# CONVERSÃO DE TEXTO DO FORMULÁRIO
# ---------------------------------------------------------------------------

def texto_obrigatorio(texto, campo):
    if not texto.strip():
        raise ValueError(f"O campo '{campo}' é obrigatório.")
    return texto.strip()


def para_inteiro(texto, campo):
    try:
        return int(texto.strip())
    except ValueError:
        raise ValueError(f"O campo '{campo}' deve ser um número inteiro.") from None


def para_numero(texto, campo):
    try:
        return float(texto.strip().replace(",", "."))
    except ValueError:
        raise ValueError(
            f"O campo '{campo}' deve ser um número (ex.: 80 ou 80.50)."
        ) from None


# ---------------------------------------------------------------------------
# APLICAÇÃO
# ---------------------------------------------------------------------------

class AplicacaoPadaria:

    ATRIBUTOS_LABEL = {
        "codigo": "Código",
        "nome": "Nome",
        "categoria": "Categoria",
        "preco": "Preço",
        "quantidade": "Quantidade",
        "validade": "Validade",
    }

    def __init__(self, root):
        self.lista = ListaProdutos()
        self.lista_vendas = ListaVendas()
        self.label_para_atributo = {v: c for c, v in self.ATRIBUTOS_LABEL.items()}

        self.root = root
        self.root.title("Sistema de Gestão de Padaria")
        self.root.geometry("1100x650")
        self.root.minsize(900, 550)

        self._popular_exemplo()
        self._construir_layout()

    # ---------------- LAYOUT PRINCIPAL ----------------
    def _construir_layout(self):
        self.container = ttk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self._construir_sidebar()
        self._construir_area_conteudo()

    # ---------------- SIDEBAR (BARRA LATERAL) ----------------
    def _construir_sidebar(self):
        sidebar = ttk.Frame(self.container, width=200)
        sidebar.pack(side="left", fill="y", padx=(0, 2))
        sidebar.pack_propagate(False)

        ttk.Label(sidebar, text="Operações", font=FONTE_DESTAQUE).pack(
            pady=(10, 15), padx=10)

        operacoes = [
            ("Buscar Produto", self.acao_buscar_produto),
            ("Registar Venda", self.acao_registar_venda),
            ("Buscar (1 atributo)", self.acao_buscar_um_atributo),
            ("Buscar (2 atributos)", self.acao_buscar_dois_atributos),
            ("Eliminar por posição", self.acao_eliminar_posicao),
            ("Eliminar por código", self.acao_eliminar_codigo),
            ("Listar todos", self.acao_listar_todos),
            ("Listar por critério", self.acao_listar_criterio),
            ("Listar ordenado", self.acao_listar_ordenado),
        ]

        for texto, comando in operacoes:
            ttk.Button(sidebar, text=texto, command=comando).pack(
                fill="x", padx=8, pady=3)

    # ---------------- ÁREA DE CONTEÚDO ----------------
    def _construir_area_conteudo(self):
        area = ttk.Frame(self.container)
        area.pack(side="left", fill="both", expand=True)

        self._construir_formulario(area)
        self._construir_abas(area)

    # ---------------- FORMULÁRIO DE ENTRADA ----------------
    def _construir_formulario(self, parent):
        frame = ttk.LabelFrame(parent, text="Dados do Produto")
        frame.pack(fill="x", padx=10, pady=(10, 5))

        self.entradas = {}
        for i, atributo in enumerate(ATRIBUTOS):
            ttk.Label(frame, text=self.ATRIBUTOS_LABEL[atributo] + ":").grid(
                row=i // 3, column=(i % 3) * 2, sticky="e", padx=5, pady=5)
            entrada = ttk.Entry(frame, width=20)
            entrada.grid(row=i // 3, column=(i % 3) * 2 + 1, padx=5, pady=5)
            self.entradas[atributo] = entrada

        ttk.Label(frame, text="Validade no formato dd/mm/aaaa",
                  foreground="gray").grid(row=2, column=0, columnspan=6,
                                          sticky="w", padx=5, pady=(0, 5))

        # Botões que actuam sobre os dados do formulário ficam junto dele.
        botoes = ttk.Frame(frame)
        botoes.grid(row=3, column=0, columnspan=6, sticky="e", padx=5, pady=(0, 8))
        ttk.Button(botoes, text="Alterar (por código)",
                   command=self.acao_alterar).pack(side="right", padx=(6, 0))
        ttk.Button(botoes, text="Cadastrar",
                   command=self.acao_cadastrar).pack(side="right")

    # ---------------- ABAS INFERIORES (REGISTOS / VENDAS) ----------------
    def _construir_abas(self, parent):
        self.abas = ttk.Notebook(parent)
        self.abas.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # --- Aba Registos ---
        self.tab_registos = ttk.Frame(self.abas)
        self.abas.add(self.tab_registos, text="  Registos  ")

        self.tabela_registos = self._criar_tabela(
            self.tab_registos, ATRIBUTOS,
            [self.ATRIBUTOS_LABEL[a] for a in ATRIBUTOS])

        # --- Aba Vendas ---
        self.tab_vendas = ttk.Frame(self.abas)
        self.abas.add(self.tab_vendas, text="  Vendas  ")

        colunas_venda = ("data", "codigo", "nome", "quantidade", "preco_unit", "total")
        self.tabela_vendas = self._criar_tabela(
            self.tab_vendas, colunas_venda,
            ["Data", "Código", "Produto", "Qtd Solicitada", "Preço Unitário", "Total"],
            largura=130)

        # Resumo das vendas, por baixo da tabela
        resumo = ttk.Frame(self.tab_vendas)
        resumo.pack(fill="x", padx=5, pady=5)

        self.label_total_qtd = ttk.Label(resumo, text="Total Qtd: 0", font=FONTE_DESTAQUE)
        self.label_total_qtd.pack(side="left", padx=20)

        self.label_total_vendas = ttk.Label(resumo, text="Total Vendas: 0.00 MT",
                                            font=FONTE_DESTAQUE)
        self.label_total_vendas.pack(side="left", padx=20)

        ttk.Button(resumo, text="+ Registar Venda",
                   command=self.acao_registar_venda).pack(side="right", padx=20)

        self._atualizar_tabela_registos()
        self._atualizar_tabela_vendas()

    def _criar_tabela(self, parent, colunas, etiquetas, largura=120):
        """Cria uma Treeview com barra de deslocamento vertical."""
        tabela = ttk.Treeview(parent, columns=colunas, show="headings")
        for coluna, etiqueta in zip(colunas, etiquetas):
            tabela.heading(coluna, text=etiqueta)
            tabela.column(coluna, width=largura, anchor="center")
        tabela.pack(fill="both", expand=True, side="left")

        barra = ttk.Scrollbar(parent, orient="vertical", command=tabela.yview)
        tabela.configure(yscrollcommand=barra.set)
        barra.pack(fill="y", side="right")
        return tabela

    # ---------------- DADOS DE EXEMPLO ----------------
    def _popular_exemplo(self):
        exemplos = [
            (1, "Pão de forma", "Pão", 80.0, 50, "15/09/2026"),
            (2, "Bolo de chocolate", "Bolo", 350.0, 10, "12/09/2026"),
            (3, "Pastel de nata", "Doce", 45.0, 30, "13/09/2026"),
            (4, "Pão careca", "Pão", 15.0, 100, "14/09/2026"),
        ]
        for codigo, nome, categoria, preco, quantidade, validade in exemplos:
            self.lista.cadastrar(
                Produto(codigo, nome, categoria, preco, quantidade,
                        analisar_data(validade)))

        self.lista_vendas.registar_venda(1, "Pão de forma", 10, 80.0)
        self.lista_vendas.registar_venda(3, "Pastel de nata", 5, 45.0)
        self.lista_vendas.registar_venda(2, "Bolo de chocolate", 2, 350.0)

    # ---------------- ATUALIZAR TABELAS ----------------
    def _atualizar_tabela_registos(self, produtos=None):
        if produtos is None:
            produtos = self.lista.listar_todos()
        self.tabela_registos.delete(*self.tabela_registos.get_children())
        for p in produtos:
            self.tabela_registos.insert("", "end", values=tuple(
                formatar_valor(getattr(p, a)) for a in ATRIBUTOS))

    def _atualizar_tabela_vendas(self):
        self.tabela_vendas.delete(*self.tabela_vendas.get_children())
        # Travessia inversa: a venda mais recente aparece em primeiro lugar.
        for v in self.lista_vendas.listar_recentes_primeiro():
            self.tabela_vendas.insert("", "end", values=(
                v.data.strftime(FORMATO_DATA + " %H:%M"),
                v.codigo_produto, v.nome_produto, v.quantidade,
                f"{v.preco_unitario:.2f}", f"{v.total:.2f}",
            ))
        self.label_total_qtd.config(
            text=f"Total Qtd: {self.lista_vendas.total_quantidade()}")
        self.label_total_vendas.config(
            text=f"Total Vendas: {self.lista_vendas.total_vendas():.2f} MT")

    # ---------------- FORMULÁRIO ----------------
    def _ler_formulario(self):
        return {a: self.entradas[a].get().strip() for a in ATRIBUTOS}

    def _limpar_formulario(self):
        for entrada in self.entradas.values():
            entrada.delete(0, tk.END)

    def _preencher_formulario(self, produto):
        self._limpar_formulario()
        for atributo in ATRIBUTOS:
            self.entradas[atributo].insert(
                0, formatar_valor(getattr(produto, atributo)))

    # ---------------- DIÁLOGO GENÉRICO ----------------
    def _dialogo(self, titulo, campos):
        """Abre um diálogo modal e devolve {chave: valor}, ou None se cancelado.

        Cada campo é um tuplo (chave, etiqueta, tipo), com tipo em:
          "texto"    -> caixa de texto, devolve string
          "atributo" -> lista de atributos do produto, devolve o nome interno
          "opcao"    -> caixa de selecção, devolve True/False
        """
        janela = tk.Toplevel(self.root)
        janela.title(titulo)
        janela.resizable(False, False)
        janela.transient(self.root)

        widgets = {}
        primeira = None
        etiquetas_atributos = [self.ATRIBUTOS_LABEL[a] for a in ATRIBUTOS]

        for linha, (chave, etiqueta, tipo) in enumerate(campos):
            if tipo == "opcao":
                variavel = tk.BooleanVar()
                ttk.Checkbutton(janela, text=etiqueta, variable=variavel).grid(
                    row=linha, column=0, columnspan=2, padx=12, pady=6, sticky="w")
                widgets[chave] = variavel
                continue

            ttk.Label(janela, text=etiqueta + ":").grid(
                row=linha, column=0, padx=12, pady=6, sticky="e")

            if tipo == "atributo":
                widget = ttk.Combobox(janela, values=etiquetas_atributos,
                                      state="readonly", width=18)
            else:
                widget = ttk.Entry(janela, width=21)

            widget.grid(row=linha, column=1, padx=12, pady=6)
            widgets[chave] = widget
            if primeira is None:
                primeira = widget

        estado = {"confirmado": False}
        resultado = {}

        def confirmar(evento=None):
            for chave, widget in widgets.items():
                if isinstance(widget, tk.BooleanVar):
                    resultado[chave] = widget.get()
                elif isinstance(widget, ttk.Combobox):
                    # Converte a etiqueta visível no nome interno do atributo.
                    resultado[chave] = self.label_para_atributo.get(widget.get(), "")
                else:
                    resultado[chave] = widget.get().strip()
            estado["confirmado"] = True
            janela.destroy()

        ttk.Button(janela, text="Confirmar", command=confirmar).grid(
            row=len(campos), column=0, columnspan=2, pady=12)

        janela.bind("<Return>", confirmar)
        janela.bind("<Escape>", lambda e: janela.destroy())
        if primeira is not None:
            primeira.focus_set()

        janela.grab_set()
        self.root.wait_window(janela)

        return resultado if estado["confirmado"] else None

    def _mostrar_resultados(self, produtos):
        self._atualizar_tabela_registos(produtos)
        self.abas.select(self.tab_registos)
        if not produtos:
            messagebox.showinfo("Busca", "Nenhum produto encontrado.")

    # ---------------- AÇÕES ----------------
    def acao_buscar_produto(self):
        dados = self._dialogo("Buscar Produto", [("codigo", "Código do Produto", "texto")])
        if dados is None:
            return
        try:
            codigo = para_inteiro(dados["codigo"], "Código")
            produto = self.lista.buscar_por_codigo(codigo)
            if produto is None:
                messagebox.showinfo(
                    "Resultado", f"Nenhum produto encontrado com código {codigo}.")
                return
            self._preencher_formulario(produto)
            self._atualizar_tabela_registos([produto])
            self.abas.select(self.tab_registos)
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def acao_cadastrar(self):
        dados = self._ler_formulario()
        try:
            produto = Produto(
                codigo=para_inteiro(dados["codigo"], "Código"),
                nome=texto_obrigatorio(dados["nome"], "Nome"),
                categoria=texto_obrigatorio(dados["categoria"], "Categoria"),
                preco=para_numero(dados["preco"], "Preço"),
                quantidade=para_inteiro(dados["quantidade"], "Quantidade"),
                validade=analisar_data(dados["validade"]),
            )
            self.lista.cadastrar(produto)
            self._atualizar_tabela_registos()
            self.abas.select(self.tab_registos)
            self._limpar_formulario()
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso.")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def acao_buscar_um_atributo(self):
        self._buscar_por_atributos("Buscar por 1 atributo")

    def acao_listar_criterio(self):
        self._buscar_por_atributos("Listar por critério")

    def _buscar_por_atributos(self, titulo):
        dados = self._dialogo(titulo, [
            ("atributo", "Atributo", "atributo"),
            ("valor", "Valor", "texto"),
        ])
        if dados is None:
            return
        try:
            self._mostrar_resultados(
                self.lista.buscar_por_um_atributo(dados["atributo"], dados["valor"]))
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def acao_buscar_dois_atributos(self):
        dados = self._dialogo("Buscar por 2 atributos", [
            ("atributo1", "Atributo 1", "atributo"),
            ("valor1", "Valor 1", "texto"),
            ("atributo2", "Atributo 2", "atributo"),
            ("valor2", "Valor 2", "texto"),
        ])
        if dados is None:
            return
        try:
            self._mostrar_resultados(self.lista.buscar_por_dois_atributos(
                dados["atributo1"], dados["valor1"],
                dados["atributo2"], dados["valor2"]))
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def acao_alterar(self):
        dados = self._ler_formulario()
        try:
            codigo = para_inteiro(dados["codigo"], "Código")
            # Campos em branco ficam a None e são ignorados na alteração.
            novos_dados = {
                "nome": dados["nome"] or None,
                "categoria": dados["categoria"] or None,
                "preco": para_numero(dados["preco"], "Preço") if dados["preco"] else None,
                "quantidade": (para_inteiro(dados["quantidade"], "Quantidade")
                               if dados["quantidade"] else None),
                "validade": analisar_data(dados["validade"]) if dados["validade"] else None,
            }
            self.lista.alterar_por_codigo(codigo, novos_dados)
            self._atualizar_tabela_registos()
            self.abas.select(self.tab_registos)
            messagebox.showinfo("Sucesso", "Produto alterado com sucesso.")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def acao_eliminar_posicao(self):
        dados = self._dialogo("Eliminar por posição",
                              [("posicao", "Posição (1 = primeiro)", "texto")])
        if dados is None:
            return
        try:
            posicao = para_inteiro(dados["posicao"], "Posição")
            removido = self.lista.eliminar_por_posicao(posicao)
            self._atualizar_tabela_registos()
            self.abas.select(self.tab_registos)
            messagebox.showinfo("Sucesso", f"Produto '{removido.nome}' eliminado.")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def acao_eliminar_codigo(self):
        dados = self._dialogo("Eliminar por código", [("codigo", "Código", "texto")])
        if dados is None:
            return
        try:
            codigo = para_inteiro(dados["codigo"], "Código")
            removido = self.lista.eliminar_por_codigo(codigo)
            self._atualizar_tabela_registos()
            self.abas.select(self.tab_registos)
            messagebox.showinfo("Sucesso", f"Produto '{removido.nome}' eliminado.")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def acao_listar_todos(self):
        self._atualizar_tabela_registos()
        self.abas.select(self.tab_registos)

    def acao_listar_ordenado(self):
        dados = self._dialogo("Listar ordenado", [
            ("atributo", "Ordenar por", "atributo"),
            ("decrescente", "Ordem decrescente", "opcao"),
        ])
        if dados is None:
            return
        try:
            produtos = self.lista.listar_ordenado(dados["atributo"], dados["decrescente"])
            self._atualizar_tabela_registos(produtos)
            self.abas.select(self.tab_registos)
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def acao_registar_venda(self):
        dados = self._dialogo("Registar Venda", [
            ("codigo", "Código do Produto", "texto"),
            ("quantidade", "Quantidade", "texto"),
        ])
        if dados is None:
            return
        try:
            codigo = para_inteiro(dados["codigo"], "Código")
            quantidade = para_inteiro(dados["quantidade"], "Quantidade")
            if quantidade <= 0:
                raise ValueError("A quantidade deve ser maior que 0.")

            produto = self.lista.dar_baixa_stock(codigo, quantidade)
            venda = self.lista_vendas.registar_venda(
                codigo, produto.nome, quantidade, produto.preco)

            self._atualizar_tabela_registos()
            self._atualizar_tabela_vendas()
            self.abas.select(self.tab_vendas)
            messagebox.showinfo(
                "Sucesso",
                f"Venda registada: {quantidade}x {produto.nome} = {venda.total:.2f} MT")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
