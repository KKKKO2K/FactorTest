from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "k200_universe_portability_results"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("seqattr", HERE / "k200_sequence_attribution.py")
seqattr = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(seqattr)

lab = seqattr.lab
base = seqattr.base
off = seqattr.off
enh = seqattr.enh
INDEX_ASSET = seqattr.INDEX_ASSET
START, SPLIT, END, STEP = seqattr.START, seqattr.SPLIT, seqattr.END, seqattr.STEP
COST_BPS = seqattr.COST_BPS

LOCAL_UNIVERSES = ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"]
ACTIVE_OFF_ENGINES = {"VALUE_REV_30", "REV_BREADTH_70", "CONTRARIAN_70"}


def universe_codes_ext(basic_panel: pd.DataFrame, universe: str) -> pd.Index:
    market = basic_panel["market"].astype(str).str.upper()
    if universe == "K200":
        mask = basic_panel["k200"] == 1
    elif universe == "KOSPI_ALL":
        mask = market.str.contains("KOSPI", na=False)
    elif universe == "KOSPI_EX_K200":
        mask = market.str.contains("KOSPI", na=False) & (basic_panel["k200"] == 0)
    elif universe == "KOSDAQ":
        mask = market.str.contains("KOSDAQ", na=False)
    else:
        raise KeyError(universe)
    return basic_panel.index[mask]


def build_true_calendar_panel_universe(returns, basic_panels, universe):
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
    original_uc = glb["universe_codes"]

    def raw_scheduled(dt, universe_, returns_, _scheduled, factor_cache):
        eff = asof_map[pd.Timestamp(dt)]
        f = original_raw(eff, universe_, returns_, basic_panels, factor_cache)
        q = f.reset_index()
        q["date"] = pd.Timestamp(dt)
        return q.set_index(["date", "code"])

    try:
        glb["universe_codes"] = universe_codes_ext
        glb["raw_snapshot"] = raw_scheduled
        glb["STEP"] = 1
        glb["START"] = START
        glb["END"] = END
        panel = lab.build_panel(universe, returns, scheduled_panels)
    finally:
        glb["universe_codes"] = original_uc
        glb["raw_snapshot"] = original_raw
        glb["STEP"] = original_step
        glb["START"] = original_start
        glb["END"] = original_end

    smap = pd.DataFrame([
        {
            "universe": universe,
            "scheduled_date": dt,
            "factor_snapshot_date": eff,
            "calendar_day_staleness": int((dt - eff).days),
            "exact_snapshot": bool(dt == eff),
        }
        for dt, eff in asof_map.items()
    ])
    return panel, scheduled_panels, smap


def score_history_for(panel, returns, universe):
    fwd20 = lab.forward_return(returns, lab.HORIZON)
    ic = lab.ic_detail(panel, fwd20, universe)
    static, mapping, _ = lab.factor_maps(ic, universe)
    scores, selections = lab.score_history(panel, ic, universe, static, mapping)
    return scores, selections


def synthetic_cap_benchmark(panel, scheduled_panels, returns):
    fwd10 = lab.forward_return(returns, STEP)
    out = {}
    nrows = []
    for dt, g0 in panel.groupby(level="date"):
        dt = pd.Timestamp(dt)
        if dt not in fwd10.index or dt not in scheduled_panels:
            out[dt] = np.nan
            continue
        codes = g0.index.get_level_values("code")
        bp = scheduled_panels[dt].reindex(codes)
        mcap = pd.to_numeric(bp["mcap"], errors="coerce").clip(lower=0.0)
        w = enh.cap_weights(mcap, max_abs=1.0)
        rr = fwd10.loc[dt].reindex(w.index).fillna(0.0)
        out[dt] = float((w * rr).sum()) if len(w) else np.nan
        nrows.append({"date": dt, "n_names": int(len(codes)), "effective_benchmark_names": int(len(w))})
    return pd.Series(out, name="k200_return"), pd.DataFrame(nrows)


def simulate_local(universe, panel, scores, returns, scheduled_panels, benchmark):
    candidate_detail, _ = off.run_all(panel, scores, returns, scheduled_panels, benchmark, cost_bps=COST_BPS)
    leader_signal = seqattr.build_leader_signal(panel, candidate_detail)
    d, w = seqattr.simulate_variant(
        universe, {}, panel, scores, returns, scheduled_panels, benchmark, leader_signal
    )
    d["test_type"] = "LOCAL_UNIVERSE"
    d["selection_universe"] = universe
    w["test_type"] = "LOCAL_UNIVERSE"
    w["selection_universe"] = universe
    return d, w, leader_signal


