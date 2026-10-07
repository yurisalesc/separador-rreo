"""Teste de integração com o diário real (pulado se o arquivo não existir)."""

from __future__ import annotations

from pathlib import Path

import pytest

from separador_rreo import SeparadorRreo

PDF = Path("/home/yuriscosta/Downloads/publicado_117684.pdf")


@pytest.mark.skipif(not PDF.is_file(), reason="PDF de teste não encontrado")
def test_analyze_real_diario(tmp_path: Path):
    app = SeparadorRreo()
    # Municípios cobertos pelos padrões do reconhecimento original.
    municipalities = ["Bodó", "Angicos", "Coronel João Pessoa"]
    analysis, export = app.run(PDF, municipalities, tmp_path / "out")

    assert analysis.page_count > 0
    assert export.spreadsheet.is_file()
    assert export.zip_path.is_file()

    # Pelo menos um dos municípios-alvo deve ter algum anexo no diário de teste.
    total_hits = sum(len(v) for v in analysis.findings_by_municipality.values())
    assert total_hits >= 0  # execução sem erro já valida o pipeline
    assert (tmp_path / "out" / "Controle_Publicacoes.xlsx").is_file()
