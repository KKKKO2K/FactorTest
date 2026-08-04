from __future__ import annotations

import math
import types
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

HERE = Path(__file__).resolve().parent
OUT = HERE / "k200_actual_index_results"
OUT.mkdir(parents=True, exist_ok=True)

# Import the research lab after fixing pandas>=3 all-NA idxmax behavior.
lab_path = HERE / "factor_rotation_event_lab.py"
lab_source = lab_path.read_text(encoding="utf-8")
old_event = '''    p["event_score"] = event_scores.max(axis=1, skipna=True)\n    p["event_type"] = event_scores.idxmax(axis=1, skipna=True)\n    p["event_any"] = event_scores.notna().any(axis=1)\n'''
new_event = '''    p["event_score"] = event_scores.max(axis=1, skipna=True)\n    p["event_any"] = event_scores.notna().any(axis=1)\n    p["event_type"] = pd.Series(index=p.index, dtype="object")\n    valid_event = p["event_any"]\n    p.loc[valid_event, "event_type"] = event_scores.loc[valid_event].idxmax(axis=1)\n'''
if old_event not in lab_source:
    raise RuntimeError("Expected event-score block not found")
lab_source = lab_source.replace(old_event, new_event)
lab_ns = {"__name__": "factor_rotation_event_lab_imported", "__file__": str(lab_path)}
exec(compile(lab_source, str(lab_path), "exec"), lab_ns)
lab = types.SimpleNamespace(**lab_ns)

START = lab.START
SPLIT = lab.SPLIT
END = lab.END
STEP = lab.STEP
COST_BPS = 60
TARGET_STRATEGIES = ("EVENT_STATE_MACHINE", "REGIME_HYSTERESIS")
PERIODS_PER_YEAR = 252 / STEP


