---
title: Documentação e site
sidebar_label: Documentação
sidebar_position: 5
description: Como este site é construído, como regenerar as páginas automáticas e como publicar.
---

# Documentação e site

Este site é um [Docusaurus 3](https://docusaurus.io/) em `website/`, com parte do conteúdo escrito à
mão e parte **gerada a partir do código-fonte**.

## Rodar localmente

```bash
cd website
npm install
npm start          # http://localhost:3000/PersonaDB/
```

| Script | O que faz |
|---|---|
| `npm run gen:docs` | Executa `scripts/generate_reference.py` (apenas stdlib do Python) |
| `npm start` | Regenera a documentação automática e sobe o servidor de desenvolvimento |
| `npm run build` | Regenera e constrói o site estático em `website/build/` |
| `npm run serve` | Serve o build local |
| `npm run typecheck` | Checa os tipos TypeScript da configuração |
| `npm run clear` | Limpa o cache do Docusaurus |

Os hooks `prestart` e `prebuild` chamam `gen:docs`, então as páginas automáticas nunca ficam
desatualizadas em um build limpo.

## O que é gerado

| Destino | Origem | Versionado? |
|---|---|---|
| `docs/referencia-api/**` | análise `ast` de todos os módulos de `persona_db/` | não |
| `docs/schema/**` | parsing dos DDL em `persona_db/sql/schema/*.sql` | não |
| `docs/geradores/catalogo.md` | docstrings + tabelas detectadas nos geradores | não |
| `docs/validadores/regras.md` | literais `"rule": "…"` nos validadores | não |
| `src/data/stats.json` | contagens usadas na página inicial | sim |

Tudo o mais em `docs/` é escrito à mão.

```mermaid
flowchart LR
    PY["persona_db/**/*.py"] --> GEN[generate_reference.py]
    SQL["persona_db/sql/schema/*.sql"] --> GEN
    GEN --> API["docs/referencia-api/**"]
    GEN --> SCH["docs/schema/**"]
    GEN --> CAT["docs/geradores/catalogo.md"]
    GEN --> RUL["docs/validadores/regras.md"]
    GEN --> ST["src/data/stats.json"]
    API & SCH & CAT & RUL & ST --> DOC[Docusaurus build]
```

## Como o gerador funciona

`website/scripts/generate_reference.py` usa **somente a biblioteca padrão** — não importa
`persona_db`, portanto não precisa de `numpy`, `scipy` nem de qualquer dependência instalada. Isso
mantém o build do site rápido e independente do ambiente Python do projeto.

Para cada módulo ele extrai docstring, constantes, classes (com atributos e métodos públicos),
funções com assinatura completa e número da linha, gerando links diretos para o GitHub. Para cada
arquivo DDL, extrai tabelas, colunas, tipos, nulidade, defaults, `CHECK`, chaves estrangeiras,
ENUMs, funções, views, triggers e índices, além de montar o diagrama ER em Mermaid.

A ligação **tabela → gerador responsável** é inferida cruzando os nomes de tabela do DDL com as
chaves de dicionário efetivamente escritas por cada gerador (padrões `rows = {"tabela": []}`,
`rows["tabela"].append(...)` e `rows.setdefault("tabela", [])`).

## Escrevendo páginas à mão

- Arquivos `.md` são interpretados como **CommonMark** (`markdown.format: 'detect'`); use `.mdx`
  apenas se precisar de JSX.
- Front matter recomendado: `title`, `sidebar_label`, `sidebar_position`, `description`.
- Matemática com KaTeX: `$inline$` e `$$bloco$$`.
- Diagramas com blocos ```` ```mermaid ````.
- Admonições: `:::tip`, `:::note`, `:::info`, `:::caution`, `:::danger`.
- Links entre páginas devem usar caminhos relativos com extensão (`../motores/rng.md`), para que o
  Docusaurus valide links quebrados no build.

Páginas novas escritas à mão precisam ser adicionadas a `website/sidebars.ts` (a sidebar principal
é explícita; as de API e schema são autogeradas a partir dos diretórios).

## Publicação

O workflow `.github/workflows/docs.yml` constrói e publica o site no GitHub Pages a cada push na
branch `main` que toque em `website/`, `persona_db/` ou no próprio workflow — e também sob demanda
(`workflow_dispatch`).

A URL publicada é `https://havaianasdestruido.github.io/PersonaDB/`, configurada em
`docusaurus.config.ts` por `url` + `baseUrl`.

:::caution Dois workflows publicam no Pages
O repositório mantém o workflow legado `jekyll-gh-pages.yml`, que também publica em `main`. Como os
dois usam o mesmo ambiente `github-pages`, o último a concluir sobrescreve o anterior. Para
publicar somente este site, desative o workflow do Jekyll em **Actions → Deploy Jekyll with GitHub
Pages dependencies preinstalled → Disable workflow**.
:::

## Fontes auxiliares

| Arquivo do repositório | Papel na documentação |
|---|---|
| `README.MD` | resumo e quick start (espelhado em [Introdução](../intro.md)) |
| `PERSONA.MD` | especificação conceitual das entidades |
| `persona_db/docs/MATH_MODELS.md` | formulação matemática de referência dos motores |
| `persona_db/docs/SCHEMA.md` | dicionário de dados versionado, gerado por `document_schema.py` |
| `TODO.MD` | backlog por tarefa |
| `rewrite.MD` | estudo de performance (não implementado) |
