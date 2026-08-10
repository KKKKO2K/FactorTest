from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "k200_factor_sleeve_aggregation_results"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("seqattr", HERE / "k200_sequence_attribution.py")
seqattr = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(seqattr)

off = seqattr.off
lab = seqattr.lab
base = seqattr.base
seqbase = seqattr.seqbase
INDEX_ASSET = seqattr.INDEX_ASSET
START, SPLIT, END, STEP = seqattr.START, seqattr.SPLIT, seqattr.END, seqattr.STEP
COST_BPS = seqattr.COST_BPS

ENGINE_SPECS = {
    "VALUE_REV_30": {
        "components": {"VALUE": 0.35, "REVISION": 0.25, "VALUE_UNLOCK": 0.25, "PRIVATE": 0.15},
        "top_n": 30,
        "kappa": 2.2,
        "cap": 0.35,
        "index_weight": 0.70,
    },
    "REV_BREADTH_70": {
        "components": {"REVISION": 0.30, "EARNINGS_BREADTH": 0.30, "LONG_MOM": 0.20, "PRIVATE": 0.20},
        "top_n": 20,
        "kappa": 2.2,
        "cap": 0.35,
        "index_weight": 0.30,
    },
    "CONTRARIAN_70": {
        "components": {"VALUE": 0.35, "SHORT_REVERSAL": 0.30, "PRIVATE": 0.20, "REVISION": 0.15},
        "top_n": 20,
        "kappa": 2.2,
        "cap": 0.35,
        "index_weight": 0.30,
    },
}


def build_true_calendar_panel_fixed(returns, basic_panels):
    trading = returns.loc[(returns.index >= START) & (returns.index <= END)].index
    schedule = list(trading[::STEP])
    available = sorted(pd.Timestamp(x) for x in basic_panels if pd.Timestamp(x) <= END)
    available_np = np.array(available, dtype="datetime64[ns]")
    asof_map = {}
    for dt in schedule:
        pos = np.searchsorted(available_np, np.datetime64(dt), side="right") - 1
        if pos >= 0:
            asof_map[pd.Timestamp(dt)] = available[int(pos)]
    scheduled_panels = {dt: basic_panels[eff] for dt, eff in asof_map.items()}

    glb = lab.build_panel.__globals__
    original_raw = glb["raw_snapshot"]
    original_step = glb["STEP"]
    original_start = glb["START"]
    original_end = glb["END"]

    def raw_scheduled(dt, universe, returns_, _scheduled, factor_cache):
        eff = asof_map[pd.Timestamp(dt)]
        f = original_raw(eff, universe, returns_, basic_panels, factor_cache)
        q = f.reset_index()
        q["date"] = pd.Timestamp(dt)
        return q.set_index(["date", "code"])

    try:
        glb["raw_snapshot"] = raw_scheduled
        glb["STEP"] = 1
        glb["START"] = START
        glb["END"] = END
        panel = lab.build_panel("K200", returns, scheduled_panels)
    finally:
        glb["raw_snapshot"] = original_raw
        glb["STEP"] = original_step
        glb["START"] = original_start
        glb["END"] = original_end

    schedule_map = pd.DataFrame([
        {
            "scheduled_date": dt,
            "factor_snapshot_date": eff,
            "calendar_day_staleness": int((dt - eff).days),
            "exact_snapshot": bool(dt == eff),
        }
        for dt, eff in asof_map.items()
    ])
    return panel, scheduled_panels, schedule_map


