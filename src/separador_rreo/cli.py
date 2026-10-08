"""Interface de linha de comando do separador-rreo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from separador_rreo import __version__
from separador_rreo.aplicacao import SeparadorRreo


def criar_analisador_argumentos() -> argparse.ArgumentParser:
    analisador = argparse.ArgumentParser(
        prog="separador-rreo",
        description=(
            "Separa anexos RREO de diários oficiais FEMURN em PDFs por município, "
            "com planilha de conferência e ZIP."
        ),
    )
    analisador.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        help=(
            "Caminho do PDF do diário (opcional; pergunta interativamente se omitido)."
        ),
    )
    analisador.add_argument(
        "--municipios",
        nargs="+",
        metavar="NOME",
        help='Municípios a extrair, ex.: --municipios "Bodó" "Angicos"',
    )
    analisador.add_argument(
        "--saida",
        default="RREO_separados",
        type=Path,
        help="Pasta de saída (padrão: RREO_separados).",
    )
    analisador.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return analisador


def _resolver_pdf(informado: Path | None) -> Path:
    if informado is not None:
        return informado

    pdfs = sorted(Path.cwd().glob("*.pdf"))
    if len(pdfs) == 1:
        print(f"PDF: {pdfs[0]}")
        return pdfs[0]

    print("PDFs encontrados:", ", ".join(path.name for path in pdfs) or "nenhum")
    digitado = input("Digite o nome/caminho do PDF: ").strip().strip('"')
    return Path(digitado)


def _resolver_municipios(informados: list[str] | None) -> list[str]:
    if informados:
        return informados
    digitado = input("Municípios separados por vírgula: ")
    return [parte.strip() for parte in digitado.split(",") if parte.strip()]


def main(argumentos: list[str] | None = None) -> int:
    analisador_argumentos = criar_analisador_argumentos()
    opcoes = analisador_argumentos.parse_args(argumentos)

    caminho_pdf = _resolver_pdf(opcoes.pdf)
    if not caminho_pdf.is_file():
        analisador_argumentos.error(f"PDF não encontrado: {caminho_pdf}")

    municipios = _resolver_municipios(opcoes.municipios)
    if not municipios:
        analisador_argumentos.error("Informe municípios.")

    try:
        analise, exportacao = SeparadorRreo().executar(
            caminho_pdf, municipios, opcoes.saida
        )
    except ValueError as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1

    for municipio, ocorrencias in analise.ocorrencias_por_municipio.items():
        if not ocorrencias:
            print(f"{municipio} | nenhum anexo localizado")
            continue
        for ocorrencia in ocorrencias:
            print(
                f"{municipio} | RREO {int(ocorrencia.anexo):02d} | "
                f"{ocorrencia.pagina_inicial}-{ocorrencia.pagina_final} | "
                f"{ocorrencia.situacao.value}"
            )

    print(
        f"PDFs criados: {exportacao.quantidade_pdfs}; "
        f"planilha: {exportacao.planilha}; "
        f"ZIP: {exportacao.arquivo_zip}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
