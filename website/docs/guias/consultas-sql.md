---
title: Consultas SQL úteis
sidebar_label: Consultas SQL
sidebar_position: 2
description: Receitas de consulta sobre o dataset carregado no PostgreSQL.
---

# Consultas SQL úteis

Todas as consultas assumem o schema aplicado (`make -C persona_db migrate`) e o dataset carregado
(`bulk_insert`).

## Perfil consolidado de uma persona

```sql
SELECT
    p.id,
    p.nome_completo,
    p.data_nascimento,
    p.classe_social,
    p.estado_civil,
    ps.valor_total_estimado AS patrimonio_liquido,
    rs.valor_score          AS score_reputacao
FROM pessoa p
-- patrimonio_snapshot e reputacao_score são séries temporais (várias linhas por
-- pessoa): o LATERAL pega só a mais recente e evita duplicar a pessoa.
LEFT JOIN LATERAL (
    SELECT valor_total_estimado
    FROM patrimonio_snapshot
    WHERE pessoa_id = p.id
    ORDER BY data DESC NULLS LAST
    LIMIT 1
) ps ON TRUE
LEFT JOIN LATERAL (
    SELECT valor_score
    FROM reputacao_score
    WHERE pessoa_id = p.id
    ORDER BY data DESC NULLS LAST
    LIMIT 1
) rs ON TRUE
ORDER BY ps.valor_total_estimado DESC NULLS LAST
LIMIT 20;
```

## Árvore genealógica recursiva

```sql
WITH RECURSIVE linhagem AS (
    SELECT p.id AS pessoa_id, p.nome_completo,
           ag.pessoa_id_pai, ag.pessoa_id_mae, 0 AS nivel
    FROM pessoa p
    LEFT JOIN arvore_genealogica ag ON ag.pessoa_id = p.id
    WHERE p.id = :pessoa_alvo_id

    UNION ALL

    SELECT parente.id, parente.nome_completo,
           ag_par.pessoa_id_pai, ag_par.pessoa_id_mae, l.nivel + 1
    FROM linhagem l
    JOIN pessoa parente ON parente.id IN (l.pessoa_id_pai, l.pessoa_id_mae)
    LEFT JOIN arvore_genealogica ag_par ON ag_par.pessoa_id = parente.id
    WHERE l.nivel < 5
)
SELECT * FROM linhagem ORDER BY nivel;
```

## Linha do tempo de uma pessoa

```sql
SELECT ldt.ordem_cronologica, ev.data, ev.tipo_evento, ev.descricao, mhp.importancia
FROM linha_do_tempo ldt
JOIN evento_vida ev ON ev.id = ldt.evento_vida_id
LEFT JOIN marco_historico_pessoal mhp ON mhp.evento_vida_id = ev.id
WHERE ldt.pessoa_id = :pessoa_alvo_id
ORDER BY ldt.ordem_cronologica;
```

## Distribuição por classe social e escolaridade

```sql
SELECT p.classe_social,
       COUNT(*)                                        AS pessoas,
       ROUND(AVG(EXTRACT(YEAR FROM age(p.data_nascimento)))::numeric, 1) AS idade_media,
       -- EXISTS em vez de JOIN: quem tem dois diplomas não é contado duas vezes
       COUNT(*) FILTER (
           WHERE EXISTS (SELECT 1 FROM diploma d WHERE d.pessoa_id = p.id)
       )                                               AS com_diploma
FROM pessoa p
GROUP BY p.classe_social
ORDER BY p.classe_social;
```

## Renda mensal por setor

```sql
SELECT e.setor,
       COUNT(DISTINCT ct.pessoa_id) AS trabalhadores,
       ROUND(AVG(s.valor)::numeric, 2) AS salario_medio,
       ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY s.valor)::numeric, 2) AS mediana
FROM contrato_trabalho ct
JOIN empresa e ON e.id = ct.empresa_id
JOIN salario s ON s.contrato_id = ct.id
GROUP BY e.setor
ORDER BY salario_medio DESC;
```

## Coerência genética (auditoria)

```sql
SELECT f.id AS filho, f.tipo_sanguineo AS tipo_filho,
       pai.tipo_sanguineo AS tipo_pai, mae.tipo_sanguineo AS tipo_mae
FROM pessoa f
JOIN pessoa pai ON pai.id = f.pai_id
JOIN pessoa mae ON mae.id = f.mae_id
WHERE NOT validar_tipo_sanguineo_filho(pai.tipo_sanguineo, mae.tipo_sanguineo, f.tipo_sanguineo);
-- deve retornar zero linhas
```

A função `validar_tipo_sanguineo_filho` é definida em `99_functions.sql` e replica, no banco, a
regra do [motor genético](../motores/genetics.md).

## Views prontas

| View | Conteúdo |
|---|---|
| `v_pessoa_completa` | hub com os atributos mais consultados já desnormalizados |
| `v_perfil_criminal` | consolidação de processos, sentenças e antecedentes |
| `v_arvore_familiar` | relações de parentesco em formato plano |
| `mv_estatisticas_populacao` | materializada; use `REFRESH MATERIALIZED VIEW` após carregar |

```sql
SELECT * FROM v_pessoa_completa LIMIT 10;
REFRESH MATERIALIZED VIEW mv_estatisticas_populacao;
SELECT * FROM mv_estatisticas_populacao;
```

## Particionamento de `transacao`

`98_indexes.sql` cria partições anuais de 2015 a 2031. Consultas com filtro de data aproveitam o
*partition pruning*:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT pessoa_id, SUM(valor)
FROM transacao
WHERE data BETWEEN DATE '2023-01-01' AND DATE '2023-12-31'
GROUP BY pessoa_id;
```

## Idade na data corrente

```sql
SELECT nome_completo, calcular_idade(data_nascimento) AS idade
FROM pessoa
WHERE esta_vivo
ORDER BY idade DESC
LIMIT 10;
```

:::note `calcular_idade` usa `CURRENT_DATE`
Diferente dos geradores (ancorados em `PERSONADB_TODAY`), essa função SQL usa a data real do
servidor. Para comparações reprodutíveis, calcule a idade em relação à âncora:
`date_part('year', age(DATE '2026-01-01', data_nascimento))`.
:::
