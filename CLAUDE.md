# Stock Scanner — CLAUDE.md

## Project purpose

A Streamlit dashboard that scans NASDAQ-100 or DJIA constituents and surfaces
stocks passing three simultaneous filters:

| Filter | Threshold |
|---|---|
| P/E ratio | < 20 |
| Volume spike | ≥ 2× the 20-day average volume |
| RSI (14-period) | ≥ 50 |

Results are ranked by a composite score and displayed in a sortable table that
auto-refreshes on a user-configurable interval (default 60 s).

---

## Directory layout

```
stock-scanner-claude/
├── app.py                 # Streamlit entry point — wires sidebar, data, UI
├── config.py              # All tunable constants (thresholds, tickers, weights)
├── requirements.txt       # Pinned Python dependencies
├── CLAUDE.md              # This file
├── README.md              # End-user run instructions
└── src/
    ├── __init__.py
    ├── data_fetcher.py    # All yfinance I/O (history batch + per-ticker info)
    ├── screener.py        # RSI, volume-ratio calc; filter pipeline; scoring
    └── ui_components.py   # Reusable Streamlit components (table, sidebar, KPIs)
```

### Layer responsibilities

```
config.py           ← pure constants, no imports from src/
src/data_fetcher.py ← I/O only; imports config
src/screener.py     ← pure calculations + pipeline; imports config + data_fetcher
src/ui_components.py← presentation only; imports config
app.py              ← orchestration; imports everything
```

This separation means `screener.py` is testable without Streamlit, and
`data_fetcher.py` can be swapped for a different data source without touching
the indicator logic.

---

## Conventions

- **Python 3.11+** required (uses `list[str]` generics and `from __future__ import annotations`)
- No type ignores — keep mypy-clean
- No comments unless the WHY is non-obvious
- All filter thresholds live in `config.py`; do not hardcode numbers elsewhere
- Caching: `@st.cache_data(ttl=...)` is applied in `app.py` around the full `run_screen` call. The `ttl` is the user's chosen refresh interval, so the cache is always hot when the autorefresh fires but stale data never lingers longer than the refresh period.

---

## Ranking / composite score

1. Each of the three metrics is min-max normalised within the current result set.
   - P/E is *inverted* (lower is better).
   - Volume ratio and RSI are direct (higher is better).
2. Normalised scores are averaged with equal weights (⅓ each).
3. Results are sorted descending by composite score.

Weights live in `config.py` (`SCORE_WEIGHT_*`) and can be adjusted there.

---

## Known limitations / design choices

- **Missing P/E**: Stocks without a valid `trailingPE` or `forwardPE` in
  yfinance are excluded. They cannot satisfy the P/E < 20 hard filter.
- **Data delay**: yfinance provides ~15-minute delayed data. Intraday volume
  uses the *current session* bar; outside market hours the last completed bar
  is used.
- **Rate limits**: yfinance batch-downloads OHLCV history in a single call,
  which avoids most rate-limit issues. Fundamentals are fetched per-ticker
  sequentially; the `@st.cache_data` TTL prevents re-fetching on every rerun.
- **Constituent lists**: Hardcoded in `config.py`. Update them when index
  compositions change.

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

---

## Adding a new index

1. Add the ticker list to `config.py` under a new key in `INDEX_TICKERS`.
2. Add the key string to `AVAILABLE_INDICES`.
3. No other changes required — `get_constituents()` is data-driven.
