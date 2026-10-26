"""Rolling-VWAP dip-buying strategy: loading prices, building the signal, simulating trades."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"

START = "2016-10-24"  # first backtest day
SPLIT = "2023-10-24"  # first out-of-sample day: nothing from here on is looked at until the final test
END = "2026-10-23"


@dataclass(frozen=True)
class Params:
    vwap_days: int = 20     # rolling VWAP window, in trading days (about a month)
    sigma_days: int = 60    # past window used to measure the typical distance from VWAP
    entry_z: float = -2.0   # buy when the distance from VWAP is this many σ or lower
    max_days: int = 10      # time stop: sell after this many trading days at most


def load_prices(symbol):
    """Cleaned daily bars from notebook 02, with every price adjusted for dividends and splits."""
    h = pd.read_csv(PROCESSED / f"{symbol}.csv", index_col="Date", parse_dates=True)
    factor = h["Adj Close"] / h["Close"]  # the same adjustment Yahoo applied to the close, applied to the whole bar
    bars = pd.DataFrame({col.lower(): h[col] * factor for col in ["Open", "High", "Low", "Close"]})
    bars["volume"] = h["Volume"]
    return bars


def add_signal(bars, p=Params()):
    """Add the rolling VWAP, today's % distance from it, and that distance in σ units.

    Every value on a row uses only data known at that day's close.
    """
    b = bars.copy()
    typical = (b["high"] + b["low"] + b["close"]) / 3  # stand-in for the day's average trade price
    b["vwap"] = (typical * b["volume"]).rolling(p.vwap_days).sum() / b["volume"].rolling(p.vwap_days).sum()
    b["dist"] = b["close"] / b["vwap"] - 1
    b["dist_sd"] = b["dist"].rolling(p.sigma_days).std().shift(1)  # yardstick from the previous days only
    b["z"] = b["dist"] / b["dist_sd"]
    return b


def simulate(b, symbol, p=Params()):
    """Walk through the days in order. Decisions are made at a day's close; orders fill at the next day's open.

    One position per stock at a time. A trade still open on the last day is left out.
    """
    opens, closes = b["open"].to_numpy(), b["close"].to_numpy()
    vwaps, zs = b["vwap"].to_numpy(), b["z"].to_numpy()
    dates = b.index

    trades = []
    entry_i = None  # row of the entry day while in a trade, None while flat
    for i in range(len(b) - 1):  # the last day has no next open to trade at
        if entry_i is None:
            if zs[i] <= p.entry_z:  # comparisons with NaN are False, so warm-up days never trigger
                entry_i = i + 1
        elif i >= entry_i:
            back_to_vwap = closes[i] >= vwaps[i]
            days_in = i - entry_i + 1
            if back_to_vwap or days_in >= p.max_days:
                exit_i = i + 1
                trades.append({
                    "symbol": symbol,
                    "signal_date": dates[entry_i - 1],
                    "entry_date": dates[entry_i],
                    "exit_date": dates[exit_i],
                    "signal_z": zs[entry_i - 1],
                    "entry_price": opens[entry_i],
                    "exit_price": opens[exit_i],
                    "days_held": exit_i - entry_i,
                    "exit_reason": "back to VWAP" if back_to_vwap else "time stop",
                })
                entry_i = None

    trades = pd.DataFrame(trades)
    if not trades.empty:
        trades["return"] = trades["exit_price"] / trades["entry_price"] - 1
    return trades


def run(symbols, p=Params()):
    """Signal and trades for every symbol. Returns (bars by symbol, all trades in one table)."""
    bars = {s: add_signal(load_prices(s), p) for s in symbols}
    trades = pd.concat([simulate(b, s, p) for s, b in bars.items()], ignore_index=True)
    return bars, trades.sort_values("entry_date", ignore_index=True)
