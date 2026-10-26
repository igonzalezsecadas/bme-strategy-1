"""Collect everything the explainer video shows into video/data.json.

Run with the research environment (it uses pandas and src/):
    .venv/Scripts/python.exe video/prepare_data.py
"""

import json
import sys
from math import sqrt
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from vwap_dip import SPLIT, START, run  # noqa: E402

symbols = pd.read_csv(ROOT / "data" / "universe" / "universe_v1.csv")["yahoo_symbol"].tolist()
bars, _ = run(symbols)
ins = pd.read_csv(ROOT / "data" / "results" / "trades_in_sample.csv", parse_dates=["signal_date", "entry_date", "exit_date"])
oos = pd.read_csv(ROOT / "data" / "results" / "trades_out_of_sample.csv", parse_dates=["signal_date", "entry_date", "exit_date"])
decade = pd.concat([ins, oos], ignore_index=True)


def t_by_month(r, dates):
    ev = r.mean()
    se = sqrt(((r - ev).groupby(dates.dt.to_period("M")).sum() ** 2).sum()) / len(r)
    return ev / se


# example chart: Tubacex, early 2020
ex = bars["TUB.MC"].loc["2020-01-02":"2020-05-15"]
ex_trades = ins[(ins["symbol"] == "TUB.MC") & ins["entry_date"].between("2020-01-02", "2020-05-15")]
pos = {d: i for i, d in enumerate(ex.index)}
example = {
    "dates": [d.strftime("%Y-%m-%d") for d in ex.index],
    "close": ex["close"].round(4).tolist(),
    "vwap": ex["vwap"].round(4).tolist(),
    "band": (ex["vwap"] * (1 - 2 * ex["dist_sd"])).round(4).tolist(),  # the price at which z = -2
    "volume": ex["volume"].astype(float).tolist(),
    "trades": [{"entry": pos[t.entry_date], "exit": pos[t.exit_date], "entry_price": round(t.entry_price, 4),
                "exit_price": round(t.exit_price, 4), "return": round(100 * t["return"], 1)}
               for _, t in ex_trades.iterrows()],
}

# Nextil around the split Yahoo missed: raw close vs fixed close
raw = pd.read_csv(ROOT / "data" / "raw" / "NXT.MC.csv", index_col="Date", parse_dates=True).loc["2018-06-01":"2018-10-31"]
fixed = pd.read_csv(ROOT / "data" / "processed" / "NXT.MC.csv", index_col="Date", parse_dates=True).loc["2018-06-01":"2018-10-31"]
fixed = fixed["Close"].reindex(raw.index).ffill()
nextil = {"raw": raw["Close"].round(4).tolist(), "fixed": fixed.round(4).tolist(),
          "split_index": int(np.searchsorted(raw.index, pd.Timestamp("2018-08-03")))}

# random twins, in-sample: same recipe and seed as notebook 03
rng = np.random.default_rng(42)
opens = {s: b["open"].to_numpy() for s, b in bars.items()}
pool = {s: np.flatnonzero((b.index >= START) & (b.index < SPLIT)) for s, b in bars.items()}
twins = np.array([np.mean([opens[s][e + h] / opens[s][e] - 1 for s, h in zip(ins["symbol"], ins["days_held"])
                           for e in [rng.choice(pool[s])]]) for _ in range(2000)])

by_year = decade[decade["entry_date"].dt.year >= 2017].groupby(decade["entry_date"].dt.year)["return"].mean()

r_is, r_oos = ins["return"], oos["return"]
sd = decade["return"].std()
edge = 0.005
data = {
    "example": example,
    "nextil": nextil,
    "twins": (100 * twins).round(4).tolist(),
    "in_sample": {"trades": len(ins), "win_rate": round(100 * (r_is > 0).mean(), 1),
                  "avg_win": round(100 * r_is[r_is > 0].mean(), 2), "avg_loss": round(100 * r_is[r_is <= 0].mean(), 2),
                  "ev": round(100 * r_is.mean(), 2), "random_as_good": round(100 * (twins >= r_is.mean()).mean())},
    "out_of_sample": {"trades": len(oos), "ev_auction": round(100 * oos["net_auction"].mean(), 2),
                      "t_month": round(t_by_month(oos["net_auction"], oos["entry_date"]), 2),
                      # portfolio Sharpe ratios above the ECB deposit rate, from notebook 05 (Part D)
                      "sharpe": 1.36, "sharpe_buy_hold": 0.38},
    "decade": {"trades": len(decade), "ev": round(100 * decade["return"].mean(), 2),
               "t_month": round(t_by_month(decade["return"], decade["entry_date"]), 2),
               "sharpe": 0.24, "sharpe_buy_hold": 0.27},  # from notebook 05 (Part D)
    "by_year": {str(y): round(100 * v, 2) for y, v in by_year.items()},
    "power": {"sd": round(100 * sd, 1), "edge": 100 * edge, "trades": round((2 * sd / edge) ** 2),
              "years": round((2 * sd / edge) ** 2 / (len(decade) / 10))},
}
(ROOT / "video" / "data.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
print({k: v for k, v in data.items() if k not in ("example", "nextil", "twins")})
