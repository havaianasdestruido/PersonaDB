"""gen_07_residencia — domínio 07: endereços, residências, condomínios, aluguéis e vizinhos.

Implementa TASK-048 de TODO.MD:
- Trajetória residencial correlacionada com cidade de nascimento, saída da casa
  dos pais (`Normal(23, 4)` para A/B e `Normal(20, 3)` para C/D/E), migração
  por oportunidade de trabalho (`GeographyEngine`) e mudanças familiares.
- Bairros selecionados de acordo com o perfil socioeconômico (`GeographyEngine`).
- Tipo de posse (`proprio`, `financiado`, `alugado`, `cedido`) alinhado com
  ativos e financiamentos gerados em `gen_06_financas`.
"""
from __future__ import annotations

import hashlib
import os
import sys
from datetime import date, timedelta
from typing import Any
from uuid import NAMESPACE_URL, uuid5

try:  # pragma: no cover
    from persona_db.engines.geography import CITY_SET, GeographyEngine
    from persona_db.engines.rng import SeededRNG, new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.geography import CITY_SET, GeographyEngine
    from persona_db.engines.rng import SeededRNG, new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today

_LOGRADOUROS = [
    "Rua das Palmeiras Fictícias",
    "Avenida Central Simulada",
    "Alameda dos Ipês Inventados",
    "Rua Horizonte Azul",
    "Travessa da Liberdade Virtual",
    "Avenida Brasil Fictício",
    "Rua Sete de Setembro Simulado",
    "Rua das Acácias Douradas",
]

_MOTIVOS_MUDANCA = [
    "saída da casa dos pais",
    "oportunidade de emprego",
    "casamento ou união",
    "busca por menor custo de vida",
    "aquisição de imóvel próprio",
]


def _birth(p: dict[str, Any]) -> date:
    return date.fromisoformat(p["data_nascimento"])


def _end_date(p: dict[str, Any], today: date) -> date:
    if p.get("data_obito"):
        return min(today, date.fromisoformat(p["data_obito"]))
    return today


def _make_endereco(
    key: str,
    rng: SeededRNG,
    geo: GeographyEngine,
    class_label: str,
    city_name: str | None = None,
    uf: str | None = None,
) -> dict[str, Any]:
    city = next((c for c in CITY_SET if c["name"] == city_name), None)
    if city is None:
        city = geo.city_for_class(class_label)
    bairro = geo.neighborhood_for(city["city_id"], class_label)
    end_id = str(uuid5(NAMESPACE_URL, f"end-{key}"))
    cep_prefix = 10000 + int.from_bytes(hashlib.sha256(key.encode()).digest(), "big") % 89999
    cep_suffix = 100 + int.from_bytes(hashlib.sha256(end_id.encode()).digest(), "big") % 899
    return {
        "id": end_id,
        "logradouro_ficticio": str(rng.choice(_LOGRADOUROS)),
        "numero": str(rng.integer(10, 2500)),
        "bairro": bairro["name"],
        "cidade_ficticia": city["name"],
        "uf": (uf or city["uf"])[:2],
        "cep_ficticio": f"{cep_prefix:05d}-{cep_suffix:03d}",
    }


