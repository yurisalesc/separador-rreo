"""Utilitários de normalização de texto."""

from __future__ import annotations

import re
import unicodedata


def normalizar(texto: str) -> str:
    """Normaliza texto para comparação: maiúsculas, sem acentos e espaços extras."""
    decomposto = unicodedata.normalize("NFKD", texto.upper())
    sem_acentos = "".join(
        caractere for caractere in decomposto if not unicodedata.combining(caractere)
    )
    return re.sub(r"\s+", " ", sem_acentos).upper().strip(" .-")


def nome_diretorio_seguro(nome: str) -> str:
    """Converte um nome normalizado em nome de diretório seguro."""
    return re.sub(r"[^A-Z0-9_-]+", "_", nome)
