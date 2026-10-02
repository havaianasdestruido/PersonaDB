---
title: "benchmark — medição do pipeline"
sidebar_label: benchmark
sidebar_position: 5
description: Medir tempo e volume de linhas da geração em memória.
---

# `scripts.benchmark`

```bash
python3 -m persona_db.scripts.benchmark [--people N] [--seed S]
```

Mede o tempo de parede da geração **em memória** (sem validação, sem I/O).

| Flag | Padrão |
|---|---|
| `--people` | `1000` |
| `--seed` | `7` |

```bash
$ python3 -m persona_db.scripts.benchmark --people 1000 --seed 7
1000 personas; 342118 rows; 57.413s
```

A implementação é deliberadamente mínima:

```python
start = time.perf_counter()
dataset = generate_dataset(args.people, args.seed)
elapsed = time.perf_counter() - start
print(f"{args.people} personas; {sum(map(len, dataset.values()))} rows; {elapsed:.3f}s")
```

## Comparando execuções

```bash
for n in 100 250 500 1000; do
  python3 -m persona_db.scripts.benchmark --people "$n" --seed 7
done
```

Como a geração é determinística, a contagem de linhas é estável entre execuções — qualquer
variação indica mudança de código, de seeds ou da âncora temporal, não ruído.

## Perfilamento

O extra `[dev]` instala o `snakeviz`, que combina bem com o `cProfile`:

```bash
python3 -m cProfile -o profile.out -m persona_db.scripts.benchmark --people 200
snakeviz profile.out
```

Pontos tipicamente dominantes: `SeededRNG.fork` (instanciar um `Generator` do NumPy),
`SeededRNG.choice` (conversão de listas Python para arrays) e `uuid5`. A análise detalhada está em
[Desempenho](../guias/desempenho.md).

## Via Makefile

```bash
make -C persona_db benchmark N_PESSOAS=1000 SEED=7
```