def factor_sleeve_target(g0: pd.DataFrame, basic: pd.DataFrame, engine: str):
    spec0 = ENGINE_SPECS[engine]
    benchmark = off.benchmark_weights(g0, basic)
    g = g0.copy()
    g.index = g.index.get_level_values("code")

    combined = pd.Series(dtype=float)
    memberships = pd.DataFrame(index=benchmark.index)
    sleeve_weight_rows = []

    for factor, budget in spec0["components"].items():
        sleeve = off.satellite(
            benchmark,
            g[factor],
            kappa=spec0["kappa"],
            top_n=spec0["top_n"],
            cap=spec0["cap"],
        )
        idx = combined.index.union(sleeve.index)
        combined = combined.reindex(idx, fill_value=0.0) + budget * sleeve.reindex(idx, fill_value=0.0)
        memberships[factor] = memberships.index.isin(sleeve.index).astype(int)
        for code, w in sleeve.items():
            sleeve_weight_rows.append({"factor": factor, "asset": code, "factor_budget": budget, "within_factor_weight": float(w), "budgeted_weight": float(budget * w)})

    combined = combined[combined > 1e-12]
    combined = combined / combined.sum()
    target = off.mix(spec0["index_weight"], combined).sort_values(ascending=False)

    counts = memberships[list(spec0["components"])].sum(axis=1)
    stock_weights = target.drop(INDEX_ASSET, errors="ignore")
    stock_total = float(stock_weights.sum())
    consensus = counts.reindex(stock_weights.index).fillna(0)
    diag = {
        "factor_union_names": int((counts > 0).sum()),
        "factor_overlap_names_ge2": int((counts >= 2).sum()),
        "factor_overlap_names_ge3": int((counts >= 3).sum()),
        "factor_overlap_names_all": int((counts == len(spec0["components"])).sum()),
        "stock_weight_in_ge2": float(stock_weights[consensus >= 2].sum() / stock_total) if stock_total > 0 else 0.0,
        "stock_weight_in_ge3": float(stock_weights[consensus >= 3].sum() / stock_total) if stock_total > 0 else 0.0,
        "weighted_mean_factor_count": float((stock_weights / stock_total * consensus).sum()) if stock_total > 0 else 0.0,
        "max_factor_count": int(consensus.max()) if len(consensus) else 0,
    }
    return target, diag, pd.DataFrame(sleeve_weight_rows)


def target_for_variant(variant, g0, z, basic, engine):
    base_target = off.targets_for_date(g0, z, basic)[engine].sort_values(ascending=False)
    empty_diag = {
        "factor_union_names": 0,
        "factor_overlap_names_ge2": 0,
        "factor_overlap_names_ge3": 0,
        "factor_overlap_names_all": 0,
        "stock_weight_in_ge2": 0.0,
        "stock_weight_in_ge3": 0.0,
        "weighted_mean_factor_count": 0.0,
        "max_factor_count": 0,
    }
    if variant == "COMPOSITE" or engine not in ENGINE_SPECS:
        return base_target, empty_diag, pd.DataFrame()
    return factor_sleeve_target(g0, basic, engine)


def simulate(variant, panel, scores, returns, scheduled_panels, k200_period, leader_signal):
    fwd10 = lab.forward_return(returns, STEP)
    old_end = pd.Series(dtype=float)
    rows, weight_rows, sleeve_rows = [], [], []

    for dt0, g0 in panel.groupby(level="date"):
        dt = pd.Timestamp(dt0)
        if dt not in scores or dt not in k200_period.index or pd.isna(k200_period.loc[dt]) or dt not in fwd10.index:
            continue

        state = str(g0["state"].iloc[0])
        size_state = str(g0["size_state"].iloc[0])
        leader_on = bool(leader_signal.at[dt, "leader_on"])
        engine = seqattr.current_engine(state, size_state, leader_on)

        target, diag, sleeve_detail = target_for_variant(variant, g0, scores[dt], scheduled_panels[dt], engine)
        if not sleeve_detail.empty:
            sleeve_detail.insert(0, "date", dt)
            sleeve_detail.insert(1, "engine", engine)
            sleeve_rows.append(sleeve_detail)

        codes = g0.index.get_level_values("code")
        stock_future = fwd10.loc[dt].reindex(codes).fillna(0.0)
        asset_r = stock_future.copy()
        asset_r.loc[INDEX_ASSET] = float(k200_period.loc[dt])
        rr = asset_r.reindex(target.index).fillna(0.0)

        turn = seqattr.turnover(old_end, target)
        gross = float((target * rr).sum())
        net = gross - turn * COST_BPS / 10000.0
        denom = 1.0 + gross
        old_end = target * (1.0 + rr) / denom if denom > 0 else target.copy()
        old_end = old_end[old_end.abs() > 1e-12]

        stock_w = target.drop(INDEX_ASSET, errors="ignore").sort_values(ascending=False)
        rows.append({
            "date": dt,
            "variant": variant,
            "state": state,
            "size_state": size_state,
            "leader_on": leader_on,
            "engine": engine,
            "gross": gross,
            "net": net,
            "k200_return": float(k200_period.loc[dt]),
            "active_return": net - float(k200_period.loc[dt]),
            "turnover": turn,
            "index_weight": float(target.get(INDEX_ASSET, 0.0)),
            "stock_weight": float(stock_w.sum()),
            "n_stocks": int((stock_w > 1e-10).sum()),
            "top1_stock_weight": float(stock_w.head(1).sum()),
            "top5_stock_weight": float(stock_w.head(5).sum()),
            **diag,
        })
        for asset, w in target.items():
            weight_rows.append({"date": dt, "variant": variant, "engine": engine, "asset": asset, "weight": float(w)})

    return pd.DataFrame(rows), pd.DataFrame(weight_rows), (pd.concat(sleeve_rows, ignore_index=True) if sleeve_rows else pd.DataFrame())


