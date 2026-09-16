# TODO.md — Mega-Schema de Personas Fictícias (PostgreSQL + Motor Probabilístico)

```markdown
# TODO.md
# Mega-Schema de Personas Fictícias
# PostgreSQL + Motor Probabilístico (Python + NumPy/SciPy)
# Ordem de execução: de cima para baixo, sem pular etapas.
# Cada tarefa é uma sessão independente para o Claude Code.

---

## FASE 0 — INFRAESTRUTURA & AMBIENTE

### TASK-001 — Setup do projeto e ambiente Python
- Criar estrutura de diretórios do projeto:
  ```
  persona_db/
  ├── sql/          # DDL e migrations
  ├── engines/      # motores probabilísticos Python
  ├── generators/   # geradores por domínio
  ├── validators/   # validadores de consistência
  ├── seeds/        # dados de referência (lookup tables)
  ├── tests/        # testes de consistência
  └── scripts/      # scripts de orquestração
  ```
- Criar `pyproject.toml` com dependências:
  - psycopg2-binary, numpy, scipy, faker (pt_BR),
    networkx, pandas, sqlalchemy, pydantic, rich, tqdm
- Criar `.env.example` com DATABASE_URL, SEED, N_PESSOAS
- Criar `docker-compose.yml` com PostgreSQL 16 + pgAdmin
- Criar `Makefile` com targets: setup, migrate, generate, validate, reset

---

### TASK-002 — Motor de aleatoriedade controlada (engines/rng.py)
- Classe `SeededRNG` que encapsula `numpy.random.Generator`
- Toda aleatoriedade do projeto DEVE passar por esta classe
- Métodos:
  - `fork(pessoa_id, domain)` → sub-RNG determinístico por pessoa+domínio
  - `bernoulli(p)` → bool
  - `choice(options, weights)` → item
  - `beta_sample(alpha, beta)` → float [0,1]
  - `normal_clipped(mu, sigma, low, high)` → float
  - `dirichlet(alphas)` → array somando 1.0
- Garantia: mesma SEED + mesmo pessoa_id = mesmos dados sempre
- Registrar seed usada na tabela `semente_aleatoria`

---

### TASK-003 — Motor de herança genética (engines/genetics.py)
- Implementar modelo de alelos para traços físicos:

  **Cor dos olhos** (modelo poligênico simplificado OCA2/HERC2):
  ```python
  # Alelos: B=castanho(dominante), b=azul(recessivo), G=verde(intermediário)
  # Genótipos e fenótipos com probabilidades reais:
  # BB, Bb → castanho (~75% pop. brasileira)
  # Gg, bg → verde (~5%)
  # bb → azul (~5%)
  # + influência de ancestralidade
  ```

  **Cor do cabelo** (gene MC1R + ASIP):
  ```python
  # Preto > Castanho > Loiro > Ruivo (dominância)
  # P(ruivo) ≈ 0.01 para ancestralidade europeia
  # P(preto) ≈ 0.85 para ancestralidade africana/indígena
  # Função: herdar_cor_cabelo(alelo_pai, alelo_mae, ancestralidade)
  ```

  **Lateralidade (mão dominante)**:
  ```python
  # P(canhoto) = 0.10 baseline
  # Se pai canhoto: P += 0.09 (OR≈2.0 baseado em estudos)
  # Se mãe canhota: P += 0.07
  # Se ambos canhotos: P = 0.26
  # Modelo logístico: logit(P) = -2.1 + 0.69*pai_canhoto + 0.55*mae_canhota
  ```

  **Tipo sanguíneo** (herança mendeliana ABO + Rh):
  ```python
  # Tabela de Punnett completa para ABO
  # Rh: Rr × Rr → 75% Rh+, 25% Rh-
  # herdar_tipo_sanguineo(tipo_pai, tipo_mae) → tipo_filho
  ```

  **Altura** (herança poligênica):
  ```python
  # Fórmula de mid-parent height:
  # altura_esperada = (altura_pai + altura_mae_corrigida) / 2
  # altura_mae_corrigida = altura_mae * 1.08 (para filho) ou * 0.923 (filha)
  # Residual: Normal(0, 6.5cm) — variância ambiental
  ```

  **Doenças hereditárias** (modelo de risco poligênico):
  ```python
  # PRS (Polygenic Risk Score) simplificado:
  # risco = sigmoid(soma(beta_i * genótipo_i) + efeito_familiar)
  # Condições modeladas: diabetes t2, hipertensão, depressão,
  #   daltonismo (recessivo ligado ao X), fenilcetonúria (recessivo)
  ```

- Todas as funções devem receber `rng: SeededRNG` como parâmetro
- Output: dict com traços e seus valores + probabilidades calculadas

---

### TASK-004 — Motor de probabilidade socioeconômica (engines/socio.py)
- Classe `SocioeconomicEngine`:

  **Classe social** (distribuição brasileira 2024):
  ```python
  # A: 3%, B1: 7%, B2: 15%, C1: 22%, C2: 25%, D-E: 28%
  # Herdabilidade da classe: correlação pai-filho ≈ 0.45
  # P(filho_classe_A | pai_classe_A) → matriz de mobilidade social
  ```

  **Influência familiar no emprego**:
  ```python
  # P(mesmo_setor_que_parente) = 0.32 (nepotismo/influência)
  # P(empresa_familiar) dado parente_na_empresa = 0.18
  # Bonus de salário por nepotismo: LogNormal(mu=0.05, sigma=0.12)
  # Modelar como: setor_emprego ~ Categorical(pesos_setor_familiar * fator_influencia)
  ```

  **Escolaridade**:
  ```python
  # P(nivel_superior | pai_superior) = 0.58
  # P(nivel_superior | pai_fundamental) = 0.11
  # Efeito renda familiar: coeficiente 0.23 por desvio padrão de renda
  ```

  **Salário** (função multivariada):
  ```python
  # log(salário) = β0 + β1*educação + β2*experiência + β3*experiência²
  #              + β4*setor + β5*gênero_gap + β6*raça_gap + ε
  # β valores calibrados para mercado brasileiro
  # ε ~ Normal(0, 0.35)
  ```

---

### TASK-005 — Motor de saúde e doenças (engines/health.py)
- Classe `HealthEngine`:

  **Incidência de doenças por idade/sexo**:
  ```python
  # Tabela de hazard rates (incidência/ano) por doença:
  # diabetes: 0.007/ano após 40 anos
  # hipertensão: 0.015/ano após 35 anos
  # depressão: 0.021/ano, pico 25-44 anos
  # câncer: Gompertz(a=0.0003, b=0.085) — cresce exponencialmente com idade
  
  # Função survival:
  # S(t) = exp(-integral(h(u)du, 0, t))
  # Simular tempo até doença com método inverse CDF
  ```

  **Impacto da doença na vida**:
  ```python
  # Impacto no emprego:
  #   P(demissão | doença_grave) += 0.15
  #   Redução salarial: Beta(2,5) * 0.4 (até 40% menos)
  #   P(afastamento_INSS) = f(gravidade_doença, tipo_contrato)
  
  # Impacto financeiro:
  #   gasto_saude ~ LogNormal(gravidade * 8, 1.2) em R$
  #   P(endividamento | doença_crônica) = 0.34
  
  # Impacto nos relacionamentos:
  #   P(divórcio | doença_mental_grave) *= 1.8
  #   P(depressão_secundária | doença_crônica) = 0.22
  ```

  **Saúde mental**:
  ```python
  # Modelo de fatores de risco acumulados:
  # score_risco = w1*histórico_familiar + w2*trauma + w3*isolamento
  #             + w4*desemprego + w5*divórcio + w6*luto
  # P(transtorno) = sigmoid(score_risco - threshold)
  ```

---

### TASK-006 — Motor criminal e jurídico (engines/criminal.py)
- Classe `CriminalEngine`:

  **Probabilidade de envolvimento criminal**:
  ```python
  # Modelo logístico com fatores de risco:
  # logit(P(crime)) = β0
  #   + β1 * masculino          # +1.8
  #   + β2 * idade_15_25        # +0.9
  #   + β3 * classe_D_E         # +0.7
  #   + β4 * pai_criminal       # +1.1 (maior preditor familiar)
  #   + β5 * mae_criminal       # +0.8
  #   + β6 * irmao_criminal     # +0.6
  #   + β7 * desemprego         # +0.5
  #   + β8 * abandono_escolar   # +0.4
  #   + β9 * transtorno_mental  # +0.3
  #   - β10 * ensino_superior   # -0.9
  #   - β11 * renda_alta        # -0.8
  
  # Tipo de crime por perfil (distribuição multinomial):
  # crimes_violentos, crimes_patrimoniais, crimes_digitais,
  # crimes_de_trânsito, crimes_corporativos, tráfico
  ```

  **Impacto do histórico criminal na vida**:
  ```python
  # Impacto no emprego:
  #   P(contratação | antecedente) *= 0.45
  #   Redução salarial esperada: 25-40%
  #   Setores vetados: público, financeiro, educação
  
  # Impacto nos relacionamentos:
  #   P(divórcio | prisão) = 0.73
  #   P(perda_guarda_filhos | antecedente_violência) = 0.65
  
  # Impacto financeiro:
  #   custo_processo ~ LogNormal(9.5, 0.8) em R$ (advogado + multas)
  #   P(perda_patrimônio | processo_criminal) = 0.28
  
  # Reincidência:
  #   P(reincidência_5anos) = 0.42 (dado Brasil)
  #   Reduzida por: emprego_formal(-0.3), família_suporte(-0.2)
  ```

---

### TASK-007 — Motor de relacionamentos e família (engines/family.py)
- Classe `FamilyEngine`:

  **Probabilidade de casamento/união**:
  ```python
  # Hazard de primeiro casamento por idade:
  # Pico: homens 28-32 anos, mulheres 25-29 anos
  # P(casamento_algum_dia) = 0.72
  # P(divórcio | casado) = 0.21 (Brasil 2023)
  # P(segundo_casamento | divorciado) = 0.38
  ```

  **Número de filhos**:
  ```python
  # Distribuição por classe social:
  # Classe A/B: Poisson(λ=1.4)
  # Classe C: Poisson(λ=1.9)
  # Classe D/E: Poisson(λ=2.6)
  # Modificadores: doença(-0.3), divórcio(-0.2), ensino_superior(-0.4)
  ```

  **Homogamia** (tendência de casar com similar):
  ```python
  # Similaridade de classe social: correlação 0.58
  # Similaridade de escolaridade: correlação 0.55
  # Similaridade de idade: diferença ~ Normal(2.5, 4.2) anos
  # Similaridade de religião: P(mesma_religião) = 0.61
  ```

---

### TASK-008 — Motor de geografia e mobilidade (engines/geography.py)
- Mapas de distribuição populacional por cidade fictícia
- Probabilidade de migração por classe/idade:
  ```python
  # P(migração_cidade) = f(oportunidade_emprego, custo_vida, laços_familiares)
  # Gravity model: fluxo_ij = k * pop_i * pop_j / distância_ij²
  ```
- Correlação bairro ↔ classe social ↔ criminalidade ↔ escola ↔ saúde
- Gerar ~50 cidades fictícias com ~500 bairros com perfis socioeconômicos

---

## FASE 1 — DDL PostgreSQL (sql/schema/)

### TASK-010 — DDL: Hub Central + Domínio 00
```sql
-- Arquivo: sql/schema/00_hub.sql
-- Tabela: pessoa
-- Tipos: ENUM para sexo, estado_civil, nacionalidade
-- Constraints: CHECK (data_nascimento < CURRENT_DATE)
-- Índices: idx_pessoa_data_nascimento, idx_pessoa_sexo
-- Extensions: uuid-ossp, pgcrypto, pg_trgm
```

### TASK-011 — DDL: Domínio 01 — Identidade & Biometria
```sql
-- Arquivo: sql/schema/01_identidade.sql
-- Tabelas: pessoa_nome_anterior, pessoa_apelido, pessoa_documento,
--          pessoa_biometria, pessoa_foto, pessoa_assinatura,
--          pessoa_caracteristica_fisica, pessoa_marca_distintiva,
--          pessoa_idioma
-- Constraints especiais:
--   CHECK (altura BETWEEN 50 AND 250) -- cm
--   CHECK (peso BETWEEN 2 AND 300)    -- kg
--   ENUM cor_olhos: castanho, azul, verde, avelã, cinza, âmbar
--   ENUM cor_cabelo: preto, castanho, loiro, ruivo, grisalho, branco
--   ENUM mao_dominante: direita, esquerda, ambidestro
--   ENUM tipo_sanguineo: A, B, AB, O
--   ENUM fator_rh: positivo, negativo
```

### TASK-012 — DDL: Domínio 02 — Genealogia & Herança
```sql
-- Arquivo: sql/schema/02_genealogia.sql
-- Tabelas: familia, membro_familia, parentesco, arvore_genealogica,
--          heranca, heranca_item, doacao_familiar,
--          condicao_genetica, predisposicao_genetica,
--          ancestralidade_ficticia
-- Constraints:
--   CHECK (grau BETWEEN 1 AND 10)
--   CHECK (percentual_manifestacao BETWEEN 0 AND 100)
--   UNIQUE(pessoa_id_a, pessoa_id_b, tipo_parentesco) em parentesco
-- Índice: idx_parentesco_pessoa_a, idx_parentesco_pessoa_b
```

### TASK-013 — DDL: Domínio 03 — Saúde
```sql
-- Arquivo: sql/schema/03_saude.sql
-- Todas as 28 tabelas do domínio saúde
-- ENUMs: status_doenca, gravidade, tipo_exame, tipo_cirurgia
-- Particionamento: exame_resultado por ano (range partition)
-- Índices compostos: (pessoa_id, data_diagnostico) em doenca_pessoa
```

### TASK-014 — DDL: Domínio 04 — Educação
```sql
-- Arquivo: sql/schema/04_educacao.sql
-- Todas as 13 tabelas de educação
-- ENUMs: nivel_curso, status_matricula, tipo_bolsa
-- CHECK: nota BETWEEN 0 AND 10
-- CHECK: percentual_presenca BETWEEN 0 AND 100
```

### TASK-015 — DDL: Domínio 05 — Carreira & Trabalho
```sql
-- Arquivo: sql/schema/05_carreira.sql
-- Todas as 15 tabelas de carreira
-- ENUMs: tipo_contrato, motivo_saida, tipo_demissao
-- CHECK: salario.valor > 0
-- Constraint: data_fim > data_inicio em contrato_trabalho
-- Índice: idx_historico_emprego_pessoa, idx_contrato_empresa
```

### TASK-016 — DDL: Domínio 06 — Patrimônio & Finanças
```sql
-- Arquivo: sql/schema/06_financas.sql
-- Todas as 16 tabelas financeiras
-- ENUMs: tipo_conta, tipo_transacao, tipo_investimento
-- CHECK: financiamento.taxa_juros BETWEEN 0 AND 500
-- Particionamento: transacao por ano-mês
-- Índice: idx_transacao_conta_data
```

### TASK-017 — DDL: Domínio 07 — Residência
```sql
-- Arquivo: sql/schema/07_residencia.sql
```

### TASK-018 — DDL: Domínio 08 — Relacionamentos & Família Nuclear
```sql
-- Arquivo: sql/schema/08_relacionamentos.sql
-- Constraint: não permitir self-reference (pessoa_id_a != pessoa_id_b)
-- Constraint: datas de casamento coerentes com nascimento
```

### TASK-019 — DDL: Domínios 09-12 (Rede Social, Vida Digital, Jurídico, Eleitoral)
```sql
-- Arquivos: sql/schema/09_rede_social.sql
--           sql/schema/10_vida_digital.sql
--           sql/schema/11_juridico.sql
--           sql/schema/12_eleitoral.sql
-- ENUMs: papel_processo (reu/autor/testemunha/perito)
-- ENUMs: tipo_crime, tipo_pena, status_processo
-- CHECK: voto não pode ser de menor de 16 anos
```

### TASK-020 — DDL: Domínios 13-17 (Viagens, Pets, Consumo, Timeline, Comportamento)
```sql
-- Arquivos: sql/schema/13_viagens.sql ... sql/schema/17_comportamento.sql
```

### TASK-021 — DDL: Domínios 18-25 (Religião, Esporte, Militar, Imigração,
--                                   Comunicação, Mídia, Meta, Junções N:N)
```sql
-- Arquivos: sql/schema/18_religiao.sql ... sql/schema/25_juncoes.sql
-- Tabela meta: fonte_dado, versao_registro, log_alteracao,
--              auditoria, regra_geracao, semente_aleatoria,
--              validacao_consistencia, exportacao_dataset
```

### TASK-022 — DDL: Views, Triggers e Functions PostgreSQL
```sql
-- Arquivo: sql/schema/99_functions.sql
-- FUNCTION: calcular_idade(data_nascimento) → integer
-- FUNCTION: validar_tipo_sanguineo_filho(tipo_pai, tipo_mae, tipo_filho) → bool
-- TRIGGER: ao inserir em pessoa, auto-criar semente_aleatoria
-- TRIGGER: ao inserir antecedente_criminal, atualizar reputacao_score
-- TRIGGER: log_alteracao automático via trigger genérico
-- VIEW: v_pessoa_completa (join das tabelas mais comuns)
-- VIEW: v_perfil_criminal (pessoa + processos + antecedentes + impactos)
-- VIEW: v_arvore_familiar (CTE recursiva para genealogia)
-- MATERIALIZED VIEW: mv_estatisticas_populacao
```

### TASK-023 — DDL: Índices de performance e particionamento
```sql
-- Arquivo: sql/schema/98_indexes.sql
-- Índices GIN para buscas em JSONB (se usado)
-- Índices BTREE compostos para queries frequentes
-- Particionamento: transacao (por ano), exame_resultado (por ano)
-- CLUSTER nas tabelas mais acessadas
-- Estatísticas customizadas: ALTER TABLE ... ALTER COLUMN ... SET STATISTICS 500
```

---

## FASE 2 — SEEDS (dados de referência)

### TASK-030 — Seeds: lookup tables e dados fixos
```python
# Arquivo: seeds/lookup_data.py
# Gerar e inserir via SQL/Python:

