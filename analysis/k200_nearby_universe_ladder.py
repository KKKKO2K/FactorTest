from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

import k200_universe_portability as up

ADD_N = int(os.environ.get("ADD_N", "50"))
LABEL = f"K200_PLUS_{ADD_N}"
OUT = Path(__file__).resolve().parent / "k200_nearby_universe_ladder_results" / f"PLUS_{ADD_N}"
OUT.mkdir(parents=True, exist_ok=True)

ACTIVE = {"VALUE_REV_30", "REV_BREADTH_70", "CONTRARIAN_70"}
BASE_TOPN = {"VALUE_REV_30": 30, "REV_BREADTH_70": 20, "CONTRARIAN_70": 20}
INDEX_WEIGHT = {"VALUE_REV_30": 0.70, "REV_BREADTH_70": 0.30, "CONTRARIAN_70": 0.30}
SCORE_NAME = {"VALUE_REV_30": "VALUE_REV", "REV_BREADTH_70": "REV_BREADTH", "CONTRARIAN_70": "CONTRARIAN"}


def custom_universe_codes(bp: pd.DataFrame, universe: str) -> pd.Index:
    if universe != LABEL:
        return up._ORIGINAL_UC(bp, universe) if hasattr(up, "_ORIGINAL_UC") else up.universe_codes_ext(bp, universe)
    market = bp["market"].astype(str).str.upper()
    k200 = bp.index[bp["k200"] == 1]
    ex_mask = market.str.contains("KOSPI", na=False) & (bp["k200"] == 0)
    ex = bp.loc[ex_mask].copy()
    ex["_mcap"] = pd.to_numeric(ex["mcap"], errors="coerce")
    extra = ex.sort_values("_mcap", ascending=False).head(ADD_N).index
    return k200.union(extra)


def build_expanded(returns, basic_panels):
    original = up.universe_codes_ext
    up._ORIGINAL_UC = original
    up.universe_codes_ext = custom_universe_codes
    try:
        return up.build_true_calendar_panel_universe(returns, basic_panels, LABEL)
    finally:
        up.universe_codes_ext = original
        if hasattr(up, "_ORIGINAL_UC"):
            delattr(up, "_ORIGINAL_UC")


def active_target(
    engine: str,
    g_exp: pd.DataFrame,
    z_exp: pd.DataFrame,
    basic_exp: pd.DataFrame,
    k200_n: int,
    mode: str,
):
    benchmark = up.off.benchmark_weights(g_exp, basic_exp)
    scores = up.off.candidate_scores(g_exp, z_exp)
    base_n = BASE_TOPN[engine]
    if mode == "FIXED_N":
        top_n = base_n
    elif mode == "PCT_MATCHED":
        ratio = len(benchmark) / max(k200_n, 1)
        top_n = int(round(base_n * ratio))
        top_n = max(base_n, min(top_n, len(benchmark)))
    else:
        raise KeyError(mode)
    sat = up.off.satellite(
        benchmark,
        scores[SCORE_NAME[engine]],
        kappa=2.2,
        top_n=top_n,
        cap=0.35,
    )
    return up.off.mix(INDEX_WEIGHT[engine], sat).sort_values(ascending=False), top_n


