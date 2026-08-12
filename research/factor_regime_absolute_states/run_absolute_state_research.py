from __future__ import annotations

import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REGIME_DIR = ROOT / "research" / "factor_regime_v1" / "results"
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

SPLIT = pd.Timestamp("2023-01-01")
CUTS = {"Q25": 0.25, "Q33": 1 / 3, "Q50": 0.50}
MAIN_CUT = "Q33"
MIN_N = 8
HORIZONS = (1, 5, 20)

FACTOR_FAMILY = {
    "MOM1M": "MOMENTUM", "MOM12_1": "MOMENTUM",
    "OP12_REV": "REVISION", "OPFY1_REV": "REVISION",
    "PBR12MF": "VALUE", "PER12MF": "VALUE",
    "PRIVATE_FLOW": "FLOW", "FOREIGN_FLOW": "FLOW",
}
MOMS = ("MOM1M", "MOM12_1")
OTHERS = {
    "REVISION": ("OP12_REV", "OPFY1_REV"),
    "VALUE": ("PBR12MF", "PER12MF"),
    "FLOW": ("PRIVATE_FLOW", "FOREIGN_FLOW"),
}
PAIRS = [(m, o, fam) for m in MOMS for fam, xs in OTHERS.items() for o in xs]


def compound_roll(df: pd.DataFrame, n: int = 4) -> pd.DataFrame:
    return (1.0 + df).rolling(n, min_periods=n).apply(np.prod, raw=True) - 1.0


def future_compound(df: pd.DataFrame, n: int) -> pd.DataFrame:
    if n == 1:
        return df.shift(-1)
    out = 1.0 + df.shift(-1)
    for i in range(2, n + 1):
        out = out * (1.0 + df.shift(-i))
    return out - 1.0


