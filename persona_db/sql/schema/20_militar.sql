-- ============================================================================
-- PersonaDB - 20_militar.sql (Domínio 20 - Militar & Serviço)
-- ----------------------------------------------------------------------------
-- Hub: unidade_militar.
-- Satélites: servico_militar, patente, convocacao, baixa_militar,
-- condecoracao_ficticia.
-- ============================================================================

CREATE TABLE IF NOT EXISTS unidade_militar (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome                TEXT NOT NULL,
    localizacao_ficticia TEXT
);
COMMENT ON TABLE unidade_militar IS 'Unidades militares fictícias.';

CREATE TABLE IF NOT EXISTS servico_militar (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id       UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data_inicio     DATE,
    data_fim        DATE,
    ramo            TEXT
);
COMMENT ON TABLE servico_militar IS 'Período de serviço militar/alistamento.';

CREATE TABLE IF NOT EXISTS patente (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    servico_militar_id UUID NOT NULL REFERENCES servico_militar(id) ON DELETE CASCADE,
    nome_patente       TEXT,
    data_promocao      DATE
);
COMMENT ON TABLE patente IS 'Patentes alcançadas durante o serviço.';

CREATE TABLE IF NOT EXISTS convocacao (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data       DATE,
    motivo     TEXT,
    resultado  TEXT CHECK (resultado IN ('dispensado','incorporado','adiado'))
);
COMMENT ON TABLE convocacao IS 'Convocações militares fictícias.';

CREATE TABLE IF NOT EXISTS baixa_militar (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    servico_militar_id UUID NOT NULL REFERENCES servico_militar(id) ON DELETE CASCADE,
    data               DATE,
    motivo             TEXT
);
COMMENT ON TABLE baixa_militar IS 'Baixa do serviço militar.';

CREATE TABLE IF NOT EXISTS condecoracao_ficticia (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome      TEXT,
    data      DATE
);
COMMENT ON TABLE condecoracao_ficticia IS 'Condecorações e honrarias recebidas.';