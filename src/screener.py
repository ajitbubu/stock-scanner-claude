"""
Screening and indicator layer.

Pure functions: no I/O, no Streamlit imports.
Inputs are pandas Series/DataFrames; output is a filtered, scored DataFrame.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from src.data_fetcher import (
    get_close_series,
    get_volume_series,
    fetch_history,
    fetch_fundamentals,
)


# ---------------------------------------------------------------------------
# Indicator calculations
# ---------------------------------------------------------------------------

def calculate_rsi(closes: pd.Series, period: int = config.RSI_PERIOD) -> float | None:
    """
    Wilder's RSI for the given close price series.

    Returns the most recent RSI value, or None if there is insufficient data.
    """
    closes = closes.dropna()
    if len(closes) < period + 1:
        return None

    delta = closes.diff().dropna()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder smoothing via ewm with adjust=False
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

    last_avg_gain = avg_gain.iloc[-1]
    last_avg_loss = avg_loss.iloc[-1]

    if last_avg_loss == 0:
        return 100.0
    rs = last_avg_gain / last_avg_loss
    return float(100 - (100 / (1 + rs)))


def calculate_volume_ratio(volumes: pd.Series, window: int = config.VOLUME_AVG_WINDOW) -> float | None:
    """
    Ratio of the most recent session's volume to the prior `window`-day average.

    The most recent bar is excluded from the average to avoid look-ahead.
    Returns None if there is insufficient data.
    """
    volumes = volumes.dropna()
    if len(volumes) < window + 1:
        return None
    avg = volumes.iloc[-(window + 1):-1].mean()
    if avg == 0:
        return None
    return float(volumes.iloc[-1] / avg)


# ---------------------------------------------------------------------------
# Composite scoring
# ---------------------------------------------------------------------------

def _normalise_series(s: pd.Series, invert: bool = False) -> pd.Series:
    """Min-max normalise to [0, 1]. Invert so that lower = better becomes higher score."""
    min_v, max_v = s.min(), s.max()
    if max_v == min_v:
        return pd.Series(0.5, index=s.index)
    normed = (s - min_v) / (max_v - min_v)
    return 1 - normed if invert else normed


def compute_composite_score(df: pd.DataFrame) -> pd.Series:
    """
    Equal-weight composite score across the three screener metrics.

    - P/E:           lower is better  → invert
    - Volume ratio:  higher is better
    - RSI:           higher is better (already filtered to > RSI_MIN)

    Returns a Series of scores in [0, 1].
    """
    pe_score = _normalise_series(df["pe"], invert=True)
    vol_score = _normalise_series(df["volume_ratio"], invert=False)
    rsi_score = _normalise_series(df["rsi"], invert=False)

    composite = (
        config.SCORE_WEIGHT_PE * pe_score
        + config.SCORE_WEIGHT_VOLUME * vol_score
        + config.SCORE_WEIGHT_RSI * rsi_score
    )
    return composite.round(4)


# ---------------------------------------------------------------------------
# Main screening pipeline
# ---------------------------------------------------------------------------

def run_screen(index_name: str) -> pd.DataFrame:
    """
    Full pipeline for the given index.

    Steps:
      1. Fetch constituent history (batch)
      2. Fetch fundamentals (P/E + name)
      3. Compute RSI and volume ratio per ticker
      4. Apply hard filters: PE < PE_MAX, volume_ratio >= VOLUME_SPIKE_MIN, RSI >= RSI_MIN
      5. Compute composite score
      6. Return sorted DataFrame

    Returns an empty DataFrame if nothing passes the filters.
    """
    from src.data_fetcher import get_constituents

    tickers = get_constituents(index_name)
    history = fetch_history(tickers)
    fundamentals = fetch_fundamentals(tickers)

    rows: list[dict] = []
    for ticker in tickers:
        fund = fundamentals.get(ticker)
        if fund is None:
            # Missing or invalid P/E — cannot apply PE filter, skip
            continue

        pe = fund["pe"]
        if pe >= config.PE_MAX:
            continue

        closes = get_close_series(history, ticker)
        volumes = get_volume_series(history, ticker)

        rsi = calculate_rsi(closes)
        vol_ratio = calculate_volume_ratio(volumes)

        if rsi is None or vol_ratio is None:
            continue

        if rsi < config.RSI_MIN:
            continue
        if vol_ratio < config.VOLUME_SPIKE_MIN:
            continue

        price = float(closes.iloc[-1]) if not closes.empty else None
        if price is None:
            continue

        rows.append(
            {
                "ticker": ticker,
                "name": fund["name"],
                "price": price,
                "pe": round(pe, 2),
                "volume_ratio": round(vol_ratio, 2),
                "rsi": round(rsi, 2),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=["ticker", "name", "price", "pe", "volume_ratio", "rsi", "score"]
        )

    df = pd.DataFrame(rows)
    df["score"] = compute_composite_score(df)
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df.index = df.index + 1   # 1-based rank
    df.index.name = "rank"
    return df
