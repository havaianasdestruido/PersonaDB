-- ============================================================================
-- PersonaDB - 26_metadata.sql (Metadados do schema e controle)
-- ----------------------------------------------------------------------------
-- Complementa o domínio 24 com informações de versão do schema e views de
-- catálogo. Idempotente.
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    versao              TEXT NOT NULL,
    descricao           TEXT,
    data_aplicacao      TIMESTAMPTZ DEFAULT now()
);
COMMENT ON TABLE schema_version IS 'Versões de schema aplicadas ao banco.';

INSERT INTO schema_version (versao, descricao)
SELECT '1.0.0', 'PersonaDB schema inicial (25 domínios + controle)'
WHERE NOT EXISTS (SELECT 1 FROM schema_version WHERE versao = '1.0.0');

-- ------------------------------------------------------------------ --
-- View de catálogo: tabelas por domínio
-- ------------------------------------------------------------------ --
CREATE OR REPLACE VIEW vw_tabelas_por_dominio AS
SELECT
    table_name,
    CASE
        WHEN table_name ~ '^pessoa'                     THEN '01_identidade'
        WHEN table_name = 'pessoa'                      THEN '00_hub'
        WHEN table_name IN ('familia','membro_familia','parentesco','arvore_genealogica',
                            'heranca','heranca_item','doacao_familiar','condicao_genetica',
                            'predisposicao_genetica','ancestralidade_ficticia')
                                                        THEN '02_genealogia'
        WHEN table_name IN ('luto_ficticio','evento_vida','marco_historico_pessoal',
                            'linha_do_tempo','aniversario','comemoracao')
                                                        THEN '16_timeline'
        ELSE 'outro'
    END AS dominio_provavel
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- ------------------------------------------------------------------ --
-- View de catálogo: contagem de tabelas por domínio (arquivo)
-- ------------------------------------------------------------------ --
CREATE OR REPLACE VIEW vw_contagem_tabelas AS
SELECT
    LEFT(table_name, 2) AS prefixo,
    count(*)            AS total_tabelas
FROM information_schema.tables
WHERE table_schema = 'public'
GROUP BY 1
ORDER BY 1;

COMMENT ON VIEW vw_contagem_tabelas IS
    'Contagem de tabelas para auditoria do schema (prefixos 00-26).';