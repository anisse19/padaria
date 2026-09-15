"""

Estrutura de dados: LISTA LIGADA (doubly linked list)

Cada nó guarda uma referência ao nó anterior e ao nó seguinte. Face à lista
simplesmente ligada, isso dá-nos:
  - inserção no fim em O(1), porque a lista mantém um ponteiro para a cauda
    (antes era preciso percorrer a lista toda até ao último nó);
  - remoção de um nó em O(1) quando já temos o nó, porque ele conhece o seu
    antecessor (antes era preciso arrastar uma variável "anterior");
  - travessia nos dois sentidos, usada para chegar a uma posição a partir da
    extremidade mais próxima e para listar as vendas da mais recente para a
    mais antiga.

Este módulo não importa tkinter: é lógica pura e pode ser testado sozinho.
"""

from dataclasses import dataclass, field, replace
from datetime import date, datetime

FORMATO_DATA = "%d/%m/%Y"

# Atributos de um produto que podem ser usados em buscas e ordenações.
ATRIBUTOS = ("codigo", "nome", "categoria", "preco", "quantidade", "validade")


# ---------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
#
# Convencção usada em todo o projecto: qualquer ValueError levantado aqui traz
# uma mensagem já escrita para o utilizador final, de modo a que a interface
# gráfica a possa mostrar directamente sem expor erros internos do Python.
# ---------------------------------------------------------------------------

def analisar_data(texto):
    """Converte 'dd/mm/aaaa' num objecto date."""
    try:
        return datetime.strptime(str(texto).strip(), FORMATO_DATA).date()
    except ValueError:
        raise ValueError(
            "O campo 'Validade' deve ter o formato dd/mm/aaaa (ex.: 15/09/2026)."
        ) from None


def validar_atributo(atributo):
    """Garante que o atributo existe antes de ser usado em getattr()."""
    if not atributo:
        raise ValueError("Escolha um atributo.")
    if atributo not in ATRIBUTOS:
        raise ValueError(f"Atributo inválido: '{atributo}'.")
    return atributo


def formatar_valor(valor):
    """Representação de um valor para mostrar ao utilizador."""
    if isinstance(valor, date):
        return valor.strftime(FORMATO_DATA)
    if isinstance(valor, float):
        return f"{valor:.2f}"
    return str(valor)


def valores_iguais(guardado, procurado):
    """Compara o valor guardado no produto com o texto escrito pelo utilizador.

    A comparação respeita o tipo do atributo, para que procurar o preço "80"
    encontre 80.0 e procurar a validade "15/09/2026" encontre a data
    correspondente.
    """
    procurado = str(procurado).strip()
    if isinstance(guardado, date):
        try:
            return guardado == analisar_data(procurado)
        except ValueError:
            return False
    if isinstance(guardado, (int, float)):
        try:
            return float(guardado) == float(procurado.replace(",", "."))
        except ValueError:
            return False
    return str(guardado).strip().lower() == procurado.lower()


def chave_ordenacao(valor):
    """Normaliza um valor para efeitos de comparação na ordenação."""
    return valor.lower() if isinstance(valor, str) else valor


# ---------------------------------------------------------------------------
# DADOS DO DOMÍNIO
#
# O produto e a venda são separados do nó: o nó é uma peça da estrutura de
# dados (guarda ligações), o produto é a informação do negócio. Assim a lista
# ligada fica genérica e serve para guardar produtos ou vendas.
# ---------------------------------------------------------------------------

@dataclass
class Produto:
    codigo: int
    nome: str
    categoria: str
    preco: float
    quantidade: int
    validade: date

    def __post_init__(self):
        """Valida o produto sempre que é criado ou alterado."""
        if not str(self.nome).strip():
            raise ValueError("O campo 'Nome' é obrigatório.")
        if not str(self.categoria).strip():
            raise ValueError("O campo 'Categoria' é obrigatório.")
        if self.preco < 0:
            raise ValueError("O preço não pode ser negativo.")
        if self.quantidade < 0:
            raise ValueError("A quantidade não pode ser negativa.")


