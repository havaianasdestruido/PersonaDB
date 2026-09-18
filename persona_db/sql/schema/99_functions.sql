-- ============================================================================
-- PersonaDB - 99_functions.sql (Functions, Triggers & Views)
-- ----------------------------------------------------------------------------
-- TASK-022. Idempotente. Deve ser executado após todos os DDL (00-26).
--   * calcular_idade(data_nascimento) -> integer
--   * validar_tipo_sanguineo_filho(tipo_pai, tipo_mae, tipo_filho) -> boolean
--   * trigger: auto-criar semente_aleatoria ao inserir em pessoa
--   * trigger: atualizar reputacao_score ao inserir antecedente_criminal
--   * trigger genérico: registrar alterações em log_alteracao
--   * views: v_pessoa_completa, v_perfil_criminal, v_arvore_familiar
--   * materialized view: mv_estatisticas_populacao
-- ============================================================================

-- ------------------------------------------------------------------ --
-- 1. FUNÇÕES UTILITÁRIAS
-- ------------------------------------------------------------------ --

CREATE OR REPLACE FUNCTION calcular_idade(data_nascimento DATE)
RETURNS INTEGER
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT date_part('year', age(CURRENT_DATE, data_nascimento))::integer
$$;
COMMENT ON FUNCTION calcular_idade(DATE) IS
    'Idade completa em anos na data corrente.';