def simulate(
    mode: str,
    panel_k200: pd.DataFrame,
    scores_k200: dict,
    panel_exp: pd.DataFrame,
    scores_exp: dict,
    returns: pd.DataFrame,
    basic_k200: dict,
    basic_exp: dict,
    official_k200: pd.Series,
    leader_k200: pd.DataFrame,
):
    fwd10 = up.lab.forward_return(returns, up.STEP)
    exp_map = {pd.Timestamp(dt): g for dt, g in panel_exp.groupby(level="date")}
    old_end = pd.Series(dtype=float)
    rows, weights = [], []

    for dt0, gk in panel_k200.groupby(level="date"):
        dt = pd.Timestamp(dt0)
        if (
            dt not in scores_k200
            or dt not in scores_exp
            or dt not in exp_map
            or dt not in official_k200.index
            or pd.isna(official_k200.loc[dt])
            or dt not in fwd10.index
        ):
            continue

        ge = exp_map[dt]
        state = str(gk["state"].iloc[0])
        size_state = str(gk["size_state"].iloc[0])
        leader_on = bool(leader_k200.at[dt, "leader_on"])
        engine = up.seqattr.current_engine(state, size_state, leader_on)
        k200_codes = pd.Index(gk.index.get_level_values("code").unique())
        exp_codes = pd.Index(ge.index.get_level_values("code").unique())

        selected_top_n = np.nan
        if engine in ACTIVE:
            target, selected_top_n = active_target(
                engine,
                ge,
                scores_exp[dt],
                basic_exp[dt],
                len(k200_codes),
                mode,
            )
            selection_mode = LABEL
        else:
            target = up.off.targets_for_date(
                gk, scores_k200[dt], basic_k200[dt]
            )[engine].sort_values(ascending=False)
            selection_mode = "K200"

        stock_assets = target.index[target.index != up.INDEX_ASSET]
        stock_r = fwd10.loc[dt].reindex(stock_assets).fillna(0.0)
        asset_r = stock_r.copy()
        asset_r.loc[up.INDEX_ASSET] = float(official_k200.loc[dt])
        rr = asset_r.reindex(target.index).fillna(0.0)

        turn = up.seqattr.turnover(old_end, target)
        gross = float((target * rr).sum())
        net = gross - turn * up.COST_BPS / 10000.0
        denom = 1.0 + gross
        old_end = target * (1.0 + rr) / denom if denom > 0 else target.copy()
        old_end = old_end[old_end.abs() > 1e-12]

        outside = stock_assets.difference(k200_codes)
        non_k200_weight = float(target.reindex(outside).fillna(0.0).sum())
        sw = target.drop(up.INDEX_ASSET, errors="ignore").sort_values(ascending=False)
        variant = f"PLUS_{ADD_N}_{mode}"
        rows.append({
            "date": dt,
            "variant": variant,
            "state": state,
            "size_state": size_state,
            "leader_on": leader_on,
            "engine": engine,
            "selection_mode": selection_mode,
            "gross": gross,
            "net": net,
            "k200_return": float(official_k200.loc[dt]),
            "active_return": net - float(official_k200.loc[dt]),
            "turnover": turn,
            "top1_stock_weight": float(sw.head(1).sum()),
            "top5_stock_weight": float(sw.head(5).sum()),
            "n_stock_holdings": int((sw > 1e-10).sum()),
            "index_weight": float(target.get(up.INDEX_ASSET, 0.0)),
            "universe_size": int(len(exp_codes)),
            "k200_size": int(len(k200_codes)),
            "selected_top_n": selected_top_n,
            "n_non_k200_holdings": int(len(outside)),
            "non_k200_weight": non_k200_weight,
        })
        for asset, wt in target.items():
            weights.append({
                "date": dt,
                "variant": variant,
                "engine": engine,
                "asset": asset,
                "weight": float(wt),
                "is_non_k200": bool(asset != up.INDEX_ASSET and asset not in k200_codes),
                "selection_mode": selection_mode,
            })
    return pd.DataFrame(rows), pd.DataFrame(weights)


def compare_to_control(detail: pd.DataFrame) -> pd.DataFrame:
    c = detail[detail.variant == "K200_CONTROL"].set_index("date").sort_index()
    rows = []
    for variant in sorted(v for v in detail.variant.unique() if v != "K200_CONTROL"):
        x = detail[detail.variant == variant].set_index("date").sort_index()
        dates = c.index.intersection(x.index)
        for dt in dates:
            rows.append({
                "date": dt,
                "sample": "train" if dt < up.SPLIT else "test",
                "variant": variant,
                "engine": str(x.at[dt, "engine"]),
                "delta_net": float(x.at[dt, "net"] - c.at[dt, "net"]),
                "delta_bp": float((x.at[dt, "net"] - c.at[dt, "net"]) * 10000),
                "turnover_delta": float(x.at[dt, "turnover"] - c.at[dt, "turnover"]),
                "non_k200_weight": float(x.at[dt, "non_k200_weight"]),
                "n_non_k200_holdings": int(x.at[dt, "n_non_k200_holdings"]),
                "selected_top_n": x.at[dt, "selected_top_n"],
            })
    return pd.DataFrame(rows)


def engine_delta(cmp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, sample, engine), g in cmp.groupby(["variant", "sample", "engine"]):
        if len(g) < 2:
            continue
        rows.append({
            "variant": variant,
            "sample": sample,
            "engine": engine,
            "n_periods": int(len(g)),
            "mean_delta_bp": float(g.delta_bp.mean()),
            "median_delta_bp": float(g.delta_bp.median()),
            "hit_rate": float((g.delta_bp > 0).mean()),
            "mean_turnover_delta": float(g.turnover_delta.mean()),
            "mean_non_k200_weight": float(g.non_k200_weight.mean()),
            "mean_n_non_k200_holdings": float(g.n_non_k200_holdings.mean()),
            "mean_selected_top_n": float(pd.to_numeric(g.selected_top_n, errors="coerce").mean()),
        })
    return pd.DataFrame(rows)


