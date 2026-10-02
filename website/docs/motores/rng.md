---
title: "Motor de aleatoriedade (rng.py)"
sidebar_label: rng — aleatoriedade
sidebar_position: 1
description: SeededRNG, forking determinístico com BLAKE2b e amostradores disponíveis.
---

# `SeededRNG` — aleatoriedade determinística

Arquivo: [`persona_db/engines/rng.py`](../referencia-api/engines/rng.md)

`SeededRNG` é um invólucro fino sobre `numpy.random.Generator` (PCG64) que acrescenta **forking
determinístico**. Todo o restante do projeto — motores, geradores e testes — obtém aleatoriedade
exclusivamente por aqui.

## Construção e forking

```python
from persona_db.engines.rng import SeededRNG, new_rng

master = new_rng(42)                     # ou SeededRNG(master_seed=42)
rng = master.fork(persona_id, "gen05-carreira")
rng_alt = master.fork(persona_id, "gen05-carreira", salt="promocoes")
```

Sem semente explícita, `SeededRNG()` sorteia 8 bytes de `os.urandom` — útil para exploração, nunca
para datasets reprodutíveis.

A semente derivada é:

$$S(p, d, \text{salt}) = \text{int64}_{\text{big}}\Big(\text{BLAKE2b}\big(\text{UTF8}(S_0 \,\|\, p \,\|\, d \,\|\, \text{salt})\big)_{0..7}\Big)$$

```python
payload = f"{self._master_seed}|{persona_id}|{domain}|{salt}"
seed_bytes = hashlib.blake2b(payload.encode()).digest()[:8]
return SeededRNG(master_seed=int.from_bytes(seed_bytes, "big"))
```

Consequências estão detalhadas em [Determinismo](../arquitetura/determinismo.md).

## Amostradores

| Método | Distribuição | Garantias |
|---|---|---|
| `bernoulli(p)` | $X \sim \text{Bernoulli}(p)$ | devolve `bool` nativo |
| `choice(options, weights=None)` | categórica | pesos são normalizados automaticamente ($\sum w_i = 1$) |
| `integer(low, high)` | uniforme discreta | intervalo **inclusivo** em ambos os extremos |
| `uniform(low, high)` | $U(a, b)$ | `float` |
| `normal(mu, sigma)` | $\mathcal{N}(\mu, \sigma^2)$ | `float` |
| `normal_clipped(mu, sigma, low, high)` | normal truncada | $X = \min(\max(Y, a), b)$ — **truncamento, não rejeição** |
| `log_normal(mu, sigma)` | $\ln X \sim \mathcal{N}(\mu, \sigma^2)$ | $\mathbb{E}[X] = e^{\mu + \sigma^2/2}$ |
| `poisson(lam)` | $P(K=k) = \lambda^k e^{-\lambda}/k!$ | `int` |
| `beta_sample(alpha, beta)` | $\text{Beta}(\alpha, \beta)$ em $[0,1]$ | `float` |
| `dirichlet(alphas)` | $\text{Dir}(\boldsymbol{\alpha})$ | `ndarray` que soma 1 |
| `rng` (propriedade) | — | acesso ao `numpy.random.Generator` subjacente |

:::caution `normal_clipped` enviesa as caudas
O método **grampeia** o valor nos limites em vez de reamostrar. Com limites próximos da média,
acumula massa de probabilidade exatamente em `low` e `high`. Para faixas estreitas, prefira uma
Beta reescalada.
:::

## Registro de sementes

```python
from persona_db.engines.rng import register_seed

register_seed(persona_id, {"seed": 42, "domain": "gen03"})
```

Anexa uma linha JSON em `persona_db/data/rng_log.jsonl` (o diretório é criado sob demanda). Falhas
de I/O são **silenciosamente ignoradas** de propósito: o log é um auxílio de depuração e nunca pode
derrubar uma simulação. A tabela `semente_aleatoria` do domínio 24 cumpre o papel equivalente dentro
do banco.

## Exemplo completo

```python
from persona_db.engines.rng import new_rng

master = new_rng(7)
rng = master.fork("b3f1…-uuid", "exemplo")

print(rng.bernoulli(0.3))                                   # False
print(rng.choice(["A", "B1", "C2"], weights=[0.1, 0.3, 0.6]))
print(round(rng.normal_clipped(170, 7, 140, 210), 1))       # 168.4
print(rng.poisson(1.9))                                     # 2
print(rng.dirichlet([3, 2, 1]).round(3))                    # [0.52 0.33 0.15]
```

Rodar o mesmo trecho novamente, em qualquer máquina, imprime exatamente os mesmos valores.

## Custo computacional

Cada `fork()` instancia um novo `numpy.random.Generator`, e cada `choice()` converte a sequência
Python em arrays NumPy. Para populações grandes isso domina o tempo de execução — a análise está em
[Desempenho](../guias/desempenho.md) e em `rewrite.MD`. A troca por um gerador puro em Python é
considerada, mas **ainda não implementada**; qualquer mudança aqui quebra a reprodutibilidade dos
datasets existentes.