def metrics(g):
    g = g.sort_values("date").dropna(subset=["net", "k200_return"])
    periods = 252 / STEP
    years = len(g) / periods
    s, b = g.net, g.k200_return
    active = s - b
    sw, bw = (1 + s).cumprod(), (1 + b).cumprod()
    rw = sw / bw
    return {
        "n_periods": len(g),
        "strategy_cagr": float(sw.iloc[-1] ** (1 / years) - 1),
        "k200_cagr": float(bw.iloc[-1] ** (1 / years) - 1),
        "relative_cagr": float(rw.iloc[-1] ** (1 / years) - 1),
        "information_ratio": float(active.mean() / active.std(ddof=1) * math.sqrt(periods)) if active.std(ddof=1) > 0 else np.nan,
        "strategy_mdd": float((sw / sw.cummax() - 1).min()),
        "relative_mdd": float((rw / rw.cummax() - 1).min()),
        "annual_turnover": float(g.turnover.mean() * periods),
        "avg_n_stocks": float(g.n_stocks.mean()),
        "avg_top1_stock_weight": float(g.top1_stock_weight.mean()),
        "avg_top5_stock_weight": float(g.top5_stock_weight.mean()),
    }


def summarize(detail):
    rows = []
    for variant, g0 in detail.groupby("variant"):
        for sample, lo, hi in (("train", START, SPLIT), ("test", SPLIT, END + pd.Timedelta(days=1))):
            g = g0[(g0.date >= lo) & (g0.date < hi)]
            if len(g) >= 5:
                rows.append({"variant": variant, "sample": sample, **metrics(g)})
    return pd.DataFrame(rows)


def compare_periods(detail):
    a = detail[detail.variant == "COMPOSITE"].set_index("date").sort_index()
    b = detail[detail.variant == "FACTOR_SLEEVES"].set_index("date").sort_index()
    dates = a.index.intersection(b.index)
    rows = []
    for dt in dates:
        rows.append({
            "date": dt,
            "sample": "train" if dt < SPLIT else "test",
            "state": b.at[dt, "state"],
            "engine": b.at[dt, "engine"],
            "composite_net": float(a.at[dt, "net"]),
            "sleeves_net": float(b.at[dt, "net"]),
            "delta_net": float(b.at[dt, "net"] - a.at[dt, "net"]),
            "turnover_delta": float(b.at[dt, "turnover"] - a.at[dt, "turnover"]),
            "n_stocks_delta": float(b.at[dt, "n_stocks"] - a.at[dt, "n_stocks"]),
            "top1_stock_weight_delta": float(b.at[dt, "top1_stock_weight"] - a.at[dt, "top1_stock_weight"]),
            "top5_stock_weight_delta": float(b.at[dt, "top5_stock_weight"] - a.at[dt, "top5_stock_weight"]),
        })
    return pd.DataFrame(rows)


def grouped_attribution(comp):
    q = comp[comp["sample"] == "test"].copy()
    rows = []
    for group_type, grp in (("engine", q.groupby("engine")), ("state", q.groupby("state"))):
        for key, g in grp:
            rows.append({
                "group_type": group_type,
                "group": key,
                "n_periods": len(g),
                "mean_delta_bp": float(g.delta_net.mean() * 10000),
                "median_delta_bp": float(g.delta_net.median() * 10000),
                "hit_rate": float((g.delta_net > 0).mean()),
                "mean_turnover_delta": float(g.turnover_delta.mean()),
                "mean_n_stocks_delta": float(g.n_stocks_delta.mean()),
                "mean_top1_stock_weight_delta": float(g.top1_stock_weight_delta.mean()),
                "mean_top5_stock_weight_delta": float(g.top5_stock_weight_delta.mean()),
            })
    return pd.DataFrame(rows)


