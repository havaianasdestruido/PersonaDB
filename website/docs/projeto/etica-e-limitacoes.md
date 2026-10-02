---
title: Ética e limitações
sidebar_label: Ética e limitações
sidebar_position: 1
description: Usos legítimos, usos vedados e os limites de validade dos modelos.
---

# Ética e limitações

## Os dados são fictícios

Nenhum registro produzido pelo PersonaDB corresponde a uma pessoa real. Não há ingestão,
anonimização, pseudonimização ou derivação de bases reais: nomes, documentos, endereços, empresas,
hospitais, processos e eventos são **inventados** por catálogos fechados e sorteios determinísticos.

Alguns identificadores têm **formato válido** (por exemplo, CNPJ com dígitos verificadores
corretos) justamente para exercitar validadores de sistemas consumidores. Formato válido não
significa registro legítimo.

## Usos adequados

- testes automatizados, QA e ambientes de staging;
- demonstrações de produto sem expor dados de clientes;
- ensino de modelagem relacional, SQL e estatística aplicada;
- benchmarks de carga e de desempenho;
- pesquisa em geração de dados sintéticos.

## Usos vedados

:::danger Não faça isso
- Preencher cadastros reais, formulários oficiais ou qualquer sistema de produção de terceiros com
  os identificadores gerados.
- Treinar ou avaliar modelos de **decisão sobre pessoas reais** (crédito, contratação, policiamento
  preditivo, seguro) usando estes dados.
- Apresentar os números como estatísticas do Brasil ou de qualquer população real.
- Reidentificar, inferir ou insinuar correspondência entre uma persona e alguém real.
:::

## Limitações dos modelos

| Modelo | Limitação |
|---|---|
| Mobilidade social (Markov) | matriz 6×6 estilizada; ignora região, raça e geração |
| Escolaridade (logit) | coeficientes escolhidos por plausibilidade, não estimados |
| Salários (Mincer) | sem informalidade explícita, sem desemprego de longa duração, sem inflação salarial setorial |
| Mortalidade (Gompertz–Makeham) | hazards de doença tratados como aditivos; não reproduz a tábua do IBGE |
| Genética | modelos poligênicos simplificados (2 loci para cor de olhos); ignora epistasia e penetrância |
| Criminalidade | modelo logístico com coeficientes fictícios; **não** é instrumento preditivo |
| Geografia | 50 cidades e ~500 bairros procedurais; distâncias e CEPs não têm correspondência real |
| Pirâmide etária | aproximação por faixas, sem projeção demográfica |

## O viés é explícito — e intencional

Vários modelos incorporam penalidades de gênero (−0,14 no log-salário), de raça (−0,11) e de
classe (probabilidade de prisão modulada pela qualidade da defesa). Isso existe para que os dados
sintéticos **exercitem** análises de equidade e testes de viés, e está documentado abertamente em
cada motor.

:::caution Não naturalize os coeficientes
Esses valores são parâmetros de simulação escolhidos para gerar desigualdade observável, não
medidas de desigualdade real. Reportar resultados derivados deles como evidência empírica seria
uma leitura equivocada do projeto.
:::

## Reprodutibilidade como prática ética

Como tudo é determinístico, qualquer resultado pode ser auditado: dada a semente, a âncora temporal
e a versão do código, qualquer pessoa reproduz exatamente o mesmo dataset e pode inspecionar como
cada número apareceu. Em dados sintéticos, isso é a melhor defesa contra conclusões não verificáveis.

## Licença

O projeto é distribuído sob a [licença MIT](https://github.com/havaianasdestruido/PersonaDB/blob/main/LICENSE),
que inclui a isenção de garantias usual. A responsabilidade pelo uso dos dados gerados é de quem os
utiliza.
