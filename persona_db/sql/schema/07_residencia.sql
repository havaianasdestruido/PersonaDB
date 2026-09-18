-- ============================================================================
-- PersonaDB - 07_residencia.sql (Domínio 07 - Residência)
-- ----------------------------------------------------------------------------
-- Hub: endereco. Satélites: residencia, historico_residencia, condominio,
-- taxa_condominio, vizinho, contrato_aluguel, financiamento_imobiliario.
-- Resolve FKs cruzadas pendentes dos domínios 05 e 06:
--   empresa.endereco_id -> endereco(id)
--   imovel.endereco_id  -> endereco(id)
-- ============================================================================

CREATE TABLE IF NOT EXISTS endereco (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    logradouro_ficticio TEXT NOT NULL,
    numero              TEXT,
    bairro              TEXT,
    cidade_ficticia     TEXT,
    uf                  CHAR(2),
    cep_ficticio        TEXT
);
COMMENT ON TABLE endereco IS 'Endereços 100% fictícios.';

CREATE TABLE IF NOT EXISTS residencia (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    endereco_id  UUID NOT NULL REFERENCES endereco(id) ON DELETE CASCADE,
    tipo_posse   TEXT CHECK (tipo_posse IN ('proprio','alugado','cedido','financiado')),
    data_entrada DATE
);
COMMENT ON TABLE residencia IS 'Residência atual da persona.';

CREATE TABLE IF NOT EXISTS historico_residencia (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    endereco_id  UUID NOT NULL REFERENCES endereco(id) ON DELETE CASCADE,
    data_entrada DATE,
    data_saida   DATE,
    motivo_mudanca TEXT
);
COMMENT ON TABLE historico_residencia IS 'Endereços anteriores da persona.';

CREATE TABLE IF NOT EXISTS condominio (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome            TEXT NOT NULL,
    endereco_id     UUID NOT NULL REFERENCES endereco(id) ON DELETE CASCADE,
    numero_unidades INTEGER
);
COMMENT ON TABLE condominio IS 'Condomínios fictícios.';

CREATE TABLE IF NOT EXISTS taxa_condominio (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    residencia_id  UUID NOT NULL REFERENCES residencia(id) ON DELETE CASCADE,
    mes_referencia DATE,
    valor          NUMERIC(10,2)
);
COMMENT ON TABLE taxa_condominio IS 'Taxas mensais de condomínio.';

CREATE TABLE IF NOT EXISTS vizinho (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_a         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_b         UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    endereco_id         UUID NOT NULL REFERENCES endereco(id) ON DELETE CASCADE,
    periodo_convivencia TEXT
);
COMMENT ON TABLE vizinho IS 'Relações de vizinhança entre personas.';

CREATE TABLE IF NOT EXISTS contrato_aluguel (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    imovel_id    UUID NOT NULL REFERENCES imovel(id) ON DELETE CASCADE,
    valor_mensal NUMERIC(12,2),
    data_inicio  DATE,
    data_fim     DATE
);
COMMENT ON TABLE contrato_aluguel IS 'Contratos de locação residencial.';

CREATE TABLE IF NOT EXISTS financiamento_imobiliario (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    imovel_id        UUID NOT NULL REFERENCES imovel(id) ON DELETE CASCADE,
    financiamento_id UUID NOT NULL REFERENCES financiamento(id) ON DELETE CASCADE
);
COMMENT ON TABLE financiamento_imobiliario IS 'Vínculo imóvel <-> financiamento imobiliário.';

-- ------------------------------------------------------------------ --
-- FKs cruzadas pendentes dos domínios 05 e 06
-- ------------------------------------------------------------------ --
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'empresa_endereco_id_fkey') THEN
        ALTER TABLE empresa
            ADD CONSTRAINT empresa_endereco_id_fkey
            FOREIGN KEY (endereco_id) REFERENCES endereco(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'imovel_endereco_id_fkey') THEN
        ALTER TABLE imovel
            ADD CONSTRAINT imovel_endereco_id_fkey
            FOREIGN KEY (endereco_id) REFERENCES endereco(id) ON DELETE SET NULL;
    END IF;
END
$$;