@dataclass
class Venda:
    codigo_produto: int
    nome_produto: str
    quantidade: int
    preco_unitario: float
    data: datetime = field(default_factory=datetime.now)

    @property
    def total(self):
        return self.quantidade * self.preco_unitario


# ---------------------------------------------------------------------------
# LISTA LIGADA DUPLA (GENÉRICA)
# ---------------------------------------------------------------------------

class No:
    """Nó da lista ligada dupla: um valor e as ligações aos dois vizinhos."""

    __slots__ = ("valor", "anterior", "proximo")

    def __init__(self, valor):
        self.valor = valor
        self.anterior = None
        self.proximo = None

    def __repr__(self):
        return f"No({self.valor!r})"


class ListaLigadaDupla:
    """Lista duplamente ligada com ponteiros para a cabeça e para a cauda."""

    def __init__(self):
        self.cabeca = None
        self.cauda = None
        self.tamanho = 0

    def __len__(self):
        return self.tamanho

    def __iter__(self):
        """Percorre os valores do início para o fim."""
        atual = self.cabeca
        while atual is not None:
            yield atual.valor
            atual = atual.proximo

    def percorrer_nos(self):
        """Percorre os nós do início para o fim."""
        atual = self.cabeca
        while atual is not None:
            yield atual
            atual = atual.proximo

    def percorrer_nos_inverso(self):
        """Percorre os nós do fim para o início (só possível na lista dupla)."""
        atual = self.cauda
        while atual is not None:
            yield atual
            atual = atual.anterior

    def valores(self):
        return list(self)

    def valores_invertidos(self):
        return [no.valor for no in self.percorrer_nos_inverso()]

    # ---------------- INSERÇÃO ----------------
    def inserir_fim(self, valor):
        """Insere no fim em O(1), graças ao ponteiro para a cauda."""
        novo = No(valor)
        if self.cauda is None:
            self.cabeca = self.cauda = novo
        else:
            novo.anterior = self.cauda
            self.cauda.proximo = novo
            self.cauda = novo
        self.tamanho += 1
        return novo

    # ---------------- ACESSO POR POSIÇÃO ----------------
    def no_na_posicao(self, posicao):
        """Devolve o nó da posição indicada (1 = primeiro).

        Percorre a partir da extremidade mais próxima, o que reduz o número de
        passos para metade no pior caso.
        """
        if not isinstance(posicao, int) or posicao < 1 or posicao > self.tamanho:
            raise ValueError(
                f"Posição inválida: {posicao}. A lista tem {self.tamanho} elemento(s)."
            )
        if posicao <= self.tamanho // 2:
            atual = self.cabeca
            for _ in range(posicao - 1):
                atual = atual.proximo
        else:
            atual = self.cauda
            for _ in range(self.tamanho - posicao):
                atual = atual.anterior
        return atual

    # ---------------- REMOÇÃO ----------------
    def remover_no(self, no):
        """Remove um nó em O(1), religando directamente os seus vizinhos."""
        if no.anterior is None:
            self.cabeca = no.proximo
        else:
            no.anterior.proximo = no.proximo

        if no.proximo is None:
            self.cauda = no.anterior
        else:
            no.proximo.anterior = no.anterior

        no.anterior = no.proximo = None
        self.tamanho -= 1
        return no.valor

    def remover_por_posicao(self, posicao):
        return self.remover_no(self.no_na_posicao(posicao))


# ---------------------------------------------------------------------------
# LISTA DE PRODUTOS
# ---------------------------------------------------------------------------

