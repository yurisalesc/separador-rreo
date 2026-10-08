from pathlib import Path

import pytest

from separador_rreo.cli import criar_analisador_argumentos, main


def test_analisador_argumentos_usa_opcoes_em_portugues():
    opcoes = criar_analisador_argumentos().parse_args(
        [
            "diario.pdf",
            "--municipios",
            "Bodó",
            "Angicos",
            "--saida",
            "resultado",
        ]
    )

    assert opcoes.pdf == Path("diario.pdf")
    assert opcoes.municipios == ["Bodó", "Angicos"]
    assert opcoes.saida == Path("resultado")


def test_cli_rejeita_pdf_inexistente(tmp_path: Path):
    with pytest.raises(SystemExit) as erro:
        main([str(tmp_path / "inexistente.pdf"), "--municipios", "Bodó"])

    assert erro.value.code == 2
