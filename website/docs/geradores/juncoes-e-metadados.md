---
title: Junções e metadados
sidebar_label: Junções e metadados
sidebar_position: 4
description: Como o orquestrador deriva as tabelas N:N (domínio 25) e os metadados (24 e 26).
---

# Junções e metadados

Três domínios não têm gerador próprio: eles são derivados pelo orquestrador
[`scripts/generate.py`](../referencia-api/scripts/generate.md) depois que todos os geradores rodam.

## Domínio 25 — tabelas de junção N:N

`_build_junction_tables(dataset, today)` percorre as tabelas já geradas e materializa 14 relações
muitos-para-muitos, **deduplicando pares** com conjuntos auxiliares.

| Tabela de junção | Derivada de | Colunas extras |
|---|---|---|
| `pessoa_habilidade` | `habilidade` | `nivel` |
| `pessoa_idioma_nivel` | `pessoa_idioma` | `nivel_leitura`, `nivel_fala` |
| `pessoa_hobby` | `hobby` | `desde_quando` |
| `pessoa_grupo_social` | `membro_grupo_social` | `papel` |
| `pessoa_evento` | `participacao_evento_social` | `papel` |
| `pessoa_doenca_familiar` | `predisposicao_genetica` | `grau_risco` (normalizado em [0,1]) |
| `pessoa_pet` | `pet` | `tipo_vinculo` |
| `pessoa_veiculo` | `veiculo` | `tipo_posse` |
| `pessoa_imovel` | `imovel` | `tipo_posse` |
| `pessoa_eleicao` | `comparecimento_eleitoral` | `participou` |
| `pessoa_viagem_companheiro` | `companhia_viagem` | `papel` |
| `pessoa_empresa_socio` | `contrato_trabalho` com `tipo_contrato = "PJ"` | `percentual_participacao` |
| `pessoa_religiao_historico` | `conversao_religiosa` | `data_inicio`, `data_fim` |
| `pessoa_documento_historico` | `pessoa_documento` | `data_emissao`, `data_expiracao` |

A tabela `pessoa_processo` também é N:N, mas é produzida diretamente por `gen_11_juridico`.

:::note Fallback de religião
Se nenhuma conversão religiosa foi sorteada, o orquestrador insere uma linha mínima em
`pessoa_religiao_historico` (primeira pessoa, primeira crença, início na data de nascimento) para
que a tabela nunca fique vazia no dataset.
:::

```python
for v in dataset.get("veiculo", []):
    prop_id = v.get("proprietario_pessoa_id") or v.get("pessoa_id_proprietario") or v.get("pessoa_id")
    if prop_id and v.get("id"):
        junc["pessoa_veiculo"].append({"pessoa_id": prop_id, "veiculo_id": v["id"],
                                       "tipo_posse": "proprietario"})
```

O padrão `a or b or c` acomoda variações de nomenclatura entre geradores — um detalhe pragmático
que vale conhecer ao criar novas tabelas.

## Domínio 24 — metadados, auditoria e proveniência

| Tabela | Conteúdo |
|---|---|
| `versao_registro` | uma linha de exemplo versionando o primeiro registro de `pessoa` |
| `log_alteracao` | exemplo de alteração de `estado_civil` (campo antigo → novo) |
| `auditoria` | registra a chamada `generate_all(n=…, seed=…)`, usuário `personadb_orchestrator`, tabela `ALL` |
| `regra_geracao` | uma linha por posição do pipeline (`parametro = "pipeline_order"`) |
| `fonte_dado` | uma linha por tabela do dataset, com `metodo_geracao = "deterministic_pcg64_generator"` |
| `validacao_consistencia` | resultado dos validadores (violações ou cinco linhas `nenhuma_violacao`) |
| `exportacao_dataset` | formato, número de tabelas e `destino = "sha256:<digest>"` |
| `semente_aleatoria` | preenchida no banco pelo gatilho de `99_functions.sql` ao inserir em `pessoa` |

O digest é calculado sobre o mapa ordenado de contagens por tabela:

```python
digest = hashlib.sha256(
    json.dumps({k: len(v) for k, v in sorted(dataset.items())}, sort_keys=True).encode("utf-8")
).hexdigest()[:32]
```

Ou seja: **duas execuções com a mesma semente produzem o mesmo digest**, o que dá um teste de
regressão barato para o pipeline.

## Domínio 26 — versão do schema

`schema_version` recebe uma linha fixa (`1.0.0`, "PersonaDB schema inicial (25 domínios +
controle)"), útil para validar que o dataset e o DDL aplicado estão na mesma geração.

## Reproduzindo fora do orquestrador

```python
from datetime import date
from persona_db.scripts.generate import _build_junction_tables, generate_all

dataset = generate_all(n=50, seed=7)
juncoes = _build_junction_tables(dataset, date(2026, 1, 1))
print({k: len(v) for k, v in juncoes.items()})
```

A função tem prefixo `_` por ser detalhe de implementação: a interface pública é `generate_all`,
que já a chama quando o filtro `--domains` inclui `25_juncoes` (ou quando não há filtro).
