"""Regras para reunir partes sequenciais do mesmo anexo."""

from __future__ import annotations

from collections.abc import Iterable

from separador_rreo.enumeracoes import SituacaoOcorrencia
from separador_rreo.modelos import Ocorrencia


class AgrupadorOcorrencias:
    """Agrupa ocorrências adjacentes sem misturar publicações separadas."""

    def agrupar(self, ocorrencias: Iterable[Ocorrencia]) -> list[Ocorrencia]:
        grupos: list[Ocorrencia] = []
        for ocorrencia in ocorrencias:
            if grupos and ocorrencia.pagina_inicial <= grupos[-1].pagina_final + 1:
                grupos[-1] = self._reunir(grupos[-1], ocorrencia)
            else:
                grupos.append(ocorrencia)
        return grupos

    @staticmethod
    def _reunir(anterior: Ocorrencia, atual: Ocorrencia) -> Ocorrencia:
        encontrados = {
            SituacaoOcorrencia.ENCONTRADO,
            SituacaoOcorrencia.ENCONTRADO_PARTES_REUNIDAS,
        }
        if anterior.situacao in encontrados and atual.situacao in encontrados:
            situacao = SituacaoOcorrencia.ENCONTRADO_PARTES_REUNIDAS
        else:
            situacao = SituacaoOcorrencia.VERIFICAR_PARTES_REUNIDAS

        return Ocorrencia(
            anexo=atual.anexo,
            pagina_inicial=anterior.pagina_inicial,
            pagina_final=max(anterior.pagina_final, atual.pagina_final),
            situacao=situacao,
            titulo=f"{anterior.titulo} / {atual.titulo}",
        )
