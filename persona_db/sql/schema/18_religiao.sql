-- ============================================================================
-- PersonaDB - 18_religiao.sql (Domínio 18 - Religião & Crenças)
-- ----------------------------------------------------------------------------
-- Hubs: crenca, instituicao_religiosa.
-- Satélites: participacao_religiosa, ritual_ficticio, conversao_religiosa,
-- dizimo_ficticio.
-- ============================================================================

CREATE TABLE IF NOT EXISTS crenca (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_ficticio TEXT NOT NULL,
    intensidade   NUMERIC(5,2) CHECK (intensidade BETWEEN 0 AND 10)
);
COMMENT ON TABLE crenca IS 'Crenças religiosas/espirituais fictícias (hub).';

CREATE TABLE IF NOT EXISTS instituicao_religiosa (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome        TEXT NOT NULL,
    endereco_id UUID
);
COMMENT ON TABLE instituicao_religiosa IS 'Templos/igrejas fictícios.';

CREATE TABLE IF NOT EXISTS participacao_religiosa (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    instituicao_id    UUID NOT NULL REFERENCES instituicao_religiosa(id) ON DELETE CASCADE,
    frequencia        TEXT,
    papel             TEXT
);
COMMENT ON TABLE participacao_religiosa IS 'Frequência religiosa da persona.';

CREATE TABLE IF NOT EXISTS ritual_ficticio (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome      TEXT,
    data      DATE
);
COMMENT ON TABLE ritual_ficticio IS 'Rituais praticados (batismo, cerimônias).';

CREATE TABLE IF NOT EXISTS conversao_religiosa (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    crenca_anterior_id UUID NOT NULL REFERENCES crenca(id) ON DELETE CASCADE,
    crenca_nova_id    UUID NOT NULL REFERENCES crenca(id) ON DELETE CASCADE,
    data              DATE
);
COMMENT ON TABLE conversao_religiosa IS 'Mudanças de crença ao longo da vida.';

CREATE TABLE IF NOT EXISTS dizimo_ficticio (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    instituicao_id    UUID NOT NULL REFERENCES instituicao_religiosa(id) ON DELETE CASCADE,
    valor             NUMERIC(12,2),
    periodicidade     TEXT
);
COMMENT ON TABLE dizimo_ficticio IS 'Contribuições financeiras regulares.';