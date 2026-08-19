from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
WM_DIR = ROOT / "research" / "weighted_momentum_filter_sol"
sys.path.insert(0, str(WM_DIR))
import run_weighted_momentum_filter as wm  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = ROOT / "source" / "factor_all_values"
STATE_PATH = HERE / "results" / "state_panel.csv"
OUT = HERE / "results_allocation_nav"
OUT.mkdir(parents=True, exist_ok=True)

OP12_DIR = DATA / "OP(12MF_1M_CHG)"
OPFY1_DIR = DATA / "OP(FY1_1M_CHG)"
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
MCAP_CUTOFF_BN = 250.0
Q_SIDE = 0.20
COSTS_BP = (0, 30, 60)
UNIVERSES = wm.UNIVERSES

SAMPLES = {
    "TRAIN_2017_2022": (pd.Timestamp("2017-01-01"), pd.Timestamp("2022-12-31")),
    "POST_2023_PLUS": (pd.Timestamp("2023-01-01"), pd.Timestamp("2099-12-31")),
    "POST_2023_2024": (pd.Timestamp("2023-01-01"), pd.Timestamp("2024-12-31")),
    "BULL_2025": (pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
    "YTD_2026": (pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31")),
}

STRATEGIES = (
    "MOM_BASE",
    "RMINUS_TO_REV_ANY",
    "RMINUS_TO_REV_POS",
)


def dated_files(folder: Path) -> dict[pd.Timestamp, Path]:
    out = {}
    for p in folder.glob("*.csv"):
        m = DATE_RE.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def load_factor(path: Path) -> pd.Series:
    df = wm.read_csv(path)
    cc = wm.find_col(df, exact=("StockCode", "Code", "종목코드"))
    vc = wm.find_col(df, exact=("FactorValue",), contains=("FactorValue", "factor value"))
    if cc is None or vc is None:
        raise ValueError(f"factor schema not found: {path}")
    s = pd.Series(pd.to_numeric(df[vc], errors="coerce").to_numpy(), index=wm.normalize_code(df[cc]))
    return s[~s.index.duplicated(keep="last")]


def pct_good(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").rank(pct=True, method="average", ascending=True)


def ew_target(score: pd.Series) -> pd.Series | None:
    s = pd.to_numeric(score, errors="coerce").dropna().sort_values(ascending=False)
    n = int(math.floor(len(s) * Q_SIDE))
    if n < 8:
        return None
    names = s.head(n).index
    return pd.Series(1.0 / n, index=names, dtype=float)


def build_targets(returns, mcap, k200_by_date, market_by_date, wmom, panel):
    op12 = dated_files(OP12_DIR)
    opfy1 = dated_files(OPFY1_DIR)
    targets = {u: {} for u in UNIVERSES}
    diag = []
    panel_dates = sorted(set(panel["date"]))
    for i, dt in enumerate(panel_dates, 1):
        if dt not in returns.index or dt not in mcap.index or dt not in wmom.index or dt not in op12 or dt not in opfy1:
            continue
        op12_s = load_factor(op12[dt])
        opfy1_s = load_factor(opfy1[dt])
        for u in UNIVERSES:
            if dt not in k200_by_date or dt not in market_by_date:
                continue
            codes = wm.universe_codes(u, dt, k200_by_date, market_by_date)
            mc = pd.to_numeric(mcap.loc[dt].reindex(codes), errors="coerce")
            elig = mc.index[(mc >= MCAP_CUTOFF_BN).fillna(False)]
            if len(elig) < 40:
                continue
            mom_score = pct_good(pd.to_numeric(wmom.loc[dt].reindex(elig), errors="coerce"))
            r12 = pct_good(op12_s.reindex(elig))
            rfy1 = pct_good(opfy1_s.reindex(elig))
            rev_score = pd.concat([r12.rename("op12"), rfy1.rename("opfy1")], axis=1).mean(axis=1, skipna=False)
            mom = ew_target(mom_score)
            rev = ew_target(rev_score)
            if mom is None or rev is None:
                continue
            targets[u][dt] = {"MOMENTUM": mom, "REVISION": rev}
            overlap = len(mom.index.intersection(rev.index))
            diag.append({
                "date": dt,
                "universe": u,
                "eligible_n": int(len(elig)),
                "mom_n": int(len(mom)),
                "rev_n": int(len(rev)),
                "mom_rev_overlap_n": int(overlap),
                "mom_rev_overlap_share_mom": float(overlap / len(mom)),
            })
        if i % 100 == 0:
            print(f"built targets {i}/{len(panel_dates)}", flush=True)
    return targets, pd.DataFrame(diag)


def choose_family(strategy: str, state: pd.Series) -> str:
    if strategy == "MOM_BASE":
        return "MOMENTUM"
    if strategy == "RMINUS_TO_REV_ANY":
        return "REVISION" if state["momentum_state"] == "R-" else "MOMENTUM"
    if strategy == "RMINUS_TO_REV_POS":
        cond = state["momentum_state"] == "R-" and float(state["revision_top_abs20"]) > 0.0
        return "REVISION" if cond else "MOMENTUM"
    raise ValueError(strategy)


def build_strategy_targets(panel: pd.DataFrame, base_targets):
    store = {u: {s: {} for s in STRATEGIES} for u in UNIVERSES}
    decisions = []
    pidx = panel.set_index(["date", "universe"]).sort_index()
    for u in UNIVERSES:
        for dt, fam_targets in sorted(base_targets[u].items()):
            key = (dt, u)
            if key not in pidx.index:
                continue
            state = pidx.loc[key]
            if isinstance(state, pd.DataFrame):
                state = state.iloc[-1]
            for strategy in STRATEGIES:
                fam = choose_family(strategy, state)
                store[u][strategy][dt] = fam_targets[fam].copy()
                decisions.append({
                    "date": dt,
                    "universe": u,
                    "strategy": strategy,
                    "chosen_family": fam,
                    "momentum_state": state["momentum_state"],
                    "revision_state": state["revision_state"],
                    "revision_top_abs20": float(state["revision_top_abs20"]),
                    "is_rminus": int(state["momentum_state"] == "R-"),
                    "revision_positive": int(float(state["revision_top_abs20"]) > 0.0),
                })
    return store, pd.DataFrame(decisions)


def simulate_one(returns: pd.DataFrame, targets: dict[pd.Timestamp, pd.Series]) -> pd.DataFrame:
    scheduled = sorted(targets)
    if not scheduled:
        return pd.DataFrame()
    scheduled_set = set(scheduled)
    current = pd.Series(dtype=float)
    rows = []
    for dt in returns.index[returns.index >= scheduled[0]]:
        gross = 0.0
        if len(current):
            rr = pd.to_numeric(returns.loc[dt].reindex(current.index), errors="coerce").clip(lower=-0.999999).fillna(0.0)
            gross = float((current * rr).sum())
            grown = current * (1.0 + rr)
            denom = float(grown.sum())
            if denom > 0:
                current = grown / denom
        turnover = 0.0
        if dt in scheduled_set:
            target = targets[dt]
            if len(current):
                union = current.index.union(target.index)
                turnover = float(0.5 * (current.reindex(union, fill_value=0.0) - target.reindex(union, fill_value=0.0)).abs().sum())
            else:
                turnover = 1.0
            current = target.copy()
        rec = {"date": dt, "gross_ret": gross, "turnover": turnover}
        for bp in COSTS_BP:
            cost = turnover * bp / 10000.0
            rec[f"net{bp}_ret"] = (1.0 + gross) * (1.0 - cost) - 1.0
        rows.append(rec)
    return pd.DataFrame(rows)


def cagr(r: pd.Series) -> float:
    r = pd.Series(r).dropna()
    if len(r) < 2:
        return np.nan
    total = float((1.0 + r).prod())
    years = len(r) / 252.0
    return total ** (1.0 / years) - 1.0 if total > 0 and years > 0 else np.nan


def sharpe(r: pd.Series) -> float:
    r = pd.Series(r).dropna()
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(252.0)) if len(r) >= 3 and np.isfinite(sd) and sd > 0 else np.nan


def mdd(r: pd.Series) -> float:
    r = pd.Series(r).dropna()
    if not len(r):
        return np.nan
    nav = (1.0 + r).cumprod()
    return float((nav / nav.cummax() - 1.0).min())


def summarize(daily: pd.DataFrame, decisions: pd.DataFrame):
    rows = []
    for sample, (lo, hi) in SAMPLES.items():
        for (u, strategy), g in daily.groupby(["universe", "strategy"]):
            z = g[(g.date >= lo) & (g.date <= hi)].copy()
            if len(z) < 40:
                continue
            dz = decisions[(decisions.universe == u) & (decisions.strategy == strategy) & (decisions.date >= lo) & (decisions.date <= hi)]
            years = len(z) / 252.0
            for bp in COSTS_BP:
                r = z[f"net{bp}_ret"]
                rows.append({
                    "sample": sample,
                    "universe": u,
                    "strategy": strategy,
                    "cost_bp": bp,
                    "n_days": int(len(z)),
                    "cagr": cagr(r),
                    "sharpe": sharpe(r),
                    "mdd": mdd(r),
                    "ann_turnover": float(z.turnover.sum() / years) if years > 0 else np.nan,
                    "decision_n": int(len(dz)),
                    "revision_exposure": float((dz.chosen_family == "REVISION").mean()) if len(dz) else np.nan,
                    "rminus_decision_n": int(dz.is_rminus.sum()) if len(dz) else 0,
                })
    stats = pd.DataFrame(rows)
    paired = []
    for key, g in stats.groupby(["sample", "universe", "cost_bp"]):
        d = g.set_index("strategy")
        if "MOM_BASE" not in d.index:
            continue
        b = d.loc["MOM_BASE"]
        for strategy in ("RMINUS_TO_REV_ANY", "RMINUS_TO_REV_POS"):
            if strategy not in d.index:
                continue
            s = d.loc[strategy]
            paired.append(dict(zip(["sample", "universe", "cost_bp"], key)) | {
                "strategy": strategy,
                "base_cagr": float(b.cagr),
                "strategy_cagr": float(s.cagr),
                "delta_cagr": float(s.cagr - b.cagr),
                "base_sharpe": float(b.sharpe),
                "strategy_sharpe": float(s.sharpe),
                "delta_sharpe": float(s.sharpe - b.sharpe),
                "base_mdd": float(b.mdd),
                "strategy_mdd": float(s.mdd),
                "delta_mdd": float(s.mdd - b.mdd),
                "base_ann_turnover": float(b.ann_turnover),
                "strategy_ann_turnover": float(s.ann_turnover),
                "delta_ann_turnover": float(s.ann_turnover - b.ann_turnover),
                "revision_exposure": float(s.revision_exposure),
                "rminus_decision_n": int(s.rminus_decision_n),
            })
    return stats, pd.DataFrame(paired)


def decision_summary(decisions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sample, (lo, hi) in SAMPLES.items():
        z0 = decisions[(decisions.date >= lo) & (decisions.date <= hi)]
        for (u, strategy), z in z0.groupby(["universe", "strategy"]):
            if strategy == "MOM_BASE" or len(z) == 0:
                continue
            rminus = z[z.is_rminus == 1]
            rows.append({
                "sample": sample,
                "universe": u,
                "strategy": strategy,
                "decision_n": int(len(z)),
                "rminus_n": int(len(rminus)),
                "rminus_share": float(len(rminus) / len(z)),
                "revision_exposure": float((z.chosen_family == "REVISION").mean()),
                "revision_positive_within_rminus": float(rminus.revision_positive.mean()) if len(rminus) else np.nan,
            })
    return pd.DataFrame(rows)


def write_summary(paired: pd.DataFrame, dsum: pd.DataFrame, target_diag: pd.DataFrame):
    lines = [
        "# Momentum R- -> Revision portfolio NAV backtest",
        "",
        "Tradeable construction: decision uses factor state observed through close t; basket is formed ex-ante at close t and held from t+1. Equal-weight top quintile, mcap >= KRW 250bn, rebalance on the existing 5-trading-day state grid.",
        "",
        "- MOM_BASE: always Momentum top quintile.",
        "- RMINUS_TO_REV_ANY: Momentum R- -> Revision, no Revision sign filter.",
        "- RMINUS_TO_REV_POS: Momentum R- -> Revision only when Revision trailing preferred-leg 20D return > 0.",
        "",
        "Transaction cost = one-way turnover x 0/30/60 bp. 2023+ is researched post-sample, not untouched OOS.",
        "",
    ]
    for bp in (30, 60):
        lines += [f"## NET{bp}: CAGR delta vs always-Momentum", "", "| Sample | Universe | R- -> Rev ANY | R- -> Rev if Rev+ | Rev+ exposure |", "|---|---|---:|---:|---:|"]
        z = paired[paired.cost_bp == bp]
        for sample in SAMPLES:
            for u in UNIVERSES:
                g = z[(z["sample"] == sample) & (z.universe == u)].set_index("strategy")
                if len(g) < 2:
                    continue
                a = g.loc["RMINUS_TO_REV_ANY"]
                p = g.loc["RMINUS_TO_REV_POS"]
                lines.append(f"| {sample} | {u} | {a.delta_cagr:+.2%} | {p.delta_cagr:+.2%} | {p.revision_exposure:.1%} |")
        lines.append("")
    lines += ["## NET30 detailed: KOSDAQ + KOSPI ex-K200", "", "| Sample | Strategy | CAGR delta | Sharpe delta | MDD delta | Ann turnover delta | Revision exposure | R- decisions |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    z = paired[(paired.cost_bp == 30) & (paired.universe == "KOSDAQ_PLUS_KOSPI_EX_K200")]
    for _, r in z.iterrows():
        lines.append(f"| {r['sample']} | {r.strategy} | {r.delta_cagr:+.2%} | {r.delta_sharpe:+.2f} | {r.delta_mdd:+.2%} | {r.delta_ann_turnover:+.2f}x | {r.revision_exposure:.1%} | {int(r.rminus_decision_n)} |")
    lines += ["", "## Decision frequency: KOSDAQ + KOSPI ex-K200", "", "| Sample | Strategy | R- share | Rev positive within R- | Revision exposure |", "|---|---|---:|---:|---:|"]
    z = dsum[dsum.universe == "KOSDAQ_PLUS_KOSPI_EX_K200"]
    for _, r in z.iterrows():
        lines.append(f"| {r['sample']} | {r.strategy} | {r.rminus_share:.1%} | {r.revision_positive_within_rminus:.1%} | {r.revision_exposure:.1%} |")
    lines.append("")
    if len(target_diag):
        x = target_diag.groupby("universe").agg(dates=("date", "count"), avg_mom_n=("mom_n", "mean"), avg_rev_n=("rev_n", "mean"), avg_overlap=("mom_rev_overlap_share_mom", "mean")).reset_index()
        lines += ["## Basket diagnostics", "", "| Universe | dates | avg Momentum N | avg Revision N | avg overlap / Momentum |", "|---|---:|---:|---:|---:|"]
        for _, r in x.iterrows():
            lines.append(f"| {r.universe} | {int(r.dates)} | {r.avg_mom_n:.1f} | {r.avg_rev_n:.1f} | {r.avg_overlap:.1%} |")
        lines.append("")
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    panel = pd.read_csv(STATE_PATH)
    panel["date"] = pd.to_datetime(panel["date"])
    panel = panel.sort_values(["date", "universe"]).reset_index(drop=True)
    print("loading basic", flush=True)
    returns, mcap, k200_by_date, market_by_date = wm.load_basic()
    print("building weighted momentum", flush=True)
    wmom, _ = wm.calendar_weighted_momentum(returns, mcap)
    print("building ex-ante momentum/revision targets", flush=True)
    base_targets, tdiag = build_targets(returns, mcap, k200_by_date, market_by_date, wmom, panel)
    strategy_targets, decisions = build_strategy_targets(panel, base_targets)
    daily_parts = []
    for u in UNIVERSES:
        for strategy in STRATEGIES:
            print(f"simulate {u} {strategy}", flush=True)
            d = simulate_one(returns, strategy_targets[u][strategy])
            if d.empty:
                continue
            d["universe"] = u
            d["strategy"] = strategy
            daily_parts.append(d)
    daily = pd.concat(daily_parts, ignore_index=True)
    stats, paired = summarize(daily, decisions)
    dsum = decision_summary(decisions)
    tdiag.to_csv(OUT / "target_diagnostics.csv", index=False, encoding="utf-8-sig")
    decisions.to_csv(OUT / "decisions.csv", index=False, encoding="utf-8-sig")
    daily.to_csv(OUT / "strategy_daily.csv", index=False, encoding="utf-8-sig")
    stats.to_csv(OUT / "strategy_stats.csv", index=False, encoding="utf-8-sig")
    paired.to_csv(OUT / "paired_vs_momentum.csv", index=False, encoding="utf-8-sig")
    dsum.to_csv(OUT / "decision_summary.csv", index=False, encoding="utf-8-sig")
    write_summary(paired, dsum, tdiag)
    print(f"done daily={len(daily)} stats={len(stats)} paired={len(paired)} decisions={len(decisions)}", flush=True)


if __name__ == "__main__":
    main()
