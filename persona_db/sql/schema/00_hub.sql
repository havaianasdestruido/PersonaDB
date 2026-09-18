-- ============================================================================
-- PersonaDB - 00_hub.sql (Domínio 00 - Hub central)
-- ----------------------------------------------------------------------------
-- Cria o núcleo do schema de personas fictícias:
--   * extensões (uuid-ossp, pgcrypto, pg_trgm)
--   * enums base (sexo, estado_civil, nacionalidade)
--   * tabela central "pessoa"
--   * função de auditoria set_update_timestamp() + trigger
--
-- Idempotente (PostgreSQL 16): seguro para execução repetida.
-- Convenções: PK UUID (uuid_generate_v4); FK sempre ON DELETE CASCADE,
-- salvo indicação "sob medida"; dinheiro como NUMERIC; datas DATE/TIMESTAMPTZ.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Extensões (guardadas por IF NOT EXISTS)
-- ----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ----------------------------------------------------------------------------
-- 2. Enums base — criados via DO $$ para não estourar erro em re-execução
-- ----------------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sexo') THEN
        CREATE TYPE sexo AS ENUM ('masculino', 'feminino');
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_civil') THEN
        CREATE TYPE estado_civil AS ENUM (
            'solteiro', 'casado', 'divorciado', 'viuvo', 'uniao_estavel'
        );
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'nacionalidade') THEN
        CREATE TYPE nacionalidade AS ENUM (
            'brasileira', 'naturalizado', 'estrangeiro'
        );
    END IF;
END
$$;

-- ----------------------------------------------------------------------------
-- 3. Tabela central: pessoa
-- Núcleo de todo o banco; todas as demais tabelas penduram em pessoa.id.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pessoa (
    id                UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_completo     TEXT          NOT NULL,
    nome_social       TEXT,
    data_nascimento   DATE          NOT NULL
        CONSTRAINT chk_pessoa_nascimento_pregresso CHECK (data_nascimento < CURRENT_DATE),
    sexo              sexo          NOT NULL,
    nacionalidade     nacionalidade NOT NULL DEFAULT 'brasileira',
    cidade_nascimento TEXT,
    uf_nascimento     CHAR(2)
        CONSTRAINT chk_pessoa_uf CHECK (
            uf_nascimento IS NULL OR uf_nascimento ~ '^[A-Z]{2}$'
        ),
    classe_social     TEXT          DEFAULT 'C1',
    estado_civil      estado_civil   DEFAULT 'solteiro',
    esta_vivo         BOOLEAN       DEFAULT TRUE,
    data_obito        DATE,
    criado_em         TIMESTAMPTZ   DEFAULT now(),
    atualizado_em     TIMESTAMPTZ   DEFAULT now(),
    -- DATA de óbito coerente com a data de nascimento
    CONSTRAINT chk_pessoa_obito CHECK (
        data_obito IS NULL OR data_obito >= data_nascimento
    ),
    -- Se não estiver vivo, precisa ter data de óbito
    CONSTRAINT chk_pessoa_vivo_obito CHECK (
        esta_vivo = TRUE OR data_obito IS NOT NULL
    )
);

COMMENT ON TABLE pessoa IS
    'Hub central: registro base de cada persona fictícia. Todas as tabelas satélites referenciam pessoa.id.';

-- ----------------------------------------------------------------------------
-- 4. Índices úteis (BTREE + 1 GIN trigram para busca por nome)
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_pessoa_data_nascimento ON pessoa (data_nascimento);
CREATE INDEX IF NOT EXISTS idx_pessoa_sexo            ON pessoa (sexo);
CREATE INDEX IF NOT EXISTS idx_pessoa_classe          ON pessoa (classe_social);
-- Busca aproximada por nome_completo (aproveita pg_trgm)
CREATE INDEX IF NOT EXISTS idx_pessoa_nome_trgm       ON pessoa
    USING GIN (nome_completo gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_pessoa_nome_social     ON pessoa (nome_social);

-- ----------------------------------------------------------------------------
-- 5. Função de atualização automática de timestamp (padrão marca_atualizado)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_update_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.atualizado_em := now();
    RETURN NEW;
END
$$;

COMMENT ON FUNCTION set_update_timestamp() IS
    'Trigger function que atualiza atualizado_em a cada UPDATE. Padrão reutilizado por todas as tabelas que possuem coluna atualizado_em.';

DROP TRIGGER IF EXISTS trg_pessoa_atualizado_em ON pessoa;

CREATE TRIGGER trg_pessoa_atualizado_em
    BEFORE UPDATE ON pessoa
    FOR EACH ROW
    EXECUTE FUNCTION set_update_timestamp();