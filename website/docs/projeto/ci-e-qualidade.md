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
| **Documentação** | `.github/workflows/docs.yml` | push em `main` tocando `website/` ou `persona_db/`, e `workflow_dispatch` | gera a documentação automática, constrói o Docusaurus e publica no GitHub Pages |
| **Jekyll (legado)** | `.github/workflows/jekyll-gh-pages.yml` | push em `main` | publicação antiga, baseada em Jekyll |

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

:::caution Conflito de publicação
`docs.yml` e `jekyll-gh-pages.yml` publicam no mesmo ambiente `github-pages`. Quando os dois rodam
no mesmo push, o último a terminar substitui o site. Desative o workflow do Jekyll em
**Actions → Deploy Jekyll with GitHub Pages dependencies preinstalled → Disable workflow** para
manter apenas esta documentação no ar.
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