# Lista de ~200 nomes fictícios masculinos brasileiros
# Lista de ~200 nomes fictícios femininos brasileiros  
# Lista de ~300 sobrenomes fictícios brasileiros
# 50 cidades fictícias com estados, regiões e perfis socioeconômicos
# 30 bancos fictícios com códigos
# 100 empresas fictícias com CNPJs gerados via algoritmo (válido mas fictício)
# 50 instituições de ensino fictícias (universidades, faculdades, escolas)
# 30 hospitais fictícios
# 20 partidos políticos fictícios
# Lista de 500+ profissões com setor, nível hierárquico e salário mediano
# Lista de 200+ doenças fictícias categorizadas
# Lista de 100+ medicamentos fictícios com princípios ativos fictícios
# Lista de 50+ cursos universitários com duração
# Lista de raças de pets (cães, gatos, outros)
# Tabelas de salário mínimo histórico fictício (2000-2024)
# Tabela IPCA fictício mensal para correção monetária
```

### TASK-031 — Seeds: tabelas de probabilidade calibradas
```python
# Arquivo: seeds/probability_tables.py
# Gerar tabelas de lookup usadas pelos motores:

# Matriz de mobilidade social (5x5): P(classe_filho | classe_pai)
# Tabela de mortalidade por idade/sexo (tábua de vida)
# Distribuição de doenças por faixa etária e sexo
# Distribuição de crimes por perfil demográfico
# Taxas de emprego por setor/escolaridade/idade
# Distribuição de renda por percentil (curva de Lorenz)
# Matriz de ancestralidade → traços físicos prováveis
```

---

## FASE 3 — GERADORES POR DOMÍNIO

### TASK-040 — Generator: Hub Central — Pessoa base
```python
# Arquivo: generators/gen_00_pessoa.py
# Classe PessoaGenerator:
#   - Gerar N pessoas base sem dependências entre si
#   - Atribuir pessoa_id (UUID v4)
#   - Nome: escolhido por região/ancestralidade
#   - Data nascimento: distribuição etária realista (não uniforme)
#     Usar distribuição piramidal populacional brasileira
#   - Sexo: P(feminino)=0.51, P(masculino)=0.49
#   - Local nascimento: ponderado por população das cidades fictícias
#   - Registrar seed em semente_aleatoria
# Output: lista de dicts prontos para INSERT em lote (COPY)
```

### TASK-041 — Generator: Genealogia (requer TASK-040)
```python
# Arquivo: generators/gen_02_genealogia.py
# ATENÇÃO: deve rodar ANTES dos demais para estabelecer parentesco
# 
# Algoritmo de geração de famílias:
# 1. Agrupar pessoas em núcleos familiares
# 2. Para cada núcleo: designar pais (geração G0)
# 3. Gerar filhos (G1) com datas coerentes (mãe 16-45 anos no parto)
# 4. Calcular avós fictícios (G-1) mesmo que não sejam pessoas completas
# 5. Registrar arvore_genealogica com ramo paterno/materno
# 6. Aplicar engines/genetics.py para herdar traços dos pais
# 
# Output: tabelas familia, membro_familia, parentesco, arvore_genealogica
# Dependência cruzada: os traços físicos (TASK-042) dependem deste output
```

### TASK-042 — Generator: Identidade & Biometria (requer TASK-041)
```python
# Arquivo: generators/gen_01_identidade.py
# 
# pessoa_caracteristica_fisica:
#   - cor_olhos: via engines/genetics.py (herança mendeliana dos pais)
#   - cor_cabelo: via engines/genetics.py (herança dos pais + ancestralidade)
#   - mao_dominante: via engines/genetics.py (modelo logístico familiar)
#   - tipo_sanguineo: via engines/genetics.py (Punnett dos pais)
#   - fator_rh: via engines/genetics.py
#   - altura: mid-parent formula + residual Normal
#   - peso: correlacionado com altura (BMI ~ LogNormal), modificado por doença
#
# pessoa_documento:
#   - CPF: gerar número fictício com dígitos verificadores VÁLIDOS
#   - RG: formato por estado de nascimento
#   - Passaporte: se viajou ao exterior (verificar com TASK-056)
#   - CNH: P(tem_CNH | idade>=18) = f(classe_social, cidade)
#
# pessoa_biometria:
#   - hash_facial_ficticio: SHA256 de (pessoa_id + "face")
#   - impressao_digital_ficticia: string hexadecimal 40 chars
#   - padrao_iris_ficticio: string base64 de 64 chars
#
# pessoa_nome_anterior:
#   - P(mudança_nome) = P(casamento)*0.4 + P(divórcio)*0.1 + 0.01
#
# pessoa_idioma:
#   - Português: 100% para brasileiros natos
#   - Inglês: P(fluente) = f(escolaridade, classe_social)
#   - Espanhol: P(básico) = 0.25 para regiões de fronteira
```

### TASK-043 — Generator: Saúde (requer TASK-041, TASK-042)
```python
# Arquivo: generators/gen_03_saude.py
#
# Algoritmo principal (por pessoa):
# 1. Calcular risco base por idade/sexo/ancestralidade
# 2. Adicionar risco hereditário via predisposicao_genetica
# 3. Para cada doença no catálogo, simular tempo_até_diagnóstico
#    usando método de Monte Carlo com taxa de hazard
# 4. Se tempo <= idade_atual: inserir em doenca_pessoa
# 5. Gerar tratamentos, medicamentos, cirurgias como consequência
# 6. Calcular impactos: registrar em tabela auxiliar para uso por outros generators
#
# Saúde mental:
# - Calcular score_estresse acumulado ao longo da vida simulada
# - P(transtorno_mental) = sigmoid(score_estresse)
# - Gerar sessoes_terapia se terapia iniciada
#
# Vacinas: protocolo padrão SUS fictício por idade
# Alergias: P(alergia_alguma) = 0.30
#
# Output inclui: impactos_saude dict para uso em TASK-044, TASK-045, TASK-047
```

### TASK-044 — Generator: Educação (requer TASK-041, TASK-043)
```python
# Arquivo: generators/gen_04_educacao.py
#
# Algoritmo de trajetória educacional:
# 1. Determinar nível máximo de educação via:
#    logit(P(superior)) = f(escolaridade_pais, renda_familiar, região)
# 2. Simular matrícula, notas (Normal por dificuldade do curso),
#    frequência, reprovações, conclusão
# 3. Notas correlacionadas com: inteligência latente (variável oculta),
#    saúde_mental (se transtorno: -15% nas notas), 
#    trabalho paralelo (se empregado: -8% nas notas)
# 4. Bolsas de estudo: P(bolsa) = f(renda_familiar, notas)
# 5. Estágios: P(estágio) = P(cursando_superior) * 0.65
#
# Impacto de doença na educação:
#   Se doença grave durante período escolar:
#     P(abandono) += 0.25
#     frequencia_escolar -= Beta(2,5) * 30%
```

### TASK-045 — Generator: Carreira & Trabalho (requer TASK-044, TASK-043, TASK-006)
```python
# Arquivo: generators/gen_05_carreira.py
#
# Algoritmo de histórico de emprego:
# 1. Calcular idade de entrada no mercado: f(escolaridade)
# 2. Para cada período de vida adulta:
#    a. P(empregado) = f(idade, escolaridade, saúde, antecedente_criminal)
#    b. Se antecedente criminal: reduzir P(contratação) em setores específicos
#    c. Setor de emprego: influenciado por parentes (TASK-041)
#       P(mesmo_setor_pai) = 0.25 + influencia_familiar
#       P(empresa_familiar) = 0.12 se pai/mãe tem empresa
#    d. Salário: engines/socio.py com todos os modificadores
#    e. Simular promoções: P(promoção_anual) = f(nota_avaliação, tempo_casa)
#    f. Simular demissão: P(demissão | ano) = f(saúde, crime, avaliação, economia)
# 3. Se doença grave: gerar licenca_trabalho ou demissão
# 4. Calcular holerite com descontos (INSS, IR) por faixa
#
# Nepotismo (engines/socio.py):
#   Verificar parentesco com funcionários da mesma empresa
#   Registrar em colega_trabalho com flag influencia_familiar
```

### TASK-046 — Generator: Patrimônio & Finanças (requer TASK-045, TASK-043)
```python
# Arquivo: generators/gen_06_financas.py
#
# Simulação financeira temporal (mês a mês):
# 1. Saldo inicial = herança recebida (TASK-041) + patrimônio acumulado
# 2. Para cada mês de vida adulta:
#    receita = salario_liquido + rendimentos_investimentos
#    gastos_fixos = f(residencia, filhos, saude, dividas)
#    gastos_variaveis ~ LogNormal(mu_classe, sigma=0.3)
#    saldo += receita - gastos_fixos - gastos_variaveis
#    
#    Se saldo < 0: gerar divida com banco
#    Se doença grave no mês: gasto_saude_extra ~ LogNormal(8, 1.5)
#    Se processo_criminal: gasto_juridico ~ LogNormal(9, 0.8)
#
# 3. Investimentos: P(investe) = f(classe_social, escolaridade)
#    tipo_investimento: poupança(classe_D_E), CDB(classe_C), fundos(classe_B), ações(classe_A)
#
# 4. Imóvel:
#    P(imovel_proprio) = f(classe_social, idade, estado_civil)
#    Gerar financiamento_imobiliario se necessário
#    valor_imovel ~ LogNormal calibrado por cidade/bairro fictício
#
# 5. Veículo:
#    P(tem_veiculo) = f(classe_social, cidade, renda)
#    ano_fabricacao correlacionado com renda
```

### TASK-047 — Generator: Jurídico & Criminal (requer TASK-041, TASK-044, TASK-045, TASK-006)
```python
# Arquivo: generators/gen_11_juridico.py
#
# Algoritmo criminal:
# 1. Calcular P(envolvimento_criminal) via engines/criminal.py
#    usando todos os fatores de risco disponíveis
# 2. Se cometeu crime:
#    a. Determinar tipo via distribuição multinomial por perfil
#    b. P(foi_preso) = f(tipo_crime, classe_social, qualidade_advogado)
#    c. Gerar processo, julgamento, sentença em cadeia
#    d. Calcular impactos retroativos em emprego, família, finanças
#    e. Simular reincidência com P(reincidência_5anos) = 0.42
# 3. Ocorrências policiais (sem processo):
#    P(boletim_ocorrencia_como_vítima) = f(bairro_residencia, classe_social)
#
# Processos cíveis (separado do criminal):
#    P(processo_trabalhista) = 0.08
#    P(processo_divorciado) = 0.15 * P(divorciado)
#    P(processo_consumidor) = 0.04
#
# Cascata de impactos:
#   Chamar engines/criminal.py para calcular e retornar
#   modificadores que serão aplicados retroativamente em:
#   - historico_emprego (marcar demissões relacionadas)
#   - conta_bancaria (marcar bloqueios)
#   - relacionamento (marcar crises)
```

### TASK-048 — Generator: Residência (requer TASK-046, TASK-041)
```python
# Arquivo: generators/gen_07_residencia.py
#
# Trajetória residencial:
# 1. Local de nascimento → primeiro endereço (com pais)
# 2. Saída da casa dos pais: idade ~ Normal(23, 4) para classe A/B
#                                   Normal(20, 3) para classe C/D/E
# 3. Sequência de mudanças com motivos correlacionados:
#    - casamento → mudança conjunta
#    - divórcio → mudança individual
#    - emprego novo em outra cidade → migração
#    - doença grave → downgrade de imóvel
#    - herança → possível upgrade
# 4. Tipo de posse: P(próprio) = f(renda, financiamento, herança)
# 5. Bairro: correlacionado com classe social (engines/geography.py)
```

### TASK-049 — Generator: Relacionamentos & Família Nuclear (requer TASK-041, TASK-043, TASK-047)
```python
# Arquivo: generators/gen_08_relacionamentos.py
#
# Usando engines/family.py:
# 1. Simular linha do tempo afetiva:
#    - Namorados: idade início ~ Normal(17, 3)
#    - P(casamento | namoro_longo) = f(tempo_namoro, classe_social)
#    - Regime de bens: f(classe_social)
# 2. Divórcio:
#    Fatores que aumentam P(divórcio):
#    + doença_mental_conjuge (+0.8)
#    + antecedente_criminal_conjuge (+1.2)
#    + diferença_classe_social (+0.3)
#    + desemprego_prolongado (+0.5)
#    Fatores que reduzem:
#    - filhos_pequenos (-0.4)
#    - religiosidade_alta (-0.5)
# 3. Filhos: número via engines/family.py
#    Datas de nascimento coerentes com estado civil e idade
# 4. Guarda/pensão após divórcio: baseado em antecedentes criminais
```

### TASK-050 — Generator: Eleitoral & Política (requer TASK-044, TASK-046)
```python
# Arquivo: generators/gen_12_eleitoral.py
#
# Modelo de comportamento eleitoral:
# P(voto_esquerda) = sigmoid(β1*classe_baixa + β2*sindicato + β3*religiao_baixa)
# P(voto_direita)  = sigmoid(β1*classe_alta + β2*militar + β3*religiao_alta)
# P(abstenção)     = f(renda_muito_baixa, processo_criminal, desengajamento)
# 
# Candidatos: P(candidatar_se) = f(cargo_publico, partido, patrimônio)
# Coerência temporal: voto consistente com perfil (com ruído ~15%)
```

### TASK-051 — Generator: Viagens (requer TASK-046, TASK-045)
```python
# Arquivo: generators/gen_13_viagens.py
# P(viagem_internacional) = f(classe_social, passaporte, renda)
# P(viagem_nacional_anual) = f(classe_social)
# Destinos: ponderados por distância e renda (gravity model)
# Correlação: viagens de negócio correlacionadas com cargo/setor
```

### TASK-052 — Generator: Vida Digital (requer TASK-042, TASK-044)
```python
# Arquivo: generators/gen_10_digital.py
# 
# Geração de contas digitais por faixa etária e classe:
# P(smartphone) = f(idade, classe_social, ano) — curva de adoção S
# Plataformas: distribuição por faixa etária (jovens→TikTok, adultos→Facebook)
# Seguidores: distribuição power-law (maioria tem poucos, poucos têm muitos)
# Histórico de navegação: categorias correlacionadas com personalidade/hobbies
# Senhas fracas: correlacionadas com baixa escolaridade
```

### TASK-053 — Generator: Domínios restantes (Pets, Consumo, Timeline, Comportamento,
#                          Religião, Esporte, Militar, Imigração, Comunicação, Mídia)
```python
# Arquivos: generators/gen_14_pets.py ... generators/gen_23_midia.py
#
# Pets:
#   P(tem_pet) = f(classe_social, tipo_residencia, filhos)
#   Raça correlacionada com classe social
#
# Consumo:
#   Padrão de compras: f(renda, número_filhos, hobbies)
#   Sazonalidade: Natal, Páscoa, Dia das Mães, etc.
#
# Comportamento & Personalidade:
#   Big Five: derivados de variáveis latentes correlacionadas
#   Hábitos correlacionados com traços de personalidade
#
# Religião:
#   P(evangélico|brasileiro) = 0.31, P(católico) = 0.45, ...
#   Correlação com comportamento eleitoral e fertilidade
#
# Militar:
#   Apenas para homens (alistamento obrigatório no Brasil)
#   P(incorporado | homem_18_anos) = 0.12
#
# Mídia e Reputação:
#   Gerar reputacao_score como função agregada de:
#   antecedentes_criminais, menções_mídia, cargo_público
```

### TASK-054 — Generator: Timeline & Eventos de Vida
```python
# Arquivo: generators/gen_16_timeline.py
# RODA POR ÚLTIMO entre os generators de domínio
# 
# Consolidar todos os eventos já inseridos e criar:
# evento_vida com tipo e data para cada evento relevante:
#   nascimento, primeiro_emprego, casamento, divorcio,
#   nascimento_filho, morte_parente, diagnostico_doença,
#   processo_criminal, compra_imovel, aposentadoria, etc.
#
# linha_do_tempo: ordenação cronológica de todos os eventos
# marco_historico_pessoal: importância 1-10 por evento
# luto_ficticio: cruzar com mortes de parentes (tabela de mortalidade)
```

---

## FASE 4 — ORQUESTRADOR PRINCIPAL

### TASK-060 — Script orquestrador de geração (scripts/generate.py)
```python
# Arquivo: scripts/generate.py
# 
# Pipeline de geração em ordem topológica CORRETA:
# 
# ETAPA 1 - Fundação:
#   1.1 Gerar N pessoas base (sem dependências)
#   1.2 Inserir seeds/lookup tables
#   1.3 Criar famílias e parentescos (engines/genetics.py disponível)
#
# ETAPA 2 - Traços derivados de genealogia:
#   2.1 Gerar características físicas (herança dos pais)
#   2.2 Gerar predisposições genéticas
#   2.3 Gerar documentos de identidade
#
# ETAPA 3 - Saúde (depende de genética e genealogia):
#   3.1 Simular doenças ao longo da vida
#   3.2 Gerar tratamentos, internações, medicamentos
#   3.3 Calcular e armazenar impactos_saude (dict temporário)
#
# ETAPA 4 - Educação (depende de saúde, genealogia):
#   4.1 Trajetória educacional com todos os modificadores
#
# ETAPA 5 - Carreira (depende de educação, saúde, genealogia):
#   5.1 Histórico de emprego com nepotismo e influências
#   5.2 Salários, benefícios, avaliações
#
# ETAPA 6 - Finanças (depende de carreira, herança):
#   6.1 Simulação financeira mensal
#   6.2 Imóveis, veículos, dívidas
#
# ETAPA 7 - Jurídico (depende de tudo acima):
#   7.1 Calcular P(crime) com todos os fatores
#   7.2 Gerar processos, sentenças, antecedentes
#   7.3 Aplicar impactos retroativos em emprego, família, finanças
#
# ETAPA 8 - Residência (depende de finanças, família, jurídico):
#   8.1 Trajetória de moradia correlacionada com vida
#
# ETAPA 9 - Relacionamentos (depende de saúde, jurídico, finanças):
#   9.1 Casamentos, divórcios, filhos com todos os modificadores
#
# ETAPA 10 - Domínios independentes (podem rodar em paralelo após etapa 9):
#   10.1 Eleitoral, Viagens, Digital, Pets, Consumo, Religião
#   10.2 Esporte, Militar, Imigração, Comunicação
#   10.3 Comportamento, Personalidade, Hobbies
#
# ETAPA 11 - Consolidação:
#   11.1 Timeline de eventos de vida
#   11.2 Reputação e mídia
#   11.3 Snapshots de patrimônio
#   11.4 Validação de consistência
#
# Configuração:
#   N_PESSOAS configurável via .env (default: 10_000)
#   Geração em lotes de 1000 com COPY para performance
#   Barra de progresso (tqdm) por etapa
#   Logging detalhado com tempo por etapa
```

### TASK-061 — Geração em lote otimizada (scripts/bulk_insert.py)
```python
# Usar psycopg2 COPY FROM STDIN para inserções massivas
# Serializar para CSV em memória (StringIO)
# Transações por etapa com rollback em caso de erro
# Connection pooling para inserções paralelas onde possível
# Estimated rows por tabela documentado
```

---

## FASE 5 — VALIDADORES DE CONSISTÊNCIA

### TASK-070 — Validador: Consistência genealógica
```python
# Arquivo: validators/val_genealogia.py
# Verificar:
# - Nenhum pai mais jovem que o filho (margem: pai >= filho + 14 anos)
# - Tipo sanguíneo do filho compatível com os pais (Punnett)
# - Cor dos olhos biologicamente possível dado os pais
# - Lateralidade com probabilidade não-zero dado os pais
# - Nenhum ciclo em arvore_genealogica
# - Herança só de pessoas marcadas como falecidas
```

### TASK-071 — Validador: Consistência temporal
```python
# Arquivo: validators/val_temporal.py
# Verificar:
# - data_fim > data_inicio em todos os contratos e relacionamentos
# - Casamento após 16 anos de idade
# - Primeiro emprego após 14 anos (menor aprendiz) ou 18 anos (CLT)
# - Ensino superior após conclusão do ensino médio
# - Diagnósticos de doença após nascimento e antes de morte (se aplicável)
# - Processos criminais com datas coerentes com idade adulta (imputabilidade 18+)
# - Viagens internacionais com passaporte válido na data
# - Filhos com mãe em idade fértil (14-50 anos) e pai (14-70 anos)
```

### TASK-072 — Validador: Consistência financeira
```python
# Arquivo: validators/val_financas.py
# Verificar:
# - Soma de transações coerente com saldo
# - Financiamento imobiliário coerente com valor do imóvel
# - Salário acima do mínimo vigente no período
# - Investimentos não excedem patrimônio total
# - Patrimônio_snapshot coerente com histórico de transações
# - Herança recebida de pessoa marcada como falecida
```

### TASK-073 — Validador: Consistência de saúde
```python
# Arquivo: validators/val_saude.py
# Verificar:
# - Tipo sanguíneo do paciente consistente em todas as tabelas
# - Medicamentos prescritos para doenças diagnosticadas
# - Cirurgias relacionadas a diagnósticos existentes
# - Vacinas em doses corretas e intervalos mínimos respeitados
# - Internações com data_entrada < data_saida
# - Alta hospitalar referência a internação existente
# - Peso e altura dentro de limites fisiológicos (nunca negativos)
```

### TASK-074 — Validador: Consistência jurídico-eleitoral
```python
# Arquivo: validators/val_juridico.py
# Verificar:
# - Votos apenas de maiores de 16 anos na data da eleição
# - Candidatos filiados ao partido representado
# - Sentenças referenciam julgamentos existentes
# - Penas referenciam sentenças existentes
# - Antecedentes criminais referenciam processos existentes
# - Pessoas em prisão não têm contratos de trabalho no período
# - Processos com advogado registrado (pelo menos um lado)
```

### TASK-075 — Validador: Consistência social e relacional
```python
# Arquivo: validators/val_social.py
# Verificar:
# - Casamento não simultaneamente com outro casamento ativo
# - Filhos com exatamente um pai e uma mãe biológicos
# - Não há auto-referência em relacionamentos (A-A)
# - Guarda compartilhada refere a filho existente
# - Pensão alimentícia refere a relação parental válida
# - Amizade é simétrica (se A é amigo de B, B é amigo de A)
```

### TASK-076 — Validador: Runner e relatório de qualidade
```python
# Arquivo: validators/run_validators.py
# Rodar todos os validadores
# Gerar relatório JSON com:
#   - Total de registros por tabela
#   - Número de violações por regra
#   - Percentual de consistência por domínio
#   - Score geral de qualidade (0-100)
# Inserir resultados em validacao_consistencia
# Exportar relatório HTML com tabelas e gráficos (pandas + matplotlib)
```

---

## FASE 6 — TESTES

### TASK-080 — Testes unitários dos motores probabilísticos
```python
# Arquivo: tests/test_engines.py
# pytest com fixtures de seed fixa
# 
# test_genetics.py:
#   - test_blood_type_inheritance: pai O+mae O → filho nunca AB
#   - test_eye_color: dois pais olhos azuis → filho sempre olhos azuis
#   - test_handedness_probability: distribuição dentro de ±3σ esperado
#   - test_height_regression: filhos de pais altos são em média mais altos
#   - test_determinism: mesma seed → mesmo output sempre
#
# test_criminal.py:
#   - test_risk_factors: score aumenta com fatores adversos
#   - test_impact_on_employment: antecedente reduz P(contratação)
#   - test_recidivism_rate: taxa dentro de 38-46% esperado
#
# test_health.py:
#   - test_disease_age_distribution: diagnósticos em faixas corretas
#   - test_hereditary_risk: predisposição aumenta P(doença)
#   - test_survival_function: S(t) decrescente e em [0,1]
```

### TASK-081 — Testes de integração (pipeline completo)
```python
# Arquivo: tests/test_integration.py
# Gerar 100 pessoas com seed fixa
# Verificar que todos os validadores passam com 0 violações críticas
# Verificar distribuições estatísticas:
#   - % canhotos: 9-11%
#   - % divorciados: 18-24%
#   - % com ensino superior: 20-25%
#   - % com antecedente criminal: 8-15%
#   - % com doença crônica: 25-35%
#   - Distribuição de tipo sanguíneo: próxima à brasileira (O:47%, A:41%, B:9%, AB:3%)
# Verificar que genealogia não tem ciclos (networkx cycle detection)
# Verificar performance: 1000 pessoas em < 60 segundos
```

### TASK-082 — Testes de queries SQL complexas
```python
# Arquivo: tests/test_queries.sql / tests/test_queries.py
# Verificar que as views funcionam corretamente
# Verificar que queries cruzadas retornam resultados não-vazios:
#   - "Canhotos que herdaram dinheiro e têm antecedente criminal"
#   - "Pessoas com doença hereditária cujo pai também tinha"
#   - "Pessoas demitidas após diagnóstico de doença grave"
#   - "Filhos que trabalham no mesmo setor que os pais"
# Verificar performance das queries (EXPLAIN ANALYZE)
```

---

## FASE 7 — DOCUMENTAÇÃO E EXPORTAÇÃO

### TASK-090 — Documentação técnica dos motores matemáticos
```markdown
# Arquivo: docs/MATH_MODELS.md
# Para cada motor, documentar:
# - Referências bibliográficas usadas
# - Fórmulas matemáticas em LaTeX
# - Parâmetros e suas fontes (IBGE, estudos científicos, etc.)
# - Limitações e simplificações assumidas
# - Como calibrar para diferentes populações
```

### TASK-091 — Documentação do schema completo
```markdown
# Arquivo: docs/SCHEMA.md (gerado automaticamente via script)
# Para cada tabela:
# - Propósito
# - Todas as colunas com tipo e constraint
# - Chaves estrangeiras
# - Regras de negócio aplicáveis
# - Exemplos de dados
# Gerar diagrama ER automaticamente (eralchemy2 ou similar)
```

### TASK-092 — Script de exportação de datasets
```python
# Arquivo: scripts/export.py
# Exportar em formatos:
#   - CSV por tabela (comprimido em .tar.gz)
#   - JSON por pessoa (documento completo com todos os domínios)
#   - Parquet para análise (via pandas)
#   - SQL dump (pg_dump)
# Registrar exportação em exportacao_dataset
# Incluir README.md com schema summary no export
```

### TASK-093 — README.md principal do projeto
```markdown
# Documentar:
# - Visão geral do projeto
# - Como rodar (docker-compose up + make generate)
# - Configurações disponíveis (.env)
# - Arquitetura dos motores probabilísticos
# - Exemplos de queries SQL interessantes
# - Como estender com novos domínios
# - Referências matemáticas e estatísticas
```

---

## FASE 8 — OTIMIZAÇÕES FINAIS

### TASK-100 — Otimização de performance de geração
```python
# Arquivo: scripts/benchmark.py
# Profile completo do pipeline de geração
# Identificar gargalos (cProfile + snakeviz)
# Implementar multiprocessing para etapas independentes (ETAPA 10)
# Otimizar queries de INSERT (COPY vs executemany vs INSERT ... SELECT)
# Adicionar índices que faltam baseado em EXPLAIN ANALYZE das queries de geração
# Meta: gerar 10.000 pessoas em < 10 minutos
```

### TASK-101 — Configuração final do PostgreSQL para produção
```sql
-- Arquivo: sql/tuning/postgresql.conf.recommended
-- shared_buffers = 256MB
-- effective_cache_size = 1GB
-- maintenance_work_mem = 64MB
-- checkpoint_completion_target = 0.9
-- wal_buffers = 16MB
-- default_statistics_target = 100
-- random_page_cost = 1.1 (SSD)
-- Configurar autovacuum para tabelas grandes
-- Configurar pg_stat_statements para monitoring
```

### TASK-102 — CI/CD e automação final
```yaml
# Arquivo: .github/workflows/ci.yml (ou similar)
# Pipeline:
#   1. Lint (ruff, black)
#   2. Type check (mypy)
#   3. Unit tests (pytest com PostgreSQL em container)
#   4. Integration test com 100 pessoas
#   5. Validação de consistência (score >= 95%)
#   6. Benchmark de performance
```

---

## ORDEM DE EXECUÇÃO RESUMIDA

```
TASK-001 → TASK-002 → TASK-003 → TASK-004 → TASK-005 → TASK-006
         → TASK-007 → TASK-008
         ↓
