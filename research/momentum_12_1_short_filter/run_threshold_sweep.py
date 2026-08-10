from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

import run_research as core

OUT = Path(__file__).resolve().parent / "results"
THRESHOLDS = (-10.0, -5.0, 0.0, 5.0, 10.0)
OOS_START = pd.Timestamp("2023-01-01")


def label(threshold: float) -> str:
    sign = "P" if threshold >= 0 else "M"
    return f"MOM12_1_1M_GT_{sign}{abs(int(threshold)):02d}"


def max_drawdown(r: pd.Series) -> float:
    if r.empty:
        return np.nan
    nav = (1.0 + r.fillna(0.0)).cumprod()
    return float((nav / nav.cummax() - 1.0).min())


def ann_return(r: pd.Series, horizon: int) -> float:
    if r.empty:
        return np.nan
    ppy = 252.0 / horizon
    return float((1.0 + r).prod() ** (ppy / len(r)) - 1.0)


def sharpe(r: pd.Series, horizon: int) -> float:
    if len(r) < 3 or r.std(ddof=1) <= 0:
        return np.nan
    return float(r.mean() / r.std(ddof=1) * math.sqrt(252.0 / horizon))


def main() -> None:
    horizon = core.DEFAULT_HORIZON
    step = core.DEFAULT_STEP
    returns, basic_panels = core.load_basic_panels()
    mom12_files = core.dated_files(core.MOM12)
    mom1_files = core.dated_files(core.MOM1)

    dates = sorted(set(basic_panels) & set(mom12_files) & set(mom1_files))[::step]
    current: dict[tuple[str, int, str, int], pd.Series] = {}
    rows: list[dict] = []

    for dt in dates:
        future = core.forward_return(returns, dt, horizon)
        if future.empty:
            continue
        basic = basic_panels[dt]
        names = basic.index[basic["k200"] == 1]
        mom12 = core.load_factor(mom12_files[dt]).reindex(names)
        mom1 = core.load_factor(mom1_files[dt]).reindex(names)
        future_k200 = future.reindex(names)
        benchmark = float(future_k200.dropna().mean()) if future_k200.notna().any() else np.nan

        variants: dict[str, pd.Series] = {"MOM12_1_BASE": mom12}
        for t in THRESHOLDS:
            variants[label(t)] = mom12.where(mom1 > t)

        for variant, score in variants.items():
            eligible = score.dropna()
            ic = core.rank_ic(score, future_k200)
            for top_n in core.TOP_NS:
                for weighting in core.WEIGHTINGS:
                    new_w = core.portfolio_weights(score, top_n, weighting)
                    if new_w.empty:
                        continue
                    gross = float((new_w * future_k200.reindex(new_w.index).fillna(0.0)).sum())
                    for cost_bps in core.COSTS_BPS:
                        key = (variant, top_n, weighting, cost_bps)
                        old_w = current.get(key, pd.Series(dtype=float))
                        turn = core.turnover(old_w, new_w)
                        net = gross - turn * cost_bps / 10000.0
                        rows.append(
                            {
                                "date": dt,
                                "variant": variant,
                                "threshold": np.nan if variant == "MOM12_1_BASE" else next(
                                    t for t in THRESHOLDS if label(t) == variant
                                ),
                                "top_n": top_n,
                                "weighting": weighting,
                                "cost_bps": cost_bps,
                                "net": net,
                                "benchmark": benchmark,
                                "turnover": turn,
                                "n_eligible": len(eligible),
                                "rank_ic": ic,
                            }
                        )
                        current[key] = new_w

    periods = pd.DataFrame(rows)
    periods["date"] = pd.to_datetime(periods["date"])
    periods.to_csv(OUT / "threshold_sweep_period_returns.csv", index=False, encoding="utf-8-sig")

    split = periods.copy()
    split["sample"] = np.where(split["date"] < OOS_START, "IS_PRE_2023", "OOS_2023_PLUS")
    split = pd.concat([split, split.assign(sample="FULL")], ignore_index=True)

    summaries: list[dict] = []
    group_cols = ["sample", "variant", "threshold", "top_n", "weighting", "cost_bps"]
    # Base has NaN threshold, so handle it separately by filling a sentinel for grouping.
    split["threshold_key"] = split["threshold"].fillna(9999.0)
    group_cols = ["sample", "variant", "threshold_key", "top_n", "weighting", "cost_bps"]
    for keys, g in split.groupby(group_cols, dropna=False):
        g = g.sort_values("date")
        summaries.append(
            {
                "sample": keys[0],
                "variant": keys[1],
                "threshold": np.nan if keys[2] == 9999.0 else keys[2],
                "top_n": keys[3],
                "weighting": keys[4],
                "cost_bps": keys[5],
                "n_periods": len(g),
                "annualized_return": ann_return(g["net"], horizon),
                "sharpe": sharpe(g["net"], horizon),
                "mdd": max_drawdown(g["net"]),
                "avg_turnover": float(g["turnover"].mean()),
                "avg_eligible": float(g["n_eligible"].mean()),
                "avg_rank_ic": float(g["rank_ic"].mean()),
            }
        )
    summary = pd.DataFrame(summaries)
    summary.to_csv(OUT / "threshold_sweep_summary.csv", index=False, encoding="utf-8-sig")

    # Compact comparison for the agreed key construction.
    key = summary[
        (summary["top_n"] == 10)
        & (summary["weighting"] == "equal")
        & (summary["cost_bps"] == 30)
        & (summary["sample"].isin(["FULL", "OOS_2023_PLUS"]))
    ].sort_values(["sample", "annualized_return"], ascending=[True, False])
    key.to_csv(OUT / "threshold_sweep_key.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# 1M absolute-threshold sweep",
        "",
        "Thresholds are percentage-point cutoffs on the existing `단기모멘텀` FactorValue.",
        "Key construction: Top10 / equal-weight / 30 bps.",
        "",
    ]
    for sample in ("FULL", "OOS_2023_PLUS"):
        lines += [f"## {sample}", ""]
        for _, r in key[key["sample"] == sample].iterrows():
            t = "BASE" if pd.isna(r["threshold"]) else f"> {r['threshold']:.0f}%"
            lines.append(
                f"- {t}: ann {r['annualized_return']:.2%}, Sharpe {r['sharpe']:.2f}, "
                f"MDD {r['mdd']:.2%}, turnover {r['avg_turnover']:.2f}, eligible {r['avg_eligible']:.1f}"
            )
        lines.append("")
    (OUT / "THRESHOLD_SWEEP.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
