from __future__ import annotations
import os
import sys
import time
from pathlib import Pathfrom __future__ import annotations
import os
import sys
import time
from pathlib import Path
import streamlit as st
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.rag_pipeline import BISRAGPipeline  
st.set_page_config(
    page_title="BIS Standards Recommender",
    page_icon="📐",
    layout="wide",
)
@st.cache_resource(show_spinner="Loading BIS knowledge base… (one-time, ~20 s)")
def get_pipeline() -> BISRAGPipeline:
    p = BISRAGPipeline()
    p.load()
    return p
@st.cache_data(show_spinner=False)
def get_cached_standard_count() -> int | None:
    """Return the number of cached standards without loading the model."""
    chunks_path = ROOT / ".cache" / "chunks.json"
    if not chunks_path.exists():
        return None
    import json
    try:
        with open(chunks_path) as f:
            return len(json.load(f))
    except Exception:
        return None
st.title("BIS Standards Recommendation Engine")
st.caption(
    "Describe a product, material, or process and the engine retrieves the most "
    "relevant Indian Standards (IS) from the **SP 21 : 2005 Building Materials Handbook**."
)
with st.sidebar:
    st.subheader("Settings")
    top_k = st.slider("Number of results", 1, 10, 5)
    st.markdown("---")
    st.subheader("Try a sample query")
    samples = [
        "We manufacture 33 Grade Ordinary Portland Cement.",
        "Lightweight hollow concrete masonry blocks for partition walls.",
        "Calcined-clay-based Portland pozzolana cement plant.",
        "White Portland cement for architectural finishing.",
        "Reinforced concrete pipes for water mains and sewers.",
        "Corrugated asbestos cement roofing sheets.",
        "Masonry cement for non-structural mortars.",
        "Supersulphated cement for marine works.",
    ]
    pick = st.selectbox("Sample queries", [""] + samples, index=0)
query_default = pick if pick else ""
query = st.text_area(
    "Your query",
    value=query_default,
    height=100,
    placeholder="e.g. 'We are setting up a 53-grade OPC plant — which BIS standard applies?'",
)
if st.button("Recommend standards", type="primary", use_container_width=True):
    if not query.strip():
        st.warning("Please enter a query first.")
    else:
        try:
            pipeline = get_pipeline()
            t0 = time.perf_counter()
            recs = pipeline.recommend(query, top_k=top_k)
            latency = time.perf_counter() - t0
            m1, m2 = st.columns(2)
            m1.metric("Latency", f"{latency*1000:.0f} ms")
            m2.metric("Standards returned", len(recs))
            st.markdown("### Recommended Indian Standards")
            for i, r in enumerate(recs, 1):
                with st.container(border=True):
                    top = st.columns([1, 4, 1])
                    top[0].markdown(f"**#{i}**")
                    top[1].markdown(f"**{r.standard}** — {r.title.title()}")
                    top[2].markdown(f"score {r.score:.3f}")
                    st.caption(r.rationale)
            with st.expander("Raw JSON (matches submission schema)"):
                st.json(
                    {
                        "query": query,
                        "retrieved_standards": [r.standard for r in recs],
                        "latency_seconds": round(latency, 4),
                    }
                )
        except Exception as exc:
            st.error("Unable to load the recommendation engine.")
            st.exception(exc)
st.markdown("---")
standard_count = get_cached_standard_count()
if standard_count is None:
    st.caption(
        "The BIS knowledge base loads on demand from the cached handbook. "
        "Hybrid retrieval: BM25 + TF-IDF + sentence-transformer embeddings."
    )
else:
    st.caption(
        f"Indexed **{standard_count}** standards from SP 21 : 2005. "
        "Hybrid retrieval: BM25 + TF-IDF + sentence-transformer embeddings."
    )
import streamlit as st
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.rag_pipeline import BISRAGPipeline  
st.set_page_config(
    page_title="BIS Standards Recommender",
    page_icon="📐",
    layout="wide",
)
@st.cache_resource(show_spinner="Loading BIS knowledge base… (one-time, ~20 s)")
def get_pipeline() -> BISRAGPipeline:
    p = BISRAGPipeline()
    p.load()
    return p
@st.cache_data(show_spinner=False)
def get_cached_standard_count() -> int | None:
    """Return the number of cached standards without loading the model."""
    chunks_path = ROOT / ".cache" / "chunks.json"
    if not chunks_path.exists():
        return None
    import json
    try:
        with open(chunks_path) as f:
            return len(json.load(f))
    except Exception:
        return None
st.title("BIS Standards Recommendation Engine")
st.caption(
    "Describe a product, material, or process and the engine retrieves the most "
    "relevant Indian Standards (IS) from the **SP 21 : 2005 Building Materials Handbook**."
)
with st.sidebar:
    st.subheader("Settings")
    top_k = st.slider("Number of results", 1, 10, 5)
    st.markdown("---")
    st.subheader("Try a sample query")
    samples = [
        "We manufacture 33 Grade Ordinary Portland Cement.",
        "Lightweight hollow concrete masonry blocks for partition walls.",
        "Calcined-clay-based Portland pozzolana cement plant.",
        "White Portland cement for architectural finishing.",
        "Reinforced concrete pipes for water mains and sewers.",
        "Corrugated asbestos cement roofing sheets.",
        "Masonry cement for non-structural mortars.",
        "Supersulphated cement for marine works.",
    ]
    pick = st.selectbox("Sample queries", [""] + samples, index=0)
query_default = pick if pick else ""
query = st.text_area(
    "Your query",
    value=query_default,
    height=100,
    placeholder="e.g. 'We are setting up a 53-grade OPC plant — which BIS standard applies?'",
)
if st.button("Recommend standards", type="primary", use_container_width=True):
    if not query.strip():
        st.warning("Please enter a query first.")
    else:
        try:
            pipeline = get_pipeline()
            t0 = time.perf_counter()
            recs = pipeline.recommend(query, top_k=top_k)
            latency = time.perf_counter() - t0
            m1, m2 = st.columns(2)
            m1.metric("Latency", f"{latency*1000:.0f} ms")
            m2.metric("Standards returned", len(recs))
            st.markdown("### Recommended Indian Standards")
            for i, r in enumerate(recs, 1):
                with st.container(border=True):
                    top = st.columns([1, 4, 1])
                    top[0].markdown(f"**#{i}**")
                    top[1].markdown(f"**{r.standard}** — {r.title.title()}")
                    top[2].markdown(f"score {r.score:.3f}")
                    st.caption(r.rationale)
            with st.expander("Raw JSON (matches submission schema)"):
                st.json(
                    {
                        "query": query,
                        "retrieved_standards": [r.standard for r in recs],
                        "latency_seconds": round(latency, 4),
                    }
                )
        except Exception as exc:
            st.error("Unable to load the recommendation engine.")
            st.exception(exc)
st.markdown("---")
standard_count = get_cached_standard_count()
if standard_count is None:
    st.caption(
        "The BIS knowledge base loads on demand from the cached handbook. "
        "Hybrid retrieval: BM25 + TF-IDF + sentence-transformer embeddings."
    )
else:
    st.caption(
        f"Indexed **{standard_count}** standards from SP 21 : 2005. "
        "Hybrid retrieval: BM25 + TF-IDF + sentence-transformer embeddings."
    ).   This is my website I want you to take inspiration from the official https://standards.bis.gov.in/website and design it properly without any unnecessary text or button give a header completely fully in the top bar of the screen and with proper menu side bar as you know, we need this based on this, redesign it completely with the proper colors and proper text style from this particular website