def simulate_k200_core_kospi_all(
    panel_k200, scores_k200, panel_all, scores_all, returns,
    basic_k200, basic_all, official_k200, leader_signal_k200,
):
    fwd10 = lab.forward_return(returns, STEP)
    old_end = pd.Series(dtype=float)
    rows, weight_rows = [], []
    all_map = {pd.Timestamp(dt): g for dt, g in panel_all.groupby(level="date")}

    for dt0, gk in panel_k200.groupby(level="date"):
        dt = pd.Timestamp(dt0)
        if (
            dt not in scores_k200 or dt not in scores_all or dt not in official_k200.index
            or pd.isna(official_k200.loc[dt]) or dt not in fwd10.index or dt not in all_map
        ):
            continue
        state = str(gk["state"].iloc[0])
        size_state = str(gk["size_state"].iloc[0])
        leader_on = bool(leader_signal_k200.at[dt, "leader_on"])
        engine = seqattr.current_engine(state, size_state, leader_on)

        if engine in ACTIVE_OFF_ENGINES:
            ga = all_map[dt]
            target = off.targets_for_date(ga, scores_all[dt], basic_all[dt])[engine].sort_values(ascending=False)
            selection_mode = "KOSPI_ALL"
            stock_codes = ga.index.get_level_values("code")
        else:
            target = off.targets_for_date(gk, scores_k200[dt], basic_k200[dt])[engine].sort_values(ascending=False)
            selection_mode = "K200"
            stock_codes = gk.index.get_level_values("code")

        stock_future = fwd10.loc[dt].reindex(stock_codes).fillna(0.0)
        asset_r = stock_future.copy()
        asset_r.loc[INDEX_ASSET] = float(official_k200.loc[dt])
        rr = asset_r.reindex(target.index).fillna(0.0)
        turn = seqattr.turnover(old_end, target)
        gross = float((target * rr).sum())
        net = gross - turn * COST_BPS / 10000.0
        denom = 1.0 + gross
        old_end = target * (1.0 + rr) / denom if denom > 0 else target.copy()
        old_end = old_end[old_end.abs() > 1e-12]
        sw = target.sort_values(ascending=False)
        rows.append({
            "date": dt, "variant": "K200_CORE_KOSPI_ALL_OFF", "state": state,
            "size_state": size_state, "leader_on": leader_on, "engine": engine,
            "selection_mode": selection_mode, "gross": gross, "net": net,
            "k200_return": float(official_k200.loc[dt]),
            "active_return": net - float(official_k200.loc[dt]), "turnover": turn,
            "top1_weight": float(sw.head(1).sum()), "top5_weight": float(sw.head(5).sum()),
            "n_holdings": int((target > 1e-10).sum()),
            "index_weight": float(target.get(INDEX_ASSET, 0.0)),
            "test_type": "K200_CORE_EXPANDED_SELECTION", "selection_universe": selection_mode,
        })
        for asset, wt in target.items():
            weight_rows.append({
                "date": dt, "variant": "K200_CORE_KOSPI_ALL_OFF", "engine": engine,
                "asset": asset, "weight": float(wt), "selection_mode": selection_mode,
                "test_type": "K200_CORE_EXPANDED_SELECTION",
            })
    return pd.DataFrame(rows), pd.DataFrame(weight_rows)


def summarize(detail):
    rows = []
    for variant, g0 in detail.groupby("variant"):
        for sample, lo, hi in (("train", START, SPLIT), ("test", SPLIT, END + pd.Timedelta(days=1))):
            g = g0[(g0.date >= lo) & (g0.date < hi)].copy()
            m = seqattr.strategy_metrics(g)
            if m:
                rows.append({"variant": variant, "sample": sample, **m})
    return pd.DataFrame(rows)


def engine_attribution(detail):
    rows = []
    for variant, v0 in detail.groupby("variant"):
        for sample, lo, hi in (("train", START, SPLIT), ("test", SPLIT, END + pd.Timedelta(days=1))):
            q = v0[(v0.date >= lo) & (v0.date < hi)].copy()
            for engine, g in q.groupby("engine"):
                if len(g) < 2:
                    continue
                active = g["net"] - g["k200_return"]
                rows.append({
                    "variant": variant, "sample": sample, "engine": engine,
                    "n_periods": int(len(g)), "mean_active_bp": float(active.mean() * 10000),
                    "median_active_bp": float(active.median() * 10000),
                    "hit_rate": float((active > 0).mean()), "mean_turnover": float(g.turnover.mean()),
                })
    return pd.DataFrame(rows)


def compare_expanded_to_control(detail):
    a = detail[detail.variant == "K200_CONTROL"].set_index("date").sort_index()
    b = detail[detail.variant == "K200_CORE_KOSPI_ALL_OFF"].set_index("date").sort_index()
    dates = a.index.intersection(b.index)
    rows = []
    for dt in dates:
        delta = float(b.at[dt, "net"] - a.at[dt, "net"])
        rows.append({
            "date": dt, "sample": "train" if dt < SPLIT else "test",
            "engine": str(b.at[dt, "engine"]), "selection_mode": str(b.at[dt, "selection_mode"]),
            "control_net": float(a.at[dt, "net"]), "expanded_net": float(b.at[dt, "net"]),
            "delta_net": delta, "delta_bp": delta * 10000,
            "turnover_delta": float(b.at[dt, "turnover"] - a.at[dt, "turnover"]),
        })
    return pd.DataFrame(rows)


