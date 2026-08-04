from __future__ import annotations

import importlib.util
import math
import types
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

HERE = Path(__file__).resolve().parent
OUT = HERE / "enhanced_k200_results"
OUT.mkdir(parents=True, exist_ok=True)

# Import the existing point-in-time factor/event research code while fixing its
# all-NaN idxmax edge case. The branch remains research-only.
lab_path = HERE / "factor_rotation_event_lab.py"
lab_source = lab_path.read_text(encoding="utf-8")
old_event = '''    p["event_score"] = event_scores.max(axis=1, skipna=True)\n    p["event_type"] = event_scores.idxmax(axis=1, skipna=True)\n    p["event_any"] = event_scores.notna().any(axis=1)\n'''
new_event = '''    p["event_score"] = event_scores.max(axis=1, skipna=True)\n    p["event_any"] = event_scores.notna().any(axis=1)\n    p["event_type"] = pd.Series(index=p.index, dtype="object")\n    valid_event = p["event_any"]\n    p.loc[valid_event, "event_type"] = event_scores.loc[valid_event].idxmax(axis=1)\n'''
if old_event in lab_source:
    lab_source = lab_source.replace(old_event, new_event)
ns = {"__name__": "enhanced_k200_lab", "__file__": str(lab_path)}
exec(compile(lab_source, str(lab_path), "exec"), ns)
lab = types.SimpleNamespace(**ns)
base = lab.base

START = pd.Timestamp("2017-01-02")
SPLIT = pd.Timestamp("2023-05-26")
END = pd.Timestamp("2026-07-31")
STEP = 10
COSTS = (30, 60, 100)


