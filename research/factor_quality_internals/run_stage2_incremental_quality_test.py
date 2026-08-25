from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
INFILE = HERE / "results_stage1" / "factor_quality_block_panel.csv"
OUT = HERE / "results_stage2"
OUT.mkdir(parents=True, exist_ok=True)

PRIMARY = ["K200", "KOSPI_EX_K200", "KOSDAQ"]
FEATURES = ["WITHIN_ALIGNMENT", "BREADTH_ALIGNMENT", "BROAD_CONTRIBUTION", "LIQUIDITY_SUPPORT20"]


def era(dt: pd.Timestamp) -> str:
    y = dt.year
    if y <= 2019:
        return "2016-19"
    if y <= 2022:
        return "2020-22"
    if y <= 2024:
        return "2023-24"
    return str(y)


def rank_avg(s: pd.Series) -> pd.Series:
    return s.rank(method="average")


def residualize(y: pd.Series, x: pd.Series) -> np.ndarray:
    yy = y.to_numpy(dtype=float)
    xx = x.to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(xx)), xx])
    beta = np.linalg.lstsq(X, yy, rcond=None)[0]
    return yy - X @ beta


def partial_rank_corr(a: pd.Series, b: pd.Series, control: pd.Series) -> float:
    z = pd.DataFrame({"a": a, "b": b, "c": control}).dropna()
    if len(z) < 5:
        return np.nan
    ra = rank_avg(z.a)
    rb = rank_avg(z.b)
    rc = rank_avg(z.c)
    ea = residualize(ra, rc)
    eb = residualize(rb, rc)
    if np.std(ea, ddof=1) <= 0 or np.std(eb, ddof=1) <= 0:
        return np.nan
    return float(np.corrcoef(ea, eb)[0, 1])


def tstat(s: pd.Series) -> float:
    z = s.dropna()
    if len(z) < 3 or z.std(ddof=1) <= 0:
        return np.nan
    return float(z.mean() / (z.std(ddof=1) / np.sqrt(len(z))))


