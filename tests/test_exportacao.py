import zipfile
from pathlib import Path

from openpyxl import load_workbook

from separador_rreo import (
    AnexoRreo,
    ExportadorRreo,
    Ocorrencia,
    ResultadoAnalise,
    SituacaoOcorrencia,
)


class DocumentoPdfFalso:
    caminho = Path("teste.pdf")

    def __init__(self) -> None:
        self.extracoes: list[tuple[int, int, Path]] = []

    def __len__(self) -> int:
        return 1

    def texto_da_pagina(self, indice_pagina: int) -> str:
        return ""

    def extrair_paginas(
        self, pagina_inicial: int, pagina_final: int, destino: Path
    ) -> None:
        self.extracoes.append((pagina_inicial, pagina_final, destino))
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(b"%PDF-falso")

    def fechar(self) -> None:
        pass


def test_exportador_gera_pdf_planilha_e_zip(tmp_path: Path):
    documento = DocumentoPdfFalso()
    analise = ResultadoAnalise(
        ocorrencias_por_municipio={
            "BODO": [
                Ocorrencia(
                    anexo=AnexoRreo.BALANCO_ORCAMENTARIO,
                    pagina_inicial=2,
                    pagina_final=4,
                    situacao=SituacaoOcorrencia.ENCONTRADO,
                    titulo="ANEXO 01_RREO",
                )
            ]
        }
    )

    resultado = ExportadorRreo(anexos=[AnexoRreo.BALANCO_ORCAMENTARIO]).exportar(
        documento, analise, tmp_path / "saida"
    )

    assert resultado.quantidade_pdfs == 1
    assert resultado.planilha.is_file()
    assert resultado.arquivo_zip.is_file()
    assert documento.extracoes[0][:2] == (2, 4)

    workbook = load_workbook(resultado.planilha)
    planilha = workbook["Conferencia RREO"]
    assert planilha["A2"].value == "BODO"
    assert planilha["B2"].value == 1
    assert planilha["F2"].value == "Encontrado"

    with zipfile.ZipFile(resultado.arquivo_zip) as arquivo:
        assert "Controle_Publicacoes.xlsx" in arquivo.namelist()
        assert "BODO/RREO_01_BODO.pdf" in arquivo.namelist()


def test_exportador_cria_linha_nao_localizada(tmp_path: Path):
    resultado = ExportadorRreo(anexos=[AnexoRreo.RESTOS_A_PAGAR]).exportar(
        DocumentoPdfFalso(),
        ResultadoAnalise(ocorrencias_por_municipio={"BODO": []}),
        tmp_path / "saida",
    )

    linha = resultado.linhas[0]
    assert linha.situacao is SituacaoOcorrencia.NAO_LOCALIZADO
    assert linha.rotulo_situacao == "Nao localizado"
    assert linha.arquivo is None
