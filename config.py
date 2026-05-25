"""
Central configuration for the stock scanner.
"""

# Screening thresholds
PE_MAX = 20.0
VOLUME_SPIKE_MIN = 2.0   # current volume must be >= 2x the 20-day average
RSI_MIN = 50.0
RSI_PERIOD = 14
VOLUME_AVG_WINDOW = 20

# UI defaults
DEFAULT_REFRESH_SECONDS = 60
DEFAULT_INDEX = "NASDAQ-100"
AVAILABLE_INDICES = ["NASDAQ-100", "DJIA"]

# Composite score weights (must sum to 1.0)
SCORE_WEIGHT_PE = 1 / 3
SCORE_WEIGHT_VOLUME = 1 / 3
SCORE_WEIGHT_RSI = 1 / 3

# yfinance download parameters
HISTORY_PERIOD = "3mo"   # enough for 20-day avg + RSI(14)
HISTORY_INTERVAL = "1d"

# --- Index constituents -------------------------------------------------------
# NASDAQ-100 components (QQQ constituents, as of early 2025)
NASDAQ100_TICKERS = [
    "AAPL", "ABNB", "ADBE", "ADI", "ADP", "ADSK", "AEP", "AMAT", "AMD",
    "AMGN", "AMZN", "ANSS", "APP", "ARM", "ASML", "AVGO", "AZN", "BIIB",
    "BKNG", "BKR", "CCEP", "CDNS", "CDW", "CEG", "CHTR", "CMCSA", "COST",
    "CPRT", "CRWD", "CSCO", "CSX", "CTAS", "CTSH", "DDOG", "DLTR", "DXCM",
    "EA", "EXC", "FANG", "FAST", "FTNT", "GEHC", "GFS", "GILD", "GOOG",
    "GOOGL", "HON", "IDXX", "ILMN", "INTC", "INTU", "ISRG", "KDP", "KHC",
    "KLAC", "LIN", "LRCX", "LULU", "MAR", "MCHP", "MDLZ", "MELI", "META",
    "MNST", "MRNA", "MRVL", "MSFT", "MU", "NFLX", "NVDA", "NXPI", "ODFL",
    "ON", "ORLY", "PANW", "PAYX", "PCAR", "PDD", "PEP", "PLTR", "PYPL",
    "QCOM", "REGN", "ROP", "ROST", "SBUX", "SNPS", "TEAM", "TMUS", "TSLA",
    "TTD", "TTWO", "TXN", "VRSK", "VRTX", "WBD", "WDAY", "XEL", "ZS",
]

# DJIA 30 components (as of early 2025)
DJIA_TICKERS = [
    "AAPL", "AMGN", "AMZN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX",
    "DIS", "DOW", "GS", "HD", "HON", "IBM", "JNJ", "JPM", "KO", "MCD",
    "MMM", "MRK", "MSFT", "NKE", "NVDA", "PG", "SHW", "TRV", "UNH",
    "V", "WMT",
]

INDEX_TICKERS = {
    "NASDAQ-100": NASDAQ100_TICKERS,
    "DJIA": DJIA_TICKERS,
}
