"""gen_17_comportamento — domínio 17: personalidade Big Five, hábitos, rotina e estilo de aprendizagem.

Implementa a seção de Comportamento & Personalidade de TASK-053 em TODO.MD:
- Traços de personalidade Big Five (`abertura`, `conscienciosidade`,
  `extroversao`, `amabilidade`, `neuroticismo`) em `[0, 10]`.
- Hábitos, rotina diária, preferências, aversões, habilidades, talentos,
  medos, sonhos e estilo de aprendizagem.
"""
from __future__ import annotations

import os
import sys
from datetime import date
from typing import Any
from uuid import NAMESPACE_URL, uuid5

try:  # pragma: no cover
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today

_BIG_FIVE = [
    "abertura",
    "conscienciosidade",
    "extroversao",
    "amabilidade",
    "neuroticismo",
]

_HABITOS = [
    ("Leitura diária antes de dormir", "diária"),
    ("Caminhada matinal no parque", "semanal"),
    ("Organização de finanças domésticas", "mensal"),
    ("Preparo de refeições caseiras", "diária"),
]

_PREFERENCIAS = [
    ("gastronomia", "culinária regional brasileira"),
    ("música", "MPB e samba clássico"),
    ("lazer", "cinema e séries documentais"),
]

_AVERSOES = [
    ("ambiente", "locais excessivamente barulhentos"),
    ("clima", "calor extremo"),
    ("rotina", "trânsito intenso no horário de pico"),
]

_HABILIDADES_GERAIS = [
    "Culinária doméstica",
    "Oratória e comunicação",
    "Jardinagem urbana",
    "Fotografia amadora",
]

_TALENTOS = [
    "música instrumental",
    "desenho e pintura",
    "escrita criativa",
    "raciocínio lógico",
]

_MEDOS = [
    ("acrofobia leve (medo de altura)", "infância"),
    ("receio de falar em público", "adolescência"),
    ("medo de insetos", "infância"),
]

_SONHOS = [
    ("Conquistar independência financeira familiar", "em_curso"),
    ("Conhecer todas as regiões do país", "em_curso"),
    ("Concluir formação educacional superior", "realizado"),
]


def generate(
    personas: list[dict[str, Any]],
    seed: int = 7,
    today: date | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Gera todas as tabelas do domínio 17 (Comportamento & Personalidade)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "traco_personalidade": [],
        "habito": [],
        "rotina_diaria": [],
        "preferencia": [],
        "aversao": [],
        "habilidade": [],
        "talento": [],
        "medo_ficticio": [],
        "sonho_ficticio": [],
        "estilo_aprendizagem": [],
    }

    for p in personas:
        rng = master.fork(p["id"], "gen17-comportamento")

        for t_idx, traco in enumerate(_BIG_FIVE):
            mu = 6.2 if traco != "neuroticismo" else (6.8 if p.get("tem_transtorno_mental") else 4.5)
            val = round(rng.normal_clipped(mu, 1.6, 0.0, 10.0), 2)
            rows["traco_personalidade"].append({
                "id": str(uuid5(NAMESPACE_URL, f"traco-{p['id']}-{t_idx}")),
                "pessoa_id": p["id"],
                "nome_traco": traco,
                "intensidade": val,
            })

        hab_desc, hab_freq = rng.choice(_HABITOS)
        rows["habito"].append({
            "id": str(uuid5(NAMESPACE_URL, f"habito-{p['id']}")),
            "pessoa_id": p["id"],
            "descricao": str(hab_desc),
            "frequencia": str(hab_freq),
        })

        rows["rotina_diaria"].append({
            "id": str(uuid5(NAMESPACE_URL, f"rotina-{p['id']}")),
            "pessoa_id": p["id"],
            "horario": "07:00:00",
            "atividade": "Café da manhã e início das atividades diárias",
        })

        p_cat, p_item = rng.choice(_PREFERENCIAS)
        rows["preferencia"].append({
            "id": str(uuid5(NAMESPACE_URL, f"pref-{p['id']}")),
            "pessoa_id": p["id"],
            "categoria": str(p_cat),
            "item_preferido": str(p_item),
        })

        a_cat, a_item = rng.choice(_AVERSOES)
        rows["aversao"].append({
            "id": str(uuid5(NAMESPACE_URL, f"aver-{p['id']}")),
            "pessoa_id": p["id"],
            "categoria": str(a_cat),
            "item_evitado": str(a_item),
        })

        rows["habilidade"].append({
            "id": str(uuid5(NAMESPACE_URL, f"habil-{p['id']}")),
            "pessoa_id": p["id"],
            "nome": str(rng.choice(_HABILIDADES_GERAIS)),
            "nivel": str(rng.choice(["basico", "intermediario", "avancado", "especialista"])),
        })

        rows["talento"].append({
            "id": str(uuid5(NAMESPACE_URL, f"talento-{p['id']}")),
            "pessoa_id": p["id"],
            "area": str(rng.choice(_TALENTOS)),
            "nivel_ficticio": round(rng.normal_clipped(6.8, 1.5, 0.0, 10.0), 2),
        })

        m_desc, m_orig = rng.choice(_MEDOS)
        rows["medo_ficticio"].append({
            "id": str(uuid5(NAMESPACE_URL, f"medo-{p['id']}")),
            "pessoa_id": p["id"],
            "descricao": str(m_desc),
            "origem": str(m_orig),
        })

        s_desc, s_stat = rng.choice(_SONHOS)
        rows["sonho_ficticio"].append({
            "id": str(uuid5(NAMESPACE_URL, f"sonho-{p['id']}")),
            "pessoa_id": p["id"],
            "descricao": str(s_desc),
            "status": str(s_stat),
        })

        rows["estilo_aprendizagem"].append({
            "id": str(uuid5(NAMESPACE_URL, f"estapr-{p['id']}")),
            "pessoa_id": p["id"],
            "tipo": str(rng.choice(["visual", "auditivo", "cinestesico"])),
        })

    return rows
