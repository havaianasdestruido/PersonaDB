-- ============================================================================
-- PersonaDB - 05_carreira.sql (Domínio 05 - Carreira & Trabalho)
-- ----------------------------------------------------------------------------
-- Hubs: empresa, cargo.
-- Satélites: contrato_trabalho, historico_emprego, salario, holerite,
-- beneficio, avaliacao_desempenho, promocao, demissao, ferias,
-- licenca_trabalho, habilidade_profissional, certificacao_profissional,
-- sindicato_ficticio, colega_trabalho.
-- Também resolve a FK cruzada estagio.empresa_id (domínio 04).
-- FK cruzada: empresa.endereco_id -> endereco(id) resolvida em 07_residencia.sql.
-- ============================================================================

CREATE TABLE IF NOT EXISTS empresa (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome            TEXT NOT NULL,
    cnpj_ficticio   TEXT NOT NULL,
    ramo_atividade  TEXT,
    endereco_id     UUID,
    CONSTRAINT uq_empresa_cnpj UNIQUE (cnpj_ficticio)
);
COMMENT ON TABLE empresa IS 'Empregadores fictícios com CNPJ sintético válido.';

CREATE TABLE IF NOT EXISTS cargo (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome              TEXT NOT NULL,
    nivel_hierarquico INTEGER
);
COMMENT ON TABLE cargo IS 'Cargos fictícios com nível hierárquico.';

CREATE TABLE IF NOT EXISTS contrato_trabalho (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    empresa_id   UUID NOT NULL REFERENCES empresa(id) ON DELETE CASCADE,
    cargo_id     UUID NOT NULL REFERENCES cargo(id) ON DELETE CASCADE,
    tipo_contrato TEXT CHECK (tipo_contrato IN ('CLT','PJ','estagio','temporario','publico')),
    data_inicio  DATE,
    data_fim     DATE
);
COMMENT ON TABLE contrato_trabalho IS 'Contratos de trabalho vigentes/históricos.';

CREATE TABLE IF NOT EXISTS historico_emprego (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    empresa_id   UUID NOT NULL REFERENCES empresa(id) ON DELETE CASCADE,
    cargo_id     UUID NOT NULL REFERENCES cargo(id) ON DELETE CASCADE,
    inicio       DATE,
    fim          DATE,
    motivo_saida TEXT
);
COMMENT ON TABLE historico_emprego IS 'Linha do tempo dos empregos da persona.';

CREATE TABLE IF NOT EXISTS salario (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contrato_id  UUID NOT NULL REFERENCES contrato_trabalho(id) ON DELETE CASCADE,
    valor        NUMERIC(14,2) NOT NULL,
    data_vigencia DATE
);
COMMENT ON TABLE salario IS 'Histórico salarial por contrato.';

CREATE TABLE IF NOT EXISTS holerite (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contrato_id     UUID NOT NULL REFERENCES contrato_trabalho(id) ON DELETE CASCADE,
    mes_referencia  DATE,
    valor_liquido   NUMERIC(14,2),
    descontos       NUMERIC(14,2)
);
COMMENT ON TABLE holerite IS 'Holerites mensais fictícios.';

CREATE TABLE IF NOT EXISTS beneficio (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contrato_id  UUID NOT NULL REFERENCES contrato_trabalho(id) ON DELETE CASCADE,
    tipo         TEXT,
    valor        NUMERIC(12,2)
);
COMMENT ON TABLE beneficio IS 'Benefícios corporativos (VT, VA, plano, etc).';

CREATE TABLE IF NOT EXISTS avaliacao_desempenho (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    empresa_id     UUID NOT NULL REFERENCES empresa(id) ON DELETE CASCADE,
    periodo        TEXT,
    nota           NUMERIC(4,2) CHECK (nota BETWEEN 0 AND 10),
    feedback_ficticio TEXT
);
COMMENT ON TABLE avaliacao_desempenho IS 'Avaliações periódicas de desempenho.';

CREATE TABLE IF NOT EXISTS promocao (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    empresa_id        UUID NOT NULL REFERENCES empresa(id) ON DELETE CASCADE,
    cargo_anterior_id UUID NOT NULL REFERENCES cargo(id) ON DELETE CASCADE,
    cargo_novo_id     UUID NOT NULL REFERENCES cargo(id) ON DELETE CASCADE,
    data              DATE
);
COMMENT ON TABLE promocao IS 'Promoções de cargo.';

CREATE TABLE IF NOT EXISTS demissao (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contrato_id  UUID NOT NULL REFERENCES contrato_trabalho(id) ON DELETE CASCADE,
    data         DATE,
    motivo       TEXT,
    tipo         TEXT CHECK (tipo IN ('justa_causa','sem_justa_causa','pedido'))
);
COMMENT ON TABLE demissao IS 'Desligamentos e rescisões.';

CREATE TABLE IF NOT EXISTS ferias (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contrato_id  UUID NOT NULL REFERENCES contrato_trabalho(id) ON DELETE CASCADE,
    data_inicio  DATE,
    data_fim     DATE,
    dias         INTEGER
);
COMMENT ON TABLE ferias IS 'Períodos de férias.';

CREATE TABLE IF NOT EXISTS licenca_trabalho (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    empresa_id   UUID NOT NULL REFERENCES empresa(id) ON DELETE CASCADE,
    tipo         TEXT,
    data_inicio  DATE,
    data_fim     DATE
);
COMMENT ON TABLE licenca_trabalho IS 'Licenças (saúde, maternidade, etc).';

CREATE TABLE IF NOT EXISTS habilidade_profissional (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome_habilidade TEXT NOT NULL,
    nivel          TEXT CHECK (nivel IN ('basico','intermediario','avancado'))
);
COMMENT ON TABLE habilidade_profissional IS 'Habilidades técnicas da persona.';

CREATE TABLE IF NOT EXISTS certificacao_profissional (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id     UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome          TEXT NOT NULL,
    orgao_emissor TEXT,
    validade      DATE
);
COMMENT ON TABLE certificacao_profissional IS 'Certificações profissionais.';

CREATE TABLE IF NOT EXISTS sindicato_ficticio (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id     UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome_sindicato TEXT,
    categoria     TEXT
);
COMMENT ON TABLE sindicato_ficticio IS 'Sindicatos de categoria fictícios.';

CREATE TABLE IF NOT EXISTS colega_trabalho (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_a UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_b UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    empresa_id  UUID NOT NULL REFERENCES empresa(id) ON DELETE CASCADE,
    periodo     TEXT
);
COMMENT ON TABLE colega_trabalho IS 'Relações de coleguismo no trabalho.';

-- ------------------------------------------------------------------ --
-- FK cruzada: estagio (04_educacao) -> empresa(id) (dono: este arquivo)
-- ------------------------------------------------------------------ --
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'estagio_empresa_id_fkey') THEN
        ALTER TABLE estagio
            ADD CONSTRAINT estagio_empresa_id_fkey
            FOREIGN KEY (empresa_id) REFERENCES empresa(id) ON DELETE CASCADE;
    END IF;
END
$$;