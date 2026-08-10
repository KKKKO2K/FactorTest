from __future__ import annotations

import os
from pathlib import Path
import pandas as pd

import k200_universe_portability as up

MODE = os.environ.get("MODE", "LOCAL").upper()
UNIVERSE = os.environ.get("UNIVERSE", "K200")
OUT = Path(__file__).resolve().parent / "k200_universe_portability_parallel_results" / f"{MODE}_{UNIVERSE}"
OUT.mkdir(parents=True, exist_ok=True)


def summarize_one(detail: pd.DataFrame) -> pd.DataFrame:
    return up.summarize(detail)


def run_local():
    returns, basic_panels = up.base.load_basic()
    returns = returns.loc[:up.END]
    panel, sp, smap = up.build_true_calendar_panel_universe(returns, basic_panels, UNIVERSE)
    scores, _ = up.score_history_for(panel, returns, UNIVERSE)
    bench, sizes = up.synthetic_cap_benchmark(panel, sp, returns)
    detail, weights, _ = up.simulate_local(UNIVERSE, panel, scores, returns, sp, bench)
    detail["variant"] = f"{UNIVERSE}_LOCAL"
    weights["variant"] = f"{UNIVERSE}_LOCAL"
    summary = summarize_one(detail)
    attr = up.engine_attribution(detail)
    smap.to_csv(OUT / "schedule_map.csv", index=False, encoding="utf-8-sig")
    sizes["universe"] = UNIVERSE
    sizes.to_csv(OUT / "universe_sizes.csv", index=False, encoding="utf-8-sig")
    detail.to_csv(OUT / "period_returns.csv", index=False, encoding="utf-8-sig")
    weights.to_csv(OUT / "target_weights.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "strategy_summary.csv", index=False, encoding="utf-8-sig")
    attr.to_csv(OUT / "engine_attribution.csv", index=False, encoding="utf-8-sig")
    print(summary.to_markdown(index=False), flush=True)
    print(attr.to_markdown(index=False), flush=True)


def run_expanded():
    returns, basic_panels = up.base.load_basic()
    returns = returns.loc[:up.END]
    pk, bk, smk = up.build_true_calendar_panel_universe(returns, basic_panels, "K200")
    pa, ba, sma = up.build_true_calendar_panel_universe(returns, basic_panels, "KOSPI_ALL")
    sk, _ = up.score_history_for(pk, returns, "K200")
    sa, _ = up.score_history_for(pa, returns, "KOSPI_ALL")
    signal_dates = sorted(pk.index.get_level_values("date").unique())
    close = up.seqattr.download_kospi200_patched()
    k200 = up.seqattr.forward_index_returns_aligned(close, signal_dates, up.STEP, returns.index)
    cand, _ = up.off.run_all(pk, sk, returns, bk, k200, cost_bps=up.COST_BPS)
    leader = up.seqattr.build_leader_signal(pk, cand)
    control, cw = up.seqattr.simulate_variant("K200_CONTROL", {}, pk, sk, returns, bk, k200, leader)
    control["selection_mode"] = "K200"
    expanded, ew = up.simulate_k200_core_kospi_all(pk, sk, pa, sa, returns, bk, ba, k200, leader)
    detail = pd.concat([control, expanded], ignore_index=True, sort=False)
    weights = pd.concat([cw, ew], ignore_index=True, sort=False)
    summary = summarize_one(detail)
    cmp = up.compare_expanded_to_control(detail)
    rows = []
    for sample in ["train", "test"]:
        z = cmp[cmp["sample"] == sample]
        for engine, g in z.groupby("engine"):
            if len(g) < 2:
                continue
            rows.append({
                "sample": sample,
                "engine": engine,
                "n_periods": int(len(g)),
                "mean_delta_bp": float(g.delta_bp.mean()),
                "median_delta_bp": float(g.delta_bp.median()),
                "hit_rate": float((g.delta_bp > 0).mean()),
                "mean_turnover_delta": float(g.turnover_delta.mean()),
            })
    attr = pd.DataFrame(rows)
    pd.concat([smk, sma], ignore_index=True).to_csv(OUT / "schedule_map.csv", index=False, encoding="utf-8-sig")
    detail.to_csv(OUT / "period_returns.csv", index=False, encoding="utf-8-sig")
    weights.to_csv(OUT / "target_weights.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "strategy_summary.csv", index=False, encoding="utf-8-sig")
    cmp.to_csv(OUT / "period_comparison.csv", index=False, encoding="utf-8-sig")
    attr.to_csv(OUT / "engine_attribution.csv", index=False, encoding="utf-8-sig")
    print(summary.to_markdown(index=False), flush=True)
    print(attr.to_markdown(index=False), flush=True)


if __name__ == "__main__":
    if MODE == "LOCAL":
        run_local()
    elif MODE == "EXPANDED":
        run_expanded()
    else:
        raise KeyError(MODE)
