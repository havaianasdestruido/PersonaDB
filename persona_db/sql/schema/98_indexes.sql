-- ============================================================================
-- PersonaDB - 98_indexes.sql (Índices, particionamento e estatísticas)
-- ----------------------------------------------------------------------------
-- TASK-023. Deve ser executado após os DDL (00-26) e antes de carregar dados.
--   * partições de transacao (por ano) e exame_resultado (por hash)
--   * índices BTREE compostos para consultas frequentes
--   * índice GIN trigram em nomes (complementa 00_hub.sql)
--   * estatísticas customizadas (SET STATISTICS) em colunas pesadas
--   * CLUSTER recomendado (comentado; requer carga prévia)
-- ============================================================================

-- ------------------------------------------------------------------ --
-- 1. PARTIÇÕES CONCRETAS
-- ------------------------------------------------------------------ --

-- 1.1 transacao — por ano (cobertura 2015..2031)
DO $$
DECLARE
    y INTEGER;
    part TEXT;
BEGIN
    FOR y IN 2015 .. 2031 LOOP
        part := format('transacao_%s', y);
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF transacao '
            'FOR VALUES FROM (%L) TO (%L)',
            part,
            make_date(y, 1, 1),
            make_date(y + 1, 1, 1));
        EXECUTE format(
            'CREATE INDEX IF NOT EXISTS %I ON %I (conta_id, data)',
            format('idx_%s_conta_data', part), part);
    END LOOP;
    -- partição de fallback para datas fora do intervalo
    EXECUTE 'CREATE TABLE IF NOT EXISTS transacao_transicao PARTITION OF transacao DEFAULT';
END
$$;
COMMENT ON TABLE transacao IS 'Transações financeiras fictícias (particionadas por ano).';

-- 1.2 exame_resultado — por hash da chave exame_id (4 partições)
CREATE TABLE IF NOT EXISTS exame_resultado_0 PARTITION OF exame_resultado
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE IF NOT EXISTS exame_resultado_1 PARTITION OF exame_resultado
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE IF NOT EXISTS exame_resultado_2 PARTITION OF exame_resultado
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE IF NOT EXISTS exame_resultado_3 PARTITION OF exame_resultado
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
CREATE INDEX IF NOT EXISTS idx_exame_resultado_exame ON exame_resultado (exame_id);
COMMENT ON TABLE exame_resultado IS 'Resultado de parâmetros de exames (particionada por hash).';

-- ------------------------------------------------------------------ --
-- 2. ÍNDICES BTREE COMPOSTOS (consultas frequentes)
-- ------------------------------------------------------------------ --

-- Pessoa + características
CREATE INDEX IF NOT EXISTS idx_pessoa_fisica_altura ON pessoa_caracteristica_fisica (altura);
CREATE INDEX IF NOT EXISTS idx_pessoa_fisica_olhos  ON pessoa_caracteristica_fisica (cor_olhos);

-- Genealogia
CREATE INDEX IF NOT EXISTS idx_parentesco_a    ON parentesco (pessoa_id_a, tipo_parentesco);
CREATE INDEX IF NOT EXISTS idx_parentesco_b    ON parentesco (pessoa_id_b, tipo_parentesco);
CREATE INDEX IF NOT EXISTS idx_membro_familia  ON membro_familia (familia_id);

-- Carreira
CREATE INDEX IF NOT EXISTS idx_contrato_pessoa ON contrato_trabalho (pessoa_id, cargo_id);
CREATE INDEX IF NOT EXISTS idx_contrato_data   ON contrato_trabalho (data_inicio, data_fim);
CREATE INDEX IF NOT EXISTS idx_historico_emp   ON historico_emprego (pessoa_id, inicio);

-- Finanças
CREATE INDEX IF NOT EXISTS idx_conta_pessoa    ON conta_bancaria (pessoa_id, banco_id);
CREATE INDEX IF NOT EXISTS idx_cartao_conta    ON cartao_credito (conta_id);
CREATE INDEX IF NOT EXISTS idx_imovel_pessoa   ON imovel (proprietario_pessoa_id);
CREATE INDEX IF NOT EXISTS idx_veiculo_pessoa  ON veiculo (proprietario_pessoa_id);

-- Residência
CREATE INDEX IF NOT EXISTS idx_residencia_end  ON residencia (endereco_id);
CREATE INDEX IF NOT EXISTS idx_hist_resid_pess ON historico_residencia (pessoa_id, data_entrada, data_saida);
CREATE INDEX IF NOT EXISTS idx_vizinho_ab     ON vizinho (pessoa_id_a, pessoa_id_b);

-- Saúde
CREATE INDEX IF NOT EXISTS idx_doenca_pessoa_pess ON doenca_pessoa (pessoa_id, status);
CREATE INDEX IF NOT EXISTS idx_prescricao_pess    ON prescricao (pessoa_id);
CREATE INDEX IF NOT EXISTS idx_vacina_pessoa      ON vacina_dose (pessoa_id, data);

-- Educação
CREATE INDEX IF NOT EXISTS idx_matricula_pessoa   ON matricula (pessoa_id, status);
CREATE INDEX IF NOT EXISTS idx_nota_pessoa        ON nota (pessoa_id, disciplina_id);

