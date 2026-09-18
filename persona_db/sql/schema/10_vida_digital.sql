-- ============================================================================
-- PersonaDB - 10_vida_digital.sql (Domínio 10 - Vida Digital)
-- ----------------------------------------------------------------------------
-- Satélites de pessoa com hubs locais (dispositivo, conta_digital, jogo).
-- provedor_internet referencia residencia (domínio 07).
-- ============================================================================

CREATE TABLE IF NOT EXISTS dispositivo (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id          UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo               TEXT CHECK (tipo IN ('celular','tablet','notebook','desktop','smarttv','smartwatch')),
    modelo             TEXT,
    sistema_operacional TEXT,
    data_aquisicao     DATE
);
COMMENT ON TABLE dispositivo IS 'Dispositivos eletrônicos da persona.';

CREATE TABLE IF NOT EXISTS conta_digital (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    plataforma       TEXT NOT NULL,
    username_ficticio TEXT,
    data_criacao     DATE
);
COMMENT ON TABLE conta_digital IS 'Contas em plataformas digitais fictícias.';

CREATE TABLE IF NOT EXISTS perfil_rede_social (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conta_digital_id     UUID NOT NULL REFERENCES conta_digital(id) ON DELETE CASCADE,
    seguidores_ficticios INTEGER,
    bio_ficticia         TEXT
);
COMMENT ON TABLE perfil_rede_social IS 'Perfis públicos em redes sociais.';

CREATE TABLE IF NOT EXISTS publicacao_rede_social (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    perfil_id           UUID NOT NULL REFERENCES perfil_rede_social(id) ON DELETE CASCADE,
    data                TIMESTAMPTZ,
    tipo_conteudo       TEXT,
    engajamento_ficticio INTEGER
);
COMMENT ON TABLE publicacao_rede_social IS 'Publicações e posts fictícios.';

CREATE TABLE IF NOT EXISTS historico_navegacao_ficticio (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dispositivo_id   UUID NOT NULL REFERENCES dispositivo(id) ON DELETE CASCADE,
    dominio_visitado TEXT,
    data             TIMESTAMPTZ,
    duracao          INTERVAL
);
COMMENT ON TABLE historico_navegacao_ficticio IS 'Registro de navegação fictício (sem URLs reais).';

CREATE TABLE IF NOT EXISTS jogo (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome      TEXT NOT NULL,
    plataforma TEXT,
    genero    TEXT
);
COMMENT ON TABLE jogo IS 'Jogos fictícios.';

CREATE TABLE IF NOT EXISTS progresso_jogo (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    jogo_id           UUID NOT NULL REFERENCES jogo(id) ON DELETE CASCADE,
    horas_jogadas     INTEGER,
    nivel_atual       INTEGER,
    data_ultima_sessao DATE
);
COMMENT ON TABLE progresso_jogo IS 'Aproveitamento da persona em jogos.';

CREATE TABLE IF NOT EXISTS assinatura_streaming (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    servico      TEXT,
    plano        TEXT,
    data_inicio  DATE,
    valor_mensal NUMERIC(10,2)
);
COMMENT ON TABLE assinatura_streaming IS 'Assinaturas de streaming.';

CREATE TABLE IF NOT EXISTS senha_registro_ficticio (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conta_digital_id    UUID NOT NULL REFERENCES conta_digital(id) ON DELETE CASCADE,
    data_ultima_troca   DATE,
    forca_senha         TEXT CHECK (forca_senha IN ('fraca','media','forte'))
);
COMMENT ON TABLE senha_registro_ficticio IS 'Metadados de senha (nunca a senha real).';

CREATE TABLE IF NOT EXISTS dispositivo_troca_historico (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id            UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    dispositivo_antigo_id UUID NOT NULL REFERENCES dispositivo(id) ON DELETE CASCADE,
    dispositivo_novo_id  UUID NOT NULL REFERENCES dispositivo(id) ON DELETE CASCADE,
    data                 DATE,
    motivo               TEXT
);
COMMENT ON TABLE dispositivo_troca_historico IS 'Troca de aparelhos ao longo do tempo.';

CREATE TABLE IF NOT EXISTS app_instalado (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dispositivo_id  UUID NOT NULL REFERENCES dispositivo(id) ON DELETE CASCADE,
    nome_app        TEXT NOT NULL,
    data_instalacao DATE,
    categoria       TEXT
);
COMMENT ON TABLE app_instalado IS 'Aplicativos instalados por dispositivo.';

CREATE TABLE IF NOT EXISTS provedor_internet (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    residencia_id     UUID NOT NULL REFERENCES residencia(id) ON DELETE CASCADE,
    operadora         TEXT,
    velocidade_contratada TEXT
);
COMMENT ON TABLE provedor_internet IS 'Internet contratada na residência.';