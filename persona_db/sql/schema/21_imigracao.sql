-- ============================================================================
-- PersonaDB - 21_imigracao.sql (Domínio 21 - Imigração & Documentos fictícios)
-- ----------------------------------------------------------------------------
-- Satélites de pessoa: documento_identidade, visto_ficticio,
-- naturalizacao_ficticia, residencia_permanente_ficticia,
-- deportacao_ficticia, fronteira_travessia_ficticia.
-- ============================================================================

CREATE TABLE IF NOT EXISTS documento_identidade (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id            UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo                 TEXT,
    pais_emissor_ficticio TEXT,
    validade             DATE
);
COMMENT ON TABLE documento_identidade IS 'Documentos emitidos por outros países (fictícios).';

CREATE TABLE IF NOT EXISTS visto_ficticio (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id             UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pais_destino_ficticio TEXT,
    tipo                  TEXT,
    validade              DATE
);
COMMENT ON TABLE visto_ficticio IS 'Vistos concedidos à persona.';

CREATE TABLE IF NOT EXISTS naturalizacao_ficticia (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id     UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pais_origem   TEXT,
    pais_destino  TEXT,
    data          DATE
);
COMMENT ON TABLE naturalizacao_ficticia IS 'Processos de naturalização.';

CREATE TABLE IF NOT EXISTS residencia_permanente_ficticia (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pais           TEXT,
    data_concessao DATE
);
COMMENT ON TABLE residencia_permanente_ficticia IS 'Residências permanentes no exterior.';

CREATE TABLE IF NOT EXISTS deportacao_ficticia (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pais      TEXT,
    data      DATE,
    motivo    TEXT
);
COMMENT ON TABLE deportacao_ficticia IS 'Deportações da persona.';

CREATE TABLE IF NOT EXISTS fronteira_travessia_ficticia (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id       UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    ponto_fronteira TEXT,
    data            DATE,
    direcao         TEXT
);
COMMENT ON TABLE fronteira_travessia_ficticia IS 'Passagens de fronteira registradas.';