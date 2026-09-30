# Modelos Matemáticos e Probabilísticos — PersonaDB

Este documento detalha a formulação matemática, os parâmetros de calibração, as referências estatísticas e as simplificações adotadas em cada motor do **PersonaDB** (`persona_db/engines/`).

---

## 1. Motor de Aleatoriedade Determinística (`engines/rng.py` — `SeededRNG`)

### Formulação
Todo o sistema é determinístico a partir de uma semente inteira mestre $S_0 \in \mathbb{N}$. Para isolar domínios e personas sem dependência de ordem de chamada, cada sub-gerador é derivado via hash criptográfico **BLAKE2b**:

$$S(p, d, \text{salt}) = \text{int64}_{\text{big}}\!\left(\text{BLAKE2b}\!\left(\text{UTF8}(S_0 \,\|\, p \,\|\, d \,\|\, \text{salt})\right)_{0..7}\right)$$

onde $p$ é o UUID da persona e $d$ é o identificador do domínio (ex.: `"gen03-saude"`, `"gen05-carreira"`). O gerador subjacente utiliza o permutador **PCG64** do NumPy (`numpy.random.default_rng`).

### Distribuições Suportadas
- **Normal truncada**: $X = \min(\max(Y, a), b)$ com $Y \sim \mathcal{N}(\mu, \sigma^2)$.
- **Log-Normal**: $X = \exp(\mu + \sigma Z)$, $Z \sim \mathcal{N}(0, 1)$, com $\mathbb{E}[X] = e^{\mu + \sigma^2/2}$.
- **Poisson**: $\mathbb{P}(K = k) = \frac{\lambda^k e^{-\lambda}}{k!}$.
- **Beta**: $f(x;\alpha,\beta) = \frac{x^{\alpha-1}(1-x)^{\beta-1}}{\text{B}(\alpha,\beta)}$ em $[0,1]$.
- **Dirichlet**: $\mathbf{x} \sim \text{Dir}(\boldsymbol{\alpha})$ no simplex $\sum_i x_i = 1$.

---

## 2. Motor Genético (`engines/genetics.py` — `GeneticEngine`)

### 2.1 Sistema ABO e Fator Rh (Quadrado de Punnett)
- **Alelos ABO**: $\{I^A, I^B, i\}$, onde $I^A$ e $I^B$ são codominantes e $i$ é recessivo:
  - Fenótipo $A \in \{(I^A, I^A), (I^A, i)\}$
  - Fenótipo $B \in \{(I^B, I^B), (I^B, i)\}$
  - Fenótipo $AB = \{(I^A, I^B)\}$
  - Fenótipo $O = \{(i, i)\}$
- **Fator Rh**: alelo dominante $D$ versus recessivo $d$. Dois pais $\text{Rh}^-$ $(d,d) \times (d,d)$ geram exclusivamente filhos $\text{Rh}^-$.
- **Priors populacionais brasileiros**: $O: 47\%$, $A: 41\%$, $B: 9\%$, $AB: 3\%$, $\text{Rh}^+: 87\%$, $\text{Rh}^-: 13\%$.

### 2.2 Cor dos Olhos (Modelo Poligênico Simplificado OCA2/HERC2)
Representada por 2 loci equivalentes com alelos $\{B, G, g, b\}$ ($B$: castanho dominante; $G$: verde intermediário; $g$: avelã; $b$: azul recessivo). Pais homozigotos recessivos $(b,b) \times (b,b)$ não geram descendentes de olhos castanhos.

### 2.3 Lateralidade Manual (Modelo Logístico Familiar)
A probabilidade de um indivíduo ser canhoto dado o fenótipo dos pais segue:

$$\text{logit}\!\left(\mathbb{P}(\text{canhoto})\right) = -2.10 + 0.69 \cdot \mathbb{I}(\text{pai canhoto}) + 0.55 \cdot \mathbb{I}(\text{mãe canhota})$$

Resultando em $\approx 10.9\%$ quando nenhum dos pais é canhoto e $\approx 30.0\%$ quando ambos são canhotos.

### 2.4 Estatura Adulta (Fórmula Mid-Parent de Galton)
A estatura esperada do filho em centímetros é modelada com regressão à média e dimorfismo sexual ($\pm 8\%$):

$$\mu_{\text{altura}} = \begin{cases}
\frac{H_{\text{pai}} + 1.08 \, H_{\text{mãe}}}{2}, & \text{se masculino} \\[4pt]
\frac{0.923 \, H_{\text{pai}} + H_{\text{mãe}}}{2}, & \text{se feminino}
\end{cases}, \qquad H_{\text{filho}} \sim \mathcal{N}(\mu_{\text{altura}}, 6.5^2)$$

O peso adulto deriva de um IMC log-normal correlacionado com idade e condições metabólicas: $W = \text{IMC} \cdot (H/100)^2$.

---

## 3. Motor Socioeconômico (`engines/socio.py` — `SocioeconomicEngine`)

### 3.1 Mobilidade Intergeracional de Classe Social (Cadeia de Markov)
As 6 classes socioeconômicas brasileiras (critério ABEP/IBGE: $A, B_1, B_2, C_1, C_2, D/E$) têm distribuição estacionária:

$$\pi = (0.03,\; 0.07,\; 0.15,\; 0.22,\; 0.25,\; 0.28)$$

