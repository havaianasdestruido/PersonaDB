-- ============================================================================
-- PersonaDB - 17_comportamento.sql (Domínio 17 - Comportamento & Personalidade)
-- ----------------------------------------------------------------------------
-- Satélites de pessoa: traco_personalidade, habito, rotina_diaria,
-- preferencia, aversao, habilidade, talento, medo_ficticio, sonho_ficticio,
-- estilo_aprendizagem.
-- ============================================================================

CREATE TABLE IF NOT EXISTS traco_personalidade (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome_traco  TEXT NOT NULL,
    intensidade NUMERIC(5,2) CHECK (intensidade BETWEEN 0 AND 10)
);
COMMENT ON TABLE traco_personalidade IS 'Traços de personalidade (ex.: Big Five fictício).';

CREATE TABLE IF NOT EXISTS habito (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    descricao  TEXT,
    frequencia TEXT
);
COMMENT ON TABLE habito IS 'Hábitos cotidianos da persona.';

CREATE TABLE IF NOT EXISTS rotina_diaria (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    horario   TIME,
    atividade TEXT
);
COMMENT ON TABLE rotina_diaria IS 'Rotina diária típica da persona.';

CREATE TABLE IF NOT EXISTS preferencia (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id     UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    categoria     TEXT,
    item_preferido TEXT
);
COMMENT ON TABLE preferencia IS 'Preferências pessoais (comida, música, etc).';

CREATE TABLE IF NOT EXISTS aversao (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    categoria   TEXT,
    item_evitado TEXT
);
COMMENT ON TABLE aversao IS 'Aversões pessoais.';

CREATE TABLE IF NOT EXISTS habilidade (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome      TEXT NOT NULL,
    nivel     TEXT CHECK (nivel IN ('basico','intermediario','avancado','especialista'))
);
COMMENT ON TABLE habilidade IS 'Habilidades gerais da persona.';

CREATE TABLE IF NOT EXISTS talento (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id     UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    area          TEXT,
    nivel_ficticio NUMERIC(5,2) CHECK (nivel_ficticio BETWEEN 0 AND 10)
);
COMMENT ON TABLE talento IS 'Talentos naturais (nota fictícia 0-10).';

CREATE TABLE IF NOT EXISTS medo_ficticio (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    descricao  TEXT,
    origem     TEXT
);
COMMENT ON TABLE medo_ficticio IS 'Fobias/medos fictícios.';

CREATE TABLE IF NOT EXISTS sonho_ficticio (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    descricao  TEXT,
    status     TEXT CHECK (status IN ('realizado','em_curso','abandonado'))
);
COMMENT ON TABLE sonho_ficticio IS 'Aspirações e sonhos da persona.';

CREATE TABLE IF NOT EXISTS estilo_aprendizagem (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo      TEXT CHECK (tipo IN ('visual','auditivo','cinestesico'))
);
COMMENT ON TABLE estilo_aprendizagem IS 'Estilo dominante de aprendizagem.';