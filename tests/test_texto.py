from separador_rreo.texto import nome_diretorio_seguro, normalizar


def test_normalizacao_remove_acentos_e_espacos_extras():
    assert normalizar("  Coronel  João Pessoa ") == "CORONEL JOAO PESSOA"


def test_nome_diretorio_seguro():
    assert nome_diretorio_seguro("CORONEL JOAO PESSOA") == "CORONEL_JOAO_PESSOA"
