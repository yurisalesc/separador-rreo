"""Análise de diários FEMURN para localizar anexos RREO por município."""

from __future__ import annotations

import bisect
import re
from collections.abc import Sequence

from separador_rreo.contratos import DocumentoPdf, ReconhecedorTitulo
from separador_rreo.enumeracoes import SituacaoOcorrencia
from separador_rreo.modelos import (
    MarcadorCodigo,
    MarcadorSecao,
    Ocorrencia,
    ResultadoAnalise,
    TituloLocalizado,
)
from separador_rreo.reconhecimento import ReconhecedorTituloRreo
from separador_rreo.texto import normalizar

PADRAO_CABECALHO = re.compile(
    r"(?m)^[ \t]*PREFEITURA MUNICIPAL DE[ \t]+([A-ZÀ-Ú][A-ZÀ-Ú \-']{2,55})[ \t]*$"
)
PADRAO_CODIGO = re.compile(r"C[oó]digo\s+Identificador\s*:\s*[A-Z0-9]{6,12}", re.I)


class AnalisadorRreo:
    """Transforma o texto de um diário em ocorrências de anexos por município."""

    def __init__(self, reconhecedor: ReconhecedorTitulo | None = None) -> None:
        self._reconhecedor = reconhecedor or ReconhecedorTituloRreo()

    def analisar(
        self, documento: DocumentoPdf, municipios: Sequence[str]
    ) -> ResultadoAnalise:
        textos = [documento.texto_da_pagina(i) for i in range(len(documento))]
        deslocamentos: list[int] = []
        secoes: list[MarcadorSecao] = []
        titulos: list[TituloLocalizado] = []
        codigos: list[MarcadorCodigo] = []
        posicao = 0

        for indice_pagina, texto in enumerate(textos):
            deslocamentos.append(posicao)
            self._coletar_marcadores(
                texto, indice_pagina, posicao, secoes, titulos, codigos
            )
            posicao += len(texto) + 1

        secoes.sort(key=lambda item: item.deslocamento)
        codigos.sort(key=lambda item: item.inicio)
        titulos.sort(key=lambda item: item.deslocamento)
        titulos = self._descartar_cabecalhos_de_continuacao(titulos, secoes, codigos)

        if not secoes:
            raise ValueError(
                "Não encontrei cabeçalhos de prefeituras. "
                "Confira se o PDF possui texto selecionável."
            )

        ocorrencias = self._localizar_ocorrencias(
            titulos=titulos,
            secoes=secoes,
            codigos=codigos,
            deslocamentos=deslocamentos,
            municipios=municipios,
            fim_documento=posicao,
            quantidade_paginas=len(documento),
        )
        return ResultadoAnalise(
            ocorrencias_por_municipio=ocorrencias,
            quantidade_paginas=len(documento),
            origem=documento.caminho,
        )

    def _coletar_marcadores(
        self,
        texto: str,
        indice_pagina: int,
        posicao: int,
        secoes: list[MarcadorSecao],
        titulos: list[TituloLocalizado],
        codigos: list[MarcadorCodigo],
    ) -> None:
        for correspondencia in PADRAO_CABECALHO.finditer(texto):
            secoes.append(
                MarcadorSecao(
                    posicao + correspondencia.start(),
                    normalizar(correspondencia.group(1)),
                )
            )
        for correspondencia in PADRAO_CODIGO.finditer(texto):
            codigos.append(
                MarcadorCodigo(
                    posicao + correspondencia.start(),
                    posicao + correspondencia.end(),
                )
            )

        linhas = texto.splitlines(keepends=True)
        contexto_rreo = self._pagina_contem_rreo(texto)
        anexos_na_pagina: set[int] = set()
        cursor = 0
        for indice_linha, linha in enumerate(linhas):
            anexo, titulo_original = self._reconhecer_titulo(
                linhas, indice_linha, contexto_rreo
            )
            if anexo is not None and int(anexo) not in anexos_na_pagina:
                titulos.append(
                    TituloLocalizado(
                        deslocamento=posicao + cursor,
                        pagina=indice_pagina + 1,
                        anexo=anexo,
                        titulo_original=titulo_original,
                    )
                )
                anexos_na_pagina.add(int(anexo))
            cursor += len(linha)

    def _reconhecer_titulo(
        self,
        linhas: list[str],
        indice_linha: int,
        contexto_rreo: bool,
    ) -> tuple[int | None, str]:
        """Tenta reconhecer o título na linha atual e em janelas de até três linhas."""
        for tamanho in (1, 2, 3):
            trecho = linhas[indice_linha : indice_linha + tamanho]
            if len(trecho) < tamanho:
                break
            titulo = " ".join(linha.strip() for linha in trecho if linha.strip())
            if not titulo:
                continue
            anexo = self._reconhecedor.reconhecer(titulo, contexto_rreo=contexto_rreo)
            if anexo is not None:
                return anexo, titulo
        return None, linhas[indice_linha].strip()

    @staticmethod
    def _pagina_contem_rreo(texto: str) -> bool:
        normalizado = normalizar(texto)
        return "RREO" in normalizado or (
            "RELATORIO RESUMIDO" in normalizado
            and "EXECUCAO ORCAMENTARIA" in normalizado
        )

    @staticmethod
    def _descartar_cabecalhos_de_continuacao(
        titulos: list[TituloLocalizado],
        secoes: list[MarcadorSecao],
        codigos: list[MarcadorCodigo],
    ) -> list[TituloLocalizado]:
        """Ignora cabeçalhos repetidos do mesmo anexo antes do código identificador."""
        if not titulos:
            return []

        inicio_secoes = [item.deslocamento for item in secoes]
        inicio_codigos = [item.inicio for item in codigos]
        filtrados: list[TituloLocalizado] = []

        for titulo in titulos:
            if not filtrados:
                filtrados.append(titulo)
                continue

            anterior = filtrados[-1]
            if anterior.anexo != titulo.anexo:
                filtrados.append(titulo)
                continue

            secao_atual = bisect.bisect_right(inicio_secoes, titulo.deslocamento) - 1
            secao_anterior = (
                bisect.bisect_right(inicio_secoes, anterior.deslocamento) - 1
            )
            if secao_atual != secao_anterior:
                filtrados.append(titulo)
                continue

            indice_codigo = bisect.bisect_right(inicio_codigos, anterior.deslocamento)
            if (
                indice_codigo < len(codigos)
                and codigos[indice_codigo].inicio < titulo.deslocamento
            ):
                filtrados.append(titulo)
                continue

        return filtrados

    @staticmethod
    def _localizar_ocorrencias(
        *,
        titulos: list[TituloLocalizado],
        secoes: list[MarcadorSecao],
        codigos: list[MarcadorCodigo],
        deslocamentos: list[int],
        municipios: Sequence[str],
        fim_documento: int,
        quantidade_paginas: int,
    ) -> dict[str, list[Ocorrencia]]:
        resultado: dict[str, list[Ocorrencia]] = {
            normalizar(nome): [] for nome in municipios
        }
        inicio_secoes = [item.deslocamento for item in secoes]
        inicio_codigos = [item.inicio for item in codigos]

        for indice, titulo in enumerate(titulos):
            indice_secao = bisect.bisect_right(inicio_secoes, titulo.deslocamento) - 1
            if indice_secao < 0:
                continue

            municipio = secoes[indice_secao].municipio
            if municipio not in resultado:
                continue

            proxima_secao = (
                inicio_secoes[indice_secao + 1]
                if indice_secao + 1 < len(inicio_secoes)
                else fim_documento
            )
            proximo_titulo = (
                titulos[indice + 1].deslocamento
                if indice + 1 < len(titulos)
                else fim_documento
            )
            indice_codigo = bisect.bisect_right(inicio_codigos, titulo.deslocamento)
            limite = min(proxima_secao, proximo_titulo)

            if indice_codigo < len(codigos) and codigos[indice_codigo].inicio < limite:
                fim = codigos[indice_codigo].fim
                situacao = SituacaoOcorrencia.ENCONTRADO
            else:
                # Sem código: recorta até o próximo artigo e pede conferência.
                fim = limite - 1
                situacao = SituacaoOcorrencia.VERIFICAR_LIMITE_FINAL

            pagina_final = bisect.bisect_right(deslocamentos, fim - 1)
            pagina_final = max(titulo.pagina, min(pagina_final, quantidade_paginas))
            resultado[municipio].append(
                Ocorrencia(
                    anexo=titulo.anexo,
                    pagina_inicial=titulo.pagina,
                    pagina_final=pagina_final,
                    situacao=situacao,
                    titulo=titulo.titulo_original,
                )
            )
        return resultado


HEADER_RE = PADRAO_CABECALHO
CODE_RE = PADRAO_CODIGO
