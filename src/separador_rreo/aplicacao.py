"""Fachada de alto nível do fluxo de separação RREO."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from separador_rreo.analisador import AnalisadorRreo
from separador_rreo.contratos import (
    Analisador,
    Exportador,
    FabricaDocumentoPdf,
    ReconhecedorTitulo,
)
from separador_rreo.documento_pdf import abrir_documento_pdf
from separador_rreo.exportacao import ExportadorRreo
from separador_rreo.modelos import ResultadoAnalise, ResultadoExportacao


class SeparadorRreo:
    """Orquestra leitura, análise e exportação sem conter regras de domínio."""

    def __init__(
        self,
        *,
        analisador: Analisador | None = None,
        exportador: Exportador | None = None,
        reconhecedor: ReconhecedorTitulo | None = None,
        fabrica_documento: FabricaDocumentoPdf = abrir_documento_pdf,
    ) -> None:
        self._analisador = analisador or AnalisadorRreo(reconhecedor)
        self._exportador = exportador or ExportadorRreo()
        self._fabrica_documento = fabrica_documento

    def analisar(
        self, caminho_pdf: Path | str, municipios: Sequence[str]
    ) -> ResultadoAnalise:
        documento = self._fabrica_documento(caminho_pdf)
        try:
            return self._analisador.analisar(documento, municipios)
        finally:
            documento.fechar()

    def executar(
        self,
        caminho_pdf: Path | str,
        municipios: Sequence[str],
        destino: Path | str = "RREO_separados",
    ) -> tuple[ResultadoAnalise, ResultadoExportacao]:
        documento = self._fabrica_documento(caminho_pdf)
        try:
            analise = self._analisador.analisar(documento, municipios)
            exportacao = self._exportador.exportar(documento, analise, destino)
            return analise, exportacao
        finally:
            documento.fechar()


def separar_rreo(
    caminho_pdf: Path | str,
    municipios: Sequence[str],
    destino: Path | str = "RREO_separados",
) -> ResultadoExportacao:
    """Analisa o diário e gera PDFs, planilha e ZIP."""
    _, exportacao = SeparadorRreo().executar(caminho_pdf, municipios, destino)
    return exportacao
