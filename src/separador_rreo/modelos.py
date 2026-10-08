"""Modelos de domínio usados pela análise e pela exportação."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from separador_rreo.enumeracoes import (
    AnexoRreo,
    SituacaoConferencia,
    SituacaoOcorrencia,
)
from separador_rreo.texto import normalizar


@dataclass(frozen=True, slots=True)
class MarcadorSecao:
    """Cabeçalho de prefeitura encontrado no texto concatenado do PDF."""

    deslocamento: int
    municipio: str


@dataclass(frozen=True, slots=True)
class MarcadorCodigo:
    """Marcador de código identificador que costuma encerrar o artigo."""

    inicio: int
    fim: int


@dataclass(frozen=True, slots=True)
class TituloLocalizado:
    """Título de anexo RREO reconhecido no PDF."""

    deslocamento: int
    pagina: int
    anexo: AnexoRreo
    titulo_original: str


@dataclass(frozen=True, slots=True)
class Ocorrencia:
    """Trecho de um anexo localizado para um município."""

    anexo: AnexoRreo
    pagina_inicial: int
    pagina_final: int
    situacao: SituacaoOcorrencia
    titulo: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "anexo", AnexoRreo(self.anexo))
        object.__setattr__(self, "situacao", SituacaoOcorrencia(self.situacao))


@dataclass(frozen=True, slots=True)
class LinhaConferencia:
    """Linha tipada da planilha e do resultado de exportação."""

    municipio: str
    anexo: AnexoRreo
    pagina_inicial: int | None
    pagina_final: int | None
    situacao: SituacaoOcorrencia
    conferencia: SituacaoConferencia
    titulo: str | None
    arquivo: str | None
    multiplas_publicacoes: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "anexo", AnexoRreo(self.anexo))
        object.__setattr__(self, "situacao", SituacaoOcorrencia(self.situacao))
        object.__setattr__(self, "conferencia", SituacaoConferencia(self.conferencia))

    @property
    def total_paginas(self) -> int | None:
        if self.pagina_inicial is None or self.pagina_final is None:
            return None
        return self.pagina_final - self.pagina_inicial + 1

    @property
    def rotulo_situacao(self) -> str:
        if self.multiplas_publicacoes:
            return self.situacao.com_multiplas_publicacoes()
        return self.situacao.value


@dataclass(slots=True)
class ResultadoAnalise:
    """Resultado da análise de um diário FEMURN."""

    ocorrencias_por_municipio: dict[str, list[Ocorrencia]] = field(default_factory=dict)
    quantidade_paginas: int = 0
    origem: Path | None = None

    def do_municipio(self, municipio: str) -> list[Ocorrencia]:
        return list(self.ocorrencias_por_municipio.get(normalizar(municipio), []))

    @property
    def municipios(self) -> tuple[str, ...]:
        return tuple(sorted(self.ocorrencias_por_municipio))


@dataclass(frozen=True, slots=True)
class ResultadoExportacao:
    """Artefatos gerados após a exportação."""

    diretorio_saida: Path
    planilha: Path
    arquivo_zip: Path
    quantidade_pdfs: int
    linhas: tuple[LinhaConferencia, ...]


__all__ = [
    "LinhaConferencia",
    "MarcadorCodigo",
    "MarcadorSecao",
    "Ocorrencia",
    "ResultadoAnalise",
    "ResultadoExportacao",
    "TituloLocalizado",
]