def main() -> None:
    p = pd.read_csv(INFILE, parse_dates=["signal_date"])
    p = p.sort_values(["universe", "factor", "signal_date"]).reset_index(drop=True)
    keys = ["universe", "factor"]

    # Only completed prior blocks enter the 20D state.
    for src, dst, how in [
        ("raw_ls", "RAW20", "sum"),
        ("within_selection", "WITHIN20", "sum"),
        ("allocation", "ALLOCATION20", "sum"),
        ("pairwise_breadth", "BREADTH20", "mean"),
        ("top5_abs_contrib_share", "CONCENTRATION20", "mean"),
        ("liquidity_support", "LIQUIDITY_SUPPORT20", "mean"),
    ]:
        if how == "sum":
            p[dst] = p.groupby(keys, observed=True)[src].transform(lambda s: s.shift(1).rolling(4, min_periods=4).sum())
        else:
            p[dst] = p.groupby(keys, observed=True)[src].transform(lambda s: s.shift(1).rolling(4, min_periods=4).mean())

    sgn = np.sign(p.RAW20)
    denom = p.WITHIN20.abs() + p.ALLOCATION20.abs()
    p["WITHIN_ALIGNMENT"] = np.where(denom > 1e-12, sgn * p.WITHIN20 / denom, np.nan)
    p["BREADTH_ALIGNMENT"] = np.where(p.RAW20 >= 0, p.BREADTH20, 1.0 - p.BREADTH20)
    p["BROAD_CONTRIBUTION"] = 1.0 - p.CONCENTRATION20
    p["NEXT_RAW5"] = p.raw_ls
    p["CONTINUATION5"] = sgn * p.NEXT_RAW5
    p["ABS_RAW20"] = p.RAW20.abs()
    p["era"] = p.signal_date.map(era)

    eval_rows = []
    required = ["RAW20", "NEXT_RAW5", "CONTINUATION5", "ABS_RAW20"] + FEATURES

    for (dt, universe), g0 in p.groupby(["signal_date", "universe"], observed=True):
        g = g0.dropna(subset=required).copy()
        if len(g) < 6:
            continue
        raw_rank = rank_avg(g.RAW20)
        future_rank = rank_avg(g.NEXT_RAW5)
        abs_raw_rank = rank_avg(g.ABS_RAW20)
        cont_rank = rank_avg(g.CONTINUATION5)
        n = len(g)
        center = (n + 1.0) / 2.0

        for feat in FEATURES:
            q_rank = rank_avg(g[feat])
            signed_quality = np.sign(g.RAW20) * (q_rank - center)
            signed_quality_rank = rank_avg(pd.Series(signed_quality, index=g.index))

            primary_ic = partial_rank_corr(signed_quality_rank, future_rank, raw_rank)
            continuation_ic = partial_rank_corr(q_rank, cont_rank, abs_raw_rank)

            top4 = g.nlargest(min(4, len(g)), "RAW20").copy()
            if len(top4) == 4:
                top4 = top4.sort_values(feat, ascending=False, kind="mergesort")
                spread = float(top4.iloc[:2].NEXT_RAW5.mean() - top4.iloc[-2:].NEXT_RAW5.mean())
                cont_spread = float(top4.iloc[:2].CONTINUATION5.mean() - top4.iloc[-2:].CONTINUATION5.mean())
            else:
                spread = np.nan
                cont_spread = np.nan

            eval_rows.append({
                "signal_date": dt,
                "era": era(dt),
                "universe": universe,
                "feature": feat,
                "n_factors": n,
                "primary_partial_ic": primary_ic,
                "continuation_partial_ic": continuation_ic,
                "top4_quality_spread_raw5": spread,
                "top4_quality_spread_cont5": cont_spread,
            })

    ev = pd.DataFrame(eval_rows)
    ev.to_csv(OUT / "date_level_quality_evaluation.csv", index=False)

    summary = (ev.groupby(["era", "universe", "feature"], observed=True)
               .agg(n_dates=("signal_date", "size"),
                    mean_primary_partial_ic=("primary_partial_ic", "mean"),
                    median_primary_partial_ic=("primary_partial_ic", "median"),
                    mean_continuation_partial_ic=("continuation_partial_ic", "mean"),
                    mean_top4_quality_spread_raw5=("top4_quality_spread_raw5", "mean"),
                    mean_top4_quality_spread_cont5=("top4_quality_spread_cont5", "mean"))
               .reset_index())
    summary.to_csv(OUT / "universe_era_feature_summary.csv", index=False)

    # Primary gate: only disjoint primitive universes count.
    prim = summary[summary.universe.isin(PRIMARY)].copy()
    gate_rows = []
    for e in ["2016-19", "2020-22", "2023-24", "2025", "2026"]:
        for feat in FEATURES:
            z = prim[(prim.era == e) & (prim.feature == feat)]
            if len(z) == 0:
                continue
            de = ev[(ev.era == e) & (ev.feature == feat) & (ev.universe.isin(PRIMARY))]
            gate_rows.append({
                "era": e,
                "feature": feat,
                "n_universes": len(z),
                "median_universe_primary_ic": float(z.mean_primary_partial_ic.median()),
                "positive_primary_ic_universes": int((z.mean_primary_partial_ic > 0).sum()),
                "median_universe_continuation_ic": float(z.mean_continuation_partial_ic.median()),
                "median_universe_top4_spread": float(z.mean_top4_quality_spread_raw5.median()),
                "positive_top4_spread_universes": int((z.mean_top4_quality_spread_raw5 > 0).sum()),
                "pooled_mean_primary_ic": float(de.primary_partial_ic.mean()),
                "pooled_primary_ic_tstat": tstat(de.primary_partial_ic),
                "pooled_mean_top4_spread": float(de.top4_quality_spread_raw5.mean()),
                "pooled_top4_spread_tstat": tstat(de.top4_quality_spread_raw5),
            })
    gate = pd.DataFrame(gate_rows)
    gate.to_csv(OUT / "gate_summary.csv", index=False)

    decisions = []
    for feat in FEATURES:
        ok = True
        details = []
        for e in ["2020-22", "2023-24"]:
            z = gate[(gate.era == e) & (gate.feature == feat)]
            if len(z) != 1:
                ok = False
                details.append(f"{e}:missing")
                continue
            r = z.iloc[0]
            cond = (
                r.median_universe_primary_ic > 0.02
                and r.positive_primary_ic_universes >= 2
                and r.median_universe_top4_spread > 0
                and r.positive_top4_spread_universes >= 2
            )
            ok = ok and bool(cond)
            details.append(
                f"{e}:pIC={r.median_universe_primary_ic:+.3f} "
                f"({int(r.positive_primary_ic_universes)}/3), "
                f"top4={r.median_universe_top4_spread:+.4%} "
                f"({int(r.positive_top4_spread_universes)}/3), pass={cond}"
            )
        decisions.append({"feature": feat, "primary_pass": ok, "details": " | ".join(details)})

    dec = pd.DataFrame(decisions)
    dec.to_csv(OUT / "primary_decision.csv", index=False)

    lines = ["# Stage 2 Incremental Factor Quality Test — Results", ""]
    for _, r in dec.iterrows():
        lines.append(f"- **{r['feature']}**: {'PASS' if r['primary_pass'] else 'FAIL'} — {r['details']}")
    lines += [
        "",
        "Primary IC is the partial cross-sectional rank IC of direction-aware quality vs next raw 5D factor payoff, controlling RAW20 rank.",
        "No feature combination or threshold search is performed in Stage 2.",
    ]
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
