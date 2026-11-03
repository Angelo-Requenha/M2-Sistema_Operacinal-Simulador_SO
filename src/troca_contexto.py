"""Troca de contexto: estado de cada CPU e acúmulo de tempo útil, de troca e ocioso."""

JANELA_GANTT = 200


class Cpu:
    def __init__(self, i):
        self.i = i
        self.proc = None
        self.estado = None  # None (livre), 'troca' ou 'exec'
        self.ate = 0        # fim da troca de contexto
        self.ultimo = None
        self.qusado = 0
        self.trocas = 0
        self.util = 0
        self.troca = 0
        self.ocioso = 0
        self.gantt = []

    def inicia(self, p, t, custo):
        # processo diferente do último desta CPU (ou primeiro despacho) paga a troca
        self.proc = p
        self.qusado = 0
        if p.pid != self.ultimo:
            self.trocas += 1
        if p.pid != self.ultimo and custo > 0:
            self.estado = 'troca'
            self.ate = t + custo
        else:
            self.estado = 'exec'
        self.ultimo = p.pid

    def fim_troca(self, t):
        if self.estado == 'troca' and self.ate == t:
            self.estado = 'exec'

    def libera(self):
        self.proc = None
        self.estado = None

    def contabiliza(self, t, dur=1):
        if self.estado == 'exec':
            self.util += dur
            ev = 'P%d' % self.proc.pid
        elif self.estado == 'troca':
            self.troca += dur
            ev = 'TROCA'
        else:
            self.ocioso += dur
            ev = 'OCIOSA'
        self.marca(t, t + dur, ev)

    def marca(self, ini, fim, ev):
        fim = min(fim, JANELA_GANTT)
        if ini >= fim:
            return
        if self.gantt and self.gantt[-1][2] == ev and self.gantt[-1][1] == ini:
            self.gantt[-1][1] = fim
        else:
            self.gantt.append([ini, fim, ev])
