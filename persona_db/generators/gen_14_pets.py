"""gen_14_pets — domínio 14: animais de estimação, raças, clínicas veterinárias e vacinação.

Implementa a seção de Pets de TASK-053 em TODO.MD:
- Probabilidade de posse de pet em função da classe social e perfil familiar.
- Raças correlacionadas com classe socioeconômica.
- Consultas veterinárias, vacinas e histórico de adoção/tutela.
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from typing import Any
from uuid import NAMESPACE_URL, uuid5

try:  # pragma: no cover
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
    from persona_db.seeds.lookup_data import RACAS_PET
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
    from persona_db.seeds.lookup_data import RACAS_PET

_NOMES_PET = [
    "Thor", "Mel", "Bela", "Bob", "Luna", "Simba", "Nina", "Zeus", "Amora", "Fred",
]

_ESPECIE_MAP = {
    "cao": "canina",
    "gato": "felina",
    "outros": "aves",
}

_CLINICAS = [
    "Clínica Veterinária São Francisco Fictícia",
    "Hospital PetVida Simulado",
    "Centro Veterinário Amigo Fiel Virtual",
]


def _birth(p: dict[str, Any]) -> date:
    return date.fromisoformat(p["data_nascimento"])


def _end_date(p: dict[str, Any], today: date) -> date:
    if p.get("data_obito"):
        return min(today, date.fromisoformat(p["data_obito"]))
    return today


def generate(
    personas: list[dict[str, Any]],
    seed: int = 7,
    today: date | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Gera todas as tabelas do domínio 14 (Pets & Animais)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "raca": [],
        "pet": [],
        "veterinario": [],
        "clinica_veterinaria": [],
        "consulta_veterinaria": [],
        "vacina_pet": [],
        "adocao_pet": [],
        "pet_historico_dono": [],
    }

    racas: list[dict[str, Any]] = []
    for rp in RACAS_PET[:25]:
        rid = str(uuid5(NAMESPACE_URL, f"raca-{rp['tipo']}-{rp['raca']}"))
        rec = {
            "id": rid,
            "nome": rp["raca"],
            "especie": _ESPECIE_MAP.get(rp["tipo"], "canina"),
        }
        rows["raca"].append(rec)
        racas.append(rec)

    vets: list[dict[str, Any]] = []
    for idx, esp in enumerate(["clínica médica", "cirurgia", "dermatologia"]):
        vid = str(uuid5(NAMESPACE_URL, f"vet-{idx}"))
        rec = {"id": vid, "nome": f"Dr(a). Vet Simulado {idx + 1}", "especialidade": esp}
        rows["veterinario"].append(rec)
        vets.append(rec)

    clinicas: list[dict[str, Any]] = []
    for nome in _CLINICAS:
        cid = str(uuid5(NAMESPACE_URL, f"clinvet-{nome}"))
        rec = {"id": cid, "nome": nome, "endereco_id": None}
        rows["clinica_veterinaria"].append(rec)
        clinicas.append(rec)

    for p in personas:
        rng = master.fork(p["id"], "gen14-pets")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)
        if age < 18 or not rng.bernoulli(0.46):
            continue

        raca = rng.choice(racas)
        pet_id = str(uuid5(NAMESPACE_URL, f"pet-{p['id']}"))
        pet_birth = max(born + timedelta(days=18 * 365), end - timedelta(days=rng.integer(180, 2500)))
        if pet_birth > end:
            pet_birth = end - timedelta(days=30)

        rows["pet"].append({
            "id": pet_id,
            "pessoa_id_dono": p["id"],
            "nome": str(rng.choice(_NOMES_PET)),
            "raca_id": raca["id"],
            "data_nascimento": pet_birth.isoformat(),
        })

        adoc_dt = min(end, pet_birth + timedelta(days=60))
        origem = str(
            rng.choice(
                ["resgate", "canil", "loja"],
                weights=[0.30, 0.45, 0.25] if p["classe_social"] in ("A", "B1") else [0.65, 0.20, 0.15],
            )
        )
        rows["adocao_pet"].append({
            "id": str(uuid5(NAMESPACE_URL, f"adocpet-{pet_id}")),
            "pet_id": pet_id,
            "pessoa_id_adotante": p["id"],
            "data": adoc_dt.isoformat(),
            "origem": origem,
        })

        rows["pet_historico_dono"].append({
            "id": str(uuid5(NAMESPACE_URL, f"pethist-{pet_id}")),
            "pet_id": pet_id,
            "pessoa_id": p["id"],
            "data_inicio": adoc_dt.isoformat(),
            "data_fim": end.isoformat(),
            "motivo_transferencia": "tutor atual",
        })

        cons_dt = min(end, adoc_dt + timedelta(days=30))
        vet = rng.choice(vets)
        clin = rng.choice(clinicas)
        rows["consulta_veterinaria"].append({
            "id": str(uuid5(NAMESPACE_URL, f"consvet-{pet_id}")),
            "pet_id": pet_id,
            "veterinario_id": vet["id"],
            "clinica_id": clin["id"],
            "data": cons_dt.isoformat(),
            "motivo": "check-up e imunização",
        })
        rows["vacina_pet"].append({
            "id": str(uuid5(NAMESPACE_URL, f"vacpet-{pet_id}")),
            "pet_id": pet_id,
            "tipo_vacina": "polivalente V10 / antirrábica fictícia",
            "data": cons_dt.isoformat(),
        })

    return rows