-- Valida se o tipo sanguíneo (ABO) do filho é compatível com os pais
-- (tabela de herança ABO padrão).
CREATE OR REPLACE FUNCTION validar_tipo_sanguineo_filho(
    tipo_pai  TEXT,
    tipo_mae  TEXT,
    tipo_filho TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    validos TEXT[] := ARRAY['A','B','AB','O'];
BEGIN
    IF tipo_pai NOT IN (SELECT unnest(validos)) OR
       tipo_mae NOT IN (SELECT unnest(validos)) OR
       tipo_filho NOT IN (SELECT unnest(validos)) THEN
        RETURN FALSE;
    END IF;

    IF tipo_pai = 'O' THEN
        IF tipo_mae = 'O' THEN
            RETURN tipo_filho IN ('O');
        ELSIF tipo_mae = 'A' THEN
            RETURN tipo_filho IN ('A','O');
        ELSIF tipo_mae = 'B' THEN
            RETURN tipo_filho IN ('B','O');
        ELSE -- mae AB
            RETURN tipo_filho IN ('A','B');
        END IF;
    ELSIF tipo_pai = 'A' THEN
        IF tipo_mae = 'O' THEN
            RETURN tipo_filho IN ('A','O');
        ELSIF tipo_mae = 'A' THEN
            RETURN tipo_filho IN ('A','O');
        ELSIF tipo_mae = 'B' THEN
            RETURN tipo_filho IN ('A','B','AB','O');
        ELSE -- mae AB
            RETURN tipo_filho IN ('A','B','AB');
        END IF;
    ELSIF tipo_pai = 'B' THEN
        IF tipo_mae = 'O' THEN
            RETURN tipo_filho IN ('B','O');
        ELSIF tipo_mae = 'A' THEN
            RETURN tipo_filho IN ('A','B','AB','O');
        ELSIF tipo_mae = 'B' THEN
            RETURN tipo_filho IN ('B','O');
        ELSE -- mae AB
            RETURN tipo_filho IN ('A','B','AB');
        END IF;
    ELSE -- pai AB
        IF tipo_mae = 'O' THEN
            RETURN tipo_filho IN ('A','B');
        ELSIF tipo_mae = 'A' THEN
            RETURN tipo_filho IN ('A','B','AB');
        ELSIF tipo_mae = 'B' THEN
            RETURN tipo_filho IN ('A','B','AB');
        ELSE -- mae AB
            RETURN tipo_filho IN ('A','B','AB');
        END IF;
    END IF;
END
$$;
COMMENT ON FUNCTION validar_tipo_sanguineo_filho(TEXT, TEXT, TEXT) IS
    'Compatibilidade ABO de filho dado os tipos dos pais (herança mendeliana).';

-- ------------------------------------------------------------------ --
-- 2. TRIGGERS
-- ------------------------------------------------------------------ --

-- 2.1 Ao inserir em pessoa, cria o seed determinístico em semente_aleatoria.
CREATE OR REPLACE FUNCTION trg_fn_criar_semente_aleatoria()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO semente_aleatoria (pessoa_id, seed_valor)
    VALUES (NEW.id, md5(NEW.id::text || ':' || COALESCE(NEW.nome_completo, '')))
    ON CONFLICT DO NOTHING;
    RETURN NEW;
END
$$;

DROP TRIGGER IF EXISTS trg_pessoa_criar_semente ON pessoa;

CREATE TRIGGER trg_pessoa_criar_semente
    AFTER INSERT ON pessoa
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_criar_semente_aleatoria();

-- 2.2 Ao inserir antecedente_criminal, recalcula/registra reputacao_score.
CREATE OR REPLACE FUNCTION trg_fn_reputacao_antecedente()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_score NUMERIC(5,2);
BEGIN
    SELECT 100.0
         - 25.0 * COUNT(*) FILTER (WHERE status = 'ativo')
         - 8.0  * COUNT(*) FILTER (WHERE status = 'arquivado')
    INTO v_score
    FROM antecedente_criminal
    WHERE pessoa_id = NEW.pessoa_id;

    IF v_score IS NULL THEN
        v_score := 100.0;
    END IF;

    INSERT INTO reputacao_score (pessoa_id, data, valor_score)
    VALUES (NEW.pessoa_id, CURRENT_DATE, GREATEST(0.0, LEAST(100.0, v_score)))
    ON CONFLICT DO NOTHING;

    RETURN NEW;
END
$$;

DROP TRIGGER IF EXISTS trg_antecedente_reputacao ON antecedente_criminal;

CREATE TRIGGER trg_antecedente_reputacao
    AFTER INSERT ON antecedente_criminal
    FOR EACH ROW
    EXECUTE FUNCTION trg_fn_reputacao_antecedente();

-- 2.3 Trigger genérico de auditoria: registra UPDATE/DELETE em log_alteracao.
CREATE OR REPLACE FUNCTION trg_fn_log_alteracao()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    cols TEXT[];
    col  TEXT;
BEGIN
    SELECT array_agg(column_name) INTO cols
    FROM information_schema.columns
    WHERE table_schema = TG_TABLE_SCHEMA
      AND table_name   = TG_TABLE_NAME;

    IF TG_OP = 'UPDATE' THEN
        FOREACH col IN ARRAY cols LOOP
            BEGIN
                IF coalesce(row_to_json(NEW)::jsonb ->> col, '')
                   <> coalesce(row_to_json(OLD)::jsonb ->> col, '') THEN
                    INSERT INTO log_alteracao (tabela, registro_id, campo_alterado,
                                               valor_antigo, valor_novo)
                    VALUES (TG_TABLE_NAME, NEW.id,
                            col,
                            row_to_json(OLD)::jsonb ->> col,
                            row_to_json(NEW)::jsonb ->> col);
                END IF;
            EXCEPTION WHEN OTHERS THEN
                NULL;  -- coluna não aplicável ao registro (timezone etc.) — ignora
            END;
        END LOOP;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO log_alteracao (tabela, registro_id, campo_alterado,
                                   valor_antigo, valor_novo, data)
        VALUES (TG_TABLE_NAME, OLD.id, '*', 'row deleted', NULL, now());
    END IF;
    RETURN NULL;
END
$$;

-- Aplicar o trigger genérico às tabelas mais relevantes.
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY['pessoa_caracteristica_fisica',
                             'pessoa_documento',
                             'fatura',
                             'contrato_trabalho'] LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS trg_gen_log ON %I', t);
        EXECUTE format(
            'CREATE TRIGGER trg_gen_log AFTER UPDATE OR DELETE ON %I '
            'FOR EACH ROW EXECUTE FUNCTION trg_fn_log_alteracao()', t);
    END LOOP;
END
$$;

-- ------------------------------------------------------------------ --
-- 3. VIEWS
-- ------------------------------------------------------------------ --

-- 3.1 v_pessoa_completa — join das tabelas comuns.
CREATE OR REPLACE VIEW v_pessoa_completa AS
SELECT
    p.id                        AS pessoa_id,
    p.nome_completo,
    p.data_nascimento,
    calcular_idade(p.data_nascimento) AS idade,
    p.sexo::text                AS sexo,
    p.nacionalidade::text       AS nacionalidade,
    p.estado_civil::text        AS estado_civil,
    p.classe_social,
    f.cor_olhos,
    f.cor_cabelo,
    f.mao_dominante,
    f.altura,
    f.peso,
    f.tipo_sanguineo,
    f.fator_rh,
    d.tipo                     AS documento_tipo,
    d.numero_ficticio          AS documento_numero,
    c.cidade_ficticia          AS cidade_residencia,
    c.uf                       AS uf_residencia,
    h.historico_empregos
FROM pessoa p
LEFT JOIN pessoa_caracteristica_fisica f  ON f.pessoa_id = p.id
LEFT JOIN pessoa_documento d              ON d.pessoa_id = p.id
LEFT JOIN residencia r                    ON r.pessoa_id = p.id
LEFT JOIN endereco c                      ON c.id = r.endereco_id
LEFT JOIN LATERAL (
    SELECT count(*)::int AS historico_empregos
    FROM historico_emprego he
    WHERE he.pessoa_id = p.id
) h ON TRUE;
COMMENT ON VIEW v_pessoa_completa IS
    'Perfil consolidado da persona para consulta rápida.';

-- 3.2 v_perfil_criminal — pessoa + processos + antecedentes + reputação.
CREATE OR REPLACE VIEW v_perfil_criminal AS
SELECT
    p.id                    AS pessoa_id,
    p.nome_completo,
    calcular_idade(p.data_nascimento) AS idade,
    p.classe_social,
    count(DISTINCT a.id)    AS total_antecedentes,
    count(*) FILTER (WHERE a.status = 'ativo')::int  AS antecedentes_ativos,
    count(DISTINCT pr.id)   AS total_processos,
    rs.valor_score           AS reputacao_atual
FROM pessoa p
LEFT JOIN antecedente_criminal a   ON a.pessoa_id = p.id
LEFT JOIN pessoa_processo pp       ON pp.pessoa_id = p.id
LEFT JOIN processo pr              ON pr.id = pp.processo_id
LEFT JOIN LATERAL (
    SELECT valor_score
    FROM reputacao_score rs
    WHERE rs.pessoa_id = p.id
    ORDER BY rs.data DESC
    LIMIT 1
) rs ON TRUE
GROUP BY p.id, p.nome_completo, p.data_nascimento, p.classe_social, rs.valor_score;
COMMENT ON VIEW v_perfil_criminal IS
    'Resumo criminal da persona alimentado por engines/ e trigonometria de reputação.';

-- 3.3 v_arvore_familiar — CTE recursiva sobre parentesco.
CREATE OR REPLACE VIEW v_arvore_familiar AS
WITH RECURSIVE arvore AS (
    SELECT
        id                               AS raiz_pessoa_id,
        id                               AS pessoa_id,
        nome_completo,
        0::int                           AS profundidade,
        'self'::text                     AS relacao,
        ARRAY[id]                        AS caminho
    FROM pessoa

    UNION ALL

    SELECT
        a.raiz_pessoa_id,
        p2.id,
        p2.nome_completo,
        a.profundidade + 1,
        pa.tipo_parentesco,
        a.caminho || p2.id
    FROM arvore a
    JOIN parentesco pa
      ON (pa.pessoa_id_a = a.pessoa_id AND pa.pessoa_id_b <> ALL (a.caminho))
    JOIN pessoa p2 ON p2.id = pa.pessoa_id_b
    WHERE a.profundidade < 6
)
SELECT DISTINCT
    raiz_pessoa_id,
    pessoa_id,
    nome_completo,
    profundidade,
    relacao
FROM arvore;
COMMENT ON VIEW v_arvore_familiar IS
    'Árvore familiar via CTE recursiva limitada a 6 níveis (guarda contra ciclos).';

-- ------------------------------------------------------------------ --
-- 4. MATERIALIZED VIEW
-- ------------------------------------------------------------------ --

DROP MATERIALIZED VIEW IF EXISTS mv_estatisticas_populacao;

CREATE MATERIALIZED VIEW mv_estatisticas_populacao AS
SELECT
    COUNT(*)                                            AS total_pessoas,
    COUNT(*) FILTER (WHERE sexo = 'feminino')::int      AS total_feminino,
    COUNT(*) FILTER (WHERE sexo = 'masculino')::int     AS total_masculino,
    ROUND(AVG(EXTRACT(EPOCH FROM (CURRENT_DATE - p.data_nascimento)) / 365.2425), 2)
                                                        AS idade_media,
    ROUND(SUM(intervalo_renda_salarial.valor_medio), 2) AS soma_salarios_medio,
    COUNT(*) FILTER (WHERE classe_social IN ('A','B1','B2'))::int AS classe_ab
FROM pessoa p
LEFT JOIN LATERAL (
    SELECT AVG(s.valor) AS valor_medio
    FROM salario s
    JOIN contrato_trabalho ct ON ct.id = s.contrato_id
    WHERE ct.pessoa_id = p.id
) intervalo_renda_salarial ON TRUE;

CREATE UNIQUE INDEX IF NOT EXISTS uq_mv_estatisticas ON mv_estatisticas_populacao ((1));

COMMENT ON MATERIALIZED VIEW mv_estatisticas_populacao IS
    'Estatísticas agregadas da população gerada (refresh manual ou por job).';