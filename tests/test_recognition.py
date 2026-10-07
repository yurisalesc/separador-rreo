from separador_rreo.recognition import AnexoRecognizer


def test_recognize_explicit_annex_rreo():
    recognizer = AnexoRecognizer()
    assert recognizer.recognize("ANEXO 01_RREO") == 1
    assert recognizer.recognize("ANEXO 12 - RREO") == 12


def test_recognize_rreo_4bim_with_roman_annex():
    recognizer = AnexoRecognizer()
    assert (
        recognizer.recognize("RREO - IV BIM - ANEXO XIV - DEMONSTRATIVO SIMPLIFICADO")
        == 14
    )


def test_recognize_keyword_balanco():
    recognizer = AnexoRecognizer()
    assert recognizer.recognize("RREO - 4º BIM - BALANÇO ORÇAMENTÁRIO") == 1


def test_ignore_non_header_citation():
    recognizer = AnexoRecognizer()
    assert recognizer.recognize("conforme o RREO do anexo 1 mencionado abaixo") is None


def test_custom_heuristic_extension():
    def custom(line: str) -> int | None:
        return 9 if "CUSTOM ANEXO NOVE" in line.upper() else None

    recognizer = AnexoRecognizer(heuristics=[custom])
    assert recognizer.recognize("CUSTOM ANEXO NOVE") == 9
    assert recognizer.recognize("ANEXO 01_RREO") is None
