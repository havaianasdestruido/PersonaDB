"""Tabelas de probabilidade calibradas usadas pelos motores.

Owned by Agent 5. 100% determinístico (sem random); toda calibração é
feita por construção programática com fórmulas fechadas ou tabelas fixas.
Consumido por engines/ (socio, health, criminal, genetics) e generators/.
"""
from __future__ import annotations

# Classes socioeconômicas (alinhadas a engines/constants.py e socio.py).
SOCIAL_CLASSES: list[str] = ["A", "B1", "B2", "C1", "C2", "D_E"]

# Faixas etárias canônicas (anos) usadas nas tabelas de risco/emprego.
AGE_BANDS: list[tuple[int, int]] = [
    (0, 4), (5, 9), (10, 14), (15, 19), (20, 24), (25, 29), (30, 34),
    (35, 39), (40, 44), (45, 49), (50, 54), (55, 59), (60, 64), (65, 69),
    (70, 74), (75, 79), (80, 120),
]

# --------------------------------------------------------------------------- #
# 1. Matriz de mobilidade social intergeracional (6x6).
#    P(classe_filho | classe_pai). Cada linha soma 1.0. Diagonais 0.55-0.65.
# --------------------------------------------------------------------------- #
SOCIAL_MOBILITY_MATRIX: list[list[float]] = [
    [0.62, 0.20, 0.10, 0.05, 0.02, 0.01],  # pai A
    [0.08, 0.55, 0.22, 0.10, 0.03, 0.02],  # pai B1
    [0.03, 0.10, 0.58, 0.20, 0.06, 0.03],  # pai B2
    [0.01, 0.04, 0.12, 0.56, 0.18, 0.09],  # pai C1
    [0.01, 0.02, 0.06, 0.16, 0.57, 0.18],  # pai C2
    [0.01, 0.01, 0.04, 0.10, 0.24, 0.60],  # pai D_E
]
SOCIAL_MOBILITY_MATRIX = [  # normaliza linhas defensivamente
    [round(x / sum(row), 4) for x in row]
    for row in SOCIAL_MOBILITY_MATRIX
]

# --------------------------------------------------------------------------- #
# 2. Tábua de vida (tábua de mortalidade) por idade e sexo.
#    qx = probabilidade anual de óbito na idade exata `idade`.
#    Construída analiticamente com uma curva de mortalidade em forma de J:
#      qx(0) alto (mortalidade infantil), cai até ~10 anos, sobe monotônico.
#    Mulheres têm força de mortalidade ~20% menor na pós-menopausa.
# --------------------------------------------------------------------------- #

_MALE_BASE = 0.055   # qx no primeiro ano
_FEMALE_BASE = 0.047
_MAX_AGE = 110


def _qx_for_age(age: int, sex: str) -> float:
    """Hazard rate anual (qx) aproximado para idade exata *age* e sexo."""
    if age < 0:
        return 0.0
    female = sex == "F"
    base = _FEMALE_BASE if female else _MALE_BASE
    if age == 0:
        q = base
    elif age == 1:
        q = base * 0.22
    elif age <= 4:
        q = base * (0.10 - 0.012 * (age - 1))
    elif age <= 9:
        q = 0.0009 + 0.00008 * age
    elif age <= 14:
        q = 0.0012 + 0.0001 * age
    elif age <= 24:
        q = 0.0022 + 0.00018 * (age - 14)
    elif age <= 34:
        q = 0.0048 + 0.00028 * (age - 24)
    elif age <= 44:
        q = 0.0075 + 0.00055 * (age - 34)
    elif age <= 54:
        q = 0.0130 + 0.0013 * (age - 44)
    elif age <= 64:
        q = 0.0260 + 0.0024 * (age - 54)
    elif age <= 74:
        q = 0.0500 + 0.0054 * (age - 64)
    elif age <= 84:
        q = 0.1100 + 0.0110 * (age - 74)
    elif age <= 94:
        q = 0.2300 + 0.0220 * (age - 84)
    else:
        q = 0.4600 + 0.0300 * (age - 94)
    if female and age >= 50:
        q *= 0.82
    q = max(0.0, min(q, 0.999))
    return round(q, 5)


MORTALITY_TABLE: dict[str, list[float]] = {
    "M": [_qx_for_age(a, "M") for a in range(_MAX_AGE + 1)],
    "F": [_qx_for_age(a, "F") for a in range(_MAX_AGE + 1)],
}

