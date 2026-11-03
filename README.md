# Simulador de escalonamento de CPU com paginação sob demanda

Requer apenas Python 3.10 ou mais novo (biblioteca padrão).

## Uma execução

```
python3 simulador.py --arquivo cenarios/cenario_A_t0.json --cpus 4 --sched rr --quantum 10 --subst lru
```

Argumentos: `--arquivo`, `--cpus` (1 ou 4), `--sched` (fcfs|sjf|rr), `--quantum` (só RR),
`--subst` (fifo|lru), `--quadros` (padrão 256), `--custo-troca` (padrão 1), `--log ARQUIVO` (opcional).
Só para testes: `--tempo-fault` (padrão 20) e `--sem-memoria`.

Saídas: resumo no terminal, uma linha acrescentada em `resultados.csv` e o Gantt (0 a 200) em `gantt/gantt_<parâmetros>.csv`.

## Testes

```
python3 testes/verificar.py
```

## Experimentos

```
bash rodar_experimentos.sh
```

Gera `resultados.csv` (32 execuções), os Gantts em `gantt/` e `speedup.csv`.
