-- ============================================================================
-- PersonaDB - 11_juridico.sql (Domínio 11 - Jurídico)
-- ----------------------------------------------------------------------------
-- Hubs: processo, advogado, tribunal.
-- Satélites: pessoa_processo, ocorrencia_policial, boletim_ocorrencia,
-- julgamento, sentenca, pena, antecedente_criminal, processo_advogado,
-- multa, contrato_juridico.
-- ============================================================================

CREATE TABLE IF NOT EXISTS tribunal (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_ficticio   TEXT NOT NULL,
    jurisdicao      TEXT
);
COMMENT ON TABLE tribunal IS 'Tribunais fictícios.';

CREATE TABLE IF NOT EXISTS processo (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_ficticio TEXT NOT NULL,
    tipo            TEXT,
    tribunal_id     UUID NOT NULL REFERENCES tribunal(id) ON DELETE CASCADE,
    status          TEXT CHECK (status IN ('em_andamento','julgado','arquivado','suspenso')),
    CONSTRAINT uq_processo_numero UNIQUE (numero_ficticio)
);
COMMENT ON TABLE processo IS 'Processos judiciais fictícios.';

CREATE TABLE IF NOT EXISTS pessoa_processo (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    processo_id  UUID NOT NULL REFERENCES processo(id) ON DELETE CASCADE,
    papel        TEXT CHECK (papel IN ('reu','autor','testemunha','terceiro'))
);
COMMENT ON TABLE pessoa_processo IS 'Vínculo persona <-> processo.';

CREATE TABLE IF NOT EXISTS advogado (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome          TEXT NOT NULL,
    oab_ficticia  TEXT NOT NULL,
    CONSTRAINT uq_advogado_oab UNIQUE (oab_ficticia)
);
COMMENT ON TABLE advogado IS 'Advogados fictícios.';

CREATE TABLE IF NOT EXISTS processo_advogado (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    processo_id      UUID NOT NULL REFERENCES processo(id) ON DELETE CASCADE,
    advogado_id      UUID NOT NULL REFERENCES advogado(id) ON DELETE CASCADE,
    parte_representada TEXT
);
COMMENT ON TABLE processo_advogado IS 'Defesas e representações jurídicas.';

CREATE TABLE IF NOT EXISTS ocorrencia_policial (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id       UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo            TEXT,
    data            TIMESTAMPTZ,
    local_endereco_id UUID
);
COMMENT ON TABLE ocorrencia_policial IS 'Ocorrências registradas (como vítima/envolvido).';

CREATE TABLE IF NOT EXISTS boletim_ocorrencia (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ocorrencia_id    UUID NOT NULL REFERENCES ocorrencia_policial(id) ON DELETE CASCADE,
    numero_ficticio  TEXT NOT NULL,
    delegacia        TEXT,
    CONSTRAINT uq_boletim_numero UNIQUE (numero_ficticio)
);
COMMENT ON TABLE boletim_ocorrencia IS 'Boletins de ocorrência fictícios.';

CREATE TABLE IF NOT EXISTS julgamento (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    processo_id   UUID NOT NULL REFERENCES processo(id) ON DELETE CASCADE,
    data          DATE,
    resultado     TEXT
);
COMMENT ON TABLE julgamento IS 'Julgamentos do processo.';

CREATE TABLE IF NOT EXISTS sentenca (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    julgamento_id UUID NOT NULL REFERENCES julgamento(id) ON DELETE CASCADE,
    tipo          TEXT,
    descricao     TEXT
);
COMMENT ON TABLE sentenca IS 'Sentenças proferidas nos julgamentos.';

CREATE TABLE IF NOT EXISTS pena (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sentenca_id      UUID NOT NULL REFERENCES sentenca(id) ON DELETE CASCADE,
    tipo             TEXT CHECK (tipo IN ('multa','prisao','prestacao_servico','restritiva')),
    duracao_ou_valor TEXT
);
COMMENT ON TABLE pena IS 'Penas aplicadas conforme a sentença.';

CREATE TABLE IF NOT EXISTS antecedente_criminal (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    processo_id  UUID NOT NULL REFERENCES processo(id) ON DELETE CASCADE,
    status       TEXT CHECK (status IN ('ativo','arquivado','sancionado'))
);
COMMENT ON TABLE antecedente_criminal IS 'Antecedentes criminais da persona.';

CREATE TABLE IF NOT EXISTS multa (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo           TEXT,
    valor          NUMERIC(12,2),
    data           DATE,
    status_pagamento TEXT CHECK (status_pagamento IN ('paga','pendente','recurso'))
);
COMMENT ON TABLE multa IS 'Multas aplicadas à persona.';

CREATE TABLE IF NOT EXISTS contrato_juridico (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_a   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_b   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo          TEXT,
    data          DATE,
    objeto        TEXT
);
COMMENT ON TABLE contrato_juridico IS 'Contratos privados entre personas.';