TASK-010 → TASK-011 → ... → TASK-023  (DDL completo)
         ↓
TASK-030 → TASK-031  (Seeds)
         ↓
TASK-040 → TASK-041 → TASK-042 → TASK-043 → TASK-044 → TASK-045
         → TASK-046 → TASK-047 → TASK-048 → TASK-049 → TASK-050
         → TASK-051 → TASK-052 → TASK-053 → TASK-054
         ↓
TASK-060 → TASK-061  (Orquestrador)
         ↓
TASK-070 → TASK-071 → TASK-072 → TASK-073 → TASK-074 → TASK-075
         → TASK-076  (Validadores)
         ↓
TASK-080 → TASK-081 → TASK-082  (Testes)
         ↓
TASK-090 → TASK-091 → TASK-092 → TASK-093  (Documentação)
         ↓
TASK-100 → TASK-101 → TASK-102  (Otimização final)
```

---

## NOTAS PARA O CLAUDE CODE

- **Nunca pular a ordem topológica**: genealogia ANTES de traços físicos,
  saúde ANTES de educação/carreira, criminal ANTES de residência final.
- **Toda aleatoriedade via SeededRNG**: nenhum `random.random()` direto.
- **Testar após cada TASK**: rodar validators antes de prosseguir.
- **Parâmetros como constantes nomeadas**: nunca magic numbers no código.
- **Tipos PostgreSQL nativos**: usar NUMERIC para dinheiro, nunca FLOAT.
- **CPF fictício**: gerar com algoritmo de dígitos verificadores VÁLIDO
  mas com prefixo especial (ex: começa com 000) para nunca conflitar com real.
- **Performance**: preferir INSERT ... SELECT e COPY sobre loops Python
  para tabelas com > 100k registros esperados.
```