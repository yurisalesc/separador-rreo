from separador_rreo import AnexoRreo, ReconhecedorTituloRreo


def test_reconhece_anexo_rreo_explicito():
    reconhecedor = ReconhecedorTituloRreo()
    assert reconhecedor.reconhecer("ANEXO 01_RREO") == AnexoRreo.BALANCO_ORCAMENTARIO
    assert (
        reconhecedor.reconhecer("ANEXO 12 - RREO") == AnexoRreo.RECEITAS_DESPESAS_SAUDE
    )


def test_reconhece_quarto_bimestre_com_anexo_romano():
    reconhecedor = ReconhecedorTituloRreo()
    assert (
        reconhecedor.reconhecer(
            "RREO - IV BIM - ANEXO XIV - DEMONSTRATIVO SIMPLIFICADO"
        )
        == AnexoRreo.DEMONSTRATIVO_SIMPLIFICADO
    )


def test_reconhece_palavra_chave_balanco():
    reconhecedor = ReconhecedorTituloRreo()
    assert (
        reconhecedor.reconhecer("RREO - 4º BIM - BALANÇO ORÇAMENTÁRIO")
        == AnexoRreo.BALANCO_ORCAMENTARIO
    )


def test_ignora_citacao_que_nao_e_cabecalho():
    reconhecedor = ReconhecedorTituloRreo()
    assert (
        reconhecedor.reconhecer("conforme o RREO do anexo 1 mencionado abaixo") is None
    )


def test_regra_adicional_preserva_regras_padrao():
    def regra_personalizada(linha: str) -> int | None:
        return 9 if "ANEXO PERSONALIZADO NOVE" in linha.upper() else None

    reconhecedor = ReconhecedorTituloRreo(regras_adicionais=[regra_personalizada])
    assert (
        reconhecedor.reconhecer("ANEXO PERSONALIZADO NOVE")
        == AnexoRreo.RECEITAS_OPERACOES_CREDITO
    )
    assert reconhecedor.reconhecer("ANEXO 01_RREO") == AnexoRreo.BALANCO_ORCAMENTARIO


def test_ignora_anexo_de_gestao_fiscal():
    reconhecedor = ReconhecedorTituloRreo()
    assert (
        reconhecedor.reconhecer(
            "ANEXO 06_RGF_DEMONSTRATIVO SIMPLIFICADO DO RELATÓRIO DE GESTÃO FISCAL",
            contexto_rreo=True,
        )
        is None
    )


def test_reconhece_despesas_por_funcao_no_cabecalho_do_quarto_bimestre():
    reconhecedor = ReconhecedorTituloRreo()
    assert (
        reconhecedor.reconhecer("RREO - IV BIM - DEMONSTRATIVO DAS DESPESAS POR FUNÇÃO")
        == AnexoRreo.DESPESAS_POR_FUNCAO
    )


def test_filtra_anexos_permitidos():
    reconhecedor = ReconhecedorTituloRreo(
        anexos_permitidos=[AnexoRreo.BALANCO_ORCAMENTARIO]
    )

    assert reconhecedor.reconhecer("ANEXO 01_RREO") is not None
    assert reconhecedor.reconhecer("ANEXO 12_RREO") is None
