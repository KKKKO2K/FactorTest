from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "k200_factor_sleeve_topn_sensitivity_results"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location(
    "agg", HERE / "k200_factor_sleeve_aggregation.py"
)
agg = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(agg)

START, SPLIT, END, STEP = agg.START, agg.SPLIT, agg.END, agg.STEP
COST_BPS = agg.COST_BPS
ENGINE_SPECS = agg.ENGINE_SPECS

ORIGINAL_TOPN = {k: int(v["top_n"]) for k, v in ENGINE_SPECS.items()}
FIXED_TOPN = (5, 10, 15, 20)


def restore_original_topn():
    for engine, n in ORIGINAL_TOPN.items():
        ENGINE_SPECS[engine]["top_n"] = n


def set_fixed_topn(n: int):
    for engine in ENGINE_SPECS:
        ENGINE_SPECS[engine]["top_n"] = int(n)


def overlay_cagr(v: pd.Series, b: pd.Series) -> float:
    x = pd.concat([v.rename("v"), b.rename("b")], axis=1).dropna()
    if x.empty:
        return np.nan
    ratio = float((1.0 + x.v).prod() / (1.0 + x.b).prod())
    return ratio ** ((252.0 / STEP) / len(x)) - 1.0


def comparison_table(detail: pd.DataFrame) -> pd.DataFrame:
    base = detail[detail.variant == "COMPOSITE"].set_index("date").sort_index()
    rows = []
    for variant in sorted(set(detail.variant) - {"COMPOSITE"}):
        v = detail[detail.variant == variant].set_index("date").sort_index()
        for dt in base.index.intersection(v.index):
            rows.append({
                "date": dt,
                "sample": "train" if dt < SPLIT else "test",
                "variant": variant,
                "state": v.at[dt, "state"],
                "engine": v.at[dt, "engine"],
                "base_net": float(base.at[dt, "net"]),
                "variant_net": float(v.at[dt, "net"]),
                "delta_net": float(v.at[dt, "net"] - base.at[dt, "net"]),
                "turnover_delta": float(v.at[dt, "turnover"] - base.at[dt, "turnover"]),
                "n_stocks_delta": float(v.at[dt, "n_stocks"] - base.at[dt, "n_stocks"]),
                "top1_delta": float(v.at[dt, "top1_stock_weight"] - base.at[dt, "top1_stock_weight"]),
                "top5_delta": float(v.at[dt, "top5_stock_weight"] - base.at[dt, "top5_stock_weight"]),
            })
    return pd.DataFrame(rows)


def grouped_attribution(comp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, sample), q in comp.groupby(["variant", "sample"]):
        for group_type, group_cols in (("engine", ["engine"]), ("state", ["state"])):
            for key, g in q.groupby(group_cols[0]):
                if len(g) == 0:
                    continue
                sd = g.delta_net.std(ddof=1)
                tstat = (
                    float(g.delta_net.mean() / (sd / math.sqrt(len(g))))
                    if len(g) > 2 and sd > 0
                    else np.nan
                )
                rows.append({
                    "variant": variant,
                    "sample": sample,
                    "group_type": group_type,
                    "group": key,
                    "n_periods": int(len(g)),
                    "mean_delta_bp": float(g.delta_net.mean() * 10000),
                    "median_delta_bp": float(g.delta_net.median() * 10000),
                    "hit_rate": float((g.delta_net > 0).mean()),
                    "t_stat": tstat,
                    "mean_turnover_delta": float(g.turnover_delta.mean()),
                    "mean_n_stocks_delta": float(g.n_stocks_delta.mean()),
                    "mean_top1_delta": float(g.top1_delta.mean()),
                    "mean_top5_delta": float(g.top5_delta.mean()),
                })
    return pd.DataFrame(rows)


