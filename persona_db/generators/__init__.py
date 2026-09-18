"""Generadores de PersonaDB.

Each module mirrors a DDL domain and produces plain-dict rows ready for
bulk insertion (see Agent 14 scripts/). Domains:
  - gen_00_pessoa.py       Hub: persona
  - gen_01_identidade.py   Domínio 01: documentos, biometria, fenótipos
  - gen_02_genealogia.py   Domínio 02: famílias, parentesco, herança
"""
from __future__ import annotations