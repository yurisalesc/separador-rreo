from separador_rreo import (
    AnexoRreo,
    SituacaoConferencia,
    SituacaoOcorrencia,
)


def test_enum_anexo_comporta_se_como_inteiro():
    assert AnexoRreo.BALANCO_ORCAMENTARIO == 1
    assert f"{AnexoRreo.DEMONSTRATIVO_SIMPLIFICADO:02d}" == "14"


def test_enums_situacao_preservam_rotulos_externos():
    assert SituacaoOcorrencia.ENCONTRADO.value == "Encontrado"
    assert (
        SituacaoOcorrencia.ENCONTRADO.com_multiplas_publicacoes()
        == "Encontrado - multiplas publicacoes"
    )
    assert [item.value for item in SituacaoConferencia] == [
        "Pendente",
        "Correto",
        "Verificar",
    ]
