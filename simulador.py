#!/usr/bin/env python3
"""Ponto de entrada do simulador; as camadas estão em src/."""
from src import saidas
from src.argumentos import parse_args
from src.entrada import carregar
from src.simulacao import simular


def main():
    a = parse_args()
    procs = carregar(a.arquivo)
    if a.log:
        with open(a.log, 'w', encoding='utf-8') as log:
            r = simular(procs, a, log)
    else:
        r = simular(procs, a)
    saidas.imprime_resumo(a, r)
    saidas.grava_resultados(a, r)
    print('Gantt: %s' % saidas.grava_gantt(a, r))


if __name__ == '__main__':
    main()
