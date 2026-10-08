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

PADRAO_NUMERO_ANEXO = (
    r"(?P<arabico>\d{1,2})|"
    r"(?P<romano>XIV|XIII|XII|XI|VIII|VII|VI|IV|III|II|IX|X|I)"
)

PALAVRAS_CHAVE_ANEXOS: tuple[tuple[str, AnexoRreo], ...] = (
    ("DEMONSTRATIVO SIMPLIFICADO", AnexoRreo.DEMONSTRATIVO_SIMPLIFICADO),
    ("BALANCO ORCAMENTARIO", AnexoRreo.BALANCO_ORCAMENTARIO),
    ("DESPESAS POR FUNCAO", AnexoRreo.DESPESAS_POR_FUNCAO),
    ("RECEITA CORRENTE LIQUIDA", AnexoRreo.RECEITA_CORRENTE_LIQUIDA),
    (
        "RECEITAS E DESPESAS PREVIDENCIARIAS",
        AnexoRreo.RECEITAS_DESPESAS_PREVIDENCIARIAS,
    ),
    ("PREVIDENCIARIAS", AnexoRreo.RECEITAS_DESPESAS_PREVIDENCIARIAS),
    ("RESULTADO PRIMARIO", AnexoRreo.RESULTADOS_PRIMARIO_NOMINAL),
    ("RESULTADO NOMINAL", AnexoRreo.RESULTADOS_PRIMARIO_NOMINAL),
    ("RESTOS A PAGAR", AnexoRreo.RESTOS_A_PAGAR),
    (
        "MANUTENCAO E DESENVOLVIMENTO DO ENSINO",
        AnexoRreo.MANUTENCAO_DESENVOLVIMENTO_ENSINO,
    ),
    ("COM MDE", AnexoRreo.MANUTENCAO_DESENVOLVIMENTO_ENSINO),
    (
        "OPERACOES DE CREDITO E DESPESAS DE CAPITAL",
        AnexoRreo.RECEITAS_OPERACOES_CREDITO,
    ),
    ("PROJECAO ATUARIAL", AnexoRreo.PROJECAO_ATUARIAL_PREVIDENCIARIA),
    ("ALIENACAO DE ATIVOS", AnexoRreo.RECEITA_ALIENACAO_ATIVOS),
    (
        "ACOES E SERVICOS PUBLICOS DE SAUDE",
        AnexoRreo.RECEITAS_DESPESAS_SAUDE,
    ),
    (
        "RECEITAS DE IMPOSTOS E DESPESAS PROPRIAS COM SAUDE",
        AnexoRreo.RECEITAS_DESPESAS_SAUDE,
    ),
    ("PARCERIAS PUBLICO", AnexoRreo.PARCERIAS_PUBLICO_PRIVADAS),
)


class RegraReconhecimento(Protocol):
    """Regra capaz de reconhecer um anexo a partir de uma linha."""

    def reconhecer(
        self, linha: str, *, contexto_rreo: bool = False
    ) -> int | AnexoRreo | None: ...


@dataclass(frozen=True, slots=True)
class RegraFuncaoAdaptada:
    """Adapta uma função simples ao contrato orientado a objetos."""

    funcao: RegraFuncao

    def reconhecer(
        self, linha: str, *, contexto_rreo: bool = False
    ) -> int | AnexoRreo | None:
        return self.funcao(linha)


def _numero_do_anexo(correspondencia: re.Match[str]) -> int:
    """Converte o grupo arábico ou romano de uma expressão em número."""
    if correspondencia.group("arabico"):
        return int(correspondencia.group("arabico"))
    return NUMEROS_ROMANOS[correspondencia.group("romano")]


class RegraAnexoExplicito:
    """Reconhece títulos no formato `ANEXO 01_RREO`."""

    _padrao = re.compile(r"\bANEXO\s*0*(\d{1,2})\s*[_-]\s*RREO(?=$|[^A-Z])")

    def reconhecer(self, linha: str, *, contexto_rreo: bool = False) -> int | None:
        correspondencia = self._padrao.search(normalizar(linha))
        return int(correspondencia.group(1)) if correspondencia else None


