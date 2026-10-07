"""Análise de diários FEMURN para localizar anexos RREO por município."""

from __future__ import annotations

import bisect
import re
from collections.abc import Sequence
from pathlib import Path

from separador_rreo.models import (
    AnalysisResult,
    CodeMarker,
    Finding,
    SectionMarker,
    TitleHit,
)
from separador_rreo.pdf_source import PdfDocument
from separador_rreo.recognition import AnexoRecognizer, TitleRecognizer
from separador_rreo.text import normalize

HEADER_RE = re.compile(
    r"(?m)^[ \t]*PREFEITURA MUNICIPAL DE[ \t]+([A-ZÀ-Ú][A-ZÀ-Ú \-']{2,55})[ \t]*$"
)
CODE_RE = re.compile(r"C[oó]digo\s+Identificador\s*:\s*[A-Z0-9]{6,12}", re.I)


class RreoAnalyzer:
    """
    Localiza seções de prefeitura, títulos RREO e códigos identificadores.

    Responsabilidade única: transformar um `PdfDocument` em `AnalysisResult`.
    Não abre nem fecha o PDF — isso fica a cargo do pipeline (DIP).
    """

    def __init__(self, recognizer: TitleRecognizer | None = None) -> None:
        self._recognizer = recognizer or AnexoRecognizer()

    def analyze(
        self,
        document: PdfDocument,
        municipalities: Sequence[str],
        *,
        source: Path | None = None,
    ) -> AnalysisResult:
        texts = [document.page_text(i) for i in range(len(document))]
        offsets: list[int] = []
        sections: list[SectionMarker] = []
        titles: list[TitleHit] = []
        codes: list[CodeMarker] = []
        pos = 0

        for page_index, text in enumerate(texts):
            offsets.append(pos)
            for match in HEADER_RE.finditer(text):
                sections.append(
                    SectionMarker(pos + match.start(), normalize(match.group(1)))
                )
            for match in CODE_RE.finditer(text):
                codes.append(CodeMarker(pos + match.start(), pos + match.end()))

            cursor = 0
            for line in text.splitlines(keepends=True):
                annex = self._recognizer.recognize(line)
                if annex is not None:
                    titles.append(
                        TitleHit(
                            offset=pos + cursor,
                            page=page_index + 1,
                            annex=annex,
                            raw_title=line.strip(),
                        )
                    )
                cursor += len(line)
            pos += len(text) + 1

        sections.sort(key=lambda item: item.offset)
        codes.sort(key=lambda item: item.start)
        titles.sort(key=lambda item: item.offset)

        if not sections:
            raise ValueError(
                "Não encontrei cabeçalhos de prefeituras. "
                "Confira se o PDF possui texto selecionável."
            )

        wanted: dict[str, list[Finding]] = {
            normalize(name): [] for name in municipalities
        }
        section_offsets = [item.offset for item in sections]
        code_starts = [item.start for item in codes]
        resolved_source = source or getattr(document, "path", None)

        for index, hit in enumerate(titles):
            section_index = bisect.bisect_right(section_offsets, hit.offset) - 1
            if section_index < 0:
                continue

            municipality = sections[section_index].municipality
            if municipality not in wanted:
                continue

            next_section = (
                section_offsets[section_index + 1]
                if section_index + 1 < len(section_offsets)
                else pos
            )
            next_title = titles[index + 1].offset if index + 1 < len(titles) else pos
            code_index = bisect.bisect_right(code_starts, hit.offset)
            code_end = codes[code_index].end if code_index < len(codes) else None

            # Em geral o artigo termina no primeiro código após o título.
            # Nunca atravessar o título de outro RREO ou a próxima prefeitura.
            limit = min(next_section, next_title)
            if code_end is not None and codes[code_index].start < limit:
                end = code_end
                status = "Encontrado"
            else:
                # Sem código: recorta até o próximo artigo e sinaliza verificação.
                end = limit - 1
                status = "Verificar limite final"

            page_end = bisect.bisect_right(offsets, end - 1)
            page_end = max(hit.page, min(page_end, len(document)))
            wanted[municipality].append(
                Finding(
                    annex=hit.annex,
                    page_start=hit.page,
                    page_end=page_end,
                    status=status,
                    title=hit.raw_title,
                )
            )

        return AnalysisResult(
            findings_by_municipality=wanted,
            page_count=len(document),
            source=resolved_source,
        )
