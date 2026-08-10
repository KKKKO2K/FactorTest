from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

import run_cross_factor_liquidity as base
import run_multi_universe_liquidity as mu

HERE = Path(__file__).resolve().parent
OUT = HERE / "results_conditional_state"
OUT.mkdir(parents=True, exist_ok=True)

OVERLAYS = ("BASE", "ACT1_W10", "ACT5_KEEP_TOP70")
TOP_NS = (10, 20)
COSTS = (0, 30, 60)
SPLIT = base.OOS_START

STATE_VARS = (
    "MKT_ACT1",
    "MKT_ACT5",
    "MKT_ACT1_BREADTH",
    "MKT_ACT5_BREADTH",
    "KOSDAQ_TA_SHARE",
    "FACTOR_TOP_ACT5_BREADTH",
    "FACTOR_TOP_TA_SHARE",
    "FACTOR_TOP_REL_ACT5",
)


def safe_div(a: float, b: float) -> float:
    return float(a / b) if pd.notna(a) and pd.notna(b) and b != 0 else np.nan


def tstat(x: pd.Series) -> float:
    x = x.dropna()
    if len(x) < 3:
        return np.nan
    sd = x.std(ddof=1)
    if pd.isna(sd) or sd <= 0:
        return np.nan
    return float(x.mean() / (sd / math.sqrt(len(x))))


def bin_from_train(x: pd.Series, q1: float, q2: float) -> pd.Series:
    return pd.Series(np.where(x <= q1, "LOW", np.where(x >= q2, "HIGH", "MID")), index=x.index)


