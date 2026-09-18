"""Geografia ficcional: cidades, bairros e mobilidade espacial.

Owned by Agent 3. Tudo aqui é fictício; nenhum dado real é usado.
"""
from __future__ import annotations

from typing import Any

try:  # pragma: no cover - fallback stub
    from .rng import SeededRNG
except Exception:  # pragma: no cover
    SeededRNG = object

# Roteiro de distribuição regional aproximada do Brasil
_REGION_SPLIT = {"SE": 0.43, "NE": 0.27, "S": 0.15, "N": 0.08, "CO": 0.07}

_UF_BY_REGION = {
    "N": ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
    "NE": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "CO": ["DF", "GO", "MS", "MT"],
    "SE": ["ES", "MG", "RJ", "SP"],
    "S": ["PR", "RS", "SC"],
}

_CITY_ROOT = [
    "Alvorada", "Porto", "Vale", "Serra", "Boa", "Vista", "Lagoa", "Monte",
    "Carmo", "São", "Santo", "Bela", "Pontal", "Campo", "Rio", "Nova",
    "Alto", "Santa", "Flor", "Pedra", "Águas", "Castelo", "Jardim", "Terra",
]

_CITY_MOD = [
    "Nova", "Leste", "Oeste", "Serena", "Azul", "Clara", "Dourada", "Brava",
    "Real", "Verde", "Grande", "Mirim", "Bonita", "Alta", "Fria", "Quente",
    "Flores", "Bela", "Vermelha", "Perdida", "Luminosa", "das Águas", "do Sul",
    "da Serra", "de Deus", "do Norte", "Feliz", "Antiga", "Prata", "Ouro",
]

_SURNAMES_CITY = [
    "Gama", "Brandão", "Ferreira", "Mendes", "Barros", "Cardoso", "Lima",
    "Rocha", "Prado", "Neves", "Castro", "Moreira", "Azevedo", "Guerra",
]

_REGION_ID = {"N": 1, "NE": 2, "CO": 3, "SE": 4, "S": 5}

_BAIRRO_STEM = [
    "Centro", "Jardim", "Vila", "Bela", "Alto", "Bosque", "Lagoa", "Parque",
    "Industrial", "Residencial", "Universitário", "Comercial",
]


def _build_city_set() -> list[dict[str, Any]]:
    """Gera ~50 cidades fictícias determinísticas."""
    cities: list[dict[str, Any]] = []
    idx = 0
    target = [("SE", 22), ("NE", 13), ("S", 8), ("N", 4), ("CO", 3)]
    pop_seed = [1_200_000, 860_000, 540_000, 890_000, 310_000, 470_000, 780_000, 260_000]
    for region, count in target:
        ufs = _UF_BY_REGION[region]
        for i in range(count):
            nome = f"{_CITY_ROOT[(idx + i) % len(_CITY_ROOT)]} {_CITY_MOD[(idx * 3 + i) % len(_CITY_MOD)]}".strip()
            if region == "S":
                nome += f" {_SURNAMES_CITY[i % len(_SURNAMES_CITY)]}"
            pop = pop_seed[(idx + i) % len(pop_seed)] * (0.7 + ((idx * 7 + i) % 10) / 10.0) * 1000

            classe = {
                "A": round(0.06 if region in ("S",) else 0.03, 3),
                "B1": round(0.10 if region in ("S",) else 0.07, 3),
                "B2": round(0.18 if region in ("SE", "S") else 0.14, 3),
                "C1": round(0.24 if region in ("SE",) else 0.21, 3),
                "C2": round(0.23 if region in ("SE", "S") else 0.25, 3),
            }
            classe["D_E"] = round(1.0 - sum(classe.values()), 3)
            crime = (_REGION_ID[region] * 11 + idx * 37) % 100
            cities.append({
                "city_id": f"CID-{idx + 1:03d}",
                "name": nome,
                "uf": ufs[i % len(ufs)],
                "region": region,
                "population": int(pop),
                "base_class_dist": classe,
                "cost_of_living": round(1.0 + (idx % 5) * 0.18, 2),
                "crime_index": int(crime),
                "university_count": 1 + (idx % 4),
            })
            idx += 1
    return cities


def _build_neighborhoods(cities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """~10 bairros por cidade -> ~500 bairros com perfil socioeconômico."""
    bairros: list[dict[str, Any]] = []
    nid = 0
    for city in cities:
        n_neigh = 8 + (city["population"] // 250_000) % 4
        base_class = city["base_class_dist"]
        classes = [c for c in base_class if base_class[c] > 0.05] or ["C1"]
        for i in range(n_neigh):
            nome = f"{_BAIRRO_STEM[i % len(_BAIRRO_STEM)]} {i + 1}"
            crime = (city["crime_index"] + (i * 13) % 40) // 2 % 100
            school = max(0, min(10, 10 - abs(5 - (i % 9))))
            health = max(0, min(10, 7 - (i % 5) // 2))
            profile = classes[i % len(classes)]
            bairros.append({
                "neighborhood_id": f"BAI-{nid + 1:04d}",
                "city_id": city["city_id"],
                "name": nome,
                "class_profiles": [profile],
                "crime_level": int(crime),
                "school_quality": int(school),
                "health_quality": int(health),
            })
            nid += 1
    return bairros


CITY_SET: list[dict[str, Any]] = _build_city_set()
NEIGHBORHOODS: list[dict[str, Any]] = _build_neighborhoods(CITY_SET)


class GeographyEngine:
    """Mobilidade espacial e correlação bairro <-> classe social."""

    def __init__(self, rng: SeededRNG):
        self._rng = rng

    @staticmethod
    def _class_weight(city: dict, class_label: str) -> float:
        dist = city.get("base_class_dist", {})
        return max(0.01, dist.get(class_label, 0.03))

    def city_for_class(self, class_label: str) -> dict:
        """Cidade ponderada pela população e adequação de classe."""
        weights = [c["population"] * self._class_weight(c, class_label) for c in CITY_SET]
        return self._rng.choice(CITY_SET, weights=weights)

    def neighborhood_for(self, city_id: str, class_label: str) -> dict:
        """Bairro compatível com a classe na cidade."""
        candidates = [b for b in NEIGHBORHOODS if b["city_id"] == city_id]
        if not candidates:
            return NEIGHBORHOODS[self._rng.integer(0, len(NEIGHBORHOODS) - 1)]
        pool = [b for b in candidates if class_label in b["class_profiles"]] or candidates
        return self._rng.choice(pool)

    @staticmethod
    def gravity_model(pop_i: float, pop_j: float, distance_km: float, k: float = 1e-3) -> float:
        """Gravity model: fluxo_ij = k * pop_i * pop_j / dist²."""
        if distance_km <= 0.5:
            distance_km = 0.5
        return k * pop_i * pop_j / (distance_km ** 2)

    def migration_prob(self, age: float, class_label: str, job_opportunity_ratio: float = 1.0) -> float:
        """Probabilidade de migração para outra cidade."""
        base = 0.03
        if 18 <= age <= 35:
            base += 0.05
        if class_label in ("A", "B1"):
            base += 0.02
        if class_label in ("C2", "D_E"):
            base -= 0.01
        base *= max(0.5, job_opportunity_ratio)
        return max(0.01, min(0.5, base))


def city_summary() -> dict:
    return {
        "n_cidades": len(CITY_SET),
        "n_bairros": len(NEIGHBORHOODS),
        "regioes": sorted({c["region"] for c in CITY_SET}),
        "ufs": sorted({c["uf"] for c in CITY_SET}),
    }