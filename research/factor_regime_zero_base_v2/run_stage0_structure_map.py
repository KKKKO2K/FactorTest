from __future__ import annotations

from itertools import combinations
from pathlib import Path
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "research/factor_regime_v1/results/factor_5d_returns.csv"
OUT = Path(__file__).resolve().parent / "results_stage0_structure"
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = [
    "MOM1M", "MOM12_1", "OP12_REV", "OPFY1_REV",
    "PBR12MF", "PER12MF", "PRIVATE_FLOW", "FOREIGN_FLOW",
]


def sample_of(dt: pd.Timestamp) -> str:
    y = dt.year
    if y <= 2019:
        return "2016_2019"
    if y <= 2022:
        return "2020_2022"
    if y <= 2024:
        return "2023_2024"
    if y == 2025:
        return "2025"
    return "2026"


def compound_block(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    if a.ndim != 2 or np.isnan(a).any():
        return np.full(a.shape[1] if a.ndim == 2 else len(FACTORS), np.nan)
    if np.any(a <= -0.999999):
        return np.sum(a, axis=0)
    return np.prod(1.0 + a, axis=0) - 1.0


def spearman(a: np.ndarray | pd.Series, b: np.ndarray | pd.Series) -> float:
    x = pd.Series(np.asarray(a, dtype=float))
    y = pd.Series(np.asarray(b, dtype=float))
    z = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    if len(z) < 3 or z.x.nunique() < 2 or z.y.nunique() < 2:
        return np.nan
    return float(z.x.rank(method="average").corr(z.y.rank(method="average")))


def avg_pair_corr(a: np.ndarray) -> float:
    x = pd.DataFrame(a).dropna(axis=1, how="all")
    if x.shape[1] < 2 or len(x) < 6:
        return np.nan
    c = x.corr(min_periods=max(5, len(x) // 2)).to_numpy(dtype=float)
    vals = c[np.triu_indices_from(c, k=1)]
    vals = vals[np.isfinite(vals)]
    return float(vals.mean()) if len(vals) else np.nan


def pc1_share(a: np.ndarray) -> float:
    x = pd.DataFrame(a).dropna(axis=1, how="all")
    if x.shape[1] < 2 or len(x) < 6:
        return np.nan
    c = x.corr(min_periods=max(5, len(x) // 2)).to_numpy(dtype=float)
    if not np.isfinite(c).all():
        return np.nan
    eig = np.linalg.eigvalsh(c)
    eig = np.clip(eig, 0, None)
    den = eig.sum()
    return float(eig[-1] / den) if den > 0 else np.nan


def ann_sharpe_5d(x: pd.Series) -> float:
    x = x.dropna().astype(float)
    if len(x) < 3 or x.std(ddof=1) <= 0:
        return np.nan
    return float(x.mean() / x.std(ddof=1) * math.sqrt(252 / 5))


def load_factor_panel() -> pd.DataFrame:
    f = pd.read_csv(SRC)
    required = {"date", "universe", "factor", "ls_return"}
    missing = required - set(f.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    f["date"] = pd.to_datetime(f["date"])
    f = f[f.factor.isin(FACTORS)].copy()
    f["ls_return"] = pd.to_numeric(f["ls_return"], errors="coerce")
    f = f.dropna(subset=["date", "universe", "factor", "ls_return"])
    return f.sort_values(["universe", "date", "factor"])


def factor_distribution_summary(f: pd.DataFrame) -> pd.DataFrame:
    x = f.copy()
    x["sample"] = x.date.map(sample_of)
    x = pd.concat([x, x.assign(sample="FULL")], ignore_index=True)
    rows = []
    for (sample, universe, factor), g in x.groupby(["sample", "universe", "factor"]):
        r = g.ls_return.astype(float)
        rows.append({
            "sample": sample,
            "universe": universe,
            "factor": factor,
            "n_5d": len(r),
            "mean_5d": float(r.mean()),
            "median_5d": float(r.median()),
            "vol_5d": float(r.std(ddof=1)),
            "sharpe_5d_ann": ann_sharpe_5d(r),
            "positive_share": float((r > 0).mean()),
            "q10": float(r.quantile(.10)),
            "q90": float(r.quantile(.90)),
            "skew": float(r.skew()),
        })
    return pd.DataFrame(rows)


def pair_correlation_summary(f: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for universe, g in f.groupby("universe"):
        w = g.pivot(index="date", columns="factor", values="ls_return").sort_index().reindex(columns=FACTORS)
        for sample in ["FULL", "2016_2019", "2020_2022", "2023_2024", "2025", "2026"]:
            z = w if sample == "FULL" else w[[sample_of(d) == sample for d in w.index]]
            c = z.corr(min_periods=20)
            for a, b in combinations(FACTORS, 2):
                rows.append({
                    "sample": sample,
                    "universe": universe,
                    "factor_a": a,
                    "factor_b": b,
                    "corr": float(c.loc[a, b]) if a in c.index and b in c.columns else np.nan,
                })
    return pd.DataFrame(rows)


def build_structure_panel(f: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for universe, g in f.groupby("universe"):
        w = g.pivot(index="date", columns="factor", values="ls_return").sort_index()
        if not set(FACTORS).issubset(w.columns):
            continue
        w = w[FACTORS]
        arr = w.to_numpy(dtype=float)
        dates = list(w.index)

        for i in range(11, len(w) - 4):
            cur20 = compound_block(arr[i - 3:i + 1])
            cur60 = compound_block(arr[i - 11:i + 1])
            fwd20 = compound_block(arr[i + 1:i + 5])
            if not (np.isfinite(cur20).all() and np.isfinite(cur60).all() and np.isfinite(fwd20).all()):
                continue

            top2 = np.argsort(cur20)[-2:]
            bottom2 = np.argsort(cur20)[:2]
            future_top2 = set(np.argsort(fwd20)[-2:])
            future_top4 = set(np.argsort(fwd20)[-4:])
            cur_top2 = set(top2)
            den_abs = float(np.abs(cur20).sum())

            rec = {
                "date": dates[i],
                "sample": sample_of(dates[i]),
                "universe": universe,
                "breadth20": float((cur20 > 0).mean()),
                "dispersion20": float(np.std(cur20, ddof=1)),
                "abs_opportunity20": float(np.mean(np.abs(cur20))),
                "range20": float(np.max(cur20) - np.min(cur20)),
                "leader_abs_share20": float(np.max(np.abs(cur20)) / den_abs) if den_abs > 0 else np.nan,
                "rank_agreement_20_60": spearman(cur20, cur60),
                "sign_agreement_20_60": float((np.sign(cur20) == np.sign(cur60)).mean()),
                "avg_pair_corr_60": avg_pair_corr(arr[i - 11:i + 1]),
                "pc1_share_60": pc1_share(arr[i - 11:i + 1]),
                "rank_persistence_next20": spearman(cur20, fwd20),
                "top2_same_share_next20": float(len(cur_top2 & future_top2) / 2),
                "top2_survival_top4_next20": float(len(cur_top2 & future_top4) / 2),
                "top2_alpha_vs_ew8_next20": float(np.mean(fwd20[top2]) - np.mean(fwd20)),
                "bottom2_alpha_vs_ew8_next20": float(np.mean(fwd20[bottom2]) - np.mean(fwd20)),
                "winner_minus_loser_next20": float(np.mean(fwd20[top2]) - np.mean(fwd20[bottom2])),
                "future_dispersion20": float(np.std(fwd20, ddof=1)),
                "future_abs_opportunity20": float(np.mean(np.abs(fwd20))),
                "future_breadth20": float((fwd20 > 0).mean()),
            }
            for j, factor in enumerate(FACTORS):
                rec[f"cur20_{factor}"] = float(cur20[j])
                rec[f"fwd20_{factor}"] = float(fwd20[j])
            rows.append(rec)
    return pd.DataFrame(rows).sort_values(["universe", "date"]).reset_index(drop=True)


def cross_universe_rank_agreement(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    cols = [f"cur20_{f}" for f in FACTORS]
    for dt, g in panel.groupby("date"):
        g = g.drop_duplicates("universe").set_index("universe")
        universes = sorted(g.index)
        for a, b in combinations(universes, 2):
            ra = g.loc[a, cols].to_numpy(dtype=float)
            rb = g.loc[b, cols].to_numpy(dtype=float)
            rows.append({
                "date": dt,
                "sample": sample_of(pd.Timestamp(dt)),
                "universe_a": a,
                "universe_b": b,
                "rank_corr_20": spearman(ra, rb),
            })
    return pd.DataFrame(rows)


def phenomenon_summary(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    x = pd.concat([panel, panel.assign(sample="FULL")], ignore_index=True)
    for (sample, universe), g in x.groupby(["sample", "universe"]):
        rows.append({
            "sample": sample,
            "universe": universe,
            "n_states": len(g),
            "median_rank_persistence_next20": float(g.rank_persistence_next20.median()),
            "positive_rank_persistence_share": float((g.rank_persistence_next20 > 0).mean()),
            "mean_top2_same_share_next20": float(g.top2_same_share_next20.mean()),
            "mean_top2_survival_top4_next20": float(g.top2_survival_top4_next20.mean()),
            "mean_top2_alpha_vs_ew8_next20": float(g.top2_alpha_vs_ew8_next20.mean()),
            "mean_winner_minus_loser_next20": float(g.winner_minus_loser_next20.mean()),
            "dispersion_current_future_spearman": spearman(g.dispersion20, g.future_dispersion20),
            "abs_opportunity_current_future_spearman": spearman(g.abs_opportunity20, g.future_abs_opportunity20),
            "breadth_current_future_spearman": spearman(g.breadth20, g.future_breadth20),
            "median_avg_pair_corr_60": float(g.avg_pair_corr_60.median()),
            "median_pc1_share_60": float(g.pc1_share_60.median()),
            "median_cross_horizon_rank_agreement": float(g.rank_agreement_20_60.median()),
        })
    return pd.DataFrame(rows)


def cross_universe_summary(xu: pd.DataFrame) -> pd.DataFrame:
    rows = []
    x = pd.concat([xu, xu.assign(sample="FULL")], ignore_index=True)
    for sample, g in x.groupby("sample"):
        by_pair = g.groupby(["universe_a", "universe_b"]).rank_corr_20.median()
        rows.append({
            "sample": sample,
            "n_pair_dates": len(g),
            "median_pair_rank_corr_20": float(g.rank_corr_20.median()),
            "median_of_pair_medians": float(by_pair.median()),
            "positive_pair_share": float((g.rank_corr_20 > 0).mean()),
        })
    return pd.DataFrame(rows)


def fmt(x: float, pct: bool = False) -> str:
    if not np.isfinite(x):
        return "NA"
    return f"{x:+.2%}" if pct else f"{x:+.3f}"


def make_report(fdist: pd.DataFrame, ps: pd.DataFrame, xu: pd.DataFrame) -> str:
    lines = [
        "# Stage 0 — Factor Payoff Empirical Structure Map", "",
        "This stage intentionally contains no predictor selection, no clustering, no regime labels and no trading-rule test.",
        "The purpose is to establish which factor-payoff phenomena exist before deciding what to forecast.", "",
        "## Data", "",
        f"- Factors: {', '.join(FACTORS)}",
        f"- Universes: {ps.universe.nunique()}",
        f"- Factor return observations: {int(fdist[fdist['sample'].eq('FULL')].n_5d.sum())}", "",
        "## Unconditional phenomenon map", "",
    ]

    for sample in ["2016_2019", "2020_2022", "2023_2024", "2025", "2026", "FULL"]:
        q = ps[ps.sample.eq(sample)]
        if q.empty:
            continue
        lines.append(
            f"- {sample}: rank persistence median {fmt(q.median_rank_persistence_next20.median())}; "
            f"top2 exact survival {q.mean_top2_same_share_next20.median():.1%}; "
            f"top2-in-top4 survival {q.mean_top2_survival_top4_next20.median():.1%}; "
            f"top2 alpha vs EW8 {fmt(q.mean_top2_alpha_vs_ew8_next20.median(), True)}; "
            f"winner-minus-loser {fmt(q.mean_winner_minus_loser_next20.median(), True)}; "
            f"dispersion persistence {fmt(q.dispersion_current_future_spearman.median())}; "
            f"absolute-opportunity persistence {fmt(q.abs_opportunity_current_future_spearman.median())}"
        )

    lines += ["", "## Cross-universe agreement", ""]
    for r in xu.itertuples(index=False):
        lines.append(
            f"- {r.sample}: median 20D factor-rank agreement across universe pairs "
            f"{fmt(r.median_pair_rank_corr_20)}; positive pair-date share {r.positive_pair_share:.1%}"
        )

    lines += [
        "", "## Stage-0 interpretation rule", "",
        "No PASS/FAIL is assigned here. Stage 1 may only target phenomena that are visibly present across multiple eras and universes.",
        "A phenomenon that appears only in 2025/2026 or only in one universe is not eligible for Stage 1 predictor research.",
        "The next action after reading these diagnostics is to pre-register at most 2–3 target phenomena before constructing any forecasting features.",
    ]
    return "\n".join(lines)


def main() -> None:
    f = load_factor_panel()
    fdist = factor_distribution_summary(f)
    pcorr = pair_correlation_summary(f)
    panel = build_structure_panel(f)
    ps = phenomenon_summary(panel)
    xu_long = cross_universe_rank_agreement(panel)
    xu = cross_universe_summary(xu_long)

    fdist.to_csv(OUT / "factor_distribution_summary.csv", index=False, encoding="utf-8-sig")
    pcorr.to_csv(OUT / "pair_correlation_summary.csv", index=False, encoding="utf-8-sig")
    panel.to_csv(OUT / "structure_panel.csv", index=False, encoding="utf-8-sig")
    ps.to_csv(OUT / "phenomenon_summary.csv", index=False, encoding="utf-8-sig")
    xu_long.to_csv(OUT / "cross_universe_rank_agreement.csv", index=False, encoding="utf-8-sig")
    xu.to_csv(OUT / "cross_universe_summary.csv", index=False, encoding="utf-8-sig")

    text = make_report(fdist, ps, xu)
    (OUT / "RESEARCH_SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
