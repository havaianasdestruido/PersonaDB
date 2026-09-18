-- ============================================================================
-- PersonaDB - 15_consumo.sql (Domínio 15 - Consumo)
-- ----------------------------------------------------------------------------
-- Hubs: produto, loja.
-- Satélites: compra, item_compra, avaliacao_produto, assinatura_servico,
-- devolucao, programa_fidelidade, carrinho_abandonado, historico_preco.
-- ============================================================================

CREATE TABLE IF NOT EXISTS produto (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome          TEXT NOT NULL,
    categoria     TEXT,
    marca_ficticia TEXT
);
COMMENT ON TABLE produto IS 'Produtos de consumo fictícios.';

CREATE TABLE IF NOT EXISTS loja (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome        TEXT NOT NULL,
    tipo        TEXT CHECK (tipo IN ('fisica','online','marketplace')),
    endereco_id UUID
);
COMMENT ON TABLE loja IS 'Lojas fictícias.';

CREATE TABLE IF NOT EXISTS compra (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    loja_id     UUID NOT NULL REFERENCES loja(id) ON DELETE CASCADE,
    data        DATE,
    valor_total NUMERIC(14,2)
);
COMMENT ON TABLE compra IS 'Compras realizadas pela persona.';

CREATE TABLE IF NOT EXISTS item_compra (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    compra_id       UUID NOT NULL REFERENCES compra(id) ON DELETE CASCADE,
    produto_id      UUID NOT NULL REFERENCES produto(id) ON DELETE CASCADE,
    quantidade      INTEGER,
    valor_unitario  NUMERIC(12,2)
);
COMMENT ON TABLE item_compra IS 'Itens de cada compra.';

CREATE TABLE IF NOT EXISTS avaliacao_produto (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    produto_id       UUID NOT NULL REFERENCES produto(id) ON DELETE CASCADE,
    nota             NUMERIC(4,2) CHECK (nota BETWEEN 0 AND 10),
    comentario_ficticio TEXT
);
COMMENT ON TABLE avaliacao_produto IS 'Avaliações de produtos.';

CREATE TABLE IF NOT EXISTS assinatura_servico (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    servico      TEXT NOT NULL,
    valor_mensal NUMERIC(10,2),
    data_inicio  DATE
);
COMMENT ON TABLE assinatura_servico IS 'Assinaturas de serviços contínuos.';

CREATE TABLE IF NOT EXISTS devolucao (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    compra_id   UUID NOT NULL REFERENCES compra(id) ON DELETE CASCADE,
    produto_id  UUID NOT NULL REFERENCES produto(id) ON DELETE CASCADE,
    motivo      TEXT,
    data        DATE
);
COMMENT ON TABLE devolucao IS 'Devoluções de produtos.';

CREATE TABLE IF NOT EXISTS programa_fidelidade (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id          UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    loja_id            UUID NOT NULL REFERENCES loja(id) ON DELETE CASCADE,
    pontos_acumulados  INTEGER
);
COMMENT ON TABLE programa_fidelidade IS 'Pontos acumulados em programas de fidelidade.';

CREATE TABLE IF NOT EXISTS carrinho_abandonado (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    loja_id        UUID NOT NULL REFERENCES loja(id) ON DELETE CASCADE,
    itens_ficticios TEXT,
    data           DATE
);
COMMENT ON TABLE carrinho_abandonado IS 'Carrinhos de compra abandonados.';

CREATE TABLE IF NOT EXISTS historico_preco (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    produto_id  UUID NOT NULL REFERENCES produto(id) ON DELETE CASCADE,
    data        DATE,
    valor       NUMERIC(12,2)
);
COMMENT ON TABLE historico_preco IS 'Variação de preços ao longo do tempo.';