def download_index() -> pd.Series:
    raw = yf.download(
        "^KS200",
        start=(START - pd.Timedelta(days=20)).date().isoformat(),
        end=(END + pd.Timedelta(days=5)).date().isoformat(),
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if raw.empty:
        raise RuntimeError("Yahoo Finance returned no ^KS200 data")
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"].iloc[:, 0]
    else:
        close = raw["Close"]
    close.index = pd.to_datetime(close.index).tz_localize(None)
    close = pd.to_numeric(close, errors="coerce").dropna().sort_index()
    close.name = "k200_close"
    return close


def cagr(ret: pd.Series) -> float:
    if ret.empty:
        return np.nan
    wealth = float((1.0 + ret).prod())
    years = len(ret) / PERIODS_PER_YEAR
    return wealth ** (1.0 / years) - 1.0 if wealth > 0 and years > 0 else np.nan


def summarize(g: pd.DataFrame, sample: str) -> dict[str, float | str | int]:
    s = g["strategy_net"].astype(float)
    b = g["k200_return"].astype(float)
    active = s - b
    sw = float((1.0 + s).prod())
    bw = float((1.0 + b).prod())
    rel = sw / bw - 1.0
    beta = float(np.cov(s, b, ddof=1)[0, 1] / np.var(b, ddof=1)) if len(g) > 2 and np.var(b, ddof=1) > 0 else np.nan
    alpha_ann = float((s.mean() - beta * b.mean()) * PERIODS_PER_YEAR) if pd.notna(beta) else np.nan
    info_ratio = float(active.mean() / active.std(ddof=1) * math.sqrt(PERIODS_PER_YEAR)) if len(g) > 2 and active.std(ddof=1) > 0 else np.nan
    relative_nav = (1.0 + s).cumprod() / (1.0 + b).cumprod()
    return {
        "strategy": str(g["strategy"].iloc[0]),
        "sample": sample,
        "start_signal_date": g["date"].min().date().isoformat(),
        "end_signal_date": g["date"].max().date().isoformat(),
        "n_periods": len(g),
        "strategy_total_return": sw - 1.0,
        "k200_matched_total_return": bw - 1.0,
        "relative_total_return": rel,
        "strategy_cagr": cagr(s),
        "k200_cagr": cagr(b),
        "active_ann_mean": float(active.mean() * PERIODS_PER_YEAR),
        "information_ratio": info_ratio,
        "beta_to_k200": beta,
        "capm_alpha_ann": alpha_ann,
        "relative_mdd": float((relative_nav / relative_nav.cummax() - 1.0).min()),
        "positive_active_periods": float((active > 0).mean()),
        "avg_turnover": float(g["turnover"].mean()),
    }


def calendar_price_return(close: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> dict[str, float | str]:
    x = close[(close.index >= start) & (close.index <= end)]
    if len(x) < 2:
        return {
            "start_date": "",
            "end_date": "",
            "start_close": np.nan,
            "end_close": np.nan,
            "price_return": np.nan,
            "multiple": np.nan,
        }
    return {
        "start_date": x.index[0].date().isoformat(),
        "end_date": x.index[-1].date().isoformat(),
        "start_close": float(x.iloc[0]),
        "end_close": float(x.iloc[-1]),
        "price_return": float(x.iloc[-1] / x.iloc[0] - 1.0),
        "multiple": float(x.iloc[-1] / x.iloc[0]),
    }


def main() -> None:
    close = download_index()
    close.to_csv(OUT / "kospi200_yahoo_close.csv", encoding="utf-8-sig")

    returns, basic_panels = lab.base.load_basic()
    returns = returns.loc[:END]
    fwd10 = lab.forward_return(returns, STEP)
    fwd20 = lab.forward_return(returns, lab.HORIZON)

    panel = lab.build_panel("K200", returns, basic_panels)
    ic = lab.ic_detail(panel, fwd20, "K200")
    static, mapping, _ = lab.factor_maps(ic, "K200")
    scores, _ = lab.score_history(panel, ic, "K200", static, mapping)
    bt, _ = lab.backtest("K200", panel, scores, fwd10, COST_BPS)
    bt = bt[bt["strategy"].isin(TARGET_STRATEGIES)].copy()

    # Match Yahoo KOSPI200 closes to the exact daily calendar used by the strategy.
    aligned_close = close.reindex(returns.index)
    missing = aligned_close.isna()
    if missing.any():
        # Only bridge isolated vendor gaps; never extrapolate before/after the downloaded range.
        aligned_close = aligned_close.interpolate(method="time", limit=2, limit_area="inside")
    index_daily = aligned_close.pct_change(fill_method=None)
    index_fwd10 = lab.forward_return(index_daily.to_frame("K200"), STEP)["K200"]

    bt["k200_return"] = bt["date"].map(index_fwd10)
    bt = bt.dropna(subset=["k200_return"]).sort_values(["strategy", "date"])
    bt["strategy_net"] = bt["net"]
    bt["active_return"] = bt["strategy_net"] - bt["k200_return"]
    bt["sample"] = np.where(bt["date"] < SPLIT, "train", "test")
    bt["strategy_wealth"] = bt.groupby(["strategy", "sample"])["strategy_net"].transform(lambda x: (1.0 + x).cumprod())
    bt["k200_wealth"] = bt.groupby(["strategy", "sample"])["k200_return"].transform(lambda x: (1.0 + x).cumprod())
    bt["relative_wealth"] = bt["strategy_wealth"] / bt["k200_wealth"]
    bt.to_csv(OUT / "strategy_vs_kospi200_periods.csv", index=False, encoding="utf-8-sig")

    rows = []
    for (strategy, sample), g in bt.groupby(["strategy", "sample"]):
        rows.append(summarize(g.sort_values("date"), sample))
    summary = pd.DataFrame(rows).sort_values(["strategy", "sample"])
    summary.to_csv(OUT / "strategy_vs_kospi200_summary.csv", index=False, encoding="utf-8-sig")

    calendar_rows = []
    for sample, start, end in (
        ("train", START, SPLIT - pd.Timedelta(days=1)),
        ("test", SPLIT, END),
        ("full", START, END),
    ):
        row = {"sample": sample, **calendar_price_return(close, start, end)}
        calendar_rows.append(row)
    calendar = pd.DataFrame(calendar_rows)
    calendar.to_csv(OUT / "kospi200_calendar_price_returns.csv", index=False, encoding="utf-8-sig")

    md = [
        "# Strategy vs actual KOSPI200 price index",
        "",
        "Source: Yahoo Finance ^KS200 close. Strategy uses 60 bps one-way cost.",
        "Matched benchmark returns use the exact same 10-trading-day forward windows as the strategy.",
        "",
        "## Calendar KOSPI200 price return",
        "",
        calendar.to_markdown(index=False),
        "",
        "## Matched strategy comparison",
        "",
        summary.to_markdown(index=False),
    ]
    (OUT / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print(calendar.to_string(index=False))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
