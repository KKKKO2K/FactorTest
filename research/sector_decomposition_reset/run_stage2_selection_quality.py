from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
INFILE = HERE / "results_stage1" / "sector_decomposition_panel.csv"
OUT = HERE / "results_stage2"
OUT.mkdir(parents=True, exist_ok=True)
PRIMARY = ["K200", "KOSPI_EX_K200", "KOSDAQ"]
SCORES = {"RAW20": "raw20", "WITHIN20": "within20", "NEUTRAL20": "neutral20"}


def era(dt: pd.Timestamp) -> str:
    y = dt.year
    if y <= 2019: return "2016-19"
    if y <= 2022: return "2020-22"
    if y <= 2024: return "2023-24"
    return str(y)


def spear(x: pd.Series, y: pd.Series) -> float:
    z = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(z) < 4 or z.x.nunique() < 2 or z.y.nunique() < 2:
        return np.nan
    return float(z.x.rank(method="average").corr(z.y.rank(method="average")))


def main() -> None:
    p = pd.read_csv(INFILE, parse_dates=["signal_date", "payoff_end_date"])
    p = p.sort_values(["universe", "factor", "signal_date"]).reset_index(drop=True)
    keys = ["universe", "factor"]
    for src, dst in [("raw_ls", "raw20"), ("within_selection", "within20"), ("neutral_ls", "neutral20")]:
        p[dst] = p.groupby(keys, observed=True)[src].transform(lambda s: s.shift(1).rolling(4, min_periods=4).sum())
    p["era"] = p.signal_date.map(era)

    eval_rows = []
    for (dt, universe), g0 in p.groupby(["signal_date", "universe"], observed=True):
        # common score/target sample for apples-to-apples comparison
        g = g0.dropna(subset=["raw20", "within20", "neutral20", "raw_ls", "neutral_ls"]).copy()
        if len(g) < 6:
            continue
        realized_raw_top2 = set(g.nlargest(2, "raw_ls").factor)
        for label, col in SCORES.items():
            sel = g.nlargest(2, col)
            eval_rows.append({
                "signal_date": dt,
                "era": era(dt),
                "universe": universe,
                "score": label,
                "n_factors": len(g),
                "ic_to_raw5": spear(g[col], g.raw_ls),
                "ic_to_neutral5": spear(g[col], g.neutral_ls),
                "top2_raw_minus_ew8": float(sel.raw_ls.mean() - g.raw_ls.mean()),
                "top2_neutral_minus_ew8": float(sel.neutral_ls.mean() - g.neutral_ls.mean()),
                "top2_overlap_share": len(set(sel.factor) & realized_raw_top2) / 2.0,
            })

    ev = pd.DataFrame(eval_rows)
    ev.to_csv(OUT / "date_level_selection_evaluation.csv", index=False)

    summary = (ev.groupby(["era", "universe", "score"], observed=True)
               .agg(n_dates=("signal_date", "size"),
                    mean_ic_raw=("ic_to_raw5", "mean"),
                    median_ic_raw=("ic_to_raw5", "median"),
                    mean_ic_neutral=("ic_to_neutral5", "mean"),
                    median_ic_neutral=("ic_to_neutral5", "median"),
                    mean_top2_raw_alpha=("top2_raw_minus_ew8", "mean"),
                    mean_top2_neutral_alpha=("top2_neutral_minus_ew8", "mean"),
                    mean_top2_overlap=("top2_overlap_share", "mean"))
               .reset_index())
    summary.to_csv(OUT / "universe_era_score_summary.csv", index=False)

    # Gate summary across the three disjoint primitive universes.
    prim = summary.loc[summary.universe.isin(PRIMARY)].copy()
    raw_ref = (prim.loc[prim.score.eq("RAW20"), ["era", "universe", "mean_ic_raw"]]
               .rename(columns={"mean_ic_raw": "raw20_ic"}))
    comp = prim.merge(raw_ref, on=["era", "universe"], how="left")
    comp["ic_improvement_vs_raw20"] = comp.mean_ic_raw - comp.raw20_ic
    gate = (comp.groupby(["era", "score"], observed=True)
            .agg(median_ic_raw=("mean_ic_raw", "median"),
                 positive_ic_universes=("mean_ic_raw", lambda s: int((s > 0).sum())),
                 median_ic_improvement_vs_raw20=("ic_improvement_vs_raw20", "median"),
                 median_top2_raw_alpha=("mean_top2_raw_alpha", "median"),
                 positive_top2_alpha_universes=("mean_top2_raw_alpha", lambda s: int((s > 0).sum())),
                 median_ic_neutral=("mean_ic_neutral", "median"),
                 median_top2_neutral_alpha=("mean_top2_neutral_alpha", "median"))
            .reset_index())
    gate.to_csv(OUT / "gate_summary.csv", index=False)

    # Apply preregistered primary gate to sector-quality candidates.
    decisions = []
    for score in ["WITHIN20", "NEUTRAL20"]:
        ok = True
        details = []
        for e in ["2020-22", "2023-24"]:
            z = gate[(gate.era == e) & (gate.score == score)]
            if len(z) != 1:
                ok = False
                details.append(f"{e}:missing")
                continue
            r = z.iloc[0]
            cond = (r.median_ic_raw > 0 and
                    r.positive_ic_universes >= 2 and
                    r.median_ic_improvement_vs_raw20 >= 0.02 and
                    r.median_top2_raw_alpha > 0)
            ok = ok and bool(cond)
            details.append(
                f"{e}:IC={r.median_ic_raw:+.3f}, posIC={int(r.positive_ic_universes)}/3, "
                f"dIC={r.median_ic_improvement_vs_raw20:+.3f}, top2={r.median_top2_raw_alpha:+.4%}, pass={cond}"
            )
        decisions.append({"score": score, "primary_pass": ok, "details": " | ".join(details)})
    dec = pd.DataFrame(decisions)
    dec.to_csv(OUT / "primary_decision.csv", index=False)

    lines = ["# Stage 2 Selection Quality — Results", ""]
    for _, r in dec.iterrows():
        lines.append(f"- **{r['score']}**: {'PASS' if r['primary_pass'] else 'FAIL'} — {r['details']}")
    lines += ["", "See `gate_summary.csv` and `universe_era_score_summary.csv` for the complete results."]
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
