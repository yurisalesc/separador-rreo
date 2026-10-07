"""Modelos de domínio imutáveis usados pela análise e pela exportação."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True, slots=True)
class SectionMarker:
    """Cabeçalho de prefeitura encontrado no texto concatenado do PDF."""

    offset: int
    municipality: str


@dataclass(frozen=True, slots=True)
class CodeMarker:
    """Marcador de 'Código Identificador' que costuma encerrar o artigo."""

    start: int
    end: int


@dataclass(frozen=True, slots=True)
class TitleHit:
    """Título de anexo RREO reconhecido no PDF."""

    offset: int
    page: int
    annex: int
    raw_title: str


@dataclass(frozen=True, slots=True)
class Finding:
    """Trecho de um anexo localizado para um município."""

    annex: int
    page_start: int
    page_end: int
    status: str
    title: str


@dataclass(slots=True)
class AnalysisResult:
    """Resultado da análise de um diário FEMURN."""

    findings_by_municipality: dict[str, list[Finding]] = field(default_factory=dict)
    page_count: int = 0
    source: Path | None = None

    def for_municipality(self, municipality: str) -> list[Finding]:
        from separador_rreo.text import normalize

        return list(self.findings_by_municipality.get(normalize(municipality), []))

    @property
    def municipalities(self) -> tuple[str, ...]:
        return tuple(sorted(self.findings_by_municipality))


@dataclass(frozen=True, slots=True)
class ExportResult:
    """Artefatos gerados após a exportação."""

    output_dir: Path
    spreadsheet: Path
    zip_path: Path
    pdf_count: int
    rows: tuple[Mapping[str, object], ...]
