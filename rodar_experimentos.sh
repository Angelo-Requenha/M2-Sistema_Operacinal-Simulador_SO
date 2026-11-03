#!/usr/bin/env bash
# Roda todas as execuções exigidas e calcula speedup/eficiência em speedup.csv.
set -e
cd "$(dirname "$0")"
if python3 -c '' 2>/dev/null; then PY=python3; else PY=python; fi

rm -f resultados.csv speedup.csv

for arq in cenarios/cenario_A_t0.json cenarios/cenario_B_espacadas.json; do
  for cpus in 1 4; do
    for s in fcfs sjf; do
      $PY simulador.py --arquivo "$arq" --cpus "$cpus" --sched "$s" --subst lru --quadros 256
    done
    for q in 2 5 10 20 50; do
      $PY simulador.py --arquivo "$arq" --cpus "$cpus" --sched rr --quantum "$q" --subst lru --quadros 256
    done
  done
  # FIFO para comparar com LRU
  $PY simulador.py --arquivo "$arq" --cpus 4 --sched fcfs --subst fifo --quadros 256
  $PY simulador.py --arquivo "$arq" --cpus 4 --sched rr --quantum 10 --subst fifo --quadros 256
done

$PY - <<'PYEOF'
import csv
chave = lambda r: (r['arquivo'], r['sched'], r['quantum'], r['subst'], r['quadros'], r['custo_troca'], r['tempo_fault'])
ms = {}
with open('resultados.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        ms[chave(r) + (r['cpus'],)] = int(r['makespan'])
with open('speedup.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['arquivo', 'sched', 'quantum', 'subst', 'quadros', 'custo_troca', 'tempo_fault',
                'makespan_1cpu', 'makespan_4cpus', 'speedup', 'eficiencia'])
    for k in sorted({k[:-1] for k in ms}):
        if k + ('1',) in ms and k + ('4',) in ms:
            m1, m4 = ms[k + ('1',)], ms[k + ('4',)]
            w.writerow(list(k) + [m1, m4, '%.4f' % (m1 / m4), '%.4f' % (m1 / m4 / 4)])
print('speedup.csv gerado')
PYEOF
