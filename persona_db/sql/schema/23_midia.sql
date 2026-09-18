-- ============================================================================
-- PersonaDB - 23_midia.sql (Domínio 23 - Mídia & Reputação)
-- ----------------------------------------------------------------------------
-- Hubs: noticia_ficticia.
-- Satélites: mencao_midia, reputacao_score, premio_ficticio,
-- entrevista_ficticia.
-- ============================================================================

CREATE TABLE IF NOT EXISTS noticia_ficticia (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id          UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    titulo             TEXT,
    veiculo_ficticio   TEXT NOT NULL,
    data               DATE
);
COMMENT ON TABLE noticia_ficticia IS 'Notícias fictícias sobre a persona.';

CREATE TABLE IF NOT EXISTS mencao_midia (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    noticia_id UUID NOT NULL REFERENCES noticia_ficticia(id) ON DELETE CASCADE,
    contexto   TEXT CHECK (contexto IN ('positivo','negativo','neutro'))
);
COMMENT ON TABLE mencao_midia IS 'Menções da persona na mídia.';

CREATE TABLE IF NOT EXISTS reputacao_score (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data        DATE,
    valor_score NUMERIC(5,2) CHECK (valor_score BETWEEN 0 AND 100)
);
COMMENT ON TABLE reputacao_score IS 'Índice de reputação fictício ao longo do tempo.';

CREATE TABLE IF NOT EXISTS premio_ficticio (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome       TEXT,
    categoria  TEXT,
    data       DATE
);
COMMENT ON TABLE premio_ficticio IS 'Prêmios/honras recebidos.';

CREATE TABLE IF NOT EXISTS entrevista_ficticia (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    veiculo_ficticio TEXT NOT NULL,
    data             DATE,
    tema             TEXT
);
COMMENT ON TABLE entrevista_ficticia IS 'Entrevistas concedidas à mídia.';