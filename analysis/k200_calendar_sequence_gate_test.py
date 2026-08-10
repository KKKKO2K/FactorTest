from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "k200_calendar_sequence_gate_results"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("off", HERE / "k200_off_engine_lab.py")
off = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(off)

enh = off.enh
lab = enh.lab
base = enh.base
INDEX_ASSET = off.INDEX_ASSET

START = pd.Timestamp("2017-01-02")
SPLIT = pd.Timestamp("2023-05-26")
END = pd.Timestamp("2026-08-07")
STEP = 10
COST_BPS = 60

VARIANTS = {
    "BASE_CALENDAR": ("base", False),
    "SEQ_ONLY": ("base", True),
    "GATE_MILD": ("mild", False),
    "GATE_FAST": ("fast", False),
    "SEQ_GATE_MILD": ("mild", True),
    "SEQ_GATE_FAST": ("fast", True),
}


def current_engine(state: str, size_state: str, on_signal: bool) -> str:
    if on_signal:
        return "LEADER5_80"
    if size_state != "LARGE_LEAD":
        return "INDEX_ONLY"
    return {
        "BROAD_RISK_ON": "VALUE_REV_30",
        "HIGH_DISPERSION": "REV_BREADTH_70",
        "RISK_OFF": "CONTRARIAN_70",
        "NEUTRAL": "PYRAMID_50",
    }.get(state, "INDEX_ONLY")


def compound(s: pd.Series) -> float:
    x = pd.to_numeric(s, errors="coerce").dropna()
    return float((1.0 + x).prod() - 1.0) if len(x) else np.nan


def build_true_calendar_panel(returns, basic_panels):
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

    original_raw = lab.raw_snapshot
    original_step, original_start, original_end = lab.STEP, lab.START, lab.END

    def raw_scheduled(dt, universe, returns_, _scheduled, factor_cache):
        eff = asof_map[pd.Timestamp(dt)]
        f = original_raw(eff, universe, returns_, basic_panels, factor_cache)
        q = f.reset_index()
        q["date"] = pd.Timestamp(dt)
        return q.set_index(["date", "code"])

    try:
        lab.raw_snapshot = raw_scheduled
        lab.STEP = 1
        lab.START = START
        lab.END = END
        panel = lab.build_panel("K200", returns, scheduled_panels)
    finally:
        lab.raw_snapshot = original_raw
        lab.STEP, lab.START, lab.END = original_step, original_start, original_end

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


def build_gates(panel, candidate_detail):
    d = candidate_detail[candidate_detail.cost_bps == COST_BPS].copy()
    p = d.pivot(index="date", columns="strategy", values="net").sort_index()
    b = d[d.strategy == "INDEX_ONLY"].drop_duplicates("date").set_index("date")["k200_return"].sort_index()
    completed = p.index.intersection(b.index)
    rows = []
    for dt, g0 in panel.groupby(level="date"):
        dt = pd.Timestamp(dt)
        hist = completed[completed < dt]
        rel = pd.Series(dtype=float)
        bench = pd.Series(dtype=float)
        if len(hist):
            leader = p.loc[hist, "LEADER5_80"]
            bench = b.loc[hist]
            rel = (1.0 + leader) / (1.0 + bench) - 1.0
        rel90 = compound(rel.tail(9)) if len(rel) >= 9 else np.nan
        bench30 = compound(bench.tail(3)) if len(bench) >= 3 else np.nan
        if len(rel) >= 12:
            rw = (1.0 + rel).cumprod()
            dd120 = float(rw.iloc[-1] / rw.tail(12).max() - 1.0)
        else:
            dd120 = np.nan
        last1 = float(rel.iloc[-1]) if len(rel) >= 1 else np.nan
        last2 = compound(rel.tail(2)) if len(rel) >= 2 else np.nan
        state = str(g0["state"].iloc[0])
        size_state = str(g0["size_state"].iloc[0])
        eligible = state in {"BROAD_RISK_ON", "NARROW_RISK_ON", "RISK_OFF"}
        base_on = bool(
            eligible
            and pd.notna(rel90) and rel90 > 0.05
            and pd.notna(bench30) and bench30 > 0.0
            and pd.notna(dd120) and dd120 > -0.10
        )
        mild_on = bool(base_on and pd.notna(last2) and last2 > -0.03)
        fast_on = bool(
            base_on
            and pd.notna(last1) and last1 > -0.015
            and pd.notna(last2) and last2 > -0.02
        )
        rows.append({
            "date": dt,
            "state": state,
            "size_state": size_state,
            "leader_relative_90d": rel90,
            "k200_return_30d": bench30,
            "leader_relative_drawdown_120d": dd120,
            "leader_active_last1": last1,
            "leader_active_last2": last2,
            "base_on": base_on,
            "mild_on": mild_on,
            "fast_on": fast_on,
            "base_engine": current_engine(state, size_state, base_on),
            "mild_engine": current_engine(state, size_state, mild_on),
            "fast_engine": current_engine(state, size_state, fast_on),
        })
    return pd.DataFrame(rows).set_index("date").sort_index()


