-- ============================================================================
-- PersonaDB - 01_identidade.sql (Domínio 01 - Identidade & Biometria)
-- ----------------------------------------------------------------------------
-- Pessoa -> nome anterior/apelido/documentos/biometria/foto/assinatura/
--           características físicas/marcas distintivas/idiomas.
-- Idempotente, PostgreSQL 16. Convenções: PK UUID, FK ON DELETE CASCADE,
-- dinheiro NUMERIC, datas DATE.
-- ============================================================================

CREATE TABLE IF NOT EXISTS pessoa_nome_anterior (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome_antigo  TEXT NOT NULL,
    motivo_mudanca TEXT,
    data_mudanca DATE
);
COMMENT ON TABLE pessoa_nome_anterior IS 'Nomes anteriores da persona (retificação civil, casamento etc).';

CREATE TABLE IF NOT EXISTS pessoa_apelido (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id     UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    apelido       TEXT NOT NULL,
    origem        TEXT,
    contexto_uso  TEXT
);
COMMENT ON TABLE pessoa_apelido IS 'Apelidos/fuãs informais usados pela persona.';

CREATE TABLE IF NOT EXISTS pessoa_documento (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo             TEXT NOT NULL,           -- RG/CPF/passaporte/CNH/título de eleitor
    numero_ficticio  TEXT NOT NULL,
    orgao_emissor    TEXT,
    validade         DATE,
    CONSTRAINT uq_pessoa_documento_numero UNIQUE (tipo, numero_ficticio)
);
COMMENT ON TABLE pessoa_documento IS 'Documentos fictícios com numeração própria (sem dados reais).';

CREATE TABLE IF NOT EXISTS pessoa_biometria (
    id                        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id                 UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    impressao_digital_ficticia TEXT NOT NULL,     -- hex 40 chars
    padrao_iris_ficticio      TEXT NOT NULL,      -- base64 64 chars
    hash_facial_ficticio      TEXT NOT NULL       -- sha256
);
COMMENT ON TABLE pessoa_biometria IS 'Biometria 100% fictícia, derivada deterministicamente da persona.';

CREATE TABLE IF NOT EXISTS pessoa_foto (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    url_ficticia TEXT NOT NULL,
    data         DATE,
    contexto     TEXT
);
COMMENT ON TABLE pessoa_foto IS 'URLs fictícias de fotos (nunca apontam para pessoas reais).';

CREATE TABLE IF NOT EXISTS pessoa_assinatura (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    modelo_assinatura TEXT NOT NULL,
    data_registro    DATE
);
COMMENT ON TABLE pessoa_assinatura IS 'Modelo de assinatura fictício.';

CREATE TABLE IF NOT EXISTS pessoa_caracteristica_fisica (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    altura            NUMERIC(5,2) CHECK (altura BETWEEN 1.20 AND 2.40),
    peso              NUMERIC(5,2) CHECK (peso BETWEEN 25.0 AND 300.0),
    cor_olhos         TEXT,
    cor_cabelo        TEXT,
    mao_dominante     TEXT CHECK (mao_dominante IN ('destra', 'canhota', 'ambidestra')),
    tipo_sanguineo    TEXT CHECK (tipo_sanguineo IN ('A','B','AB','O')),
    fator_rh          TEXT CHECK (fator_rh IN ('positivo','negativo')),
    CONSTRAINT uq_pessoa_fisica UNIQUE (pessoa_id)
);
COMMENT ON TABLE pessoa_caracteristica_fisica IS 'Fenótipos físicos herdados (ver engines/genetics.py).';

CREATE TABLE IF NOT EXISTS pessoa_marca_distintiva (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id            UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo                 TEXT CHECK (tipo IN ('tatuagem','cicatriz','sinal','pintinha','protesis')),
    localizacao_corporal TEXT,
    descricao            TEXT,
    data_aquisicao       DATE
);
COMMENT ON TABLE pessoa_marca_distintiva IS 'Marcas corporais distintivas fictícias.';

CREATE TABLE IF NOT EXISTS pessoa_idioma (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    idioma            TEXT NOT NULL,
    nivel_fluencia    TEXT CHECK (nivel_fluencia IN ('basico','intermediario','avancado','fluente','nativo')),
    forma_aprendizado TEXT
);
COMMENT ON TABLE pessoa_idioma IS 'Idiomas falados pela persona.';