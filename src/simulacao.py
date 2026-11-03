"""Tempo e estados: relógio discreto e transições novo -> pronto -> executando -> bloqueado -> terminado."""
import heapq

from .entrada import criar_processos
from .escalonadores import preempta_rr
from .fila_despacho import FilaProntos, despacha
from .memoria import Memoria
from .metricas import calcular
from .saidas import linha_log
from .troca_contexto import Cpu


def simular(procs, a, log=None):
    P = criar_processos(procs)
    chegadas = sorted(P.values(), key=lambda p: (p.chegada, p.pid))
    F = a.tempo_fault
    mem = None if a.sem_memoria else Memoria(a.quadros, a.subst == 'lru')
    fila = FilaProntos(a.sched)
    cpus = [Cpu(i) for i in range(a.cpus)]
    bloq = []  # heap (instante de retorno, pid, motivo): 'es', 'fault' ou 'retry'
    eventos = []
    ic = terminados = faults = t = 0

    def despachar(c):
        p = despacha(c, fila, t, a.custo_troca)
        eventos.append('DESPACHO P%d->CPU%d' % (p.pid, c.i))

    def tenta_carregar(p):
        ok = mem.carrega(p.pid, p.pagina())
        heapq.heappush(bloq, (t + F, p.pid, 'fault' if ok else 'retry'))

    def executa(c):
        # Resolve a referência da unidade [t, t+1); um fault libera a CPU no mesmo instante.
        nonlocal faults
        while True:
            if c.estado is None:
                if not fila:
                    return
                despachar(c)
            if c.estado == 'troca' or mem is None:
                return
            p = c.proc
            if mem.acessa(p.pid, p.pagina()):
                return
            faults += 1
            tenta_carregar(p)
            c.libera()
            eventos.append('FAULT P%d' % p.pid)

    while True:
        # (0) conclui a unidade [t-1, t) e as trocas que acabam em t
        for c in cpus:
            match c.estado:
                case 'exec':
                    p = c.proc
                    p.pos += 1
                    p.rest -= 1
                    c.qusado += 1
                    if p.rest == 0:
                        p.idx += 1
                        if p.idx >= len(p.bursts):
                            p.termino = t
                            terminados += 1
                            if mem:
                                mem.libera(p.pid)
                            eventos.append('TERMINO P%d' % p.pid)
                        else:
                            heapq.heappush(bloq, (t + p.bursts[p.idx]['es'], p.pid, 'es'))
                            p.idx += 1
                            p.pos = 0
                            p.rest = p.bursts[p.idx]['cpu']
                            eventos.append('FIM_BURST P%d' % p.pid)
                        c.libera()
                case 'troca':
                    c.fim_troca(t)
        if terminados == len(P):
            break

        # (1) chegadas e retornos de E/S e de page fault, em ordem de pid
        evs = []
        while ic < len(chegadas) and chegadas[ic].chegada == t:
            evs.append((chegadas[ic].pid, 'chegada'))
            ic += 1
        while bloq and bloq[0][0] == t:
            _, pid, motivo = heapq.heappop(bloq)
            evs.append((pid, motivo))
        evs.sort()
        for pid, motivo in evs:
            p = P[pid]
            match motivo:
                case 'retry':
                    tenta_carregar(p)
                    continue
                case 'chegada':
                    nome = 'CHEGADA'
                case 'es':
                    nome = 'RETORNO_ES'
                case 'fault':
                    nome = 'RETORNO_FAULT'
            fila.entra(p, t)
            eventos.append('%s P%d' % (nome, pid))

        # (2) preempção por quantum
        if a.sched == 'rr':
            for c in cpus:
                if preempta_rr(c, fila, a.quantum):
                    p = c.proc
                    c.libera()
                    fila.entra(p, t)
                    eventos.append('PREEMPCAO P%d' % p.pid)

        # (3) despachos, menor índice primeiro; depois as referências da unidade [t, t+1)
        for c in cpus:
            if c.estado is None and fila:
                despachar(c)
        for c in cpus:
            executa(c)

        for c in cpus:
            c.contabiliza(t)
        if log and eventos:
            log.write(linha_log(t, eventos, fila, bloq, cpus, mem))
        eventos.clear()

        t += 1
        # pula instantes em que nada acontece
        if not fila and all(c.estado is None for c in cpus):
            prox = []
            if ic < len(chegadas):
                prox.append(chegadas[ic].chegada)
            if bloq:
                prox.append(bloq[0][0])
            if not prox:
                raise RuntimeError('simulação travada em t=%d' % t)
            nt = max(t, min(prox))
            if nt > t:
                for c in cpus:
                    c.contabiliza(t, nt - t)
            t = nt

    return calcular(P, cpus, faults, t, mem is not None)
