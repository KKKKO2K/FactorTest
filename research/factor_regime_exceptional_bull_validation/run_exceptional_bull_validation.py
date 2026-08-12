from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FULL = ROOT / "research" / "factor_regime_full_state_map" / "results"
ABS = ROOT / "research" / "factor_regime_absolute_states" / "results"
REG = ROOT / "research" / "factor_regime_v1" / "results"
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

TRAIN_START = pd.Timestamp("2016-01-01")
STATIC_SPLIT = pd.Timestamp("2023-01-01")
MAIN_CUT = "Q33"
FAMILIES = ("MOMENTUM", "REVISION", "VALUE", "FLOW")
FAMILY_PAIRS = list(itertools.combinations(FAMILIES, 2))
MIN_CELL = 5          # descriptive short-period cells
MIN_CONTRAST = 8      # keep prior inferential minimum for two-sided contrasts

PERIODS = {
    "DISCOVERY_2016_2022": (pd.Timestamp("2016-01-01"), pd.Timestamp("2023-01-01")),
    "NORMAL_2023_2024": (pd.Timestamp("2023-01-01"), pd.Timestamp("2025-01-01")),
    "EXCEPTIONAL_2025": (pd.Timestamp("2025-01-01"), pd.Timestamp("2026-01-01")),
    "EXCEPTIONAL_2026_YTD": (pd.Timestamp("2026-01-01"), pd.Timestamp("2027-01-01")),
    "EXCEPTIONAL_2025_2026": (pd.Timestamp("2025-01-01"), pd.Timestamp("2027-01-01")),
    "POST_2023_ALL": (pd.Timestamp("2023-01-01"), pd.Timestamp("2027-01-01")),
}

BREADTH_VARS = [
    "RELATIVE_WORKING_BREADTH",
    "ABS_CONFIRMED_BREADTH",
    "DEFENSIVE_WORKING_BREADTH",
    "BEARISH_REVERSE_BREADTH",
    "POSITIVE_ABS_BREADTH",
]


def period_mask(dates: pd.Series, name: str) -> pd.Series:
    lo, hi = PERIODS[name]
    return (dates >= lo) & (dates < hi)