-- Relacionamentos
CREATE INDEX IF NOT EXISTS idx_relacionamento_ab  ON relacionamento (pessoa_id_a, pessoa_id_b);
CREATE INDEX IF NOT EXISTS idx_casamento_ab       ON casamento (pessoa_id_a, pessoa_id_b);

-- Rede social / eventos
CREATE INDEX IF NOT EXISTS idx_amizade_a          ON amizade (pessoa_id_a, data_inicio);
CREATE INDEX IF NOT EXISTS idx_evento_data        ON evento_social (data);

-- Digital
CREATE INDEX IF NOT EXISTS idx_dispositivo_pessoa ON dispositivo (pessoa_id);
CREATE INDEX IF NOT EXISTS idx_conta_digital_pess ON conta_digital (pessoa_id);

-- Jurídico
CREATE INDEX IF NOT EXISTS idx_processo_pessoa    ON pessoa_processo (pessoa_id);
CREATE INDEX IF NOT EXISTS idx_processo_status    ON processo (status, tribunal_id);
CREATE INDEX IF NOT EXISTS idx_ocorrencia_pessoa  ON ocorrencia_policial (pessoa_id, data);

-- Eleitoral
CREATE INDEX IF NOT EXISTS idx_voto_pessoa        ON voto (pessoa_id, eleicao_id);
CREATE INDEX IF NOT EXISTS idx_candidato_eleicao  ON candidato (eleicao_id, partido_id);

-- Viagens
CREATE INDEX IF NOT EXISTS idx_viagem_pessoa      ON viagem (pessoa_id, data_ida);
CREATE INDEX IF NOT EXISTS idx_hospedagem_viagem  ON hospedagem (viagem_id);

-- Pets
CREATE INDEX IF NOT EXISTS idx_pet_dono           ON pet (pessoa_id_dono);
CREATE INDEX IF NOT EXISTS idx_consulta_pet       ON consulta_veterinaria (pet_id, data);

-- Consumo
CREATE INDEX IF NOT EXISTS idx_compra_pessoa      ON compra (pessoa_id, data);
CREATE INDEX IF NOT EXISTS idx_item_compra        ON item_compra (compra_id);

-- Timeline
CREATE INDEX IF NOT EXISTS idx_evento_vida_pessoa ON evento_vida (pessoa_id, data);
CREATE INDEX IF NOT EXISTS idx_aniversario_pessoa ON aniversario (pessoa_id, data);

-- Comportamento
CREATE INDEX IF NOT EXISTS idx_habito_pessoa      ON habito (pessoa_id);
CREATE INDEX IF NOT EXISTS idx_preferencia_pessoa ON preferencia (pessoa_id, categoria);

-- Comunicação
CREATE INDEX IF NOT EXISTS idx_telefone_pessoa    ON telefone (pessoa_id);
CREATE INDEX IF NOT EXISTS idx_email_pessoa       ON email (pessoa_id);
CREATE INDEX IF NOT EXISTS idx_mensagem_par       ON mensagem_registro (pessoa_id_a, pessoa_id_b, data);

-- Mídia
CREATE INDEX IF NOT EXISTS idx_noticia_pessoa     ON noticia_ficticia (pessoa_id, data);
CREATE INDEX IF NOT EXISTS idx_reputacao_pessoa   ON reputacao_score (pessoa_id, data DESC);

-- Junções
CREATE INDEX IF NOT EXISTS idx_pessoa_habilidade  ON pessoa_habilidade (habilidade_id);
CREATE INDEX IF NOT EXISTS idx_pessoa_pet_pet     ON pessoa_pet (pet_id);
CREATE INDEX IF NOT EXISTS idx_pessoa_imovel_im   ON pessoa_imovel (imovel_id);

-- ------------------------------------------------------------------ --
-- 3. ÍNDICE GIN TRIGRAM complementar em nomes
-- ------------------------------------------------------------------ --
CREATE INDEX IF NOT EXISTS idx_empresa_nome_trgm  ON empresa
    USING GIN (nome gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_inst_ensino_trgm   ON instituicao_ensino
    USING GIN (nome gin_trgm_ops);

-- ------------------------------------------------------------------ --
-- 4. ESTATÍSTICAS CUSTOMIZADAS
-- ------------------------------------------------------------------ --
ALTER TABLE pessoa ALTER COLUMN nome_completo SET STATISTICS 500;
ALTER TABLE pessoa ALTER COLUMN cidade_nascimento SET STATISTICS 400;
ALTER TABLE transacao ALTER COLUMN descricao SET STATISTICS 300;
ALTER TABLE historico_emprego ALTER COLUMN motivo_saida SET STATISTICS 300;
ALTER TABLE empresa ALTER COLUMN ramo_atividade SET STATISTICS 300;

-- ------------------------------------------------------------------ --
-- 5. CLUSTER (recomendado após a primeira carga de dados)
--    O comando real de clustering só deve rodar quando as tabelas
--    estiverem populadas:
--      CLUSTER idx_pessoa_data_nascimento ON pessoa;
--      CLUSTER idx_contrato_pessoa ON contrato_trabalho;
-- ------------------------------------------------------------------ --
COMMENT ON SCHEMA public IS
    'PersonaDB: 25 domínios ~256 tabelas de personas sintéticas. Consulte sql/schema/99_functions.sql para views/funções.';