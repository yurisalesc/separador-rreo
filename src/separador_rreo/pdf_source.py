"""Abstração de leitura de PDF (Dependency Inversion sobre PyMuPDF)."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import pymupdf


class PdfDocument(Protocol):
    """Contrato mínimo de um documento PDF usado pelo analisador/exportador."""

    def __len__(self) -> int: ...

    def page_text(self, page_index: int) -> str: ...

    def extract_pages(self, page_start: int, page_end: int, destination: Path) -> None: ...

    def close(self) -> None: ...


class PyMuPdfDocument:
    """Adaptador de `pymupdf` para o contrato `PdfDocument`."""

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._doc = pymupdf.open(str(self._path))

    @property
    def path(self) -> Path:
        return self._path

    def __len__(self) -> int:
        return self._doc.page_count

    def page_text(self, page_index: int) -> str:
        return self._doc[page_index].get_text(sort=True)

    def extract_pages(self, page_start: int, page_end: int, destination: Path) -> None:
        """Extrai páginas 1-based inclusivas para um novo arquivo PDF."""
        out = pymupdf.open()
        try:
            out.insert_pdf(self._doc, from_page=page_start - 1, to_page=page_end - 1)
            destination.parent.mkdir(parents=True, exist_ok=True)
            out.save(str(destination), garbage=3, deflate=True)
        finally:
            out.close()

    def close(self) -> None:
        self._doc.close()


def open_pdf(path: Path | str) -> PyMuPdfDocument:
    return PyMuPdfDocument(path)
