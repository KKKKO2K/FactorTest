from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIQ_DIR = ROOT / "research" / "liquidity_cross_factor"
REGIME_DIR = ROOT / "research" / "factor_regime_v1"
sys.path.insert(0, str(LIQ_DIR))
sys.path.insert(0, str(REGIME_DIR))

import run_cross_factor_liquidity as base
import run_multi_universe_liquidity as mu
import run_factor_regime as regime

OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)
SPLIT = base.OOS_START
UNIVERSES = mu.UNIVERSES
FWD_HORIZONS = (1, 5, 20)
FACTOR_WINDOWS = {"FACTOR_5D": 1, "FACTOR_10D": 2, "FACTOR_20D": 4, "FACTOR_40D": 8}
LIQ_WINDOWS = {
    # Recent-window sensitivity with baseline held at 20D.
    "LIQ_1D_VS_20D": (1, 20),
    "LIQ_3D_VS_20D": (3, 20),
    "LIQ_5D_VS_20D": (5, 20),
    "LIQ_10D_VS_20D": (10, 20),
    "LIQ_20D_VS_20D": (20, 20),
    # Baseline sensitivity with recent window held at 5D.
    "LIQ_5D_VS_10D": (5, 10),
    "LIQ_5D_VS_40D": (5, 40),
    "LIQ_5D_VS_60D": (5, 60),
    # Slow/slow anchor.
    "LIQ_20D_VS_60D": (20, 60),
}


def diff_tstat(a: pd.Series, b: pd.Series) -> float:
    a, b = a.dropna(), b.dropna()
    if len(a) < 3 or len(b) < 3:
        return np.nan
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = math.sqrt(va / len(a) + vb / len(b))
    return float((a.mean() - b.mean()) / se) if se > 0 else np.nan


def rolling_compound(df: pd.DataFrame, periods: int) -> pd.DataFrame:
    if periods == 1:
        return df.copy()
    return (1.0 + df).rolling(periods, min_periods=periods).apply(np.prod, raw=True) - 1.0


def robust_thresholds(x: pd.Series) -> tuple[float, float] | None:
    x = x.dropna()
    uniq = np.sort(x.unique())
    if len(x) < 30 or len(uniq) < 3:
        return None
    q1, q2 = x.quantile([1 / 3, 2 / 3]).tolist()
    if np.isfinite(q1) and np.isfinite(q2) and q1 < q2:
        return float(q1), float(q2)
    i1 = min(len(uniq) - 2, max(0, int(math.floor((len(uniq) - 1) / 3))))
    i2 = max(i1 + 1, min(len(uniq) - 1, int(math.ceil(2 * (len(uniq) - 1) / 3))))
    if uniq[i1] >= uniq[i2]:
        return None
    return float(uniq[i1]), float(uniq[i2])


def build_factor_states() -> pd.DataFrame:
    path = REGIME_DIR / "results" / "factor_5d_returns.csv"
    f = pd.read_csv(path)
    f["date"] = pd.to_datetime(f["date"])
    rows: list[dict] = []
    for u, gu in f.groupby("universe"):
        ls = gu.pivot(index="date", columns="factor", values="ls_return").sort_index()
        for label, periods in FACTOR_WINDOWS.items():
            comp = rolling_compound(ls, periods)
            valid = comp.notna().sum(axis=1)
            breadth = (comp > 0).sum(axis=1) / valid.replace(0, np.nan)
            for dt, val in breadth.items():
                if valid.loc[dt] < 5 or pd.isna(val):
                    continue
                rows.append({
                    "date": dt,
                    "universe": u,
                    "predictor_type": "FACTOR_BREADTH",
                    "definition": label,
                    "value": float(val),
                    "n_components": int(valid.loc[dt]),
                })
    return pd.DataFrame(rows)


def activity_ratio(raw: pd.DataFrame, recent: int, baseline: int) -> pd.DataFrame:
    if recent == 1:
        recent_avg = raw
        prior = raw.shift(1).rolling(baseline, min_periods=max(8, int(baseline * 0.75))).mean()
    else:
        recent_avg = raw.rolling(recent, min_periods=max(1, int(math.ceil(recent * 0.8)))).mean()
        prior = raw.shift(recent).rolling(baseline, min_periods=max(8, int(baseline * 0.75))).mean()
    return recent_avg / prior


