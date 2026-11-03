"""MÉTRICAS: espera, turnaround, resposta, makespan, trocas, uso das CPUs e page faults."""


def calcular(P, cpus, faults, makespan, com_memoria):
    lp = list(P.values())
    n = len(lp)
    esperas = [p.espera for p in lp]
    refs = sum(len(b['refs']) for p in lp for b in p.bursts if 'cpu' in b) if com_memoria else 0
    return {
        'procs': {p.pid: {'espera': p.espera, 'resposta': p.primeiro - p.chegada,
                          'turnaround': p.termino - p.chegada} for p in lp},
        'espera_media': sum(esperas) / n,
        'espera_max': max(esperas),
        'turnaround_medio': sum(p.termino - p.chegada for p in lp) / n,
        'resposta_media': sum(p.primeiro - p.chegada for p in lp) / n,
        'makespan': makespan,
        'cpus': [{'util': c.util, 'troca': c.troca, 'ocioso': c.ocioso, 'trocas': c.trocas,
                  'gantt': c.gantt} for c in cpus],
        'faults': faults,
        'refs': refs,
        'taxa_faults': faults / refs if refs else 0.0,
    }
