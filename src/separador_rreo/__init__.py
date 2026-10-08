"""Separador RREO — extrai anexos RREO de diários oficiais FEMURN."""

from separador_rreo.analisador import AnalisadorRreo
from separador_rreo.aplicacao import SeparadorRreo, separar_rreo
from separador_rreo.enumeracoes import (
    AnexoRreo,
    SituacaoConferencia,
    SituacaoOcorrencia,
)
from separador_rreo.exportacao import ExportadorRreo
from separador_rreo.modelos import (
    Ocorrencia,
    ResultadoAnalise,
    ResultadoExportacao,
)
from separador_rreo.reconhecimento import ReconhecedorTituloRreo

__all__ = [
    "AnalisadorRreo",
    "AnexoRreo",
    "ExportadorRreo",
    "Ocorrencia",
    "ReconhecedorTituloRreo",
    "ResultadoAnalise",
    "ResultadoExportacao",
    "SeparadorRreo",
    "SituacaoConferencia",
    "SituacaoOcorrencia",
    "separar_rreo",
    "__version__",
]

__version__ = "0.1.0"
