# Stock Scanner

A Streamlit dashboard that scans NASDAQ-100 or DJIA constituents in real-time
and surfaces stocks meeting all three criteria simultaneously:

- **P/E ratio** below 20
- **Volume spike** of at least 2× the 20-day average volume
- **RSI (14)** above 50

Results are ranked by a composite score and the table auto-refreshes on a
user-configurable interval (default: 60 seconds).

---

## Requirements

- Python 3.11 or later
- Internet access (yfinance fetches data from Yahoo Finance — ~15 min delayed)

---

## Quick start

```bash
# 1. Clone the repo
git clone <repo-url>
cd stock-scanner-claude

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the dashboard
streamlit run app.py --server.port 8501
```

Open **http://localhost:8501** in your browser.

---

## Port

The app runs on port **8501** by default. To use a different port:

```bash
streamlit run app.py --server.port 9000
```

---

## Usage

| Control | Location | Description |
|---|---|---|
| Index universe | Sidebar | Toggle between NASDAQ-100 and DJIA |
| Auto-refresh interval | Sidebar slider | 30 – 300 seconds (default 60 s) |
| Column sort | Table header click | Sort ascending/descending by any metric |

### Dashboard columns

| Column | Description |
|---|---|
| Rank | Composite score rank (1 = best) |
| Ticker | Stock symbol |
| Company | Company name |
| Price ($) | Most recent closing price |
| P/E | Trailing (or forward) P/E ratio |
| Vol Ratio | Current volume ÷ 20-day average volume |
| RSI(14) | 14-period Wilder RSI |
| Score | Normalised composite score [0 – 1] |

### Composite score

Each metric is min-max normalised within the current result set, then
averaged with equal ⅓ weights. P/E is inverted so that a lower P/E
yields a higher score.

---

## Project structure

```
stock-scanner-claude/
├── app.py                 # Streamlit entry point
├── config.py              # Thresholds, ticker lists, score weights
├── requirements.txt       # Pinned dependencies
├── CLAUDE.md              # Developer / agent documentation
└── src/
    ├── data_fetcher.py    # yfinance I/O layer
    ├── screener.py        # RSI, volume-ratio calculations; filter pipeline
    └── ui_components.py   # Streamlit components
```

---

## Troubleshooting

**"No stocks currently pass all three filters"**
The filters are strict and may return zero results, especially outside US
market hours or in low-volatility sessions. This is expected behaviour.

**Data looks stale**
yfinance provides ~15-minute delayed quotes. The timestamp shown above the
table reflects when the scan ran, not when prices were last updated.

**Rate limit / connection error**
Yahoo Finance occasionally throttles requests. The dashboard will display an
error message. Wait 30–60 seconds and the next auto-refresh will retry.
