"""Reference seed data package.

Coordinates shared lookup tables that generators import at runtime.
Owner agents may add modules below this package but must not delete.

Exposed helpers:
- lookup_data: nomes, cidades, bairros, profissões, doenças, empresas...
- probability_tables: mobilidade, mortalidade, doenças, crimes, emprego,
  renda (Lorenz) e ancestralidade→traços.
"""
from . import lookup_data  # noqa: F401
from . import probability_tables  # noqa: F401