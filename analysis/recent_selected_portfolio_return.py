from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd
import yfinance as yf

OUT = Path(__file__).resolve().parent / "recent_selected_portfolio_return"
OUT.mkdir(parents=True, exist_ok=True)

SIGNAL_DATE = pd.Timestamp("2026-07-22")
WEIGHTS = {
    "005930.KS": 0.36000000,   # Samsung Electronics
    "034730.KS": 0.25967187,   # SK Inc.
    "^KS200":    0.20000000,   # KOSPI 200 price index
    "010950.KS": 0.09486023,   # S-Oil
    "278470.KS": 0.07157544,   # APR
    "009420.KS": 0.01389247,   # Hanall Biopharma
}
NAMES = {
    "005930.KS": "삼성전자",
    "034730.KS": "SK",
    "^KS200": "KOSPI200 지수",
    "010950.KS": "S-Oil",
    "278470.KS": "에이피알",
    "009420.KS": "한올바이오파마",
}

raw = yf.download(
    list(WEIGHTS),
    start="2026-07-20",
    end="2026-08-08",
    auto_adjust=False,
    progress=False,
    group_by="column",
    threads=False,
)
if raw.empty:
    raise RuntimeError("No market data returned")

# yfinance may return either a MultiIndex or a single-level frame.
def field(name: str) -> pd.DataFrame:
    if isinstance(raw.columns, pd.MultiIndex):
        return raw[name].copy()
    return raw[[name]].copy()

close = field("Close").sort_index()
open_ = field("Open").sort_index()
close.index = pd.to_datetime(close.index).tz_localize(None)
open_.index = pd.to_datetime(open_.index).tz_localize(None)

# Use the KOSPI200 calendar to identify the 10th trading day after the signal.
calendar = close["^KS200"].dropna().index
post = calendar[calendar > SIGNAL_DATE]
if len(post) < 10:
    raise RuntimeError(f"Only {len(post)} post-signal trading dates available")
exit_10d = post[9]
latest_date = calendar.max()
entry_next = post[0]

rows = []
for ticker, weight in WEIGHTS.items():
    c = close[ticker].dropna()
    o = open_[ticker].dropna()
    signal_close = float(c.loc[SIGNAL_DATE])
    exit_close = float(c.loc[exit_10d])
    latest_close = float(c.loc[latest_date])
    next_open = float(o.loc[entry_next])
    rows.append({
        "ticker": ticker,
        "name": NAMES[ticker],
        "weight": weight,
        "signal_date": SIGNAL_DATE,
        "signal_close": signal_close,
        "next_trade_date": entry_next,
        "next_open": next_open,
        "exit_10d_date": exit_10d,
        "exit_10d_close": exit_close,
        "latest_date": latest_date,
        "latest_close": latest_close,
        "return_signal_close_to_10d_close": exit_close / signal_close - 1.0,
        "return_next_open_to_10d_close": exit_close / next_open - 1.0,
        "return_signal_close_to_latest_close": latest_close / signal_close - 1.0,
    })

result = pd.DataFrame(rows)
for col in [
    "return_signal_close_to_10d_close",
    "return_next_open_to_10d_close",
    "return_signal_close_to_latest_close",
]:
    result[f"contribution_{col}"] = result["weight"] * result[col]

portfolio_10d = float(result["contribution_return_signal_close_to_10d_close"].sum())
portfolio_next_open = float(result["contribution_return_next_open_to_10d_close"].sum())
portfolio_latest = float(result["contribution_return_signal_close_to_latest_close"].sum())
k200_10d = float(result.loc[result.ticker == "^KS200", "return_signal_close_to_10d_close"].iloc[0])
k200_latest = float(result.loc[result.ticker == "^KS200", "return_signal_close_to_latest_close"].iloc[0])

summary = {
    "signal_date": str(SIGNAL_DATE.date()),
    "next_trade_date": str(entry_next.date()),
    "ten_trading_day_exit": str(exit_10d.date()),
    "latest_available_date": str(latest_date.date()),
    "portfolio_return_signal_close_to_10d_close": portfolio_10d,
    "portfolio_return_next_open_to_10d_close": portfolio_next_open,
    "k200_return_signal_close_to_10d_close": k200_10d,
    "active_return_signal_close_to_10d_close": (1 + portfolio_10d) / (1 + k200_10d) - 1,
    "portfolio_return_signal_close_to_latest_close": portfolio_latest,
    "k200_return_signal_close_to_latest_close": k200_latest,
    "active_return_signal_close_to_latest_close": (1 + portfolio_latest) / (1 + k200_latest) - 1,
    "full_entry_60bps_net_10d": portfolio_10d - 0.006,
    "full_entry_60bps_net_latest": portfolio_latest - 0.006,
}

result.to_csv(OUT / "asset_returns_and_contributions.csv", index=False, encoding="utf-8-sig")
close.to_csv(OUT / "raw_close_prices.csv", encoding="utf-8-sig")
open_.to_csv(OUT / "raw_open_prices.csv", encoding="utf-8-sig")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
print(result[["name", "weight", "return_signal_close_to_10d_close", "contribution_return_signal_close_to_10d_close"]].to_string(index=False))
