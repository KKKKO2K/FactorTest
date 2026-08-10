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
    "MKT_ACT1", "MKT_ACT5", "MKT_ACT1_BREADTH", "MKT_ACT5_BREADTH",
    "KOSDAQ_TA_SHARE", "FACTOR_TOP_ACT5_BREADTH", "FACTOR_TOP_TA_SHARE", "FACTOR_TOP_REL_ACT5",
)


def div(a, b):
    return float(a / b) if pd.notna(a) and pd.notna(b) and b != 0 else np.nan


def tstat(x: pd.Series) -> float:
    x = x.dropna()
    if len(x) < 3 or x.std(ddof=1) <= 0:
        return np.nan
    return float(x.mean() / (x.std(ddof=1) / math.sqrt(len(x))))


def main() -> None:
    returns, mcap, k200_by_date = base.load_basic()
    market_by_date = mu.load_market_by_date()
    ta = base.load_trading_amount()
    fwd = base.forward_returns(returns, base.HORIZON)
    liq = base.build_liquidity_features(ta, mcap)
    factor_files = {n: base.dated_files(p) for n, p in base.FACTORS.items()}

    # Precompute constituent-level history once; point-in-time universe membership is applied only at dt.
    ta_hist20 = ta.shift(1).rolling(20, min_periods=15).mean()
    ta_recent5 = ta.rolling(5, min_periods=4).mean()
    ta_prior20 = ta.shift(5).rolling(20, min_periods=15).mean()

    common = sorted(set(returns.index) & set(ta.index) & set(k200_by_date) & set(market_by_date))
    dates = [d for d in common if d >= base.START][::base.STEP]
    current = {}
    rows = []

    for dt in dates:
        if dt not in fwd.index:
            continue
        k = k200_by_date[dt]
        market = market_by_date[dt]
        raw_ta = ta.loc[dt]
        mc_full = mcap.loc[dt]
        lfull = {n: x.loc[dt] if dt in x.index else pd.Series(dtype=float) for n, x in liq.items()}

        kd = market.index[market.eq("KOSDAQ")]
        kp = market.index[market.eq("KOSPI")]
        kd_ta = raw_ta.reindex(kd).sum(min_count=1)
        kp_ta = raw_ta.reindex(kp).sum(min_count=1)
        kosdaq_share = div(kd_ta, kd_ta + kp_ta)
        factor_raw = {n: base.load_factor(files[dt]) for n, files in factor_files.items() if dt in files}

        for universe in mu.UNIVERSES:
            codes = mu.universe_codes(universe, k, market)
            y = fwd.loc[dt].reindex(codes)
            min_obs = 80 if universe == "K200" else 150
            if y.notna().sum() < min_obs:
                continue

            raw_u = lfull["raw"].reindex(codes)
            act1_u = lfull["act1"].reindex(codes)
            act5_u = lfull["act5"].reindex(codes)
            mc = mc_full.reindex(codes)
            lu = {n: s.reindex(codes) for n, s in lfull.items()}

            mkt_act1 = div(raw_u.sum(min_count=1), ta_hist20.loc[dt].reindex(codes).sum(min_count=1))
            mkt_act5 = div(ta_recent5.loc[dt].reindex(codes).sum(min_count=1), ta_prior20.loc[dt].reindex(codes).sum(min_count=1))
            mkt_act1_breadth = float((act1_u > 1).mean()) if act1_u.notna().any() else np.nan
            mkt_act5_breadth = float((act5_u > 1).mean()) if act5_u.notna().any() else np.nan
            total_u_ta = raw_u.sum(min_count=1)

            for factor, rf in factor_raw.items():
                raw = rf.reindex(codes)
                if raw.notna().sum() < max(50, min_obs // 2):
                    continue
                for direction, high_good in (("HIGH", True), ("LOW", False)):
                    fs = base.pct_rank(raw, high_good=high_good)
                    scores = mu.build_scores(fs, lu, mc)
                    valid = fs.dropna().sort_values(ascending=False)
                    top_k = min(len(valid), max(20, int(math.ceil(len(valid) * 0.10))))
                    ftop = valid.head(top_k).index
                    ftop_act5 = act5_u.reindex(ftop)
                    states = {
                        "MKT_ACT1": mkt_act1,
                        "MKT_ACT5": mkt_act5,
                        "MKT_ACT1_BREADTH": mkt_act1_breadth,
                        "MKT_ACT5_BREADTH": mkt_act5_breadth,
                        "KOSDAQ_TA_SHARE": kosdaq_share,
                        "FACTOR_TOP_ACT5_BREADTH": float((ftop_act5 > 1).mean()) if ftop_act5.notna().any() else np.nan,
                        "FACTOR_TOP_TA_SHARE": div(raw_u.reindex(ftop).sum(min_count=1), total_u_ta),
                        "FACTOR_TOP_REL_ACT5": float(ftop_act5.median() - act5_u.median()) if ftop_act5.notna().any() else np.nan,
                    }
                    for overlay in OVERLAYS:
                        for n in TOP_NS:
                            names = base.select_top(scores[overlay], n)
                            if len(names) < n:
                                continue
                            gross = float(y.reindex(names).mean())
                            for cost in COSTS:
                                key = (universe, factor, direction, overlay, n, cost)
                                turn = base.overlap_turnover(current.get(key, []), names, n)
                                r = {
                                    "date": dt, "universe": universe, "factor": factor, "direction": direction,
                                    "overlay": overlay, "top_n": n, "cost_bps": cost,
                                    "net": gross - turn * cost / 10000.0,
                                }
                                r.update(states)
                                rows.append(r)
                                current[key] = names

    p = pd.DataFrame(rows)
    p["date"] = pd.to_datetime(p.date)
    idx = ["date", "universe", "factor", "direction", "top_n", "cost_bps"]
    b = p[p.overlay == "BASE"].set_index(idx).net.rename("base_net")
    q = p[p.overlay != "BASE"].copy().join(b, on=idx)
    q["delta"] = q.net - q.base_net

    detail, spreads = [], []
    cfgcols = ["universe", "factor", "direction", "overlay", "top_n", "cost_bps"]
    for cfg, g0 in q.groupby(cfgcols):
        g0 = g0.sort_values("date")
        tr0 = g0[g0.date < SPLIT]
        if len(tr0) < 30:
            continue
        for state in STATE_VARS:
            xs = tr0[state].dropna()
            if len(xs) < 30 or xs.nunique() < 5:
                continue
            q1, q2 = xs.quantile([1/3, 2/3]).tolist()
            if not np.isfinite(q1) or not np.isfinite(q2) or q1 >= q2:
                continue
            g = g0[g0[state].notna()].copy()
            g["bin"] = np.where(g[state] <= q1, "LOW", np.where(g[state] >= q2, "HIGH", "MID"))
            for sample, mask in (("TRAIN", g.date < SPLIT), ("OOS", g.date >= SPLIT)):
                x = g[mask]
                vals = {}
                for bn in ("LOW", "MID", "HIGH"):
                    z = x[x.bin == bn]
                    if len(z) < 5:
                        continue
                    ann = float(z.delta.mean() * 252.0 / base.HORIZON)
                    vals[bn] = ann
                    detail.append({
                        "sample": sample, "universe": cfg[0], "factor": cfg[1], "direction": cfg[2],
                        "overlay": cfg[3], "top_n": cfg[4], "cost_bps": cfg[5], "state": state, "state_bin": bn,
                        "n_periods": len(z), "train_q1": q1, "train_q2": q2,
                        "annualized_arith_uplift": ann, "tstat": tstat(z.delta),
                        "positive_delta_share": float((z.delta > 0).mean()),
                    })
                if "LOW" in vals and "HIGH" in vals:
                    spreads.append({
                        "sample": sample, "universe": cfg[0], "factor": cfg[1], "direction": cfg[2],
                        "overlay": cfg[3], "top_n": cfg[4], "cost_bps": cfg[5], "state": state,
                        "high_minus_low": vals["HIGH"] - vals["LOW"],
                        "low_uplift": vals["LOW"], "high_uplift": vals["HIGH"],
                    })

    detail = pd.DataFrame(detail)
    spreads = pd.DataFrame(spreads)
    detail.to_csv(OUT / "conditional_bins.csv", index=False, encoding="utf-8-sig")
    spreads.to_csv(OUT / "conditional_spreads_by_config.csv", index=False, encoding="utf-8-sig")

    agg = []
    for (sample, universe, overlay, state), g in spreads.groupby(["sample", "universe", "overlay", "state"]):
        agg.append({
            "sample": sample, "universe": universe, "overlay": overlay, "state": state,
            "n_configs": len(g), "median_high_minus_low": float(g.high_minus_low.median()),
            "positive_spread_share": float((g.high_minus_low > 0).mean()),
            "median_low_uplift": float(g.low_uplift.median()), "median_high_uplift": float(g.high_uplift.median()),
        })
    agg = pd.DataFrame(agg)
    agg.to_csv(OUT / "conditional_spreads_aggregate.csv", index=False, encoding="utf-8-sig")

    pers = []
    for u in mu.UNIVERSES:
        for ov in ("ACT1_W10", "ACT5_KEEP_TOP70"):
            for st in STATE_VARS:
                tr = agg[(agg["sample"] == "TRAIN") & (agg.universe == u) & (agg.overlay == ov) & (agg.state == st)]
                oo = agg[(agg["sample"] == "OOS") & (agg.universe == u) & (agg.overlay == ov) & (agg.state == st)]
                if tr.empty or oo.empty:
                    continue
                tr, oo = tr.iloc[0], oo.iloc[0]
                pers.append({
                    "universe": u, "overlay": ov, "state": st,
                    "train_spread": tr.median_high_minus_low, "oos_spread": oo.median_high_minus_low,
                    "same_sign": bool(np.sign(tr.median_high_minus_low) == np.sign(oo.median_high_minus_low)),
                    "train_positive_share": tr.positive_spread_share, "oos_positive_share": oo.positive_spread_share,
                })
    pers = pd.DataFrame(pers)
    pers.to_csv(OUT / "state_persistence.csv", index=False, encoding="utf-8-sig")

    cross = pers.groupby(["overlay", "state"]).agg(
        universe_count=("universe", "size"), same_sign_share=("same_sign", "mean"),
        median_train_spread=("train_spread", "median"), median_oos_spread=("oos_spread", "median"),
        median_oos_positive_share=("oos_positive_share", "median"),
    ).reset_index()
    cross.to_csv(OUT / "cross_universe_state_summary.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# Conditional liquidity-state test", "",
        "State tercile thresholds are estimated on 2016-2022 TRAIN only and frozen into 2023+ OOS.",
        "H-L is the annualized arithmetic overlay uplift in HIGH state minus LOW state, always versus the same BASE.", "",
    ]
    for u in mu.UNIVERSES:
        lines += [f"## {u}", ""]
        z = pers[pers.universe == u]
        for ov in ("ACT1_W10", "ACT5_KEEP_TOP70"):
            zz = z[z.overlay == ov].copy()
            if zz.empty:
                continue
            zz["rank"] = zz.oos_spread.abs() * (0.5 + zz.oos_positive_share)
            lines.append(f"### {ov}")
            for _, r in zz.sort_values("rank", ascending=False).head(5).iterrows():
                lines.append(
                    f"- {r.state}: TRAIN H-L {r.train_spread:+.2%}, OOS H-L {r.oos_spread:+.2%}; "
                    f"OOS positive-config {r.oos_positive_share:.0%}; same-sign={r.same_sign}"
                )
            lines.append("")

    lines += ["# Cross-universe", ""]
    for ov in ("ACT1_W10", "ACT5_KEEP_TOP70"):
        zz = cross[cross.overlay == ov].copy()
        zz["rank"] = zz.same_sign_share * zz.median_oos_spread.abs() * (0.5 + zz.median_oos_positive_share)
        lines.append(f"## {ov}")
        for _, r in zz.sort_values("rank", ascending=False).iterrows():
            lines.append(
                f"- {r.state}: same-sign {r.same_sign_share:.0%}; median TRAIN H-L {r.median_train_spread:+.2%}; "
                f"median OOS H-L {r.median_oos_spread:+.2%}; OOS positive-config {r.median_oos_positive_share:.0%}"
            )
        lines.append("")

    (OUT / "CONDITIONAL_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print((OUT / "CONDITIONAL_SUMMARY.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
