"""
Reusable Streamlit UI components.

Keeps presentation logic separate from the main app orchestration.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

import config


def render_sidebar() -> tuple[str, int]:
    """
    Render the sidebar controls.

    Returns:
        (selected_index, refresh_interval_seconds)
    """
    st.sidebar.title("Stock Scanner")
    st.sidebar.markdown("---")

    selected_index = st.sidebar.radio(
        "Index universe",
        options=config.AVAILABLE_INDICES,
        index=config.AVAILABLE_INDICES.index(config.DEFAULT_INDEX),
    )

    refresh_seconds = st.sidebar.slider(
        "Auto-refresh interval (seconds)",
        min_value=30,
        max_value=300,
        value=config.DEFAULT_REFRESH_SECONDS,
        step=10,
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"**Filters applied**\n"
        f"- P/E < {config.PE_MAX}\n"
        f"- Volume ≥ {config.VOLUME_SPIKE_MIN}x 20-day avg\n"
        f"- RSI({config.RSI_PERIOD}) ≥ {config.RSI_MIN}"
    )
    st.sidebar.caption(
        "Data via [yfinance](https://github.com/ranaroussi/yfinance) "
        "(~15-min delayed)."
    )

    return selected_index, refresh_seconds


def render_metrics_table(df: pd.DataFrame) -> None:
    """
    Display the screened results as a styled, sortable table.
    """
    if df.empty:
        st.info(
            "No stocks currently pass all three filters. "
            "The market may be closed, or no tickers meet the criteria right now."
        )
        return

    display_df = df.reset_index().rename(
        columns={
            "rank": "Rank",
            "ticker": "Ticker",
            "name": "Company",
            "price": "Price ($)",
            "pe": "P/E",
            "volume_ratio": "Vol Ratio",
            "rsi": f"RSI({config.RSI_PERIOD})",
            "score": "Score",
        }
    )

    # Format numeric columns
    display_df["Price ($)"] = display_df["Price ($)"].map("${:,.2f}".format)
    display_df["P/E"] = display_df["P/E"].map("{:.2f}".format)
    display_df["Vol Ratio"] = display_df["Vol Ratio"].map("{:.2f}x".format)
    display_df[f"RSI({config.RSI_PERIOD})"] = display_df[f"RSI({config.RSI_PERIOD})"].map("{:.1f}".format)
    display_df["Score"] = display_df["Score"].map("{:.4f}".format)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_order=[
            "Rank", "Ticker", "Company", "Price ($)",
            "P/E", "Vol Ratio", f"RSI({config.RSI_PERIOD})", "Score",
        ],
    )


def render_summary_metrics(df: pd.DataFrame, elapsed_s: float) -> None:
    """Render top-line KPI tiles above the table."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Stocks passing filters", len(df))
    col2.metric("Avg P/E", f"{df['pe'].mean():.1f}" if not df.empty else "—")
    col3.metric("Avg RSI", f"{df['rsi'].mean():.1f}" if not df.empty else "—")
    col4.metric("Avg Vol Ratio", f"{df['volume_ratio'].mean():.2f}x" if not df.empty else "—")
