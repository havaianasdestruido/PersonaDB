"""gen_00_pessoa — gera a persona base (tabela `pessoa`, domínio 00).

Owned by Agent 10. Produz dicionários deterministicamente a partir de um
seed mestre; todos os atributos são derivados dos engines (socio, health,
geography, genetics, criminal) e dos seeds.

Contrato de saída (chaves do dict persona) — consumido por gen_01, gen_02 e
pelos demais generators:

    id, nome_completo, nome_social, data_nascimento (ISO str), sexo,
    nacionalidade, cidade_nascimento, uf_nascimento, classe_social,
    estado_civil, esta_vivo, data_obito,
    education, setor_empregado, ancestry, ancestry_pcts,
    cor_olhos, cor_cabelo, pele, mao_dominante, tipo_sanguineo, fator_rh,
    altura, peso, criminal (dict do CriminalEngine), cidade_residencia
"""
from __future__ import annotations

import os
import sys
from datetime import date, datetime, timedelta
from uuid import NAMESPACE_URL, uuid5

# Permitir execução direta (python gen_00_pessoa.py) e import como pacote.
try:  # pragma: no cover
    from persona_db.engines.rng import SeededRNG, new_rng
    from persona_db.engines.socio import SocioeconomicEngine
    from persona_db.engines.geography import GeographyEngine
    from persona_db.engines.genetics import GeneticEngine
    from persona_db.engines.criminal import CriminalEngine
    from persona_db.engines.constants import BLOOD_GROUP_PRIORS
    from persona_db.seeds.lookup_data import (
        MALE_FIRST_NAMES,
        FEMALE_FIRST_NAMES,
        SURNAMES,
    )
    from persona_db.seeds.probability_tables import (
        SOCIAL_CLASSES,
        trait_probs,
        mortality_qx,
    )
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.rng import SeededRNG, new_rng
    from persona_db.engines.socio import SocioeconomicEngine
    from persona_db.engines.geography import GeographyEngine
    from persona_db.engines.genetics import GeneticEngine
    from persona_db.engines.criminal import CriminalEngine
    from persona_db.engines.constants import BLOOD_GROUP_PRIORS
    from persona_db.seeds.lookup_data import (
        MALE_FIRST_NAMES,
        FEMALE_FIRST_NAMES,
        SURNAMES,
    )
    from persona_db.seeds.probability_tables import (
        SOCIAL_CLASSES,
        trait_probs,
        mortality_qx,
    )

# ---------------------------------------------------------------------------
# Âncora temporal simulada. Determinística por padrão, sobreponível por env.
# ---------------------------------------------------------------------------
DEFAULT_TODAY = date(2026, 1, 1)


def simulation_today() -> date:
    raw = os.environ.get("PERSONADB_TODAY")
    if raw:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    return DEFAULT_TODAY


_FIRST_NAMES = {"masculino": MALE_FIRST_NAMES, "feminino": FEMALE_FIRST_NAMES}

# Pirâmide populacional fictícia: (idade_final, peso).
_AGE_PYRAMID = [
    (4, 0.06), (9, 0.065), (14, 0.07), (19, 0.075), (24, 0.08), (29, 0.08),
    (34, 0.075), (39, 0.07), (44, 0.065), (49, 0.06), (54, 0.055),
    (59, 0.05), (64, 0.045), (69, 0.04), (74, 0.035), (79, 0.025),
    (89, 0.025), (99, 0.008), (115, 0.002),
]

_ANCESTRY_PRIORS = {
    "europeia": 0.46, "mista": 0.24, "africana": 0.21,
    "indigena": 0.06, "asiatica": 0.03,
}


def sample_age(rng: SeededRNG) -> int:
    """Idade inteira varrida da pirâmide etária fictícia."""
    total = sum(w for _, w in _AGE_PYRAMID)
    roll = rng.uniform(0.0, total)
    acc = 0.0
    for hi, w in _AGE_PYRAMID:
        acc += w
        if roll <= acc:
            lo = _band_low(hi)
            return rng.integer(lo, hi) if lo < hi else hi
    return rng.integer(70, 90)


