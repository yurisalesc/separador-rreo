"""Separador RREO — extrai anexos RREO de diários oficiais FEMURN."""

from separador_rreo.exporter import ExportResult, RreoExporter
from separador_rreo.models import AnalysisResult, Finding
from separador_rreo.pipeline import SeparadorRreo, separar
from separador_rreo.recognition import AnexoRecognizer

__all__ = [
    "AnalysisResult",
    "AnexoRecognizer",
    "ExportResult",
    "Finding",
    "RreoExporter",
    "SeparadorRreo",
    "separar",
    "__version__",
]

__version__ = "0.1.0"
