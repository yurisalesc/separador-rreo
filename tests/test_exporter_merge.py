from separador_rreo.exporter import _merge_sequential
from separador_rreo.models import Finding


def test_merge_sequential_parts():
    findings = [
        Finding(1, 10, 12, "Encontrado", "t1"),
        Finding(1, 13, 15, "Encontrado", "t2"),
        Finding(1, 20, 22, "Encontrado", "t3"),
    ]
    merged = _merge_sequential(findings)
    assert len(merged) == 2
    assert merged[0].page_start == 10
    assert merged[0].page_end == 15
    assert merged[0].status == "Encontrado - partes reunidas"
    assert merged[1].page_start == 20


def test_merge_marks_verify_when_mixed_status():
    findings = [
        Finding(1, 10, 12, "Encontrado", "t1"),
        Finding(1, 13, 15, "Verificar limite final", "t2"),
    ]
    merged = _merge_sequential(findings)
    assert len(merged) == 1
    assert merged[0].status == "Verificar partes reunidas"
