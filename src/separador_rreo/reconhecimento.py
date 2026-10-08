"""Reconhecimento extensível de títulos de anexos RREO."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol

from separador_rreo.constantes import NUMEROS_ROMANOS
from separador_rreo.enumeracoes import ANEXOS_PADRAO, AnexoRreo
from separador_rreo.texto import normalizar

RegraFuncao = Callable[[str], int | AnexoRreo | None]


class RegraReconhecimento(Protocol):
    """Regra capaz de reconhecer um anexo a partir de uma linha."""

    def reconhecer(self, linha: str) -> int | AnexoRreo | None: ...


@dataclass(frozen=True, slots=True)
class RegraFuncaoAdaptada:
    """Adapta uma função simples ao contrato orientado a objetos."""

    funcao: RegraFuncao

    def reconhecer(self, linha: str) -> int | AnexoRreo | None:
        return self.funcao(linha)


class RegraAnexoExplicito:
    """Reconhece títulos no formato `ANEXO 01_RREO`."""

    _padrao = re.compile(r"\bANEXO\s*0*(\d{1,2})\s*[_-]\s*RREO(?=$|[^A-Z])")

    def reconhecer(self, linha: str) -> int | None:
        correspondencia = self._padrao.search(normalizar(linha))
        return int(correspondencia.group(1)) if correspondencia else None


class RegraCabecalhoQuartoBimestre:
    """Reconhece os formatos textuais usados nos cabeçalhos do quarto bimestre."""

    _cabecalho = re.compile(r"^RREO\s*[-–]?\s*(?:IV\s*BIM\b|4\s*[º°O]?\s*BIM\b)")
    _anexo_arabico = re.compile(r"\bANEXO\s*0*(\d{1,2})\b")
    _anexo_romano = re.compile(
        r"\bANEXO\s+(XIV|XIII|XII|XI|VIII|VII|VI|IV|III|II|IX|X|I)\b"
    )
    _palavras_chave: tuple[tuple[str, AnexoRreo], ...] = (
        ("BALANCO ORCAMENTARIO", AnexoRreo.BALANCO_ORCAMENTARIO),
        (
            "PREVIDENCIARIAS",
            AnexoRreo.RECEITAS_DESPESAS_PREVIDENCIARIAS,
        ),
        ("RESULTADO PRIMARIO", AnexoRreo.RESULTADOS_PRIMARIO_NOMINAL),
        ("RESULTADO NOMINAL", AnexoRreo.RESULTADOS_PRIMARIO_NOMINAL),
        (
            "ACOES E SERVICOS PUBLICOS DE SAUDE",
            AnexoRreo.RECEITAS_DESPESAS_SAUDE,
        ),
        ("RECEITA CORRENTE LIQUIDA", AnexoRreo.RECEITA_CORRENTE_LIQUIDA),
        ("RESTOS A PAGAR", AnexoRreo.RESTOS_A_PAGAR),
        (
            "DESPESAS COM MANUTENCAO",
            AnexoRreo.MANUTENCAO_DESENVOLVIMENTO_ENSINO,
        ),
        ("COM MDE", AnexoRreo.MANUTENCAO_DESENVOLVIMENTO_ENSINO),
        ("PARCERIAS PUBLICO", AnexoRreo.PARCERIAS_PUBLICO_PRIVADAS),
        ("DEMONSTRATIVO SIMPLIFICADO", AnexoRreo.DEMONSTRATIVO_SIMPLIFICADO),
    )

    def reconhecer(self, linha: str) -> int | AnexoRreo | None:
        texto = normalizar(linha)
        if not self._cabecalho.match(texto):
            return None

        correspondencia = self._anexo_arabico.search(texto)
        if correspondencia:
            return int(correspondencia.group(1))

        correspondencia = self._anexo_romano.search(texto)
        if correspondencia:
            return NUMEROS_ROMANOS[correspondencia.group(1)]

        for trecho, anexo in self._palavras_chave:
            if trecho in texto:
                return anexo
        return None


def regras_padrao() -> tuple[RegraReconhecimento, ...]:
    """Cria as regras conhecidas para publicações da FEMURN."""
    return (RegraAnexoExplicito(), RegraCabecalhoQuartoBimestre())


class ReconhecedorTituloRreo:
    """Aplica regras ordenadas para identificar títulos de anexos RREO."""

    def __init__(
        self,
        *,
        anexos_permitidos: Sequence[int | AnexoRreo] = ANEXOS_PADRAO,
        regras_adicionais: Iterable[RegraReconhecimento | RegraFuncao] = (),
        incluir_regras_padrao: bool = True,
    ) -> None:
        self._anexos_permitidos = frozenset(
            AnexoRreo(anexo) for anexo in anexos_permitidos
        )
        adicionais = tuple(self._adaptar_regra(regra) for regra in regras_adicionais)
        self._regras = (
            (*regras_padrao(), *adicionais) if incluir_regras_padrao else adicionais
        )

    @staticmethod
    def _adaptar_regra(
        regra: RegraReconhecimento | RegraFuncao,
    ) -> RegraReconhecimento:
        if hasattr(regra, "reconhecer"):
            return regra  # type: ignore[return-value]
        return RegraFuncaoAdaptada(regra)  # type: ignore[arg-type]

    @property
    def anexos_permitidos(self) -> frozenset[AnexoRreo]:
        return self._anexos_permitidos

    def reconhecer(self, linha: str) -> AnexoRreo | None:
        for regra in self._regras:
            numero = regra.reconhecer(linha)
            if numero is None:
                continue
            try:
                anexo = AnexoRreo(numero)
            except ValueError:
                continue
            if anexo in self._anexos_permitidos:
                return anexo
        return None
