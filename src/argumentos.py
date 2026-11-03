"""ARGUMENTOS: linha de comando (argparse)."""
import argparse


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description='Simulador de escalonamento de CPU com paginação sob demanda')
    ap.add_argument('--arquivo', required=True)
    ap.add_argument('--cpus', type=int, choices=[1, 4], required=True)
    ap.add_argument('--sched', choices=['fcfs', 'sjf', 'rr'], required=True)
    ap.add_argument('--quantum', type=int)
    ap.add_argument('--subst', choices=['fifo', 'lru'], default='lru')
    ap.add_argument('--quadros', type=int, default=256)
    ap.add_argument('--custo-troca', type=int, default=1)
    ap.add_argument('--log')
    ap.add_argument('--tempo-fault', type=int, default=20)
    ap.add_argument('--sem-memoria', action='store_true')
    a = ap.parse_args(argv)
    if a.sched == 'rr' and (a.quantum is None or a.quantum < 1):
        ap.error('--sched rr exige --quantum >= 1')
    if a.sched != 'rr':
        a.quantum = None
    return a
