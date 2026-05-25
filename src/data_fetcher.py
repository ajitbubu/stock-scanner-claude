"""
Data fetching layer: retrieves OHLCV history and fundamental info via yfinance.

All external I/O is isolated here so the screener layer stays pure.
"""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd
import yfinance as yf

import config

logger = logging.getLogger(__name__)


def get_constituents(index_name: str) -> list[str]:
    """Return the ticker list for the given index name."""
    tickers = config.INDEX_TICKERS.get(index_name)
    if tickers is None:
        raise ValueError(f"Unknown index '{index_name}'. Choose from {list(config.INDEX_TICKERS)}")
    return tickers


def fetch_history(tickers: list[str]) -> pd.DataFrame:
    """
    Download daily OHLCV history for all tickers in one batch call.

    Returns a MultiIndex DataFrame: (field, ticker).
    Missing tickers are silently dropped by yfinance.
    """
    if not tickers:
        return pd.DataFrame()

    data = yf.download(
        tickers=" ".join(tickers),
        period=config.HISTORY_PERIOD,
        interval=config.HISTORY_INTERVAL,
        auto_adjust=True,
        progress=False,
        group_by="ticker",
        threads=True,
    )
    return data


def fetch_fundamentals(tickers: list[str]) -> dict[str, dict]:
    """
    Fetch per-ticker fundamental data (P/E, company name) via yf.Ticker.info.

    Returns a dict keyed by ticker symbol. Tickers that fail or have no data
    are omitted from the result.
    """
    result: dict[str, dict] = {}
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            pe = info.get("trailingPE") or info.get("forwardPE")
            name = info.get("shortName") or info.get("longName") or ticker
            if pe is not None and pe > 0:
                result[ticker] = {"pe": float(pe), "name": name}
        except Exception as exc:
            logger.debug("Could not fetch fundamentals for %s: %s", ticker, exc)
    return result


def get_last_price(history: pd.DataFrame, ticker: str) -> Optional[float]:
    """Extract the most recent closing price for a ticker from the batch download."""
    try:
        if isinstance(history.columns, pd.MultiIndex):
            prices = history["Close"][ticker].dropna()
        else:
            # Single-ticker download — columns are field names
            prices = history["Close"].dropna()
        return float(prices.iloc[-1]) if not prices.empty else None
    except (KeyError, IndexError):
        return None


def get_close_series(history: pd.DataFrame, ticker: str) -> pd.Series:
    """Return the Close price series for a ticker; empty Series if missing."""
    try:
        if isinstance(history.columns, pd.MultiIndex):
            return history["Close"][ticker].dropna()
        return history["Close"].dropna()
    except KeyError:
        return pd.Series(dtype=float)


def get_volume_series(history: pd.DataFrame, ticker: str) -> pd.Series:
    """Return the Volume series for a ticker; empty Series if missing."""
    try:
        if isinstance(history.columns, pd.MultiIndex):
            return history["Volume"][ticker].dropna()
        return history["Volume"].dropna()
    except KeyError:
        return pd.Series(dtype=float)