def forward_market(market: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(market.clip(lower=-0.999999))
    acc = sum(logs.shift(-i) for i in range(1, h + 1))
    return np.expm1(acc)


def mean_tstat(x: pd.Series) -> float:
    x = x.dropna()
    if len(x) < 3:
        return np.nan
    sd = x.std(ddof=1)
    return float(x.mean() / (sd / math.sqrt(len(x)))) if sd > 0 else np.nan


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    f = pd.read_csv(REGIME_DIR / "factor_5d_returns.csv")
    f["date"] = pd.to_datetime(f["date"])
    req = {"date", "universe", "factor", "ls_return", "top_abs_return"}
    missing = req - set(f.columns)
    if missing:
        raise ValueError(f"factor_5d_returns.csv missing columns: {sorted(missing)}")
    f["bottom_abs_return"] = f["top_abs_return"] - f["ls_return"]
    market = pd.read_csv(REGIME_DIR / "market_daily_returns.csv", index_col=0)
    market.index = pd.to_datetime(market.index)
    return f.sort_values(["universe", "date", "factor"]), market.sort_index()


def build_factor_panel(f: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, cuts = [], []
    for u, g in f.groupby("universe"):
        top5 = g.pivot(index="date", columns="factor", values="top_abs_return").sort_index()
        bot5 = g.pivot(index="date", columns="factor", values="bottom_abs_return").sort_index()
        ls5 = g.pivot(index="date", columns="factor", values="ls_return").sort_index()
        top20 = compound_roll(top5, 4)
        bot20 = compound_roll(bot5, 4)
        # Main interpretable relative state: cumulative preferred leg minus cumulative opposite leg.
        spread20 = top20 - bot20
        # Legacy definition retained only for diagnostics.
        legacy20 = compound_roll(ls5, 4)

        for factor in [x for x in FACTOR_FAMILY if x in spread20.columns]:
            tr = spread20.loc[spread20.index < SPLIT, factor].dropna()
            if len(tr) < 40:
                continue
            abs_tr = tr.abs()
            factor_cuts = {}
            for cn, q in CUTS.items():
                c = float(abs_tr.quantile(q))
                if np.isfinite(c) and c > 0:
                    factor_cuts[cn] = c
                    cuts.append({"universe": u, "factor": factor, "family": FACTOR_FAMILY[factor],
                                 "cut_name": cn, "abs_spread_cut": c, "train_n": len(tr)})
            for dt in spread20.index:
                rel = spread20.at[dt, factor]
                ta = top20.at[dt, factor]
                ba = bot20.at[dt, factor]
                leg = legacy20.at[dt, factor]
                if not np.isfinite(rel) or not np.isfinite(ta) or not np.isfinite(ba):
                    continue
                for cn, c in factor_cuts.items():
                    rel_state = "WORKING" if rel >= c else ("REVERSE" if rel <= -c else "NEUTRAL")
                    abs_sign = "POS" if ta > 0 else "NEG"
                    if rel_state == "WORKING":
                        state5 = "W+" if ta > 0 else "W-"
                    elif rel_state == "REVERSE":
                        state5 = "R+" if ta > 0 else "R-"
                    else:
                        state5 = "N"
                    state6 = state5 if rel_state != "NEUTRAL" else ("N+" if ta > 0 else "N-")
                    rows.append({
                        "date": dt, "universe": u, "factor": factor, "family": FACTOR_FAMILY[factor],
                        "cut_name": cn, "top_abs_20d": float(ta), "bottom_abs_20d": float(ba),
                        "spread_20d": float(rel), "legacy_ls_compound_20d": float(leg),
                        "relative_state": rel_state, "preferred_abs_sign": abs_sign,
                        "state5": state5, "state6": state6, "strength_vs_cut": float(rel / c),
                    })
    return pd.DataFrame(rows), pd.DataFrame(cuts)


def build_breadth(panel: pd.DataFrame) -> pd.DataFrame:
    z = panel[panel.cut_name == MAIN_CUT].copy()
    rows = []
    for (dt, u), g in z.groupby(["date", "universe"]):
        n = g.factor.nunique()
        if n < 5:
            continue
        rows.append({
            "date": dt, "universe": u, "n_factors": n,
            "RELATIVE_WORKING_BREADTH": float((g.relative_state == "WORKING").mean()),
            "ABS_CONFIRMED_BREADTH": float((g.state5 == "W+").mean()),
            "DEFENSIVE_WORKING_BREADTH": float((g.state5 == "W-").mean()),
            "REVERSE_BREADTH": float((g.relative_state == "REVERSE").mean()),
            "BULLISH_REVERSE_BREADTH": float((g.state5 == "R+").mean()),
            "BEARISH_REVERSE_BREADTH": float((g.state5 == "R-").mean()),
            "POSITIVE_ABS_BREADTH": float((g.top_abs_20d > 0).mean()),
        })
    return pd.DataFrame(rows)


def test_breadth(breadth: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    fwd = {h: forward_market(market, h) for h in HORIZONS}
    vars_ = [c for c in breadth.columns if c.endswith("BREADTH")]
    rows = []
    for u, g in breadth.groupby("universe"):
        tr = g[g.date < SPLIT]
        for v in vars_:
            x = tr[v].dropna()
            if len(x) < 30 or x.nunique() < 3:
                continue
            q1, q2 = x.quantile([1/3, 2/3]).tolist()
            if not np.isfinite(q1) or not np.isfinite(q2) or q1 >= q2:
                continue
            gg = g.copy()
            gg["bin"] = np.where(gg[v] <= q1, "LOW", np.where(gg[v] >= q2, "HIGH", "MID"))
            for h in HORIZONS:
                if u not in fwd[h].columns:
                    continue
                gg["fwd"] = gg.date.map(fwd[h][u])
                for sample, mask in (("TRAIN", gg.date < SPLIT), ("OOS", gg.date >= SPLIT)):
                    s = gg[mask & gg.fwd.notna()]
                    lo, hi = s[s.bin == "LOW"].fwd, s[s.bin == "HIGH"].fwd
                    if len(lo) < MIN_N or len(hi) < MIN_N:
                        continue
                    rows.append({"sample": sample, "universe": u, "state": v, "horizon": h,
                                 "q1": q1, "q2": q2, "n_low": len(lo), "n_high": len(hi),
                                 "low_mean": float(lo.mean()), "high_mean": float(hi.mean()),
                                 "high_minus_low": float(hi.mean() - lo.mean())})
    return pd.DataFrame(rows)


def classify_pair(m_rel: str, m_top: float, o_rel: str, o_top: float) -> str:
    if m_rel == "REVERSE" and m_top <= 0 and o_rel == "WORKING" and o_top > 0:
        return "GENUINE_ROTATION"
    if m_rel == "REVERSE" and m_top <= 0 and o_rel == "WORKING" and o_top <= 0:
        return "DEFENSIVE_ROTATION"
    if m_rel == "REVERSE" and m_top > 0 and o_rel == "WORKING" and o_top > 0:
        return "BULLISH_STYLE_SHIFT"
    if m_rel == "WORKING" and m_top > 0 and o_rel == "WORKING" and o_top > 0:
        return "BROAD_CONFIRMATION"
    if m_rel == "WORKING" and m_top <= 0 and o_rel == "WORKING" and o_top <= 0:
        return "DEFENSIVE_CONFIRMATION"
    if m_rel == "REVERSE" and m_top <= 0 and o_rel == "REVERSE" and o_top <= 0:
        return "BROAD_BREAKDOWN"
    return "OTHER"


def build_pair_results(f: pd.DataFrame, panel: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    fwd_mkt = {h: forward_market(market, h) for h in HORIZONS}
    rows = []
    for u, g in f.groupby("universe"):
        top5 = g.pivot(index="date", columns="factor", values="top_abs_return").sort_index()
        bot5 = g.pivot(index="date", columns="factor", values="bottom_abs_return").sort_index()
        ftop5, ftop20 = future_compound(top5, 1), future_compound(top5, 4)
        fbot5, fbot20 = future_compound(bot5, 1), future_compound(bot5, 4)
        su = panel[panel.universe == u]
        for mom, other, fam in PAIRS:
            for cn in CUTS:
                a = su[(su.factor == mom) & (su.cut_name == cn)][["date", "relative_state", "state5", "state6", "top_abs_20d", "bottom_abs_20d", "spread_20d"]].rename(columns={c: f"m_{c}" for c in ["relative_state", "state5", "state6", "top_abs_20d", "bottom_abs_20d", "spread_20d"]})
                b = su[(su.factor == other) & (su.cut_name == cn)][["date", "relative_state", "state5", "state6", "top_abs_20d", "bottom_abs_20d", "spread_20d"]].rename(columns={c: f"o_{c}" for c in ["relative_state", "state5", "state6", "top_abs_20d", "bottom_abs_20d", "spread_20d"]})
                p = a.merge(b, on="date", how="inner")
                if p.empty or mom not in top5.columns or other not in top5.columns:
                    continue
                p["pair_regime"] = [classify_pair(r.m_relative_state, r.m_top_abs_20d, r.o_relative_state, r.o_top_abs_20d) for r in p.itertuples()]
                for h in HORIZONS:
                    if u in fwd_mkt[h].columns:
                        p[f"mkt_{h}"] = p.date.map(fwd_mkt[h][u])
                for label, frame in (("mom_top_fwd5", ftop5), ("mom_top_fwd20", ftop20), ("mom_bot_fwd5", fbot5), ("mom_bot_fwd20", fbot20)):
                    p[label] = p.date.map(frame[mom])
                for label, frame in (("oth_top_fwd5", ftop5), ("oth_top_fwd20", ftop20), ("oth_bot_fwd5", fbot5), ("oth_bot_fwd20", fbot20)):
                    p[label] = p.date.map(frame[other])
                p["mom_spread_fwd5"] = p.mom_top_fwd5 - p.mom_bot_fwd5
                p["mom_spread_fwd20"] = p.mom_top_fwd20 - p.mom_bot_fwd20
                p["oth_spread_fwd5"] = p.oth_top_fwd5 - p.oth_bot_fwd5
                p["oth_spread_fwd20"] = p.oth_top_fwd20 - p.oth_bot_fwd20

                for sample, mask in (("TRAIN", p.date < SPLIT), ("OOS", p.date >= SPLIT)):
                    ps = p[mask]
                    for regime, z in ps.groupby("pair_regime"):
                        if regime == "OTHER" or len(z) < MIN_N:
                            continue
                        base = {"sample": sample, "universe": u, "cut_name": cn, "factor_a": mom, "factor_b": other,
                                "family_pair": f"MOMENTUM_X_{fam}", "pair_regime": regime, "n": len(z),
                                "mean_mom_top20": float(z.m_top_abs_20d.mean()), "mean_other_top20": float(z.o_top_abs_20d.mean()),
                                "mean_mom_spread20": float(z.m_spread_20d.mean()), "mean_other_spread20": float(z.o_spread_20d.mean())}
                        for h in HORIZONS:
                            x = z[f"mkt_{h}"].dropna()
                            if len(x):
                                base[f"mkt_{h}d_mean"] = float(x.mean())
                                base[f"mkt_{h}d_median"] = float(x.median())
                                base[f"mkt_{h}d_positive_share"] = float((x > 0).mean())
                                base[f"mkt_{h}d_tstat"] = mean_tstat(x)
                        for c in ["mom_top_fwd5", "mom_top_fwd20", "mom_spread_fwd5", "mom_spread_fwd20",
                                  "oth_top_fwd5", "oth_top_fwd20", "oth_spread_fwd5", "oth_spread_fwd20"]:
                            x = z[c].dropna()
                            if len(x):
                                base[f"{c}_mean"] = float(x.mean())
                                base[f"{c}_positive_share"] = float((x > 0).mean())
                        rows.append(base)
    return pd.DataFrame(rows)


def compare_regimes(results: pd.DataFrame) -> pd.DataFrame:
    comps = {
        "GENUINE_MINUS_DEFENSIVE_ROTATION": ("GENUINE_ROTATION", "DEFENSIVE_ROTATION"),
        "GENUINE_ROTATION_MINUS_BROAD_CONFIRMATION": ("GENUINE_ROTATION", "BROAD_CONFIRMATION"),
        "BULLISH_SHIFT_MINUS_BROAD_CONFIRMATION": ("BULLISH_STYLE_SHIFT", "BROAD_CONFIRMATION"),
    }
    rows = []
    keys = ["sample", "universe", "cut_name", "factor_a", "factor_b", "family_pair"]
    for key, g in results.groupby(keys):
        base = dict(zip(keys, key))
        for name, (lreg, rreg) in comps.items():
            l = g[g.pair_regime == lreg]
            r = g[g.pair_regime == rreg]
            if l.empty or r.empty:
                continue
            l, r = l.iloc[0], r.iloc[0]
            row = {**base, "contrast": name, "n_left": int(l.n), "n_right": int(r.n)}
            for col in ["mkt_5d_mean", "mkt_20d_mean", "mom_top_fwd20_mean", "mom_spread_fwd20_mean", "oth_top_fwd20_mean", "oth_spread_fwd20_mean"]:
                if pd.notna(l.get(col)) and pd.notna(r.get(col)):
                    row[col.replace("_mean", "_diff")] = float(l[col] - r[col])
            rows.append(row)
    return pd.DataFrame(rows)


def yearly_oos(results: pd.DataFrame) -> pd.DataFrame:
    # Results are aggregated by sample; yearly concentration is recomputed from raw pair panel in a later walk-forward stage.
    # This placeholder intentionally does not pretend the current 2023+ sample is untouched OOS.
    return pd.DataFrame()


def summarize(panel: pd.DataFrame, breadth_tests: pd.DataFrame, pair: pd.DataFrame, contrasts: pd.DataFrame) -> str:
    lines = [
        "# Absolute-Confirmed Factor State Research", "",
        "Core correction: factor 'working' is not defined from long-short spread alone. Each 20D state keeps preferred absolute return, opposite absolute return, and their cumulative-return difference.",
        "Main relative state uses 20D preferred cumulative return minus 20D opposite cumulative return. The prior compounded-5D-LS definition is retained only as a diagnostic column.",
        "State5: W+ = relative working and preferred absolute return > 0; W- = relative working but preferred absolute return <= 0; N = neutral; R+ / R- analogously split reverse states by preferred absolute sign.",
        "Primary rotation labels: GENUINE_ROTATION = Momentum R- + Other W+; DEFENSIVE_ROTATION = Momentum R- + Other W-; BULLISH_STYLE_SHIFT = Momentum R+ + Other W+; BROAD_CONFIRMATION = Momentum W+ + Other W+.",
        "Thresholds are fit on 2016-2022 TRAIN and frozen for 2023+. Q33 is main; Q25/Q50 are robustness. 2023+ is post-discovery validation, not untouched OOS.", "",
        "## Refined breadth: same-universe market outcome", "",
    ]
    if not breadth_tests.empty:
        for u in ("K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ", "KOSDAQ_PLUS_KOSPI_EX_K200"):
            z = breadth_tests[(breadth_tests.universe == u) & (breadth_tests.horizon == 20)]
            if z.empty: continue
            lines += [f"### {u}"]
            for st in ["RELATIVE_WORKING_BREADTH", "ABS_CONFIRMED_BREADTH", "DEFENSIVE_WORKING_BREADTH", "BEARISH_REVERSE_BREADTH", "POSITIVE_ABS_BREADTH"]:
                tr = z[(z["sample"] == "TRAIN") & (z.state == st)]
                oo = z[(z["sample"] == "OOS") & (z.state == st)]
                if not tr.empty and not oo.empty:
                    lines.append(f"- {st}: TRAIN H-L {tr.iloc[0].high_minus_low:+.2%} -> OOS {oo.iloc[0].high_minus_low:+.2%}")
            lines.append("")

    lines += ["## Pair regimes: Q33 same-universe market outcomes", ""]
    for u in ("K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ", "KOSDAQ_PLUS_KOSPI_EX_K200"):
        z = pair[(pair.universe == u) & (pair.cut_name == MAIN_CUT)]
        if z.empty: continue
        lines += [f"### {u}"]
        for fam in ("MOMENTUM_X_REVISION", "MOMENTUM_X_VALUE", "MOMENTUM_X_FLOW"):
            zz = z[z.family_pair == fam]
            if zz.empty: continue
            lines.append(f"{fam}:")
            for reg in ("GENUINE_ROTATION", "DEFENSIVE_ROTATION", "BULLISH_STYLE_SHIFT", "BROAD_CONFIRMATION", "BROAD_BREAKDOWN"):
                for sample in ("TRAIN", "OOS"):
                    q = zz[(zz.pair_regime == reg) & (zz["sample"] == sample)]
                    if q.empty: continue
                    med5 = q.mkt_5d_mean.median() if "mkt_5d_mean" in q else np.nan
                    med20 = q.mkt_20d_mean.median() if "mkt_20d_mean" in q else np.nan
                    lines.append(f"- {reg}, {sample}: median pair market +5D {med5:+.2%}, +20D {med20:+.2%} (pairs={len(q)})")
        lines.append("")

    lines += ["## Rotation contrast stability", ""]
    if not contrasts.empty:
        q = contrasts[contrasts.cut_name == MAIN_CUT]
        for fam in ("MOMENTUM_X_REVISION", "MOMENTUM_X_VALUE", "MOMENTUM_X_FLOW"):
            lines.append(f"### {fam}")
            for cname in q[q.family_pair == fam].contrast.unique():
                x = q[(q.family_pair == fam) & (q.contrast == cname)]
                for outcome in ("mkt_5d_diff", "mkt_20d_diff"):
                    if outcome not in x.columns: continue
                    p = x.pivot_table(index=["universe", "factor_a", "factor_b"], columns="sample", values=outcome, aggfunc="first").dropna()
                    if len(p):
                        stable = float((np.sign(p.TRAIN) == np.sign(p.OOS)).mean())
                        lines.append(f"- {cname} / {outcome}: sign stability {stable:.0%} (n={len(p)}), median TRAIN {p.TRAIN.median():+.2%}, OOS {p.OOS.median():+.2%}")
            lines.append("")

    lines += ["## Research-structure guardrails", "",
              "- Do not call a relative W state 'bullish' without checking the absolute preferred leg.",
              "- Do not call Momentum R + Other W a rotation until the absolute legs distinguish genuine rotation from defensive relative performance.",
              "- Breadth is a summary layer, not the primitive state variable; preserve factor identity and both absolute legs first.",
              "- The next validation stage should use expanding/rolling walk-forward thresholds rather than reusing 2023+ as an untouched OOS sample.", ""]
    return "\n".join(lines)


def main() -> None:
    f, market = load_inputs()
    panel, cuts = build_factor_panel(f)
    breadth = build_breadth(panel)
    breadth_tests = test_breadth(breadth, market)
    pair = build_pair_results(f, panel, market)
    contrasts = compare_regimes(pair)

    panel.to_csv(OUT / "factor_state_panel.csv", index=False, encoding="utf-8-sig")
    cuts.to_csv(OUT / "state_thresholds.csv", index=False, encoding="utf-8-sig")
    breadth.to_csv(OUT / "refined_breadth_panel.csv", index=False, encoding="utf-8-sig")
    breadth_tests.to_csv(OUT / "refined_breadth_market_tests.csv", index=False, encoding="utf-8-sig")
    pair.to_csv(OUT / "pair_regime_results.csv", index=False, encoding="utf-8-sig")
    contrasts.to_csv(OUT / "pair_regime_contrasts.csv", index=False, encoding="utf-8-sig")
    (OUT / "RESEARCH_SUMMARY.md").write_text(summarize(panel, breadth_tests, pair, contrasts), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