def outlier_robustness(comp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, sample), q0 in comp.groupby(["variant", "sample"]):
        q = q0.sort_values("delta_net", ascending=False).copy()
        if len(q) < 5:
            continue
        base_total = float(q.delta_net.sum())
        rec = {
            "variant": variant,
            "sample": sample,
            "n_periods": int(len(q)),
            "mean_delta_bp": float(q.delta_net.mean() * 10000),
            "median_delta_bp": float(q.delta_net.median() * 10000),
            "hit_rate": float((q.delta_net > 0).mean()),
            "overlay_relative_cagr": overlay_cagr(q.variant_net, q.base_net),
            "simple_delta_sum": base_total,
        }
        for k in (1, 3, 5):
            top_sum = float(q.head(k).delta_net.sum())
            keep = q.iloc[k:]
            rec[f"top{k}_share_of_delta"] = (
                top_sum / base_total if abs(base_total) > 1e-12 else np.nan
            )
            rec[f"overlay_cagr_drop_top{k}"] = overlay_cagr(
                keep.variant_net, keep.base_net
            ) if len(keep) else np.nan
            rec[f"mean_delta_bp_drop_top{k}"] = (
                float(keep.delta_net.mean() * 10000) if len(keep) else np.nan
            )
        rows.append(rec)
    return pd.DataFrame(rows)


def consensus_summary(detail: pd.DataFrame) -> pd.DataFrame:
    q = detail[(detail.variant != "COMPOSITE") & detail.engine.isin(ENGINE_SPECS)].copy()
    rows = []
    for (variant, sample, engine), g in q.assign(
        sample=np.where(q.date < SPLIT, "train", "test")
    ).groupby(["variant", "sample", "engine"]):
        rows.append({
            "variant": variant,
            "sample": sample,
            "engine": engine,
            "n_periods": int(len(g)),
            "avg_union_names": float(g.factor_union_names.mean()),
            "avg_overlap_names_ge2": float(g.factor_overlap_names_ge2.mean()),
            "avg_overlap_names_ge3": float(g.factor_overlap_names_ge3.mean()),
            "avg_overlap_names_all": float(g.factor_overlap_names_all.mean()),
            "avg_stock_weight_in_ge2": float(g.stock_weight_in_ge2.mean()),
            "avg_stock_weight_in_ge3": float(g.stock_weight_in_ge3.mean()),
            "avg_weighted_factor_count": float(g.weighted_mean_factor_count.mean()),
            "avg_n_stocks": float(g.n_stocks.mean()),
            "avg_top1_stock_weight": float(g.top1_stock_weight.mean()),
            "avg_top5_stock_weight": float(g.top5_stock_weight.mean()),
        })
    return pd.DataFrame(rows)


