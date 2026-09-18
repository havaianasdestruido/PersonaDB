-- ============================================================================
-- PersonaDB - 02_genealogia.sql (Domínio 02 - Genealogia & Herança)
-- ----------------------------------------------------------------------------
-- Hub: familia. Relações: membro_familia, parentesco, arvore_genealogica,
-- heranca/heranca_item, doacao_familiar, condicao_genetica/
-- predisposicao_genetica, ancestralidade_ficticia.
-- ============================================================================

CREATE TABLE IF NOT EXISTS familia (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sobrenome_familiar TEXT NOT NULL,
    origem_ficticia    TEXT
);
COMMENT ON TABLE familia IS 'Hub de núcleos familiares fictícios.';

CREATE TABLE IF NOT EXISTS membro_familia (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    familia_id     UUID NOT NULL REFERENCES familia(id) ON DELETE CASCADE,
    papel_familiar TEXT,               -- pai/mae/filho/avo/etc.
    CONSTRAINT uq_membro_familia UNIQUE (pessoa_id, familia_id)
);
COMMENT ON TABLE membro_familia IS 'Vínculo persona <-> família.';

CREATE TABLE IF NOT EXISTS parentesco (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_a     UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_b     UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo_parentesco TEXT NOT NULL,
    grau            INTEGER CHECK (grau BETWEEN 1 AND 20)
);
COMMENT ON TABLE parentesco IS 'Grafo de parentesco entre personas.';

CREATE TABLE IF NOT EXISTS arvore_genealogica (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    geracao     INTEGER NOT NULL,
    ramo        TEXT CHECK (ramo IN ('paterno','materno'))
);
COMMENT ON TABLE arvore_genealogica IS 'Posição de cada persona na árvore genealógica.';

CREATE TABLE IF NOT EXISTS heranca (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_herdeiro  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_falecido  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data                DATE,
    origem              TEXT
);
COMMENT ON TABLE heranca IS 'Heranças recebidas por personas fictícias.';

CREATE TABLE IF NOT EXISTS heranca_item (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    heranca_id     UUID NOT NULL REFERENCES heranca(id) ON DELETE CASCADE,
    tipo_bem       TEXT,
    valor_estimado NUMERIC(14,2),
    descricao      TEXT
);
COMMENT ON TABLE heranca_item IS 'Bens que compõem a herança.';

CREATE TABLE IF NOT EXISTS doacao_familiar (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_doador   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_receptor UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    item               TEXT,
    data               DATE,
    motivo             TEXT
);
COMMENT ON TABLE doacao_familiar IS 'Doações entre membros da família.';

CREATE TABLE IF NOT EXISTS condicao_genetica (
    id                       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_condicao_ficticia   TEXT NOT NULL,
    linha_familiar           TEXT CHECK (linha_familiar IN ('paterna','materna')),
    percentual_manifestacao  NUMERIC(5,2) CHECK (percentual_manifestacao BETWEEN 0 AND 100)
);
COMMENT ON TABLE condicao_genetica IS 'Catálogo de condições genéticas fictícias.';

CREATE TABLE IF NOT EXISTS predisposicao_genetica (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id             UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    condicao_id           UUID NOT NULL REFERENCES condicao_genetica(id) ON DELETE CASCADE,
    grau_predisposicao    NUMERIC(5,2) CHECK (grau_predisposicao BETWEEN 0 AND 1)
);
COMMENT ON TABLE predisposicao_genetica IS 'Predisposição individual a condições hereditárias.';

CREATE TABLE IF NOT EXISTS ancestralidade_ficticia (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    origem_percentual NUMERIC(5,2) CHECK (origem_percentual BETWEEN 0 AND 100),
    regiao_ficticia   TEXT
);
COMMENT ON TABLE ancestralidade_ficticia IS 'Composição ancestral fictícia (europeia/africana/indígena/etc).';