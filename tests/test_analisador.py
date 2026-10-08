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


def test_nao_fragmenta_anexo_por_cabecalho_de_continuacao():
    documento = DocumentoPdfFalso(
        [
            "PREFEITURA MUNICIPAL DE CORONEL JOÃO PESSOA\n"
            "RREO 4º BIM. 2026 - ANEXO XII - DEMONSTRATIVO DAS RECEITAS "
            "E DESPESAS COM ACOES E SERVICOS PUBLICOS DE SAUDE\n"
            "conteúdo inicial\n",
            "RREO - ANEXO 12 (LC 141/2012, art. 35)\ncontinuação da tabela\n",
            "resto do demonstrativo\nCódigo Identificador: ABC12345\n",
        ]
    )

    ocorrencias = (
        AnalisadorRreo()
        .analisar(documento, ["Coronel João Pessoa"])
        .do_municipio("Coronel João Pessoa")
    )

    assert len(ocorrencias) == 1
    assert (
        ocorrencias[0].anexo,
        ocorrencias[0].pagina_inicial,
        ocorrencias[0].pagina_final,
    ) == (12, 1, 3)


def test_mantem_publicacoes_distintas_do_mesmo_anexo():
    documento = DocumentoPdfFalso(
        [
            "PREFEITURA MUNICIPAL DE ANGICOS\n"
            "ANEXO 06_RREO\nprimeiro\n"
            "Código Identificador: AAA11111\n",
            "ANEXO 06_RREO\nsegundo\nCódigo Identificador: BBB22222\n",
        ]
    )

    ocorrencias = (
        AnalisadorRreo().analisar(documento, ["Angicos"]).do_municipio("Angicos")
    )

    assert [
        (item.anexo, item.pagina_inicial, item.pagina_final) for item in ocorrencias
    ] == [(6, 1, 1), (6, 2, 2)]


def test_rejeita_pdf_sem_cabecalhos_de_municipio():
    documento = DocumentoPdfFalso(["ANEXO 01_RREO\nconteúdo\n"])

    with pytest.raises(ValueError, match="cabeçalhos de prefeituras"):
        AnalisadorRreo().analisar(documento, ["Bodó"])
