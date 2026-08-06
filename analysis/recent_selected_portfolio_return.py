from __future__ import annotations

from pathlib import Path
import json
import pandas as pd
import requests

OUT = Path(__file__).resolve().parent / "recent_selected_portfolio_return"
OUT.mkdir(parents=True, exist_ok=True)

SIGNAL_DATE = pd.Timestamp("2026-07-22")
WEIGHTS = {
    "005930": 0.36000000,
    "034730": 0.25967187,
    "KPI200": 0.20000000,
    "010950": 0.09486023,
    "278470": 0.07157544,
    "009420": 0.01389247,
}
NAMES = {
    "005930": "삼성전자",
    "034730": "SK",
    "KPI200": "KOSPI200 지수",
    "010950": "S-Oil",
    "278470": "에이피알",
    "009420": "한올바이오파마",
}
HEADERS = {"User-Agent": "Mozilla/5.0"}


def num(value):
    if value is None:
        return None
    return float(str(value).replace(",", ""))


def fetch_stock(code: str) -> pd.DataFrame:
    url = f"https://m.stock.naver.com/api/stock/{code}/price?pageSize=60&page=1"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()
    frame = pd.DataFrame(data)
    if frame.empty:
        raise RuntimeError(f"No stock data for {code}")
    frame["date"] = pd.to_datetime(frame["localTradedAt"])
    for src, dst in (("closePrice", "close"), ("openPrice", "open")):
        frame[dst] = frame[src].map(num)
    return frame.set_index("date")[["open", "close"]].sort_index()


def fetch_index(code: str) -> pd.DataFrame:
    url = f"https://m.stock.naver.com/api/index/{code}/price?pageSize=60&page=1"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()
    frame = pd.DataFrame(data)
    if frame.empty:
        raise RuntimeError(f"No index data for {code}")
    frame["date"] = pd.to_datetime(frame["localTradedAt"])
    for src, dst in (("closePrice", "close"), ("openPrice", "open")):
        frame[dst] = frame[src].map(num)
    return frame.set_index("date")[["open", "close"]].sort_index()


prices = {}
for code in WEIGHTS:
    prices[code] = fetch_index(code) if code == "KPI200" else fetch_stock(code)

calendar = prices["KPI200"].index
post = calendar[calendar > SIGNAL_DATE]
if len(post) < 10:
    raise RuntimeError(f"Only {len(post)} post-signal trading dates available: {list(post)}")
entry_next = post[0]
exit_10d = post[9]
latest_date = calendar.max()

rows = []
for code, weight in WEIGHTS.items():
    p = prices[code]
    required = [SIGNAL_DATE, entry_next, exit_10d, latest_date]
    missing = [str(d.date()) for d in required if d not in p.index]
    if missing:
        raise RuntimeError(f"{code} missing dates: {missing}")
    signal_close = float(p.loc[SIGNAL_DATE, "close"])
    next_open = float(p.loc[entry_next, "open"])
    exit_close = float(p.loc[exit_10d, "close"])
    latest_close = float(p.loc[latest_date, "close"])
    rows.append({
        "code": code,
        "name": NAMES[code],
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
return_cols = [
    "return_signal_close_to_10d_close",
    "return_next_open_to_10d_close",
    "return_signal_close_to_latest_close",
]
for col in return_cols:
    result[f"contribution_{col}"] = result["weight"] * result[col]

portfolio_10d = float(result["contribution_return_signal_close_to_10d_close"].sum())
portfolio_next_open = float(result["contribution_return_next_open_to_10d_close"].sum())
portfolio_latest = float(result["contribution_return_signal_close_to_latest_close"].sum())
k200_row = result[result.code == "KPI200"].iloc[0]
k200_10d = float(k200_row.return_signal_close_to_10d_close)
k200_latest = float(k200_row.return_signal_close_to_latest_close)

summary = {
    "source": "Naver Finance mobile daily OHLC API",
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
for code, frame in prices.items():
    frame.to_csv(OUT / f"raw_{code}_ohlc.csv", encoding="utf-8-sig")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
print(result[["name", "weight", "return_signal_close_to_10d_close", "contribution_return_signal_close_to_10d_close"]].to_string(index=False))
