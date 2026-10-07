"""Utilitários de normalização de texto."""

from __future__ import annotations

import re
import unicodedata


def normalize(text: str) -> str:
    """Normaliza texto para comparação (maiúsculas, sem acentos, espaços colapsados)."""
    folded = unicodedata.normalize("NFKD", text.upper())
    without_marks = "".join(c for c in folded if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", without_marks).upper().strip(" .-")


def safe_dirname(name: str) -> str:
    """Converte um nome de município normalizado em nome de pasta seguro."""
    return re.sub(r"[^A-Z0-9_-]+", "_", name)
