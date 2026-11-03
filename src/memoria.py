"""Memória: paginação sob demanda com quadros globais e substituição FIFO ou LRU."""
from collections import OrderedDict


class Memoria:
    """OrderedDict em ordem de carga (FIFO) ou de referência (LRU)."""

    def __init__(self, quadros, lru):
        self.n = quadros
        self.lru = lru
        self.pags = OrderedDict()  # (pid, pagina) -> None
        self.prot = set()          # páginas trazidas por fault ainda não re-referenciadas
        self.por_proc = {}

    def acessa(self, pid, pg):
        k = (pid, pg)
        if k not in self.pags:
            return False
        self.prot.discard(k)
        if self.lru:
            self.pags.move_to_end(k)
        return True

    def carrega(self, pid, pg):
        if len(self.pags) >= self.n:
            if len(self.prot) >= len(self.pags):
                return False  # todos os quadros protegidos
            for v in self.pags:
                if v not in self.prot:
                    break
            del self.pags[v]
            self.por_proc[v[0]].discard(v)
        k = (pid, pg)
        self.pags[k] = None
        self.prot.add(k)
        self.por_proc.setdefault(pid, set()).add(k)
        return True

    def libera(self, pid):
        for k in self.por_proc.pop(pid, ()):
            del self.pags[k]
            self.prot.discard(k)