def main() -> None:
    returns, mcap, k200_by_date = base.load_basic()
    market_by_date = mu.load_market_by_date()
    ta = base.load_trading_amount()
    fwd = base.forward_returns(returns, base.HORIZON)
    liq_frames = base.build_liquidity_features(ta, mcap)
    factor_files = {name: base.dated_files(folder) for name, folder in base.FACTORS.items()}

    # Aggregate market trading amount features are computed strictly point-in-time.
    total_all = ta.sum(axis=1, min_count=1)
    total_all_hist20 = total_all.shift(1).rolling(20, min_periods=15).mean()
    total_all_prior20 = total_all.shift(5).rolling(20, min_periods=15).mean()
    total_all_recent5 = total_all.rolling(5, min_periods=4).mean()

    common = sorted(set(returns.index) & set(ta.index) & set(k200_by_date) & set(market_by_date))
    dates = [d for d in common if d >= base.START][::base.STEP]

    current: dict[tuple, list[str]] = {}
    rows: list[dict] = []

    for dt in dates:
        if dt not in fwd.index:
            continue
        k = k200_by_date[dt]
        market = market_by_date[dt]
        mc_full = mcap.loc[dt]
        raw_ta_full = ta.loc[dt]
        liq_full = {name: frame.loc[dt] if dt in frame.index else pd.Series(dtype=float)
                    for name, frame in liq_frames.items()}

        # One market-level cross-market state used for all universes.
        kosdaq_codes = market.index[market.eq("KOSDAQ")]
        kospi_codes = market.index[market.eq("KOSPI")]
        kd_ta = raw_ta_full.reindex(kosdaq_codes).sum(min_count=1)
        kp_ta = raw_ta_full.reindex(kospi_codes).sum(min_count=1)
        kosdaq_share = safe_div(kd_ta, kd_ta + kp_ta)

        factor_raw = {factor: base.load_factor(files[dt]) for factor, files in factor_files.items() if dt in files}

        for universe in mu.UNIVERSES:
            codes = mu.universe_codes(universe, k, market)
            y = fwd.loc[dt].reindex(codes)
            min_obs = 80 if universe == "K200" else 150
            if y.notna().sum() < min_obs:
                continue

            mc = mc_full.reindex(codes)
            liq = {name: s.reindex(codes) for name, s in liq_full.items()}
            raw_u = liq["raw"]
            act1_u = liq["act1"]
            act5_u = liq["act5"]

            # Universe-level activity states.
            # Weighted aggregate activity ratio uses constituent trading amount sums.
            # Cross-sectional breadth is deliberately separate.
            u_ta_hist20 = ta.reindex(columns=codes).shift(1).rolling(20, min_periods=15).mean().loc[dt].sum(min_count=1)
            u_ta_prior20 = ta.reindex(columns=codes).shift(5).rolling(20, min_periods=15).mean().loc[dt].sum(min_count=1)
            u_ta_recent5 = ta.reindex(columns=codes).rolling(5, min_periods=4).mean().loc[dt].sum(min_count=1)
            u_ta_now = raw_u.sum(min_count=1)
            mkt_act1 = safe_div(u_ta_now, u_ta_hist20)
            mkt_act5 = safe_div(u_ta_recent5, u_ta_prior20)
            mkt_act1_breadth = float((act1_u > 1).mean()) if act1_u.notna().sum() else np.nan
            mkt_act5_breadth = float((act5_u > 1).mean()) if act5_u.notna().sum() else np.nan
            total_u_ta = raw_u.sum(min_count=1)

            for factor, raw_full in factor_raw.items():
                raw = raw_full.reindex(codes)
                if raw.notna().sum() < max(50, min_obs // 2):
                    continue

                for direction, high_good in (("HIGH", True), ("LOW", False)):
                    factor_score = base.pct_rank(raw, high_good=high_good)
                    scores = mu.build_scores(factor_score, liq, mc)

                    # Factor-top state uses top decile with a 20-name floor.
                    valid = factor_score.dropna().sort_values(ascending=False)
                    top_k = min(len(valid), max(20, int(math.ceil(len(valid) * 0.10))))
                    factor_top = valid.head(top_k).index
                    ft_act5 = act5_u.reindex(factor_top)
                    ft_ta = raw_u.reindex(factor_top).sum(min_count=1)
                    factor_top_act5_breadth = float((ft_act5 > 1).mean()) if ft_act5.notna().sum() else np.nan
                    factor_top_ta_share = safe_div(ft_ta, total_u_ta)
                    factor_top_rel_act5 = float(ft_act5.median() - act5_u.median()) if ft_act5.notna().sum() else np.nan

                    states = {
                        "MKT_ACT1": mkt_act1,
                        "MKT_ACT5": mkt_act5,
                        "MKT_ACT1_BREADTH": mkt_act1_breadth,
                        "MKT_ACT5_BREADTH": mkt_act5_breadth,
                        "KOSDAQ_TA_SHARE": kosdaq_share,
                        "FACTOR_TOP_ACT5_BREADTH": factor_top_act5_breadth,
                        "FACTOR_TOP_TA_SHARE": factor_top_ta_share,
                        "FACTOR_TOP_REL_ACT5": factor_top_rel_act5,
                    }

                    for n in TOP_NS:
                        for overlay in OVERLAYS:
                            score = scores[overlay]
                            names = base.select_top(score, n)
                            if len(names) < n:
                                continue
                            gross = float(y.reindex(names).mean())
                            for cost in COSTS:
                                key = (universe, factor, direction, overlay, n, cost)
                                turn = base.overlap_turnover(current.get(key, []), names, n)
                                net = gross - turn * cost / 10000.0
                                row = {
                                    "date": dt, "universe": universe, "factor": factor, "direction": direction,
                                    "overlay": overlay, "top_n": n, "cost_bps": cost,
                                    "net": net, "turnover": turn,
                                }
                                row.update(states)
                                rows.append(row)
                                current[key] = names

    periods = pd.DataFrame(rows)
    periods["date"] = pd.to_datetime(periods["date"])

    # Pair overlay with same-date BASE; period delta is the clean object for conditional tests.
    idx = ["date", "universe", "factor", "direction", "top_n", "cost_bps"]
    base_p = periods[periods.overlay == "BASE"].set_index(idx)["net"].rename("base_net")
    paired = periods[periods.overlay != "BASE"].copy()
    paired = paired.join(base_p, on=idx)
    paired["delta"] = paired["net"] - paired["base_net"]

    detail_rows = []
    spread_rows = []
    config_cols = ["universe", "factor", "direction", "overlay", "top_n", "cost_bps"]

    for cfg, g in paired.groupby(config_cols):
        g = g.sort_values("date").copy()
        train = g[g.date < SPLIT]
        if len(train) < 30:
            continue
        for state in STATE_VARS:
            tr_state = train[state].dropna()
            if len(tr_state) < 30 or tr_state.nunique() < 5:
                continue
            q1, q2 = tr_state.quantile([1/3, 2/3]).tolist()
            if not np.isfinite(q1) or not np.isfinite(q2) or q1 >= q2:
                continue
            g["state_bin"] = bin_from_train(g[state], q1, q2)
            for sample, smask in (("TRAIN", g.date < SPLIT), ("OOS", g.date >= SPLIT)):
                x = g[smask & g[state].notna()]
                if len(x) < 15:
                    continue
                means = {}
                for b in ("LOW", "MID", "HIGH"):
                    z = x[x.state_bin == b]
                    if len(z) < 5:
                        continue
                    ann_uplift = float(z.delta.mean() * (252.0 / base.HORIZON))
                    means[b] = ann_uplift
                    detail_rows.append({
                        "sample": sample, "universe": cfg[0], "factor": cfg[1], "direction": cfg[2],
                        "overlay": cfg[3], "top_n": cfg[4], "cost_bps": cfg[5], "state": state,
                        "state_bin": b, "train_q1": q1, "train_q2": q2, "n_periods": len(z),
                        "annualized_arith_uplift": ann_uplift, "period_delta_mean": float(z.delta.mean()),
                        "period_delta_tstat": tstat(z.delta), "positive_delta_share": float((z.delta > 0).mean()),
                    })
                if "LOW" in means and "HIGH" in means:
                    spread_rows.append({
                        "sample": sample, "universe": cfg[0], "factor": cfg[1], "direction": cfg[2],
                        "overlay": cfg[3], "top_n": cfg[4], "cost_bps": cfg[5], "state": state,
                        "high_minus_low_ann_uplift": means["HIGH"] - means["LOW"],
                        "low_ann_uplift": means["LOW"], "high_ann_uplift": means["HIGH"],
                    })

    detail = pd.DataFrame(detail_rows)
    spreads = pd.DataFrame(spread_rows)
    detail.to_csv(OUT / "conditional_bins.csv", index=False, encoding="utf-8-sig")
    spreads.to_csv(OUT / "conditional_spreads_by_config.csv", index=False, encoding="utf-8-sig")

    agg_rows = []
    if not spreads.empty:
        for (sample, universe, overlay, state), g in spreads.groupby(["sample", "universe", "overlay", "state"]):
            agg_rows.append({
                "sample": sample, "universe": universe, "overlay": overlay, "state": state,
                "n_configs": len(g),
                "median_high_minus_low_ann_uplift": float(g.high_minus_low_ann_uplift.median()),
                "positive_high_minus_low_share": float((g.high_minus_low_ann_uplift > 0).mean()),
                "median_low_ann_uplift": float(g.low_ann_uplift.median()),
                "median_high_ann_uplift": float(g.high_ann_uplift.median()),
            })
    agg = pd.DataFrame(agg_rows)
    agg.to_csv(OUT / "conditional_spreads_aggregate.csv", index=False, encoding="utf-8-sig")

    persistence_rows = []
    for universe in mu.UNIVERSES:
        for overlay in ("ACT1_W10", "ACT5_KEEP_TOP70"):
            for state in STATE_VARS:
                tr = agg[(agg["sample"] == "TRAIN") & (agg.universe == universe) & (agg.overlay == overlay) & (agg.state == state)]
                oo = agg[(agg["sample"] == "OOS") & (agg.universe == universe) & (agg.overlay == overlay) & (agg.state == state)]
                if tr.empty or oo.empty:
                    continue
                tr, oo = tr.iloc[0], oo.iloc[0]
                persistence_rows.append({
                    "universe": universe, "overlay": overlay, "state": state,
                    "train_spread": tr.median_high_minus_low_ann_uplift,
                    "oos_spread": oo.median_high_minus_low_ann_uplift,
                    "same_sign": np.sign(tr.median_high_minus_low_ann_uplift) == np.sign(oo.median_high_minus_low_ann_uplift),
                    "train_positive_share": tr.positive_high_minus_low_share,
                    "oos_positive_share": oo.positive_high_minus_low_share,
                })
    persistence = pd.DataFrame(persistence_rows)
    persistence.to_csv(OUT / "state_persistence.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# Conditional liquidity-state test",
        "",
        "TRAIN thresholds (terciles) are estimated only on 2016-2022 and frozen into 2023+ OOS.",
        "The target is period-by-period overlay uplift versus the same factor/direction/TopN/cost BASE.",
        "Positive HIGH-LOW means the liquidity overlay works better when the state variable is high.",
        "",
    ]
    for universe in mu.UNIVERSES:
        lines += [f"## {universe}", ""]
        z = persistence[persistence.universe == universe].copy()
        for overlay in ("ACT1_W10", "ACT5_KEEP_TOP70"):
            q = z[z.overlay == overlay].copy()
            if q.empty:
                continue
            q["score"] = q.oos_spread.abs() * (0.5 + q.oos_positive_share)
            q = q.sort_values("score", ascending=False).head(5)
            lines.append(f"### {overlay}")
            for _, r in q.iterrows():
                lines.append(
                    f"- {r.state}: TRAIN H-L {r.train_spread:+.2%}p-equivalent, OOS H-L {r.oos_spread:+.2%}p-equivalent; "
                    f"OOS positive-config share {r.oos_positive_share:.0%}; same-sign={bool(r.same_sign)}"
                )
            lines.append("")

    # Cross-universe persistent relationships only.
    lines += ["# Cross-universe persistence", ""]
    if not persistence.empty:
        cross = persistence.groupby(["overlay", "state"]).agg(
            universe_count=("universe", "size"),
            same_sign_share=("same_sign", "mean"),
            median_train_spread=("train_spread", "median"),
            median_oos_spread=("oos_spread", "median"),
            median_oos_positive_share=("oos_positive_share", "median"),
        ).reset_index()
        cross["rank"] = cross.same_sign_share * cross.median_oos_spread.abs() * (0.5 + cross.median_oos_positive_share)
        for overlay in ("ACT1_W10", "ACT5_KEEP_TOP70"):
            lines.append(f"## {overlay}")
            for _, r in cross[cross.overlay == overlay].sort_values("rank", ascending=False).head(6).iterrows():
                lines.append(
                    f"- {r.state}: same-sign {r.same_sign_share:.0%} of universes; median TRAIN H-L {r.median_train_spread:+.2%}, "
                    f"median OOS H-L {r.median_oos_spread:+.2%}; median OOS positive-config share {r.median_oos_positive_share:.0%}"
                )
            lines.append("")
        cross.to_csv(OUT / "cross_universe_state_summary.csv", index=False, encoding="utf-8-sig")

    (OUT / "CONDITIONAL_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print((OUT / "CONDITIONAL_SUMMARY.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
