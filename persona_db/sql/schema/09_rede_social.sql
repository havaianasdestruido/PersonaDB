-- ============================================================================
-- PersonaDB - 09_rede_social.sql (Domínio 09 - Rede Social)
-- ----------------------------------------------------------------------------
-- Hubs: grupo_social, evento_social, clube.
-- Satélites: amizade, membro_grupo_social, participacao_evento_social,
-- contato_pessoal, inimizade_ficticia.
-- ============================================================================

CREATE TABLE IF NOT EXISTS grupo_social (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome           TEXT NOT NULL,
    tipo           TEXT,
    data_criacao   DATE
);
COMMENT ON TABLE grupo_social IS 'Grupos de convivência fictícios.';

CREATE TABLE IF NOT EXISTS evento_social (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome              TEXT NOT NULL,
    data              TIMESTAMPTZ,
    local_endereco_id UUID
);
COMMENT ON TABLE evento_social IS 'Eventos sociais (festa, encontro, evento).';

CREATE TABLE IF NOT EXISTS clube (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome      TEXT NOT NULL,
    categoria TEXT
);
COMMENT ON TABLE clube IS 'Clubes recreativos/sociais fictícios.';

CREATE TABLE IF NOT EXISTS amizade (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_a          UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_b          UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data_inicio          DATE,
    contexto_conhecimento TEXT
);
COMMENT ON TABLE amizade IS 'Laços de amizade entre personas.';

CREATE TABLE IF NOT EXISTS membro_grupo_social (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    grupo_id     UUID NOT NULL REFERENCES grupo_social(id) ON DELETE CASCADE,
    data_entrada DATE,
    papel        TEXT
);
COMMENT ON TABLE membro_grupo_social IS 'Participação de personas em grupos.';

CREATE TABLE IF NOT EXISTS participacao_evento_social (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    evento_id  UUID NOT NULL REFERENCES evento_social(id) ON DELETE CASCADE,
    papel      TEXT CHECK (papel IN ('convidado','organizador','palestrante'))
);
COMMENT ON TABLE participacao_evento_social IS 'Presença de personas em eventos.';

CREATE TABLE IF NOT EXISTS contato_pessoal (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_contato UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    frequencia_contato TEXT,
    tipo_vinculo      TEXT
);
COMMENT ON TABLE contato_pessoal IS 'Agenda de contatos da persona.';

CREATE TABLE IF NOT EXISTS inimizade_ficticia (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_a  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_b  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    motivo       TEXT,
    data_inicio  DATE
);
COMMENT ON TABLE inimizade_ficticia IS 'Conflitos interpessoais fictícios.';