-- ============================================================================
-- PersonaDB - 12_eleitoral.sql (Domínio 12 - Eleitoral & Política)
-- ----------------------------------------------------------------------------
-- Hubs: eleicao, partido.
-- Satélites: candidato, voto, filiacao_partidaria, cargo_publico,
-- doacao_campanha_ficticia, comparecimento_eleitoral.
-- ============================================================================

CREATE TABLE IF NOT EXISTS eleicao (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ano               INTEGER NOT NULL,
    tipo              TEXT CHECK (tipo IN ('municipal','estadual','federal')),
    municipio_ficticio TEXT
);
COMMENT ON TABLE eleicao IS 'Plebiscitos/eleições fictícias.';

CREATE TABLE IF NOT EXISTS partido (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_ficticio  TEXT NOT NULL,
    sigla_ficticia TEXT NOT NULL,
    CONSTRAINT uq_partido_sigla UNIQUE (sigla_ficticia)
);
COMMENT ON TABLE partido IS 'Partidos políticos 100% fictícios.';

CREATE TABLE IF NOT EXISTS candidato (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    eleicao_id       UUID NOT NULL REFERENCES eleicao(id) ON DELETE CASCADE,
    partido_id       UUID NOT NULL REFERENCES partido(id) ON DELETE CASCADE,
    cargo_pretendido TEXT
);
COMMENT ON TABLE candidato IS 'Candidaturas nas eleições.';

CREATE TABLE IF NOT EXISTS voto (
    id                        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id                 UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    eleicao_id                UUID NOT NULL REFERENCES eleicao(id) ON DELETE CASCADE,
    candidato_id_escolhido    UUID,
    tipo                      TEXT CHECK (tipo IN ('candidato','branco','nulo'))
);
COMMENT ON TABLE voto IS 'Votos computados (fictícios).';

CREATE TABLE IF NOT EXISTS filiacao_partidaria (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    partido_id       UUID NOT NULL REFERENCES partido(id) ON DELETE CASCADE,
    data_filiacao    DATE,
    data_desfiliacao DATE
);
COMMENT ON TABLE filiacao_partidaria IS 'Filiações partidárias.';

CREATE TABLE IF NOT EXISTS cargo_publico (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id     UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome_cargo    TEXT NOT NULL,
    orgao         TEXT,
    data_inicio   DATE,
    data_fim      DATE
);
COMMENT ON TABLE cargo_publico IS 'Cargos públicos ocupados pela persona.';

CREATE TABLE IF NOT EXISTS doacao_campanha_ficticia (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_doador UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    candidato_id     UUID NOT NULL REFERENCES candidato(id) ON DELETE CASCADE,
    valor            NUMERIC(12,2),
    data             DATE
);
COMMENT ON TABLE doacao_campanha_ficticia IS 'Doações eleitorais fictícias.';

CREATE TABLE IF NOT EXISTS comparecimento_eleitoral (
    id                     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id              UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    eleicao_id             UUID NOT NULL REFERENCES eleicao(id) ON DELETE CASCADE,
    compareceu             BOOLEAN DEFAULT TRUE,
    justificativa_ausencia TEXT
);
COMMENT ON TABLE comparecimento_eleitoral IS 'Comparecimento nas eleições.';