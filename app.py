from __future__ import annotations
import os
import sys
import time
import json
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

# ── Custom CSS — BIS Government Portal Theme ──────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600&family=Noto+Sans:wght@400;500;600&display=swap" rel="stylesheet">

<style>
/* ── Root palette ── */
:root {
    --bis-navy:       #003580;
    --bis-navy-dark:  #002060;
    --bis-saffron:    #FF6B00;
    --bis-cream:      #F9F7F2;
    --bis-border:     #C8D4E8;
    --bis-text:       #1A1A2E;
    --bis-muted:      #5A6A8A;
    --bis-light:      #EEF3FF;
    --bis-white:      #FFFFFF;
}

/* ── Global font override ── */
html, body, [class*="css"] {
    font-family: 'Noto Sans', sans-serif !important;
    color: var(--bis-text);
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; }

/* ── Government top banner ── */
.gov-banner {
    background: var(--bis-navy-dark);
    color: rgba(255,255,255,.7);
    font-size: 11px;
    padding: 5px 24px;
    letter-spacing: .3px;
    margin-bottom: 0;
}

/* ── Site header ── */
.bis-header {
    background: var(--bis-navy);
    border-bottom: 4px solid var(--bis-saffron);
    padding: 14px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 0;
}
.bis-header h1 {
    font-family: 'Noto Serif', serif !important;
    font-size: 20px;
    font-weight: 600;
    color: #fff;
    margin: 0;
    line-height: 1.25;
}
.bis-header p {
    font-size: 11px;
    color: rgba(255,255,255,.6);
    margin: 3px 0 0;
    text-transform: uppercase;
    letter-spacing: .4px;
}
.bis-header-badge {
    margin-left: auto;
    background: rgba(255,255,255,.1);
    border: 1px solid rgba(255,255,255,.2);
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 11px;
    color: rgba(255,255,255,.8);
    white-space: nowrap;
}

/* ── Nav bar ── */
.bis-nav {
    background: var(--bis-navy-dark);
    display: flex;
    border-bottom: 1px solid rgba(255,255,255,.1);
    margin-bottom: 0;
}
.bis-nav-item {
    padding: 9px 16px;
    font-size: 11px;
    color: rgba(255,255,255,.7);
    text-transform: uppercase;
    letter-spacing: .4px;
    font-weight: 500;
    border-bottom: 3px solid transparent;
    cursor: default;
}
.bis-nav-item.active {
    color: #fff;
    border-bottom-color: var(--bis-saffron);
    background: rgba(255,255,255,.05);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bis-white) !important;
    border-right: 1px solid var(--bis-border) !important;
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 16px !important;
}

/* ── Sidebar section headers ── */
.sidebar-head {
    font-size: 11px;
    font-weight: 600;
    color: var(--bis-saffron);
    text-transform: uppercase;
    letter-spacing: .8px;
    border-left: 3px solid var(--bis-saffron);
    background: rgba(255,107,0,.04);
    padding: 7px 12px;
    margin: 10px -1rem 6px;
}

/* ── Slider label ── */
.stSlider label, .stSelectbox label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: var(--bis-muted) !important;
    text-transform: uppercase;
    letter-spacing: .5px;
}

/* ── Slider accent ── */
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: var(--bis-navy) !important;
}
.stSlider [data-baseweb="slider"] div[data-testid="stThumbValue"] {
    background: var(--bis-navy) !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: var(--bis-navy) !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Noto Sans', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: .3px !important;
    font-size: 13px !important;
    padding: 10px 24px !important;
    transition: background .15s !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--bis-navy-dark) !important;
}

/* ── Text area ── */
.stTextArea textarea {
    border: 1px solid var(--bis-border) !important;
    border-radius: 4px !important;
    font-family: 'Noto Sans', sans-serif !important;
    font-size: 13px !important;
    color: var(--bis-text) !important;
}
.stTextArea textarea:focus {
    border-color: var(--bis-navy) !important;
    box-shadow: 0 0 0 2px rgba(0,53,128,.15) !important;
}
.stTextArea label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: var(--bis-navy) !important;
    text-transform: uppercase;
    letter-spacing: .5px;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: var(--bis-white);
    border: 1px solid var(--bis-border);
    border-top: 2px solid var(--bis-saffron);
    border-radius: 6px;
    padding: 14px 16px !important;
}
[data-testid="metric-container"] label {
    font-size: 11px !important;
    color: var(--bis-muted) !important;
    text-transform: uppercase;
    letter-spacing: .5px;
    font-weight: 500 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Noto Serif', serif !important;
    font-size: 22px !important;
    font-weight: 600 !important;
    color: var(--bis-navy) !important;
}

