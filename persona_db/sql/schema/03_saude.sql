-- ============================================================================
-- PersonaDB - 03_saude.sql (Domínio 03 - Saúde)
-- ----------------------------------------------------------------------------
-- Hubs: doenca, sintoma, medicamento, cirurgiao, hospital, leito, vacina,
-- plano_saude, convenio. Demais tabelas são satélites de pessoa.
-- Ordem de definição respeita dependências de FKs.
-- ============================================================================

-- ------------------------------------------------------------------ --
-- Catálogos básicos
-- ------------------------------------------------------------------ --
CREATE TABLE IF NOT EXISTS doenca (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome             TEXT NOT NULL,
    categoria        TEXT,
    gravidade_padrao TEXT
);
COMMENT ON TABLE doenca IS 'Catálogo de doenças fictícias (não corresponde a CID real).';

CREATE TABLE IF NOT EXISTS sintoma (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome      TEXT NOT NULL,
    categoria TEXT
);
COMMENT ON TABLE sintoma IS 'Catálogo de sintomas fictícios.';

CREATE TABLE IF NOT EXISTS medicamento (
    id                       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_ficticio            TEXT NOT NULL,
    principio_ativo_ficticio TEXT
);
COMMENT ON TABLE medicamento IS 'Medicamentos com nomes 100% fictícios.';

-- ------------------------------------------------------------------ --
-- Hubs de saúde
-- ------------------------------------------------------------------ --
CREATE TABLE IF NOT EXISTS cirurgiao (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome          TEXT NOT NULL,
    especialidade TEXT
);
COMMENT ON TABLE cirurgiao IS 'Médicos cirurgiões fictícios.';

CREATE TABLE IF NOT EXISTS hospital (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome        TEXT NOT NULL,
    endereco_id UUID,
    tipo        TEXT
);
COMMENT ON TABLE hospital IS 'Hospitais fictícios.';

CREATE TABLE IF NOT EXISTS leito (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_id UUID NOT NULL REFERENCES hospital(id) ON DELETE CASCADE,
    numero      TEXT,
    ala         TEXT
);
COMMENT ON TABLE leito IS 'Leitos por hospital.';

CREATE TABLE IF NOT EXISTS vacina (
    id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    tipo TEXT
);
COMMENT ON TABLE vacina IS 'Catálogo de vacinas fictícias.';

CREATE TABLE IF NOT EXISTS plano_saude (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operadora   TEXT NOT NULL,
    cobertura   TEXT,
    mensalidade NUMERIC(10,2)
);
COMMENT ON TABLE plano_saude IS 'Planos de saúde fictícios.';

CREATE TABLE IF NOT EXISTS convenio (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome                  TEXT NOT NULL,
    hospitais_conveniados INTEGER DEFAULT 0
);
COMMENT ON TABLE convenio IS 'Convênios médicos fictícios.';

-- ------------------------------------------------------------------ --
-- Satélites de pessoa
-- ------------------------------------------------------------------ --
CREATE TABLE IF NOT EXISTS doenca_pessoa (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    doenca_id         UUID NOT NULL REFERENCES doenca(id) ON DELETE CASCADE,
    data_diagnostico  DATE,
    estagio           TEXT,
    status            TEXT CHECK (status IN ('ativa','remissao','curada'))
);
COMMENT ON TABLE doenca_pessoa IS 'Diagnósticos individuais de doenças.';

CREATE TABLE IF NOT EXISTS tratamento (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    doenca_pessoa_id UUID NOT NULL REFERENCES doenca_pessoa(id) ON DELETE CASCADE,
    tipo             TEXT,
    data_inicio      DATE,
    data_fim         DATE
);
COMMENT ON TABLE tratamento IS 'Tratamentos associados a diagnósticos.';

CREATE TABLE IF NOT EXISTS sintoma_ocorrencia (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    sintoma_id  UUID NOT NULL REFERENCES sintoma(id) ON DELETE CASCADE,
    data_inicio DATE,
    intensidade TEXT CHECK (intensidade IN ('leve','moderado','intenso','severo'))
);
COMMENT ON TABLE sintoma_ocorrencia IS 'Episódios sintomáticos vividos pela persona.';

CREATE TABLE IF NOT EXISTS exame (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo_exame TEXT NOT NULL,
    data       DATE,
    local      TEXT
);
COMMENT ON TABLE exame IS 'Exames médicos realizados (fictícios).';

