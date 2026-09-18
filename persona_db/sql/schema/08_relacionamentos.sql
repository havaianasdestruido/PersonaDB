-- ============================================================================
-- PersonaDB - 08_relacionamentos.sql (Domínio 08 - Relacionamentos & Família nuclear)
-- ----------------------------------------------------------------------------
-- Satélites de pessoa: relacionamento, namoro, casamento, divorcio,
-- uniao_estavel, filho, guarda_compartilhada, pensao_alimenticia,
-- adocao_ficticia, padrinho_madrinha.
-- ============================================================================

CREATE TABLE IF NOT EXISTS relacionamento (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_a  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_b  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo         TEXT,
    data_inicio  DATE,
    data_fim     DATE,
    status       TEXT CHECK (status IN ('ativo','encerrado','pausado'))
);
COMMENT ON TABLE relacionamento IS 'Relações interpessoais afetivas/amorosas.';

CREATE TABLE IF NOT EXISTS namoro (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    relacionamento_id UUID NOT NULL REFERENCES relacionamento(id) ON DELETE CASCADE,
    motivo_termino   TEXT
);
COMMENT ON TABLE namoro IS 'Datalhes de namoros.';

CREATE TABLE IF NOT EXISTS casamento (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_a  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_b  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data         DATE,
    regime_bens  TEXT
);
COMMENT ON TABLE casamento IS 'Casamentos civis fictícios.';

CREATE TABLE IF NOT EXISTS divorcio (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    casamento_id  UUID NOT NULL REFERENCES casamento(id) ON DELETE CASCADE,
    data          DATE,
    motivo_ficticio TEXT
);
COMMENT ON TABLE divorcio IS 'Divórcios.';

CREATE TABLE IF NOT EXISTS uniao_estavel (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_a          UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_b          UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data_inicio          DATE,
    data_reconhecimento  DATE
);
COMMENT ON TABLE uniao_estavel IS 'Uniões estáveis (escritura ou não).';

CREATE TABLE IF NOT EXISTS filho (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_pai    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_mae    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_filho  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data_nascimento  DATE
);
COMMENT ON TABLE filho IS 'Filhos registrados por pai e mãe.';

CREATE TABLE IF NOT EXISTS guarda_compartilhada (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filho_id            UUID NOT NULL REFERENCES filho(id) ON DELETE CASCADE,
    responsavel_pessoa_id UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    percentual_tempo    NUMERIC(5,2) CHECK (percentual_tempo BETWEEN 0 AND 100)
);
COMMENT ON TABLE guarda_compartilhada IS 'Guarda compartilhada de filhos.';

CREATE TABLE IF NOT EXISTS pensao_alimenticia (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_pagador     UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_beneficiario UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    valor_mensal          NUMERIC(12,2),
    data_inicio           DATE
);
COMMENT ON TABLE pensao_alimenticia IS 'Pensões alimentícias entre personas.';

CREATE TABLE IF NOT EXISTS adocao_ficticia (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_adotante UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_adotado  UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data              DATE
);
COMMENT ON TABLE adocao_ficticia IS 'Adoções (parentalidade não-biológica).';

CREATE TABLE IF NOT EXISTS padrinho_madrinha (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_afilhado UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    pessoa_id_padrinho UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    tipo           TEXT CHECK (tipo IN ('batismo','casamento'))
);
COMMENT ON TABLE padrinho_madrinha IS 'Padrinhos/madrinhas de batismo ou casamento.';