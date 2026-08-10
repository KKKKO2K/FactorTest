from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

# Reuse point-in-time loaders and universe definitions from the liquidity research.
import sys
HERE = Path(__file__).resolve().parent
LIQ_DIR = HERE.parent / "liquidity_cross_factor"
sys.path.insert(0, str(LIQ_DIR))
import run_cross_factor_liquidity as base
import run_multi_universe_liquidity as mu

OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

SPLIT = base.OOS_START
STEP = 5
FACTOR_HOLD = 5
Q = 0.20

# Canonical/economic factor directions. This is deliberately not selected on OOS performance.
DIRECTIONS = {
    "OP12_REV": True,
    "OPFY1_REV": True,
    "PBR12MF": False,
    "PER12MF": False,
    "MOM1M": True,
    "MOM12_1": True,
    "PRIVATE_FLOW": True,
    "FOREIGN_FLOW": True,
}

FACTOR_UNIVERSES = mu.UNIVERSES
MARKET_TARGETS = mu.UNIVERSES
HORIZONS = (1, 5, 20)

STATE_VARS = (
    "LS_BREADTH_1P",
    "LS_BREADTH_4P",
    "ABS_BREADTH_1P",
    "ABS_BREADTH_4P",
    "AVG_CORR_12P",
    "AVG_CORR_24P",
    "DISPERSION_LS_4P",
    "LEADER_STRENGTH_12P",
    "LEADER_CORRECTION_1P",
    "OTHERS_LS_BREADTH_4P",
    "OTHERS_ABS_BREADTH_1P",
    "OTHERS_ABS_BREADTH_4P",
    "ORTHOGONAL_ABS_BREADTH_1P",
    # Liquidity variables are supplemental; factor-only states above remain the core model.
    "MKT_ACT5_BREADTH",
    "MKT_ACT1_BREADTH",
    "KOSDAQ_TA_SHARE",
    "FACTOR_TOP_ACT5_BREADTH_MEAN",
)


def compound(x: pd.Series) -> float:
    x = x.dropna()
    return float((1.0 + x).prod() - 1.0) if len(x) else np.nan


def row_compound(df: pd.DataFrame, window: int) -> pd.DataFrame:
    return (1.0 + df).rolling(window, min_periods=window).apply(np.prod, raw=True) - 1.0


