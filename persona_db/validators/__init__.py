"""Módulos de validação de consistência do PersonaDB."""
from __future__ import annotations

from .run_validators import (
    build_validation_table_rows,
    render_html_report,
    validate_dataset,
)
from .val_financas import validate_financas
from .val_genealogia import validate_genealogia
from .val_juridico import validate_juridico
from .val_saude import validate_saude
from .val_social import validate_social
from .val_temporal import validate_temporal

__all__ = [
    "build_validation_table_rows",
    "render_html_report",
    "validate_dataset",
    "validate_financas",
    "validate_genealogia",
    "validate_juridico",
    "validate_saude",
    "validate_social",
    "validate_temporal",
]