/* ── Result cards (st.container with border) ── */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 1px solid var(--bis-border) !important;
    border-radius: 6px !important;
    background: var(--bis-white) !important;
    overflow: hidden;
}
[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
    border-color: var(--bis-navy) !important;
}

/* ── Breadcrumb & page title ── */
.bis-breadcrumb {
    font-size: 12px;
    color: var(--bis-muted);
    padding: 12px 0 4px;
    display: flex;
    gap: 6px;
    align-items: center;
}
.bis-breadcrumb .sep { color: var(--bis-border); }
.bis-breadcrumb .current { color: var(--bis-navy); font-weight: 500; }

.bis-page-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
.bis-page-title h2 {
    font-family: 'Noto Serif', serif !important;
    font-size: 20px;
    font-weight: 600;
    color: var(--bis-navy-dark);
    margin: 0;
}
.bis-ai-badge {
    background: var(--bis-saffron);
    color: #fff;
    font-size: 10px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 3px;
    text-transform: uppercase;
    letter-spacing: .5px;
}

/* ── Result card row header ── */
.result-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 2px 0 6px;
}
.result-rank {
    width: 28px;
    height: 28px;
    background: var(--bis-navy);
    color: #fff;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    flex-shrink: 0;
    font-family: 'Noto Serif', serif;
}
.result-is {
    font-family: 'Noto Serif', serif;
    font-size: 15px;
    font-weight: 600;
    color: var(--bis-navy);
}
.score-pill {
    margin-left: auto;
    background: var(--bis-light);
    color: var(--bis-navy);
    font-size: 11px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 20px;
    border: 1px solid var(--bis-border);
    white-space: nowrap;
}

/* ── Footer ── */
.bis-footer {
    background: var(--bis-navy-dark);
    border-top: 3px solid var(--bis-saffron);
    color: rgba(255,255,255,.55);
    font-size: 11px;
    padding: 14px 24px;
    margin-top: 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: var(--bis-navy) !important;
    text-transform: uppercase;
    letter-spacing: .4px;
}

/* ── Warning / error ── */
.stWarning, .stException {
    border-radius: 4px !important;
    border-left: 3px solid var(--bis-saffron) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Government top banner ─────────────────────────────────────────────────────
st.markdown("""
<div class="gov-banner">
  Government of India &nbsp;|&nbsp;
  Ministry of Consumer Affairs, Food &amp; Public Distribution &nbsp;|&nbsp;
  Bureau of Indian Standards
</div>
""", unsafe_allow_html=True)

# ── Site header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="bis-header">
  <svg width="48" height="48" viewBox="0 0 60 60" fill="none">
    <circle cx="30" cy="30" r="28" fill="#003580" stroke="#FF6B00" stroke-width="2"/>
    <circle cx="30" cy="30" r="18" fill="none" stroke="#FFD700" stroke-width="1.5"/>
    <circle cx="30" cy="30" r="4" fill="#FFD700"/>
    <path d="M30 12 L30 48 M12 30 L48 30 M16.4 16.4 L43.6 43.6 M43.6 16.4 L16.4 43.6"
          stroke="#FFD700" stroke-width="0.8" opacity="0.5"/>
    <text x="30" y="33" text-anchor="middle" fill="#FFD700"
          font-size="8" font-weight="bold" font-family="serif">BIS</text>
  </svg>
  <div>
    <h1>Bureau of Indian Standards</h1>
    <p>Standards Recommendation Engine &nbsp;·&nbsp; SP 21 : 2005 Building Materials Handbook</p>
  </div>
  <div class="bis-header-badge">IS Portal v2.0</div>
</div>
""", unsafe_allow_html=True)

# ── Navigation bar ────────────────────────────────────────────────────────────
st.markdown("""
<div class="bis-nav">
  <div class="bis-nav-item active">Standards Search</div>
  <div class="bis-nav-item">Browse Catalogue</div>
  <div class="bis-nav-item">IS Amendments</div>
  <div class="bis-nav-item">Certification</div>
  <div class="bis-nav-item">Help &amp; Docs</div>
</div>
""", unsafe_allow_html=True)


# ── Pipeline helpers ──────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading BIS knowledge base… (one-time, ~20 s)")
def get_pipeline() -> BISRAGPipeline:
    p = BISRAGPipeline()
    p.load()
    return p


@st.cache_data(show_spinner=False)
def get_cached_standard_count() -> int | None:
    chunks_path = ROOT / ".cache" / "chunks.json"
    if not chunks_path.exists():
        return None
    try:
        with open(chunks_path) as f:
            return len(json.load(f))
    except Exception:
        return None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-head">Search Settings</div>', unsafe_allow_html=True)
    top_k = st.slider("Number of results", 1, 10, 5)

    st.markdown('<div class="sidebar-head">Sample Queries</div>', unsafe_allow_html=True)
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
    pick = st.selectbox("Choose a sample", [""] + samples, index=0)

    st.markdown('<div class="sidebar-head">Quick Links</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:13px;color:#5A6A8A;line-height:2.2">
      📄 &nbsp;SP 21 : 2005 Handbook<br>
      🌐 &nbsp;BIS Online Portal<br>
      ✅ &nbsp;IS Mark Certification<br>
      📋 &nbsp;Grievance Redressal
    </div>
    """, unsafe_allow_html=True)


