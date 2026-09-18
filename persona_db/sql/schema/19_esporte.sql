-- ============================================================================
-- PersonaDB - 19_esporte.sql (Domínio 19 - Esporte & Lazer)
-- ----------------------------------------------------------------------------
-- Hubs: clube_esportivo, competicao.
-- Satélites: esporte_praticado, membro_clube_esportivo,
-- resultado_competicao, equipamento_esportivo, hobby, colecao_ficticia.
-- ============================================================================

CREATE TABLE IF NOT EXISTS clube_esportivo (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome       TEXT NOT NULL,
    modalidade TEXT
);
COMMENT ON TABLE clube_esportivo IS 'Clubes esportivos.';

CREATE TABLE IF NOT EXISTS competicao (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome       TEXT NOT NULL,
    modalidade TEXT,
    data       DATE
);
COMMENT ON TABLE competicao IS 'Competições esportivas fictícias.';

CREATE TABLE IF NOT EXISTS esporte_praticado (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome_esporte TEXT NOT NULL,
    nivel        TEXT,
    frequencia   TEXT
);
COMMENT ON TABLE esporte_praticado IS 'Esportes que a persona pratica.';

CREATE TABLE IF NOT EXISTS membro_clube_esportivo (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    clube_id     UUID NOT NULL REFERENCES clube_esportivo(id) ON DELETE CASCADE,
    data_entrada DATE
);
COMMENT ON TABLE membro_clube_esportivo IS 'Associação a clubes esportivos.';

CREATE TABLE IF NOT EXISTS resultado_competicao (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    competicao_id  UUID NOT NULL REFERENCES competicao(id) ON DELETE CASCADE,
    colocacao      INTEGER
);
COMMENT ON TABLE resultado_competicao IS 'Resultados da persona em competições.';

CREATE TABLE IF NOT EXISTS equipamento_esportivo (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id       UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo            TEXT,
    marca_ficticia  TEXT,
    data_aquisicao  DATE
);
COMMENT ON TABLE equipamento_esportivo IS 'Equipamentos de esporte da persona.';

CREATE TABLE IF NOT EXISTS hobby (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome       TEXT NOT NULL,
    frequencia TEXT
);
COMMENT ON TABLE hobby IS 'Passatempos da persona.';

CREATE TABLE IF NOT EXISTS colecao_ficticia (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tema              TEXT,
    quantidade_itens  INTEGER
);
COMMENT ON TABLE colecao_ficticia IS 'Coleções particulares da persona.';