"""Contratos entre as camadas da aplicação."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from separador_rreo.modelos import ResultadoAnalise, ResultadoExportacao


class DocumentoPdf(Protocol):
    """Operações de PDF necessárias ao domínio."""

    @property
    def caminho(self) -> Path: ...

    def __len__(self) -> int: ...

    def texto_da_pagina(self, indice_pagina: int) -> str: ...

    def extrair_paginas(
        self, pagina_inicial: int, pagina_final: int, destino: Path
    ) -> None: ...

    def fechar(self) -> None: ...


class FabricaDocumentoPdf(Protocol):
    """Cria um documento PDF a partir de um caminho."""

    def __call__(self, caminho: Path | str) -> DocumentoPdf: ...


class ReconhecedorTitulo(Protocol):
    """Reconhece o anexo representado por uma linha de título."""

    def reconhecer(self, linha: str) -> int | None: ...


class Analisador(Protocol):
    """Analisa um PDF para localizar anexos por município."""

    def analisar(
        self, documento: DocumentoPdf, municipios: Sequence[str]
    ) -> ResultadoAnalise: ...


class Exportador(Protocol):
    """Gera os artefatos de saída a partir da análise."""

    def exportar(
        self,
        documento: DocumentoPdf,
        analise: ResultadoAnalise,
        destino: Path | str,
    ) -> ResultadoExportacao: ...
