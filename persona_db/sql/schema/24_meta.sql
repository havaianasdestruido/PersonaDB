-- ============================================================================
-- PersonaDB - 24_meta.sql (Domínio 24 - Meta & Sistema)
-- ----------------------------------------------------------------------------
-- Tabelas de controle do próprio banco (rastreabilidade da geração).
-- ============================================================================

CREATE TABLE IF NOT EXISTS fonte_dado (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tabela_origem TEXT NOT NULL,
    metodo_geracao TEXT,
    data_geracao  TIMESTAMPTZ DEFAULT now()
);
COMMENT ON TABLE fonte_dado IS 'Origem de cada bloco de dados gerado.';

CREATE TABLE IF NOT EXISTS versao_registro (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tabela        TEXT NOT NULL,
    registro_id   UUID,
    numero_versao INTEGER,
    data          TIMESTAMPTZ DEFAULT now()
);
COMMENT ON TABLE versao_registro IS 'Versionamento de registros gerados.';

CREATE TABLE IF NOT EXISTS log_alteracao (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tabela         TEXT,
    registro_id    UUID,
    campo_alterado TEXT,
    valor_antigo   TEXT,
    valor_novo     TEXT,
    data           TIMESTAMPTZ DEFAULT now()
);
COMMENT ON TABLE log_alteracao IS 'Histórico de alterações nos registros.';

CREATE TABLE IF NOT EXISTS auditoria (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_sistema TEXT NOT NULL,
    acao           TEXT,
    tabela_afetada TEXT,
    data           TIMESTAMPTZ DEFAULT now()
);
COMMENT ON TABLE auditoria IS 'Trilha de auditoria da geração.';

CREATE TABLE IF NOT EXISTS regra_geracao (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dominio       TEXT NOT NULL,
    parametro     TEXT,
    valor_padrao  TEXT
);
COMMENT ON TABLE regra_geracao IS 'Parâmetros de calibração usados na geração.';

CREATE TABLE IF NOT EXISTS semente_aleatoria (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id   UUID REFERENCES pessoa(id) ON DELETE CASCADE,
    seed_valor  TEXT NOT NULL
);
COMMENT ON TABLE semente_aleatoria IS 'Seed determinística usada para cada persona.';

CREATE TABLE IF NOT EXISTS validacao_consistencia (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tabela         TEXT,
    regra_violada  TEXT,
    registro_id    UUID,
    data           TIMESTAMPTZ DEFAULT now()
);
COMMENT ON TABLE validacao_consistencia IS 'Registros de validações que falharam.';

CREATE TABLE IF NOT EXISTS exportacao_dataset (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data             TIMESTAMPTZ DEFAULT now(),
    formato          TEXT,
    tabelas_incluidas TEXT,
    destino          TEXT
);
COMMENT ON TABLE exportacao_dataset IS 'Histórico de exportações geradas.';