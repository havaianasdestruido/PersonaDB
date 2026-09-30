"""gen_23_midia — domínio 23: notícias, menções na mídia, prêmios, entrevistas e reputação.

Implementa a seção de Mídia & Reputação de TASK-053 em TODO.MD:
- Calcula `reputacao_score` como função agregada de antecedentes criminais,
  menções na mídia, exercício de cargo público e escolaridade.
- Gera notícias, menções, prêmios e entrevistas fictícias.
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
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today

_VEICULOS_MIDIA = [
    "Jornal Gazeta de Alvorada Fictícia",
    "Portal Notícias do Sul Simulado",
    "Rádio e TV Horizonte Virtual",
    "Revista Economia & Sociedade Inventada",
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
    """Gera todas as tabelas do domínio 23 (Mídia & Reputação)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "noticia_ficticia": [],
        "mencao_midia": [],
        "reputacao_score": [],
        "premio_ficticio": [],
        "entrevista_ficticia": [],
    }

    for p in personas:
        rng = master.fork(p["id"], "gen23-midia")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)

        base_score = 72.0
        if p.get("education") in ("superior", "pos"):
            base_score += 6.0
        if p.get("tem_cargo_publico"):
            base_score += 8.0
        if p.get("tem_antecedente_criminal"):
            base_score -= 28.0
        if p.get("foi_preso"):
            base_score -= 12.0

        # Notícias e menções na mídia
        p_noticia = 0.45 if (p.get("tem_cargo_publico") or p.get("tem_antecedente_criminal") or p["classe_social"] == "A") else 0.12
        if age >= 18 and rng.bernoulli(p_noticia):
            veic = str(rng.choice(_VEICULOS_MIDIA))
            not_dt = max(born + timedelta(days=18 * 365), end - timedelta(days=rng.integer(15, 900)))
            not_dt = min(not_dt, end)

            if p.get("tem_antecedente_criminal"):
                contexto = "negativo"
                titulo = f"Caso judicial envolvendo {p['nome_completo']} é julgado"
                base_score -= 6.0
            elif p.get("tem_cargo_publico") or p["classe_social"] in ("A", "B1"):
                contexto = "positivo"
                titulo = f"Destaque regional: {p['nome_completo']} participa de iniciativa local"
                base_score += 5.0
            else:
                contexto = "neutro"
                titulo = f"Moradores comentam cotidiano em {p.get('cidade_residencia', 'Alvorada')}"

            not_id = str(uuid5(NAMESPACE_URL, f"noticia-{p['id']}"))
            rows["noticia_ficticia"].append({
                "id": not_id,
                "pessoa_id": p["id"],
                "titulo": titulo,
                "veiculo_ficticio": veic,
                "data": not_dt.isoformat(),
            })
            rows["mencao_midia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"mencao-{not_id}")),
                "pessoa_id": p["id"],
                "noticia_id": not_id,
                "contexto": contexto,
            })

            if contexto == "positivo" and rng.bernoulli(0.45):
                rows["entrevista_ficticia"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"entrev-{p['id']}")),
                    "pessoa_id": p["id"],
                    "veiculo_ficticio": veic,
                    "data": not_dt.isoformat(),
                    "tema": "Carreira, comunidade e desenvolvimento regional",
                })

        if age >= 18 and rng.bernoulli(0.14) and not p.get("tem_antecedente_criminal"):
            pr_dt = max(born + timedelta(days=18 * 365), end - timedelta(days=rng.integer(30, 720)))
            pr_dt = min(pr_dt, end)
            rows["premio_ficticio"].append({
                "id": str(uuid5(NAMESPACE_URL, f"premio-{p['id']}")),
                "pessoa_id": p["id"],
                "nome": "Reconhecimento Comunitário e Profissional Fictício",
                "categoria": p.get("setor_empregado") or "cidadania",
                "data": pr_dt.isoformat(),
            })
            base_score += 4.0

        final_score = round(min(100.0, max(0.0, base_score + rng.normal(0.0, 3.0))), 2)
        p["reputacao_score"] = final_score
        rows["reputacao_score"].append({
            "id": str(uuid5(NAMESPACE_URL, f"repscore-{p['id']}")),
            "pessoa_id": p["id"],
            "data": end.isoformat(),
            "valor_score": final_score,
        })

    return rows