def _band_low(hi: int) -> int:
    """Menor idade da faixa que termina em *hi*."""
    if hi <= 4:
        return 0
    if hi <= 9:
        return 5
    if hi <= 14:
        return 10
    if hi <= 19:
        return 15
    if hi <= 24:
        return 20
    if hi <= 29:
        return 25
    if hi <= 34:
        return 30
    if hi <= 39:
        return 35
    if hi <= 44:
        return 40
    if hi <= 49:
        return 45
    if hi <= 54:
        return 50
    if hi <= 59:
        return 55
    if hi <= 64:
        return 60
    if hi <= 69:
        return 65
    if hi <= 74:
        return 70
    if hi <= 79:
        return 75
    if hi <= 89:
        return 80
    if hi <= 99:
        return 90
    return 100


def _estado_civil(age: int, rng: SeededRNG) -> str:
    if age < 18:
        return "solteiro"
    profile = [
        (0.08, "casado"), (0.02, "uniao_estavel"), (0.02, "divorciado"), (0.88, "solteiro"),
    ]
    if 18 <= age <= 24:
        profile = [
            (0.45, "casado"), (0.15, "uniao_estavel"), (0.02, "divorciado"),
            (0.03, "viuvo"), (0.35, "solteiro"),
        ]
    elif age <= 34:
        pass
    elif age <= 49:
        profile = [
            (0.50, "casado"), (0.12, "uniao_estavel"), (0.12, "divorciado"),
            (0.03, "viuvo"), (0.23, "solteiro"),
        ]
    elif age <= 69:
        profile = [
            (0.45, "casado"), (0.08, "uniao_estavel"), (0.13, "divorciado"),
            (0.11, "viuvo"), (0.23, "solteiro"),
        ]
    else:
        profile = [
            (0.35, "casado"), (0.05, "uniao_estavel"), (0.10, "divorciado"),
            (0.30, "viuvo"), (0.20, "solteiro"),
        ]
    labels = [l for _, l in profile]
    weights = [w for w, _ in profile]
    return str(rng.choice(labels, weights=weights))


def _dead_or_alive(age: int, sex: str, birth: date, today: date, rng: SeededRNG) -> tuple[bool, date | None]:
    """Decide vivo/óbito a partir da tábua de vida (probabilística).

    Para falecidos, a data de óbito fica entre a data de nascimento e a
    âncora temporal simulada, pesada para o fim da vida.
    """
    cum_hazard = sum(mortality_qx(a, sex) for a in range(max(0, int(age) + 1)))
    p_dead = min(0.97, 1.0 - 1.0 / (1.0 + cum_hazard * 0.45))
    if not rng.bernoulli(p_dead):
        return True, None
    span = (today - birth).days
    frac = 1.0 - rng.uniform(0.0, 0.15)
    obito = birth + timedelta(days=int(span * frac))
    return False, obito


def _build_nome(rng: SeededRNG, sexo: str) -> dict:
    names = _FIRST_NAMES[sexo]
    first = str(rng.choice(names))
    n_surnames = 2 if rng.bernoulli(0.78) else 1
    surnames = [str(rng.choice(SURNAMES)) for _ in range(n_surnames)]
    completo = " ".join([first] + surnames)
    social = None
    if rng.bernoulli(0.04):
        alt = str(rng.choice(names))
        social = " ".join([alt] + surnames)
    return {"nome_completo": completo, "nome_social": social, "ultimo_sobrenome": surnames[-1]}