class ListaProdutos(ListaLigadaDupla):
    """Lista ligada dupla com as operações de gestão de produtos."""

    # ---------------- CADASTRO ----------------
    def cadastrar(self, produto):
        if self.buscar_por_codigo(produto.codigo) is not None:
            raise ValueError(f"Já existe um produto com o código {produto.codigo}.")
        self.inserir_fim(produto)
        return produto

    # ---------------- BUSCA ----------------
    def _no_por_codigo(self, codigo):
        for no in self.percorrer_nos():
            if no.valor.codigo == codigo:
                return no
        return None

    def buscar_por_codigo(self, codigo):
        no = self._no_por_codigo(codigo)
        return no.valor if no is not None else None

    def buscar_por_um_atributo(self, atributo, valor):
        validar_atributo(atributo)
        return [p for p in self if valores_iguais(getattr(p, atributo), valor)]

    def buscar_por_dois_atributos(self, atributo1, valor1, atributo2, valor2):
        validar_atributo(atributo1)
        validar_atributo(atributo2)
        return [
            p for p in self
            if valores_iguais(getattr(p, atributo1), valor1)
            and valores_iguais(getattr(p, atributo2), valor2)
        ]

    # ---------------- ALTERAÇÃO ----------------
    def alterar_por_codigo(self, codigo, novos_dados):
        """Altera os campos indicados. Campos a None são ignorados."""
        no = self._no_por_codigo(codigo)
        if no is None:
            raise ValueError(f"Produto com código {codigo} não encontrado.")

        alteracoes = {c: v for c, v in novos_dados.items() if v is not None}
        if not alteracoes:
            raise ValueError("Preencha pelo menos um campo para alterar.")

        # replace() constrói um novo Produto, o que volta a correr as
        # validações de __post_init__ sobre os dados já alterados.
        no.valor = replace(no.valor, **alteracoes)
        return no.valor

    def dar_baixa_stock(self, codigo, quantidade):
        produto = self.buscar_por_codigo(codigo)
        if produto is None:
            raise ValueError(f"Produto com código {codigo} não encontrado.")
        if quantidade > produto.quantidade:
            raise ValueError(f"Stock insuficiente. Disponível: {produto.quantidade}.")
        produto.quantidade -= quantidade
        return produto

    # ---------------- ELIMINAÇÃO ----------------
    def eliminar_por_posicao(self, posicao):
        return self.remover_por_posicao(posicao)

    def eliminar_por_codigo(self, codigo):
        no = self._no_por_codigo(codigo)
        if no is None:
            raise ValueError(f"Produto com código {codigo} não encontrado.")
        return self.remover_no(no)

    # ---------------- IMPRESSÃO ----------------
    def listar_todos(self):
        return self.valores()

    def listar_por_criterio(self, atributo, valor):
        return self.buscar_por_um_atributo(atributo, valor)

    def listar_ordenado(self, atributo, decrescente=False):
        """Ordena os produtos por um atributo usando bubble sort.

        O bubble sort é O(n^2) e foi escrito à mão por exigência do trabalho;
        numa aplicação real usar-se-ia sorted(). A variável `trocou` permite
        terminar mais cedo quando a lista já está ordenada.
        """
        validar_atributo(atributo)
        produtos = self.valores()
        n = len(produtos)

        for i in range(n - 1):
            trocou = False
            for j in range(n - 1 - i):
                a = chave_ordenacao(getattr(produtos[j], atributo))
                b = chave_ordenacao(getattr(produtos[j + 1], atributo))
                fora_de_ordem = a < b if decrescente else a > b
                if fora_de_ordem:
                    produtos[j], produtos[j + 1] = produtos[j + 1], produtos[j]
                    trocou = True
            if not trocou:
                break

        return produtos


# ---------------------------------------------------------------------------
# LISTA DE VENDAS
# ---------------------------------------------------------------------------

class ListaVendas(ListaLigadaDupla):
    """Lista ligada dupla com as vendas realizadas."""

    def registar_venda(self, codigo_produto, nome_produto, quantidade, preco_unitario):
        if quantidade <= 0:
            raise ValueError("A quantidade vendida deve ser maior que 0.")
        venda = Venda(codigo_produto, nome_produto, quantidade, preco_unitario)
        self.inserir_fim(venda)
        return venda

    def listar_todas(self):
        return self.valores()

    def listar_recentes_primeiro(self):
        """Vendas da mais recente para a mais antiga (travessia inversa)."""
        return self.valores_invertidos()

    def total_vendas(self):
        return sum(venda.total for venda in self)

    def total_quantidade(self):
        return sum(venda.quantidade for venda in self)