Para filhos com pais conhecidos, a transição segue a matriz estocástica $P_{6 \times 6}$ com diagonal dominante ($P_{ii} \in [0.55, 0.62]$), capturando a persistência intergeracional de renda.

### 3.2 Escolaridade (Modelo Logit Multinomial)
A utilidade latente de atingir o nível $k \in \{\text{fundamental}, \text{médio}, \text{superior}, \text{pós}\}$ depende da escolaridade parental, desvio-padrão de renda familiar $z_{\text{renda}}$ e prêmio de classe:

$$\eta_k = \alpha_k + \beta_{k,\text{pais}} + 0.23 \cdot z_{\text{renda}} \cdot \gamma_k + \delta_{k,\text{classe}}, \qquad \mathbb{P}(E = k) = \frac{e^{\eta_k}}{\sum_j e^{\eta_j}}$$

### 3.3 Equação Salarial de Mincer (Log-Normal)
O salário base anual segue uma equação minceriana com retorno côncavo à experiência ($t$ anos), prêmio educacional, diferencial setorial, penalidades demográficas e bônus de rede familiar (nepotismo):

$$\ln(w) = 5.20 + \beta_{\text{edu}} + 0.022\,t - 0.0002\,t^2 + \beta_{\text{setor}} - 0.14\,\mathbb{I}(\text{fem}) - 0.11\,\mathbb{I}(\text{minoria}) + \beta_{\text{nepotismo}} + \varepsilon$$

onde $\varepsilon \sim \mathcal{N}(0, 0.35^2)$ e o salário mensal respeita estritamente o piso histórico `MIN_WAGE_HISTORY` vigente no ano de contratação.

---

## 4. Motor Epidemiológico e de Sobrevivência (`engines/health.py` — `HealthEngine`)

### 4.1 Mortalidade de Gompertz-Makeham e Função de Sobrevivência
A força de mortalidade total $h(t)$ combina um risco basal por sexo com a soma das taxas de hazard específicas por doença $d$:

$$h(t) = h_0(\text{sexo}) + \sum_{d} \lambda_d(t, \text{sexo}), \qquad S(t) = \exp\!\left(-\int_0^t h(u)\,du\right)$$

Para neoplasias (`cancer`), o hazard segue a lei exponencial de Gompertz:

$$\lambda_{\text{cancer}}(t) = a \, e^{b t}, \qquad a = 3 \times 10^{-4},\; b = 0.085$$

### 4.2 Predisposição Genética e Impacto Socioeconômico
Indivíduos com predisposição familiar registrada em `predisposicao_genetica` sofrem multiplicador de risco $\times 1.9$. Doenças graves impõem redução salarial esperada e aumento na probabilidade de licença médica e evasão escolar.

---

## 5. Motor Jurídico e Criminal (`engines/criminal.py` — `CriminalEngine`)

### 5.1 Risco Logístico de Envolvimento Criminal
A probabilidade de envolvimento criminal na vida adulta ($\ge 18$ anos) é dada por:

$$\text{logit}(p_{\text{crime}}) = -3.50 + 1.80\,\mathbb{I}(\text{masc}) + 0.90\,\mathbb{I}(15 \le \text{idade} \le 25) + 0.70\,\mathbb{I}(\text{classe } D/E) + 1.10\,\mathbb{I}(\text{pai crim.}) + 0.50\,\mathbb{I}(\text{desemp.}) - 0.90\,\mathbb{I}(\text{sup.})$$

### 5.2 Reincidência e Impacto Trabalhista
A probabilidade de reincidência em 5 anos parte de $0.42$, sendo reduzida por emprego formal ($-0.30$) e suporte familiar ($-0.20$). Antecedentes criminais aplicam multiplicador de contratação $0.45$ e bloqueiam ingresso em cargos públicos e no setor financeiro regulado.

---

## 6. Motor de Nupcialidade e Fecundidade (`engines/family.py` — `FamilyEngine`)

- **Idade ao primeiro casamento**: truncada acima do mínimo legal brasileiro ($16$ anos, com concentração adulta $\ge 18.5$ anos), $\mathcal{N}(30, 4^2)$ para homens e $\mathcal{N}(27, 4^2)$ para mulheres.
- **Homogamia**: $58\%$ de casamentos ocorrem dentro da mesma classe social e o restante em classes adjacentes.
- **Fecundidade**: $N_{\text{filhos}} \sim \text{Poisson}(\lambda_{\text{classe}})$ com $\lambda_{A/B} = 1.4$, $\lambda_{C_1} = 1.9$ e $\lambda_{C_2/D/E} = 2.6$.
- **Divórcio**: modelo logístico modulado por desemprego prolongado ($+0.5$), antecedente criminal do cônjuge ($+1.2$), diferença de classe ($+0.3$), filhos pequenos ($-0.4$) e alta religiosidade ($-0.5$).

---

## 7. Motor Geográfico e Migratório (`engines/geography.py` — `GeographyEngine`)

- **Alocação urbana**: ponderação populacional (lei de Zipf aproximada) sobre 60 cidades fictícias brasileiras nas 5 macrorregiões, cruzada com o perfil de classe da cidade.
- **Segregação intraurbana**: seleção de bairros estratificados por faixa socioeconômica (`alto`, `medio`, `popular`).
- **Migração interna**: probabilidade anual de mudança residencial modulada por idade jovem-adulta, ascensão educacional e eventos de casamento/divórcio.