def avg_pairwise_corr(x: pd.DataFrame) -> float:
    x = x.dropna(axis=1, how="all")
    if x.shape[1] < 2 or len(x) < 5:
        return np.nan
    c = x.corr(min_periods=max(4, len(x) // 2))
    vals = c.to_numpy()[np.triu_indices(c.shape[0], 1)]
    vals = vals[np.isfinite(vals)]
    return float(vals.mean()) if len(vals) else np.nan


def diff_tstat(a: pd.Series, b: pd.Series) -> float:
    a, b = a.dropna(), b.dropna()
    if len(a) < 3 or len(b) < 3:
        return np.nan
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = math.sqrt(va / len(a) + vb / len(b))
    return float((a.mean() - b.mean()) / se) if se > 0 else np.nan


def mean_tstat(x: pd.Series) -> float:
    x = x.dropna()
    if len(x) < 3:
        return np.nan
    sd = x.std(ddof=1)
    return float(x.mean() / (sd / math.sqrt(len(x)))) if sd > 0 else np.nan


def make_market_returns(
    returns: pd.DataFrame,
    mcap: pd.DataFrame,
    k200_by_date: dict[pd.Timestamp, pd.Series],
    market_by_date: dict[pd.Timestamp, pd.Series],
) -> pd.DataFrame:
    rows = []
    dates = list(returns.index)
    for i in range(1, len(dates)):
        dt, prev = dates[i], dates[i - 1]
        if prev not in k200_by_date or prev not in market_by_date:
            continue
        k, market = k200_by_date[prev], market_by_date[prev]
        for u in MARKET_TARGETS:
            codes = mu.universe_codes(u, k, market)
            r = returns.loc[dt].reindex(codes)
            w = mcap.loc[prev].reindex(codes)
            z = pd.concat([r.rename("r"), w.rename("w")], axis=1).dropna()
            z = z[z.w > 0]
            if len(z) < (60 if u == "K200" else 100):
                continue
            ret = float((z.r * z.w).sum() / z.w.sum())
            rows.append({"date": dt, "target": u, "return": ret})
    long = pd.DataFrame(rows)
    return long.pivot(index="date", columns="target", values="return").sort_index()


def forward_market(market_returns: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(market_returns.clip(lower=-0.999999))
    acc = sum(logs.shift(-i) for i in range(1, h + 1))
    return np.expm1(acc)


def build_factor_period_returns(
    returns: pd.DataFrame,
    mcap: pd.DataFrame,
    k200_by_date: dict[pd.Timestamp, pd.Series],
    market_by_date: dict[pd.Timestamp, pd.Series],
    ta: pd.DataFrame,
    liq_frames: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    fwd5 = base.forward_returns(returns, FACTOR_HOLD)
    factor_files = {n: base.dated_files(p) for n, p in base.FACTORS.items()}
    common = sorted(set(returns.index) & set(k200_by_date) & set(market_by_date))
    signal_dates = [d for d in common if d >= base.START][::STEP]

    factor_rows = []
    liq_rows = []
    leader_name_rows = []

    for i, dt in enumerate(signal_dates[:-1]):
        end_dt = signal_dates[i + 1]
        if dt not in fwd5.index or dt not in ta.index:
            continue
        k, market = k200_by_date[dt], market_by_date[dt]
        y_full = fwd5.loc[dt]
        raw_ta = ta.loc[dt]
        act1_full = liq_frames["act1"].loc[dt] if dt in liq_frames["act1"].index else pd.Series(dtype=float)
        act5_full = liq_frames["act5"].loc[dt] if dt in liq_frames["act5"].index else pd.Series(dtype=float)

        kd = market.index[market.eq("KOSDAQ")]
        kp = market.index[market.eq("KOSPI")]
        kd_ta = raw_ta.reindex(kd).sum(min_count=1)
        kp_ta = raw_ta.reindex(kp).sum(min_count=1)
        kosdaq_share = float(kd_ta / (kd_ta + kp_ta)) if pd.notna(kd_ta + kp_ta) and (kd_ta + kp_ta) != 0 else np.nan

        factor_raw = {n: base.load_factor(files[dt]) for n, files in factor_files.items() if dt in files}

        for u in FACTOR_UNIVERSES:
            codes = mu.universe_codes(u, k, market)
            min_obs = 80 if u == "K200" else 150
            if y_full.reindex(codes).notna().sum() < min_obs:
                continue
            act1_u = act1_full.reindex(codes)
            act5_u = act5_full.reindex(codes)
            factor_top_liq = []

            for factor, raw_full in factor_raw.items():
                raw = raw_full.reindex(codes)
                y = y_full.reindex(codes)
                good_high = DIRECTIONS.get(factor, True)
                score = base.pct_rank(raw, high_good=good_high)
                z = pd.concat([score.rename("score"), y.rename("y")], axis=1).dropna().sort_values("score", ascending=False)
                n = int(math.floor(len(z) * Q))
                if n < 10:
                    continue
                top = z.head(n)
                bot = z.tail(n)
                top_abs = float(top.y.mean())
                ls = float(top.y.mean() - bot.y.mean())
                factor_rows.append({
                    "signal_date": dt, "date": end_dt, "universe": u, "factor": factor,
                    "ls_return": ls, "top_abs_return": top_abs, "n_side": n,
                })

                # Current factor-winner trading-activity support, available at signal date dt.
                top_codes = score.dropna().sort_values(ascending=False).head(max(20, int(math.ceil(score.notna().sum() * 0.10)))).index
                aa = act5_u.reindex(top_codes)
                if aa.notna().any():
                    factor_top_liq.append(float((aa > 1).mean()))

            liq_rows.append({
                "date": dt, "universe": u,
                "MKT_ACT5_BREADTH": float((act5_u > 1).mean()) if act5_u.notna().any() else np.nan,
                "MKT_ACT1_BREADTH": float((act1_u > 1).mean()) if act1_u.notna().any() else np.nan,
                "KOSDAQ_TA_SHARE": kosdaq_share,
                "FACTOR_TOP_ACT5_BREADTH_MEAN": float(np.mean(factor_top_liq)) if factor_top_liq else np.nan,
            })

    factor_long = pd.DataFrame(factor_rows)
    liquidity_states = pd.DataFrame(liq_rows).drop_duplicates(["date", "universe"])
    return factor_long, liquidity_states, pd.DataFrame(leader_name_rows)


def build_states(factor_long: pd.DataFrame, liquidity_states: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    state_rows = []
    corr_rows = []

    for u, gu in factor_long.groupby("universe"):
        ls = gu.pivot(index="date", columns="factor", values="ls_return").sort_index()
        ab = gu.pivot(index="date", columns="factor", values="top_abs_return").sort_index()
        ls4 = row_compound(ls, 4)
        ls12 = row_compound(ls, 12)
        ab4 = row_compound(ab, 4)

        # Correlation matrices by sample for direct factor-correlation inspection.
        for sample, mask in (("TRAIN", ls.index < SPLIT), ("OOS", ls.index >= SPLIT)):
            c = ls.loc[mask].corr(min_periods=20)
            for a in c.columns:
                for b in c.columns:
                    corr_rows.append({"universe": u, "sample": sample, "factor_a": a, "factor_b": b, "corr": c.loc[a, b]})

        for pos, dt in enumerate(ls.index):
            if pos < 12:
                continue
            hist12 = ls.iloc[max(0, pos - 11): pos + 1]
            hist24 = ls.iloc[max(0, pos - 23): pos + 1]
            r12 = ls12.loc[dt]
            r4 = ls4.loc[dt]
            a4 = ab4.loc[dt]
            cur_ls = ls.loc[dt]
            cur_ab = ab.loc[dt]
            if r12.notna().sum() < 5:
                continue

            leader = r12.idxmax()
            leader_strength = float(r12[leader] - r12.median())
            leader_corr = hist12.corr()[leader] if leader in hist12.columns else pd.Series(dtype=float)
            others = [f for f in ls.columns if f != leader]
            orth = [f for f in others if f in leader_corr.index and pd.notna(leader_corr[f]) and leader_corr[f] < 0.30]

            row = {
                "date": dt, "universe": u, "leader_factor": leader,
                "LS_BREADTH_1P": float((cur_ls > 0).mean()),
                "LS_BREADTH_4P": float((r4 > 0).mean()),
                "ABS_BREADTH_1P": float((cur_ab > 0).mean()),
                "ABS_BREADTH_4P": float((a4 > 0).mean()),
                "AVG_CORR_12P": avg_pairwise_corr(hist12),
                "AVG_CORR_24P": avg_pairwise_corr(hist24),
                "DISPERSION_LS_4P": float(r4.std(ddof=1)),
                "LEADER_STRENGTH_12P": leader_strength,
                "LEADER_CORRECTION_1P": float(cur_ls.get(leader, np.nan)),
                "OTHERS_LS_BREADTH_4P": float((r4.reindex(others) > 0).mean()) if others else np.nan,
                "OTHERS_ABS_BREADTH_1P": float((cur_ab.reindex(others) > 0).mean()) if others else np.nan,
                "OTHERS_ABS_BREADTH_4P": float((a4.reindex(others) > 0).mean()) if others else np.nan,
                "ORTHOGONAL_ABS_BREADTH_1P": float((cur_ab.reindex(orth) > 0).mean()) if orth else np.nan,
                "n_orthogonal": len(orth),
            }
            state_rows.append(row)

    states = pd.DataFrame(state_rows)
    states = states.merge(liquidity_states, on=["date", "universe"], how="left")
    return states, pd.DataFrame(corr_rows)


def state_bin_tests(states: pd.DataFrame, market_fwd: dict[int, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    bin_rows, spread_rows = [], []
    for fu, gu in states.groupby("universe"):
        train = gu[gu.date < SPLIT]
        for st in STATE_VARS:
            xs = train[st].dropna()
            if len(xs) < 30 or xs.nunique() < 5:
                continue
            q1, q2 = xs.quantile([1/3, 2/3]).tolist()
            if not np.isfinite(q1) or not np.isfinite(q2) or q1 >= q2:
                continue
            g = gu[gu[st].notna()].copy()
            g["bin"] = np.where(g[st] <= q1, "LOW", np.where(g[st] >= q2, "HIGH", "MID"))

            for target in MARKET_TARGETS:
                for h in HORIZONS:
                    if target not in market_fwd[h].columns:
                        continue
                    g["fwd"] = g.date.map(market_fwd[h][target])
                    for sample, mask in (("TRAIN", g.date < SPLIT), ("OOS", g.date >= SPLIT)):
                        x = g[mask & g.fwd.notna()]
                        vals = {}
                        for bn in ("LOW", "MID", "HIGH"):
                            z = x[x.bin == bn].fwd.dropna()
                            if len(z) < 8:
                                continue
                            vals[bn] = z
                            bin_rows.append({
                                "sample": sample, "factor_universe": fu, "market_target": target,
                                "horizon": h, "state": st, "state_bin": bn,
                                "train_q1": q1, "train_q2": q2, "n": len(z),
                                "mean_fwd_return": float(z.mean()), "median_fwd_return": float(z.median()),
                                "positive_market_share": float((z > 0).mean()), "mean_tstat": mean_tstat(z),
                            })
                        if "LOW" in vals and "HIGH" in vals:
                            spread_rows.append({
                                "sample": sample, "factor_universe": fu, "market_target": target,
                                "horizon": h, "state": st,
                                "high_minus_low": float(vals["HIGH"].mean() - vals["LOW"].mean()),
                                "diff_tstat": diff_tstat(vals["HIGH"], vals["LOW"]),
                                "low_mean": float(vals["LOW"].mean()), "high_mean": float(vals["HIGH"].mean()),
                                "low_positive_share": float((vals["LOW"] > 0).mean()),
                                "high_positive_share": float((vals["HIGH"] > 0).mean()),
                                "n_low": len(vals["LOW"]), "n_high": len(vals["HIGH"]),
                            })
    return pd.DataFrame(bin_rows), pd.DataFrame(spread_rows)


def leader_event_tests(states: pd.DataFrame, market_fwd: dict[int, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    support_vars = ("OTHERS_ABS_BREADTH_1P", "OTHERS_ABS_BREADTH_4P", "ORTHOGONAL_ABS_BREADTH_1P", "ABS_BREADTH_1P")
    for fu, gu in states.groupby("universe"):
        tr = gu[gu.date < SPLIT]
        strength_cut = tr.LEADER_STRENGTH_12P.quantile(2/3)
        support_cuts = {s: tr[s].median() for s in support_vars}
        # Strong prior leader + current factor-spread correction. Zero has economic meaning here.
        ge = gu[(gu.LEADER_STRENGTH_12P >= strength_cut) & (gu.LEADER_CORRECTION_1P < 0)].copy()
        for s in support_vars:
            cut = support_cuts[s]
            if pd.isna(cut):
                continue
            ge["support"] = np.where(ge[s] >= cut, "HIGH_SUPPORT", "LOW_SUPPORT")
            for target in MARKET_TARGETS:
                for h in HORIZONS:
                    if target not in market_fwd[h].columns:
                        continue
                    ge["fwd"] = ge.date.map(market_fwd[h][target])
                    for sample, mask in (("TRAIN", ge.date < SPLIT), ("OOS", ge.date >= SPLIT)):
                        x = ge[mask & ge.fwd.notna()]
                        hi = x[x.support == "HIGH_SUPPORT"].fwd
                        lo = x[x.support == "LOW_SUPPORT"].fwd
                        if len(hi) < 5 or len(lo) < 5:
                            continue
                        rows.append({
                            "sample": sample, "factor_universe": fu, "market_target": target, "horizon": h,
                            "support_state": s, "leader_strength_cut": strength_cut, "support_cut": cut,
                            "n_high": len(hi), "n_low": len(lo),
                            "high_support_mean": float(hi.mean()), "low_support_mean": float(lo.mean()),
                            "high_minus_low": float(hi.mean() - lo.mean()), "diff_tstat": diff_tstat(hi, lo),
                            "high_positive_share": float((hi > 0).mean()), "low_positive_share": float((lo > 0).mean()),
                        })
    return pd.DataFrame(rows)


def summarize(factor_long: pd.DataFrame, states: pd.DataFrame, corr_long: pd.DataFrame,
              spreads: pd.DataFrame, events: pd.DataFrame) -> str:
    lines = [
        "# Factor Regime v1", "",
        "Method: canonical-direction factor portfolios; top-minus-bottom 20% factor spread and top-20% absolute return,",
        "sampled every 5 trading days with non-overlapping 5D factor-return periods. Regime state at t only uses factor returns realized through t.",
        "State terciles are fixed on 2016-2022 TRAIN and applied unchanged to 2023+ OOS. Market targets use prior-day market-cap weights.",
        "", "## Factor correlation change", "",
    ]

    # Average off-diagonal factor correlations by universe/sample.
    c = corr_long[corr_long.factor_a != corr_long.factor_b].groupby(["universe", "sample"]).corr.mean().reset_index()
    for u in FACTOR_UNIVERSES:
        tr = c[(c.universe == u) & (c["sample"] == "TRAIN")]
        oo = c[(c.universe == u) & (c["sample"] == "OOS")]
        if not tr.empty and not oo.empty:
            lines.append(f"- {u}: avg pairwise corr TRAIN {tr.iloc[0]['corr']:+.2f} -> OOS {oo.iloc[0]['corr']:+.2f}")

    lines += ["", "## OOS state signals: same-universe market target", ""]
    # Require same sign TRAIN/OOS and show strongest OOS H-L for each universe/horizon.
    if not spreads.empty:
        for u in FACTOR_UNIVERSES:
            lines += [f"### {u}", ""]
            for h in HORIZONS:
                tr = spreads[(spreads["sample"] == "TRAIN") & (spreads.factor_universe == u) & (spreads.market_target == u) & (spreads.horizon == h)]
                oo = spreads[(spreads["sample"] == "OOS") & (spreads.factor_universe == u) & (spreads.market_target == u) & (spreads.horizon == h)]
                m = tr[["state", "high_minus_low", "diff_tstat"]].merge(
                    oo[["state", "high_minus_low", "diff_tstat", "low_mean", "high_mean", "low_positive_share", "high_positive_share"]],
                    on="state", suffixes=("_train", "_oos"))
                if m.empty:
                    continue
                m["same_sign"] = np.sign(m.high_minus_low_train) == np.sign(m.high_minus_low_oos)
                m["score"] = m.same_sign.astype(float) * m.high_minus_low_oos.abs()
                lines.append(f"Horizon {h}D:")
                for _, r in m.sort_values("score", ascending=False).head(5).iterrows():
                    lines.append(
                        f"- {r.state}: TRAIN H-L {r.high_minus_low_train:+.2%}, OOS H-L {r.high_minus_low_oos:+.2%} "
                        f"(t={r.diff_tstat_oos:+.2f}); low/high market mean {r.low_mean:+.2%}/{r.high_mean:+.2%}; same-sign={bool(r.same_sign)}"
                    )
            lines.append("")

    lines += ["## Strong-leader correction events", "",
              "Event = trailing 60D factor leader strength in TRAIN-defined top tercile AND leader's latest 5D spread return < 0.",
              "Question: does positive absolute performance in the other factors change subsequent market returns?", ""]
    if not events.empty:
        for u in FACTOR_UNIVERSES:
            z = events[(events["sample"] == "OOS") & (events.factor_universe == u) & (events.market_target == u)]
            if z.empty:
                continue
            lines.append(f"### {u}")
            for _, r in z.sort_values("high_minus_low", key=lambda s: s.abs(), ascending=False).head(8).iterrows():
                lines.append(
                    f"- {r.support_state}, {int(r.horizon)}D: high-support {r.high_support_mean:+.2%} vs low-support {r.low_support_mean:+.2%}; "
                    f"diff {r.high_minus_low:+.2%}, t={r.diff_tstat:+.2f}, n={int(r.n_high)}/{int(r.n_low)}"
                )
            lines.append("")

    lines += ["## Interpretation guardrails", "",
              "- This is a regime-screening study, not a production timing model.",
              "- Overlapping 20D forward market returns make naïve t-stats optimistic; use them for ranking evidence, not formal significance.",
              "- Next step should retain only TRAIN/OOS sign-stable states and test a small predeclared composite out of sample.", ""]
    return "\n".join(lines) + "\n"


def main() -> None:
    returns, mcap, k200_by_date = base.load_basic()
    market_by_date = mu.load_market_by_date()
    ta = base.load_trading_amount()
    liq_frames = base.build_liquidity_features(ta, mcap)

    market_returns = make_market_returns(returns, mcap, k200_by_date, market_by_date)
    market_returns.to_csv(OUT / "market_daily_returns.csv", encoding="utf-8-sig")
    market_fwd = {h: forward_market(market_returns, h) for h in HORIZONS}

    factor_long, liq_states, _ = build_factor_period_returns(returns, mcap, k200_by_date, market_by_date, ta, liq_frames)
    factor_long.to_csv(OUT / "factor_5d_returns.csv", index=False, encoding="utf-8-sig")
    liq_states.to_csv(OUT / "liquidity_states.csv", index=False, encoding="utf-8-sig")

    states, corr_long = build_states(factor_long, liq_states)
    states.to_csv(OUT / "regime_states.csv", index=False, encoding="utf-8-sig")
    corr_long.to_csv(OUT / "factor_correlation_long.csv", index=False, encoding="utf-8-sig")

    bins, spreads = state_bin_tests(states, market_fwd)
    bins.to_csv(OUT / "state_tercile_results.csv", index=False, encoding="utf-8-sig")
    spreads.to_csv(OUT / "state_high_low_spreads.csv", index=False, encoding="utf-8-sig")

    events = leader_event_tests(states, market_fwd)
    events.to_csv(OUT / "leader_correction_events.csv", index=False, encoding="utf-8-sig")

    text = summarize(factor_long, states, corr_long, spreads, events)
    (OUT / "RESEARCH_SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
