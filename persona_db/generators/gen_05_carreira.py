"""gen_05_carreira — domínio 05: empresas, cargos, contratos, salários e carreira.

Implementa TASK-045 de TODO.MD:
- Entrada no mercado de trabalho coerente com idade e escolaridade (>= 18 anos
  para contratos CLT/PJ/público, >= 14 anos para estágio/aprendiz).
- Influência familiar no setor e na empresa (nepotismo via `SocioeconomicEngine`)
  em ordem topológica geracional.
- Salários mensais calibrados via `SocioeconomicEngine.salary` com piso no
  salário mínimo histórico vigente (`MIN_WAGE_HISTORY`).
- Holerites com descontos progressivos de INSS e IRRF, benefícios, férias,
  avaliações de desempenho, promoções, demissões, licenças médicas, sindicatos
  e rede de colegas de trabalho.
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
    from persona_db.generators.gen_04_educacao import empresa_uuid
    from persona_db.seeds.lookup_data import EMPRESAS, MIN_WAGE_HISTORY, PROFISSOES
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.rng import new_rng
    from persona_db.engines.socio import SocioeconomicEngine
    from persona_db.generators.gen_00_pessoa import simulation_today
    from persona_db.generators.gen_04_educacao import empresa_uuid
    from persona_db.seeds.lookup_data import EMPRESAS, MIN_WAGE_HISTORY, PROFISSOES

# ---------------------------------------------------------------------------
# Constantes nomeadas (TASK-045)
# ---------------------------------------------------------------------------
SAME_PARENT_SECTOR_PROB = 0.32
FAMILY_COMPANY_PROB = 0.18
MIN_WAGE_BY_YEAR: dict[int, float] = {int(r["year"]): float(r["min_wage"]) for r in MIN_WAGE_HISTORY}

_HABILIDADES_TECNICAS = [
    "Gestão de Projetos Ágeis", "Análise de Dados e Planilhas", "Atendimento ao Cliente",
    "Operação de Sistemas ERP", "Comunicação Corporativa", "Contabilidade Gerencial",
    "Programação Python", "Manutenção Industrial", "Logística Integrada", "Negociação Comercial",
]

_CERTIFICACOES = [
    ("Certificação PMP Fictícia", "Instituto de Gestão Simulado"),
    ("Certificação CPA-20 Virtual", "Associação Financeira Fictícia"),
    ("Certificação Segurança do Trabalho NR-35", "Conselho Técnico Inventado"),
    ("Certificação Cloud Architect Simulada", "Academia Digital Fictícia"),
    ("Certificação Gestão da Qualidade ISO", "Bureau de Normas Fictício"),
]

_BENEFICIOS_PADRAO = [
    ("vale_refeicao", 780.0),
    ("vale_transporte", 320.0),
    ("auxilio_saude", 450.0),
    ("seguro_vida_corporativo", 95.0),
]


def min_wage_for_year(year: int) -> float:
    """Retorna o salário mínimo vigente para o ano informado."""
    if year <= 2000:
        return MIN_WAGE_BY_YEAR[2000]
    if year in MIN_WAGE_BY_YEAR:
        return MIN_WAGE_BY_YEAR[year]
    return MIN_WAGE_BY_YEAR[max(MIN_WAGE_BY_YEAR)]


def _inss_ir_deduction(gross: float) -> float:
    """Calcula desconto simplificado de INSS + IRRF sobre o salário bruto mensal."""
    inss = min(gross * 0.11, 908.85)
    base_ir = max(0.0, gross - inss - 2259.20)
    if base_ir <= 0.0:
        ir = 0.0
    elif base_ir <= 1500.0:
        ir = base_ir * 0.075
    elif base_ir <= 3000.0:
        ir = 112.50 + (base_ir - 1500.0) * 0.15
    else:
        ir = 337.50 + (base_ir - 3000.0) * 0.275
    return round(inss + ir, 2)


def _birth(p: dict[str, Any]) -> date:
    return date.fromisoformat(p["data_nascimento"])


def _end_date(p: dict[str, Any], today: date) -> date:
    if p.get("data_obito"):
        return min(today, date.fromisoformat(p["data_obito"]))
    return today


def _build_catalogs(
    rows: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    """Popula as tabelas de catálogo `empresa` e `cargo`."""
    empresas_by_sector: dict[str, list[dict[str, Any]]] = {}
    for emp in EMPRESAS:
        eid = empresa_uuid(emp["cnpj"])
        rec = {
            "id": eid,
            "nome": emp["name"],
            "cnpj_ficticio": emp["cnpj"],
            "ramo_atividade": emp["sector"],
            "endereco_id": None,
        }
        rows["empresa"].append(rec)
        empresas_by_sector.setdefault(emp["sector"], []).append(rec)

    cargos: list[dict[str, Any]] = []
    for idx, prof in enumerate(PROFISSOES[:90]):
        nome = prof["profissao"]
        if "Jr." in nome:
            nivel = 1
        elif "Sênior" in nome or "Diretor" in nome or "CEO" in nome:
            nivel = 3
        else:
            nivel = 2
        cid = str(uuid5(NAMESPACE_URL, f"cargo-{idx}-{nome}"))
        crec = {
            "id": cid,
            "nome": nome,
            "nivel_hierarquico": nivel,
            "_setor": prof["setor"],
        }
        rows["cargo"].append({
            "id": cid,
            "nome": nome,
            "nivel_hierarquico": nivel,
        })
        cargos.append(crec)

    return empresas_by_sector, cargos


def generate(
    personas: list[dict[str, Any]],
    seed: int = 7,
    today: date | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Gera todas as tabelas do domínio 05 (Carreira & Trabalho)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "empresa": [],
        "cargo": [],
        "contrato_trabalho": [],
        "historico_emprego": [],
        "salario": [],
        "holerite": [],
        "beneficio": [],
        "avaliacao_desempenho": [],
        "promocao": [],
        "demissao": [],
        "ferias": [],
        "licenca_trabalho": [],
        "habilidade_profissional": [],
        "certificacao_profissional": [],
        "sindicato_ficticio": [],
        "colega_trabalho": [],
    }

    empresas_by_sector, cargos = _build_catalogs(rows)
    all_sectors = list(empresas_by_sector.keys())
    by_id = {p["id"]: p for p in personas}
    ordered = sorted(personas, key=lambda p: (p.get("geracao", 0), p["idx"]))

    workers_by_company: dict[str, list[tuple[str, str]]] = {}

    for p in ordered:
        rng = master.fork(p["id"], "gen05-carreira")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)

        p["salario_mensal"] = 0.0
        p["renda_anual"] = 0.0
        p["desempregado"] = False
        p["sindicato"] = False
        p["empresa_atual_id"] = None

        if age < 16:
            continue

        # Idade de entrada no mercado conforme escolaridade (sempre >= 18 para CLT/PJ)
        edu = p.get("education", "medio")
        entry_age = 22 if edu in ("superior", "pos") else 18
        if age < entry_age:
            continue

        # Influência familiar (nepotismo)
        pai = by_id.get(p.get("pai_id")) if p.get("pai_id") else None
        mae = by_id.get(p.get("mae_id")) if p.get("mae_id") else None
        parent_sector = None
        parent_company_id = None
        parent_person_id = None
        for par in (pai, mae):
            if par and par.get("setor_empregado"):
                parent_sector = par["setor_empregado"]
                parent_company_id = par.get("empresa_atual_id")
                parent_person_id = par["id"]
                break

        if parent_sector and parent_sector in empresas_by_sector and rng.bernoulli(SAME_PARENT_SECTOR_PROB):
            sector = parent_sector
        else:
            sector = str(rng.choice(all_sectors))

        nepotism_mult = SocioeconomicEngine.family_influence_weight(rng, sector, parent_sector)
        nepotism_bonus = round((nepotism_mult - 1.0) * 0.8, 4)

        # Probabilidade de estar ou ter estado empregado
        emp_prob = 0.86
        if p.get("tem_doenca_grave"):
            emp_prob -= 0.15
        if p.get("criminal", {}).get("convicted"):
            emp_prob *= 0.65
        if not rng.bernoulli(max(0.25, emp_prob)):
            p["desempregado"] = True
            continue

        p["setor_empregado"] = sector

        # Habilidades e certificações profissionais
        n_skills = rng.integer(1, 3)
        for s_idx in range(n_skills):
            hab_nome = str(rng.choice(_HABILIDADES_TECNICAS))
            nivel_hab = str(rng.choice(["basico", "intermediario", "avancado"], weights=[0.25, 0.45, 0.30]))
            rows["habilidade_profissional"].append({
                "id": str(uuid5(NAMESPACE_URL, f"habprof-{p['id']}-{s_idx}")),
                "pessoa_id": p["id"],
                "nome_habilidade": hab_nome,
                "nivel": nivel_hab,
            })

        if edu in ("superior", "pos") and rng.bernoulli(0.45):
            cert_nome, cert_org = rng.choice(_CERTIFICACOES)
            rows["certificacao_profissional"].append({
                "id": str(uuid5(NAMESPACE_URL, f"certprof-{p['id']}")),
                "pessoa_id": p["id"],
                "nome": str(cert_nome),
                "orgao_emissor": str(cert_org),
                "validade": (end + timedelta(days=rng.integer(180, 1095))).isoformat(),
            })

        # Simula 1 a 3 vínculos de emprego ao longo da vida adulta
        career_start = born + timedelta(days=entry_age * 365 + rng.integer(15, 180))
        if career_start >= end - timedelta(days=60):
            continue

        max_jobs = 1 if age < 26 else (2 if age < 40 else rng.integer(1, 3))
        cur_start = career_start
        sector_empresas = empresas_by_sector[sector]
        jr_cargos = [c for c in cargos if c["nivel_hierarquico"] == 1] or cargos
        pl_cargos = [c for c in cargos if c["nivel_hierarquico"] == 2] or cargos
        sr_cargos = [c for c in cargos if c["nivel_hierarquico"] == 3] or cargos

        for j_idx in range(max_jobs):
            if cur_start >= end - timedelta(days=60):
                break

            if j_idx == 0 and parent_company_id and rng.bernoulli(FAMILY_COMPANY_PROB):
                emp_id = parent_company_id
            else:
                emp_id = rng.choice(sector_empresas)["id"]

            cargo_atual = rng.choice(jr_cargos if j_idx == 0 else pl_cargos)
            tipo_contrato = str(
                rng.choice(
                    ["CLT", "PJ", "publico", "temporario"],
                    weights=[0.70, 0.16, 0.09, 0.05],
                )
            )
            if p.get("criminal", {}).get("convicted") and tipo_contrato == "publico":
                tipo_contrato = "CLT"

            is_last_job = j_idx == max_jobs - 1
            if is_last_job and p["esta_vivo"] and not rng.bernoulli(0.14):
                dt_fim = None
            else:
                max_span = max(61, (end - cur_start).days - 10)
                dur = min(max_span, rng.integer(180, max(181, min(2500, max_span))))
                dt_fim = cur_start + timedelta(days=dur)
                if dt_fim <= cur_start:
                    dt_fim = cur_start + timedelta(days=30)

            contrato_id = str(uuid5(NAMESPACE_URL, f"contrato-{p['id']}-{j_idx}"))
            rows["contrato_trabalho"].append({
                "id": contrato_id,
                "pessoa_id": p["id"],
                "empresa_id": emp_id,
                "cargo_id": cargo_atual["id"],
                "tipo_contrato": tipo_contrato,
                "data_inicio": cur_start.isoformat(),
                "data_fim": dt_fim.isoformat() if dt_fim else None,
            })

            hist_end = dt_fim or end
            if hist_end <= cur_start:
                hist_end = cur_start + timedelta(days=30)
            motivo_saida = "ativo" if dt_fim is None else str(
                rng.choice(["transição de carreira", "reestruturação", "término de contrato", "aposentadoria"])
            )
            rows["historico_emprego"].append({
                "id": str(uuid5(NAMESPACE_URL, f"histemp-{contrato_id}")),
                "pessoa_id": p["id"],
                "empresa_id": emp_id,
                "cargo_id": cargo_atual["id"],
                "inicio": cur_start.isoformat(),
                "fim": hist_end.isoformat(),
                "motivo_saida": motivo_saida,
            })

            # Cálculo salarial calibrado (acima do salário mínimo vigente)
            exp_years = max(0.0, (cur_start - career_start).days / 365.25)
            is_female = p["sexo"] == "feminino"
            is_minority = p.get("ancestry") in ("africana", "indigena", "mista")
            base_sal = SocioeconomicEngine.salary(
                rng,
                education=edu,
                experience_years=exp_years,
                sector=sector if sector in SocioeconomicEngine.SECTOR_SHIFT else "aberto",
                gender_female=is_female,
                race_minority=is_minority,
                nepotism_log_bonus=nepotism_bonus,
            )
            # Escala mensal realista em R$ e piso do salário mínimo do ano de início
            piso = min_wage_for_year(cur_start.year)
            class_mult = {
                "A": 5.5, "B1": 3.4, "B2": 2.2, "C1": 1.6, "C2": 1.25, "D_E": 1.05,
            }.get(p["classe_social"], 1.5)
            edu_mult = {
                "fundamental": 1.0,
                "medio": 1.35,
                "superior": 2.35,
                "pos": 3.40,
            }.get(edu, 1.2)
            monthly_sal = round(max(piso * 1.08, (base_sal / 1200.0) * max(piso, 1320.0) * class_mult * edu_mult), 2)
            if p.get("impactos_saude", {}).get("income_reduction", 0.0) > 0:
                red = float(p["impactos_saude"]["income_reduction"])
                monthly_sal = round(max(piso * 1.05, monthly_sal * (1.0 - red)), 2)

            rows["salario"].append({
                "id": str(uuid5(NAMESPACE_URL, f"sal-{contrato_id}")),
                "contrato_id": contrato_id,
                "valor": monthly_sal,
                "data_vigencia": cur_start.isoformat(),
            })

            # Holerite mensal de referência
            descontos = _inss_ir_deduction(monthly_sal)
            liquido = round(max(piso * 0.85, monthly_sal - descontos), 2)
            mes_ref = date(hist_end.year, hist_end.month, 1)
            rows["holerite"].append({
                "id": str(uuid5(NAMESPACE_URL, f"hol-{contrato_id}")),
                "contrato_id": contrato_id,
                "mes_referencia": mes_ref.isoformat(),
                "valor_liquido": liquido,
                "descontos": descontos,
            })

            # Benefícios
            for b_idx, (btipo, bval) in enumerate(_BENEFICIOS_PADRAO[:2]):
                rows["beneficio"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"ben-{contrato_id}-{b_idx}")),
                    "contrato_id": contrato_id,
                    "tipo": btipo,
                    "valor": bval,
                })

            # Avaliação de desempenho e possível promoção
            nota_aval = round(rng.normal_clipped(7.8, 1.1, 3.0, 10.0), 2)
            rows["avaliacao_desempenho"].append({
                "id": str(uuid5(NAMESPACE_URL, f"aval-{contrato_id}")),
                "pessoa_id": p["id"],
                "empresa_id": emp_id,
                "periodo": f"{cur_start.year}",
                "nota": nota_aval,
                "feedback_ficticio": "Desempenho consistente com metas fictícias.",
            })

            tenure_days = (hist_end - cur_start).days
            if nota_aval >= 8.0 and tenure_days >= 365 and rng.bernoulli(0.42):
                novo_cargo = rng.choice(sr_cargos if cargo_atual["nivel_hierarquico"] >= 2 else pl_cargos)
                promo_dt = cur_start + timedelta(days=min(tenure_days - 10, 365))
                rows["promocao"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"promo-{contrato_id}")),
                    "pessoa_id": p["id"],
                    "empresa_id": emp_id,
                    "cargo_anterior_id": cargo_atual["id"],
                    "cargo_novo_id": novo_cargo["id"],
                    "data": promo_dt.isoformat(),
                })

            # Férias se trabalhou pelo menos 1 ano
            if tenure_days >= 365:
                fer_ini = cur_start + timedelta(days=330)
                fer_fim = min(hist_end - timedelta(days=1), fer_ini + timedelta(days=20))
                if fer_fim > fer_ini:
                    rows["ferias"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"ferias-{contrato_id}")),
                        "contrato_id": contrato_id,
                        "data_inicio": fer_ini.isoformat(),
                        "data_fim": fer_fim.isoformat(),
                        "dias": (fer_fim - fer_ini).days,
                    })

            # Licença médica se doença grave/crônica
            if (p.get("tem_doenca_grave") or p.get("impactos_saude", {}).get("sick_leave")) and tenure_days >= 90:
                lic_ini = cur_start + timedelta(days=45)
                lic_fim = min(hist_end - timedelta(days=1), lic_ini + timedelta(days=rng.integer(15, 40)))
                if lic_fim > lic_ini:
                    rows["licenca_trabalho"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"lic-{contrato_id}")),
                        "pessoa_id": p["id"],
                        "empresa_id": emp_id,
                        "tipo": "licença médica INSS fictícia",
                        "data_inicio": lic_ini.isoformat(),
                        "data_fim": lic_fim.isoformat(),
                    })

            # Demissão se contrato encerrado
            if dt_fim is not None:
                tipo_dem = str(
                    rng.choice(
                        ["sem_justa_causa", "pedido", "justa_causa"],
                        weights=[0.58, 0.37, 0.05],
                    )
                )
                mot_dem = (
                    "afastamento e reestruturação após problema de saúde"
                    if p.get("tem_doenca_grave")
                    else motivo_saida
                )
                rows["demissao"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"dem-{contrato_id}")),
                    "contrato_id": contrato_id,
                    "data": dt_fim.isoformat(),
                    "motivo": mot_dem,
                    "tipo": tipo_dem,
                })
                cur_start = dt_fim + timedelta(days=rng.integer(30, 180))
                if is_last_job:
                    p["desempregado"] = True
            else:
                p["salario_mensal"] = monthly_sal
                p["renda_anual"] = round(monthly_sal * 13.3, 2)
                p["empresa_atual_id"] = emp_id
                p["desempregado"] = False

            workers_by_company.setdefault(emp_id, []).append((p["id"], f"{cur_start.year}-{hist_end.year}"))
            if parent_person_id and emp_id == parent_company_id and parent_person_id != p["id"]:
                rows["colega_trabalho"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"col-fam-{parent_person_id}-{p['id']}")),
                    "pessoa_id_a": parent_person_id,
                    "pessoa_id_b": p["id"],
                    "empresa_id": emp_id,
                    "periodo": f"{cur_start.year}-{hist_end.year} (influência familiar)",
                })

        # Sindicato fictício
        if tipo_contrato in ("CLT", "publico") and rng.bernoulli(0.28):
            p["sindicato"] = True
            rows["sindicato_ficticio"].append({
                "id": str(uuid5(NAMESPACE_URL, f"sind-{p['id']}")),
                "pessoa_id": p["id"],
                "nome_sindicato": f"Sindicato dos Trabalhadores de {sector.title()} Fictício",
                "categoria": sector,
            })

    # Vínculos adicionais de colegas na mesma empresa
    for emp_id, wlist in workers_by_company.items():
        if len(wlist) >= 2:
            for idx in range(min(len(wlist) - 1, 5)):
                pa, per_a = wlist[idx]
                pb, _per_b = wlist[idx + 1]
                if pa != pb:
                    rows["colega_trabalho"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"col-{emp_id}-{pa}-{pb}")),
                        "pessoa_id_a": pa,
                        "pessoa_id_b": pb,
                        "empresa_id": emp_id,
                        "periodo": per_a,
                    })

    return rows
