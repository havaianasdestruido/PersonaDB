"""gen_03_saude — domínio 03: saúde.

generate(personas, seed, today) -> dict[str, list[dict]]

Tabelas: doenca_pessoa, tratamento, sintoma_ocorrencia, exame, exame_resultado,
prescricao, dosagem, cirurgia, internacao, alta_hospitalar, vacina_dose,
alergia, alergia_reacao, condicao_cronica, saude_mental_registro, terapia,
sessao_terapia, seguro_saude.

Catálogos (IDs determinísticos, sem FK externa):
  doenca, sintoma, medicamento, cirurgiao, hospital, leito, vacina,
  plano_saude, convenio, terapia (terapeuta como UUID fictício).
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from uuid import NAMESPACE_URL, uuid5

try:
    from persona_db.engines.health import HealthEngine
    from persona_db.engines.rng import SeededRNG, new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
except ImportError:
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.health import HealthEngine
    from persona_db.engines.rng import SeededRNG, new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today

# ---------------------------------------------------------------------------
# Catálogos determinísticos
# ---------------------------------------------------------------------------
_DOENCAS = [
    ("Hipertensão Simulada", "cardiovascular", "moderada"),
    ("Diabetes Tipo 2 Fictício", "metabólica", "moderada"),
    ("Asma Inventada", "respiratória", "leve"),
    ("Artrite Fictícia", "musculoesquelética", "leve"),
    ("Ansiedade Generalizada Simulada", "mental", "leve"),
    ("Depressão Fictícia", "mental", "moderada"),
    ("Colesterol Alto Simulado", "cardiovascular", "leve"),
    ("Enxaqueca Fictícia", "neurológica", "leve"),
    ("Gastrite Simulada", "digestiva", "leve"),
    ("Hipotireoidismo Fictício", "endócrina", "leve"),
]
_DOENCA_IDS = [str(uuid5(NAMESPACE_URL, f"doenca-{d[0]}")) for d in _DOENCAS]

_SINTOMAS = [
    ("Cefaleia Fictícia", "neurológica"),
    ("Fadiga Simulada", "geral"),
    ("Náusea Inventada", "digestiva"),
    ("Dor Torácica Fictícia", "cardiovascular"),
    ("Tosse Simulada", "respiratória"),
    ("Febre Fictícia", "infecciosa"),
    ("Tontura Simulada", "neurológica"),
    ("Dor Abdominal Fictícia", "digestiva"),
]
_SINTOMA_IDS = [str(uuid5(NAMESPACE_URL, f"sintoma-{s[0]}")) for s in _SINTOMAS]

_MEDICAMENTOS = [
    ("Simulofeno", "ácido simulofênico"),
    ("Fictivac", "composto fictivac-B"),
    ("Placinil", "placinil-X"),
    ("Testofen", "testofen-alfa"),
    ("Inventin", "inventin-II"),
    ("Simulazol", "simulazol-genérico"),
    ("Fictazida", "fictazida-HCL"),
    ("Placifor", "placifor-sulfato"),
]
_MED_IDS = [str(uuid5(NAMESPACE_URL, f"med-{m[0]}")) for m in _MEDICAMENTOS]

_HOSPITAIS = [
    ("Hospital São Fictício", "geral"),
    ("Hospital Santa Simulada", "especializado"),
    ("Clínica Inventada Norte", "clínica"),
    ("UPA Fictícia Centro", "urgência"),
    ("Hospital do Povo Simulado", "geral"),
]
_HOSP_IDS = [str(uuid5(NAMESPACE_URL, f"hosp-{h[0]}")) for h in _HOSPITAIS]

_VACINAS = [
    ("Vacina Simulada Anti-XYZ", "inativada"),
    ("Imunizante Fictício Beta", "mRNA"),
    ("Vacina Inventada Gama", "viral"),
    ("Imuno Simulado Delta", "subunidade"),
]
_VAC_IDS = [str(uuid5(NAMESPACE_URL, f"vac-{v[0]}")) for v in _VACINAS]

_PLANOS = [
    ("Simulo Saúde", "ambulatorial", 320.0),
    ("Fictivida Premium", "hospitalar", 890.0),
    ("PlanoFácil Inventado", "odontológico", 120.0),
    ("SimulaMed Plus", "completo", 1400.0),
    ("Básico Simulado", "ambulatorial", 190.0),
]
_PLANO_IDS = [str(uuid5(NAMESPACE_URL, f"plano-{p[0]}")) for p in _PLANOS]

_CONDICOES_CRONICAS = [
    "Hipertensão Controlada Fictícia", "Diabetes Tipo 2 Simulado",
    "Hipotireoidismo Inventado", "Artrite Simulada", "Asma Fictícia",
]
_SAUDE_MENTAL = [
    "Ansiedade Generalizada Fictícia", "Depressão Simulada",
    "TOC Inventado", "Fobia Específica Fictícia",
]
_TIPOS_EXAME = [
    "hemograma", "glicemia", "colesterol", "urina", "raio-x",
    "ultrassom", "eletrocardiograma", "tomografia",
]
_TERAPIAS = ["cognitivo-comportamental", "psicanálise", "gestalt", "familiar"]
_ALERGIAS = [
    ("Penicilina Fictícia", "grave"),
    ("Dipirona Simulada", "moderada"),
    ("Látex Inventado", "leve"),
    ("Amendoim Fictício", "grave"),
    ("Glúten Simulado", "leve"),
]
_ESPECIALIDADES = ["cardiologia", "ortopedia", "neurologia", "ginecologia", "clínica geral"]
_CIRURGIAO_IDS = [str(uuid5(NAMESPACE_URL, f"cirurgiao-{esp}")) for esp in _ESPECIALIDADES]
_TIPO_CIRURGIA = [
    "apendicectomia fictícia", "laparoscopia simulada", "cesariana fictícia",
    "ortopédica simulada", "cardíaca fictícia",
]


def _isodate(d: date) -> str:
    return d.isoformat()


def _birth(p: dict) -> date:
    return date.fromisoformat(p["data_nascimento"])


def _death(p: dict) -> date | None:
    if p.get("data_obito"):
        return date.fromisoformat(p["data_obito"])
    return None


def _person_active_range(p: dict, today: date) -> tuple[date, date]:
    """Retorna janela temporal válida `[start, end]` dentro da vida da persona."""
    born = _birth(p)
    end = min(_death(p) or today, today)
    if end <= born:
        return born, born
    start = min(born + timedelta(days=365), born + timedelta(days=max(1, (end - born).days // 4)))
    if start > end:
        start = born
    return start, end


def _rand_date(rng: SeededRNG, start: date, end: date) -> date:
    if start >= end:
        return start
    span = max(1, (end - start).days)
    return start + timedelta(days=rng.integer(0, span - 1))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(personas: list[dict], seed: int = 3, today: date | None = None) -> dict[str, list[dict]]:
    """Gera todos os registros de saúde e enriquece personas com `impactos_saude`."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict]] = {
        "doenca": [], "sintoma": [], "medicamento": [], "cirurgiao": [],
        "hospital": [], "leito": [], "vacina": [], "plano_saude": [],
        "convenio": [], "doenca_pessoa": [], "tratamento": [],
        "sintoma_ocorrencia": [], "exame": [], "exame_resultado": [],
        "prescricao": [], "dosagem": [], "cirurgia": [],
        "internacao": [], "alta_hospitalar": [], "vacina_dose": [],
        "alergia": [], "alergia_reacao": [], "condicao_cronica": [],
        "saude_mental_registro": [], "terapia": [], "sessao_terapia": [],
        "seguro_saude": [],
    }

    _build_catalogs(rows)

    for p in personas:
        rng = master.fork(p["id"], "gen03")
        start, end = _person_active_range(p, today)
        age = max(0, (end - _birth(p)).days // 365)

        diag_dates: list[date] = []
        has_grave = _doencas_pessoa(p, rows, rng, start, end, age, diag_dates)
        _exames(p, rows, rng, start, end)
        has_chronic = _condicoes_cronicas(p, rows, rng, start, end, age, diag_dates)
        has_mental = _saude_mental(p, rows, rng, start, end, age, diag_dates)
        _prescricoes(p, rows, rng, start, end, diag_dates)
        _vacinas(p, rows, rng, _birth(p), end, age)
        _alergias_pessoa(p, rows, rng)
        _seguro(p, rows, rng, start, end)

        impact_rng = master.fork(p["id"], "gen03-impact")
        p["tem_doenca_grave"] = has_grave
        p["tem_doenca_cronica"] = has_chronic
        p["tem_transtorno_mental"] = has_mental
        p["impactos_saude"] = HealthEngine.chronic_impact(impact_rng, has_chronic or has_grave)

    return rows


def _build_catalogs(rows: dict) -> None:
    for (nome, cat, grav), did in zip(_DOENCAS, _DOENCA_IDS):
        rows["doenca"].append({"id": did, "nome": nome, "categoria": cat, "gravidade_padrao": grav})

    for (nome, cat), sid in zip(_SINTOMAS, _SINTOMA_IDS):
        rows["sintoma"].append({"id": sid, "nome": nome, "categoria": cat})

    for (nome, pa), mid in zip(_MEDICAMENTOS, _MED_IDS):
        rows["medicamento"].append({"id": mid, "nome_ficticio": nome, "principio_ativo_ficticio": pa})

    for i, (nome, tipo) in enumerate(_HOSPITAIS):
        hid = _HOSP_IDS[i]
        rows["hospital"].append({"id": hid, "nome": nome, "endereco_id": None, "tipo": tipo})
        for j in range(10):
            lid = str(uuid5(NAMESPACE_URL, f"leito-{hid}-{j}"))
            rows["leito"].append({
                "id": lid, "hospital_id": hid,
                "numero": f"{(i * 10 + j + 1):03d}", "ala": ["A", "B", "C"][j % 3],
            })

    for (nome, tipo), vid in zip(_VACINAS, _VAC_IDS):
        rows["vacina"].append({"id": vid, "nome": nome, "tipo": tipo})

    for (nome, cob, mens), pid in zip(_PLANOS, _PLANO_IDS):
        rows["plano_saude"].append({"id": pid, "operadora": nome, "cobertura": cob, "mensalidade": mens})

    conv_id = str(uuid5(NAMESPACE_URL, "convenio-principal"))
    rows["convenio"].append({
        "id": conv_id, "nome": "Convênio Fictício Nacional",
        "hospitais_conveniados": len(_HOSPITAIS),
    })

    for esp, cid in zip(_ESPECIALIDADES, _CIRURGIAO_IDS):
        rows["cirurgiao"].append({"id": cid, "nome": f"Dr(a). Simulado {esp.title()}", "especialidade": esp})


def _doencas_pessoa(
    p: dict,
    rows: dict,
    rng: SeededRNG,
    start: date,
    end: date,
    age: int,
    diag_dates: list[date],
) -> bool:
    n = rng.integer(0, 2) if age < 18 else rng.integer(0, 3)
    chosen = list(range(len(_DOENCAS)))
    rng._rng.shuffle(chosen)
    has_grave = False
    for i in chosen[:n]:
        did = _DOENCA_IDS[i]
        diag_date = _rand_date(rng, start, end)
        diag_dates.append(diag_date)
        dp_id = str(uuid5(NAMESPACE_URL, f"dp-{p['id']}-{did}"))
        estagio = str(rng.choice(["inicial", "moderado", "avançado"]))
        if estagio == "avançado":
            has_grave = True
        status = "ativo" if not p.get("data_obito") else str(rng.choice(["ativo", "resolvido"]))
        rows["doenca_pessoa"].append({
            "id": dp_id, "pessoa_id": p["id"], "doenca_id": did,
            "data_diagnostico": _isodate(diag_date),
            "estagio": estagio, "status": status,
        })
        trat_start = min(end, diag_date + timedelta(days=rng.integer(1, 30)))
        trat_end = None
        if rng.bernoulli(0.7):
            trat_end = min(end, trat_start + timedelta(days=rng.integer(30, 365)))
            trat_end = max(trat_end, trat_start)
        tipo_trat = str(rng.choice(["medicamentoso", "cirúrgico", "fisioterapia", "acompanhamento"]))
        rows["tratamento"].append({
            "id": str(uuid5(NAMESPACE_URL, f"trat-{dp_id}")),
            "pessoa_id": p["id"], "doenca_pessoa_id": dp_id,
            "tipo": tipo_trat,
            "data_inicio": _isodate(trat_start),
            "data_fim": _isodate(trat_end) if trat_end else None,
        })
        if rng.bernoulli(0.6):
            s_idx = rng.integer(0, len(_SINTOMAS) - 1)
            rows["sintoma_ocorrencia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"sint-{dp_id}-0")),
                "pessoa_id": p["id"],
                "sintoma_id": _SINTOMA_IDS[s_idx],
                "data_inicio": _isodate(diag_date),
                "intensidade": str(rng.choice(["leve", "moderada", "intensa"])),
            })

        # Se tratamento cirúrgico ou estágio avançado e houver margem antes de `end`, gera cirurgia e internação
        if (tipo_trat == "cirúrgico" or estagio == "avançado") and (end - trat_start).days >= 5:
            hosp_idx = rng.integer(0, len(_HOSP_IDS) - 1)
            hosp_id = _HOSP_IDS[hosp_idx]
            leito_id = str(uuid5(NAMESPACE_URL, f"leito-{hosp_id}-{rng.integer(0, 9)}"))
            cirurgiao_id = _CIRURGIAO_IDS[rng.integer(0, len(_CIRURGIAO_IDS) - 1)]
            dt_entrada = trat_start
            stay_days = min(rng.integer(2, 14), max(1, (end - dt_entrada).days))
            dt_saida = dt_entrada + timedelta(days=stay_days)
            tipo_cir = str(rng.choice(_TIPO_CIRURGIA))
            rows["cirurgia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"cir-{dp_id}")),
                "pessoa_id": p["id"],
                "tipo": tipo_cir,
                "data": _isodate(dt_entrada),
                "cirurgiao_id": cirurgiao_id,
                "hospital_id": hosp_id,
            })
            int_id = str(uuid5(NAMESPACE_URL, f"int-{dp_id}"))
            rows["internacao"].append({
                "id": int_id,
                "pessoa_id": p["id"],
                "hospital_id": hosp_id,
                "leito_id": leito_id,
                "data_entrada": _isodate(dt_entrada),
                "data_saida": _isodate(dt_saida),
                "motivo": f"Tratamento de {_DOENCAS[i][0]}",
            })
            rows["alta_hospitalar"].append({
                "id": str(uuid5(NAMESPACE_URL, f"alta-{int_id}")),
                "internacao_id": int_id,
                "data": _isodate(dt_saida),
                "condicao_saida": str(rng.choice(["estável", "recuperado", "acompanhamento ambulatorial"])),
            })
    return has_grave