def generate(
    personas: list[dict[str, Any]],
    seed: int = 7,
    today: date | None = None,
    existing_tables: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Gera todas as tabelas do domínio 07 (Residência)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "endereco": [],
        "residencia": [],
        "historico_residencia": [],
        "condominio": [],
        "taxa_condominio": [],
        "vizinho": [],
        "contrato_aluguel": [],
        "financiamento_imobiliario": [],
    }

    enderecos_by_city: dict[str, list[ tuple[str, str] ]] = {}
    rental_imoveis: list[str] = []
    if existing_tables and existing_tables.get("imovel"):
        rental_imoveis = [im["id"] for im in existing_tables["imovel"]]

    for p in personas:
        rng = master.fork(p["id"], "gen07-residencia")
        geo = GeographyEngine(rng)
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)
        cls = p["classe_social"]

        # Endereço inicial (infância/família)
        end_orig = _make_endereco(
            f"{p['id']}-orig",
            rng,
            geo,
            cls,
            city_name=p.get("cidade_nascimento"),
            uf=p.get("uf_nascimento"),
        )
        rows["endereco"].append(end_orig)

        leave_mu = 23.0 if cls in ("A", "B1", "B2") else 20.0
        leave_sigma = 4.0 if cls in ("A", "B1", "B2") else 3.0
        leave_age = round(rng.normal_clipped(leave_mu, leave_sigma, 18.0, 32.0))

        if age > leave_age and (end - (born + timedelta(days=leave_age * 365))).days >= 60:
            dt_saida_pais = born + timedelta(days=leave_age * 365)
            rows["historico_residencia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"histres-{p['id']}-0")),
                "pessoa_id": p["id"],
                "endereco_id": end_orig["id"],
                "data_entrada": born.isoformat(),
                "data_saida": dt_saida_pais.isoformat(),
                "motivo_mudanca": str(rng.choice(_MOTIVOS_MUDANCA)),
            })

            # Avalia migração para outra cidade
            mig_p = geo.migration_prob(age, cls, 1.2 if not p.get("desempregado") else 0.8)
            if rng.bernoulli(mig_p):
                end_atual = _make_endereco(f"{p['id']}-atual", rng, geo, cls)
                p["cidade_residencia"] = end_atual["cidade_ficticia"]
            else:
                end_atual = _make_endereco(
                    f"{p['id']}-atual",
                    rng,
                    geo,
                    cls,
                    city_name=p.get("cidade_nascimento"),
                    uf=p.get("uf_nascimento"),
                )
            rows["endereco"].append(end_atual)
            dt_entrada_atual = dt_saida_pais
        else:
            end_atual = end_orig
            dt_entrada_atual = born

        # Determina tipo de posse coerente com finanças
        if p.get("financiamento_imovel_id") and p.get("imovel_proprio_id"):
            tipo_posse = "financiado"
        elif p.get("imovel_proprio_id"):
            tipo_posse = "proprio"
        elif age < leave_age:
            tipo_posse = "cedido"
        else:
            tipo_posse = "alugado"

        res_id = str(uuid5(NAMESPACE_URL, f"res-{p['id']}"))
        rows["residencia"].append({
            "id": res_id,
            "pessoa_id": p["id"],
            "endereco_id": end_atual["id"],
            "tipo_posse": tipo_posse,
            "data_entrada": dt_entrada_atual.isoformat(),
        })
        p["residencia_atual_id"] = res_id
        p["endereco_atual_id"] = end_atual["id"]
        enderecos_by_city.setdefault(end_atual["cidade_ficticia"], []).append((p["id"], end_atual["id"]))

        # Condomínio e taxa condominial
        if cls in ("A", "B1", "B2", "C1") and rng.bernoulli(0.45):
            cond_id = str(uuid5(NAMESPACE_URL, f"cond-{end_atual['id']}"))
            rows["condominio"].append({
                "id": cond_id,
                "nome": f"Condomínio Residencial {end_atual['bairro']}",
                "endereco_id": end_atual["id"],
                "numero_unidades": rng.integer(24, 160),
            })
            rows["taxa_condominio"].append({
                "id": str(uuid5(NAMESPACE_URL, f"taxacond-{res_id}")),
                "residencia_id": res_id,
                "mes_referencia": date(end.year, end.month, 1).isoformat(),
                "valor": round(rng.uniform(280.0, 1450.0), 2),
            })

        # Vincula financiamento_imobiliario se houver imóvel financiado
        if p.get("imovel_proprio_id") and p.get("financiamento_imovel_id"):
            rows["financiamento_imobiliario"].append({
                "id": str(uuid5(NAMESPACE_URL, f"finimob-{p['id']}")),
                "pessoa_id": p["id"],
                "imovel_id": p["imovel_proprio_id"],
                "financiamento_id": p["financiamento_imovel_id"],
            })

        # Contrato de aluguel se alugado e houver imóvel disponível no catálogo
        if tipo_posse == "alugado" and rental_imoveis and (end - dt_entrada_atual).days >= 30:
            imv_alugado_id = str(rng.choice(rental_imoveis))
            alug_fim = end
            if alug_fim <= dt_entrada_atual:
                alug_fim = dt_entrada_atual + timedelta(days=365)
            rows["contrato_aluguel"].append({
                "id": str(uuid5(NAMESPACE_URL, f"alug-{p['id']}")),
                "pessoa_id": p["id"],
                "imovel_id": imv_alugado_id,
                "valor_mensal": round(rng.uniform(850.0, 3600.0), 2),
                "data_inicio": dt_entrada_atual.isoformat(),
                "data_fim": alug_fim.isoformat(),
            })

    # Preenche endereco_id em imóveis existentes se disponível
    if existing_tables and existing_tables.get("imovel"):
        end_by_person = {p["id"]: p.get("endereco_atual_id") for p in personas}
        for imv in existing_tables["imovel"]:
            owner_id = imv.get("proprietario_pessoa_id")
            if owner_id and end_by_person.get(owner_id):
                imv["endereco_id"] = end_by_person[owner_id]

    # Vizinhos na mesma cidade/bairro
    for plist in enderecos_by_city.values():
        if len(plist) >= 2:
            for idx in range(min(len(plist) - 1, 6)):
                pa, end_a = plist[idx]
                pb, _end_b = plist[idx + 1]
                if pa != pb:
                    rows["vizinho"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"viz-{pa}-{pb}")),
                        "pessoa_id_a": pa,
                        "pessoa_id_b": pb,
                        "endereco_id": end_a,
                        "periodo_convivencia": "2022-2026",
                    })

    return rows
