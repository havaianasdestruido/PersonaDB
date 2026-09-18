-- ============================================================================
-- PersonaDB - 06_financas.sql (Domínio 06 - Patrimônio & Finanças)
-- ----------------------------------------------------------------------------
-- Hubs: banco, corretora, imovel, veiculo.
-- Satélites: conta_bancaria, cartao_credito, transacao, fatura,
-- investimento, carteira_investimento, imovel_historico, veiculo_historico,
-- divida, financiamento, seguro, patrimonio_snapshot, imposto,
-- declaracao_imposto.
-- FKs cruzadas resolvidas em 07: imovel.endereco_id -> endereco(id).
-- ============================================================================

CREATE TABLE IF NOT EXISTS banco (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome            TEXT NOT NULL,
    codigo_ficticio TEXT NOT NULL,
    CONSTRAINT uq_banco_codigo UNIQUE (codigo_ficticio)
);
COMMENT ON TABLE banco IS 'Bancos fictícios.';

CREATE TABLE IF NOT EXISTS corretora (
    id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    tipo TEXT
);
COMMENT ON TABLE corretora IS 'Corretoras de investimento fictícias.';

CREATE TABLE IF NOT EXISTS conta_bancaria (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id       UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    banco_id        UUID NOT NULL REFERENCES banco(id) ON DELETE CASCADE,
    tipo_conta      TEXT CHECK (tipo_conta IN ('corrente','poupanca','salario','digital')),
    agencia         TEXT,
    numero_ficticio TEXT
);
COMMENT ON TABLE conta_bancaria IS 'Contas bancárias fictícias.';

CREATE TABLE IF NOT EXISTS cartao_credito (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    conta_id   UUID NOT NULL REFERENCES conta_bancaria(id) ON DELETE CASCADE,
    bandeira   TEXT,
    limite     NUMERIC(12,2)
);
COMMENT ON TABLE cartao_credito IS 'Cartões de crédito fictícios.';

CREATE TABLE IF NOT EXISTS transacao (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conta_id    UUID NOT NULL REFERENCES conta_bancaria(id) ON DELETE CASCADE,
    tipo        TEXT CHECK (tipo IN ('debito','credito','pix','ted','doc','boleto')),
    valor       NUMERIC(14,2) NOT NULL,
    data        TIMESTAMPTZ NOT NULL,
    descricao   TEXT
) PARTITION BY RANGE (data);
COMMENT ON TABLE transacao IS 'Transações financeiras fictícias (particionadas por ano). As partições concretas são criadas em 98_indexes.sql.';

CREATE TABLE IF NOT EXISTS fatura (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cartao_id       UUID NOT NULL REFERENCES cartao_credito(id) ON DELETE CASCADE,
    mes_referencia  DATE,
    valor_total     NUMERIC(12,2),
    status_pagamento TEXT CHECK (status_pagamento IN ('pago','pendente','atrasado'))
);
COMMENT ON TABLE fatura IS 'Faturas mensais de cartão.';

CREATE TABLE IF NOT EXISTS investimento (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo           TEXT,
    valor_aplicado NUMERIC(14,2),
    data           DATE,
    corretora_id   UUID NOT NULL REFERENCES corretora(id) ON DELETE CASCADE
);
COMMENT ON TABLE investimento IS 'Aplicações financeiras da persona.';

CREATE TABLE IF NOT EXISTS carteira_investimento (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    valor_total NUMERIC(16,2),
    data_snapshot DATE
);
COMMENT ON TABLE carteira_investimento IS 'Snapshot periódico do patrimônio investido.';

CREATE TABLE IF NOT EXISTS imovel (
    id                     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endereco_id            UUID,
    tipo                   TEXT,
    valor_estimado         NUMERIC(14,2),
    proprietario_pessoa_id UUID REFERENCES pessoa(id) ON DELETE SET NULL
);
COMMENT ON TABLE imovel IS 'Imóveis fictícios (FK endereco resolvida em 07).';

CREATE TABLE IF NOT EXISTS imovel_historico (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    imovel_id UUID NOT NULL REFERENCES imovel(id) ON DELETE CASCADE,
    evento    TEXT CHECK (evento IN ('compra','venda','reforma','doacao')),
    data      DATE,
    valor     NUMERIC(14,2)
);
COMMENT ON TABLE imovel_historico IS 'Movimentações do imóvel.';

CREATE TABLE IF NOT EXISTS veiculo (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    modelo               TEXT NOT NULL,
    ano                  INTEGER,
    placa_ficticia       TEXT NOT NULL,
    proprietario_pessoa_id UUID REFERENCES pessoa(id) ON DELETE SET NULL,
    CONSTRAINT uq_veiculo_placa UNIQUE (placa_ficticia)
);
COMMENT ON TABLE veiculo IS 'Veículos fictícios.';

CREATE TABLE IF NOT EXISTS veiculo_historico (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    veiculo_id  UUID NOT NULL REFERENCES veiculo(id) ON DELETE CASCADE,
    evento      TEXT CHECK (evento IN ('compra','venda','acidente','manutencao')),
    data        DATE,
    valor       NUMERIC(12,2)
);
COMMENT ON TABLE veiculo_historico IS 'Eventos que marcaram o veículo.';

CREATE TABLE IF NOT EXISTS divida (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    credor           TEXT,
    valor            NUMERIC(14,2),
    data_vencimento  DATE,
    status           TEXT CHECK (status IN ('em_aberto','paga','negociada','inadimplente'))
);
COMMENT ON TABLE divida IS 'Dívidas pessoais fictícias.';

CREATE TABLE IF NOT EXISTS financiamento (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo        TEXT CHECK (tipo IN ('imovel','veiculo','pessoal','estudo')),
    valor_total NUMERIC(14,2),
    parcelas    INTEGER,
    taxa_juros  NUMERIC(5,2)
);
COMMENT ON TABLE financiamento IS 'Financiamentos contratados.';

CREATE TABLE IF NOT EXISTS seguro (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id       UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo            TEXT CHECK (tipo IN ('vida','residencial','veicular','viagem','saude')),
    seguradora      TEXT,
    valor_cobertura NUMERIC(14,2)
);
COMMENT ON TABLE seguro IS 'Apolícies de seguro contratadas.';

CREATE TABLE IF NOT EXISTS patrimonio_snapshot (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id          UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data               DATE,
    valor_total_estimado NUMERIC(16,2)
);
COMMENT ON TABLE patrimonio_snapshot IS 'Estimativa de patrimônio em datas.';

CREATE TABLE IF NOT EXISTS imposto (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo             TEXT,
    ano_referencia   INTEGER,
    valor            NUMERIC(14,2)
);
COMMENT ON TABLE imposto IS 'Impostos declarados pela persona.';

CREATE TABLE IF NOT EXISTS declaracao_imposto (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id             UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    ano                   INTEGER,
    status                TEXT CHECK (status IN ('entregue','pendente','caiu_na_malha','restituida')),
    valor_restituicao_ou_debito NUMERIC(14,2)
);
COMMENT ON TABLE declaracao_imposto IS 'Declarações anuais de imposto de renda fictícias.';