def build_liquidity_states(state_dates: dict[str, pd.DatetimeIndex]) -> pd.DataFrame:
    _, mcap, k200_by_date = base.load_basic()
    market_by_date = mu.load_market_by_date()
    ta = base.load_trading_amount().reindex(index=mcap.index, columns=mcap.columns)
    raw = ta.where(ta > 0)
    ratios = {label: activity_ratio(raw, recent, baseline)
              for label, (recent, baseline) in LIQ_WINDOWS.items()}

    rows: list[dict] = []
    for u in UNIVERSES:
        for dt in state_dates[u]:
            if dt not in k200_by_date or dt not in market_by_date:
                continue
            codes = mu.universe_codes(u, k200_by_date[dt], market_by_date[dt])
            min_obs = 60 if u == "K200" else 100
            for label, frame in ratios.items():
                if dt not in frame.index:
                    continue
                x = frame.loc[dt].reindex(codes).dropna()
                if len(x) < min_obs:
                    continue
                rows.append({
                    "date": dt,
                    "universe": u,
                    "predictor_type": "LIQUIDITY_BREADTH",
                    "definition": label,
                    "value": float((x > 1.0).mean()),
                    "n_components": int(len(x)),
                })
    return pd.DataFrame(rows)


def load_market_forward() -> dict[int, pd.DataFrame]:
    p = REGIME_DIR / "results" / "market_daily_returns.csv"
    m = pd.read_csv(p, index_col=0)
    m.index = pd.to_datetime(m.index)
    m = m.sort_index()
    return {h: regime.forward_market(m, h) for h in FWD_HORIZONS}


