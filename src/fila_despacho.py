"""Fila e despacho: fila de prontos global única, compartilhada por todas as CPUs."""
from . import escalonadores


class FilaProntos:
    def __init__(self, sched):
        self.politica = escalonadores.criar(sched)
        self.seq = 0

    def entra(self, p, t):
        p.entrada = t
        p.seq = self.seq
        self.seq += 1
        self.politica.push(p)

    def sai(self, t):
        # o processo sai da fila no instante do despacho
        p = self.politica.pop()
        p.espera += t - p.entrada
        if p.primeiro is None:
            p.primeiro = t
        return p

    def __len__(self):
        return len(self.politica)

    def ordem(self):
        return self.politica.ordem()


def despacha(c, fila, t, custo_troca):
    p = fila.sai(t)
    c.inicia(p, t, custo_troca)
    return p
