---
title: CI e qualidade
sidebar_label: CI e qualidade
sidebar_position: 3
description: Workflows do GitHub Actions, gates de qualidade e como reproduzi-los localmente.
---

# CI e qualidade

## Workflows

| Workflow | Arquivo | Gatilho | O que faz |
|---|---|---|---|
| **CI** | `.github/workflows/ci.yml` | todo push e pull request | instala o pacote com extras `[dev]`, roda `pytest` e `ruff` em Python 3.12 |
| **Pages** | `.github/workflows/docs.yml` | push em `main`, **todo pull request** e `workflow_dispatch` | constrói a raiz com Jekyll e a documentação com Docusaurus, monta o site combinado e publica no GitHub Pages |
| **Jekyll (legado)** | `.github/workflows/jekyll-gh-pages.yml` | só `workflow_dispatch` | publicação antiga, apenas da raiz; mantida para execução manual |

Em pull requests o workflow de Pages roda o build completo (é o gate de links quebrados), mas
**pula a publicação**: os passos de upload e o job `deploy` só rodam em `push`/`workflow_dispatch`.

```yaml
# ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12'}
      - run: python -m pip install -e './persona_db[dev]'
      - run: python -m pytest persona_db/tests
      - run: python -m ruff check persona_db
```

:::note Um artefato, dois sites
O GitHub Pages publica um único artefato por repositório. Para conviverem, `docs.yml` monta os dois
na mesma árvore — Jekyll na raiz (`/PersonaDB/`) e Docusaurus em `/PersonaDB/docs/` — e é o único
workflow que publica automaticamente. O `jekyll-gh-pages.yml` ficou restrito a `workflow_dispatch`
porque o artefato dele contém só a raiz e apagaria `/docs`; os dois compartilham o grupo de
concorrência `pages`.
:::

## Reproduzindo a CI localmente

```bash
python3 -m pip install -e "./persona_db[dev]"
python3 -m pytest persona_db/tests
python3 -m ruff check persona_db
```

Para o workflow de documentação:

```bash
cd website
npm ci
npm run build          # roda gen:docs automaticamente (prebuild)
npm run serve
```

## Gates de qualidade

| Gate | Ferramenta | Bloqueia merge? |
|---|---|---|
| Testes unitários, de integração e estatísticos | `pytest` | sim |
| Lint | `ruff` (linha 100, `py310`) | sim |
| Build da documentação | Docusaurus (`onBrokenLinks: 'throw'`) | sim, no workflow de docs |
| Validação de consistência do dataset | `scripts.generate` (exit 1) | não é passo da CI hoje — recomendado adicionar |
| Tipos | `mypy` | não |
| Formatação | `black` | não |

### Sugestão: validação como passo de CI

```yaml
      - name: Dataset de fumaça
        run: |
          python -m persona_db.scripts.generate --personas 100 --seed 7 --dry-run
          python -m persona_db.validators.run_validators --personas 100 --seed 7
```

Ambos retornam `1` em caso de violação, o que transforma a consistência dos dados em um gate real.

## Links quebrados na documentação

O build do site está configurado com `onBrokenLinks: 'throw'`: qualquer link interno inválido
**falha o build**, inclusive links apontando para páginas geradas que deixaram de existir. Se você
remover um módulo Python ou um arquivo DDL, rode `npm run build` para confirmar que nenhuma página
escrita à mão ficou apontando para o vazio.

## Dependências

| Grupo | Onde | Fixação |
|---|---|---|
| Runtime Python | `persona_db/pyproject.toml` | sem *pins* — resolvem para a última versão compatível |
| Dev Python | extra `[dev]` | sem *pins* |
| Node | `website/package.json` + `package-lock.json` | *lockfile* versionado; a CI usa `npm ci` |

:::note Reprodutibilidade de longo prazo
Como as dependências Python não têm versões fixas, uma mudança futura no `numpy` pode alterar
sequências do PCG64 e, com isso, os datasets. Se precisar de reprodutibilidade por anos, fixe as
versões em um `requirements.lock` próprio.
:::
