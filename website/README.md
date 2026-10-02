# Documentação do PersonaDB

Site [Docusaurus 3](https://docusaurus.io/) com a documentação completa do PersonaDB, em
português do Brasil.

## Rodar localmente

```bash
cd website
npm install
npm start            # http://localhost:3000/PersonaDB/docs/
```

## Scripts

| Script | Descrição |
|---|---|
| `npm run gen:docs` | Gera a documentação automática a partir do código (só precisa de Python 3, sem dependências) |
| `npm start` | `gen:docs` + servidor de desenvolvimento |
| `npm run build` | `gen:docs` + build estático em `build/` |
| `npm run serve` | Serve o build local |
| `npm run typecheck` | Checagem de tipos da configuração TypeScript |

## O que é gerado automaticamente

`scripts/generate_reference.py` lê o código-fonte do repositório e escreve:

- `docs/referencia-api/**` — uma página por módulo Python (docstrings, assinaturas, links para o GitHub);
- `docs/schema/**` — uma página por arquivo DDL (colunas, FKs, ENUMs, índices, diagramas ER);
- `docs/geradores/catalogo.md` — os 24 geradores, ordem no pipeline e tabelas populadas;
- `docs/validadores/regras.md` — catálogo das regras de validação;
- `src/data/stats.json` — métricas exibidas na página inicial.

Esses arquivos **não são versionados** (exceto `stats.json`): são regenerados a cada `npm start` /
`npm run build`. Todo o restante de `docs/` é escrito à mão.

## Publicação

O workflow `.github/workflows/docs.yml` publica automaticamente em
<https://havaianasdestruido.github.io/PersonaDB/docs/> a cada push na `main`. O mesmo workflow
constrói a raiz do repositório com Jekyll (`https://havaianasdestruido.github.io/PersonaDB/`) e
acopla esta documentação em `/docs`, porque o GitHub Pages publica um único artefato por
repositório. Em pull requests o build roda sem publicar.
