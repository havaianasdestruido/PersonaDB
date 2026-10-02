"""Testes unitários do motor genético `GeneticEngine` (TASK-091).

Verifica:
- Punnett ABO: `O x O` só gera `O`; `A x O` gera `A` ou `O`; `AB x O` gera `A` ou `B`.
- Punnett Rh: `negativo x negativo` só gera `negativo`.
- Cor dos olhos: `azul x azul` nunca gera `castanho`.
- Lateralidade: `P(canhoto | ambos canhotos) > P(canhoto | nenhum canhoto)`.
- Altura: filhos de pais altos são maiores que filhos de pais baixos em média.
"""
from __future__ import annotations

from persona_db.engines.genetics import GeneticEngine
from persona_db.engines.rng import SeededRNG


def test_punnett_abo_combinations() -> None:
    """Verifica quadrados de Punnett ABO para O x O, A x O e AB x O."""
    oo = GeneticEngine.punnett_abo("O", "O")
    assert set(oo.keys()) == {"O"}
    assert abs(oo["O"] - 1.0) < 1e-9

    ao = GeneticEngine.punnett_abo("A", "O")
    assert set(ao.keys()) == {"A", "O"}
    assert ao["A"] > 0.0 and ao["O"] > 0.0

    abo_o = GeneticEngine.punnett_abo("AB", "O")
    assert set(abo_o.keys()) == {"A", "B"}
    assert abs(abo_o["A"] - 0.5) < 1e-9
    assert abs(abo_o["B"] - 0.5) < 1e-9


def test_punnett_rh_negative_parents() -> None:
    """Pais ambos Rh negativo só podem gerar filho Rh negativo."""
    rh = GeneticEngine.rh_punnett("negativo", "negativo")
    assert rh["negativo"] == 1.0
    assert rh["positivo"] == 0.0

    engine = GeneticEngine(SeededRNG(101))
    for _ in range(50):
        blood = engine.herdar_tipo_sanguineo("O", "O", "negativo", "negativo")
        assert blood == "O-"


def test_eye_color_blue_parents_never_brown() -> None:
    """Dois pais de olhos azuis ('b', 'b') nunca geram filho de olhos castanhos."""
    chart = GeneticEngine.eye_color_chart(("b", "b"), ("b", "b"))
    assert chart.get("castanho", 0.0) == 0.0
    assert chart.get("azul", 0.0) == 1.0

    engine = GeneticEngine(SeededRNG(202))
    for _ in range(100):
        pheno = engine.draw_eye_color(("b", "b"), ("b", "b"))
        assert pheno != "castanho"


def test_handedness_probability_monotonic() -> None:
    """P(canhoto | ambos canhotos) > P(canhoto | 1 canhoto) > P(canhoto | nenhum canhoto)."""
    p_both = GeneticEngine.handedness_prob(True, True)
    p_father = GeneticEngine.handedness_prob(True, False)
    p_mother = GeneticEngine.handedness_prob(False, True)
    p_none = GeneticEngine.handedness_prob(False, False)

    assert p_both > p_father > p_none
    assert p_both > p_mother > p_none


def test_child_height_inherits_parental_stature() -> None:
    """Filhos de pais altos (188/175 cm) têm média superior a filhos de pais baixos (162/150 cm)."""
    rng_tall = GeneticEngine(SeededRNG(303))
    rng_short = GeneticEngine(SeededRNG(303))

    tall_children = [rng_tall.expected_child_height(188.0, 175.0, "M") for _ in range(300)]
    short_children = [rng_short.expected_child_height(162.0, 150.0, "M") for _ in range(300)]

    assert (sum(tall_children) / len(tall_children)) > (sum(short_children) / len(short_children)) + 15.0
