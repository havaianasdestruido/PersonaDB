---
title: Glossário
sidebar_label: Glossário
sidebar_position: 4
description: Termos técnicos, estatísticos e de domínio usados no PersonaDB.
---

# Glossário

## Conceitos do projeto

**Âncora temporal** — data fixa (`PERSONADB_TODAY`, padrão `2026-01-01`) que substitui o relógio do
sistema em toda a simulação.

**Catálogo** — conjunto fechado de entidades compartilhadas (hospitais, empresas, partidos) criado
por um gerador antes do laço de personas, com IDs `uuid5` estáveis.

**Contrato da persona** — dicionário Python que circula por todos os geradores, enriquecido a cada
etapa. Ver [Contratos de dados](../arquitetura/contratos-de-dados.md).

**Dataset** — `dict[str, list[dict]]` mapeando nome de tabela para linhas, em memória.

**Domínio** — recorte temático do schema (00 a 26), com um arquivo DDL e, em geral, um gerador.

**Enriquecimento** — campos acrescentados ao dicionário da persona por um gerador para uso pelos
seguintes (ex.: `tem_doenca_grave`).

**Fork (de RNG)** — derivação determinística de um sub-gerador a partir de
`(semente, persona_id, domínio, salt)` via BLAKE2b.

**Pipeline** — tupla `DOMAIN_PIPELINE` que fixa a ordem topológica de execução dos geradores.

**Semente mestre** — inteiro que determina todo o dataset (`--seed`).

**Violação** — dicionário produzido por um validador descrevendo uma invariante quebrada.

## Estatística e modelagem

**Cadeia de Markov** — processo em que a próxima classe social depende apenas da classe dos pais,
via matriz de transição.

**Coeficiente de Gini** — medida de desigualdade entre 0 e 1; o projeto usa 0,52 para derivar a
curva de Lorenz.

**Curva de Lorenz** — função que acumula a fração da renda total detida pelos *p*% mais pobres.

**Distribuição de Dirichlet** — distribuição sobre vetores que somam 1; usada para compor
percentuais de ancestralidade.

**Gompertz–Makeham** — modelo de mortalidade com componente exponencial na idade mais um termo
basal constante.

**Hazard (força de mortalidade/incidência)** — taxa instantânea de ocorrência de um evento, dado
que ele ainda não ocorreu.

**Homogamia** — tendência de formar casais com características semelhantes (classe, escolaridade,
religião).

**Logit / regressão logística** — $\text{logit}(p) = \ln\frac{p}{1-p}$; converte um escore linear
em probabilidade.

**Mid-parent (Galton)** — previsão da estatura do filho a partir da média ajustada dos pais, com
regressão à média.

**Equação de Mincer** — modelo log-linear de salários com retornos à educação e à experiência.

**PCG64** — gerador pseudoaleatório padrão do NumPy, usado por `SeededRNG`.

**PRS (escore poligênico de risco)** — escore agregado de predisposição genética a uma condição.

**Quadrado de Punnett** — tabela que enumera os genótipos possíveis dos filhos a partir dos pais.

**Softmax** — normalização exponencial que converte utilidades em probabilidades.

## Termos de domínio (pt-BR)

| Termo | Significado no projeto |
|---|---|
| **ABEP (A, B1, B2, C1, C2, D_E)** | critério de classificação socioeconômica usado como rótulo de classe |
| **Antecedente criminal** | registro que bloqueia setores de emprego e aumenta risco de divórcio |
| **Comparecimento eleitoral** | registro de presença (ou não) de uma persona em uma eleição |
| **Holerite** | contracheque mensal associado a um contrato de trabalho |
| **Patrimônio snapshot** | fotografia do patrimônio líquido estimado em uma data |
| **Pena** | sanção vinculada a uma sentença, com duração em meses |
| **Reputação score** | índice fictício de reputação pública, afetado por mídia e antecedentes |
| **União estável** | relacionamento reconhecido sem casamento civil |

## Siglas

| Sigla | Significado |
|---|---|
| **DDL** | *Data Definition Language* — os arquivos `.sql` que criam o schema |
| **ER** | Entidade-Relacionamento (diagramas Mermaid por domínio) |
| **FK / PK** | chave estrangeira / chave primária |
| **IPCA** | índice de inflação fictício usado para corrigir valores monetários |
| **N:N** | relação muitos-para-muitos, materializada no domínio 25 |
| **RNG** | *Random Number Generator* |
| **UF** | unidade federativa (sigla de duas letras) |