# ── Main content area ─────────────────────────────────────────────────────────
st.markdown("""
<div class="bis-breadcrumb">
  <span>Home</span>
  <span class="sep">›</span>
  <span>Standards Search</span>
  <span class="sep">›</span>
  <span class="current">Recommend Standards</span>
</div>
<div class="bis-page-title">
  <h2>Standards Recommendation</h2>
  <span class="bis-ai-badge">AI-Powered</span>
</div>
""", unsafe_allow_html=True)

query_default = pick if pick else ""
query = st.text_area(
    "Describe your product, material, or process",
    value=query_default,
    height=100,
    placeholder="e.g. 'We are setting up a 53-grade OPC plant — which BIS standard applies?'",
)

if st.button("Search Standards", type="primary", use_container_width=True):
    if not query.strip():
        st.warning("Please enter a query first.")
    else:
        try:
            pipeline = get_pipeline()
            t0 = time.perf_counter()
            recs = pipeline.recommend(query, top_k=top_k)
            latency = time.perf_counter() - t0

            # ── Metrics row ───────────────────────────────────────────────────
            m1, m2, m3 = st.columns(3)
            m1.metric("Response Time", f"{latency * 1000:.0f} ms")
            m2.metric("Standards Found", len(recs))
            m3.metric("Knowledge Base", "SP 21 : 2005")

            # ── Section heading ───────────────────────────────────────────────
            st.markdown("""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        margin:20px 0 10px">
              <span style="font-size:13px;font-weight:600;color:#002060;
                           text-transform:uppercase;letter-spacing:.4px">
                Recommended Indian Standards
              </span>
              <span style="font-size:12px;color:#5A6A8A">
                {} result{} for your query
              </span>
            </div>
            """.format(len(recs), "s" if len(recs) != 1 else ""), unsafe_allow_html=True)

            # ── Result cards ──────────────────────────────────────────────────
            for i, r in enumerate(recs, 1):
                with st.container(border=True):
                    # Card header row
                    st.markdown(f"""
                    <div class="result-row">
                      <div class="result-rank">{i}</div>
                      <div>
                        <div class="result-is">{r.standard}</div>
                        <div style="font-size:12px;color:#5A6A8A;margin-top:2px">
                          {r.title.title()}
                        </div>
                      </div>
                      <div class="score-pill">Score: {r.score:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Rationale
                    st.markdown(
                        f'<div style="font-size:12px;color:#5A6A8A;'
                        f'line-height:1.6;padding:6px 0 2px">{r.rationale}</div>',
                        unsafe_allow_html=True,
                    )

            # ── Raw JSON expander ─────────────────────────────────────────────
            with st.expander("Raw JSON (matches submission schema)"):
                st.json({
                    "query": query,
                    "retrieved_standards": [r.standard for r in recs],
                    "latency_seconds": round(latency, 4),
                })

        except Exception as exc:
            st.error("Unable to load the recommendation engine.")
            st.exception(exc)


# ── Footer ────────────────────────────────────────────────────────────────────
standard_count = get_cached_standard_count()
count_text = (
    f"Indexed <strong>{standard_count}</strong> standards from SP 21 : 2005 · "
    if standard_count
    else "BIS knowledge base loads on demand · "
)

st.markdown(f"""
<div class="bis-footer">
  <span>
    Bureau of Indian Standards &nbsp;·&nbsp;
    Manak Bhavan, 9 Bahadur Shah Zafar Marg, New Delhi 110002
  </span>
  <span>
    {count_text}Hybrid retrieval: BM25 + TF-IDF + Sentence-Transformer Embeddings
  </span>
</div>
""", unsafe_allow_html=True)
