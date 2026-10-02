---
title: "Motor socioeconômico (socio.py)"
sidebar_label: socio — classe e renda
sidebar_position: 2
description: Mobilidade social de Markov, escolaridade logit, equação de Mincer e nepotismo.
---

# `SocioeconomicEngine` — classe, escolaridade e renda

Arquivo: [`persona_db/engines/socio.py`](../referencia-api/engines/socio.md)

## 1. Classe social e mobilidade intergeracional

As seis classes do critério ABEP (`A`, `B1`, `B2`, `C1`, `C2`, `D_E`) têm distribuição marginal:

$$\pi = (0{,}03,\; 0{,}07,\; 0{,}15,\; 0{,}22,\; 0{,}25,\; 0{,}28)$$

Quando a classe dos pais é conhecida, o sorteio usa a linha correspondente da matriz estocástica
$P_{6\times 6}$, com diagonal dominante (persistência intergeracional):

| Pais ↓ / Filho → | A | B1 | B2 | C1 | C2 | D_E |
|---|---|---|---|---|---|---|
| **A** | 0,62 | 0,20 | 0,10 | 0,05 | 0,02 | 0,01 |
| **B1** | 0,08 | 0,55 | 0,22 | 0,10 | 0,03 | 0,02 |
| **B2** | 0,03 | 0,10 | 0,58 | 0,20 | 0,06 | 0,03 |
| **C1** | 0,01 | 0,04 | 0,12 | 0,56 | 0,18 | 0,09 |
| **C2** | 0,01 | 0,02 | 0,06 | 0,16 | 0,57 | 0,18 |
| **D_E** | 0,01 | 0,01 | 0,04 | 0,10 | 0,24 | 0,60 |

```python
SocioeconomicEngine.sample_class(rng, parent_class="C2")   # → "C2" em ~57% dos casos
SocioeconomicEngine.sample_class(rng, parent_class=None)   # usa a marginal π
```

Toda linha soma exatamente 1 — há um teste unitário dedicado a isso.

## 2. Escolaridade (logit multinomial)

A utilidade latente de cada nível $k \in \{\text{fundamental}, \text{médio}, \text{superior}, \text{pós}\}$ é:

$$\eta_k = \alpha_k + \beta_{k,\text{pais}} + 0{,}23 \cdot z_{\text{renda}} \cdot \gamma_k + \delta_{k,\text{classe}},
\qquad \mathbb{P}(E = k) = \frac{e^{\eta_k}}{\sum_j e^{\eta_j}}$$

O prêmio de classe $\delta$ incide sobre `superior` e `pos`:

| Classe | Δ superior | Δ pós |
|---|---|---|
| A | +0,55 | +0,70 |
| B1 | +0,30 | +0,35 |
| B2 | +0,10 | +0,05 |
| C1 | 0,00 | −0,10 |
| C2 | −0,15 | −0,20 |
| D_E | −0,35 | −0,30 |

O softmax é estabilizado subtraindo o máximo antes da exponenciação.

## 3. Salário — equação de Mincer

$$\ln(w) = 5{,}20 + \beta_{\text{edu}} + 0{,}022\,t - 0{,}0002\,t^2 + \beta_{\text{setor}}
- 0{,}14\,\mathbb{I}(\text{fem}) - 0{,}11\,\mathbb{I}(\text{minoria}) + \beta_{\text{nep}} + \varepsilon$$

com $t$ = anos de experiência e $\varepsilon \sim \mathcal{N}(0; 0{,}35^2)$.

| Componente | Valores |
|---|---|
| Prêmio educacional $\beta_{\text{edu}}$ | fundamental 0,00 · médio 0,35 · superior 0,85 · pós 1,25 |
| Deslocamento setorial $\beta_{\text{setor}}$ | financeiro +0,14 · tecnologia +0,10 · público +0,06 · saúde +0,03 · indústria +0,02 · aberto 0,00 · comércio −0,02 · educação −0,04 · construção −0,06 · agro −0,08 |
| Penalidades | mulher −0,14 · minoria racial −0,11 |
| Retorno à experiência | côncavo, máximo em $t = 55$ anos |

O resultado é arredondado em duas casas e **limitado inferiormente em R$ 1 200**. O gerador de
carreira ainda aplica o piso histórico do salário mínimo do ano da contratação
(`MIN_WAGE_HISTORY`), que pode ser superior.

```python
SocioeconomicEngine.salary(
    rng, education="superior", experience_years=12, sector="tecnologia",
    gender_female=False, race_minority=False, nepotism_log_bonus=0.0,
)   # → valor bruto anual em BRL, com piso de 1 200; veja a nota abaixo
```

:::note Escala do valor
A docstring descreve o retorno como **salário bruto anual em BRL**, mas o intercepto 5,20 em escala
logarítmica corresponde a apenas $e^{5{,}20} \approx 181$ unidades — ou seja, na prática o número
funciona como um **índice de escala**, não como reais.

`gen_05_carreira` o trata exatamente assim: divide por 1 200, multiplica pelo piso do ano
(`max(piso, 1320)`) e pelos multiplicadores de classe e escolaridade para chegar ao
`salario_mensal`; a `renda_anual` sai de `salario_mensal × 13,3` (12 meses + 13º + férias).
:::

## 4. Influência familiar (nepotismo)

```python
SocioeconomicEngine.family_influence_weight(rng, sector_career="financeiro", sector_parent="financeiro")
```

Se o progenitor atua no mesmo setor escolhido, há 32% de chance de aplicar um multiplicador
uniforme em $[1{,}00;\ 1{,}35]$ sobre as chances de inserção/salário. Setores diferentes ou
progenitor desconhecido devolvem exatamente `1.0`.

## Como os geradores usam este motor

| Gerador | Uso |
|---|---|
| `gen_00_pessoa` | classe social inicial e setor de emprego |
| `gen_04_educacao` | nível de escolaridade, bolsas, evasão |
| `gen_05_carreira` | salário, promoções, setor, nepotismo |
| `gen_06_financas` | renda como base de patrimônio, crédito e dívidas |
| `gen_07_residencia` | capacidade de compra ou aluguel |