def _exames(p: dict, rows: dict, rng: SeededRNG, start: date, end: date) -> None:
    for k in range(rng.integer(1, 4)):
        ex_id = str(uuid5(NAMESPACE_URL, f"ex-{p['id']}-{k}"))
        edate = _rand_date(rng, start, end)
        tipo = str(rng.choice(_TIPOS_EXAME))
        hosp = _HOSP_IDS[rng.integer(0, len(_HOSP_IDS) - 1)]
        rows["exame"].append({
            "id": ex_id, "pessoa_id": p["id"],
            "tipo_exame": tipo, "data": _isodate(edate), "local": hosp,
        })
        rows["exame_resultado"].append({
            "id": str(uuid5(NAMESPACE_URL, f"exr-{ex_id}")),
            "exame_id": ex_id,
            "parametro": tipo,
            "valor": str(round(rng.uniform(60.0, 200.0), 1)),
            "referencia": "valores de referência fictícios",
        })


def _prescricoes(
    p: dict,
    rows: dict,
    rng: SeededRNG,
    start: date,
    end: date,
    diag_dates: list[date],
) -> None:
    if not diag_dates or not rng.bernoulli(0.65):
        return
    med_idx = rng.integer(0, len(_MED_IDS) - 1)
    med_id = _MED_IDS[med_idx]
    presc_id = str(uuid5(NAMESPACE_URL, f"presc-{p['id']}-{med_id}"))
    medico_id = str(uuid5(NAMESPACE_URL, f"medico-{p['id']}"))
    min_diag = min(diag_dates)
    pdate = _rand_date(rng, min_diag, end)
    rows["prescricao"].append({
        "id": presc_id, "pessoa_id": p["id"], "medicamento_id": med_id,
        "medico_id": medico_id, "data": _isodate(pdate),
    })
    rows["dosagem"].append({
        "id": str(uuid5(NAMESPACE_URL, f"dos-{presc_id}")),
        "prescricao_id": presc_id,
        "quantidade": round(rng.uniform(0.5, 2.0), 1),
        "unidade": str(rng.choice(["mg", "ml", "comprimido"])),
        "frequencia": str(rng.choice(["1x/dia", "2x/dia", "8/8h", "12/12h"])),
    })


