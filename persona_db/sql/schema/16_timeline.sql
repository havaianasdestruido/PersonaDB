-- ============================================================================
-- PersonaDB - 16_timeline.sql (Domínio 16 - Timeline & Eventos de Vida)
-- ----------------------------------------------------------------------------
-- Hub: evento_vida (vinculado diretamente a pessoa).
-- Satélites: marco_historico_pessoal, linha_do_tempo, aniversario,
-- comemoracao, luto_ficticio.
-- ============================================================================

CREATE TABLE IF NOT EXISTS evento_vida (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data        DATE,
    tipo_evento TEXT,
    descricao   TEXT
);
COMMENT ON TABLE evento_vida IS 'Eventos marcantes da vida da persona.';

CREATE TABLE IF NOT EXISTS marco_historico_pessoal (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id       UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    evento_vida_id  UUID NOT NULL REFERENCES evento_vida(id) ON DELETE CASCADE,
    importancia     INTEGER CHECK (importancia BETWEEN 1 AND 10)
);
COMMENT ON TABLE marco_historico_pessoal IS 'Marcos classificados por importância.';

CREATE TABLE IF NOT EXISTS linha_do_tempo (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id       UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    evento_vida_id  UUID NOT NULL REFERENCES evento_vida(id) ON DELETE CASCADE,
    ordem_cronologica INTEGER
);
COMMENT ON TABLE linha_do_tempo IS 'Ordem cronológica dos eventos de vida.';

CREATE TABLE IF NOT EXISTS aniversario (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo       TEXT CHECK (tipo IN ('nascimento','casamento','emprego','formatura')),
    data       DATE
);
COMMENT ON TABLE aniversario IS 'Datas comemorativas da persona.';

CREATE TABLE IF NOT EXISTS comemoracao (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    evento_vida_id    UUID NOT NULL REFERENCES evento_vida(id) ON DELETE CASCADE,
    local_endereco_id UUID,
    convidados_ficticios INTEGER DEFAULT 0
);
COMMENT ON TABLE comemoracao IS 'Festas ou homenagens por um evento.';

CREATE TABLE IF NOT EXISTS luto_ficticio (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id          UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_falecido UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data               DATE,
    relacao            TEXT
);
COMMENT ON TABLE luto_ficticio IS 'Períodos de luto por falecimento de ente querido.';