def consensus_summary(detail):
    q = detail[(detail.variant == "FACTOR_SLEEVES") & (detail.engine.isin(ENGINE_SPECS))].copy()
    rows = []
    for sample, lo, hi in (("train", START, SPLIT), ("test", SPLIT, END + pd.Timedelta(days=1))):
        z = q[(q.date >= lo) & (q.date < hi)]
        for engine, g in z.groupby("engine"):
            rows.append({
                "sample": sample,
                "engine": engine,
                "n_periods": len(g),
                "avg_union_names": float(g.factor_union_names.mean()),
                "avg_overlap_names_ge2": float(g.factor_overlap_names_ge2.mean()),
                "avg_overlap_names_ge3": float(g.factor_overlap_names_ge3.mean()),
                "avg_overlap_names_all": float(g.factor_overlap_names_all.mean()),
                "avg_stock_weight_in_ge2": float(g.stock_weight_in_ge2.mean()),
                "avg_stock_weight_in_ge3": float(g.stock_weight_in_ge3.mean()),
                "avg_weighted_factor_count": float(g.weighted_mean_factor_count.mean()),
            })
    return pd.DataFrame(rows)


def main():
    returns, basic_panels = base.load_basic()
    returns = returns.loc[:END]
    panel, scheduled_panels, schedule_map = build_true_calendar_panel_fixed(returns, basic_panels)

    fwd20 = lab.forward_return(returns, lab.HORIZON)
    ic = lab.ic_detail(panel, fwd20, "K200")
    static, mapping, _ = lab.factor_maps(ic, "K200")
    scores, _ = lab.score_history(panel, ic, "K200", static, mapping)

    signal_dates = sorted(panel.index.get_level_values("date").unique())
    k200_close = seqattr.download_kospi200_patched()
    k200_period = seqattr.forward_index_returns_aligned(k200_close, signal_dates, STEP, returns.index)

    candidate_detail, _ = off.run_all(panel, scores, returns, scheduled_panels, k200_period, cost_bps=COST_BPS)
    leader_signal = seqattr.build_leader_signal(panel, candidate_detail)

    details, weights, sleeves = [], [], []
    for variant in ("COMPOSITE", "FACTOR_SLEEVES"):
        d, w, s = simulate(variant, panel, scores, returns, scheduled_panels, k200_period, leader_signal)
        details.append(d)
        weights.append(w)
        if not s.empty:
            s.insert(1, "variant", variant)
            sleeves.append(s)

    detail = pd.concat(details, ignore_index=True)
    weight = pd.concat(weights, ignore_index=True)
    sleeve_detail = pd.concat(sleeves, ignore_index=True) if sleeves else pd.DataFrame()
    summary = summarize(detail)
    comparison = compare_periods(detail)
    attribution = grouped_attribution(comparison)
    consensus = consensus_summary(detail)

    schedule_map.to_csv(OUT / "true_calendar_schedule_map.csv", index=False, encoding="utf-8-sig")
    detail.to_csv(OUT / "period_returns.csv", index=False, encoding="utf-8-sig")
    weight.to_csv(OUT / "target_weights.csv", index=False, encoding="utf-8-sig")
    sleeve_detail.to_csv(OUT / "factor_sleeve_detail.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "strategy_summary.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(OUT / "period_comparison.csv", index=False, encoding="utf-8-sig")
    attribution.to_csv(OUT / "engine_state_attribution.csv", index=False, encoding="utf-8-sig")
    consensus.to_csv(OUT / "consensus_diagnostics.csv", index=False, encoding="utf-8-sig")

    oos = summary[summary["sample"] == "test"].copy()
    train = summary[summary["sample"] == "train"].copy()
    text = [
        "# K200 Composite vs Factor Sleeve Aggregation",
        "",
        "## Test design",
        "",
        "- Same market-state router and Leader override.",
        "- Same engine factor budgets as the existing composite score.",
        "- Same per-engine Top N, kappa, and within-factor sleeve cap.",
        "- Factor sleeves are aggregated at portfolio level; overlapping names receive weight from every sleeve that selects them.",
        "- No final post-aggregation recap, so natural consensus concentration is preserved and measured.",
        "- Global sequence overlay remains OFF.",
        "",
        "## OOS summary",
        "",
        oos.to_markdown(index=False),
        "",
        "## Train summary",
        "",
        train.to_markdown(index=False),
        "",
        "## OOS engine/state attribution",
        "",
        attribution.to_markdown(index=False),
        "",
        "## Factor consensus diagnostics",
        "",
        consensus.to_markdown(index=False),
    ]
    (OUT / "summary.md").write_text("\n".join(text), encoding="utf-8")
    print("\n".join(text))


if __name__ == "__main__":
    main()