CREATE TABLE IF NOT EXISTS exame_resultado (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exame_id   UUID NOT NULL REFERENCES exame(id) ON DELETE CASCADE,
    parametro  TEXT NOT NULL,
    valor      TEXT,
    referencia TEXT
) PARTITION BY HASH (exame_id);
COMMENT ON TABLE exame_resultado IS 'Resultado de parâmetros de exames (particionada por hash). Partições em 98_indexes.sql.';

CREATE TABLE IF NOT EXISTS prescricao (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    medicamento_id UUID NOT NULL REFERENCES medicamento(id) ON DELETE CASCADE,
    medico_id      UUID NOT NULL REFERENCES cirurgiao(id) ON DELETE CASCADE,
    data           DATE
);
COMMENT ON TABLE prescricao IS 'Prescrições médicas fictícias.';

CREATE TABLE IF NOT EXISTS dosagem (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prescricao_id UUID NOT NULL REFERENCES prescricao(id) ON DELETE CASCADE,
    quantidade    NUMERIC(8,2),
    unidade       TEXT,
    frequencia    TEXT
);
COMMENT ON TABLE dosagem IS 'Posologia de cada prescrição.';

CREATE TABLE IF NOT EXISTS cirurgia (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo         TEXT,
    data         DATE,
    cirurgiao_id UUID NOT NULL REFERENCES cirurgiao(id) ON DELETE CASCADE,
    hospital_id  UUID NOT NULL REFERENCES hospital(id) ON DELETE CASCADE
);
COMMENT ON TABLE cirurgia IS 'Procedimentos cirúrgicos realizados.';

CREATE TABLE IF NOT EXISTS internacao (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    hospital_id  UUID NOT NULL REFERENCES hospital(id) ON DELETE CASCADE,
    leito_id     UUID NOT NULL REFERENCES leito(id) ON DELETE CASCADE,
    data_entrada DATE,
    data_saida   DATE,
    motivo       TEXT
);
COMMENT ON TABLE internacao IS 'Internações hospitalares.';

CREATE TABLE IF NOT EXISTS alta_hospitalar (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    internacao_id  UUID NOT NULL REFERENCES internacao(id) ON DELETE CASCADE,
    data           DATE,
    condicao_saida TEXT
);
COMMENT ON TABLE alta_hospitalar IS 'Registro de alta após internação.';

CREATE TABLE IF NOT EXISTS vacina_dose (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    vacina_id        UUID NOT NULL REFERENCES vacina(id) ON DELETE CASCADE,
    data             DATE,
    dose_numero      INTEGER,
    local_aplicacao  TEXT
);
COMMENT ON TABLE vacina_dose IS 'Doses de vacinas recebidas pela persona.';

CREATE TABLE IF NOT EXISTS alergia (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    substancia TEXT NOT NULL,
    gravidade  TEXT CHECK (gravidade IN ('leve','moderada','grave'))
);
COMMENT ON TABLE alergia IS 'Alergias da persona.';

CREATE TABLE IF NOT EXISTS alergia_reacao (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alergia_id          UUID NOT NULL REFERENCES alergia(id) ON DELETE CASCADE,
    sintoma_id          UUID NOT NULL REFERENCES sintoma(id) ON DELETE CASCADE,
    tratamento_aplicado TEXT
);
COMMENT ON TABLE alergia_reacao IS 'Reações alérgicas e tratamento.';

CREATE TABLE IF NOT EXISTS condicao_cronica (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome             TEXT NOT NULL,
    data_diagnostico DATE,
    controle_atual   TEXT
);
COMMENT ON TABLE condicao_cronica IS 'Condições crônicas em acompanhamento.';

CREATE TABLE IF NOT EXISTS saude_mental_registro (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    condicao_ficticia TEXT NOT NULL,
    data_inicio       DATE,
    status            TEXT
);
COMMENT ON TABLE saude_mental_registro IS 'Registros de saúde mental fictícios.';

CREATE TABLE IF NOT EXISTS terapia (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo         TEXT,
    terapeuta_id UUID,
    data_inicio  DATE
);
COMMENT ON TABLE terapia IS 'Terapias em curso (psicológica, fono, etc).';

CREATE TABLE IF NOT EXISTS sessao_terapia (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    terapia_id     UUID NOT NULL REFERENCES terapia(id) ON DELETE CASCADE,
    data           DATE,
    duracao        INTERVAL,
    notas_ficticias TEXT
);
COMMENT ON TABLE sessao_terapia IS 'Sessões individuais de terapia.';

CREATE TABLE IF NOT EXISTS seguro_saude (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    plano_id          UUID NOT NULL REFERENCES plano_saude(id) ON DELETE CASCADE,
    data_contratacao  DATE
);
COMMENT ON TABLE seguro_saude IS 'Contratação de seguro/plano de saúde.';