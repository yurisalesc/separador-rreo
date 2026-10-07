"""Interface de linha de comando do separador-rreo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from separador_rreo import __version__
from separador_rreo.pipeline import SeparadorRreo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="separador-rreo",
        description=(
            "Separa anexos RREO de diários oficiais FEMURN em PDFs por município, "
            "com planilha de conferência e ZIP."
        ),
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        help="Caminho do PDF do diário (opcional; pergunta interativamente se omitido).",
    )
    parser.add_argument(
        "--municipios",
        nargs="+",
        metavar="NOME",
        help='Municípios a extrair, ex.: --municipios "Bodó" "Angicos"',
    )
    parser.add_argument(
        "--saida",
        default="RREO_separados",
        type=Path,
        help="Pasta de saída (padrão: RREO_separados).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _resolve_pdf(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit

    pdfs = sorted(Path.cwd().glob("*.pdf"))
    if len(pdfs) == 1:
        print(f"PDF: {pdfs[0]}")
        return pdfs[0]

    print("PDFs encontrados:", ", ".join(path.name for path in pdfs) or "nenhum")
    typed = input("Digite o nome/caminho do PDF: ").strip().strip('"')
    return Path(typed)


def _resolve_municipalities(explicit: list[str] | None) -> list[str]:
    if explicit:
        return explicit
    typed = input("Municípios separados por vírgula: ")
    return [part.strip() for part in typed.split(",") if part.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    pdf_path = _resolve_pdf(args.pdf)
    if not pdf_path.is_file():
        parser.error(f"PDF não encontrado: {pdf_path}")

    municipalities = _resolve_municipalities(args.municipios)
    if not municipalities:
        parser.error("Informe municípios.")

    try:
        analysis, export = SeparadorRreo().run(pdf_path, municipalities, args.saida)
    except ValueError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

    for municipality, findings in analysis.findings_by_municipality.items():
        if not findings:
            print(f"{municipality} | nenhum anexo localizado")
            continue
        for finding in findings:
            print(
                f"{municipality} | RREO {finding.annex:02d} | "
                f"{finding.page_start}-{finding.page_end} | {finding.status}"
            )

    print(
        f"PDFs criados: {export.pdf_count}; "
        f"planilha: {export.spreadsheet}; "
        f"ZIP: {export.zip_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
