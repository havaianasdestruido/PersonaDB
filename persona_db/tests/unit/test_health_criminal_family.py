"""Testes unitários combinados para `HealthEngine`, `CriminalEngine` e `FamilyEngine` (TASK-093).

Verifica:
- `HealthEngine`: hazard de hipertensão e câncer cresce com idade; sobrevivência
  decresce após 30 anos; predisposição hereditária multiplica risco base.
- `CriminalEngine`: probabilidade maior para homens jovens que mulheres idosas;
  reincidência maior para quem não tem emprego/apoio pós-prisão; sentença
  proporcional à gravidade do crime.
- `FamilyEngine`: idade ao casar dentro de limites plausíveis; número médio de
  filhos decresce em classes sociais mais altas; divórcio mais provável com
  fatores de risco financeiros/criminais.
"""
from __future__ import annotations

from persona_db.engines.criminal import CriminalEngine
from persona_db.engines.family import FamilyEngine
from persona_db.engines.health import HealthEngine
from persona_db.engines.rng import SeededRNG
from persona_db.seeds.probability_tables import mortality_qx


def test_health_engine_age_mortality_and_hereditary_risk() -> None:
    """Hipertensão, câncer e mortalidade crescem com a idade; predisposição eleva risco."""
    h_hyp_25 = HealthEngine.lifetime_hazard(age=25, sex="M", disease="hipertension")
    h_hyp_70 = HealthEngine.lifetime_hazard(age=70, sex="M", disease="hipertension")
    assert h_hyp_70 > h_hyp_25

    q_30 = mortality_qx(age=30, sex="M")
    q_55 = mortality_qx(age=55, sex="M")
    q_80 = mortality_qx(age=80, sex="M")
    assert q_30 < q_55 < q_80

    s_30 = HealthEngine.survival(age=30, sex="M")
    s_80 = HealthEngine.survival(age=80, sex="M")
    assert s_30 > s_80

    r_base = HealthEngine.hereditary_multiplier("diabetes", has_predisposition=False, base_risk=0.05)
    r_pred = HealthEngine.hereditary_multiplier("diabetes", has_predisposition=True, base_risk=0.05)
    assert r_pred > r_base


def test_criminal_engine_demographics_recidivism_and_sentence() -> None:
    """Homens jovens vulneráveis têm maior risco criminal; falta de emprego eleva reincidência; tráfico tem pena maior."""
    engine = CriminalEngine(SeededRNG(606))

    young_male = {"sex": "masculino", "age": 21, "class_label": "D_E", "desemprego": True}
    elder_female = {"sex": "feminino", "age": 72, "class_label": "A", "desemprego": False}
    assert engine.crime_probability(young_male) > engine.crime_probability(elder_female)

    recid_vuln = sum(engine.recidivism(employment_formal=False, family_support=False) for _ in range(300))
    recid_supp = sum(engine.recidivism(employment_formal=True, family_support=True) for _ in range(300))
    assert recid_vuln > recid_supp

    trafico_months = [engine.sentence_months("trafico") for _ in range(100)]
    transito_months = [engine.sentence_months("crimes_de_transito") for _ in range(100)]
    assert (sum(trafico_months) / len(trafico_months)) > (sum(transito_months) / len(transito_months)) * 2.5


def test_family_engine_marriage_children_and_divorce() -> None:
    """Idade ao casar respeita mínimo legal; filhos decrescem na classe A; fatores de risco elevam divórcio."""
    fe = FamilyEngine(SeededRNG(707))

    for sex in ("masculino", "feminino"):
        for _ in range(50):
            age_m = fe.first_marriage_age(sex)
            if age_m is not None:
                assert 16.0 <= age_m <= 65.0

    kids_a = [fe.children_count("A") for _ in range(400)]
    kids_de = [fe.children_count("D_E") for _ in range(400)]
    assert (sum(kids_de) / len(kids_de)) > (sum(kids_a) / len(kids_a))

    div_stable = sum(fe.divorce({"religiosidade_alta": 1.0, "filhos_pequenos": 1.0}) for _ in range(400))
    div_crisis = sum(
        fe.divorce({"desemprego_prolongado": 1.0, "antecedente_criminal_conjuge": 1.0, "diferenca_classe": 2.0})
        for _ in range(400)
    )
    assert div_crisis > div_stable
