"""Escalonadores: FCFS, SJF não preemptivo e RR com quantum."""
import heapq
from collections import deque


class OrdemDeEntrada:
    """FCFS e RR: ordem de entrada na fila."""

    def __init__(self):
        self.d = deque()

    def push(self, p):
        self.d.append(p)

    def pop(self):
        return self.d.popleft()

    def __len__(self):
        return len(self.d)

    def ordem(self):
        return [p.pid for p in self.d]


class MenorBurst:
    """SJF: menor próximo burst de CPU (ou o que falta dele); empate por ordem de entrada."""

    def __init__(self):
        self.d = []

    def push(self, p):
        heapq.heappush(self.d, (p.rest, p.seq, p))

    def pop(self):
        return heapq.heappop(self.d)[2]

    def __len__(self):
        return len(self.d)

    def ordem(self):
        return [x[2].pid for x in sorted(self.d, key=lambda x: x[:2])]


def criar(sched):
    return MenorBurst() if sched == 'sjf' else OrdemDeEntrada()


def preempta_rr(c, fila, quantum):
    """Fim do quantum: True se o processo vai para o fim da fila; sem outro pronto, recebe novo quantum."""
    if c.estado != 'exec' or c.qusado < quantum:
        return False
    if fila:
        return True
    c.qusado = 0
    return False
