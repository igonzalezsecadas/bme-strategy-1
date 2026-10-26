"""Trading-cost model: broker commission, bid-ask spread estimated from daily prices, Spain's transaction tax."""

import pandas as pd
from bidask import edge_rolling

TRADE_SIZE = 10_000       # € per trade: a €100k account split into 10 slots, one per stock
COMMISSION_RATE = 0.0005  # 0.05% of trade value per order (Interactive Brokers fixed pricing for Spain)
COMMISSION_MIN = 3.0      # € minimum per order
FTT_RATE = 0.002          # 0.2% on purchases of Spanish companies on that year's tax list

# (symbol, tax year) pairs that were on the Agencia Tributaria's list for that year.
# Lists for 2021-2026 were checked: none of our 10 stocks appears on any of them.
TAXED = frozenset()


def commission_rate(trade_size=TRADE_SIZE):
    """Commission per order, as a fraction of the trade value."""
    return max(COMMISSION_MIN, COMMISSION_RATE * trade_size) / trade_size


def add_spread(bars, window=252):
    """Add each day's estimated bid-ask spread, as a fraction of price.

    Uses the EDGE estimator (Ardia, Guidotti & Kroencke, JFE 2024) over the previous `window` days,
    so the estimate on a trade date never uses that day or later.
    """
    b = bars.copy()
    b["spread"] = edge_rolling(b[["open", "high", "low", "close"]], window=window, min_periods=63).shift(1)
    return b


def net_returns(trades, bars, cross_spread):
    """Each trade's return after costs.

    cross_spread=True:  pay half the spread when buying and half when selling (market orders during the session).
    cross_spread=False: trade in the opening auction at the official open price, paying commission only.
    Commission and the transaction tax apply in both cases.
    """
    def spread_on(date_col):
        return pd.Series(
            [bars[s].at[d, "spread"] for s, d in zip(trades["symbol"], trades[date_col])], index=trades.index
        )

    half_in = spread_on("entry_date") / 2 if cross_spread else 0.0
    half_out = spread_on("exit_date") / 2 if cross_spread else 0.0
    tax = pd.Series(
        [FTT_RATE if (s, d.year) in TAXED else 0.0 for s, d in zip(trades["symbol"], trades["entry_date"])],
        index=trades.index,
    )
    comm = commission_rate()
    paid = trades["entry_price"] * (1 + half_in + comm + tax)
    received = trades["exit_price"] * (1 - half_out - comm)
    return received / paid - 1