def build_persona(idx: int, rng: SeededRNG, today: date, ancestor_class: str | None = None) -> dict:
    """Constrói uma persona completa (dict de contrato)."""
    sexo = "masculino" if rng.bernoulli(0.50) else "feminino"
    idade = sample_age(rng)
    dia_nasc = today - timedelta(days=int(idade * 365.25) + rng.integer(0, 364))
    estado_civil = _estado_civil(idade, rng)

    classe = SocioeconomicEngine.sample_class(rng, ancestor_class)
    educ = "fundamental"
    if idade >= 15:
        educ = SocioeconomicEngine.education_level(rng, None, 0.0, classe)

    ancestry = str(rng.choice(list(_ANCESTRY_PRIORS.keys()), weights=list(_ANCESTRY_PRIORS.values())))
    ancestry_pcts = _split_ancestry(rng, ancestry)

    ge = GeographyEngine(rng)
    geo_cls = classe if ancestry in ("europeia", "mista") else "C2"
    city = ge.city_for_class(geo_cls if geo_cls in SOCIAL_CLASSES else classe)
    cidade = str(city["name"])
    uf = str(city["uf"])

    gen = GeneticEngine(rng)

    def _trait(t: str) -> str:
        probs = trait_probs(ancestry, t)
        return str(rng.choice(list(probs.keys()), weights=list(probs.values())))

    cor_olhos = _trait("cor_olhos")
    cor_cabelo = _trait("cor_cabelo")
    pele = _trait("pele")
    mao = gen.handedness(False, False)
    mao_map = {"direita": "destra", "esquerda": "canhota", "ambidestro": "ambidestra"}
    abo = str(rng.choice(list(BLOOD_GROUP_PRIORS.keys()), weights=list(BLOOD_GROUP_PRIORS.values())))
    rh = "negativo" if rng.bernoulli(0.13) else "positivo"
    altura = rng.normal_clipped(172.0 if sexo == "masculino" else 160.0,
                                7.0 if sexo == "masculino" else 6.0, 140.0, 210.0)
    peso = gen.peso_from_height(altura, sexo)

    esta_vivo, data_obito = _dead_or_alive(idade, "M" if sexo == "masculino" else "F", dia_nasc, today, rng)

    criminal = CriminalEngine(rng).criminal_process_series({
        "sex": sexo,
        "age": idade,
        "class_label": classe,
        "education": educ,
        "income_annual": 0,
        "sector": None,
        "formal_employment": False,
        "family_support": True,
    })

    persona_id = str(uuid5(NAMESPACE_URL, f"personadb-s{idx}"))
    return {
        "id": persona_id,
        "idx": idx,
        "nome_completo": None,  # preenchido em assign_name
        "nome_social": None,
        "ultimo_sobrenome": None,
        "data_nascimento": dia_nasc.isoformat(),
        "sexo": sexo,
        "nacionalidade": _nacionalidade(rng),
        "cidade_nascimento": cidade,
        "uf_nascimento": uf,
        "classe_social": classe,
        "estado_civil": estado_civil,
        "esta_vivo": esta_vivo,
        "data_obito": data_obito.isoformat() if data_obito else None,
        "education": educ,
        "setor_empregado": None,
        "ancestry": ancestry,
        "ancestry_pcts": ancestry_pcts,
        "cor_olhos": cor_olhos,
        "cor_cabelo": cor_cabelo,
        "pele": pele,
        "mao_dominante": mao_map[mao],
        "tipo_sanguineo": abo,
        "fator_rh": rh,
        "altura": round(altura, 2),
        "peso": round(peso, 2),
        "criminal": criminal,
        "cidade_residencia": cidade,
    }


def _nacionalidade(rng: SeededRNG) -> str:
    r = rng.uniform(0.0, 1.0)
    if r < 0.03:
        return "estrangeiro"
    if r < 0.06:
        return "naturalizado"
    return "brasileira"


def _split_ancestry(rng: SeededRNG, primary: str) -> list[dict]:
    """Divide a composição ancestral em 2-3 componentes (soma 100%)."""
    parts = [primary]
    if rng.bernoulli(0.72):
        parts.append(str(rng.choice(["europeia", "africana", "indigena", "mista"])))
    if rng.bernoulli(0.18):
        parts.append(str(rng.choice(["europeia", "africana", "indigena"])))
    weights = rng.dirichlet([8.0 if p == primary else 3.0 for p in parts])
    pcts = [round(w * 100.0, 1) for w in weights]
    pcts[-1] = round(100.0 - sum(pcts[:-1]), 1)
    return [
        {"regiao_ficticia": p, "origem_percentual": v}
        for p, v in zip(parts, pcts)
        if v >= 1.0
    ]


def generate_personas(n: int, seed: int = 7, today: date | None = None) -> list[dict]:
    """Gera *n* personas completas a partir do seed mestre."""
    today = today or simulation_today()
    master = new_rng(seed)
    personas = [build_persona(i, master.fork(f"p{i}", "core"), today) for i in range(n)]
    for p in personas:
        rng = master.fork(p["id"], "nome")
        nome = _build_nome(rng, p["sexo"])
        p["nome_completo"] = nome["nome_completo"]
        p["nome_social"] = nome["nome_social"]
        p["ultimo_sobrenome"] = nome["ultimo_sobrenome"]
    return personas


if __name__ == "__main__":  # pragma: no cover
    demo = generate_personas(20, seed=42)
    ok = all(
        p["nome_completo"] and p["cidade_nascimento"] and p["classe_social"]
        for p in demo
    )
    print(f"geradas {len(demo)} personas | nomes ok={ok} | idades={[p['idx'] for p in demo[:3]]}")
    print("exemplo:", demo[0]["nome_completo"], demo[0]["sexo"],
          demo[0]["data_nascimento"], demo[0]["classe_social"])