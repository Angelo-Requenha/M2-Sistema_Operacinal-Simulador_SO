"""ENTRADA: leitura do JSON com a lista de processos."""
import json


class Proc:
    def __init__(self, d):
        self.pid = d['pid']
        self.chegada = d['chegada']
        self.bursts = d['bursts']         # alternam CPU e E/S; 'classe' não é usada
        self.idx = 0                      # índice do burst de CPU atual
        self.pos = 0                      # unidades já executadas do burst atual
        self.rest = self.bursts[0]['cpu']  # unidades que faltam do burst atual
        self.espera = 0
        self.entrada = 0                  # instante em que entrou na fila
        self.seq = 0                      # ordem de entrada na fila (desempate)
        self.primeiro = None
        self.termino = None

    def pagina(self):
        return self.bursts[self.idx]['refs'][self.pos]


def carregar(arquivo):
    with open(arquivo, encoding='utf-8') as f:
        return json.load(f)


def criar_processos(dados):
    return {d['pid']: Proc(d) for d in dados}