# Helper de consulta.
def mortality_qx(age: int, sex: str) -> float:
    """Probabilidade anual de óbito para idade/sexo (tábua de vida)."""
    a = max(0, min(int(age), _MAX_AGE))
    return MORTALITY_TABLE[sex][a] if sex in MORTALITY_TABLE else 0.0


# --------------------------------------------------------------------------- #
# 3. Distribuição de doenças por faixa etária e sexo (incidência anual base).
#    Chaves alinhadas a engines/constants.py DISEASE_TRANCHES.
#    Cada doenca: {faixa_a: taxa} — uso principal 35-64 anos.
# --------------------------------------------------------------------------- #
DISEASE_BY_AGE_SEX: dict[str, dict[str, dict[str, float]]] = {
    "diabetes": {
        "M": {"0-14": 0.0002, "15-34": 0.0012, "35-54": 0.0120, "55-79": 0.0320, "80+": 0.0450},
        "F": {"0-14": 0.0002, "15-34": 0.0010, "35-54": 0.0100, "55-79": 0.0280, "80+": 0.0420},
    },
    "hipertension": {
        "M": {"0-14": 0.0001, "15-34": 0.0040, "35-54": 0.0240, "55-79": 0.0700, "80+": 0.1200},
        "F": {"0-14": 0.0001, "15-34": 0.0030, "35-54": 0.0190, "55-79": 0.0620, "80+": 0.1100},
    },
    "depression": {
        "M": {"0-14": 0.0020, "15-34": 0.0180, "35-54": 0.0160, "55-79": 0.0100, "80+": 0.0080},
        "F": {"0-14": 0.0020, "15-34": 0.0310, "35-54": 0.0290, "55-79": 0.0180, "80+": 0.0140},
    },
    "cancer": {
        "M": {"0-14": 0.0003, "15-34": 0.0012, "35-54": 0.0045, "55-79": 0.0180, "80+": 0.0400},
        "F": {"0-14": 0.0003, "15-34": 0.0015, "35-54": 0.0060, "55-79": 0.0160, "80+": 0.0360},
    },
}

_DISEASE_AGE_TABLE = [
    ("0-14", 0, 14), ("15-34", 15, 34), ("35-54", 35, 54),
    ("55-79", 55, 79), ("80+", 80, 200),
]


def disease_incidence(disease: str, age: int, sex: str) -> float:
    """Taxa anual base de incidência para doença/idade/sexo."""
    tbl = DISEASE_BY_AGE_SEX.get(disease, {}).get(sex, {})
    if not tbl:
        return 0.0
    for band, lo, hi in _DISEASE_AGE_TABLE:
        if lo <= int(age) <= hi:
            return tbl.get(band, 0.0)
    return tbl.get("80+", 0.0)


# --------------------------------------------------------------------------- #
# 4. Distribuição de crimes por perfil demográfico.
#    {tipo_crime: {sexo: {faixa: taxa_anual_per_capita}}}  (aprox.)
# --------------------------------------------------------------------------- #
CRIME_BY_PROFILE: dict[str, dict[str, dict[str, float]]] = {
    "furto": {
        "M": {"15-19": 0.030, "20-29": 0.045, "30-44": 0.028, "45+": 0.010},
        "F": {"15-19": 0.008, "20-29": 0.012, "30-44": 0.008, "45+": 0.003},
    },
    "roubo": {
        "M": {"15-19": 0.020, "20-29": 0.035, "30-44": 0.018, "45+": 0.006},
        "F": {"15-19": 0.005, "20-29": 0.009, "30-44": 0.005, "45+": 0.002},
    },
    "trafico": {
        "M": {"15-19": 0.012, "20-29": 0.022, "30-44": 0.010, "45+": 0.002},
        "F": {"15-19": 0.002, "20-29": 0.004, "30-44": 0.002, "45+": 0.001},
    },
    "homicidio": {
        "M": {"15-19": 0.011, "20-29": 0.017, "30-44": 0.008, "45+": 0.002},
        "F": {"15-19": 0.001, "20-29": 0.002, "30-44": 0.001, "45+": 0.0005},
    },
    "estelionato": {
        "M": {"15-19": 0.002, "20-29": 0.006, "30-44": 0.010, "45+": 0.014},
        "F": {"15-19": 0.001, "20-29": 0.004, "30-44": 0.007, "45+": 0.010},
    },
    "violencia_domestica": {
        "M": {"15-19": 0.003, "20-29": 0.018, "30-44": 0.016, "45+": 0.008},
        "F": {"15-19": 0.001, "20-29": 0.006, "30-44": 0.005, "45+": 0.003},
    },
}

