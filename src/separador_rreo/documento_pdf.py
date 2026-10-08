"""Adaptador de documentos PDF baseado em PyMuPDF."""

from __future__ import annotations

from pathlib import Path
from types import TracebackType

import pymupdf


class DocumentoPyMuPdf:
    """Implementa o contrato de PDF usando a biblioteca PyMuPDF."""

    def __init__(self, caminho: Path | str) -> None:
        self._caminho = Path(caminho)
        self._documento = pymupdf.open(str(self._caminho))

    @property
    def caminho(self) -> Path:
        return self._caminho

    def __len__(self) -> int:
        return self._documento.page_count

    def texto_da_pagina(self, indice_pagina: int) -> str:
        return self._documento[indice_pagina].get_text(sort=True)

    def extrair_paginas(
        self, pagina_inicial: int, pagina_final: int, destino: Path
    ) -> None:
        """Extrai páginas inclusivas, numeradas a partir de 1, para outro PDF."""
        saida = pymupdf.open()
        try:
            saida.insert_pdf(
                self._documento,
                from_page=pagina_inicial - 1,
                to_page=pagina_final - 1,
            )
            destino.parent.mkdir(parents=True, exist_ok=True)
            saida.save(str(destino), garbage=3, deflate=True)
        finally:
            saida.close()

    def fechar(self) -> None:
        self._documento.close()

    def __enter__(self) -> DocumentoPyMuPdf:
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        valor: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.fechar()


def abrir_documento_pdf(caminho: Path | str) -> DocumentoPyMuPdf:
    """Fábrica padrão de documentos PDF."""
    return DocumentoPyMuPdf(caminho)
