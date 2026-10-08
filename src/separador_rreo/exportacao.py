"""Coordenação da exportação de PDFs, planilha e arquivo ZIP."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from separador_rreo.agrupamento import AgrupadorOcorrencias
from separador_rreo.compactacao import CompactadorZip
from separador_rreo.contratos import DocumentoPdf
from separador_rreo.enumeracoes import (
    ANEXOS_PADRAO,
    AnexoRreo,
    SituacaoConferencia,
    SituacaoOcorrencia,
)
from separador_rreo.modelos import (
    LinhaConferencia,
    Ocorrencia,
    ResultadoAnalise,
    ResultadoExportacao,
)
from separador_rreo.planilha import GeradorPlanilhaConferencia
from separador_rreo.texto import nome_diretorio_seguro


class ExportadorRreo:
    """Coordena a criação dos artefatos sem conhecer detalhes de apresentação."""

    def __init__(
        self,
        anexos: Sequence[int | AnexoRreo] = ANEXOS_PADRAO,
        *,
        agrupador: AgrupadorOcorrencias | None = None,
        gerador_planilha: GeradorPlanilhaConferencia | None = None,
        compactador: CompactadorZip | None = None,
    ) -> None:
        self._anexos = tuple(AnexoRreo(anexo) for anexo in anexos)
        self._agrupador = agrupador or AgrupadorOcorrencias()
        self._gerador_planilha = gerador_planilha or GeradorPlanilhaConferencia()
        self._compactador = compactador or CompactadorZip()

    def exportar(
        self,
        documento: DocumentoPdf,
        analise: ResultadoAnalise,
        destino: Path | str,
    ) -> ResultadoExportacao:
        diretorio_saida = Path(destino)
        diretorio_saida.mkdir(parents=True, exist_ok=True)
        linhas: list[LinhaConferencia] = []
        quantidade_pdfs = 0

        for municipio, ocorrencias in analise.ocorrencias_por_municipio.items():
            pasta_municipio = diretorio_saida / nome_diretorio_seguro(municipio)
            pasta_municipio.mkdir(exist_ok=True)

            for anexo in self._anexos:
                grupos = self._grupos_do_anexo(ocorrencias, anexo)
                if not grupos:
                    linhas.append(self._linha_nao_localizada(municipio, anexo))
                    continue

                for indice, ocorrencia in enumerate(grupos, start=1):
                    nome_arquivo = self._nome_arquivo(
                        municipio, anexo, indice, len(grupos)
                    )
                    documento.extrair_paginas(
                        ocorrencia.pagina_inicial,
                        ocorrencia.pagina_final,
                        pasta_municipio / nome_arquivo,
                    )
                    quantidade_pdfs += 1
                    linhas.append(
                        LinhaConferencia(
                            municipio=municipio,
                            anexo=anexo,
                            pagina_inicial=ocorrencia.pagina_inicial,
                            pagina_final=ocorrencia.pagina_final,
                            situacao=ocorrencia.situacao,
                            conferencia=SituacaoConferencia.PENDENTE,
                            titulo=ocorrencia.titulo,
                            arquivo=nome_arquivo,
                            multiplas_publicacoes=len(grupos) > 1,
                        )
                    )

        planilha = diretorio_saida / "Controle_Publicacoes.xlsx"
        self._gerador_planilha.gerar(linhas, planilha)
        arquivo_zip = self._compactador.compactar(diretorio_saida)

        return ResultadoExportacao(
            diretorio_saida=diretorio_saida.resolve(),
            planilha=planilha.resolve(),
            arquivo_zip=arquivo_zip.resolve(),
            quantidade_pdfs=quantidade_pdfs,
            linhas=tuple(linhas),
        )

    def _grupos_do_anexo(
        self, ocorrencias: Sequence[Ocorrencia], anexo: AnexoRreo
    ) -> list[Ocorrencia]:
        filtradas = sorted(
            (item for item in ocorrencias if item.anexo == anexo),
            key=lambda item: (item.pagina_inicial, item.pagina_final),
        )
        return self._agrupador.agrupar(filtradas)

    @staticmethod
    def _linha_nao_localizada(municipio: str, anexo: AnexoRreo) -> LinhaConferencia:
        return LinhaConferencia(
            municipio=municipio,
            anexo=anexo,
            pagina_inicial=None,
            pagina_final=None,
            situacao=SituacaoOcorrencia.NAO_LOCALIZADO,
            conferencia=SituacaoConferencia.VERIFICAR,
            titulo=None,
            arquivo=None,
        )

    @staticmethod
    def _nome_arquivo(
        municipio: str,
        anexo: AnexoRreo,
        indice: int,
        quantidade_publicacoes: int,
    ) -> str:
        sufixo = f"_publicacao_{indice}" if quantidade_publicacoes > 1 else ""
        return f"RREO_{int(anexo):02d}_{municipio}{sufixo}.pdf"