def seq_multiplier(g0):
    g = g0.copy()
    g.index = g.index.get_level_values("code")
    return (
        1.0
        + 0.35 * g["event_flow_revision"].fillna(False).astype(float)
        + 0.50 * g["event_three_stage"].fillna(False).astype(float)
        + 0.35 * g["event_dual_revision"].fillna(False).astype(float)
    )


def apply_sequence(target, g0):
    out = target.copy()
    stocks = out.index[out.index != INDEX_ASSET]
    stock_total = float(out.reindex(stocks).sum())
    mult = seq_multiplier(g0).reindex(stocks).fillna(1.0)
    if stock_total <= 0 or len(stocks) == 0:
        return out, 0.0, 0.0, 0
    seq = mult > 1.0
    pre = float(out.reindex(stocks)[seq].sum())
    adj = out.reindex(stocks).fillna(0.0) * mult
    if adj.sum() > 0:
        out.loc[stocks] = adj / adj.sum() * stock_total
    post = float(out.reindex(stocks)[seq].sum())
    return out[out > 1e-12], pre, post, int(seq.sum())


def turnover(old_end, new):
    idx = old_end.index.union(new.index)
    a = old_end.reindex(idx, fill_value=0.0)
    b = new.reindex(idx, fill_value=0.0)
    old_cash = 1.0 - float(a.sum())
    new_cash = 1.0 - float(b.sum())
    return 0.5 * (float((a - b).abs().sum()) + abs(old_cash - new_cash))


def simulate_variant(name, gate_kind, use_sequence, panel, scores, returns, scheduled_panels, k200_period, gates):
    fwd10 = lab.forward_return(returns, STEP)
    old_end = pd.Series(dtype=float)
    rows, weight_rows = [], []
    for dt, g0 in panel.groupby(level="date"):
        dt = pd.Timestamp(dt)
        if dt not in scores or dt not in k200_period.index or pd.isna(k200_period.loc[dt]) or dt not in fwd10.index:
            continue
        state = str(g0["state"].iloc[0])
        size_state = str(g0["size_state"].iloc[0])
        on_signal = bool(gates.at[dt, f"{gate_kind}_on"])
        engine = current_engine(state, size_state, on_signal)
        target = off.targets_for_date(g0, scores[dt], scheduled_panels[dt])[engine].sort_values(ascending=False)
        pre = post = np.nan
        seq_n = 0
        if use_sequence:
            target, pre, post, seq_n = apply_sequence(target, g0)
        codes = g0.index.get_level_values("code")
        stock_future = fwd10.loc[dt].reindex(codes).fillna(0.0)
        asset_r = stock_future.copy()
        asset_r.loc[INDEX_ASSET] = float(k200_period.loc[dt])
        rr = asset_r.reindex(target.index).fillna(0.0)
        turn = turnover(old_end, target)
        gross = float((target * rr).sum())
        net = gross - turn * COST_BPS / 10000.0
        denom = 1.0 + gross
        old_end = target * (1.0 + rr) / denom if denom > 0 else target.copy()
        old_end = old_end[old_end.abs() > 1e-12]
        sw = target.sort_values(ascending=False)
        rows.append({
            "date": dt,
            "variant": name,
            "state": state,
            "size_state": size_state,
            "on_signal": on_signal,
            "engine": engine,
            "gross": gross,
            "net": net,
            "k200_return": float(k200_period.loc[dt]),
            "active_return": net - float(k200_period.loc[dt]),
            "turnover": turn,
            "top1_weight": float(sw.head(1).sum()),
            "top5_weight": float(sw.head(5).sum()),
            "n_holdings": int((target > 1e-10).sum()),
            "index_weight": float(target.get(INDEX_ASSET, 0.0)),
            "sequence_weight_pre": pre,
            "sequence_weight_post": post,
            "sequence_names": seq_n,
        })
        for asset, w in sw.items():
            weight_rows.append({
                "date": dt,
                "variant": name,
                "engine": engine,
                "asset": asset,
                "weight": float(w),
            })
    return pd.DataFrame(rows), pd.DataFrame(weight_rows)


