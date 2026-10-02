---
title: Relatório de validação
sidebar_label: Relatório
sidebar_position: 2
description: Como o relatório é montado, o cálculo de consistência, o HTML e o código de saída.
---

# Relatório de validação

## Como o relatório é montado

`validate_dataset(dataset, today=None)`:

1. roda as 10 verificações de `CHECKS` (4 estruturais + 6 de domínio);
2. **deduplica** violações idênticas (a mesma quebra pode ser detectada por uma verificação base e
   por um validador de domínio) serializando cada dicionário com `json.dumps(..., sort_keys=True)`;
3. recalcula, por domínio, o percentual de consistência;
4. agrega as contagens por regra e as linhas por tabela.

## Cálculo de consistência

Para cada domínio $d$ com $n$ personas no dataset:

$$\text{err}_d = \max\big(|\{\text{person\_id distintos nas violações}\}|,\; |\text{violações}|\big)$$

$$\text{consistência}_d = 100 \cdot \left(1 - \frac{\min(n, \text{err}_d)}{n}\right)$$

$$\text{overall} = \frac{1}{6}\sum_d \text{consistência}_d$$

:::caution Interpretação
A métrica é limitada a 0% por domínio (muitas violações em poucas pessoas saturam o indicador) e
usa o número de **personas**, não de linhas, como denominador. Ela serve para acompanhar tendência
entre execuções, não como medida absoluta de qualidade. O indicador binário confiável é
`passed`.
:::

## Estrutura do dicionário

| Chave | Tipo | Descrição |
|---|---|---|
| `passed` | `bool` | `True` quando não há nenhuma violação |
| `violation_count` / `critical_violations` | `int` | total após deduplicação |
| `violations` | `list[dict]` | cada item com `domain`, `rule` e campos de contexto |
| `violations_by_rule` | `dict[str, int]` | contagem por regra |
| `domain_consistency` | `dict[str, float]` | percentual por domínio |
| `overall_consistency_pct` | `float` | média dos domínios |
| `row_counts` | `dict[str, int]` | linhas por tabela |

## A tabela `validacao_consistencia`

`build_validation_table_rows(dataset, today)` converte o relatório em linhas do domínio 24:

- **com violações** — uma linha por violação, com `tabela`, `regra_violada` e `registro_id`;
- **sem violações** — cinco linhas de controle com `regra_violada = "nenhuma_violacao"` apontando
  para as cinco primeiras personas, para que a tabela nunca fique vazia.

## Relatório HTML

```bash
python3 -m persona_db.scripts.generate --personas 500 --seed 42 \
  --output dataset.json --html-report report.html
```

`render_html_report(report, out_path)` escreve uma página autocontida (sem CSS externo) com:

- um cabeçalho de status — `APROVADO (0 violações)` ou `REPROVADO (N violações)` — e o percentual
  geral;
- a tabela de consistência por domínio;
- a contagem de registros por tabela.

```python
from persona_db.validators import render_html_report, validate_dataset
render_html_report(validate_dataset(dataset), "relatorio.html")
```

## Código de saída e uso em CI

| Comando | Saída 0 | Saída 1 |
|---|---|---|
| `scripts.generate` | validação aprovada (ou `--no-validate`) | qualquer violação — **o JSON não é gravado** |
| `validators.run_validators` | `passed = True` | `passed = False` |

```yaml
- name: Dataset de fumaça
  run: |
    python -m persona_db.scripts.generate --personas 100 --seed 7 --dry-run
    python -m persona_db.validators.run_validators --personas 100 --seed 7
```

## Depurando uma violação

```python
from collections import Counter
from persona_db.scripts.generate import generate_all
from persona_db.validators import validate_dataset

dataset = generate_all(n=300, seed=7)
report = validate_dataset(dataset)

print(Counter(v["rule"] for v in report["violations"]).most_common())

alvo = next(v for v in report["violations"] if v["rule"] == "parent_at_least_14")
pessoa = next(p for p in dataset["pessoa"] if p["id"] == alvo["person_id"])
print(pessoa["data_nascimento"], pessoa.get("pai_id"), pessoa.get("mae_id"))
```

Como a geração é determinística, reproduzir o caso é só repetir a mesma semente — e o
`persona_id` da violação identifica exatamente qual sub-fluxo de RNG investigar.
