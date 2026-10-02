---
title: Contribuindo
sidebar_label: Contribuindo
sidebar_position: 2
description: Fluxo de contribuição, convenções de código e checklist de pull request.
---

# Contribuindo

## Preparar o ambiente

```bash
git clone https://github.com/havaianasdestruido/PersonaDB.git
cd PersonaDB
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -e "persona_db[dev,parquet]"
python3 -m pytest persona_db/tests -q
```

## Convenções de código

| Regra | Detalhe |
|---|---|
| Estilo | `ruff` com `line-length = 100`, alvo `py310` |
| Tipagem | anotações em funções públicas; `from __future__ import annotations` no topo |
| Docstrings | em português nos módulos de domínio; descreva tabelas produzidas e campos de enriquecimento |
| Nomes | tabelas, colunas e campos de domínio em português (`data_nascimento`); utilitários internos em inglês |
| Imports | absolutos (`from persona_db.engines.rng import new_rng`) |
| Privados | prefixo `_` para helpers de módulo |

### Determinismo é regra, não preferência

```python
import random                    # ❌
np.random.rand()                 # ❌
uuid.uuid4()                     # ❌
datetime.date.today()            # ❌

master.fork(p["id"], "gen42")    # ✅
uuid5(NAMESPACE_URL, chave)      # ✅
today or simulation_today()      # ✅
```

Veja [Determinismo](../arquitetura/determinismo.md).

## Onde mexer, dependendo do que você quer

| Objetivo | Arquivos |
|---|---|
| Nova tabela/domínio | `sql/schema/XX_*.sql`, `generators/gen_XX_*.py`, `scripts/generate.py`, testes |
| Recalibrar um modelo | `engines/*.py` (e `engines/constants.py` se for compartilhado) |
| Nova regra de consistência | `validators/val_*.py` e `run_validators.CHECKS` |
| Novo catálogo fictício | `seeds/lookup_data.py` |
| Nova distribuição | `seeds/probability_tables.py` |
| Documentação | `website/docs/**` (escrita à mão) ou docstrings (automática) |

Passo a passo completo em [Adicionar um novo domínio](../guias/novo-dominio.md).

## Checklist de pull request

- [ ] `python3 -m pytest persona_db/tests -q` passa
- [ ] `python3 -m ruff check persona_db` sem erros
- [ ] `python3 -m persona_db.scripts.generate --personas 100 --seed 7 --dry-run` aprovado na validação
- [ ] Nenhuma fonte de não-determinismo introduzida
- [ ] Docstrings atualizadas (elas alimentam a [Referência de API](../referencia-api/index.md))
- [ ] `python3 -m persona_db.scripts.document_schema` rodado se houve mudança de DDL
- [ ] `cd website && npm run build` passa se houve mudança de documentação
- [ ] Mudanças que alteram datasets existentes estão declaradas na descrição do PR

:::caution Mudanças que quebram reprodutibilidade
Alterar a ordem das chamadas ao RNG, os catálogos de seeds ou os coeficientes dos motores muda os
datasets gerados com as mesmas sementes. Isso é aceitável, mas precisa ser **explícito** na
descrição do PR — quem depende de uma semente específica precisa saber.
:::

## Mensagens de commit

Formato curto e imperativo, com o escopo quando ajudar:

```text
engines/health: corrige integral de sobrevivência para idades fracionárias
generators: adiciona domínio 42 (voluntariado)
docs: documenta o contrato dos geradores
```

## Reportando problemas

Abra uma [issue](https://github.com/havaianasdestruido/PersonaDB/issues) incluindo:

- comando exato e versão do Python;
- **semente** e número de personas (sem isso, o caso não é reproduzível);
- saída completa do erro ou as violações reportadas;
- comportamento esperado.

```bash
python3 -m persona_db.scripts.generate --personas 100 --seed 12345 --dry-run 2>&1 | tail -30
```

## Estrutura de coordenação

As docstrings trazem linhas como `Ownership: Agent 2`. Elas vêm do processo multiagente registrado
em `_coordination/` e indicam qual módulo é a fonte de verdade de cada calibração. Ao editar um
arquivo "de propriedade" de outro módulo, prefira estender em vez de reescrever.