def metrics(g):
    g = g.sort_values("date").dropna(subset=["net", "k200_return"])
    if len(g) < 5:
        return {}
    periods = 252 / STEP
    years = len(g) / periods
    s, b = g["net"], g["k200_return"]
    active = s - b
    sw = (1.0 + s).cumprod()
    bw = (1.0 + b).cumprod()
    rw = sw / bw
    up, down = b > 0, b < 0
    top = b >= b.quantile(0.90)
    return {
        "n_periods": len(g),
        "strategy_cagr": float(sw.iloc[-1] ** (1 / years) - 1),
        "k200_cagr": float(bw.iloc[-1] ** (1 / years) - 1),
        "relative_cagr": float(rw.iloc[-1] ** (1 / years) - 1),
        "information_ratio": float(active.mean() / active.std(ddof=1) * math.sqrt(periods)) if active.std(ddof=1) > 0 else np.nan,
        "tracking_error": float(active.std(ddof=1) * math.sqrt(periods)),
        "strategy_mdd": float((sw / sw.cummax() - 1).min()),
        "relative_mdd": float((rw / rw.cummax() - 1).min()),
        "up_capture": float(s[up].mean() / b[up].mean()) if up.any() and b[up].mean() != 0 else np.nan,
        "down_capture": float(s[down].mean() / b[down].mean()) if down.any() and b[down].mean() != 0 else np.nan,
        "top_decile_capture": float(s[top].mean() / b[top].mean()) if top.any() and b[top].mean() != 0 else np.nan,
        "annual_turnover": float(g["turnover"].mean() * periods),
        "avg_top1_weight": float(g["top1_weight"].mean()),
        "avg_top5_weight": float(g["top5_weight"].mean()),
        "leader_on_rate": float(g["on_signal"].mean()),
    }


def summarize(detail):
    rows = []
    for variant, g0 in detail.groupby("variant"):
        for sample, lo, hi in (("train", START, SPLIT), ("test", SPLIT, END + pd.Timedelta(days=1))):
            m = metrics(g0[(g0.date >= lo) & (g0.date < hi)].copy())
            if m:
                rows.append({"variant": variant, "sample": sample, **m})
    return pd.DataFrame(rows)


def partial_returns(returns, dt, codes):
    h = returns.loc[(returns.index > dt) & (returns.index <= END), returns.columns.intersection(codes)]
    out = pd.Series(0.0, index=codes)
    if not h.empty:
        out.loc[h.columns] = (1.0 + h.fillna(0.0)).prod(axis=0) - 1.0
    return out


def index_close_return(close, start, end):
    s = close.index.searchsorted(start, side="right") - 1
    e = close.index.searchsorted(end, side="right") - 1
    if s < 0 or e < 0:
        return np.nan
    return float(close.iloc[e] / close.iloc[s] - 1.0)


def current_targets_and_partial(panel, scores, returns, scheduled_panels, gates, k200_close):
    dt = max(panel.index.get_level_values("date"))
    g0 = panel.xs(dt, level="date", drop_level=False)
    codes = g0.index.get_level_values("code")
    stock_r = partial_returns(returns, dt, codes)
    k200_r = index_close_return(k200_close, dt, END)
    rows, weights = [], []
    for variant, (gate_kind, use_sequence) in VARIANTS.items():
        state = str(g0["state"].iloc[0])
        size_state = str(g0["size_state"].iloc[0])
        on_signal = bool(gates.at[dt, f"{gate_kind}_on"])
        engine = current_engine(state, size_state, on_signal)
        target = off.targets_for_date(g0, scores[dt], scheduled_panels[dt])[engine].sort_values(ascending=False)
        pre = post = np.nan
        seq_n = 0
        if use_sequence:
            target, pre, post, seq_n = apply_sequence(target, g0)
        ar = stock_r.copy()
        ar.loc[INDEX_ASSET] = k200_r
        gross = float((target * ar.reindex(target.index).fillna(0.0)).sum())
        rows.append({
            "variant": variant,
            "signal_date": dt,
            "end_date": END,
            "state": state,
            "size_state": size_state,
            "on_signal": on_signal,
            "engine": engine,
            "gross_partial": gross,
            "k200_partial": k200_r,
            "gross_active_partial": gross - k200_r,
            "sequence_weight_pre": pre,
            "sequence_weight_post": post,
            "sequence_names": seq_n,
        })
        mult = seq_multiplier(g0)
        for asset, w in target.sort_values(ascending=False).items():
            weights.append({
                "variant": variant,
                "signal_date": dt,
                "engine": engine,
                "asset": asset,
                "weight": float(w),
                "sequence_multiplier": float(mult.get(asset, 1.0)) if asset != INDEX_ASSET else np.nan,
            })
    return pd.DataFrame(rows), pd.DataFrame(weights)


