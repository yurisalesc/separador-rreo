"""Reconhecimento de títulos de anexos RREO (aberto a extensão de heurísticas)."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence
from typing import Protocol

from separador_rreo.constants import ANEXOS_PADRAO, ROMANOS
from separador_rreo.text import normalize

Heuristic = Callable[[str], int | None]


class TitleRecognizer(Protocol):
    """Contrato para reconhecer o número do anexo a partir de uma linha de título."""

    def recognize(self, line: str) -> int | None:
        """Retorna o número do anexo ou None se a linha não for um título efetivo."""


def _explicit_annex_rreo(normalized: str) -> int | None:
    match = re.search(
        r"\bANEXO\s*0*(\d{1,2})\s*[_-]\s*RREO(?=$|[^A-Z])",
        normalized,
    )
    if match:
        return int(match.group(1))
    return None


def _is_rreo_4bim_header(normalized: str) -> bool:
    return bool(
        re.match(
            r"^RREO\s*[-–]?\s*(?:IV\s*BIM\b|4\s*[º°O]?\s*BIM\b)",
            normalized,
        )
    )


def _annex_number_token(normalized: str) -> int | None:
    match = re.search(r"\bANEXO\s*0*(\d{1,2})\b", normalized)
    if match:
        return int(match.group(1))
    match = re.search(
        r"\bANEXO\s+(XIV|XIII|XII|XI|VIII|VII|VI|IV|III|II|IX|X|I)\b",
        normalized,
    )
    if match:
        return ROMANOS[match.group(1)]
    return None


def _keyword_annex(normalized: str) -> int | None:
    # Cabeçalhos efetivos de publicação, NÃO citações ao RREO dentro do demonstrativo.
    keywords: tuple[tuple[str, int], ...] = (
        ("BALANCO ORCAMENTARIO", 1),
        ("PREVIDENCIARIAS", 4),
        ("RESULTADO PRIMARIO", 6),
        ("RESULTADO NOMINAL", 6),
        ("ACOES E SERVICOS PUBLICOS DE SAUDE", 12),
        ("RECEITA CORRENTE LIQUIDA", 3),
        ("RESTOS A PAGAR", 7),
        ("DESPESAS COM MANUTENCAO", 8),
        ("COM MDE", 8),
        ("PARCERIAS PUBLICO", 13),
        ("DEMONSTRATIVO SIMPLIFICADO", 14),
    )
    for needle, annex in keywords:
        if needle in normalized:
            return annex
    return None


def default_heuristics() -> tuple[Heuristic, ...]:
    """Heurísticas padrão (padrões Angicos, Bodó e Coronel João Pessoa)."""

    def from_explicit(line: str) -> int | None:
        return _explicit_annex_rreo(normalize(line))

    def from_rreo_header(line: str) -> int | None:
        normalized = normalize(line)
        if not _is_rreo_4bim_header(normalized):
            return None
        return _annex_number_token(normalized) or _keyword_annex(normalized)

    return (from_explicit, from_rreo_header)


class AnexoRecognizer:
    """
    Reconhece títulos de anexos RREO.

    Aberto a extensão: passe heurísticas extras sem alterar o analisador (OCP).
    """

    def __init__(
        self,
        *,
        allowed_annexes: Sequence[int] = ANEXOS_PADRAO,
        heuristics: Iterable[Heuristic] | None = None,
    ) -> None:
        self._allowed = frozenset(allowed_annexes)
        self._heuristics = tuple(heuristics) if heuristics is not None else default_heuristics()

    @property
    def allowed_annexes(self) -> frozenset[int]:
        return self._allowed

    def recognize(self, line: str) -> int | None:
        for heuristic in self._heuristics:
            annex = heuristic(line)
            if annex is not None and annex in self._allowed:
                return annex
        return None
