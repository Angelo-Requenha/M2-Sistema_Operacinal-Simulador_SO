"""SAÍDAS: resumo no terminal, resultados.csv, Gantt em CSV e linhas do log."""
import csv
import os


def nome_execucao(a):
    base = os.path.splitext(os.path.basename(a.arquivo))[0]
    q = '_q%d' % a.quantum if a.sched == 'rr' else ''
    m = 'semmem' if a.sem_memoria else '%s_f%d' % (a.subst, a.quadros)
    return '%s_cpus%d_%s%s_%s_c%d' % (base, a.cpus, a.sched, q, m, a.custo_troca)


def pct(x, total):
    return 100.0 * x / total if total else 0.0


def linha_log(t, eventos, fila, bloq, cpus, mem):
    bl = ', '.join('P%d ate %d (%s)' % (pid, tr, m) for tr, pid, m in sorted(bloq))
    cp = ' '.join('CPU%d=%s' % (c.i, ('P%d%s' % (c.proc.pid, '(troca)' if c.estado == 'troca' else ''))
                               if c.proc else '-') for c in cpus)
    fl = ', '.join('P%d' % x for x in fila.ordem())
    qd = '%d/%d' % (len(mem.pags), mem.n) if mem else '-'
    return ('t=%d | eventos: %s | fila: [%s] | bloqueados: [%s] | %s | quadros ocupados: %s\n'
            % (t, ', '.join(eventos), fl, bl, cp, qd))


def imprime_resumo(a, r):
    ms = r['makespan']
    subst = 'nenhuma' if a.sem_memoria else a.subst
    print('=== Parâmetros ===')
    print('arquivo=%s cpus=%d sched=%s quantum=%s subst=%s quadros=%d custo-troca=%d tempo-fault=%d'
          % (a.arquivo, a.cpus, a.sched, a.quantum if a.quantum else '-', subst, a.quadros,
             a.custo_troca, a.tempo_fault))
    print('=== Métricas ===')
    print('Processos:          %d' % len(r['procs']))
    print('Espera média:       %.2f' % r['espera_media'])
    print('Espera máxima:      %d' % r['espera_max'])
    print('Turnaround médio:   %.2f' % r['turnaround_medio'])
    print('Resposta média:     %.2f' % r['resposta_media'])
    print('Makespan:           %d' % ms)
    print('Trocas de contexto: %d (por CPU: %s)'
          % (sum(c['trocas'] for c in r['cpus']), ', '.join(str(c['trocas']) for c in r['cpus'])))
    print('=== Por CPU ===')
    print('%-4s %8s %8s %8s %8s %8s %8s %8s %8s' % ('CPU', 'útil', 'troca', 'ocioso', '%útil', '%troca', '%ocioso',
                                                  'utiliz.', 'trocas'))
    for i, c in enumerate(r['cpus']):
        print('%-4d %8d %8d %8d %7.2f%% %7.2f%% %7.2f%% %7.2f%% %8d'
              % (i, c['util'], c['troca'], c['ocioso'], pct(c['util'], ms), pct(c['troca'], ms),
                 pct(c['ocioso'], ms), pct(c['util'] + c['troca'], ms), c['trocas']))
    print('=== Memória ===')
    print('Page faults: %d   Referências: %d   Taxa de faults: %.4f' % (r['faults'], r['refs'], r['taxa_faults']))


def grava_resultados(a, r, caminho='resultados.csv'):
    cab = ['arquivo', 'cpus', 'sched', 'quantum', 'subst', 'quadros', 'custo_troca', 'tempo_fault',
           'espera_media', 'espera_max', 'turnaround_medio', 'resposta_media', 'makespan', 'trocas_total',
           'trocas_por_cpu', 'util_por_cpu', 'troca_por_cpu', 'ocioso_por_cpu', 'utilizacao_por_cpu',
           'page_faults', 'referencias', 'taxa_faults']
    cs = r['cpus']
    ms = r['makespan']
    linha = [os.path.basename(a.arquivo), a.cpus, a.sched, a.quantum or '',
             'nenhuma' if a.sem_memoria else a.subst, a.quadros, a.custo_troca,
             a.tempo_fault, '%.4f' % r['espera_media'], r['espera_max'], '%.4f' % r['turnaround_medio'],
             '%.4f' % r['resposta_media'], ms, sum(c['trocas'] for c in cs),
             ';'.join(str(c['trocas']) for c in cs), ';'.join(str(c['util']) for c in cs),
             ';'.join(str(c['troca']) for c in cs), ';'.join(str(c['ocioso']) for c in cs),
             ';'.join('%.4f' % ((c['util'] + c['troca']) / ms if ms else 0) for c in cs),
             r['faults'], r['refs'], '%.6f' % r['taxa_faults']]
    novo = not os.path.exists(caminho)
    with open(caminho, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if novo:
            w.writerow(cab)
        w.writerow(linha)


def grava_gantt(a, r, pasta='gantt'):
    os.makedirs(pasta, exist_ok=True)
    nome = os.path.join(pasta, 'gantt_%s.csv' % nome_execucao(a))
    with open(nome, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['cpu', 'inicio', 'fim', 'evento'])
        for i, c in enumerate(r['cpus']):
            for ini, fim, ev in c['gantt']:
                w.writerow([i, ini, fim, ev])
    return nome
