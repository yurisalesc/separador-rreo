"""Teste de integração com o diário real (pulado se o arquivo não existir)."""

from __future__ import annotations

from pathlib import Path

import pytest

from separador_rreo import SeparadorRreo

PDF = Path(__file__).resolve().parent / "fixtures" / "publicado_117684.pdf"


@pytest.mark.skipif(not PDF.is_file(), reason="PDF de teste não encontrado")
def test_analisa_diario_real(tmp_path: Path):
    separador = SeparadorRreo()
    # Municípios cobertos pelos padrões do reconhecimento original.
    municipios = ["Bodó", "Angicos", "Coronel João Pessoa"]
    analise, exportacao = separador.executar(PDF, municipios, tmp_path / "out")

    assert analise.quantidade_paginas > 0
    assert exportacao.planilha.is_file()
    assert exportacao.arquivo_zip.is_file()

    # Estes valores caracterizam o comportamento esperado para o diário de exemplo.
    assert analise.quantidade_paginas == 586
    assert {
        municipio: [
            (item.anexo, item.pagina_inicial, item.pagina_final) for item in ocorrencias
        ]
        for municipio, ocorrencias in analise.ocorrencias_por_municipio.items()
    } == {
        "BODO": [
            (8, 221, 224),
            (4, 224, 226),
            (6, 226, 227),
            (14, 227, 229),
            (1, 379, 386),
            (1, 386, 388),
            (3, 388, 389),
            (13, 391, 392),
            (7, 394, 395),
        ],
        "ANGICOS": [
            (4, 188, 190),
            (6, 190, 192),
            (6, 192, 193),
            (8, 193, 196),
            (14, 196, 197),
            (1, 359, 365),
            (2, 365, 367),
            (3, 367, 368),
            (7, 368, 368),
            (12, 368, 370),
            (13, 371, 371),
        ],
        "CORONEL JOAO PESSOA": [
            (4, 238, 239),
            (6, 239, 241),
            (12, 241, 243),
            (14, 243, 244),
            (8, 244, 247),
            (1, 395, 397),
            (2, 397, 400),
            (13, 400, 400),
            (3, 400, 402),
            (7, 402, 403),
        ],
    }
    assert exportacao.quantidade_pdfs > 0
    assert (tmp_path / "out" / "Controle_Publicacoes.xlsx").is_file()