_CRIME_AGE_BANDS = [("15-19", 15, 19), ("20-29", 20, 29), ("30-44", 30, 44), ("45+", 45, 200)]


def crime_rate(crime: str, sexo: str, idade: int) -> float:
    """Taxa anual per capita para tipo de crime/sexo/idade."""
    tbl = CRIME_BY_PROFILE.get(crime, {}).get(sexo, {})
    if not tbl:
        return 0.0
    for band, lo, hi in _CRIME_AGE_BANDS:
        if lo <= int(idade) <= hi:
            return tbl.get(band, 0.0)
    return tbl.get("45+", 0.0)


# --------------------------------------------------------------------------- #
# 5. Taxas de emprego por setor / escolaridade / faixa etária.
#    EMPLOYMENT_RATES[setor][escolaridade][faixa] = P(empregado).
# --------------------------------------------------------------------------- #
_SECTOR_JOBS = ["aberto", "agro", "comercio", "construcao", "educacao",
                "saude", "industria", "tecnologia", "financeiro", "publico"]
_EDU_LEVELS = ["fundamental", "medio", "superior", "pos"]

# Parâmetros (intercepto + incremento por escolaridade) por setor.
_SECTOR_EMPLOYMENT_BASE: dict[str, float] = {
    "aberto": 0.55, "agro": 0.58, "comercio": 0.60, "construcao": 0.62,
    "educacao": 0.72, "saude": 0.74, "industria": 0.70, "tecnologia": 0.80,
    "financeiro": 0.78, "publico": 0.88,
}
_EDU_BOOST: dict[str, float] = {
    "fundamental": -0.08, "medio": 0.00, "superior": 0.12, "pos": 0.18,
}
# Multiplicador de idade relativo à faixa-âncora (25-54).
_AGE_EMPLOYMENT_FACTOR = {
    "15-17": 0.30, "18-24": 0.80, "25-34": 1.00, "35-44": 1.00,
    "45-54": 0.92, "55-64": 0.70, "65+": 0.35,
}
_EMPLOYMENT_AGE_BANDS = [
    ("15-17", 15, 17), ("18-24", 18, 24), ("25-34", 25, 34),
    ("35-44", 35, 44), ("45-54", 45, 54), ("55-64", 55, 64), ("65+", 65, 200),
]

EMPLOYMENT_RATES: dict[str, dict[str, dict[str, float]]] = {
    sector: {
        edu: {
            band: round(
                max(0.02, min(0.97, (_SECTOR_EMPLOYMENT_BASE[sector] + _EDU_BOOST[edu])
                              * _AGE_EMPLOYMENT_FACTOR[band])),
                3,
            )
            for band, _, _ in _EMPLOYMENT_AGE_BANDS
        }
        for edu in _EDU_LEVELS
    }
    for sector in _SECTOR_JOBS
}


def employment_rate(sector: str, education: str, age: int) -> float:
    """P(empregado) para setor/escolaridade/idade."""
    sec = EMPLOYMENT_RATES.get(sector, EMPLOYMENT_RATES["aberto"])
    edu = sec.get(education, sec["medio"])
    for band, lo, hi in _EMPLOYMENT_AGE_BANDS:
        if lo <= int(age) <= hi:
            return edu.get(band, 0.5)
    return edu.get("65+", 0.5)


# --------------------------------------------------------------------------- #
# 6. Distribuição de renda por percentil (curva de Lorenz fictícia).
#    GINI ≈ 0.52 (proxy brasileira). INCOME_DIST[i] = participação acumulada
#    no renda até o percentil i (i de 0 a 100).
# --------------------------------------------------------------------------- #
_GINI = 0.52


def _lorenz_curve(gini: float, n: int = 100) -> list[float]:
    """Curva de Lorenz discreta L(x) = x - gini * (x - x^2) normalizada."""
    out = []
    for i in range(n + 1):
        x = i / n
        y = x - gini * (x - x * x)
        out.append(round(y, 6))
    scale = out[-1]
    if scale > 0:
        out = [round(v / scale, 6) for v in out]
    out[-1] = 1.0
    return out


INCOME_DIST: list[float] = _lorenz_curve(_GINI, 100)


