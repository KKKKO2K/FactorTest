from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
OUT = HERE / "k200_sequence_attribution_results"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location(
    "seqbase", HERE / "k200_calendar_sequence_gate_test.py"
)
seqbase = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(seqbase)

off = seqbase.off
enh = seqbase.enh
lab = seqbase.lab
base = seqbase.base
INDEX_ASSET = seqbase.INDEX_ASSET

START = pd.Timestamp("2017-01-02")
SPLIT = pd.Timestamp("2023-05-26")
END = pd.Timestamp("2026-08-07")
STEP = 10
COST_BPS = 60

EVENT_SPECS = {
    "FLOW": ("event_flow_revision", 0.35),
    "THREE": ("event_three_stage", 0.50),
    "DUAL": ("event_dual_revision", 0.35),
}

STRUCTURE_VARIANTS = {
    "BASE": {},
    "FLOW_ONLY": {"FLOW": 0.35},
    "THREE_ONLY": {"THREE": 0.50},
    "DUAL_ONLY": {"DUAL": 0.35},
    "FLOW_THREE": {"FLOW": 0.35, "THREE": 0.50},
    "FLOW_DUAL": {"FLOW": 0.35, "DUAL": 0.35},
    "THREE_DUAL": {"THREE": 0.50, "DUAL": 0.35},
    "ALL_CURRENT": {"FLOW": 0.35, "THREE": 0.50, "DUAL": 0.35},
}

SCALE_VARIANTS = {
    "ALL_X050": 0.50,
    "ALL_X075": 0.75,
    "ALL_X125": 1.25,
    "ALL_X150": 1.50,
}

VARIANTS = dict(STRUCTURE_VARIANTS)
for name, scale in SCALE_VARIANTS.items():
    VARIANTS[name] = {
        key: coef * scale for key, (_, coef) in EVENT_SPECS.items()
    }


def compound(s: pd.Series) -> float:
    x = pd.to_numeric(s, errors="coerce").dropna()
    return float((1.0 + x).prod() - 1.0) if len(x) else np.nan


def current_engine(state: str, size_state: str, leader_on: bool) -> str:
    if leader_on:
        return "LEADER5_80"
    if size_state != "LARGE_LEAD":
        return "INDEX_ONLY"
    return {
        "BROAD_RISK_ON": "VALUE_REV_30",
        "HIGH_DISPERSION": "REV_BREADTH_70",
        "RISK_OFF": "CONTRARIAN_70",
        "NEUTRAL": "PYRAMID_50",
    }.get(state, "INDEX_ONLY")


def _num(x):
    if x is None or x == "":
        return np.nan
    return float(str(x).replace(",", ""))


def _fetch_naver_recent() -> pd.Series:
    frames = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for page in (1, 2):
        url = f"https://m.stock.naver.com/api/index/KPI200/price?pageSize=60&page={page}"
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        f = pd.DataFrame(r.json())
        if f.empty:
            continue
        f["date"] = pd.to_datetime(f["localTradedAt"])
        f["naver_close"] = f["closePrice"].map(_num)
        frames.append(f[["date", "naver_close"]])
    if not frames:
        raise RuntimeError("Naver KOSPI200 response was empty")
    f = pd.concat(frames, ignore_index=True).drop_duplicates("date", keep="first")
    naver = f.set_index("date")["naver_close"].dropna().sort_index()
    naver.index = pd.to_datetime(naver.index).tz_localize(None)
    return naver


