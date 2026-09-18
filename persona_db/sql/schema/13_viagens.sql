-- ============================================================================
-- PersonaDB - 13_viagens.sql (Domínio 13 - Viagens)
-- ----------------------------------------------------------------------------
-- Hubs: viagem, destino.
-- Satélites: hospedagem, transporte_viagem, passagem, documento_viagem,
-- bagagem, seguro_viagem, roteiro_viagem, companhia_viagem.
-- ============================================================================

CREATE TABLE IF NOT EXISTS destino (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cidade_ficticia TEXT NOT NULL,
    pais_ficticio  TEXT
);
COMMENT ON TABLE destino IS 'Destinos de viagem 100% fictícios.';

CREATE TABLE IF NOT EXISTS viagem (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    destino_id   UUID NOT NULL REFERENCES destino(id) ON DELETE CASCADE,
    data_ida     DATE,
    data_volta   DATE,
    motivo       TEXT
);
COMMENT ON TABLE viagem IS 'Viagens realizadas pela persona.';

CREATE TABLE IF NOT EXISTS hospedagem (
    id                     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    viagem_id              UUID NOT NULL REFERENCES viagem(id) ON DELETE CASCADE,
    tipo                   TEXT CHECK (tipo IN ('hotel','hostel','airbnb','pousada','familia')),
    nome_estabelecimento   TEXT,
    custo                  NUMERIC(12,2)
);
COMMENT ON TABLE hospedagem IS 'Acomodações da viagem.';

CREATE TABLE IF NOT EXISTS transporte_viagem (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    viagem_id  UUID NOT NULL REFERENCES viagem(id) ON DELETE CASCADE,
    tipo       TEXT CHECK (tipo IN ('aereo','rodoviario','maritimo','ferroviario')),
    companhia  TEXT
);
COMMENT ON TABLE transporte_viagem IS 'Deslocamentos da viagem.';

CREATE TABLE IF NOT EXISTS passagem (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transporte_id  UUID NOT NULL REFERENCES transporte_viagem(id) ON DELETE CASCADE,
    numero_ficticio TEXT NOT NULL,
    classe         TEXT,
    valor          NUMERIC(12,2)
);
COMMENT ON TABLE passagem IS 'Passagens fictícias.';

CREATE TABLE IF NOT EXISTS documento_viagem (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo         TEXT CHECK (tipo IN ('visto','passaporte')),
    validade     DATE
);
COMMENT ON TABLE documento_viagem IS 'Documentos necessários para viagens.';

CREATE TABLE IF NOT EXISTS bagagem (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    viagem_id   UUID NOT NULL REFERENCES viagem(id) ON DELETE CASCADE,
    tipo        TEXT,
    peso        NUMERIC(6,2),
    extraviada  BOOLEAN DEFAULT FALSE
);
COMMENT ON TABLE bagagem IS 'Bolsas/malas da viagem.';

CREATE TABLE IF NOT EXISTS seguro_viagem (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    viagem_id   UUID NOT NULL REFERENCES viagem(id) ON DELETE CASCADE,
    seguradora  TEXT,
    cobertura   TEXT
);
COMMENT ON TABLE seguro_viagem IS 'Seguros contratados para a viagem.';

CREATE TABLE IF NOT EXISTS roteiro_viagem (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    viagem_id           UUID NOT NULL REFERENCES viagem(id) ON DELETE CASCADE,
    dia                 INTEGER,
    atividade_planejada TEXT
);
COMMENT ON TABLE roteiro_viagem IS 'Roteiro dia a dia da viagem.';

CREATE TABLE IF NOT EXISTS companhia_viagem (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    viagem_id         UUID NOT NULL REFERENCES viagem(id) ON DELETE CASCADE,
    pessoa_id_acompanhante UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE
);
COMMENT ON TABLE companhia_viagem IS 'Acompanhantes na viagem.';