def _vacinas(p: dict, rows: dict, rng: SeededRNG, birth: date, end: date, age: int) -> None:
    n = rng.integer(1, 4)
    vac_idx = rng.integer(0, len(_VAC_IDS) - 1)
    vac_id = _VAC_IDS[vac_idx]
    span_days = max(1, (end - birth).days)
    cur_date = birth + timedelta(days=min(60, span_days // 4))
    for k in range(n):
        if cur_date > end:
            break
        rows["vacina_dose"].append({
            "id": str(uuid5(NAMESPACE_URL, f"vacdose-{p['id']}-{k}")),
            "pessoa_id": p["id"],
            "vacina_id": vac_id,
            "data": _isodate(cur_date),
            "dose_numero": k + 1,
            "local_aplicacao": str(rng.choice(["UBS Fictícia", "Hospital Simulado", "Farmácia Inventada"])),
        })
        cur_date = cur_date + timedelta(days=rng.integer(30, 120))


def _alergias_pessoa(p: dict, rows: dict, rng: SeededRNG) -> None:
    """Attempt to add a sampled allergy and optional reaction to ``rows``.

    The initial probability draw may leave ``rows`` unchanged. Sampling errors
    propagate to callers.
    """
    if not rng.bernoulli(0.25):
        return
    item = rng.choice(_ALERGIAS)
    subst, grav = item[0], item[1]
    al_id = str(uuid5(NAMESPACE_URL, f"alergia-{p['id']}-{subst}"))
    rows["alergia"].append({
        "id": al_id, "pessoa_id": p["id"], "substancia": subst, "gravidade": grav,
    })
    if rng.bernoulli(0.5):
        s_idx = rng.integer(0, len(_SINTOMA_IDS) - 1)
        rows["alergia_reacao"].append({
            "id": str(uuid5(NAMESPACE_URL, f"alreac-{al_id}")),
            "alergia_id": al_id,
            "sintoma_id": _SINTOMA_IDS[s_idx],
            "tratamento_aplicado": "anti-histamínico fictício",
        })


def _condicoes_cronicas(
    p: dict,
    rows: dict,
    rng: SeededRNG,
    start: date,
    end: date,
    age: int,
    diag_dates: list[date],
) -> bool:
    if age < 30 and not rng.bernoulli(0.1):
        return False
    if age >= 30 and not rng.bernoulli(0.35):
        return False
    nome = str(rng.choice(_CONDICOES_CRONICAS))
    cdate = _rand_date(rng, start, end)
    diag_dates.append(cdate)
    rows["condicao_cronica"].append({
        "id": str(uuid5(NAMESPACE_URL, f"cronica-{p['id']}-{nome}")),
        "pessoa_id": p["id"],
        "nome": nome,
        "data_diagnostico": _isodate(cdate),
        "controle_atual": str(rng.choice(["controlada", "parcialmente controlada", "descontrolada"])),
    })
    return True


def _saude_mental(
    p: dict,
    rows: dict,
    rng: SeededRNG,
    start: date,
    end: date,
    age: int,
    diag_dates: list[date],
) -> bool:
    if not rng.bernoulli(0.18):
        return False
    condicao = str(rng.choice(_SAUDE_MENTAL))
    sm_id = str(uuid5(NAMESPACE_URL, f"sm-{p['id']}"))
    sm_start = _rand_date(rng, start, end)
    diag_dates.append(sm_start)
    rows["saude_mental_registro"].append({
        "id": sm_id, "pessoa_id": p["id"],
        "condicao_ficticia": condicao,
        "data_inicio": _isodate(sm_start),
        "status": str(rng.choice(["ativo", "em remissão", "tratado"])),
    })
    if rng.bernoulli(0.6):
        tipo_ter = str(rng.choice(_TERAPIAS))
        ter_id = str(uuid5(NAMESPACE_URL, f"ter-{p['id']}-{tipo_ter}"))
        ter_start = min(end, sm_start + timedelta(days=rng.integer(7, 60)))
        terapeuta_id = str(uuid5(NAMESPACE_URL, f"terapeuta-{tipo_ter}"))
        rows["terapia"].append({
            "id": ter_id, "pessoa_id": p["id"],
            "tipo": tipo_ter, "terapeuta_id": terapeuta_id,
            "data_inicio": _isodate(ter_start),
        })
        for s in range(rng.integer(2, 8)):
            sdate = ter_start + timedelta(days=s * 14)
            if sdate > end:
                break
            rows["sessao_terapia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"sess-{ter_id}-{s}")),
                "terapia_id": ter_id,
                "data": _isodate(sdate),
                "duracao": "01:00:00",
                "notas_ficticias": "sessão fictícia registrada",
            })
    return True


def _seguro(p: dict, rows: dict, rng: SeededRNG, start: date, end: date) -> None:
    if not rng.bernoulli(0.45):
        return
    plano_idx = rng.integer(0, len(_PLANO_IDS) - 1)
    rows["seguro_saude"].append({
        "id": str(uuid5(NAMESPACE_URL, f"segsaude-{p['id']}")),
        "pessoa_id": p["id"],
        "plano_id": _PLANO_IDS[plano_idx],
        "data_contratacao": _isodate(_rand_date(rng, start, end)),
    })


if __name__ == "__main__":  # pragma: no cover
    from persona_db.generators.gen_00_pessoa import generate_personas
    ps = generate_personas(300, seed=3)
    r = generate(ps)
    for tbl in ("doenca_pessoa", "tratamento", "exame", "exame_resultado",
                "prescricao", "vacina_dose", "alergia", "condicao_cronica",
                "saude_mental_registro", "terapia", "sessao_terapia", "seguro_saude"):
        print(f"{tbl:30s} {len(r[tbl])}")
