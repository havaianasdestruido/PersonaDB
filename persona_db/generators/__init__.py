"""Geradores de domínio do PersonaDB (`gen_00` a `gen_23`).

Cada módulo corresponde a um domínio do schema relacional PostgreSQL e produz
dicionários determinísticos prontos para validação em memória e carga em lote.
"""
from __future__ import annotations

__all__ = [
    "gen_00_pessoa",
    "gen_01_identidade",
    "gen_02_genealogia",
    "gen_03_saude",
    "gen_04_educacao",
    "gen_05_carreira",
    "gen_06_financas",
    "gen_07_residencia",
    "gen_08_relacionamentos",
    "gen_09_rede_social",
    "gen_10_digital",
    "gen_11_juridico",
    "gen_12_eleitoral",
    "gen_13_viagens",
    "gen_14_pets",
    "gen_15_consumo",
    "gen_16_timeline",
    "gen_17_comportamento",
    "gen_18_religiao",
    "gen_19_esporte",
    "gen_20_militar",
    "gen_21_imigracao",
    "gen_22_comunicacao",
    "gen_23_midia",
]
