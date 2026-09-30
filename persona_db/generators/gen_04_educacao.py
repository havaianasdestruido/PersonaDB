"""gen_04_educacao — domínio 04: trajetória educacional, notas, bolsas e estágios.

Implementa TASK-044 de TODO.MD:
- Determina o nível máximo de escolaridade integrando escolaridade parental,
  classe socioeconômica e impactos de saúde (`SocioeconomicEngine`).
- Simula matrículas sequenciais (`fundamental` -> `medio` -> `superior` -> `pos`)
  garantindo que o ensino superior ocorra somente após a conclusão do ensino médio.
- Gera notas correlacionadas com variável latente de desempenho, saúde mental
  (-15% se transtorno mental) e trabalho paralelo (-8%).
- Modela frequência escolar com penalidade `Beta(2,5) * 30%` e aumento de
  abandono escolar (+25%) em caso de doença grave.
- Gera bolsas de estudo, certificados, diplomas, reprovações, estágios e
  empréstimos de biblioteca.
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from typing import Any
from uuid import NAMESPACE_URL, uuid5

try:  # pragma: no cover
    from persona_db.engines.rng import new_rng
    from persona_db.engines.socio import SocioeconomicEngine
    from persona_db.generators.gen_00_pessoa import simulation_today
    from persona_db.seeds.lookup_data import CURSOS, EMPRESAS, UNIVERSIDADES
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.rng import new_rng
    from persona_db.engines.socio import SocioeconomicEngine
    from persona_db.generators.gen_00_pessoa import simulation_today
    from persona_db.seeds.lookup_data import CURSOS, EMPRESAS, UNIVERSIDADES

# ---------------------------------------------------------------------------
# Constantes nomeadas de calibração (TASK-044)
# ---------------------------------------------------------------------------
MENTAL_HEALTH_GRADE_PENALTY = 0.85   # -15% nas notas se transtorno mental
PARALLEL_WORK_GRADE_PENALTY = 0.92   # -8% nas notas se trabalha em paralelo
SEVERE_DISEASE_DROPOUT_BOOST = 0.25  # +0.25 em P(abandono) se doença grave
SEVERE_DISEASE_ATTENDANCE_MAX_DROP = 30.0
INTERNSHIP_PROB_SUPERIOR = 0.65
PASSING_GRADE_THRESHOLD = 6.0

_ESCOLAS_BASICAS = [
    ("Escola Estadual Fictícia Central", "escola"),
    ("Colégio Municipal Simulado", "colegio"),
    ("Escola Básica Horizonte Inventado", "escola"),
    ("Colégio Integrado Nova Era Fictício", "colegio"),
    ("Instituto Técnico Simulado Federal", "tecnico"),
]

_OBRAS_BIBLIOTECA = [
    "Fundamentos de Algoritmos Fictícios",
    "Introdução ao Direito Constitucional Simulado",
    "Anatomia Humana Aplicada (Edição Fictícia)",
    "Cálculo Diferencial e Integral Vol. I",
    "História Econômica da República Simulada",
    "Teoria Geral da Administração Moderna",
    "Engenharia de Estruturas e Materiais",
    "Psicologia do Desenvolvimento Humano",
]

_DISCIPLINAS_POR_NIVEL: dict[str, list[tuple[str, int]]] = {
    "fundamental": [
        ("Língua Portuguesa Fundamental", 160),
        ("Matemática Básica", 160),
        ("Ciências da Natureza", 80),
        ("História e Geografia", 80),
    ],
    "medio": [
        ("Literatura e Redação", 120),
        ("Matemática do Ensino Médio", 120),
        ("Física e Química", 100),
        ("Biologia e Sociologia", 100),
    ],
    "superior": [
        ("Metodologia Científica", 60),
        ("Fundamentos Teóricos do Curso", 90),
        ("Prática Profissional Supervisionada", 120),
        ("Projeto Integrador Avançado", 90),
    ],
    "pos": [
        ("Seminários Avançados de Pesquisa", 60),
        ("Tópicos Especiais de Pós-Graduação", 60),
        ("Elaboração de Dissertação/Monografia", 120),
    ],
}

_INCOME_STD_BY_CLASS: dict[str, float] = {
    "A": 2.0, "B1": 1.2, "B2": 0.5, "C1": 0.0, "C2": -0.5, "D_E": -1.1,
}


def empresa_uuid(cnpj: str) -> str:
    """Retorna o UUID determinístico de uma empresa a partir do seu CNPJ fictício."""
    return str(uuid5(NAMESPACE_URL, f"empresa-{cnpj}"))


def _birth(p: dict[str, Any]) -> date:
    return date.fromisoformat(p["data_nascimento"])


def _end_date(p: dict[str, Any], today: date) -> date:
    if p.get("data_obito"):
        return min(today, date.fromisoformat(p["data_obito"]))
    return today


def _build_catalogs(
    rows: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    """Popula `instituicao_ensino`, `curso`, `disciplina`, `professor` e `turma`."""
    escolas: list[dict[str, Any]] = []
    universidades: list[dict[str, Any]] = []

    for nome, tipo in _ESCOLAS_BASICAS:
        inst_id = str(uuid5(NAMESPACE_URL, f"inst-basica-{nome}"))
        rec = {"id": inst_id, "nome": nome, "tipo": tipo, "endereco_id": None}
        rows["instituicao_ensino"].append(rec)
        escolas.append(rec)

    for u in UNIVERSIDADES[:25]:
        inst_id = str(uuid5(NAMESPACE_URL, f"inst-univ-{u['name']}"))
        tipo = "universidade" if "Universidade" in u["name"] or u["type"] == "publica" else "faculdade"
        rec = {"id": inst_id, "nome": u["name"], "tipo": tipo, "endereco_id": None}
        rows["instituicao_ensino"].append(rec)
        universidades.append(rec)

    cursos_by_nivel: dict[str, list[dict[str, Any]]] = {
        "fundamental": [], "medio": [], "superior": [], "pos": [],
    }
    disc_by_curso: dict[str, list[dict[str, Any]]] = {}

    base_cursos = [
        ("Ensino Fundamental Completo", "fundamental", 9),
        ("Ensino Médio Regular", "medio", 3),
    ]
    for nome, nivel, dur in base_cursos:
        cid = str(uuid5(NAMESPACE_URL, f"curso-{nivel}-{nome}"))
        crec = {"id": cid, "nome": nome, "nivel": nivel, "duracao_anos": dur}
        rows["curso"].append(crec)
        cursos_by_nivel[nivel].append(crec)

    for c in CURSOS:
        modalidade = c["modalidade"]
        if modalidade in ("bacharelado", "licenciatura", "tecnologo"):
            nivel = "superior"
        else:
            nivel = "pos"
        dur_anos = max(1, round(int(c["duracao_meses"]) / 12))
        cid = str(uuid5(NAMESPACE_URL, f"curso-{nivel}-{c['curso']}"))
        crec = {"id": cid, "nome": c["curso"], "nivel": nivel, "duracao_anos": dur_anos}
        rows["curso"].append(crec)
        cursos_by_nivel[nivel].append(crec)

    # Professores e disciplinas/turmas
    all_insts = escolas + universidades
    prof_ids: list[str] = []
    for idx, inst in enumerate(all_insts):
        pid = str(uuid5(NAMESPACE_URL, f"prof-{inst['id']}-0"))
        rows["professor"].append({
            "id": pid,
            "nome": f"Prof(a). Acadêmico {idx + 1:02d}",
            "instituicao_id": inst["id"],
            "especialidade": "Docência e Pesquisa",
        })
        prof_ids.append(pid)

    for nivel, clist in cursos_by_nivel.items():
        templates = _DISCIPLINAS_POR_NIVEL[nivel]
        for c_idx, crec in enumerate(clist):
            cid = crec["id"]
            disc_by_curso[cid] = []
            for d_idx, (dnome, ch) in enumerate(templates):
                did = str(uuid5(NAMESPACE_URL, f"disc-{cid}-{d_idx}"))
                drec = {
                    "id": did,
                    "nome": f"{dnome} ({crec['nome'][:24]})",
                    "curso_id": cid,
                    "carga_horaria": ch,
                }
                rows["disciplina"].append(drec)
                disc_by_curso[cid].append(drec)

                prof_id = prof_ids[(c_idx + d_idx) % len(prof_ids)]
                rows["turma"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"turma-{did}")),
                    "disciplina_id": did,
                    "professor_id": prof_id,
                    "periodo": "2024.1",
                })

    return escolas, universidades, cursos_by_nivel, disc_by_curso


def generate(
    personas: list[dict[str, Any]],
    seed: int = 7,
    today: date | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Gera todas as tabelas do domínio 04 (Educação) em ordem cronológica."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "instituicao_ensino": [],
        "curso": [],
        "disciplina": [],
        "professor": [],
        "turma": [],
        "matricula": [],
        "nota": [],
        "frequencia_escolar": [],
        "bolsa_estudo": [],
        "certificado": [],
        "diploma": [],
        "reprovacao": [],
        "estagio": [],
        "biblioteca_emprestimo": [],
    }

    escolas, universidades, cursos_by_nivel, disc_by_curso = _build_catalogs(rows)
    by_id = {p["id"]: p for p in personas}
    ordered = sorted(personas, key=lambda p: (p.get("geracao", 0), p["idx"]))

    for p in ordered:
        rng = master.fork(p["id"], "gen04-educacao")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)

        # Escolaridade parental
        pai = by_id.get(p.get("pai_id")) if p.get("pai_id") else None
        mae = by_id.get(p.get("mae_id")) if p.get("mae_id") else None
        parent_edu = None
        edu_order = ("fundamental", "medio", "superior", "pos")
        for par in (pai, mae):
            if (
                par
                and par.get("education") in edu_order
                and (parent_edu is None or edu_order.index(par["education"]) > edu_order.index(parent_edu))
            ):
                parent_edu = par["education"]

        if age < 6:
            p["education"] = "fundamental"
            p["abandono_escolar"] = False
            continue

        inc_std = _INCOME_STD_BY_CLASS.get(p["classe_social"], 0.0)
        target_edu = SocioeconomicEngine.education_level(rng, parent_edu, inc_std, p["classe_social"])
        if age < 15:
            target_edu = "fundamental"
        elif age < 18 and target_edu in ("superior", "pos"):
            target_edu = "medio"
        elif age < 23 and target_edu == "pos":
            target_edu = "superior"

        # Inteligência latente e modificadores de saúde/trabalho
        latent_ability = rng.normal_clipped(7.2, 1.2, 3.5, 9.8)
        grade_mult = 1.0
        if p.get("tem_transtorno_mental"):
            grade_mult *= MENTAL_HEALTH_GRADE_PENALTY
        works_parallel = p["classe_social"] in ("C2", "D_E") and rng.bernoulli(0.45)
        if works_parallel:
            grade_mult *= PARALLEL_WORK_GRADE_PENALTY

        has_severe_health = bool(p.get("tem_doenca_grave"))
        dropout_prob = 0.04 + (SEVERE_DISEASE_DROPOUT_BOOST if has_severe_health else 0.0)
        if p["classe_social"] == "D_E":
            dropout_prob += 0.06

        # Sequência cronológica de níveis cursados
        stages = ["fundamental"]
        if target_edu in ("medio", "superior", "pos") and age >= 15:
            stages.append("medio")
        if target_edu in ("superior", "pos") and age >= 18:
            stages.append("superior")
        if target_edu == "pos" and age >= 23:
            stages.append("pos")

        abandoned = False
        attained = "fundamental"
        prev_end_date = born + timedelta(days=6 * 365)

        for stage in stages:
            if abandoned:
                break
            if stage == "fundamental":
                inst = rng.choice(escolas)
                curso = cursos_by_nivel["fundamental"][0]
                dt_ini = max(born + timedelta(days=6 * 365), prev_end_date)
                dur_days = 8 * 365
            elif stage == "medio":
                inst = rng.choice(escolas)
                curso = cursos_by_nivel["medio"][0]
                dt_ini = max(born + timedelta(days=14 * 365 + 180), prev_end_date + timedelta(days=30))
                dur_days = 3 * 365
            elif stage == "superior":
                inst = rng.choice(universidades)
                curso = rng.choice(cursos_by_nivel["superior"])
                dt_ini = max(born + timedelta(days=18 * 365), prev_end_date + timedelta(days=30))
                dur_days = int(curso["duracao_anos"]) * 365
            else:
                inst = rng.choice(universidades)
                curso = rng.choice(cursos_by_nivel["pos"])
                dt_ini = max(born + timedelta(days=22 * 365 + 180), prev_end_date + timedelta(days=30))
                dur_days = max(365, int(curso["duracao_anos"]) * 365)

            if dt_ini >= end - timedelta(days=30):
                break

            planned_end = dt_ini + timedelta(days=dur_days)
            if stage != "fundamental" and rng.bernoulli(min(0.65, dropout_prob)):
                status = "abandonada"
                span = max(30, min(dur_days // 2, (end - dt_ini).days))
                dt_fim = dt_ini + timedelta(days=span)
                abandoned = True
            elif planned_end > end:
                status = "ativa"
                dt_fim = end
                attained = stage
                abandoned = True
            else:
                status = "concluida"
                dt_fim = planned_end
                attained = stage

            if dt_fim <= dt_ini:
                dt_fim = dt_ini + timedelta(days=30)

            mat_id = str(uuid5(NAMESPACE_URL, f"mat-{p['id']}-{stage}"))
            rows["matricula"].append({
                "id": mat_id,
                "pessoa_id": p["id"],
                "instituicao_id": inst["id"],
                "curso_id": curso["id"],
                "data_inicio": dt_ini.isoformat(),
                "data_fim": dt_fim.isoformat(),
                "status": status,
            })

            periodo_str = f"{dt_ini.year}.1"
            discs = disc_by_curso[curso["id"]][:2]
            avg_grade = 0.0
            for d_idx, disc in enumerate(discs):
                raw_grade = rng.normal_clipped(latent_ability * grade_mult, 1.1, 0.0, 10.0)
                nota_val = round(raw_grade, 2)
                avg_grade += nota_val
                rows["nota"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"nota-{mat_id}-{d_idx}")),
                    "pessoa_id": p["id"],
                    "disciplina_id": disc["id"],
                    "periodo": periodo_str,
                    "valor": nota_val,
                })

                base_pres = rng.normal_clipped(88.0, 6.0, 50.0, 100.0)
                if has_severe_health:
                    base_pres = max(25.0, base_pres - rng.beta_sample(2.0, 5.0) * SEVERE_DISEASE_ATTENDANCE_MAX_DROP)
                pres_val = round(min(100.0, max(0.0, base_pres)), 2)
                rows["frequencia_escolar"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"freq-{mat_id}-{d_idx}")),
                    "pessoa_id": p["id"],
                    "disciplina_id": disc["id"],
                    "periodo": periodo_str,
                    "percentual_presenca": pres_val,
                })

                if nota_val < PASSING_GRADE_THRESHOLD or pres_val < 75.0:
                    motivo = "nota insuficiente" if nota_val < PASSING_GRADE_THRESHOLD else "frequência insuficiente"
                    rows["reprovacao"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"reprov-{mat_id}-{d_idx}")),
                        "pessoa_id": p["id"],
                        "disciplina_id": disc["id"],
                        "periodo": periodo_str,
                        "motivo": motivo,
                    })

            avg_grade = avg_grade / max(1, len(discs))

            # Bolsas de estudo (ensino superior/pós ou colégio)
            if stage in ("superior", "pos"):
                p_bolsa = 0.45 if p["classe_social"] in ("C2", "D_E") else (0.25 if p["classe_social"] == "C1" else 0.12)
                if avg_grade >= 8.0:
                    p_bolsa += 0.20
                if rng.bernoulli(min(0.85, p_bolsa)):
                    pct_bolsa = float(rng.choice([50.0, 75.0, 100.0], weights=[0.4, 0.25, 0.35]))
                    rows["bolsa_estudo"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"bolsa-{mat_id}")),
                        "pessoa_id": p["id"],
                        "instituicao_id": inst["id"],
                        "tipo": "mérito acadêmico" if avg_grade >= 8.0 else "social ProUni fictício",
                        "percentual": pct_bolsa,
                        "periodo": periodo_str,
                    })

            # Estágio durante ensino superior (P = 0.65)
            if stage == "superior" and (dt_fim - dt_ini).days >= 120 and rng.bernoulli(INTERNSHIP_PROB_SUPERIOR):
                emp = rng.choice(EMPRESAS)
                est_ini = dt_ini + timedelta(days=30)
                est_fim = min(dt_fim, est_ini + timedelta(days=rng.integer(90, 360)))
                if est_fim > est_ini:
                    rows["estagio"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"estagio-{mat_id}")),
                        "pessoa_id": p["id"],
                        "empresa_id": empresa_uuid(emp["cnpj"]),
                        "curso_id": curso["id"],
                        "data_inicio": est_ini.isoformat(),
                        "data_fim": est_fim.isoformat(),
                    })

            # Certificados e diplomas se concluído
            if status == "concluida":
                if stage == "medio":
                    p["ensino_medio_concluido_em"] = dt_fim.isoformat()
                rows["certificado"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"cert-{mat_id}")),
                    "pessoa_id": p["id"],
                    "curso_id": curso["id"],
                    "data_emissao": dt_fim.isoformat(),
                })
                if stage in ("superior", "pos"):
                    p["ensino_superior_concluido_em"] = dt_fim.isoformat()
                    rows["diploma"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"dipl-{mat_id}")),
                        "pessoa_id": p["id"],
                        "curso_id": curso["id"],
                        "data_conclusao": dt_fim.isoformat(),
                        "instituicao_id": inst["id"],
                    })

            # Empréstimo de biblioteca
            if (dt_fim - dt_ini).days >= 20 and rng.bernoulli(0.35):
                emp_dt = dt_ini + timedelta(days=rng.integer(5, max(6, (dt_fim - dt_ini).days - 15)))
                dev_dt = min(dt_fim, emp_dt + timedelta(days=rng.integer(7, 14)))
                if dev_dt > emp_dt:
                    rows["biblioteca_emprestimo"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"bib-{mat_id}")),
                        "pessoa_id": p["id"],
                        "instituicao_id": inst["id"],
                        "titulo_obra": str(rng.choice(_OBRAS_BIBLIOTECA)),
                        "data_emprestimo": emp_dt.isoformat(),
                        "data_devolucao": dev_dt.isoformat(),
                    })

            prev_end_date = dt_fim

        p["education"] = attained
        p["abandono_escolar"] = abandoned
        p["curso_superior_nome"] = curso["nome"] if attained in ("superior", "pos") else None

    return rows