class RegraRreoComAnexo:
    """Reconhece variações em que RREO aparece antes do número do anexo."""

    _padrao_direto = re.compile(
        rf"\bRREO\s*[-–]?\s*ANEXO\s*(?:{PADRAO_NUMERO_ANEXO})\b"
    )
    _padrao_titulo = re.compile(
        rf"^RREO\b.{{0,60}}?\bANEXO\s*(?:{PADRAO_NUMERO_ANEXO})\b"
    )

    def reconhecer(self, linha: str, *, contexto_rreo: bool = False) -> int | None:
        texto = normalizar(linha)
        correspondencia = self._padrao_direto.search(texto)
        if correspondencia is None:
            correspondencia = self._padrao_titulo.search(texto)
        return _numero_do_anexo(correspondencia) if correspondencia else None


class RegraNomeArquivoAnexo:
    """Reconhece linhas como `1. Anexo 1 - Balanco ... .pdf`."""

    _padrao = re.compile(
        rf"^\d+\s*[.)-]\s*ANEXO\s*(?:{PADRAO_NUMERO_ANEXO})\b.*\.PDF\b"
    )

    def reconhecer(self, linha: str, *, contexto_rreo: bool = False) -> int | None:
        if not contexto_rreo:
            return None
        correspondencia = self._padrao.search(normalizar(linha))
        return _numero_do_anexo(correspondencia) if correspondencia else None


class RegraAnexoDescritivo:
    """Reconhece `ANEXO N - DEMONSTRATIVO...` dentro de uma publicação RREO."""

    _padrao = re.compile(
        rf"^ANEXO\s*(?:{PADRAO_NUMERO_ANEXO})\s*[-–_]\s*(?P<descricao>.+)"
    )

    def reconhecer(self, linha: str, *, contexto_rreo: bool = False) -> int | None:
        if not contexto_rreo:
            return None
        correspondencia = self._padrao.search(normalizar(linha))
        if correspondencia is None:
            return None
        descricao = correspondencia.group("descricao")
        if not any(trecho in descricao for trecho, _ in PALAVRAS_CHAVE_ANEXOS):
            return None
        return _numero_do_anexo(correspondencia)


class RegraTituloSemantico:
    """Infere o anexo pelo nome oficial do demonstrativo."""

    _marcadores_relatorio = (
        "RELATORIO RESUMIDO DE EXECUCAO ORCAMENTARIA",
        "RELATORIO RESUMIDO DA EXECUCAO ORCAMENTARIA",
    )

    def reconhecer(
        self, linha: str, *, contexto_rreo: bool = False
    ) -> AnexoRreo | None:
        if not contexto_rreo:
            return None
        texto = normalizar(linha)
        if not any(marcador in texto for marcador in self._marcadores_relatorio):
            return None
        for trecho, anexo in PALAVRAS_CHAVE_ANEXOS:
            if trecho in texto:
                return anexo
        return None


class RegraCabecalhoQuartoBimestre:
    """Reconhece os formatos textuais usados nos cabeçalhos do quarto bimestre."""

    _cabecalho = re.compile(r"^RREO\s*[-–]?\s*(?:IV\s*BIM\b|4\s*[º°O]?\s*BIM\b)")
    _anexo_arabico = re.compile(r"\bANEXO\s*0*(\d{1,2})\b")
    _anexo_romano = re.compile(
        r"\bANEXO\s+(XIV|XIII|XII|XI|VIII|VII|VI|IV|III|II|IX|X|I)\b"
    )

    def reconhecer(
        self, linha: str, *, contexto_rreo: bool = False
    ) -> int | AnexoRreo | None:
        texto = normalizar(linha)
        if not self._cabecalho.match(texto):
            return None

        correspondencia = self._anexo_arabico.search(texto)
        if correspondencia:
            return int(correspondencia.group(1))

        correspondencia = self._anexo_romano.search(texto)
        if correspondencia:
            return NUMEROS_ROMANOS[correspondencia.group(1)]

        for trecho, anexo in PALAVRAS_CHAVE_ANEXOS:
            if trecho in texto:
                return anexo
        return None


def regras_padrao() -> tuple[RegraReconhecimento, ...]:
    """Cria as regras conhecidas para publicações da FEMURN."""
    return (
        RegraAnexoExplicito(),
        RegraRreoComAnexo(),
        RegraNomeArquivoAnexo(),
        RegraAnexoDescritivo(),
        RegraCabecalhoQuartoBimestre(),
        RegraTituloSemantico(),
    )


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

    def reconhecer(
        self, linha: str, *, contexto_rreo: bool = False
    ) -> AnexoRreo | None:
        for regra in self._regras:
            numero = regra.reconhecer(linha, contexto_rreo=contexto_rreo)
            if numero is None:
                continue
            try:
                anexo = AnexoRreo(numero)
            except ValueError:
                continue
            if anexo in self._anexos_permitidos:
                return anexo
        return None
