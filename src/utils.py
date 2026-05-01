"""Shared helpers — standard-name normalisation, regex, query enrichment."""
from __future__ import annotations

import re
from typing import Iterable

# ---------- BIS standard regex ----------------------------------------------
# Matches things like:
#   IS 269 : 1989
#   IS 1489 (Part 2) : 1991
#   IS 2185 (Part 1): 1979
#   IS 8042:1989
#   IS 4031 (Part 1) : 1996
STANDARD_RE = re.compile(
    r"\bIS\s*[:#]?\s*"                            # IS prefix
    r"(\d{2,5})"                                  # number
    r"(?:\s*\(\s*Part\s+([IVX0-9]+)\s*\))?"       # optional (Part N)
    r"\s*[:\-]?\s*"
    r"(\d{4})?",                                  # optional year
    re.IGNORECASE,
)

# Inline citations in body text often miss the year (e.g. "IS 4031" inside a note).
# We keep both forms so we don't lose recall during ingestion.


def format_standard(num: str, part: str | None, year: str | None) -> str:
    """Canonical printable form, e.g. ``IS 269: 1989`` or ``IS 1489 (Part 2): 1991``."""
    s = f"IS {int(num)}"
    if part:
        s += f" (Part {part})"
    if year:
        s += f": {year}"
    return s


def normalize_std(s: str) -> str:
    """Match the eval script: lowercase + remove all whitespace."""
    return re.sub(r"\s+", "", str(s)).lower()


def extract_standards(text: str) -> list[str]:
    """Return all canonical-form standards mentioned in *text*."""
    out: list[str] = []
    seen: set[str] = set()
    for m in STANDARD_RE.finditer(text):
        num, part, year = m.group(1), m.group(2), m.group(3)
        canon = format_standard(num, part, year)
        if canon not in seen:
            seen.add(canon)
            out.append(canon)
    return out


# ---------- domain-specific synonym expansion -------------------------------
# Light-weight query enrichment so that user phrasing like "OPC" maps onto
# document phrasing like "ordinary portland cement".
SYNONYMS: dict[str, list[str]] = {
    "opc": ["ordinary portland cement"],
    "ordinary portland cement": ["opc"],
    "ppc": ["portland pozzolana cement"],
    "portland pozzolana cement": ["ppc", "fly ash based", "calcined clay based"],
    "psc": ["portland slag cement"],
    "portland slag cement": ["psc", "blast furnace slag"],
    "rha": ["rice husk ash"],
    "rice husk ash": ["rha"],
    "ggbs": ["ground granulated blast furnace slag"],
    "ggbfs": ["ground granulated blast furnace slag"],
    "rcc": ["reinforced cement concrete", "reinforced concrete"],
    "rebar": ["reinforcement bar", "reinforcing bar", "tmt", "deformed bar"],
    "tmt": ["thermo mechanically treated", "deformed bar", "rebar"],
    "hysd": ["high yield strength deformed", "deformed bar"],
    "ac sheet": ["asbestos cement sheet"],
    "asbestos cement": ["ac sheet"],
    "msme": ["micro and small enterprises", "msme", "small enterprise"],
    "mse": ["micro and small enterprises"],
    "agg": ["aggregate", "aggregates"],
    "aggregate": ["coarse aggregate", "fine aggregate", "natural sources"],
    "rmc": ["ready mixed concrete", "ready-mix concrete"],
    "concrete": ["mortar", "rcc", "structural concrete"],
    "cement": ["portland cement", "hydraulic cement"],
    "white cement": ["white portland cement"],
    "masonry": ["brick", "block", "mortar", "bricks", "blocks"],
    "brick": ["masonry brick", "burnt clay brick", "fly ash brick"],
    "block": ["concrete masonry block", "concrete block", "hollow block", "solid block"],
    "tile": ["roofing tile", "flooring tile", "ceramic tile"],
    "pipe": ["concrete pipe", "asbestos cement pipe", "water pipe"],
    "roof": ["roofing", "sheet"],
    "lightweight": ["light weight", "light-weight"],
    "supersulphated cement": ["super sulphated cement", "super-sulphated cement"],
    "high alumina cement": ["high-alumina cement"],
    "marine": ["sea water", "aggressive water"],
    "decorative": ["architectural"],
    "structural": ["load bearing", "load-bearing"],
    "precast": ["pre-cast", "pre cast"],
    "prestressed": ["pre-stressed", "pre stressed"],
    "reinforcement": ["reinforced", "reinforcing"],
    "fineness": ["specific surface", "blaine"],
    "soundness": ["expansion"],
    "compressive strength": ["mortar cube strength"],
    "setting time": ["initial setting", "final setting"],
    "chemical requirements": ["chemical composition"],
    "physical requirements": ["physical properties"],
    "specification": ["covers manufacture"],
    "msme compliance": ["msme", "indian standard"],
    "calcined clay": ["calcined clay based", "metakaolin"],
    "fly ash": ["pulverised fuel ash", "pfa"],
    "33 grade": ["33-grade", "thirty three grade"],
    "43 grade": ["43-grade"],
    "53 grade": ["53-grade"],
}


def enrich_query(q: str) -> str:
    """Lower-cased query with appended synonyms.

    We append rather than substitute so the original query terms keep their
    BM25 / TF-IDF weight while extra variants raise recall.
    """
    q_low = q.lower()
    add: list[str] = []
    for key, vals in SYNONYMS.items():
        if key in q_low:
            add.extend(vals)
    if add:
        return q + " " + " ".join(dict.fromkeys(add))
    return q


# ---------- text cleaning ---------------------------------------------------
def clean_text(t: str) -> str:
    """Collapse whitespace and strip footers/PDF artefacts."""
    t = re.sub(r"\bSP\s*21\s*:\s*2005\b", " ", t)
    t = re.sub(r"\bSUMMARY\s+OF\b", " ", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def chunk_iter(items: Iterable, size: int):
    buf = []
    for x in items:
        buf.append(x)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf
