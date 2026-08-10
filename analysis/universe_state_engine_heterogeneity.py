from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

import k200_universe_portability as up

OUT = Path(__file__).resolve().parent / "universe_state_engine_heterogeneity_results"
OUT.mkdir(parents=True, exist_ok=True)

lab = up.lab
base = up.base
off = up.off
START, SPLIT, END, STEP = up.START, up.SPLIT, up.END, up.STEP
COST_BPS = up.COST_BPS

UNIVERSES = ["K200", "KOSPI_EX_K200", "KOSDAQ"]
ENGINE_FAMILIES = [
    "VALUE_REV", "REV_BREADTH", "ABSORPTION", "LOWVOL_VALUE", "QUALITY_TREND",
    "QUIET_ACCUM", "CONTRARIAN", "BALANCED", "EVENT_META",
]
CANDIDATES = [f"{x}_50" for x in ENGINE_FAMILIES] + ["INDEX_ONLY"]
MIN_STATE_TRAIN = 8
MIN_HALF_STATE_TRAIN = 4
BOOT_N = 5000
BOOT_BLOCK = 3
SEED = 42

ECONOMIC_THESIS = {
    "VALUE_REV_50": "cheap valuation + earnings revision + value unlock + private flow",
    "REV_BREADTH_50": "revision breadth + long momentum + private flow",
    "ABSORPTION_50": "ownership transfer + short reversal + value unlock + low volatility",
    "LOWVOL_VALUE_50": "defensive low-volatility + value + revision + reversal",
    "QUALITY_TREND_50": "revision quality/breadth + trend + low volatility",
    "QUIET_ACCUM_50": "neglected value + private accumulation + quiet price",
    "CONTRARIAN_50": "value + short reversal + private flow + revision",
    "BALANCED_50": "diversified value/revision/flow/reversal/low-vol/meta",
    "EVENT_META_50": "event/meta signal + value unlock + low volatility",
    "INDEX_ONLY": "no stock-selection alpha",
}


def ir_score(x: pd.Series) -> float:
    x = pd.to_numeric(x, errors="coerce").dropna()
    if len(x) < 2:
        return -np.inf
    sd = float(x.std(ddof=1))
    if sd <= 0:
        return float(x.mean()) * 1e6
    return float(x.mean() / sd)


def choose_engine(g: pd.DataFrame, min_n: int) -> tuple[str, float, int]:
    best_engine = "INDEX_ONLY"
    best_score = -np.inf
    best_n = 0
    for engine in CANDIDATES:
        q = g[g["engine"] == engine]
        if len(q) < min_n:
            continue
        score = ir_score(q["active_return"])
        if score > best_score:
            best_engine, best_score, best_n = engine, score, int(len(q))
    return best_engine, best_score, best_n


def learn_state_map(matrix: pd.DataFrame, universe: str | None = None, pooled: bool = False,
                    lo: pd.Timestamp = START, hi: pd.Timestamp = SPLIT,
                    min_n: int = MIN_STATE_TRAIN) -> tuple[dict[str, str], pd.DataFrame]:
    q = matrix[(matrix["date"] >= lo) & (matrix["date"] < hi)].copy()
    if universe is not None:
        q = q[q["universe"] == universe]
    rows = []
    mapping: dict[str, str] = {}
    for st, g in q.groupby("common_state"):
        engine, score, n = choose_engine(g, min_n)
        mapping[str(st)] = engine
        rows.append({
            "scope": "POOLED" if pooled else str(universe),
            "state": str(st), "engine": engine, "train_score_mean_over_sd": score,
            "n_state_engine_obs": n, "window_start": lo, "window_end": hi,
            "economic_thesis": ECONOMIC_THESIS.get(engine, ""),
        })
    return mapping, pd.DataFrame(rows)


def learn_best_engine(matrix: pd.DataFrame, universe: str | None = None, pooled: bool = False,
                      lo: pd.Timestamp = START, hi: pd.Timestamp = SPLIT) -> tuple[str, pd.DataFrame]:
    q = matrix[(matrix["date"] >= lo) & (matrix["date"] < hi)].copy()
    if universe is not None:
        q = q[q["universe"] == universe]
    engine, score, n = choose_engine(q.assign(common_state="ALL"), 20)
    row = pd.DataFrame([{
        "scope": "POOLED" if pooled else str(universe), "engine": engine,
        "train_score_mean_over_sd": score, "n_engine_obs": n,
        "economic_thesis": ECONOMIC_THESIS.get(engine, ""),
    }])
    return engine, row


def apply_model(matrix: pd.DataFrame, universe: str, model: str,
                state_map: dict[str, str] | None = None, best_engine: str | None = None) -> pd.DataFrame:
    q = matrix[matrix["universe"] == universe].copy()
    if state_map is not None:
        q["choice"] = q["common_state"].map(state_map).fillna("INDEX_ONLY")
    else:
        q["choice"] = best_engine or "INDEX_ONLY"
    picked = q[q["engine"] == q["choice"]].copy()
    picked["model"] = model
    return picked[["date", "universe", "common_state", "model", "choice", "net", "benchmark_return", "active_return", "turnover"]]


def perf(g: pd.DataFrame) -> dict[str, float]:
    q = g.sort_values("date").dropna(subset=["net", "benchmark_return"])
    if len(q) < 5:
        return {}
    periods = 252 / STEP
    years = len(q) / periods
    sw = (1.0 + q["net"]).cumprod()
    bw = (1.0 + q["benchmark_return"]).cumprod()
    rw = sw / bw
    active = (1.0 + q["net"]) / (1.0 + q["benchmark_return"]) - 1.0
    sd = float(active.std(ddof=1))
    return {
        "n_periods": int(len(q)),
        "strategy_cagr": float(sw.iloc[-1] ** (1.0 / years) - 1.0),
        "benchmark_cagr": float(bw.iloc[-1] ** (1.0 / years) - 1.0),
        "relative_cagr": float(rw.iloc[-1] ** (1.0 / years) - 1.0),
        "information_ratio": float(active.mean() / sd * math.sqrt(periods)) if sd > 0 else np.nan,
        "relative_mdd": float((rw / rw.cummax() - 1.0).min()),
        "mean_active_bp": float(active.mean() * 10000),
        "hit_rate": float((active > 0).mean()),
        "annual_turnover": float(q["turnover"].mean() * periods),
    }


def block_bootstrap_ci(delta: pd.Series, n_boot: int = BOOT_N, block: int = BOOT_BLOCK) -> dict[str, float]:
    x = pd.to_numeric(delta, errors="coerce").dropna().to_numpy()
    n = len(x)
    if n < 8:
        return {"mean_bp": np.nan, "ci_low_bp": np.nan, "ci_high_bp": np.nan, "prob_positive": np.nan}
    rng = np.random.default_rng(SEED)
    starts = np.arange(n)
    vals = np.empty(n_boot)
    n_blocks = int(np.ceil(n / block))
    for b in range(n_boot):
        pieces = []
        for _ in range(n_blocks):
            s = int(rng.choice(starts))
            idx = (np.arange(s, s + block) % n).astype(int)
            pieces.append(x[idx])
        sample = np.concatenate(pieces)[:n]
        vals[b] = sample.mean()
    return {
        "mean_bp": float(x.mean() * 10000),
        "ci_low_bp": float(np.quantile(vals, 0.025) * 10000),
        "ci_high_bp": float(np.quantile(vals, 0.975) * 10000),
        "prob_positive": float((vals > 0).mean()),
    }


def robust_delta(specific: pd.DataFrame, common: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for universe in UNIVERSES:
        a = specific[(specific.universe == universe) & (specific.date >= SPLIT)].set_index("date")
        b = common[(common.universe == universe) & (common.date >= SPLIT)].set_index("date")
        dates = a.index.intersection(b.index)
        d = (a.loc[dates, "net"] - b.loc[dates, "net"]).sort_values()
        boot = block_bootstrap_ci(d)
        desc = {
            "universe": universe, "n_periods": int(len(d)), **boot,
            "best1_removed_mean_bp": float(d.iloc[:-1].mean() * 10000) if len(d) > 1 else np.nan,
            "best2_removed_mean_bp": float(d.iloc[:-2].mean() * 10000) if len(d) > 2 else np.nan,
            "worst1_removed_mean_bp": float(d.iloc[1:].mean() * 10000) if len(d) > 1 else np.nan,
        }
        rows.append(desc)
    # pooled equally across all universe-date observations
    a = specific[specific.date >= SPLIT].set_index(["date", "universe"])
    b = common[common.date >= SPLIT].set_index(["date", "universe"])
    ix = a.index.intersection(b.index)
    d = (a.loc[ix, "net"] - b.loc[ix, "net"]).sort_values()
    boot = block_bootstrap_ci(d)
    rows.append({
        "universe": "POOLED", "n_periods": int(len(d)), **boot,
        "best1_removed_mean_bp": float(d.iloc[:-1].mean() * 10000) if len(d) > 1 else np.nan,
        "best2_removed_mean_bp": float(d.iloc[:-2].mean() * 10000) if len(d) > 2 else np.nan,
        "worst1_removed_mean_bp": float(d.iloc[1:].mean() * 10000) if len(d) > 1 else np.nan,
    })
    return pd.DataFrame(rows)


def mapping_stability(matrix: pd.DataFrame) -> pd.DataFrame:
    mid = START + (SPLIT - START) / 2
    rows = []
    for universe in UNIVERSES:
        full, _ = learn_state_map(matrix, universe=universe)
        early, _ = learn_state_map(matrix, universe=universe, lo=START, hi=mid, min_n=MIN_HALF_STATE_TRAIN)
        late, _ = learn_state_map(matrix, universe=universe, lo=mid, hi=SPLIT, min_n=MIN_HALF_STATE_TRAIN)
        states = sorted(set(full) | set(early) | set(late))
        for st in states:
            rows.append({
                "universe": universe, "state": st,
                "full_train_engine": full.get(st, "INDEX_ONLY"),
                "early_train_engine": early.get(st, "INDEX_ONLY"),
                "late_train_engine": late.get(st, "INDEX_ONLY"),
                "early_late_match": early.get(st, "INDEX_ONLY") == late.get(st, "INDEX_ONLY"),
                "full_matches_early": full.get(st, "INDEX_ONLY") == early.get(st, "INDEX_ONLY"),
                "full_matches_late": full.get(st, "INDEX_ONLY") == late.get(st, "INDEX_ONLY"),
            })
    return pd.DataFrame(rows)


def cell_robustness(matrix: pd.DataFrame, specific_maps: dict[str, dict[str, str]]) -> pd.DataFrame:
    rows = []
    for universe in UNIVERSES:
        q = matrix[(matrix.universe == universe) & (matrix.date >= SPLIT)]
        for st, engine in specific_maps[universe].items():
            z = q[(q.common_state == st) & (q.engine == engine)].copy()
            x = z["active_return"].dropna().sort_values()
            if len(x) == 0:
                continue
            rows.append({
                "universe": universe, "state": st, "chosen_engine": engine,
                "economic_thesis": ECONOMIC_THESIS.get(engine, ""),
                "oos_n": int(len(x)), "oos_mean_active_bp": float(x.mean() * 10000),
                "oos_median_active_bp": float(x.median() * 10000),
                "oos_hit_rate": float((x > 0).mean()),
                "oos_best1_removed_bp": float(x.iloc[:-1].mean() * 10000) if len(x) > 1 else np.nan,
                "oos_sign_positive": bool(x.mean() > 0),
            })
    return pd.DataFrame(rows)


def transfer_table(matrix: pd.DataFrame, specific_maps: dict[str, dict[str, str]]) -> pd.DataFrame:
    rows = []
    oos = matrix[matrix.date >= SPLIT]
    for source_u in UNIVERSES:
        for st, engine in specific_maps[source_u].items():
            for target_u in UNIVERSES:
                z = oos[(oos.universe == target_u) & (oos.common_state == st) & (oos.engine == engine)]
                if len(z) == 0:
                    continue
                rows.append({
                    "source_universe": source_u, "state": st, "selected_engine": engine,
                    "target_universe": target_u, "n": int(len(z)),
                    "mean_active_bp": float(z.active_return.mean() * 10000),
                    "hit_rate": float((z.active_return > 0).mean()),
                })
    return pd.DataFrame(rows)


def expanding_walk_forward(matrix: pd.DataFrame, mode: str) -> pd.DataFrame:
    dates = sorted(pd.Timestamp(x) for x in matrix.date.unique())
    rows = []
    for dt in dates:
        if dt < SPLIT:
            continue
        hist = matrix[matrix.date < dt]
        if mode == "POOLED_COMMON":
            mp, _ = learn_state_map(hist, universe=None, pooled=True, lo=START, hi=dt)
            maps = {u: mp for u in UNIVERSES}
        elif mode == "UNIVERSE_SPECIFIC":
            maps = {u: learn_state_map(hist, universe=u, lo=START, hi=dt)[0] for u in UNIVERSES}
        else:
            raise KeyError(mode)
        today = matrix[matrix.date == dt]
        for u in UNIVERSES:
            z = today[today.universe == u]
            if z.empty:
                continue
            st = str(z.common_state.iloc[0])
            choice = maps[u].get(st, "INDEX_ONLY")
            p = z[z.engine == choice]
            if p.empty:
                continue
            r = p.iloc[0]
            rows.append({
                "date": dt, "universe": u, "common_state": st, "mode": mode,
                "choice": choice, "net": float(r.net), "benchmark_return": float(r.benchmark_return),
                "active_return": float(r.active_return), "turnover": float(r.turnover),
            })
    return pd.DataFrame(rows)


def main() -> None:
    returns, basic_panels = base.load_basic()
    returns = returns.loc[:END]

    panels: dict[str, pd.DataFrame] = {}
    scheduled: dict[str, dict] = {}
    scores: dict[str, dict] = {}
    benchmarks: dict[str, pd.Series] = {}
    schedule_maps = []

    for universe in UNIVERSES:
        print(f"BUILD {universe}", flush=True)
        panel, sp, smap = up.build_true_calendar_panel_universe(returns, basic_panels, universe)
        panels[universe] = panel
        scheduled[universe] = sp
        scores[universe], _ = up.score_history_for(panel, returns, universe)
        bench, _ = up.synthetic_cap_benchmark(panel, sp, returns)
        benchmarks[universe] = bench
        schedule_maps.append(smap)

    # Common state is frozen to K200 state labels for every universe/date.
    k200_state = panels["K200"].groupby(level="date")["state"].first().astype(str)
    matrix_rows = []
    for universe in UNIVERSES:
        print(f"ENGINE MATRIX {universe}", flush=True)
        detail, _ = off.run_all(
            panels[universe], scores[universe], returns, scheduled[universe],
            benchmarks[universe], cost_bps=COST_BPS,
        )
        d = detail[detail.strategy.isin(CANDIDATES)].copy()
        d["universe"] = universe
        d["engine"] = d["strategy"]
        d["benchmark_return"] = d["k200_return"]
        d["common_state"] = d["date"].map(k200_state)
        d["active_return"] = (1.0 + d["net"]) / (1.0 + d["benchmark_return"]) - 1.0
        matrix_rows.append(d[[
            "date", "universe", "common_state", "engine", "net", "benchmark_return",
            "active_return", "turnover", "stock_weight", "index_weight",
        ]])
    matrix = pd.concat(matrix_rows, ignore_index=True)

    # Frozen train mappings.
    pooled_map, pooled_map_df = learn_state_map(matrix, pooled=True)
    k200_map, k200_map_df = learn_state_map(matrix, universe="K200")
    specific_maps: dict[str, dict[str, str]] = {}
    map_frames = [pooled_map_df.assign(model="POOLED_COMMON"), k200_map_df.assign(model="K200_COMMON")]
    for u in UNIVERSES:
        mp, df = learn_state_map(matrix, universe=u)
        specific_maps[u] = mp
        map_frames.append(df.assign(model="UNIVERSE_SPECIFIC"))

    pooled_best, pooled_best_df = learn_best_engine(matrix, pooled=True)
    best_by_u = {}
    best_frames = [pooled_best_df.assign(model="POOLED_BEST_ENGINE")]
    for u in UNIVERSES:
        be, df = learn_best_engine(matrix, universe=u)
        best_by_u[u] = be
        best_frames.append(df.assign(model="UNIVERSE_BEST_ENGINE"))

    model_parts = []
    for u in UNIVERSES:
        model_parts += [
            apply_model(matrix, u, "POOLED_COMMON_STATE_MAP", state_map=pooled_map),
            apply_model(matrix, u, "K200_COMMON_STATE_MAP", state_map=k200_map),
            apply_model(matrix, u, "UNIVERSE_SPECIFIC_STATE_MAP", state_map=specific_maps[u]),
            apply_model(matrix, u, "POOLED_BEST_ENGINE", best_engine=pooled_best),
            apply_model(matrix, u, "UNIVERSE_BEST_ENGINE", best_engine=best_by_u[u]),
        ]
    models = pd.concat(model_parts, ignore_index=True)

    summary_rows = []
    for (model, u), g in models.groupby(["model", "universe"]):
        for sample, lo, hi in (("train", START, SPLIT), ("test", SPLIT, END + pd.Timedelta(days=1))):
            z = g[(g.date >= lo) & (g.date < hi)]
            m = perf(z)
            if m:
                summary_rows.append({"model": model, "universe": u, "sample": sample, **m})
    summary = pd.DataFrame(summary_rows)

    specific = models[models.model == "UNIVERSE_SPECIFIC_STATE_MAP"]
    pooled_common = models[models.model == "POOLED_COMMON_STATE_MAP"]
    delta_robust = robust_delta(specific, pooled_common)
    stability = mapping_stability(matrix)
    cell_rob = cell_robustness(matrix, specific_maps)
    transfer = transfer_table(matrix, specific_maps)

    wf_common = expanding_walk_forward(matrix, "POOLED_COMMON")
    wf_specific = expanding_walk_forward(matrix, "UNIVERSE_SPECIFIC")
    wf = pd.concat([wf_common, wf_specific], ignore_index=True)
    wf_rows = []
    for (mode, u), g in wf.groupby(["mode", "universe"]):
        m = perf(g)
        if m:
            wf_rows.append({"mode": mode, "universe": u, **m})
    wf_summary = pd.DataFrame(wf_rows)

    # State x engine train/OOS matrix for transparent inspection.
    sx_rows = []
    for (u, st, engine), g in matrix.groupby(["universe", "common_state", "engine"]):
        for sample, lo, hi in (("train", START, SPLIT), ("test", SPLIT, END + pd.Timedelta(days=1))):
            z = g[(g.date >= lo) & (g.date < hi)]
            if len(z) == 0:
                continue
            sx_rows.append({
                "universe": u, "state": st, "engine": engine, "sample": sample,
                "n": int(len(z)), "mean_active_bp": float(z.active_return.mean() * 10000),
                "median_active_bp": float(z.active_return.median() * 10000),
                "hit_rate": float((z.active_return > 0).mean()),
                "score_mean_over_sd": ir_score(z.active_return),
            })
    state_engine = pd.DataFrame(sx_rows)

    pd.concat(schedule_maps, ignore_index=True).to_csv(OUT / "schedule_map.csv", index=False, encoding="utf-8-sig")
    matrix.to_csv(OUT / "engine_return_matrix.csv", index=False, encoding="utf-8-sig")
    state_engine.to_csv(OUT / "state_engine_matrix.csv", index=False, encoding="utf-8-sig")
    pd.concat(map_frames, ignore_index=True).to_csv(OUT / "frozen_train_mappings.csv", index=False, encoding="utf-8-sig")
    pd.concat(best_frames, ignore_index=True).to_csv(OUT / "frozen_best_engines.csv", index=False, encoding="utf-8-sig")
    models.to_csv(OUT / "model_period_returns.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "model_summary.csv", index=False, encoding="utf-8-sig")
    delta_robust.to_csv(OUT / "specific_vs_common_robustness.csv", index=False, encoding="utf-8-sig")
    stability.to_csv(OUT / "mapping_stability.csv", index=False, encoding="utf-8-sig")
    cell_rob.to_csv(OUT / "chosen_cell_robustness.csv", index=False, encoding="utf-8-sig")
    transfer.to_csv(OUT / "cross_universe_transfer.csv", index=False, encoding="utf-8-sig")
    wf.to_csv(OUT / "expanding_walkforward_returns.csv", index=False, encoding="utf-8-sig")
    wf_summary.to_csv(OUT / "expanding_walkforward_summary.csv", index=False, encoding="utf-8-sig")

    # Compact markdown summary.
    lines = [
        "# Universe × State × Engine Heterogeneity v1",
        "",
        "## Frozen design",
        "- Common regime labels: K200 state on each true 10D signal date.",
        "- Universes: K200, KOSPI ex-K200, KOSDAQ.",
        "- Engine families: 9 pre-existing composite engines; every candidate fixed at 50% stock / 50% local benchmark.",
        "- Mapping learned on train only and frozen for OOS.",
        "- Compare pooled common mapping, K200 common mapping, universe-specific mapping, and no-state best-engine controls.",
        "- Diagnostics: early/late-train mapping stability, chosen-cell OOS robustness, cross-universe transfer, expanding walk-forward, block-bootstrap specific-vs-common delta.",
        "",
        "## Model summary",
        summary.to_markdown(index=False),
        "",
        "## Frozen train mappings",
        pd.concat(map_frames, ignore_index=True).to_markdown(index=False),
        "",
        "## Universe-specific vs pooled-common robustness",
        delta_robust.to_markdown(index=False),
        "",
        "## Expanding walk-forward",
        wf_summary.to_markdown(index=False),
    ]
    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(summary.to_string(index=False), flush=True)
    print("\nROBUSTNESS\n", delta_robust.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
