"""
Sistema de Gestão de Padaria - ponto de entrada
Trabalho Prático 1 - Algoritmos e Estruturas de Dados
ISUTC - Engenharia Informática e de Telecomunicações

Executar com:  python3 main.py

Módulos:
    estruturas.py  - lista ligada dupla, produtos e vendas (sem interface)
    interface.py   - janela Tkinter
    main.py        - arranque da aplicação
"""

import tkinter as tk

from interface import AplicacaoPadaria


def main():
    root = tk.Tk()
    AplicacaoPadaria(root)
    root.mainloop()


if __name__ == "__main__":
    main()
