"""
Stock Scanner — Streamlit dashboard entry point.

Run with:
    streamlit run app.py --server.port 8501
"""

from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Ensure project root is on sys.path so `import config` and `import src.*` work
sys.path.insert(0, str(Path(__file__).parent))

import config
from src.screener import run_screen
from src.ui_components import render_metrics_table, render_sidebar, render_summary_metrics

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Stock Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar — returns user selections
# ---------------------------------------------------------------------------
selected_index, refresh_seconds = render_sidebar()

# ---------------------------------------------------------------------------
# Auto-refresh (streamlit-autorefresh ticks and triggers a full rerun)
# ---------------------------------------------------------------------------
st_autorefresh(interval=refresh_seconds * 1000, key="auto_refresh")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("📈 Stock Scanner")
st.markdown(
    f"Screening **{selected_index}** constituents · "
    f"filters: P/E < {config.PE_MAX} | Volume ≥ {config.VOLUME_SPIKE_MIN}× 20-day avg "
    f"| RSI({config.RSI_PERIOD}) ≥ {config.RSI_MIN}"
)

# ---------------------------------------------------------------------------
# Data fetch + caching
# ---------------------------------------------------------------------------

@st.cache_data(ttl=refresh_seconds, show_spinner=False)
def _cached_screen(index_name: str, _cache_buster: int) -> tuple:
    """
    Cache the screening result for `ttl=refresh_seconds` seconds.

    `_cache_buster` is the epoch // refresh_seconds so the cache is
    invalidated every refresh cycle even if the user didn't change the index.
    """
    start = time.monotonic()
    df = run_screen(index_name)
    elapsed = time.monotonic() - start
    return df, elapsed


cache_buster = int(time.time()) // refresh_seconds
with st.spinner(f"Scanning {selected_index} …"):
    try:
        result_df, elapsed_s = _cached_screen(selected_index, cache_buster)
        fetch_ok = True
    except Exception as exc:
        st.error(f"Data fetch failed: {exc}")
        result_df = None
        elapsed_s = 0.0
        fetch_ok = False

# ---------------------------------------------------------------------------
# Last-refresh timestamp
# ---------------------------------------------------------------------------
now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
st.caption(f"Last refresh: **{now_utc}** · scan took {elapsed_s:.1f}s · next refresh in ~{refresh_seconds}s")

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
if fetch_ok and result_df is not None:
    render_summary_metrics(result_df, elapsed_s)
    st.markdown("---")

    st.subheader("Qualifying stocks")
    st.markdown(
        "Ranked by composite score (equal-weight normalised rank across P/E, volume ratio, and RSI). "
        "Click any column header to re-sort."
    )
    render_metrics_table(result_df)

    if not result_df.empty:
        with st.expander("ℹ️ Scoring methodology"):
            st.markdown(
                """
**Composite score** is computed in three steps:

1. Each metric is min-max normalised within the current result set to [0, 1].
   - P/E: *inverted* (lower P/E → higher score)
   - Volume ratio: higher is better
   - RSI: higher is better

2. The three normalised scores are averaged with equal weights (⅓ each).

3. Results are ranked descending by composite score.

Stocks missing a valid P/E in yfinance data are excluded because the P/E
filter cannot be applied to them.
                """
            )
