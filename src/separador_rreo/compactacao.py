"""Compactação dos artefatos gerados."""

from __future__ import annotations

import zipfile
from pathlib import Path


class CompactadorZip:
    """Compacta recursivamente um diretório em um arquivo ZIP."""

    def compactar(self, diretorio: Path, destino: Path | None = None) -> Path:
        arquivo_zip = destino or diretorio.with_suffix(".zip")
        with zipfile.ZipFile(arquivo_zip, "w", zipfile.ZIP_DEFLATED) as arquivo:
            for caminho in diretorio.rglob("*"):
                if caminho.is_file():
                    arquivo.write(caminho, caminho.relative_to(diretorio))
        return arquivo_zip