def run_tests(states: pd.DataFrame, market_fwd: dict[int, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict] = []
    for (ptype, definition, u), g0 in states.groupby(["predictor_type", "definition", "universe"]):
        g = g0.sort_values("date").copy()
        th = robust_thresholds(g.loc[g.date < SPLIT, "value"])
        if th is None:
            continue
        q1, q2 = th
        g["bin"] = np.where(g.value <= q1, "LOW", np.where(g.value >= q2, "HIGH", "MID"))
        for h in FWD_HORIZONS:
            if u not in market_fwd[h].columns:
                continue
            g["fwd"] = g.date.map(market_fwd[h][u])
            for sample, mask in (("TRAIN", g.date < SPLIT), ("OOS", g.date >= SPLIT)):
                x = g.loc[mask & g.fwd.notna()]
                lo = x.loc[x.bin == "LOW", "fwd"].dropna()
                hi = x.loc[x.bin == "HIGH", "fwd"].dropna()
                if len(lo) < 8 or len(hi) < 8:
                    continue
                rows.append({
                    "sample": sample,
                    "predictor_type": ptype,
                    "definition": definition,
                    "universe": u,
                    "forward_horizon": h,
                    "train_q1": q1,
                    "train_q2": q2,
                    "n_low": len(lo),
                    "n_high": len(hi),
                    "low_mean": float(lo.mean()),
                    "high_mean": float(hi.mean()),
                    "high_minus_low": float(hi.mean() - lo.mean()),
                    "diff_tstat": diff_tstat(hi, lo),
                    "low_positive_share": float((lo > 0).mean()),
                    "high_positive_share": float((hi > 0).mean()),
                })
    return pd.DataFrame(rows)


def aggregate_tests(tests: pd.DataFrame) -> pd.DataFrame:
    tr = tests[tests["sample"] == "TRAIN"].copy()
    oo = tests[tests["sample"] == "OOS"].copy()
    keys = ["predictor_type", "definition", "universe", "forward_horizon"]
    m = tr[keys + ["high_minus_low", "diff_tstat"]].merge(
        oo[keys + ["high_minus_low", "diff_tstat"]], on=keys, suffixes=("_train", "_oos"))
    m["same_sign"] = np.sign(m.high_minus_low_train) == np.sign(m.high_minus_low_oos)
    m["oos_confirmed"] = np.sign(m.high_minus_low_train) * m.high_minus_low_oos
    m["abs_oos_hl"] = m.high_minus_low_oos.abs()
    m.to_csv(OUT / "train_oos_cell_comparison.csv", index=False, encoding="utf-8-sig")

    rows = []
    for keys2, g in m.groupby(["predictor_type", "definition", "forward_horizon"]):
        ptype, definition, h = keys2
        stable = g[g.same_sign]
        rows.append({
            "predictor_type": ptype,
            "definition": definition,
            "forward_horizon": h,
            "n_universes": len(g),
            "same_sign_rate": float(g.same_sign.mean()),
            "median_oos_confirmed": float(g.oos_confirmed.median()),
            "median_abs_oos_hl": float(g.abs_oos_hl.median()),
            "median_abs_oos_hl_same_sign": float(stable.abs_oos_hl.median()) if len(stable) else np.nan,
            "mean_abs_oos_tstat": float(g.diff_tstat_oos.abs().mean()),
        })
    return pd.DataFrame(rows)


def format_pct(x: float) -> str:
    return "nan" if pd.isna(x) else f"{x:+.2%}"


def summarize(agg: pd.DataFrame, cell: pd.DataFrame) -> str:
    lines = [
        "# Factor Regime Horizon Robustness", "",
        "Purpose: compare nearby lookback definitions before building the 2x2 factor-breadth x liquidity-breadth regime map.",
        "Factor breadth uses canonical factor long-short returns compounded over 5/10/20/40 trading days.",
        "Liquidity breadth is the share of universe stocks whose recent average trading amount exceeds a strictly preceding baseline. Recent-window sensitivity holds the baseline at 20D (1/3/5/10/20 vs 20); baseline sensitivity holds the recent window at 5D (5 vs 10/20/40/60), with 20/60 as a slow anchor.",
        "State low/high thresholds are fit on 2016-2022 TRAIN only and frozen for 2023+ OOS. Market target is the same universe. Forward horizons are 1/5/20D.",
        "Selection principle: prefer TRAIN->OOS sign stability and a broad neighboring-horizon plateau, not the single largest OOS return spread.", "",
    ]

    for ptype in ("FACTOR_BREADTH", "LIQUIDITY_BREADTH"):
        lines += [f"## {ptype}", ""]
        z = agg[agg.predictor_type == ptype].copy()
        overall = (z.groupby("definition")
                   .agg(same_sign_rate=("same_sign_rate", "mean"),
                        median_oos_confirmed=("median_oos_confirmed", "median"),
                        median_abs_oos_hl=("median_abs_oos_hl", "median"))
                   .reset_index())
        for _, r in overall.sort_values(["same_sign_rate", "median_oos_confirmed"], ascending=False).iterrows():
            lines.append(
                f"- {r.definition}: avg sign-stability {r.same_sign_rate:.0%}; "
                f"median sign-confirmed OOS H-L {format_pct(r.median_oos_confirmed)}; "
                f"median |OOS H-L| {format_pct(r.median_abs_oos_hl)}"
            )
        lines.append("")
        for h in FWD_HORIZONS:
            zh = z[z.forward_horizon == h].sort_values(["same_sign_rate", "median_oos_confirmed"], ascending=False)
            lines.append(f"Forward {h}D:")
            for _, r in zh.iterrows():
                lines.append(
                    f"- {r.definition}: sign-stability {r.same_sign_rate:.0%}, "
                    f"confirmed OOS {format_pct(r.median_oos_confirmed)}, "
                    f"median |H-L| {format_pct(r.median_abs_oos_hl)}"
                )
            lines.append("")

    lines += ["## Universe detail: 20D forward return", ""]
    c20 = cell[cell.forward_horizon == 20].copy()
    for u in UNIVERSES:
        lines.append(f"### {u}")
        z = c20[c20.universe == u]
        for ptype in ("FACTOR_BREADTH", "LIQUIDITY_BREADTH"):
            zz = z[z.predictor_type == ptype].sort_values("oos_confirmed", ascending=False)
            if zz.empty:
                continue
            lines.append(f"{ptype}:")
            for _, r in zz.iterrows():
                lines.append(
                    f"- {r.definition}: TRAIN H-L {format_pct(r.high_minus_low_train)}, "
                    f"OOS H-L {format_pct(r.high_minus_low_oos)}, same-sign={bool(r.same_sign)}"
                )
        lines.append("")

    lines += [
        "## Guardrails", "",
        "- This is a horizon robustness screen, not an optimization exercise. Do not choose a definition solely because it has the largest OOS H-L.",
        "- 20D forward returns overlap across 5D state dates; t-stats are descriptive.",
        "- If adjacent lookbacks behave similarly, prefer the simpler/slower definition unless responsiveness is economically important.",
        "- Any 2x2 regime test performed after this screen is post-discovery validation, not pristine OOS.", "",
    ]
    return "\n".join(lines)


def main() -> None:
    factor_states = build_factor_states()
    state_dates = {u: pd.DatetimeIndex(sorted(factor_states.loc[factor_states.universe == u, "date"].unique()))
                   for u in UNIVERSES}
    liq_states = build_liquidity_states(state_dates)
    states = pd.concat([factor_states, liq_states], ignore_index=True).sort_values(
        ["predictor_type", "definition", "universe", "date"])
    states.to_csv(OUT / "horizon_state_values.csv", index=False, encoding="utf-8-sig")

    market_fwd = load_market_forward()
    tests = run_tests(states, market_fwd)
    tests.to_csv(OUT / "horizon_tests.csv", index=False, encoding="utf-8-sig")
    agg = aggregate_tests(tests)
    agg.to_csv(OUT / "horizon_aggregate.csv", index=False, encoding="utf-8-sig")
    cell = pd.read_csv(OUT / "train_oos_cell_comparison.csv")
    text = summarize(agg, cell)
    (OUT / "RESEARCH_SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
