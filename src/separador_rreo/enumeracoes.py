"""Enumerações do domínio RREO."""

from __future__ import annotations

from enum import Enum, IntEnum


class AnexoRreo(IntEnum):
    """Anexos RREO suportados pelo separador."""

    BALANCO_ORCAMENTARIO = 1
    DESPESAS_POR_FUNCAO = 2
    RECEITA_CORRENTE_LIQUIDA = 3
    RECEITAS_DESPESAS_PREVIDENCIARIAS = 4
    RESULTADOS_PRIMARIO_NOMINAL = 6
    RESTOS_A_PAGAR = 7
    MANUTENCAO_DESENVOLVIMENTO_ENSINO = 8
    RECEITAS_OPERACOES_CREDITO = 9
    PROJECAO_ATUARIAL_PREVIDENCIARIA = 10
    RECEITA_ALIENACAO_ATIVOS = 11
    RECEITAS_DESPESAS_SAUDE = 12
    PARCERIAS_PUBLICO_PRIVADAS = 13
    DEMONSTRATIVO_SIMPLIFICADO = 14


class SituacaoOcorrencia(str, Enum):
    """Situações possíveis durante a localização e o agrupamento de anexos."""

    ENCONTRADO = "Encontrado"
    VERIFICAR_LIMITE_FINAL = "Verificar limite final"
    ENCONTRADO_PARTES_REUNIDAS = "Encontrado - partes reunidas"
    VERIFICAR_PARTES_REUNIDAS = "Verificar partes reunidas"
    NAO_LOCALIZADO = "Nao localizado"

    def __str__(self) -> str:
        return self.value

    def com_multiplas_publicacoes(self) -> str:
        """Retorna o rótulo usado quando há mais de uma publicação do anexo."""
        return f"{self.value} - multiplas publicacoes"


class SituacaoConferencia(str, Enum):
    """Valores aceitos na conferência manual da planilha."""

    PENDENTE = "Pendente"
    CORRETO = "Correto"
    VERIFICAR = "Verificar"

    def __str__(self) -> str:
        return self.value


ANEXOS_PADRAO: tuple[AnexoRreo, ...] = tuple(AnexoRreo)
