"""Parse the BIS SP 21 PDF into one structured chunk per Indian Standard.

A chunk looks like:
    {
        "std": "IS 269: 1989",
        "title": "ORDINARY PORTLAND CEMENT, 33 GRADE",
        "text": "<full summary body>",
        "page": 21,
    }

The PDF uses a very stable header pattern:
    SUMMARY OF
    IS 269 : 1989 ORDINARY PORTLAND CEMENT, 33 GRADE

We split on those headers and assemble the body until the next ``SUMMARY OF``.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TypedDict

import fitz  # PyMuPDF

from .utils import format_standard, clean_text


class StandardChunk(TypedDict):
    std: str
    title: str
    text: str
    page: int


# Header right *under* the words "SUMMARY OF":
#   IS 269 : 1989 ORDINARY PORTLAND CEMENT, 33 GRADE
#   IS 1489 (Part 2) : 1991 PORTLAND POZZOLANA CEMENT — CALCINED CLAY BASED
HEADER_RE = re.compile(
    r"IS\s+(\d{2,5})"                                     # number
    r"(?:\s*\(\s*Part\s*([IVX0-9]+)\s*\))?"               # optional (Part N) — '(PART1)' allowed
    r"\s*:\s*(\d{4})"                                     # year (required for headers)
    r"\s+([A-Z0-9][^\n]{0,200})",                         # title (caps, on the same logical line)
    re.IGNORECASE,
)

SUMMARY_MARKER_RE = re.compile(r"SUMMARY\s+OF\s*", re.IGNORECASE)


def _strip_title(t: str) -> str:
    t = t.strip().rstrip(",.;:")
    # drop trailing parenthetical revision markers like "(Fourth Revision)"
    t = re.sub(r"\(\s*[A-Za-z0-9 ]+revision\s*\)\s*$", "", t, flags=re.IGNORECASE).strip()
    return t


def parse_pdf(pdf_path: str | Path) -> list[StandardChunk]:
    """Extract one chunk per BIS standard from the SP 21 handbook."""
    pdf_path = Path(pdf_path)
    doc = fitz.open(pdf_path)

    # Concatenate all pages, but remember which page each character came from.
    full = []
    page_index: list[int] = []  # per-character page number
    for i in range(len(doc)):
        t = doc[i].get_text("text")
        full.append(t)
        page_index.extend([i] * len(t))
        page_index.append(i)  # for the "\n" we add below
    raw = "\n".join(full)

    # Find every "SUMMARY OF" then read the header that follows.
    chunks: list[StandardChunk] = []
    for sm in SUMMARY_MARKER_RE.finditer(raw):
        # Consider the text immediately after the marker — usually one or two lines.
        start = sm.end()
        # Look at the next 600 chars to find the IS header.
        window = raw[start:start + 600]
        hm = HEADER_RE.search(window)
        if not hm:
            continue
        num, part, year = hm.group(1), hm.group(2), hm.group(3)
        title = _strip_title(hm.group(4))
        std = format_standard(num, part, year)
        # The body of this summary is from the end of the header to the next "SUMMARY OF".
        header_end_in_raw = start + hm.end()
        nxt = SUMMARY_MARKER_RE.search(raw, header_end_in_raw)
        body_end = nxt.start() if nxt else min(len(raw), header_end_in_raw + 8000)
        body = raw[header_end_in_raw:body_end]
        body = clean_text(body)
        page = page_index[min(start, len(page_index) - 1)] if page_index else 0

        chunks.append(
            StandardChunk(
                std=std,
                title=title,
                text=body[:6000],  # cap to keep retrieval focused
                page=page,
            )
        )
    return _dedupe(chunks)


def _dedupe(chunks: list[StandardChunk]) -> list[StandardChunk]:
    """Keep one chunk per standard ID — prefer the longest (richest) body."""
    by_std: dict[str, StandardChunk] = {}
    for c in chunks:
        prev = by_std.get(c["std"])
        if prev is None or len(c["text"]) > len(prev["text"]):
            by_std[c["std"]] = c
    return list(by_std.values())


def save_chunks(chunks: list[StandardChunk], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(chunks, f, indent=2)


def load_chunks(path: str | Path) -> list[StandardChunk]:
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", default="bis-rag/data/dataset.pdf")
    parser.add_argument("--out", default="bis-rag/.cache/chunks.json")
    args = parser.parse_args()

    chunks = parse_pdf(args.pdf)
    save_chunks(chunks, args.out)
    print(f"Parsed {len(chunks)} standards → {args.out}")
    for c in chunks[:5]:
        print(f"  {c['std']:<32} {c['title'][:60]}")
    print("  ...")
    for c in chunks[-3:]:
        print(f"  {c['std']:<32} {c['title'][:60]}")
