---
title: Testes
sidebar_label: Testes
sidebar_position: 3
description: Estrutura da suíte, como rodar e como escrever bons testes determinísticos.
---

# Testes

```bash
python3 -m pytest persona_db/tests -q          # tudo
python3 -m pytest persona_db/tests/unit -q     # só unitários
python3 -m pytest persona_db/tests/statistical -q
python3 -m pytest persona_db/tests -k genetics -v
python3 -m pytest persona_db/tests --cov=persona_db --cov-report=term-missing
```

A configuração vive em `persona_db/pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --tb=short"
```

## Estrutura da suíte

| Diretório | Arquivos | Escopo |
|---|---|---|
| `tests/unit/` | `test_rng`, `test_socio`, `test_genetics`, `test_genetics_family_geo`, `test_health_criminal_family`, `test_criminal`, `test_base_engines`, `test_validators`, `test_exports`, `test_review_regressions` | Motores, validadores e exportação isolados |
| `tests/integration/` | `test_pipeline`, `test_full_generation` | Pipeline completo, 25 domínios, determinismo ponta a ponta |
| `tests/statistical/` | `test_distributions` | Agregados com N grande (médias, proporções, faixas) |

A lista completa de casos, extraída do código, está em
[Referência de API → tests/](/referencia-api/tests).

## Três categorias de asserção

### 1. Determinismo

```python
def test_mesmo_seed_mesmo_dataset():
    a = generate_all(n=20, seed=7)
    b = generate_all(n=20, seed=7)
    assert a == b          # todos os valores e IDs, não só as contagens
```

### 2. Invariantes duras

Propriedades que **nunca** podem falhar, independentemente da semente:

```python
def test_pais_rh_negativos_so_geram_filhos_rh_negativos():
    assert GeneticEngine.rh_punnett("negativo", "negativo") == {"positivo": 0.0, "negativo": 1.0}

def test_salario_respeita_piso():
    assert SocioeconomicEngine.salary(rng, "fundamental", 0, "agro", True, True) >= 1200.0
```

### 3. Propriedades estatísticas

Sobre agregados, com margens generosas para evitar testes instáveis:

```python
def test_proporcao_de_canhotos():
    canhotos = sum(1 for _ in range(2000) if engine.handedness(False, False) == "esquerda")
    assert 0.07 <= canhotos / 2000 <= 0.15     # esperado ≈ 10,9%
```

:::tip Sempre fixe a semente
Testes estatísticos com semente fixa são determinísticos — a margem existe para proteger contra
recalibrações pequenas, não contra aleatoriedade real.
:::

## Testar um gerador novo

```python
from persona_db.generators import gen_42_voluntariado
from persona_db.generators.gen_00_pessoa import generate_personas
from persona_db.validators import validate_dataset

def test_dominio_novo_passa_nos_validadores():
    personas = generate_personas(40, seed=7)
    dataset = {"pessoa": [p for p in personas]}
    dataset.update(gen_42_voluntariado.generate(personas, seed=7))
    assert validate_dataset(dataset)["passed"]
```

## Regressões

`tests/unit/test_review_regressions.py` guarda casos vindos de revisões e bugs já corrigidos. Ao
corrigir um defeito, acrescente ali o caso mínimo que o reproduz — é a rede de proteção contra
reintroduções.

## Lint e tipos

```bash
python3 -m ruff check persona_db          # obrigatório na CI
python3 -m ruff check --fix persona_db
python3 -m black persona_db               # opcional (linha 100)
python3 -m mypy persona_db                # opcional, não é gate na CI
```

`ruff` está configurado com `line-length = 100` e `target-version = "py310"`.

## Na CI

O workflow `.github/workflows/ci.yml` roda, a cada push e pull request, em Python 3.12:

```yaml
- run: python -m pip install -e './persona_db[dev]'
- run: python -m pytest persona_db/tests
- run: python -m ruff check persona_db
```

Detalhes em [CI e qualidade](../projeto/ci-e-qualidade.md).
