from separador_rreo.text import normalize, safe_dirname


def test_normalize_removes_accents_and_collapses_spaces():
    assert normalize("  Coronel  João Pessoa ") == "CORONEL JOAO PESSOA"


def test_safe_dirname():
    assert safe_dirname("CORONEL JOAO PESSOA") == "CORONEL_JOAO_PESSOA"
