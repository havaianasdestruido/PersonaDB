-- ============================================================================
-- PersonaDB - 25_juncoes.sql (Domínio 25 - Tabelas de junção N:N explícitas)
-- ----------------------------------------------------------------------------
-- Junções explícitas usadas para consultas cruzadas frequentes.
-- Chaves compostas (pessoa_id + entidade_id) para evitar duplicação.
-- ============================================================================

CREATE TABLE IF NOT EXISTS pessoa_habilidade (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    habilidade_id  UUID NOT NULL REFERENCES habilidade(id) ON DELETE CASCADE,
    nivel          TEXT,
    PRIMARY KEY (pessoa_id, habilidade_id)
);
COMMENT ON TABLE pessoa_habilidade IS 'Junção persona <-> habilidade (domínio 17).';

CREATE TABLE IF NOT EXISTS pessoa_idioma_nivel (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    idioma_id      UUID NOT NULL REFERENCES pessoa_idioma(id) ON DELETE CASCADE,
    nivel_leitura  TEXT,
    nivel_fala     TEXT,
    PRIMARY KEY (pessoa_id, idioma_id)
);
COMMENT ON TABLE pessoa_idioma_nivel IS 'Níveis de leitura/fala por idioma (domínio 01).';

CREATE TABLE IF NOT EXISTS pessoa_hobby (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    hobby_id       UUID NOT NULL REFERENCES hobby(id) ON DELETE CASCADE,
    desde_quando   DATE,
    PRIMARY KEY (pessoa_id, hobby_id)
);
COMMENT ON TABLE pessoa_hobby IS 'Junção persona <-> hobby (domínio 19).';

CREATE TABLE IF NOT EXISTS pessoa_grupo_social (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    grupo_id       UUID NOT NULL REFERENCES grupo_social(id) ON DELETE CASCADE,
    papel          TEXT,
    PRIMARY KEY (pessoa_id, grupo_id)
);
COMMENT ON TABLE pessoa_grupo_social IS 'Junção persona <-> grupo social (domínio 09).';

CREATE TABLE IF NOT EXISTS pessoa_evento (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    evento_id      UUID NOT NULL REFERENCES evento_social(id) ON DELETE CASCADE,
    papel          TEXT,
    PRIMARY KEY (pessoa_id, evento_id)
);
COMMENT ON TABLE pessoa_evento IS 'Junção persona <-> evento social (domínio 09).';

CREATE TABLE IF NOT EXISTS pessoa_doenca_familiar (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    condicao_genetica_id UUID NOT NULL REFERENCES condicao_genetica(id) ON DELETE CASCADE,
    grau_risco     NUMERIC(5,2) CHECK (grau_risco BETWEEN 0 AND 1),
    PRIMARY KEY (pessoa_id, condicao_genetica_id)
);
COMMENT ON TABLE pessoa_doenca_familiar IS 'Risco de condições hereditárias (domínio 02).';

CREATE TABLE IF NOT EXISTS pessoa_pet (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pet_id         UUID NOT NULL REFERENCES pet(id) ON DELETE CASCADE,
    tipo_vinculo   TEXT CHECK (tipo_vinculo IN ('dono','cuidador')),
    PRIMARY KEY (pessoa_id, pet_id)
);
COMMENT ON TABLE pessoa_pet IS 'Junção persona <-> pet (domínio 14).';

CREATE TABLE IF NOT EXISTS pessoa_veiculo (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    veiculo_id     UUID NOT NULL REFERENCES veiculo(id) ON DELETE CASCADE,
    tipo_posse     TEXT CHECK (tipo_posse IN ('proprietario','condutor_autorizado')),
    PRIMARY KEY (pessoa_id, veiculo_id)
);
COMMENT ON TABLE pessoa_veiculo IS 'Junção persona <-> veículo (domínio 06).';

CREATE TABLE IF NOT EXISTS pessoa_imovel (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    imovel_id      UUID NOT NULL REFERENCES imovel(id) ON DELETE CASCADE,
    tipo_posse     TEXT,
    PRIMARY KEY (pessoa_id, imovel_id)
);
COMMENT ON TABLE pessoa_imovel IS 'Junção persona <-> imóvel (domínio 06).';

CREATE TABLE IF NOT EXISTS pessoa_processo (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    processo_id    UUID NOT NULL REFERENCES processo(id) ON DELETE CASCADE,
    papel          TEXT,
    PRIMARY KEY (pessoa_id, processo_id)
);
COMMENT ON TABLE pessoa_processo IS 'Junção persona <-> processo (domínio 11).';

CREATE TABLE IF NOT EXISTS pessoa_eleicao (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    eleicao_id     UUID NOT NULL REFERENCES eleicao(id) ON DELETE CASCADE,
    participou     BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (pessoa_id, eleicao_id)
);
COMMENT ON TABLE pessoa_eleicao IS 'Junção persona <-> eleição (domínio 12).';

CREATE TABLE IF NOT EXISTS pessoa_viagem_companheiro (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    viagem_id      UUID NOT NULL REFERENCES viagem(id) ON DELETE CASCADE,
    papel          TEXT,
    PRIMARY KEY (pessoa_id, viagem_id)
);
COMMENT ON TABLE pessoa_viagem_companheiro IS 'Junção persona <-> viagem como acompanhante.';

CREATE TABLE IF NOT EXISTS pessoa_empresa_socio (
    pessoa_id             UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    empresa_id            UUID NOT NULL REFERENCES empresa(id) ON DELETE CASCADE,
    percentual_participacao NUMERIC(5,2) CHECK (percentual_participacao BETWEEN 0 AND 100),
    PRIMARY KEY (pessoa_id, empresa_id)
);
COMMENT ON TABLE pessoa_empresa_socio IS 'Sócios de empresas (domínio 05).';

CREATE TABLE IF NOT EXISTS pessoa_religiao_historico (
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    crenca_id      UUID NOT NULL REFERENCES crenca(id) ON DELETE CASCADE,
    data_inicio    DATE,
    data_fim       DATE,
    PRIMARY KEY (pessoa_id, crenca_id, data_inicio)
);
COMMENT ON TABLE pessoa_religiao_historico IS 'Histórico de crenças (domínio 18).';

CREATE TABLE IF NOT EXISTS pessoa_documento_historico (
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    documento_id      UUID NOT NULL REFERENCES pessoa_documento(id) ON DELETE CASCADE,
    data_emissao      DATE,
    data_expiracao    DATE,
    PRIMARY KEY (pessoa_id, documento_id)
);
COMMENT ON TABLE pessoa_documento_historico IS 'Histórico de emissões de documentos (domínio 01).';