def download_kospi200() -> pd.Series:
    data = yf.download(
        "^KS200",
        start="2016-11-01",
        end="2026-08-20",
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if data.empty:
        raise RuntimeError("Could not download ^KS200")
    close = data["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close.index = pd.to_datetime(close.index).tz_localize(None)
    return pd.to_numeric(close, errors="coerce").dropna().sort_index().rename("k200_close")


def forward_index_returns(close: pd.Series, signal_dates: list[pd.Timestamp], horizon: int) -> pd.Series:
    idx = close.index
    out: dict[pd.Timestamp, float] = {}
    for dt in signal_dates:
        pos = int(idx.searchsorted(dt, side="right"))
        if pos >= len(idx):
            out[dt] = np.nan
            continue
        end_pos = pos + horizon - 1
        if end_pos >= len(idx):
            out[dt] = np.nan
            continue
        start_px = float(close.iloc[pos - 1]) if pos > 0 else np.nan
        end_px = float(close.iloc[end_pos])
        out[dt] = end_px / start_px - 1.0 if start_px > 0 else np.nan
    return pd.Series(out, name="k200_return")


def rank01(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").rank(pct=True, method="average")


def cap_weights(raw: pd.Series, max_abs: float = 1.0) -> pd.Series:
    x = pd.to_numeric(raw, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0).clip(lower=0.0)
    if x.sum() <= 0:
        return pd.Series(dtype=float)
    x = x / x.sum()
    if max_abs >= 1.0 or x.max() <= max_abs:
        return x
    free = pd.Series(True, index=x.index)
    result = pd.Series(0.0, index=x.index)
    raw0 = x.copy()
    for _ in range(len(x) + 2):
        remaining = 1.0 - result.sum()
        if remaining <= 1e-12 or not free.any():
            break
        alloc = raw0[free]
        if alloc.sum() <= 0:
            alloc = pd.Series(1.0, index=alloc.index)
        alloc = alloc / alloc.sum() * remaining
        hit = alloc > max_abs
        if not hit.any():
            result.loc[alloc.index] = alloc
            break
        hit_names = alloc.index[hit]
        result.loc[hit_names] = max_abs
        free.loc[hit_names] = False
    if result.sum() < 1.0 - 1e-8 and free.any():
        remaining = 1.0 - result.sum()
        alloc = raw0[free]
        alloc = alloc / alloc.sum() * remaining
        result.loc[alloc.index] = alloc
    return result[result > 1e-12]


def tilt_distribution(
    benchmark: pd.Series,
    score: pd.Series,
    kappa: float,
    top_n: int | None = None,
    max_abs: float = 0.40,
) -> pd.Series:
    s = rank01(score.reindex(benchmark.index))
    valid = s.dropna()
    if top_n is not None:
        keep = valid.nlargest(min(top_n, len(valid))).index
    else:
        keep = valid.index
    if len(keep) == 0:
        return benchmark.copy()
    raw = benchmark.reindex(keep).fillna(0.0) * np.exp(kappa * (2.0 * s.reindex(keep) - 1.0))
    return cap_weights(raw, max_abs=max_abs)


def blend_weights(
    benchmark: pd.Series,
    tilt: pd.Series,
    active_share: float,
    beta: float = 1.0,
) -> pd.Series:
    idx = benchmark.index.union(tilt.index)
    core = benchmark.reindex(idx, fill_value=0.0)
    satellite = tilt.reindex(idx, fill_value=0.0)
    risky = (1.0 - active_share) * core + active_share * satellite
    risky = risky / risky.sum() if risky.sum() > 0 else core
    return (beta * risky)[lambda x: x > 1e-12]


def drifted_turnover(old_end: pd.Series, new: pd.Series) -> float:
    idx = old_end.index.union(new.index)
    old = old_end.reindex(idx, fill_value=0.0)
    target = new.reindex(idx, fill_value=0.0)
    old_cash = 1.0 - float(old.sum())
    new_cash = 1.0 - float(target.sum())
    return 0.5 * (float((target - old).abs().sum()) + abs(new_cash - old_cash))


def state_parameters(state: str) -> tuple[float, float]:
    # beta, active share
    return {
        "NARROW_RISK_ON": (1.00, 0.12),
        "BROAD_RISK_ON": (1.00, 0.40),
        "HIGH_DISPERSION": (0.95, 0.50),
        "HIGH_VOL_CHOP": (0.80, 0.30),
        "RISK_OFF": (0.55, 0.35),
        "NEUTRAL": (0.90, 0.40),
    }.get(state, (0.90, 0.35))


def strategy_targets(
    dt: pd.Timestamp,
    panel_slice: pd.DataFrame,
    score_slice: pd.DataFrame,
    basic_panel: pd.DataFrame,
) -> dict[str, pd.Series]:
    codes = panel_slice.index.get_level_values("code")
    bp = basic_panel.reindex(codes)
    mcap = pd.to_numeric(bp["mcap"], errors="coerce").clip(lower=0.0)
    benchmark = cap_weights(mcap, max_abs=1.0)

    z = score_slice.reindex(codes)
    g = panel_slice.copy()
    g.index = codes

    meta = rank01(z["EVENT_PLUS_META"])
    event = rank01(z["event_score"].where(z["event_any"]))
    event_filled = event.fillna(meta * 0.65)
    leader_raw = (
        0.30 * g["long_up"]
        + 0.20 * g["short_up"]
        + 0.25 * g["revision"]
        + 0.15 * g["private_persist"]
        + 0.10 * g["size_rank"]
    )
    leader = rank01(leader_raw)
    combined = rank01(0.50 * leader + 0.35 * meta + 0.15 * event_filled)

    state = str(g["state"].iloc[0])
    beta, adaptive_active = state_parameters(state)
    if state == "NARROW_RISK_ON":
        adaptive_score = 0.75 * leader + 0.25 * meta
    elif state == "BROAD_RISK_ON":
        adaptive_score = 0.45 * leader + 0.35 * meta + 0.20 * event_filled
    elif state == "RISK_OFF":
        adaptive_score = 0.50 * event_filled + 0.30 * g["SHORT_REVERSAL"] + 0.20 * g["VALUE_UNLOCK"]
    else:
        adaptive_score = 0.40 * meta + 0.35 * event_filled + 0.25 * leader

    event_tilt = tilt_distribution(benchmark, event_filled, kappa=2.0, top_n=25, max_abs=0.30)
    leader_tilt = tilt_distribution(benchmark, leader, kappa=2.4, top_n=10, max_abs=0.35)
    leader5_tilt = tilt_distribution(benchmark, leader, kappa=3.2, top_n=5, max_abs=0.45)
    moderate_tilt = tilt_distribution(benchmark, combined, kappa=1.8, top_n=None, max_abs=0.30)
    adaptive_tilt = tilt_distribution(benchmark, adaptive_score, kappa=2.2, top_n=12, max_abs=0.35)

    # Pyramiding: benchmark-weighted foundation, progressively larger multipliers
    # when leadership, event, and explicit sequence confirmation align.
    multiplier = np.exp(1.5 * (2.0 * leader.fillna(0.5) - 1.0))
    multiplier *= np.where(z["event_any"].fillna(False), 1.50, 1.0)
    explicit_sequence = (
        g["event_flow_revision"].fillna(False)
        | g["event_three_stage"].fillna(False)
        | g["event_dual_revision"].fillna(False)
    )
    multiplier *= np.where(explicit_sequence, 1.50, 1.0)
    multiplier *= np.where((leader >= 0.90) & (meta >= 0.75), 1.35, 1.0)
    pyramid_tilt = cap_weights(benchmark * multiplier.reindex(benchmark.index).fillna(1.0), max_abs=0.45)

    return {
        "CAP_WEIGHT_PROXY": benchmark,
        "CORE90_EVENT10": blend_weights(benchmark, event_tilt, 0.10, 1.00),
        "CORE70_EVENT30": blend_weights(benchmark, event_tilt, 0.30, 1.00),
        "ENHANCED_MODERATE": blend_weights(benchmark, moderate_tilt, 0.45, 1.00),
        "LEADER_TOP10_50": blend_weights(benchmark, leader_tilt, 0.50, 1.00),
        "LEADER_TOP5_65": blend_weights(benchmark, leader5_tilt, 0.65, 1.00),
        "FULLY_INVESTED_ADAPTIVE": blend_weights(benchmark, adaptive_tilt, adaptive_active, 1.00),
        "DYNAMIC_BETA_ADAPTIVE": blend_weights(benchmark, adaptive_tilt, adaptive_active, beta),
        "PYRAMID_CONCENTRATED": blend_weights(benchmark, pyramid_tilt, 0.65, 1.00),
    }


def run_backtest(
    panel: pd.DataFrame,
    scores: dict[pd.Timestamp, pd.DataFrame],
    returns: pd.DataFrame,
    basic_panels: dict[pd.Timestamp, pd.DataFrame],
    k200_period: pd.Series,
    cost_bps: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fwd10 = lab.forward_return(returns, STEP)
    current_end: dict[str, pd.Series] = {}
    rows: list[dict] = []
    weight_rows: list[dict] = []

    for dt, g0 in panel.groupby(level="date"):
        if dt not in scores or dt not in fwd10.index or dt not in k200_period.index:
            continue
        if pd.isna(k200_period.loc[dt]):
            continue
        codes = g0.index.get_level_values("code")
        future = fwd10.loc[dt].reindex(codes).fillna(0.0)
        targets = strategy_targets(dt, g0, scores[dt], basic_panels[dt])
        state = str(g0["state"].iloc[0])

        for strategy, new_w in targets.items():
            old = current_end.get(strategy, pd.Series(dtype=float))
            turn = drifted_turnover(old, new_w)
            stock_r = future.reindex(new_w.index).fillna(0.0)
            gross = float((new_w * stock_r).sum())
            net = gross - turn * cost_bps / 10000.0
            cash = 1.0 - float(new_w.sum())
            denom = 1.0 + gross
            if denom <= 0:
                end_w = new_w.copy()
            else:
                end_w = new_w * (1.0 + stock_r) / denom
            current_end[strategy] = end_w[end_w.abs() > 1e-12]

            sorted_w = new_w.sort_values(ascending=False)
            rows.append({
                "date": dt,
                "strategy": strategy,
                "cost_bps": cost_bps,
                "state": state,
                "gross": gross,
                "net": net,
                "k200_return": float(k200_period.loc[dt]),
                "active_return": net - float(k200_period.loc[dt]),
                "turnover": turn,
                "exposure": float(new_w.sum()),
                "n_holdings": int((new_w > 1e-8).sum()),
                "top1_weight": float(sorted_w.head(1).sum()),
                "top5_weight": float(sorted_w.head(5).sum()),
                "hhi": float((new_w ** 2).sum()),
                "cash_weight": cash,
            })
            for code, weight in sorted_w.items():
                weight_rows.append({
                    "date": dt,
                    "strategy": strategy,
                    "cost_bps": cost_bps,
                    "code": code,
                    "weight": float(weight),
                    "state": state,
                })
    return pd.DataFrame(rows), pd.DataFrame(weight_rows)


def metrics(g: pd.DataFrame) -> dict[str, float]:
    g = g.sort_values("date")
    n = len(g)
    periods = 252 / STEP
    years = n / periods
    s = g["net"]
    b = g["k200_return"]
    a = s - b
    sw = (1.0 + s).cumprod()
    bw = (1.0 + b).cumprod()
    rel = sw / bw
    s_cagr = sw.iloc[-1] ** (1.0 / years) - 1.0
    b_cagr = bw.iloc[-1] ** (1.0 / years) - 1.0
    rel_cagr = rel.iloc[-1] ** (1.0 / years) - 1.0
    te = a.std(ddof=1) * math.sqrt(periods)
    ir = a.mean() / a.std(ddof=1) * math.sqrt(periods) if a.std(ddof=1) > 0 else np.nan
    beta = np.cov(s, b, ddof=1)[0, 1] / np.var(b, ddof=1) if np.var(b, ddof=1) > 0 else np.nan
    alpha = (s.mean() - beta * b.mean()) * periods if pd.notna(beta) else np.nan
    up = b > 0
    down = b < 0
    up_capture = s[up].mean() / b[up].mean() if up.any() and b[up].mean() != 0 else np.nan
    down_capture = s[down].mean() / b[down].mean() if down.any() and b[down].mean() != 0 else np.nan
    top_rally = b >= b.quantile(0.80)
    rally_capture = s[top_rally].mean() / b[top_rally].mean() if top_rally.any() else np.nan
    return {
        "n_periods": n,
        "strategy_total_return": float(sw.iloc[-1] - 1.0),
        "k200_total_return": float(bw.iloc[-1] - 1.0),
        "strategy_cagr": float(s_cagr),
        "k200_cagr": float(b_cagr),
        "relative_cagr": float(rel_cagr),
        "strategy_vol": float(s.std(ddof=1) * math.sqrt(periods)),
        "strategy_sharpe": float(s.mean() / s.std(ddof=1) * math.sqrt(periods)) if s.std(ddof=1) > 0 else np.nan,
        "tracking_error": float(te),
        "information_ratio": float(ir),
        "beta_to_k200": float(beta),
        "capm_alpha_ann": float(alpha),
        "strategy_mdd": float((sw / sw.cummax() - 1.0).min()),
        "relative_mdd": float((rel / rel.cummax() - 1.0).min()),
        "up_capture": float(up_capture),
        "down_capture": float(down_capture),
        "top20_rally_capture": float(rally_capture),
        "annual_turnover": float(g["turnover"].mean() * periods),
        "avg_exposure": float(g["exposure"].mean()),
        "avg_holdings": float(g["n_holdings"].mean()),
        "avg_top1_weight": float(g["top1_weight"].mean()),
        "avg_top5_weight": float(g["top5_weight"].mean()),
        "avg_effective_names": float((1.0 / g["hhi"].replace(0, np.nan)).mean()),
    }


def summarize(detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict] = []
    yearly: list[dict] = []
    for (strategy, cost), g0 in detail.groupby(["strategy", "cost_bps"]):
        for sample, lo, hi in (
            ("train", START, SPLIT),
            ("test", SPLIT, END + pd.Timedelta(days=1)),
        ):
            g = g0[(g0.date >= lo) & (g0.date < hi)].copy()
            if len(g) < 20:
                continue
            row = {"strategy": strategy, "cost_bps": cost, "sample": sample}
            row.update(metrics(g))
            rows.append(row)
        test = g0[g0.date >= SPLIT].copy()
        if not test.empty:
            test["year"] = test.date.dt.year
            for year, gy in test.groupby("year"):
                yearly.append({
                    "strategy": strategy,
                    "cost_bps": cost,
                    "year": year,
                    "strategy_return": float((1.0 + gy.net).prod() - 1.0),
                    "k200_return": float((1.0 + gy.k200_return).prod() - 1.0),
                    "relative_return": float((1.0 + gy.net).prod() / (1.0 + gy.k200_return).prod() - 1.0),
                    "n_periods": len(gy),
                })
    return pd.DataFrame(rows), pd.DataFrame(yearly)


def main() -> None:
    returns, basic_panels = base.load_basic()
    returns = returns.loc[:END]
    panel = lab.build_panel("K200", returns, basic_panels)
    fwd20 = lab.forward_return(returns, lab.HORIZON)
    ic = lab.ic_detail(panel, fwd20, "K200")
    static, mapping, _ = lab.factor_maps(ic, "K200")
    scores, selections = lab.score_history(panel, ic, "K200", static, mapping)

    signal_dates = sorted(panel.index.get_level_values("date").unique())
    k200_close = download_kospi200()
    k200_period = forward_index_returns(k200_close, signal_dates, STEP)

    all_detail = []
    all_weights = []
    for cost in COSTS:
        detail, weights = run_backtest(panel, scores, returns, basic_panels, k200_period, cost)
        all_detail.append(detail)
        all_weights.append(weights)
    detail = pd.concat(all_detail, ignore_index=True)
    weights = pd.concat(all_weights, ignore_index=True)
    summary, yearly = summarize(detail)

    detail.to_csv(OUT / "period_returns.csv", index=False, encoding="utf-8-sig")
    weights.to_csv(OUT / "target_weights.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "strategy_summary.csv", index=False, encoding="utf-8-sig")
    yearly.to_csv(OUT / "yearly_returns.csv", index=False, encoding="utf-8-sig")
    selections.to_csv(OUT / "factor_selection_history.csv", index=False, encoding="utf-8-sig")
    k200_close.to_csv(OUT / "kospi200_close.csv", encoding="utf-8-sig")

    key = summary[(summary.sample == "test") & (summary.cost_bps == 60)].sort_values(
        ["relative_cagr", "information_ratio"], ascending=False
    )
    train = summary[(summary.sample == "train") & (summary.cost_bps == 60)][
        ["strategy", "relative_cagr", "information_ratio", "strategy_cagr", "k200_cagr"]
    ].rename(columns={
        "relative_cagr": "train_relative_cagr",
        "information_ratio": "train_ir",
        "strategy_cagr": "train_strategy_cagr",
        "k200_cagr": "train_k200_cagr",
    })
    key = key.merge(train, on="strategy", how="left")
    key.to_csv(OUT / "key_comparison_60bps.csv", index=False, encoding="utf-8-sig")
    (OUT / "summary.md").write_text(
        "# Enhanced K200 Allocation Test\n\n"
        "K200 benchmark weights are proxied by contemporaneous K200 constituent market-cap weights. "
        "Performance benchmark is the actual KOSPI200 price index (^KS200).\n\n"
        + key.to_markdown(index=False),
        encoding="utf-8",
    )
    print(key.to_string(index=False))


if __name__ == "__main__":
    main()
