from separador_rreo import AnexoRreo, Ocorrencia, SituacaoOcorrencia
from separador_rreo.agrupamento import AgrupadorOcorrencias


def test_reune_partes_sequenciais():
    ocorrencias = [
        Ocorrencia(
            AnexoRreo.BALANCO_ORCAMENTARIO, 10, 12, SituacaoOcorrencia.ENCONTRADO, "t1"
        ),
        Ocorrencia(
            AnexoRreo.BALANCO_ORCAMENTARIO, 13, 15, SituacaoOcorrencia.ENCONTRADO, "t2"
        ),
        Ocorrencia(
            AnexoRreo.BALANCO_ORCAMENTARIO, 20, 22, SituacaoOcorrencia.ENCONTRADO, "t3"
        ),
    ]
    grupos = AgrupadorOcorrencias().agrupar(ocorrencias)
    assert len(grupos) == 2
    assert grupos[0].pagina_inicial == 10
    assert grupos[0].pagina_final == 15
    assert grupos[0].situacao is SituacaoOcorrencia.ENCONTRADO_PARTES_REUNIDAS
    assert grupos[1].pagina_inicial == 20


def test_marca_verificacao_quando_as_situacoes_sao_mistas():
    ocorrencias = [
        Ocorrencia(
            AnexoRreo.BALANCO_ORCAMENTARIO, 10, 12, SituacaoOcorrencia.ENCONTRADO, "t1"
        ),
        Ocorrencia(
            AnexoRreo.BALANCO_ORCAMENTARIO,
            13,
            15,
            SituacaoOcorrencia.VERIFICAR_LIMITE_FINAL,
            "t2",
        ),
    ]
    grupos = AgrupadorOcorrencias().agrupar(ocorrencias)
    assert len(grupos) == 1
    assert grupos[0].situacao is SituacaoOcorrencia.VERIFICAR_PARTES_REUNIDAS