def forward_market(market: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(market.clip(lower=-0.999999))
    acc = sum(logs.shift(-i) for i in range(1, h + 1))
    return np.expm1(acc)


def trailing_market(market: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(market.clip(lower=-0.999999))
    return np.expm1(logs.rolling(h, min_periods=h).sum())


def load_inputs():
    states = pd.read_csv(FULL / "family_states_static.csv")
    states["date"] = pd.to_datetime(states["date"])
    states = states[states.cut_name == MAIN_CUT].copy()

    prim = pd.read_csv(FULL / "family_primitives.csv")
    prim["date"] = pd.to_datetime(prim["date"])

    breadth = pd.read_csv(ABS / "refined_breadth_panel.csv")
    breadth["date"] = pd.to_datetime(breadth["date"])

    leader = pd.read_csv(FULL / "generalized_leader_rotation_events.csv")
    leader["date"] = pd.to_datetime(leader["date"])

    market = pd.read_csv(REG / "market_daily_returns.csv", index_col=0)
    market.index = pd.to_datetime(market.index)
    market = market.sort_index()
    return states, prim, breadth, leader, market


def build_market_context(states: pd.DataFrame, market: pd.DataFrame):
    fwd = {h: forward_market(market, h) for h in (1, 5, 20)}
    trail = {h: trailing_market(market, h) for h in (20, 60)}
    state_dates = states[["date", "universe"]].drop_duplicates().sort_values(["universe", "date"])
    rows, thresholds = [], []
    for u, g in state_dates.groupby("universe"):
        if u not in market.columns:
            continue
        z = g.copy()
        for h in (1, 5, 20):
            z[f"mkt_fwd_{h}d"] = z.date.map(fwd[h][u])
        for h in (20, 60):
            z[f"mkt_trail_{h}d"] = z.date.map(trail[h][u])
        tr = z[(z.date >= TRAIN_START) & (z.date < STATIC_SPLIT)]
        cuts = {}
        for h in (20, 60):
            q = tr[f"mkt_trail_{h}d"].dropna().quantile([1/3, 2/3]).tolist()
            q1, q2 = (float(q[0]), float(q[1])) if len(q) == 2 else (np.nan, np.nan)
            cuts[h] = (q1, q2)
            thresholds.append({"universe": u, "horizon": h, "q1": q1, "q2": q2, "train_n": int(tr[f"mkt_trail_{h}d"].notna().sum())})
            if np.isfinite(q1) and np.isfinite(q2) and q1 < q2:
                x = z[f"mkt_trail_{h}d"]
                z[f"prior{h}_bin"] = np.where(x <= q1, "LOW", np.where(x >= q2, "HIGH", "MID"))
            else:
                z[f"prior{h}_bin"] = np.nan
        rows.append(z)
    return pd.concat(rows, ignore_index=True), pd.DataFrame(thresholds)


def summarize_market_baseline(ctx: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for u, g in ctx.groupby("universe"):
        for p in PERIODS:
            z = g[period_mask(g.date, p) & g.mkt_fwd_20d.notna()]
            if z.empty:
                continue
            rows.append({
                "universe": u, "period": p, "n": len(z),
                "trail20_mean": float(z.mkt_trail_20d.mean()),
                "trail60_mean": float(z.mkt_trail_60d.mean()),
                "fwd5_mean": float(z.mkt_fwd_5d.mean()),
                "fwd20_mean": float(z.mkt_fwd_20d.mean()),
                "fwd20_median": float(z.mkt_fwd_20d.median()),
                "fwd20_positive_share": float((z.mkt_fwd_20d > 0).mean()),
                "prior60_high_share": float((z.prior60_bin == "HIGH").mean()),
            })
    return pd.DataFrame(rows)


def prepare_pair_obs(states: pd.DataFrame, prim: pd.DataFrame, ctx: pd.DataFrame, fa: str, fb: str) -> pd.DataFrame:
    cols = ["date", "universe", "state6", "top_20d", "spread_20d", "member_same_sign_20d"]
    a = states[states.family == fa][cols].rename(columns={
        "state6": "state_a", "top_20d": "top20_a", "spread_20d": "spread20_a", "member_same_sign_20d": "agree_a"})
    b = states[states.family == fb][cols].rename(columns={
        "state6": "state_b", "top_20d": "top20_b", "spread_20d": "spread20_b", "member_same_sign_20d": "agree_b"})
    x = a.merge(b, on=["date", "universe"], how="inner")
    pm = prim[["date", "universe", "family", "top_fwd_20d", "spread_fwd_20d"]]
    pa = pm[pm.family == fa].drop(columns="family").rename(columns={"top_fwd_20d": "a_top_fwd20", "spread_fwd_20d": "a_spread_fwd20"})
    pb = pm[pm.family == fb].drop(columns="family").rename(columns={"top_fwd_20d": "b_top_fwd20", "spread_fwd_20d": "b_spread_fwd20"})
    x = x.merge(pa, on=["date", "universe"], how="left").merge(pb, on=["date", "universe"], how="left")
    return x.merge(ctx, on=["date", "universe"], how="left")


def build_pair_period_results(states: pd.DataFrame, prim: pd.DataFrame, ctx: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cell_rows, contrast_rows, conditioned_rows = [], [], []
    for fa, fb in FAMILY_PAIRS:
        x = prepare_pair_obs(states, prim, ctx, fa, fb)
        for u, g in x.groupby("universe"):
            for p in PERIODS:
                s = g[period_mask(g.date, p) & g.mkt_fwd_20d.notna()].copy()
                if s.empty:
                    continue
                sig = s[(s.state_a == "W+") & (s.state_b == "W+")]
                oth = s[~((s.state_a == "W+") & (s.state_b == "W+"))]
                if len(sig) >= MIN_CELL:
                    cell_rows.append({
                        "universe": u, "period": p, "family_a": fa, "family_b": fb, "family_pair": f"{fa}_X_{fb}",
                        "n_signal": len(sig), "n_other": len(oth),
                        "signal_fwd5": float(sig.mkt_fwd_5d.mean()), "signal_fwd20": float(sig.mkt_fwd_20d.mean()),
                        "signal_fwd20_median": float(sig.mkt_fwd_20d.median()),
                        "signal_positive_share": float((sig.mkt_fwd_20d > 0).mean()),
                        "other_fwd20": float(oth.mkt_fwd_20d.mean()) if len(oth) else np.nan,
                        "diff_vs_other": float(sig.mkt_fwd_20d.mean() - oth.mkt_fwd_20d.mean()) if len(oth) else np.nan,
                        "unconditional_fwd20": float(s.mkt_fwd_20d.mean()),
                        "excess_vs_unconditional": float(sig.mkt_fwd_20d.mean() - s.mkt_fwd_20d.mean()),
                        "signal_prior20": float(sig.mkt_trail_20d.mean()), "signal_prior60": float(sig.mkt_trail_60d.mean()),
                        "signal_prior60_high_share": float((sig.prior60_bin == "HIGH").mean()),
                        "agree_a": float(sig.agree_a.mean()), "agree_b": float(sig.agree_b.mean()),
                    })

                # Same predeclared confirmation contrast, evaluated in both directions.
                for anchor, other, ac, oc in ((fa, fb, "state_a", "state_b"), (fb, fa, "state_b", "state_a")):
                    z = s[s[ac] == "W+"]
                    left = z[z[oc] == "W+"]
                    right = z[z[oc].isin(["N+", "N-"])]
                    if len(left) >= MIN_CONTRAST and len(right) >= MIN_CONTRAST:
                        contrast_rows.append({
                            "universe": u, "period": p, "family_pair": f"{fa}_X_{fb}", "anchor_family": anchor, "other_family": other,
                            "contrast": "CONFIRM_WPLUS_VS_NEUTRAL_WHEN_ANCHOR_WPLUS",
                            "n_wplus": len(left), "n_neutral": len(right),
                            "wplus_fwd20": float(left.mkt_fwd_20d.mean()), "neutral_fwd20": float(right.mkt_fwd_20d.mean()),
                            "diff": float(left.mkt_fwd_20d.mean() - right.mkt_fwd_20d.mean()),
                            "wplus_prior60": float(left.mkt_trail_60d.mean()), "neutral_prior60": float(right.mkt_trail_60d.mean()),
                        })

            # Prior-market-state conditioned comparison: 2023-24 vs exceptional 2025-26.
            for p in ("NORMAL_2023_2024", "EXCEPTIONAL_2025_2026"):
                s = g[period_mask(g.date, p) & g.mkt_fwd_20d.notna()].copy()
                for hbin in ("LOW", "MID", "HIGH"):
                    z = s[s.prior60_bin == hbin]
                    sig = z[(z.state_a == "W+") & (z.state_b == "W+")]
                    oth = z[~((z.state_a == "W+") & (z.state_b == "W+"))]
                    if len(sig) >= MIN_CELL and len(oth) >= MIN_CELL:
                        conditioned_rows.append({
                            "universe": u, "period": p, "prior60_bin": hbin, "family_pair": f"{fa}_X_{fb}",
                            "n_signal": len(sig), "n_other": len(oth),
                            "signal_fwd20": float(sig.mkt_fwd_20d.mean()), "other_fwd20": float(oth.mkt_fwd_20d.mean()),
                            "diff_vs_other": float(sig.mkt_fwd_20d.mean() - oth.mkt_fwd_20d.mean()),
                            "signal_prior60": float(sig.mkt_trail_60d.mean()),
                        })
    return pd.DataFrame(cell_rows), pd.DataFrame(contrast_rows), pd.DataFrame(conditioned_rows)


def attach_context(df: pd.DataFrame, ctx: pd.DataFrame) -> pd.DataFrame:
    drop_cols = [c for c in df.columns if c.startswith("mkt_") or c.startswith("prior")]
    z = df.drop(columns=drop_cols, errors="ignore")
    return z.merge(ctx, on=["date", "universe"], how="left")


def build_breadth_results(breadth: pd.DataFrame, ctx: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    b = attach_context(breadth, ctx)
    threshold_rows, rows, cond_rows = [], [], []
    for u, g in b.groupby("universe"):
        tr = g[(g.date >= TRAIN_START) & (g.date < STATIC_SPLIT)]
        cuts = {}
        for v in BREADTH_VARS:
            if v not in g.columns:
                continue
            q1, q2 = tr[v].dropna().quantile([1/3, 2/3]).tolist()
            if not (np.isfinite(q1) and np.isfinite(q2) and q1 < q2):
                continue
            cuts[v] = (float(q1), float(q2))
            threshold_rows.append({"universe": u, "state": v, "q1": q1, "q2": q2, "train_n": int(tr[v].notna().sum())})
        for v, (q1, q2) in cuts.items():
            gg = g.copy()
            gg["breadth_bin"] = np.where(gg[v] <= q1, "LOW", np.where(gg[v] >= q2, "HIGH", "MID"))
            for p in PERIODS:
                s = gg[period_mask(gg.date, p) & gg.mkt_fwd_20d.notna()]
                lo, hi = s[s.breadth_bin == "LOW"], s[s.breadth_bin == "HIGH"]
                if len(lo) >= MIN_CELL and len(hi) >= MIN_CELL:
                    rows.append({
                        "universe": u, "period": p, "state": v, "n_low": len(lo), "n_high": len(hi),
                        "low_fwd20": float(lo.mkt_fwd_20d.mean()), "high_fwd20": float(hi.mkt_fwd_20d.mean()),
                        "high_minus_low": float(hi.mkt_fwd_20d.mean() - lo.mkt_fwd_20d.mean()),
                        "high_prior60": float(hi.mkt_trail_60d.mean()), "low_prior60": float(lo.mkt_trail_60d.mean()),
                        "high_prior60_high_share": float((hi.prior60_bin == "HIGH").mean()),
                    })
            if v in ("RELATIVE_WORKING_BREADTH", "ABS_CONFIRMED_BREADTH"):
                for p in ("NORMAL_2023_2024", "EXCEPTIONAL_2025_2026"):
                    s = gg[period_mask(gg.date, p) & gg.mkt_fwd_20d.notna()]
                    for hbin in ("LOW", "MID", "HIGH"):
                        z = s[s.prior60_bin == hbin]
                        lo, hi = z[z.breadth_bin == "LOW"], z[z.breadth_bin == "HIGH"]
                        if len(lo) >= MIN_CELL and len(hi) >= MIN_CELL:
                            cond_rows.append({
                                "universe": u, "period": p, "state": v, "prior60_bin": hbin,
                                "n_low": len(lo), "n_high": len(hi),
                                "low_fwd20": float(lo.mkt_fwd_20d.mean()), "high_fwd20": float(hi.mkt_fwd_20d.mean()),
                                "high_minus_low": float(hi.mkt_fwd_20d.mean() - lo.mkt_fwd_20d.mean()),
                            })
    return pd.DataFrame(rows), pd.DataFrame(cond_rows), pd.DataFrame(threshold_rows)


def collapse_leader_events(leader: pd.DataFrame, ctx: pd.DataFrame) -> pd.DataFrame:
    """One market-timing observation per date x universe x leader; avoid triple-counting alternatives."""
    priority = ["GENUINE_ROTATION", "DEFENSIVE_ROTATION", "NO_CLEAR_ROTATION", "ALT_REVERSE"]
    rows = []
    for key, g in leader.groupby(["date", "universe", "leader_family"]):
        chosen = next((r for r in priority if (g.rotation_regime == r).any()), "ALT_REVERSE")
        zz = g[g.rotation_regime == chosen]
        r0 = g.iloc[0]
        rows.append({
            "date": key[0], "universe": key[1], "leader_family": key[2], "event_regime": chosen,
            "n_alternatives_in_regime": len(zz), "leader_strength": float(r0.leader_strength),
            "leader_top_fwd20": float(r0.leader_top_fwd20) if pd.notna(r0.leader_top_fwd20) else np.nan,
            "leader_spread_fwd20": float(r0.leader_spread_fwd20) if pd.notna(r0.leader_spread_fwd20) else np.nan,
            "alt_top_fwd20_mean": float(zz.alt_top_fwd20.mean()) if zz.alt_top_fwd20.notna().any() else np.nan,
            "alt_spread_fwd20_mean": float(zz.alt_spread_fwd20.mean()) if zz.alt_spread_fwd20.notna().any() else np.nan,
        })
    return attach_context(pd.DataFrame(rows), ctx)


def summarize_leader_period(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, cond_rows = [], []
    for u, g in events.groupby("universe"):
        for p in PERIODS:
            s = g[period_mask(g.date, p) & g.mkt_fwd_20d.notna()]
            # All strong-leader breakdown events together.
            if len(s) >= 3:
                rows.append({
                    "universe": u, "period": p, "event_regime": "ALL_LEADER_BREAKS", "n": len(s),
                    "mkt_fwd5": float(s.mkt_fwd_5d.mean()), "mkt_fwd20": float(s.mkt_fwd_20d.mean()),
                    "prior60": float(s.mkt_trail_60d.mean()), "prior60_high_share": float((s.prior60_bin == "HIGH").mean()),
                    "alt_top_fwd20": float(s.alt_top_fwd20_mean.mean()),
                })
            for regime, z in s.groupby("event_regime"):
                if len(z) < 3:
                    continue
                rows.append({
                    "universe": u, "period": p, "event_regime": regime, "n": len(z),
                    "mkt_fwd5": float(z.mkt_fwd_5d.mean()), "mkt_fwd20": float(z.mkt_fwd_20d.mean()),
                    "prior60": float(z.mkt_trail_60d.mean()), "prior60_high_share": float((z.prior60_bin == "HIGH").mean()),
                    "alt_top_fwd20": float(z.alt_top_fwd20_mean.mean()),
                })
        for p in ("NORMAL_2023_2024", "EXCEPTIONAL_2025_2026"):
            s = g[period_mask(g.date, p) & g.mkt_fwd_20d.notna()]
            for hbin, z in s.groupby("prior60_bin"):
                if len(z) < 3:
                    continue
                cond_rows.append({
                    "universe": u, "period": p, "prior60_bin": hbin, "n": len(z),
                    "mkt_fwd20": float(z.mkt_fwd_20d.mean()), "alt_top_fwd20": float(z.alt_top_fwd20_mean.mean()),
                    "genuine_share": float((z.event_regime == "GENUINE_ROTATION").mean()),
                    "defensive_share": float((z.event_regime == "DEFENSIVE_ROTATION").mean()),
                })
    return pd.DataFrame(rows), pd.DataFrame(cond_rows)


def fmt_pct(x) -> str:
    return "NA" if pd.isna(x) else f"{x:+.2%}"


def getrow(df: pd.DataFrame, **kwargs):
    z = df.copy()
    for k, v in kwargs.items():
        z = z[z[k] == v]
    return None if z.empty else z.iloc[0]


def write_summary(market_base, pair_period, pair_cond, breadth_period, breadth_cond, leader_period, leader_cond, states, market) -> str:
    max_date = min(states.date.max(), market.index.max())
    lines = [
        "# 2025-2026 Exceptional Bull Regime Validation", "",
        f"Data through: {max_date.date()}.",
        "Purpose: separate 2023-2024 normal post-discovery validation from 2025 and 2026 YTD exceptional-bull behavior, and test whether factor-state effects survive conditioning on prior market strength.",
        "All family states use the existing Q33 thresholds fit on 2016-2022 and frozen thereafter. 2023+ remains post-discovery validation, not pristine OOS.",
        "20D forward returns overlap across 5D state dates; reported means are descriptive. Pair cells require n>=5; two-sided confirmation contrasts retain n>=8 per side.", "",
        "## 1. Was 2025-2026 mechanically different?", "",
    ]
    for u in ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"]:
        vals = []
        for p in ["NORMAL_2023_2024", "EXCEPTIONAL_2025", "EXCEPTIONAL_2026_YTD", "EXCEPTIONAL_2025_2026"]:
            r = getrow(market_base, universe=u, period=p)
            if r is not None:
                vals.append(f"{p}: prior60 {fmt_pct(r.trail60_mean)}, next20 {fmt_pct(r.fwd20_mean)}, high-prior60 share {r.prior60_high_share:.0%} (n={int(r.n)})")
        if vals:
            lines.append(f"- {u}: " + "; ".join(vals))

    lines += ["", "## 2. W+/W+ confirmation: raw return vs incremental return", "",
              "The key distinction is raw next-20D return versus excess over the same-period unconditional market return. A large raw return with little excess is mostly bull-regime exposure, not incremental factor-state information.", ""]
    for u in ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"]:
        lines.append(f"### {u}")
        for p in ["NORMAL_2023_2024", "EXCEPTIONAL_2025_2026"]:
            z = pair_period[(pair_period.universe == u) & (pair_period.period == p)]
            if z.empty:
                lines.append(f"- {p}: no pair cells with n>={MIN_CELL}.")
                continue
            lines.append(
                f"- {p}: {len(z)}/6 family pairs available; median W+/W+ next20 {fmt_pct(z.signal_fwd20.median())}; "
                f"median excess vs unconditional {fmt_pct(z.excess_vs_unconditional.median())}; positive incremental pairs {(z.excess_vs_unconditional > 0).sum()}/{len(z)}."
            )
        # Detail chosen only by largest sample in each period, not best return.
        z = pair_period[(pair_period.universe == u) & (pair_period.period.isin(["NORMAL_2023_2024", "EXCEPTIONAL_2025_2026"]))]
        if not z.empty:
            for pair in z.groupby("family_pair").n_signal.sum().sort_values(ascending=False).head(3).index:
                a = getrow(z, period="NORMAL_2023_2024", family_pair=pair)
                b = getrow(z, period="EXCEPTIONAL_2025_2026", family_pair=pair)
                if a is not None or b is not None:
                    sa = "NA" if a is None else f"raw {fmt_pct(a.signal_fwd20)}, excess {fmt_pct(a.excess_vs_unconditional)}, n={int(a.n_signal)}"
                    sb = "NA" if b is None else f"raw {fmt_pct(b.signal_fwd20)}, excess {fmt_pct(b.excess_vs_unconditional)}, n={int(b.n_signal)}"
                    lines.append(f"  - {pair}: 2023-24 {sa}; 2025-26 {sb}")

    lines += ["", "## 3. Does W+/W+ add information after conditioning on prior 60D market state?", ""]
    for u in ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"]:
        for p in ["NORMAL_2023_2024", "EXCEPTIONAL_2025_2026"]:
            z = pair_cond[(pair_cond.universe == u) & (pair_cond.period == p)]
            if z.empty:
                continue
            parts = []
            for hbin in ["LOW", "MID", "HIGH"]:
                zz = z[z.prior60_bin == hbin]
                if not zz.empty:
                    parts.append(f"{hbin}: median incremental {fmt_pct(zz.diff_vs_other.median())} across {len(zz)} pairs")
            if parts:
                lines.append(f"- {u} {p}: " + "; ".join(parts))

    lines += ["", "## 4. Breadth decomposition by period", ""]
    for u in ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"]:
        for v in ["RELATIVE_WORKING_BREADTH", "ABS_CONFIRMED_BREADTH", "DEFENSIVE_WORKING_BREADTH"]:
            a = getrow(breadth_period, universe=u, period="NORMAL_2023_2024", state=v)
            b = getrow(breadth_period, universe=u, period="EXCEPTIONAL_2025_2026", state=v)
            if a is not None or b is not None:
                sa = "NA" if a is None else f"{fmt_pct(a.high_minus_low)} (n {int(a.n_high)}/{int(a.n_low)})"
                sb = "NA" if b is None else f"{fmt_pct(b.high_minus_low)} (n {int(b.n_high)}/{int(b.n_low)})"
                lines.append(f"- {u} {v}: 2023-24 H-L {sa}; 2025-26 H-L {sb}")

    lines += ["", "## 5. Generalized leader rotation, de-duplicated to one market event", "",
              "Previous leader summaries counted alternative families as separate rows. Here market timing uses one observation per date x universe x leader; alternative-family returns are averaged only within the selected event regime.", ""]
    for u in ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"]:
        for p in ["NORMAL_2023_2024", "EXCEPTIONAL_2025_2026"]:
            z = leader_period[(leader_period.universe == u) & (leader_period.period == p)]
            if z.empty:
                continue
            allr = z[z.event_regime == "ALL_LEADER_BREAKS"]
            parts = []
            if not allr.empty:
                r = allr.iloc[0]
                parts.append(f"all breaks n={int(r.n)}, next20 {fmt_pct(r.mkt_fwd20)}, prior60 {fmt_pct(r.prior60)}")
            for reg in ["GENUINE_ROTATION", "DEFENSIVE_ROTATION", "NO_CLEAR_ROTATION", "ALT_REVERSE"]:
                q = z[z.event_regime == reg]
                if not q.empty:
                    r = q.iloc[0]
                    parts.append(f"{reg} n={int(r.n)} next20 {fmt_pct(r.mkt_fwd20)} alt+20 {fmt_pct(r.alt_top_fwd20)}")
            if parts:
                lines.append(f"- {u} {p}: " + "; ".join(parts))

    lines += ["", "## 6. Interpretation rules", "",
              "- Treat 2025-2026 as an exceptional-bull stress regime, not as part of the normal validation average.",
              "- For W+/W+ and breadth, prioritize incremental return versus same-period unconditional return and same prior-60D market bin, not raw return.",
              "- If a relation exists only in 2025-2026 or disappears after prior-market conditioning, classify it as regime amplification / coincident confirmation rather than a general market-timing signal.",
              "- If a relation remains in 2023-2024 and within comparable prior-market bins, it is a stronger candidate for structural factor-state information.",
              "- Leader-rotation market timing must use unique leader-break events; alternative rows are appropriate for factor-allocation analysis, not independent market observations.", ""]
    return "\n".join(lines) + "\n"


def main():
    states, prim, breadth, leader, market = load_inputs()
    ctx, market_thresholds = build_market_context(states, market)
    market_base = summarize_market_baseline(ctx)
    pair_period, pair_contrasts, pair_conditioned = build_pair_period_results(states, prim, ctx)
    breadth_period, breadth_conditioned, breadth_thresholds = build_breadth_results(breadth, ctx)
    unique_leader = collapse_leader_events(leader, ctx)
    leader_period, leader_conditioned = summarize_leader_period(unique_leader)

    market_thresholds.to_csv(OUT / "market_state_thresholds.csv", index=False, encoding="utf-8-sig")
    market_base.to_csv(OUT / "market_period_baseline.csv", index=False, encoding="utf-8-sig")
    pair_period.to_csv(OUT / "pair_wplus_period.csv", index=False, encoding="utf-8-sig")
    pair_contrasts.to_csv(OUT / "pair_confirmation_contrasts_period.csv", index=False, encoding="utf-8-sig")
    pair_conditioned.to_csv(OUT / "pair_wplus_prior60_conditioned.csv", index=False, encoding="utf-8-sig")
    breadth_thresholds.to_csv(OUT / "breadth_thresholds.csv", index=False, encoding="utf-8-sig")
    breadth_period.to_csv(OUT / "breadth_period.csv", index=False, encoding="utf-8-sig")
    breadth_conditioned.to_csv(OUT / "breadth_prior60_conditioned.csv", index=False, encoding="utf-8-sig")
    unique_leader.to_csv(OUT / "leader_unique_events.csv", index=False, encoding="utf-8-sig")
    leader_period.to_csv(OUT / "leader_period.csv", index=False, encoding="utf-8-sig")
    leader_conditioned.to_csv(OUT / "leader_prior60_conditioned.csv", index=False, encoding="utf-8-sig")

    summary = write_summary(market_base, pair_period, pair_conditioned, breadth_period, breadth_conditioned,
                            leader_period, leader_conditioned, states, market)
    (OUT / "RESEARCH_SUMMARY.md").write_text(summary, encoding="utf-8")
    print(f"data through {min(states.date.max(), market.index.max()).date()}")
    print(f"pair-period cells: {len(pair_period):,}")
    print(f"breadth-period cells: {len(breadth_period):,}")
    print(f"unique leader events: {len(unique_leader):,}")


if __name__ == "__main__":
    main()