def income_share_percentile(p: float) -> float:
    """Participação acumulada da renda até o percentil *p* (0-100)."""
    idx = max(0, min(100, int(round(p))))
    return INCOME_DIST[idx]


# --------------------------------------------------------------------------- #
# 7. Matriz ancestralidade → traços físicos prováveis.
#    ANCESTRY_TO_TRAITS[ancestria] = {traco: {opcao: probabilidade}}
# --------------------------------------------------------------------------- #
ANCESTRY_TO_TRAITS: dict[str, dict[str, dict[str, float]]] = {
    "europeia": {
        "cor_olhos": {"castanho": 0.52, "verde": 0.13, "azul": 0.22, "preto": 0.13},
        "cor_cabelo": {"castanho": 0.60, "preto": 0.20, "loiro": 0.16, "ruivo": 0.04},
        "pele": {"branca": 0.80, "parda": 0.16, "negra": 0.03, "amarela": 0.01},
    },
    "africana": {
        "cor_olhos": {"castanho": 0.08, "preto": 0.92, "verde": 0.00, "azul": 0.00},
        "cor_cabelo": {"preto": 0.95, "castanho": 0.05, "loiro": 0.00, "ruivo": 0.00},
        "pele": {"negra": 0.85, "parda": 0.14, "branca": 0.01, "amarela": 0.00},
    },
    "indigena": {
        "cor_olhos": {"preto": 0.90, "castanho": 0.10, "verde": 0.00, "azul": 0.00},
        "cor_cabelo": {"preto": 0.98, "castanho": 0.02, "loiro": 0.00, "ruivo": 0.00},
        "pele": {"parda": 0.65, "amarela": 0.30, "negra": 0.04, "branca": 0.01},
    },
    "asiatica": {
        "cor_olhos": {"preto": 0.75, "castanho": 0.25, "verde": 0.00, "azul": 0.00},
        "cor_cabelo": {"preto": 0.97, "castanho": 0.03, "loiro": 0.00, "ruivo": 0.00},
        "pele": {"amarela": 0.72, "parda": 0.25, "branca": 0.03, "negra": 0.00},
    },
    "mista": {
        "cor_olhos": {"castanho": 0.55, "preto": 0.35, "verde": 0.07, "azul": 0.03},
        "cor_cabelo": {"castanho": 0.55, "preto": 0.40, "loiro": 0.03, "ruivo": 0.02},
        "pele": {"parda": 0.58, "branca": 0.24, "negra": 0.16, "amarela": 0.02},
    },
}


def trait_probs(ancestry: str, trait: str) -> dict[str, float]:
    """Distribuição do traço físico para determinada ancestralidade."""
    return ANCESTRY_TO_TRAITS.get(ancestry, ANCESTRY_TO_TRAITS["mista"]).get(
        trait, {}
    )


# --------------------------------------------------------------------------- #
# Autocheck (execução direta).
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    print("SOCIAL_MOBILITY rows sum:", [round(sum(r), 4) for r in SOCIAL_MOBILITY_MATRIX])
    print("MORTALITY_TABLE M len:", len(MORTALITY_TABLE["M"]), "F len:", len(MORTALITY_TABLE["F"]))
    print("  qx(0):", MORTALITY_TABLE["M"][0], "| qx(60):", MORTALITY_TABLE["M"][60],
          "| qx(90):", MORTALITY_TABLE["M"][90])
    print("DISEASE diseases:", list(DISEASE_BY_AGE_SEX))
    print("CRIME types:", list(CRIME_BY_PROFILE))
    print("EMPLOYMENT tech/medio/30:',", EMPLOYMENT_RATES["tecnologia"]["medio"]["25-34"])
    print("INCOME_DIST[0,10,50,90,100]:",
          INCOME_DIST[0], INCOME_DIST[10], INCOME_DIST[50], INCOME_DIST[90], INCOME_DIST[100])
    print("ANCESTRY traits:", {k: list(v) for k, v in ANCESTRY_TO_TRAITS.items()})
    # sanity: rows sum to ~1.0
    assert all(abs(sum(r) - 1.0) < 1e-3 for r in SOCIAL_MOBILITY_MATRIX)
    assert len(MORTALITY_TABLE["M"]) == len(MORTALITY_TABLE["F"]) == _MAX_AGE + 1
    assert INCOME_DIST[-1] == 1.0
    assert all(abs(sum(trait_probs("europeia", t).values()) - 1.0) < 1e-3 for t in ("cor_olhos", "cor_cabelo", "pele"))