#!/usr/bin/env python3
"""Roda os exemplos de validação e confere os resultados esperados."""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
from src.argumentos import parse_args  # noqa: E402
from src.simulacao import simular  # noqa: E402

CASOS = [
    ('Exemplo 1 (FCFS, sem memória)', 'exemplo1.json',
     ['--cpus', '1', '--sched', 'fcfs', '--custo-troca', '1', '--sem-memoria'],
     {'espera': [0, 6, 8], 'resposta': [0, 6, 8], 'turnaround': [6, 10, 11],
      'util': 10, 'troca': 3, 'ocioso': 0, 'makespan': 13}),
    ('Exemplo 2 (FCFS, page faults)', 'exemplo2.json',
     ['--cpus', '1', '--sched', 'fcfs', '--custo-troca', '0', '--tempo-fault', '5'],
     {'espera': [0, 0, 0], 'turnaround': [12, 12, 6], 'makespan': 13}),
    ('Exemplo 3 (FCFS)', 'exemplo3.json',
     ['--cpus', '1', '--sched', 'fcfs', '--custo-troca', '0', '--tempo-fault', '20'],
     {'espera': [0, 4, 7], 'espera_media': 3.67}),
    ('Exemplo 3 (SJF)', 'exemplo3.json',
     ['--cpus', '1', '--sched', 'sjf', '--custo-troca', '0', '--tempo-fault', '20'],
     {'espera': [5, 2, 0], 'espera_media': 2.33}),
]


def confere(r, esperado):
    erros = []
    for k, v in esperado.items():
        if k in ('espera', 'resposta', 'turnaround'):
            obtido = [r['procs'][pid][k] for pid in sorted(r['procs'])]
        elif k in ('util', 'troca', 'ocioso'):
            obtido = sum(c[k] for c in r['cpus'])
        elif k == 'espera_media':
            obtido = round(r[k], 2)
        else:
            obtido = r[k]
        if obtido != v:
            erros.append('%s: esperado %s, obtido %s' % (k, v, obtido))
    return erros


def main():
    falhas = 0
    for nome, arq, argv, esperado in CASOS:
        caminho = os.path.join(AQUI, arq)
        a = parse_args(['--arquivo', caminho] + argv)
        with open(caminho, encoding='utf-8') as f:
            r = simular(json.load(f), a)
        erros = confere(r, esperado)
        print('%-32s %s' % (nome, 'OK' if not erros else 'FALHOU'))
        for e in erros:
            print('    ' + e)
        falhas += bool(erros)
    print('%d de %d testes passaram' % (len(CASOS) - falhas, len(CASOS)))
    sys.exit(1 if falhas else 0)


if __name__ == '__main__':
    main()
