from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
INFILE = HERE / "results_stage1" / "sector_decomposition_panel.csv"
OUT = HERE / "results_stage3"
OUT.mkdir(parents=True, exist_ok=True)
PRIMARY = ["K200", "KOSPI_EX_K200", "KOSDAQ"]


def era(dt: pd.Timestamp) -> str:
    y = dt.year
    if y <= 2019: return "2016-19"
    if y <= 2022: return "2020-22"
    if y <= 2024: return "2023-24"
    return str(y)


def tstat_mean(s: pd.Series) -> float:
    x = s.dropna().astype(float)
    if len(x) < 2:
        return np.nan
    sd = x.std(ddof=1)
    if not np.isfinite(sd) or sd == 0:
        return np.nan
    return float(x.mean() / (sd / np.sqrt(len(x))))


def main() -> None:
    p = pd.read_csv(INFILE, parse_dates=["signal_date", "payoff_end_date"])
    p = p.sort_values(["universe", "factor", "signal_date"]).reset_index(drop=True)
    keys = ["universe", "factor"]
    p["raw20"] = p.groupby(keys, observed=True)["raw_ls"].transform(lambda s: s.shift(1).rolling(4, min_periods=4).sum())
    p["within20"] = p.groupby(keys, observed=True)["within_selection"].transform(lambda s: s.shift(1).rolling(4, min_periods=4).sum())
    p["era"] = p.signal_date.map(era)

    cand_rows = []
    pair_rows = []
    for (dt, universe), g0 in p.groupby(["signal_date", "universe"], observed=True):
        g = g0.dropna(subset=["raw20", "within20", "raw_ls"]).copy()
        if len(g) < 6:
            continue
        ew8 = float(g.raw_ls.mean())
        top2 = g.nlargest(2, "raw20").copy()
        top2["confirmed"] = top2.within20 > 0
        for _, r in top2.iterrows():
            cand_rows.append({
                "signal_date": dt,
                "era": era(dt),
                "universe": universe,
                "factor": r.factor,
                "raw20": r.raw20,
                "within20": r.within20,
                "confirmed": bool(r.confirmed),
                "future_raw5": r.raw_ls,
                "same_date_ew8": ew8,
                "future_alpha_vs_ew8": float(r.raw_ls - ew8),
            })
        if int(top2.confirmed.sum()) == 1:
            rc = top2.loc[top2.confirmed].iloc[0]
            ru = top2.loc[~top2.confirmed].iloc[0]
            pair_rows.append({
                "signal_date": dt,
                "era": era(dt),
                "universe": universe,
                "confirmed_factor": rc.factor,
                "unconfirmed_factor": ru.factor,
                "confirmed_raw20": rc.raw20,
                "unconfirmed_raw20": ru.raw20,
                "confirmed_within20": rc.within20,
                "unconfirmed_within20": ru.within20,
                "confirmed_future_raw5": rc.raw_ls,
                "unconfirmed_future_raw5": ru.raw_ls,
                "pair_diff": float(rc.raw_ls - ru.raw_ls),
            })

    cand = pd.DataFrame(cand_rows)
    pairs = pd.DataFrame(pair_rows)
    cand.to_csv(OUT / "raw20_top2_candidates.csv", index=False)
    pairs.to_csv(OUT / "discordant_pair_comparisons.csv", index=False)

    cand_summary = (cand.groupby(["era", "universe", "confirmed"], observed=True)
                    .agg(n_candidates=("factor", "size"),
                         mean_future_raw5=("future_raw5", "mean"),
                         median_future_raw5=("future_raw5", "median"),
                         mean_alpha_vs_ew8=("future_alpha_vs_ew8", "mean"),
                         median_alpha_vs_ew8=("future_alpha_vs_ew8", "median"))
                    .reset_index())
    cand_summary.to_csv(OUT / "candidate_group_summary.csv", index=False)

    pair_summary = (pairs.groupby(["era", "universe"], observed=True)
                    .agg(n_pairs=("pair_diff", "size"),
                         mean_pair_diff=("pair_diff", "mean"),
                         median_pair_diff=("pair_diff", "median"),
                         win_rate=("pair_diff", lambda s: float((s > 0).mean())),
                         tstat=("pair_diff", tstat_mean))
                    .reset_index())
    pair_summary.to_csv(OUT / "universe_era_pair_summary.csv", index=False)

    factor_driver = (pairs.groupby(["era", "confirmed_factor"], observed=True)
                     .agg(n=("pair_diff", "size"), mean_pair_diff=("pair_diff", "mean"), win_rate=("pair_diff", lambda s: float((s > 0).mean())))
                     .reset_index())
    factor_driver.to_csv(OUT / "confirmed_factor_driver_summary.csv", index=False)

    gate_rows = []
    prim = pair_summary[pair_summary.universe.isin(PRIMARY)].copy()
    for e in ["2016-19", "2020-22", "2023-24", "2025", "2026"]:
        z = prim[prim.era.eq(e)].copy()
        pooled = pairs[(pairs.era.eq(e)) & (pairs.universe.isin(PRIMARY))]
        gate_rows.append({
            "era": e,
            "n_primitive_universes": int(z.universe.nunique()),
            "median_universe_mean_pair_diff": float(z.mean_pair_diff.median()) if len(z) else np.nan,
            "positive_mean_universes": int((z.mean_pair_diff > 0).sum()),
            "pooled_n_pairs": int(len(pooled)),
            "pooled_mean_pair_diff": float(pooled.pair_diff.mean()) if len(pooled) else np.nan,
            "pooled_median_pair_diff": float(pooled.pair_diff.median()) if len(pooled) else np.nan,
            "pooled_win_rate": float((pooled.pair_diff > 0).mean()) if len(pooled) else np.nan,
            "pooled_tstat": tstat_mean(pooled.pair_diff) if len(pooled) else np.nan,
        })
    gate = pd.DataFrame(gate_rows)
    gate.to_csv(OUT / "gate_summary.csv", index=False)

    val = gate[gate.era.isin(["2020-22", "2023-24"])].copy()
    pass_by_era = []
    for _, r in val.iterrows():
        ok = (
            r.median_universe_mean_pair_diff > 0
            and r.positive_mean_universes >= 2
            and r.pooled_mean_pair_diff > 0
            and r.pooled_win_rate > 0.5
        )
        pass_by_era.append(bool(ok))
    primary_pass = len(pass_by_era) == 2 and all(pass_by_era)
    pd.DataFrame([{"primary_pass": primary_pass}]).to_csv(OUT / "primary_decision.csv", index=False)

    lines = ["# Stage 3 Sector-Confirmed Raw Winner Test — Results", "", f"- Primary gate: **{'PASS' if primary_pass else 'FAIL'}**", ""]
    for _, r in gate.iterrows():
        lines.append(
            f"- {r.era}: median universe mean diff={r.median_universe_mean_pair_diff:+.4%}, "
            f"positive universes={int(r.positive_mean_universes)}/3, pooled mean={r.pooled_mean_pair_diff:+.4%}, "
            f"win rate={r.pooled_win_rate:.1%}, n={int(r.pooled_n_pairs)}, t={r.pooled_tstat:+.2f}"
        )
    lines += ["", "Stage 4 veto/backfill should be run only if the primary gate passes."]
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
