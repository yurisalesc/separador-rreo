from pathlib import Path

import pytest

from separador_rreo import AnalisadorRreo


class DocumentoPdfFalso:
    """Documento mínimo para caracterizar o analisador sem acessar arquivos."""

    caminho = Path("diario.pdf")

    def __init__(self, pages: list[str]) -> None:
        self._pages = pages

    def __len__(self) -> int:
        return len(self._pages)

    def texto_da_pagina(self, indice_pagina: int) -> str:
        return self._pages[indice_pagina]

    def extrair_paginas(
        self, pagina_inicial: int, pagina_final: int, destino: Path
    ) -> None:
        raise AssertionError("O analisador não deve extrair páginas")

    def fechar(self) -> None:
        pass


def test_localiza_anexo_e_usa_codigo_como_limite():
    documento = DocumentoPdfFalso(
        [
            "PREFEITURA MUNICIPAL DE BODÓ\nANEXO 01_RREO\nconteúdo do anexo\n",
            "continuação\nCódigo Identificador: ABC12345\n",
        ]
    )

    resultado = AnalisadorRreo().analisar(documento, ["Bodó"])

    assert resultado.quantidade_paginas == 2
    assert resultado.origem == Path("diario.pdf")
    assert len(resultado.do_municipio("Bodó")) == 1
    ocorrencia = resultado.do_municipio("Bodó")[0]
    assert (
        ocorrencia.anexo,
        ocorrencia.pagina_inicial,
        ocorrencia.pagina_final,
    ) == (1, 1, 2)
    assert ocorrencia.situacao.value == "Encontrado"


def test_sinaliza_codigo_ausente_para_conferencia_manual():
    documento = DocumentoPdfFalso(
        [
            "PREFEITURA MUNICIPAL DE ANGICOS\nANEXO 03_RREO\nconteúdo sem código\n",
        ]
    )

    ocorrencia = (
        AnalisadorRreo().analisar(documento, ["Angicos"]).do_municipio("Angicos")[0]
    )

    assert ocorrencia.situacao.value == "Verificar limite final"


def test_rejeita_pdf_sem_cabecalhos_de_municipio():
    documento = DocumentoPdfFalso(["ANEXO 01_RREO\nconteúdo\n"])

    with pytest.raises(ValueError, match="cabeçalhos de prefeituras"):
        AnalisadorRreo().analisar(documento, ["Bodó"])