def annual_delta(detail: pd.DataFrame) -> pd.DataFrame:
    c = detail[detail.variant == "K200_CONTROL"].set_index("date").sort_index()
    rows = []
    for variant in sorted(v for v in detail.variant.unique() if v != "K200_CONTROL"):
        x = detail[detail.variant == variant].set_index("date").sort_index()
        dates = c.index.intersection(x.index)
        for year in sorted(set(dates.year)):
            d = dates[dates.year == year]
            if len(d) == 0:
                continue
            rc = float((1.0 + c.loc[d, "net"]).prod() - 1.0)
            rx = float((1.0 + x.loc[d, "net"]).prod() - 1.0)
            rel = float((1.0 + rx) / (1.0 + rc) - 1.0)
            rows.append({"variant": variant, "year": int(year), "n_periods": int(len(d)), "control_return": rc, "variant_return": rx, "relative_vs_control": rel})
    return pd.DataFrame(rows)


def outlier_robustness(cmp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, sample), g0 in cmp.groupby(["variant", "sample"]):
        vals = g0.delta_net.dropna().sort_values(ascending=False)
        for drop_best in (0, 1, 2):
            v = vals.iloc[drop_best:] if len(vals) > drop_best else pd.Series(dtype=float)
            rows.append({
                "variant": variant,
                "sample": sample,
                "drop_best_n": drop_best,
                "n_periods": int(len(v)),
                "mean_delta_bp": float(v.mean() * 10000) if len(v) else np.nan,
                "annualized_arith_delta": float(v.mean() * (252 / up.STEP)) if len(v) else np.nan,
            })
    return pd.DataFrame(rows)


def main():
    returns, basic_panels = up.base.load_basic()
    returns = returns.loc[:up.END]

    print(f"BUILD K200 control, add_n={ADD_N}", flush=True)
    pk, bk, smk = up.build_true_calendar_panel_universe(returns, basic_panels, "K200")
    sk, _ = up.score_history_for(pk, returns, "K200")

    signal_dates = sorted(pk.index.get_level_values("date").unique())
    close = up.seqattr.download_kospi200_patched()
    k200 = up.seqattr.forward_index_returns_aligned(close, signal_dates, up.STEP, returns.index)
    cand, _ = up.off.run_all(pk, sk, returns, bk, k200, cost_bps=up.COST_BPS)
    leader = up.seqattr.build_leader_signal(pk, cand)
    control, cw = up.seqattr.simulate_variant("K200_CONTROL", {}, pk, sk, returns, bk, k200, leader)

    print(f"BUILD {LABEL}", flush=True)
    pe, be, sme = build_expanded(returns, basic_panels)
    se, _ = up.score_history_for(pe, returns, LABEL)

    variants, wvars = [], []
    for mode in ("FIXED_N", "PCT_MATCHED"):
        print(f"SIMULATE {LABEL} {mode}", flush=True)
        d, w = simulate(mode, pk, sk, pe, se, returns, bk, be, k200, leader)
        variants.append(d)
        wvars.append(w)

    detail = pd.concat([control] + variants, ignore_index=True, sort=False)
    weights = pd.concat([cw] + wvars, ignore_index=True, sort=False)
    summary = up.summarize(detail)
    cmp = compare_to_control(detail)
    eng = engine_delta(cmp)
    annual = annual_delta(detail)
    robust = outlier_robustness(cmp)

    sizes = []
    for dt, g in pe.groupby(level="date"):
        k = pk.xs(dt, level="date") if dt in pk.index.get_level_values("date") else pd.DataFrame()
        sizes.append({
            "date": pd.Timestamp(dt),
            "expanded_universe": LABEL,
            "expanded_n": int(len(g)),
            "k200_n": int(len(k)),
            "extra_n": int(len(g) - len(k)),
        })
    sizes = pd.DataFrame(sizes)

    pd.concat([smk, sme], ignore_index=True).to_csv(OUT / "schedule_map.csv", index=False, encoding="utf-8-sig")
    sizes.to_csv(OUT / "universe_sizes.csv", index=False, encoding="utf-8-sig")
    detail.to_csv(OUT / "period_returns.csv", index=False, encoding="utf-8-sig")
    weights.to_csv(OUT / "target_weights.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "strategy_summary.csv", index=False, encoding="utf-8-sig")
    cmp.to_csv(OUT / "period_comparison.csv", index=False, encoding="utf-8-sig")
    eng.to_csv(OUT / "engine_delta.csv", index=False, encoding="utf-8-sig")
    annual.to_csv(OUT / "annual_delta.csv", index=False, encoding="utf-8-sig")
    robust.to_csv(OUT / "outlier_robustness.csv", index=False, encoding="utf-8-sig")

    print("=== SUMMARY ===", flush=True)
    print(summary.to_markdown(index=False), flush=True)
    print("=== ENGINE DELTA ===", flush=True)
    print(eng.to_markdown(index=False), flush=True)
    print("=== OUTLIER ROBUSTNESS ===", flush=True)
    print(robust.to_markdown(index=False), flush=True)


if __name__ == "__main__":
    main()