def main():
    returns, basic_panels = base.load_basic()
    returns = returns.loc[:END]
    panel, scheduled_panels, schedule_map = build_true_calendar_panel(returns, basic_panels)

    fwd20 = lab.forward_return(returns, lab.HORIZON)
    ic = lab.ic_detail(panel, fwd20, "K200")
    static, mapping, _ = lab.factor_maps(ic, "K200")
    scores, selections = lab.score_history(panel, ic, "K200", static, mapping)

    signal_dates = sorted(panel.index.get_level_values("date").unique())
    k200_close = enh.download_kospi200()
    k200_period = enh.forward_index_returns(k200_close, signal_dates, STEP)

    candidate_detail, candidate_weights = off.run_all(
        panel, scores, returns, scheduled_panels, k200_period, cost_bps=COST_BPS
    )
    gates = build_gates(panel, candidate_detail)

    detail_frames, weight_frames = [], []
    for variant, (gate_kind, use_sequence) in VARIANTS.items():
        d, w = simulate_variant(
            variant, gate_kind, use_sequence, panel, scores, returns,
            scheduled_panels, k200_period, gates
        )
        detail_frames.append(d)
        weight_frames.append(w)
    detail = pd.concat(detail_frames, ignore_index=True)
    weights = pd.concat(weight_frames, ignore_index=True)
    summary = summarize(detail)
    partial, current_weights = current_targets_and_partial(
        panel, scores, returns, scheduled_panels, gates, k200_close
    )

    completed_dates = sorted(detail.date.unique())
    recent_dt = pd.Timestamp("2026-07-22")
    if recent_dt not in completed_dates and completed_dates:
        recent_dt = completed_dates[-1]
    recent = detail[detail.date == recent_dt].copy()

    test = summary[summary.sample == "test"].sort_values(
        ["relative_cagr", "information_ratio"], ascending=False
    )

    schedule_map.to_csv(OUT / "true_calendar_schedule_map.csv", index=False, encoding="utf-8-sig")
    gates.reset_index().to_csv(OUT / "gate_diagnostics.csv", index=False, encoding="utf-8-sig")
    candidate_detail.to_csv(OUT / "candidate_component_returns.csv", index=False, encoding="utf-8-sig")
    candidate_weights.to_csv(OUT / "candidate_component_weights.csv", index=False, encoding="utf-8-sig")
    detail.to_csv(OUT / "variant_period_returns.csv", index=False, encoding="utf-8-sig")
    weights.to_csv(OUT / "variant_target_weights.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "variant_summary.csv", index=False, encoding="utf-8-sig")
    recent.to_csv(OUT / "recent_completed_period.csv", index=False, encoding="utf-8-sig")
    partial.to_csv(OUT / "current_partial_to_aug7.csv", index=False, encoding="utf-8-sig")
    current_weights.to_csv(OUT / "current_targets.csv", index=False, encoding="utf-8-sig")
    selections.to_csv(OUT / "factor_selection_history.csv", index=False, encoding="utf-8-sig")

    report = (
        "# K200 True Calendar + Sequence + Deterioration Gate\n\n"
        "Schedule is anchored to every 10th trading day in the returns calendar. "
        "If a factor/basic snapshot is not available on that date, the latest prior snapshot is used and logged. "
        "All performance uses 60bp one-way turnover cost and actual KOSPI200 price-index returns (^KS200).\n\n"
        "## OOS summary\n\n" + test.to_markdown(index=False) +
        "\n\n## Latest schedule mapping\n\n" + schedule_map.tail(10).to_markdown(index=False) +
        "\n\n## Latest gate diagnostics\n\n" + gates.tail(10).reset_index().to_markdown(index=False) +
        "\n\n## Recent completed period\n\n" + recent.to_markdown(index=False) +
        "\n\n## Current partial through 2026-08-07\n\n" + partial.to_markdown(index=False)
    )
    (OUT / "summary.md").write_text(report, encoding="utf-8")

    print("=== TRUE CALENDAR LAST DATES ===")
    print(schedule_map.tail(10).to_string(index=False))
    print("\n=== OOS SUMMARY ===")
    print(test.to_string(index=False))
    print("\n=== RECENT COMPLETED PERIOD ===")
    print(recent.to_string(index=False))
    print("\n=== CURRENT PARTIAL ===")
    print(partial.to_string(index=False))
    print("\n=== CURRENT TARGET TOP 8 ===")
    print(current_weights.sort_values(["variant", "weight"], ascending=[True, False]).groupby("variant").head(8).to_string(index=False))


if __name__ == "__main__":
    main()
