"""Orquestração de alto nível (facade) do fluxo analisar → exportar."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from separador_rreo.analyzer import RreoAnalyzer
from separador_rreo.exporter import ExportResult, RreoExporter
from separador_rreo.models import AnalysisResult
from separador_rreo.pdf_source import open_pdf
from separador_rreo.recognition import TitleRecognizer


class SeparadorRreo:
    """
    Facade que coordena analisador e exportador.

    Depende de abstrações (`TitleRecognizer`, contratos de PDF) e não da CLI.
    """

    def __init__(
        self,
        *,
        analyzer: RreoAnalyzer | None = None,
        exporter: RreoExporter | None = None,
        recognizer: TitleRecognizer | None = None,
    ) -> None:
        self._analyzer = analyzer or RreoAnalyzer(recognizer=recognizer)
        self._exporter = exporter or RreoExporter()

    def analyze(
        self,
        pdf_path: Path | str,
        municipalities: Sequence[str],
    ) -> AnalysisResult:
        document = open_pdf(pdf_path)
        try:
            return self._analyzer.analyze(document, municipalities)
        finally:
            document.close()

    def run(
        self,
        pdf_path: Path | str,
        municipalities: Sequence[str],
        destination: Path | str = "RREO_separados",
    ) -> tuple[AnalysisResult, ExportResult]:
        document = open_pdf(pdf_path)
        try:
            analysis = self._analyzer.analyze(document, municipalities)
            export = self._exporter.export(document, analysis, destination)
            return analysis, export
        finally:
            document.close()


def separar(
    pdf_path: Path | str,
    municipalities: Sequence[str],
    destination: Path | str = "RREO_separados",
) -> ExportResult:
    """Atalho: analisa o diário e gera PDFs + planilha + ZIP."""
    _, export = SeparadorRreo().run(pdf_path, municipalities, destination)
    return export
