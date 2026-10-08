from pathlib import Path

import pytest

from separador_rreo import ResultadoAnalise, SeparadorRreo


class DocumentoFalso:
    caminho = Path("teste.pdf")

    def __init__(self) -> None:
        self.fechado = False

    def __len__(self) -> int:
        return 0

    def texto_da_pagina(self, indice_pagina: int) -> str:
        raise IndexError(indice_pagina)

    def extrair_paginas(
        self, pagina_inicial: int, pagina_final: int, destino: Path
    ) -> None:
        pass

    def fechar(self) -> None:
        self.fechado = True


class AnalisadorFalso:
    def analisar(self, documento, municipios):
        return ResultadoAnalise(
            ocorrencias_por_municipio={municipio: [] for municipio in municipios}
        )


def test_separador_fecha_documento_apos_analise():
    documento = DocumentoFalso()
    separador = SeparadorRreo(
        analisador=AnalisadorFalso(),
        fabrica_documento=lambda caminho: documento,
    )

    resultado = separador.analisar("teste.pdf", ["BODO"])

    assert resultado.municipios == ("BODO",)
    assert documento.fechado is True


def test_separador_fecha_documento_quando_analise_falha():
    documento = DocumentoFalso()

    class AnalisadorComErro:
        def analisar(self, documento, municipios):
            raise ValueError("falha esperada")

    separador = SeparadorRreo(
        analisador=AnalisadorComErro(),
        fabrica_documento=lambda caminho: documento,
    )

    with pytest.raises(ValueError, match="falha esperada"):
        separador.analisar("teste.pdf", ["BODO"])

    assert documento.fechado is True