def main():
    returns, basic_panels = base.load_basic()
    returns = returns.loc[:END]

    panels, scheduled, scores, benchmark = {}, {}, {}, {}
    schedule_maps, universe_sizes, local_details, local_weights = [], [], [], []

    for universe in LOCAL_UNIVERSES:
        print(f"=== BUILD {universe} ===", flush=True)
        panel, sp, smap = build_true_calendar_panel_universe(returns, basic_panels, universe)
        panels[universe], scheduled[universe] = panel, sp
        schedule_maps.append(smap)
        scores[universe], _ = score_history_for(panel, returns, universe)
        bench, sizes = synthetic_cap_benchmark(panel, sp, returns)
        benchmark[universe] = bench
        sizes["universe"] = universe
        universe_sizes.append(sizes)
        d, w, _ = simulate_local(universe, panel, scores[universe], returns, sp, bench)
        d["variant"] = f"{universe}_LOCAL"
        w["variant"] = f"{universe}_LOCAL"
        local_details.append(d)
        local_weights.append(w)

    signal_dates = sorted(panels["K200"].index.get_level_values("date").unique())
    official_close = seqattr.download_kospi200_patched()
    official_k200 = seqattr.forward_index_returns_aligned(official_close, signal_dates, STEP, returns.index)
    cand_k200, _ = off.run_all(panels["K200"], scores["K200"], returns, scheduled["K200"], official_k200, cost_bps=COST_BPS)
    leader_k200 = seqattr.build_leader_signal(panels["K200"], cand_k200)
    control, control_w = seqattr.simulate_variant(
        "K200_CONTROL", {}, panels["K200"], scores["K200"], returns,
        scheduled["K200"], official_k200, leader_k200
    )
    control["test_type"] = "PRODUCTION_CONTROL"
    control["selection_universe"] = "K200"
    control_w["test_type"] = "PRODUCTION_CONTROL"
    control_w["selection_universe"] = "K200"

    expanded, expanded_w = simulate_k200_core_kospi_all(
        panels["K200"], scores["K200"], panels["KOSPI_ALL"], scores["KOSPI_ALL"],
        returns, scheduled["K200"], scheduled["KOSPI_ALL"], official_k200, leader_k200
    )

    detail = pd.concat([control, expanded] + local_details, ignore_index=True, sort=False)
    weights = pd.concat([control_w, expanded_w] + local_weights, ignore_index=True, sort=False)
    summary = summarize(detail)
    attr = engine_attribution(detail)
    expansion_cmp = compare_expanded_to_control(detail)
    sizes = pd.concat(universe_sizes, ignore_index=True)

    exp_rows = []
    for sample in ["train", "test"]:
        z = expansion_cmp[expansion_cmp["sample"] == sample]
        for engine, g in z.groupby("engine"):
            if len(g) < 2:
                continue
            exp_rows.append({
                "sample": sample, "engine": engine, "n_periods": int(len(g)),
                "mean_delta_bp": float(g.delta_bp.mean()),
                "median_delta_bp": float(g.delta_bp.median()),
                "hit_rate": float((g.delta_bp > 0).mean()),
                "mean_turnover_delta": float(g.turnover_delta.mean()),
            })
    expansion_attr = pd.DataFrame(exp_rows)

    pd.concat(schedule_maps, ignore_index=True).to_csv(OUT / "schedule_map.csv", index=False, encoding="utf-8-sig")
    sizes.to_csv(OUT / "universe_sizes.csv", index=False, encoding="utf-8-sig")
    detail.to_csv(OUT / "period_returns.csv", index=False, encoding="utf-8-sig")
    weights.to_csv(OUT / "target_weights.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "strategy_summary.csv", index=False, encoding="utf-8-sig")
    attr.to_csv(OUT / "engine_attribution.csv", index=False, encoding="utf-8-sig")
    expansion_cmp.to_csv(OUT / "k200_expansion_period_comparison.csv", index=False, encoding="utf-8-sig")
    expansion_attr.to_csv(OUT / "k200_expansion_engine_attribution.csv", index=False, encoding="utf-8-sig")

    oos = summary[summary["sample"] == "test"].copy()
    train = summary[summary["sample"] == "train"].copy()
    text = [
        "# K200 Strategy Universe Portability",
        "",
        "## Design",
        "- K200_CONTROL: official K200 core and current K200 universe.",
        "- K200_CORE_KOSPI_ALL_OFF: keep official K200 core/state/Leader; only VALUE_REV, REV_BREADTH, CONTRARIAN selection universe expands to all KOSPI stocks.",
        "- *_LOCAL: recompute factor percentiles, market state, size leadership, Leader and composite engines inside each universe; benchmark is an internal beginning-of-period cap-weighted universe proxy.",
        "- Same 10-trading-day schedule, current fixed Top N rules, and 60bp one-way turnover cost.",
        "",
        "## OOS strategy summary", oos.to_markdown(index=False), "",
        "## Train strategy summary", train.to_markdown(index=False), "",
        "## K200 core + KOSPI all selection attribution", expansion_attr.to_markdown(index=False), "",
        "## Engine attribution", attr.to_markdown(index=False),
    ]
    (OUT / "summary.md").write_text("\n".join(text), encoding="utf-8")
    print("\n".join(text), flush=True)


if __name__ == "__main__":
    main()
