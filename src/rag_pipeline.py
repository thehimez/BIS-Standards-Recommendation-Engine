"""High-level RAG façade — load once, query many times."""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .ingest import parse_pdf, save_chunks
from .retriever import HybridIndex, Hit, build_index, search

# Project root = parent of the ``src/`` package directory.
_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PDF = str(_ROOT / "data" / "dataset.pdf")
DEFAULT_CHUNKS = str(_ROOT / ".cache" / "chunks.json")
DEFAULT_INDEX = str(_ROOT / ".cache" / "index.pkl")


@dataclass
class Recommendation:
    standard: str
    title: str
    score: float
    rationale: str


class BISRAGPipeline:
    """Lazy-loaded recommendation engine."""

    def __init__(
        self,
        pdf_path: str = DEFAULT_PDF,
        chunks_path: str = DEFAULT_CHUNKS,
        index_path: str = DEFAULT_INDEX,
        use_dense: bool = True,
    ):
        self.pdf_path = pdf_path
        self.chunks_path = chunks_path
        self.index_path = index_path
        self.use_dense = use_dense
        self._index: HybridIndex | None = None

    # ------------------------------------------------------------------ load
    def _ensure_chunks(self) -> None:
        import os

        if not os.path.exists(self.chunks_path):
            chunks = parse_pdf(self.pdf_path)
            save_chunks(chunks, self.chunks_path)

    def load(self) -> "BISRAGPipeline":
        if self._index is None:
            self._ensure_chunks()
            self._index = build_index(
                chunks_path=self.chunks_path,
                cache_path=self.index_path,
                use_dense=self.use_dense,
            )
            # Warm the embedding model so the first user query doesn't pay
            # the one-off ~15-20s torch + weights load cost.
            if self._index.dense_matrix is not None:
                try:
                    from .retriever import _model_singleton

                    _model_singleton("sentence-transformers/all-MiniLM-L6-v2").encode(
                        ["warmup"], show_progress_bar=False
                    )
                except Exception:
                    # Warming the embedding model is a latency optimisation only.
                    # If it fails here, search() already falls back to sparse signals.
                    pass
        return self

    # ----------------------------------------------------------------- query
    def retrieve(self, query: str, top_k: int = 5) -> list[Hit]:
        self.load()
        assert self._index is not None
        return search(self._index, query, top_k=top_k)

    def recommend(self, query: str, top_k: int = 5) -> list[Recommendation]:
        hits = self.retrieve(query, top_k=top_k)
        return [
            Recommendation(
                standard=h.std,
                title=h.title,
                score=h.score,
                rationale=_make_rationale(query, h),
            )
            for h in hits
        ]

    def predict_with_latency(
        self, query: str, top_k: int = 5
    ) -> tuple[list[str], float]:
        """Run the pipeline and return (standard_ids, latency_seconds)."""
        t0 = time.perf_counter()
        hits = self.retrieve(query, top_k=top_k)
        latency = time.perf_counter() - t0
        return [h.std for h in hits], latency


# ---------------------------------------------------------------------------
# Lightweight extractive rationale — no LLM call needed for the eval, but the
# UI surfaces this so users see *why* each standard was suggested.
# ---------------------------------------------------------------------------
def _make_rationale(query: str, hit: Hit) -> str:
    body = hit.text
    # Find the first sentence mentioning "Scope" or the most relevant keyword.
    snippet = body[:280]
    if "Scope" in body:
        i = body.index("Scope")
        snippet = body[i : i + 280]
    snippet = " ".join(snippet.split())
    if len(snippet) > 240:
        snippet = snippet[:237] + "…"
    return f"{hit.title.title()}. {snippet}"
