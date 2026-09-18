-- ============================================================================
-- PersonaDB - 22_comunicacao.sql (Domínio 22 - Comunicação)
-- ----------------------------------------------------------------------------
-- Satélites de pessoa: telefone, email, correspondencia,
-- ligacao_registro, mensagem_registro.
-- ============================================================================

CREATE TABLE IF NOT EXISTS telefone (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id       UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    numero_ficticio TEXT NOT NULL,
    tipo            TEXT CHECK (tipo IN ('fixo','celular'))
);
COMMENT ON TABLE telefone IS 'Telefones 100% fictícios.';

CREATE TABLE IF NOT EXISTS email (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id          UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    endereco_ficticio  TEXT NOT NULL,
    provedor           TEXT,
    CONSTRAINT uq_email_endereco UNIQUE (endereco_ficticio)
);
COMMENT ON TABLE email IS 'E-mails fictícios.';

CREATE TABLE IF NOT EXISTS correspondencia (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_remetente     UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_destinatario  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo                    TEXT,
    data                    DATE
);
COMMENT ON TABLE correspondencia IS 'Correspondências físicas trocadas.';

CREATE TABLE IF NOT EXISTS ligacao_registro (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_a  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_b  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data         TIMESTAMPTZ,
    duracao      INTERVAL
);
COMMENT ON TABLE ligacao_registro IS 'Registros de chamadas fictícios.';

CREATE TABLE IF NOT EXISTS mensagem_registro (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_a UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_b UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    plataforma  TEXT,
    data        TIMESTAMPTZ
);
COMMENT ON TABLE mensagem_registro IS 'Registros de mensagens trocadas.';