def download_kospi200_patched() -> pd.Series:
    yahoo = enh.download_kospi200().copy()
    yahoo.index = pd.to_datetime(yahoo.index).tz_localize(None)
    yahoo = pd.to_numeric(yahoo, errors="coerce").dropna().sort_index()
    naver = _fetch_naver_recent()

    patched = pd.concat(
        [yahoo.rename("yahoo_close"), naver.rename("naver_close")], axis=1
    )
    patched["patched_close"] = patched["naver_close"].combine_first(
        patched["yahoo_close"]
    )
    patched["source"] = np.where(
        patched["naver_close"].notna(), "NAVER", "YAHOO"
    )
    overlap = patched[
        patched["yahoo_close"].notna() & patched["naver_close"].notna()
    ].copy()
    overlap["pct_diff"] = (
        overlap["naver_close"] / overlap["yahoo_close"] - 1.0
    )

    audit = patched.loc[patched.index >= pd.Timestamp("2026-04-01")].copy()
    audit.index.name = "date"
    audit.to_csv(
        OUT / "k200_benchmark_patch_audit.csv",
        encoding="utf-8-sig",
    )
    overlap.loc[overlap.index >= pd.Timestamp("2026-04-01")].to_csv(
        OUT / "k200_benchmark_overlap_check.csv",
        encoding="utf-8-sig",
    )
    return patched["patched_close"].dropna().sort_index().rename("k200_close")


