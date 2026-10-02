# PersonaDB

O **PersonaDB** é um motor determinístico de geração de dados sintéticos e relacionais para **personas fictícias brasileiras**, cobrindo **25 domínios** da vida humana (**257 tabelas** no PostgreSQL 16). Todos os registros são 100% fictícios e reproduzíveis a partir de uma única semente mestre (`SeededRNG` / PCG64 com derivação criptográfica `BLAKE2b`).

📚 **Documentação completa:** <https://havaianasdestruido.github.io/PersonaDB/docs/> — guias de instalação, arquitetura, motores matemáticos, catálogo dos geradores, referência de API de todos os módulos Python e dicionário das 257 tabelas. O site vive em [`website/`](website/) (Docusaurus) e é publicado automaticamente pelo workflow [`docs.yml`](.github/workflows/docs.yml).

---

## Visão Geral

- **257 tabelas relacionais** distribuídas em 25 domínios funcionais + metadados e junções N:N (`00_hub.sql` a `26_metadata.sql`).
- **7 motores matemáticos e probabilísticos (`persona_db/engines/`)**:
  - `rng.py`: `SeededRNG` (PCG64) com `fork(persona_id, domain)` determinístico e isolado.
  - `socio.py`: mobilidade social intergeracional (cadeia de Markov 6×6), escolaridade logit ordinal, salários log-normais de Mincer e influência familiar (nepotismo).
  - `genetics.py`: quadrados de Punnett (ABO e fator Rh), herança poligênica de cor dos olhos/cabelos, estatura parental regressionada à média e lateralidade.
  - `health.py`: mortalidade de Gompertz-Makeham, incidência etária de doenças crônicas, comorbidades, cirurgias, internações e impacto ocupacional.
  - `family.py`: nupcialidade, homogamia socioeconômica, fecundidade de Poisson por classe e risco logístico de divórcio.
  - `geography.py`: distribuição demográfica em 60 municípios fictícios, segregação residencial por bairro e migração interna.
  - `criminal.py`: risco logístico de envolvimento criminal, reincidência, dosimetria de pena e restrições trabalhistas.
- **24 geradores de domínio (`persona_db/generators/gen_00_pessoa.py` .. `gen_23_midia.py`)** orquestrados em ordem topológica estrita.
- **6 validadores de consistência (`persona_db/validators/val_*.py`)**: genealogia, temporal, finanças, saúde, jurídico-eleitoral e social.

---

## Quick Start

```bash
# 1. Instalar pacote e dependências de desenvolvimento/Parquet
python3 -m pip install -e "persona_db[dev,parquet]"

# 2. Gerar um dataset sintético completo (257 tabelas) com validação automática
python3 -m persona_db.scripts.generate --personas 200 --seed 42 --output dataset.json --html-report report.html

# 3. Executar a suíte de validadores de consistência diretamente
python3 -m persona_db.validators.run_validators --personas 200 --seed 42

# 4. Rodar todos os testes (unitários, integração e estatísticos)
pytest persona_db/tests -v

# 5. Gerar a documentação completa do schema (docs/SCHEMA.md)
python3 -m persona_db.scripts.document_schema
```

### Fluxo com PostgreSQL (Docker Compose + Makefile)

```bash
cp persona_db/.env.example .env
docker compose -f persona_db/docker-compose.yml up -d
make -C persona_db migrate
make -C persona_db generate N_PESSOAS=1000 SEED=42
make -C persona_db load
make -C persona_db validate
make -C persona_db export-csv
make -C persona_db export-parquet
```

---

## Arquitetura do Projeto

```text
persona_db/
├── sql/schema/          # 28 arquivos DDL PostgreSQL (00_hub.sql .. 99_functions.sql)
├── seeds/               # Catálogos determinísticos (lookup_data.py, probability_tables.py)
├── engines/             # Motores matemáticos (rng, socio, genetics, health, family, geography, criminal)
├── generators/          # Geradores por domínio (gen_00_pessoa.py .. gen_23_midia.py)
├── validators/          # Validadores de consistência (val_genealogia, val_temporal, val_financas, val_saude, val_juridico, val_social)
├── scripts/             # CLIs: generate.py, bulk_insert.py, export.py, benchmark.py, document_schema.py
├── docs/                # Documentação técnica: SCHEMA.md e MATH_MODELS.md
└── tests/               # Testes unitários, de integração (25 domínios) e estatísticos (N=1000)
```

---

## Exemplos de Consultas SQL Úteis

### 1. Perfil consolidado de uma persona (Hub + Finanças + Carreira)

```sql
SELECT
    p.id,
    p.nome_completo,
    p.data_nascimento,
    p.classe_social,
    p.estado_civil,
    ps.valor_total_estimado AS patrimonio_liquido,
    rs.valor_score          AS score_reputacao
FROM pessoa p
LEFT JOIN patrimonio_snapshot ps ON ps.pessoa_id = p.id
LEFT JOIN reputacao_score rs     ON rs.pessoa_id = p.id
ORDER BY ps.valor_total_estimado DESC NULLS LAST
LIMIT 20;
```

### 2. Árvore genealógica recursiva (ascendentes por geração)

```sql
WITH RECURSIVE linhagem AS (
    SELECT
        p.id AS pessoa_id,
        p.nome_completo,
        ag.pessoa_id_pai,
        ag.pessoa_id_mae,
        0 AS nivel
    FROM pessoa p
    LEFT JOIN arvore_genealogica ag ON ag.pessoa_id = p.id
    WHERE p.id = :pessoa_alvo_id

    UNION ALL

    SELECT
        parente.id,
        parente.nome_completo,
        ag_par.pessoa_id_pai,
        ag_par.pessoa_id_mae,
        l.nivel + 1
    FROM linhagem l
    JOIN pessoa parente ON parente.id IN (l.pessoa_id_pai, l.pessoa_id_mae)
    LEFT JOIN arvore_genealogica ag_par ON ag_par.pessoa_id = parente.id
    WHERE l.nivel < 5
)
SELECT * FROM linhagem ORDER BY nivel;
```

### 3. Linha do tempo cronológica de eventos de vida

```sql
SELECT
    ldt.ordem_cronologica,
    ev.data,
    ev.tipo_evento,
    ev.descricao,
    mhp.importancia
FROM linha_do_tempo ldt
JOIN evento_vida ev ON ev.id = ldt.evento_vida_id
LEFT JOIN marco_historico_pessoal mhp ON mhp.evento_vida_id = ev.id
WHERE ldt.pessoa_id = :pessoa_alvo_id
ORDER BY ldt.ordem_cronologica;
```

---

## Como Estender com Novos Domínios

1. Adicione o arquivo DDL numerado em `persona_db/sql/schema/` com `CREATE TABLE IF NOT EXISTS` e `COMMENT ON TABLE`.
2. Crie o módulo gerador em `persona_db/generators/gen_XX_nome.py` expondo `generate(personas, seed=..., today=...) -> dict[str, list[dict]]`, utilizando exclusivamente `master.fork(persona["id"], "dominio")` para aleatoriedade.
3. Registre o gerador na tupla `DOMAIN_PIPELINE` em `persona_db/scripts/generate.py` após suas dependências.
4. Adicione as regras invariantes correspondentes em `persona_db/validators/` e testes em `persona_db/tests/`.

Consulte [PERSONA.MD](PERSONA.MD) para a especificação conceitual das entidades, [persona_db/docs/SCHEMA.md](persona_db/docs/SCHEMA.md) para o dicionário completo das 257 tabelas e [persona_db/docs/MATH_MODELS.md](persona_db/docs/MATH_MODELS.md) para as equações e distribuições calibradas.