def main():
    returns, basic_panels = agg.base.load_basic()
    returns = returns.loc[:END]
    panel, scheduled_panels, schedule_map = agg.build_true_calendar_panel_fixed(
        returns, basic_panels
    )

    fwd20 = agg.lab.forward_return(returns, agg.lab.HORIZON)
    ic = agg.lab.ic_detail(panel, fwd20, "K200")
    static, mapping, _ = agg.lab.factor_maps(ic, "K200")
    scores, _ = agg.lab.score_history(panel, ic, "K200", static, mapping)

    signal_dates = sorted(panel.index.get_level_values("date").unique())
    k200_close = agg.seqattr.download_kospi200_patched()
    k200_period = agg.seqattr.forward_index_returns_aligned(
        k200_close, signal_dates, STEP, returns.index
    )

    candidate_detail, _ = agg.off.run_all(
        panel,
        scores,
        returns,
        scheduled_panels,
        k200_period,
        cost_bps=COST_BPS,
    )
    leader_signal = agg.seqattr.build_leader_signal(panel, candidate_detail)

    detail_frames = []
    weight_frames = []

    restore_original_topn()
    d, w, _ = agg.simulate(
        "COMPOSITE",
        panel,
        scores,
        returns,
        scheduled_panels,
        k200_period,
        leader_signal,
    )
    detail_frames.append(d)
    weight_frames.append(w)

    restore_original_topn()
    d, w, _ = agg.simulate(
        "SLEEVE_ORIGINAL_N",
        panel,
        scores,
        returns,
        scheduled_panels,
        k200_period,
        leader_signal,
    )
    detail_frames.append(d)
    weight_frames.append(w)

    for n in FIXED_TOPN:
        set_fixed_topn(n)
        name = f"SLEEVE_TOP{n}"
        d, w, _ = agg.simulate(
            name,
            panel,
            scores,
            returns,
            scheduled_panels,
            k200_period,
            leader_signal,
        )
        detail_frames.append(d)
        weight_frames.append(w)

    restore_original_topn()

    detail = pd.concat(detail_frames, ignore_index=True)
    weights = pd.concat(weight_frames, ignore_index=True)
    summary = agg.summarize(detail)
    comparison = comparison_table(detail)
    attribution = grouped_attribution(comparison)
    outlier = outlier_robustness(comparison)
    consensus = consensus_summary(detail)

    schedule_map.to_csv(
        OUT / "true_calendar_schedule_map.csv", index=False, encoding="utf-8-sig"
    )
    detail.to_csv(OUT / "period_returns.csv", index=False, encoding="utf-8-sig")
    weights.to_csv(OUT / "target_weights.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "strategy_summary.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(OUT / "period_comparison.csv", index=False, encoding="utf-8-sig")
    attribution.to_csv(OUT / "engine_state_attribution.csv", index=False, encoding="utf-8-sig")
    outlier.to_csv(OUT / "outlier_robustness.csv", index=False, encoding="utf-8-sig")
    consensus.to_csv(OUT / "consensus_diagnostics.csv", index=False, encoding="utf-8-sig")

    order = [
        "COMPOSITE",
        "SLEEVE_ORIGINAL_N",
        "SLEEVE_TOP5",
        "SLEEVE_TOP10",
        "SLEEVE_TOP15",
        "SLEEVE_TOP20",
    ]
    oos = summary[summary.sample == "test"].copy()
    oos["order"] = oos.variant.map({v: i for i, v in enumerate(order)})
    oos = oos.sort_values("order").drop(columns="order")
    train = summary[summary.sample == "train"].copy()
    train["order"] = train.variant.map({v: i for i, v in enumerate(order)})
    train = train.sort_values("order").drop(columns="order")

    oos_attr = attribution[
        (attribution.sample == "test") & (attribution.group_type == "engine")
    ].copy()
    oos_outlier = outlier[outlier.sample == "test"].copy()
    oos_consensus = consensus[consensus.sample == "test"].copy()

    text = [
        "# K200 Factor Sleeve Top-N Sensitivity",
        "",
        "## Design",
        "",
        "- Composite baseline unchanged.",
        "- Factor budgets unchanged for every engine.",
        "- Kappa, within-factor cap, market-state router, Leader override, 10D calendar, and 60bp one-way turnover cost unchanged.",
        "- Only the number of names selected inside each factor sleeve is changed.",
        "- Fixed Top-N variants use the same N for VALUE_REV, REV_BREADTH, and CONTRARIAN factor sleeves.",
        "- SLEEVE_ORIGINAL_N retains VALUE_REV=30 and REV_BREADTH/CONTRARIAN=20.",
        "- No post-aggregation recap: overlap names naturally accumulate weight across factor sleeves.",
        "",
        "## OOS summary",
        "",
        oos.to_markdown(index=False),
        "",
        "## Train summary",
        "",
        train.to_markdown(index=False),
        "",
        "## OOS engine attribution vs Composite",
        "",
        oos_attr.to_markdown(index=False),
        "",
        "## OOS outlier robustness vs Composite",
        "",
        oos_outlier.to_markdown(index=False),
        "",
        "## OOS consensus / concentration diagnostics",
        "",
        oos_consensus.to_markdown(index=False),
    ]
    (OUT / "summary.md").write_text("\n".join(text), encoding="utf-8")
    print("\n".join(text))


if __name__ == "__main__":
    main()