def forward_index_returns_aligned(
    close: pd.Series,
    signal_dates,
    horizon: int,
    stock_calendar,
) -> pd.Series:
    stock_idx = pd.DatetimeIndex(stock_calendar).sort_values()
    close = close.sort_index()
    rows = []
    for dt0 in signal_dates:
        dt = pd.Timestamp(dt0)
        pos = stock_idx.searchsorted(dt, side="left")
        if (
            pos >= len(stock_idx)
            or stock_idx[pos] != dt
            or pos + horizon >= len(stock_idx)
        ):
            rows.append(
                {"date": dt, "end_date": pd.NaT, "k200_return": np.nan}
            )
            continue
        end_dt = pd.Timestamp(stock_idx[pos + horizon])
        if dt not in close.index or end_dt not in close.index:
            rows.append(
                {"date": dt, "end_date": end_dt, "k200_return": np.nan}
            )
            continue
        rows.append(
            {
                "date": dt,
                "end_date": end_dt,
                "k200_return": float(close.loc[end_dt] / close.loc[dt] - 1.0),
            }
        )
    audit = pd.DataFrame(rows)
    audit.to_csv(
        OUT / "k200_aligned_period_returns.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return audit.set_index("date")["k200_return"]


def build_leader_signal(panel, candidate_detail) -> pd.DataFrame:
    """Preserve the pre-existing leader activation rule; no deterioration gates."""
    d = candidate_detail[candidate_detail.cost_bps == COST_BPS].copy()
    p = d.pivot(index="date", columns="strategy", values="net").sort_index()
    b = (
        d[d.strategy == "INDEX_ONLY"]
        .drop_duplicates("date")
        .set_index("date")["k200_return"]
        .sort_index()
    )
    completed = p.index.intersection(b.index)

    rows = []
    for dt0, g0 in panel.groupby(level="date"):
        dt = pd.Timestamp(dt0)
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

        state = str(g0["state"].iloc[0])
        size_state = str(g0["size_state"].iloc[0])
        eligible = state in {"BROAD_RISK_ON", "NARROW_RISK_ON", "RISK_OFF"}
        leader_on = bool(
            eligible
            and pd.notna(rel90)
            and rel90 > 0.05
            and pd.notna(bench30)
            and bench30 > 0.0
            and pd.notna(dd120)
            and dd120 > -0.10
        )
        rows.append(
            {
                "date": dt,
                "state": state,
                "size_state": size_state,
                "leader_relative_90d": rel90,
                "k200_return_30d": bench30,
                "leader_relative_drawdown_120d": dd120,
                "leader_on": leader_on,
                "engine": current_engine(state, size_state, leader_on),
            }
        )
    return pd.DataFrame(rows).set_index("date").sort_index()


def sequence_multiplier(g0: pd.DataFrame, coefs: dict[str, float]) -> pd.Series:
    g = g0.copy()
    g.index = g.index.get_level_values("code")
    mult = pd.Series(1.0, index=g.index, dtype=float)
    for key, coef in coefs.items():
        flag_col = EVENT_SPECS[key][0]
        mult = mult + coef * g[flag_col].fillna(False).astype(float)
    return mult


def apply_sequence(target, g0, coefs):
    out = target.copy()
    stocks = out.index[out.index != INDEX_ASSET]
    stock_total = float(out.reindex(stocks).sum())
    if stock_total <= 0 or len(stocks) == 0 or not coefs:
        return out, {
            "sequence_weight_pre": 0.0,
            "sequence_weight_post": 0.0,
            "sequence_names": 0,
            "flow_names": 0,
            "three_names": 0,
            "dual_names": 0,
            "multi_event_names": 0,
        }

    g = g0.copy()
    g.index = g.index.get_level_values("code")
    mult = sequence_multiplier(g0, coefs).reindex(stocks).fillna(1.0)
    bumped = mult > 1.0

    info = {
        "sequence_weight_pre": float(out.reindex(stocks)[bumped].sum()),
        "sequence_names": int(bumped.sum()),
        "flow_names": int(
            g["event_flow_revision"].reindex(stocks).fillna(False).sum()
        )
        if "FLOW" in coefs
        else 0,
        "three_names": int(
            g["event_three_stage"].reindex(stocks).fillna(False).sum()
        )
        if "THREE" in coefs
        else 0,
        "dual_names": int(
            g["event_dual_revision"].reindex(stocks).fillna(False).sum()
        )
        if "DUAL" in coefs
        else 0,
    }

    active_cols = [EVENT_SPECS[k][0] for k in coefs]
    if active_cols:
        active_count = (
            g[active_cols]
            .reindex(stocks)
            .fillna(False)
            .astype(int)
            .sum(axis=1)
        )
        info["multi_event_names"] = int((active_count >= 2).sum())
    else:
        info["multi_event_names"] = 0

    adj = out.reindex(stocks).fillna(0.0) * mult
    if adj.sum() > 0:
        out.loc[stocks] = adj / adj.sum() * stock_total

    info["sequence_weight_post"] = float(out.reindex(stocks)[bumped].sum())
    return out[out > 1e-12], info


def turnover(old_end: pd.Series, new: pd.Series) -> float:
    idx = old_end.index.union(new.index)
    a = old_end.reindex(idx, fill_value=0.0)
    b = new.reindex(idx, fill_value=0.0)
    old_cash = 1.0 - float(a.sum())
    new_cash = 1.0 - float(b.sum())
    return 0.5 * (
        float((a - b).abs().sum()) + abs(old_cash - new_cash)
    )


def simulate_variant(
    name,
    coefs,
    panel,
    scores,
    returns,
    scheduled_panels,
    k200_period,
    leader_signal,
):
    fwd10 = lab.forward_return(returns, STEP)
    old_end = pd.Series(dtype=float)
    rows = []
    weight_rows = []

    for dt0, g0 in panel.groupby(level="date"):
        dt = pd.Timestamp(dt0)
        if (
            dt not in scores
            or dt not in k200_period.index
            or pd.isna(k200_period.loc[dt])
            or dt not in fwd10.index
        ):
            continue

        state = str(g0["state"].iloc[0])
        size_state = str(g0["size_state"].iloc[0])
        leader_on = bool(leader_signal.at[dt, "leader_on"])
        engine = current_engine(state, size_state, leader_on)

        target = off.targets_for_date(
            g0, scores[dt], scheduled_panels[dt]
        )[engine].sort_values(ascending=False)

        target, seq_info = apply_sequence(target, g0, coefs)

        codes = g0.index.get_level_values("code")
        stock_future = fwd10.loc[dt].reindex(codes).fillna(0.0)
        asset_r = stock_future.copy()
        asset_r.loc[INDEX_ASSET] = float(k200_period.loc[dt])
        rr = asset_r.reindex(target.index).fillna(0.0)

        turn = turnover(old_end, target)
        gross = float((target * rr).sum())
        net = gross - turn * COST_BPS / 10000.0

        denom = 1.0 + gross
        old_end = (
            target * (1.0 + rr) / denom if denom > 0 else target.copy()
        )
        old_end = old_end[old_end.abs() > 1e-12]

        sw = target.sort_values(ascending=False)
        rows.append(
            {
                "date": dt,
                "variant": name,
                "state": state,
                "size_state": size_state,
                "leader_on": leader_on,
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
                **seq_info,
            }
        )

        g_for_flags = g0.copy()
        g_for_flags.index = g_for_flags.index.get_level_values("code")
        mult = sequence_multiplier(g0, coefs)
        for asset, w in sw.items():
            if asset == INDEX_ASSET:
                flags = {
                    "event_flow_revision": False,
                    "event_three_stage": False,
                    "event_dual_revision": False,
                }
                m = np.nan
            else:
                flags = {
                    col: bool(
                        g_for_flags[col].get(asset, False)
                        if col in g_for_flags
                        else False
                    )
                    for col in [
                        "event_flow_revision",
                        "event_three_stage",
                        "event_dual_revision",
                    ]
                }
                m = float(mult.get(asset, 1.0))
            weight_rows.append(
                {
                    "date": dt,
                    "variant": name,
                    "engine": engine,
                    "asset": asset,
                    "weight": float(w),
                    "sequence_multiplier": m,
                    **flags,
                }
            )

    return pd.DataFrame(rows), pd.DataFrame(weight_rows)


def strategy_metrics(g: pd.DataFrame) -> dict:
    g = g.sort_values("date").dropna(subset=["net", "k200_return"])
    if len(g) < 5:
        return {}
    periods = 252 / STEP
    years = len(g) / periods
    s = g["net"]
    b = g["k200_return"]
    active = s - b
    sw = (1.0 + s).cumprod()
    bw = (1.0 + b).cumprod()
    rw = sw / bw
    return {
        "n_periods": int(len(g)),
        "strategy_cagr": float(sw.iloc[-1] ** (1 / years) - 1),
        "k200_cagr": float(bw.iloc[-1] ** (1 / years) - 1),
        "relative_cagr": float(rw.iloc[-1] ** (1 / years) - 1),
        "information_ratio": float(
            active.mean() / active.std(ddof=1) * math.sqrt(periods)
        )
        if active.std(ddof=1) > 0
        else np.nan,
        "strategy_mdd": float((sw / sw.cummax() - 1).min()),
        "relative_mdd": float((rw / rw.cummax() - 1).min()),
        "annual_turnover": float(g["turnover"].mean() * periods),
        "avg_top1_weight": float(g["top1_weight"].mean()),
        "avg_top5_weight": float(g["top5_weight"].mean()),
    }


def summarize_strategy(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for variant, g0 in detail.groupby("variant"):
        for sample, lo, hi in (
            ("train", START, SPLIT),
            ("test", SPLIT, END + pd.Timedelta(days=1)),
        ):
            m = strategy_metrics(
                g0[(g0.date >= lo) & (g0.date < hi)].copy()
            )
            if m:
                rows.append({"variant": variant, "sample": sample, **m})
    return pd.DataFrame(rows)


def bootstrap_mean_ci(x: pd.Series, seed=42, n_boot=20000):
    arr = pd.to_numeric(x, errors="coerce").dropna().to_numpy(dtype=float)
    if len(arr) < 2:
        return np.nan, np.nan
    rng = np.random.default_rng(seed)
    draws = rng.choice(arr, size=(n_boot, len(arr)), replace=True).mean(axis=1)
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def overlay_ann(v: pd.Series, b: pd.Series) -> float:
    x = pd.concat([v.rename("v"), b.rename("b")], axis=1).dropna()
    if len(x) == 0:
        return np.nan
    ratio = float(
        (1.0 + x["v"]).prod() / (1.0 + x["b"]).prod()
    )
    return ratio ** ((252 / STEP) / len(x)) - 1.0


def overlay_stats(detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_d = (
        detail[detail.variant == "BASE"]
        .set_index("date")
        .sort_index()
    )
    rows = []
    outlier_rows = []

    for variant in sorted(set(detail.variant) - {"BASE"}):
        v0 = detail[detail.variant == variant].set_index("date").sort_index()
        dates = base_d.index.intersection(v0.index)
        x = pd.DataFrame(
            {
                "base": base_d.loc[dates, "net"],
                "variant_ret": v0.loc[dates, "net"],
                "state": v0.loc[dates, "state"],
                "engine": v0.loc[dates, "engine"],
            },
            index=dates,
        )
        x["delta"] = x["variant_ret"] - x["base"]
        x["relative_period"] = (
            (1.0 + x["variant_ret"]) / (1.0 + x["base"]) - 1.0
        )

        for sample, lo, hi in (
            ("train", START, SPLIT),
            ("test", SPLIT, END + pd.Timedelta(days=1)),
        ):
            q = x[(x.index >= lo) & (x.index < hi)].copy()
            if len(q) < 5:
                continue
            sd = q["delta"].std(ddof=1)
            tstat = (
                float(q["delta"].mean() / (sd / math.sqrt(len(q))))
                if sd > 0
                else np.nan
            )
            ci_lo, ci_hi = bootstrap_mean_ci(q["delta"])
            total_delta = float(q["delta"].sum())
            ordered = q.sort_values("delta", ascending=False)

            row = {
                "variant": variant,
                "sample": sample,
                "n_periods": int(len(q)),
                "mean_delta": float(q["delta"].mean()),
                "median_delta": float(q["delta"].median()),
                "hit_rate": float((q["delta"] > 0).mean()),
                "t_stat": tstat,
                "bootstrap_mean_ci_lo": ci_lo,
                "bootstrap_mean_ci_hi": ci_hi,
                "simple_delta_sum": total_delta,
                "overlay_relative_cagr": overlay_ann(
                    q["variant_ret"], q["base"]
                ),
            }
            for k in (1, 3, 5):
                top_sum = float(ordered["delta"].head(k).sum())
                row[f"top{k}_delta_sum"] = top_sum
                row[f"top{k}_share_of_net_delta"] = (
                    top_sum / total_delta
                    if abs(total_delta) > 1e-12
                    else np.nan
                )
            rows.append(row)

            for k in (1, 3, 5):
                drop_dates = ordered.head(k).index
                keep = q.drop(index=drop_dates)
                outlier_rows.append(
                    {
                        "variant": variant,
                        "sample": sample,
                        "drop_top_k": k,
                        "remaining_periods": int(len(keep)),
                        "overlay_relative_cagr_after_drop": overlay_ann(
                            keep["variant_ret"], keep["base"]
                        ),
                        "mean_delta_after_drop": float(
                            keep["delta"].mean()
                        )
                        if len(keep)
                        else np.nan,
                        "hit_rate_after_drop": float(
                            (keep["delta"] > 0).mean()
                        )
                        if len(keep)
                        else np.nan,
                    }
                )
    return pd.DataFrame(rows), pd.DataFrame(outlier_rows)


def period_attribution(detail: pd.DataFrame) -> pd.DataFrame:
    base_d = (
        detail[detail.variant == "BASE"]
        .set_index("date")
        .sort_index()
    )
    rows = []
    for variant in sorted(set(detail.variant) - {"BASE"}):
        v0 = detail[detail.variant == variant].set_index("date").sort_index()
        for dt in base_d.index.intersection(v0.index):
            rows.append(
                {
                    "date": dt,
                    "sample": "train" if dt < SPLIT else "test",
                    "variant": variant,
                    "state": v0.at[dt, "state"],
                    "engine": v0.at[dt, "engine"],
                    "base_net": float(base_d.at[dt, "net"]),
                    "variant_net": float(v0.at[dt, "net"]),
                    "delta_net": float(
                        v0.at[dt, "net"] - base_d.at[dt, "net"]
                    ),
                    "relative_period": float(
                        (1.0 + v0.at[dt, "net"])
                        / (1.0 + base_d.at[dt, "net"])
                        - 1.0
                    ),
                    "turnover_delta": float(
                        v0.at[dt, "turnover"]
                        - base_d.at[dt, "turnover"]
                    ),
                    "sequence_weight_pre": float(
                        v0.at[dt, "sequence_weight_pre"]
                    ),
                    "sequence_weight_post": float(
                        v0.at[dt, "sequence_weight_post"]
                    ),
                    "sequence_names": int(v0.at[dt, "sequence_names"]),
                }
            )
    return pd.DataFrame(rows)


def grouped_overlay_stats(attribution: pd.DataFrame) -> pd.DataFrame:
    q = attribution[attribution["sample"] == "test"].copy()
    rows = []
    for variant in ["FLOW_ONLY", "THREE_ONLY", "DUAL_ONLY", "ALL_CURRENT"]:
        v = q[q.variant == variant]
        for dims, grp in [
            (["state"], v.groupby("state")),
            (["engine"], v.groupby("engine")),
            (["state", "engine"], v.groupby(["state", "engine"])),
        ]:
            for keys, g in grp:
                if not isinstance(keys, tuple):
                    keys = (keys,)
                if len(g) < 3:
                    continue
                rec = {
                    "variant": variant,
                    "group_type": "+".join(dims),
                    "n_periods": int(len(g)),
                    "mean_delta": float(g.delta_net.mean()),
                    "median_delta": float(g.delta_net.median()),
                    "hit_rate": float((g.delta_net > 0).mean()),
                    "delta_sum": float(g.delta_net.sum()),
                    "avg_sequence_weight_pre": float(
                        g.sequence_weight_pre.mean()
                    ),
                    "avg_sequence_weight_post": float(
                        g.sequence_weight_post.mean()
                    ),
                    "avg_sequence_names": float(
                        g.sequence_names.mean()
                    ),
                }
                for dim, key in zip(dims, keys):
                    rec[dim] = key
                rows.append(rec)
    return pd.DataFrame(rows)


def main():
    returns, basic_panels = base.load_basic()
    returns = returns.loc[:END]

    panel, scheduled_panels, schedule_map = seqbase.build_true_calendar_panel(
        returns, basic_panels
    )

    fwd20 = lab.forward_return(returns, lab.HORIZON)
    ic = lab.ic_detail(panel, fwd20, "K200")
    static, mapping, _ = lab.factor_maps(ic, "K200")
    scores, selections = lab.score_history(
        panel, ic, "K200", static, mapping
    )

    signal_dates = sorted(
        panel.index.get_level_values("date").unique()
    )
    k200_close = download_kospi200_patched()
    k200_period = forward_index_returns_aligned(
        k200_close, signal_dates, STEP, returns.index
    )

    candidate_detail, _ = off.run_all(
        panel,
        scores,
        returns,
        scheduled_panels,
        k200_period,
        cost_bps=COST_BPS,
    )
    leader_signal = build_leader_signal(panel, candidate_detail)

    detail_frames = []
    weight_frames = []
    for name, coefs in VARIANTS.items():
        d, w = simulate_variant(
            name,
            coefs,
            panel,
            scores,
            returns,
            scheduled_panels,
            k200_period,
            leader_signal,
        )
        detail_frames.append(d)
        weight_frames.append(w)

    detail = pd.concat(detail_frames, ignore_index=True)
    weights = pd.concat(weight_frames, ignore_index=True)

    strategy_summary = summarize_strategy(detail)
    overlay_summary, outlier_robustness = overlay_stats(detail)
    attribution = period_attribution(detail)
    grouped = grouped_overlay_stats(attribution)

    schedule_map.to_csv(
        OUT / "true_calendar_schedule_map.csv",
        index=False,
        encoding="utf-8-sig",
    )
    leader_signal.reset_index().to_csv(
        OUT / "leader_signal_diagnostics.csv",
        index=False,
        encoding="utf-8-sig",
    )
    selections.to_csv(
        OUT / "factor_selection_history.csv",
        index=False,
        encoding="utf-8-sig",
    )
    detail.to_csv(
        OUT / "variant_period_returns.csv",
        index=False,
        encoding="utf-8-sig",
    )
    weights.to_csv(
        OUT / "variant_target_weights.csv",
        index=False,
        encoding="utf-8-sig",
    )
    strategy_summary.to_csv(
        OUT / "strategy_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    overlay_summary.to_csv(
        OUT / "sequence_overlay_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    outlier_robustness.to_csv(
        OUT / "outlier_robustness.csv",
        index=False,
        encoding="utf-8-sig",
    )
    attribution.to_csv(
        OUT / "period_attribution.csv",
        index=False,
        encoding="utf-8-sig",
    )
    grouped.to_csv(
        OUT / "state_engine_attribution.csv",
        index=False,
        encoding="utf-8-sig",
    )

    structure_order = list(STRUCTURE_VARIANTS)
    oos_strategy = strategy_summary[
        strategy_summary["sample"] == "test"
    ].copy()
    oos_structure = oos_strategy[
        oos_strategy["variant"].isin(structure_order)
    ].copy()
    oos_structure["order"] = oos_structure["variant"].map(
        {k: i for i, k in enumerate(structure_order)}
    )
    oos_structure = oos_structure.sort_values("order").drop(
        columns="order"
    )

    oos_overlay = overlay_summary[
        overlay_summary["sample"] == "test"
    ].copy()
    oos_structure_overlay = oos_overlay[
        oos_overlay["variant"].isin(
            [x for x in structure_order if x != "BASE"]
        )
    ].copy()

    scale_order = ["ALL_X050", "ALL_X075", "ALL_CURRENT", "ALL_X125", "ALL_X150"]
    oos_scale = oos_strategy[
        oos_strategy["variant"].isin(scale_order)
    ].copy()
    oos_scale["order"] = oos_scale["variant"].map(
        {k: i for i, k in enumerate(scale_order)}
    )
    oos_scale = oos_scale.sort_values("order").drop(columns="order")

    all_attr = attribution[
        (attribution["variant"] == "ALL_CURRENT")
        & (attribution["sample"] == "test")
    ].sort_values("delta_net", ascending=False)
    top_periods = pd.concat(
        [all_attr.head(10), all_attr.tail(10)]
    ).drop_duplicates()

    report = (
        "# K200 Sequence Attribution v1\n\n"
        "Deterioration gates are excluded. The pre-existing leader activation rule and "
        "the intended concentrated portfolio construction are held fixed. The only "
        "experimental change is the sequence overlay applied inside the stock sleeve.\n\n"
        "## OOS structural variants\n\n"
        + oos_structure.to_markdown(index=False)
        + "\n\n## OOS overlay statistics vs BASE\n\n"
        + oos_structure_overlay.to_markdown(index=False)
        + "\n\n## Multiplier sensitivity\n\n"
        + oos_scale.to_markdown(index=False)
        + "\n\n## ALL_CURRENT best/worst OOS periods\n\n"
        + top_periods.to_markdown(index=False)
        + "\n\n## State / engine attribution\n\n"
        + grouped[
            (grouped["variant"] == "ALL_CURRENT")
        ].to_markdown(index=False)
    )
    (OUT / "summary.md").write_text(report, encoding="utf-8")

    print("=== OOS STRUCTURAL VARIANTS ===")
    print(oos_structure.to_string(index=False))
    print("\n=== OOS OVERLAY STATS VS BASE ===")
    print(oos_structure_overlay.to_string(index=False))
    print("\n=== OUTLIER ROBUSTNESS: ALL_CURRENT OOS ===")
    print(
        outlier_robustness[
            (outlier_robustness.variant == "ALL_CURRENT")
            & (outlier_robustness["sample"] == "test")
        ].to_string(index=False)
    )
    print("\n=== MULTIPLIER SENSITIVITY OOS ===")
    print(oos_scale.to_string(index=False))
    print("\n=== ALL_CURRENT STATE/ENGINE ATTRIBUTION ===")
    print(
        grouped[
            grouped.variant == "ALL_CURRENT"
        ].to_string(index=False)
    )
    print("\n=== ALL_CURRENT TOP/BOTTOM OOS PERIODS ===")
    print(top_periods.to_string(index=False))


if __name__ == "__main__":
    main()
