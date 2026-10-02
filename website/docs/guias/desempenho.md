---
title: Desempenho
sidebar_label: Desempenho
sidebar_position: 4
description: Onde o tempo é gasto, o que já dá para fazer hoje e o que está apenas estudado.
---

# Desempenho

## Medindo

```bash
python3 -m persona_db.scripts.benchmark --people 1000 --seed 7
python3 -m cProfile -o profile.out -m persona_db.scripts.benchmark --people 200
snakeviz profile.out
```

O custo é aproximadamente **linear** no número de personas: cada persona passa por 24 geradores que
fazem trabalho proporcional a ela própria. As exceções são os domínios que formam pares entre
personas (genealogia, rede social), com componente levemente super-linear.

## Onde o tempo vai

| Ponto quente | Por quê |
|---|---|
| `SeededRNG.fork()` | instancia um `numpy.random.Generator` novo — várias vezes por persona |
| `SeededRNG.choice()` | converte listas Python (às vezes de dicionários) em arrays NumPy para sortear **um** elemento |
| `SocioeconomicEngine.education_level()` | aloca um array de 4 posições por pessoa só para um softmax |
| `uuid5()` | hash SHA-1 por linha gerada (centenas por persona) |
| Serialização JSON | `json.dump` do dataset inteiro ao final |

:::info NumPy aqui é custo, não ganho
O projeto usa NumPy para sorteios **escalares**, caso em que o overhead de boxing/unboxing supera o
benefício vetorial. A análise completa está em
[`rewrite.MD`](https://github.com/havaianasdestruido/PersonaDB/blob/main/rewrite.MD).
:::

## O que dá para fazer hoje

| Ação | Ganho | Risco |
|---|---|---|
| `--no-validate` em lotes grandes | evita a passagem extra de validação | perde a garantia de consistência |
| `--domains` ao desenvolver | gera só o necessário | dataset parcial |
| Gerar em lotes paralelos por faixa de personas (processos separados, sementes distintas) | escala com os núcleos | personas de lotes diferentes não se relacionam |
| Carregar com `--page-size 2000–5000` | menos *round-trips* ao PostgreSQL | mais memória no servidor |
| Criar índices (`98_indexes.sql`) **após** a carga | `INSERT`s muito mais rápidos | consultas lentas até os índices existirem |

```bash
# geração "crua" e validação separada de uma amostra
python3 -m persona_db.scripts.generate --personas 20000 --seed 7 --no-validate --output big.json
python3 -m persona_db.validators.run_validators --personas 500 --seed 7
```

## Memória

Todo o dataset vive em dicionários Python até a serialização. Como regra prática, conte alguns
**kilobytes por persona por domínio** — milhares de personas chegam facilmente a vários gigabytes.
Para populações muito grandes, prefira gerar em vários lotes e carregar cada um no banco.

A carga no banco já é segura nesse aspecto: `bulk_insert` usa `ijson` em streaming e nunca
materializa o arquivo inteiro.

## Otimizações estudadas (não implementadas)

`rewrite.MD` avalia quatro caminhos. O documento é explícito: **não está no plano implementá-los
ainda**.

| Caminho | Veredito |
|---|---|
| **GraalPy / PyPy** | melhor relação ganho/esforço, desde que `rng.py` pare de chamar NumPy para cada sorteio escalar (~40 linhas) |
| **Correção cirúrgica em CPython** (`rng.py` + `gen_02_genealogia.py`) | 5×–20× sem trocar de runtime, com ~60 linhas alteradas |
| **Vetorização NumPy completa** | exigiria reescrever todos os motores e geradores em formato colunar e quebraria o contrato `fork(persona_id, domain)` |
| **Cython** | mesmo problema: reescrita massiva |

:::danger Qualquer mudança no RNG quebra datasets existentes
Trocar o gerador subjacente altera as sequências e, portanto, todos os datasets gerados com as
sementes atuais. Se isso for feito, trate como *breaking change*: incremente `schema_version`,
atualize os testes estatísticos e avise no `CHANGELOG`.
:::

## Lado PostgreSQL

- Use o `sql/tuning/postgresql.conf.recommended` como linha de base.
- Rode `ANALYZE` após a carga.
- Aproveite o particionamento de `transacao` filtrando sempre por `data`.
- Para consultas por nome, o índice GIN trigram criado em `98_indexes.sql` acelera `ILIKE '%…%'`.
