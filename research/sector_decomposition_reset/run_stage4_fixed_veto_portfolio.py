from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
INFILE = HERE / "results_stage1" / "sector_decomposition_panel.csv"
OUT = HERE / "results_stage4"
OUT.mkdir(parents=True, exist_ok=True)
PRIMARY = ["K200", "KOSPI_EX_K200", "KOSDAQ"]
FACTORS = ["MOM1M", "MOM12_1", "OP12_REV", "OPFY1_REV", "PBR12MF", "PER12MF", "PRIVATE_FLOW", "FOREIGN_FLOW"]
ANN = np.sqrt(252/5)
COST_PER_TURNOVER = 0.001


def era(dt: pd.Timestamp) -> str:
    y = dt.year
    if y <= 2019: return "2016-19"
    if y <= 2022: return "2020-22"
    if y <= 2024: return "2023-24"
    return str(y)


def sharpe(s: pd.Series) -> float:
    x = s.dropna().astype(float)
    if len(x) < 2:
        return np.nan
    sd = x.std(ddof=1)
    if not np.isfinite(sd) or sd == 0:
        return np.nan
    return float(x.mean() / sd * ANN)


def weight_vector(g: pd.DataFrame, strategy: str) -> dict[str, float]:
    available = list(g.factor)
    ew = {f: (1.0/len(available) if f in available else 0.0) for f in FACTORS}
    if strategy == "EW":
        return ew
    if strategy == "RAW_TOP2":
        top = list(g.nlargest(2, "raw20").factor)
        return {f: (0.5 if f in top else 0.0) for f in FACTORS}
    if strategy == "SECTOR_CONFIRMED_TOP2":
        confirmed = g[g.within20 > 0].sort_values("raw20", ascending=False)
        chosen = list(confirmed.head(2).factor)
        w = {f: 0.0 for f in FACTORS}
        for f in chosen:
            w[f] += 0.5
        missing = 2 - len(chosen)
        if missing > 0:
            fallback_mass = 0.5 * missing
            for f in FACTORS:
                w[f] += fallback_mass * ew[f]
        return w
    raise ValueError(strategy)


def main() -> None:
    p = pd.read_csv(INFILE, parse_dates=["signal_date", "payoff_end_date"])
    p = p.sort_values(["universe", "factor", "signal_date"]).reset_index(drop=True)
    keys = ["universe", "factor"]
    p["raw20"] = p.groupby(keys, observed=True)["raw_ls"].transform(lambda s: s.shift(1).rolling(4, min_periods=4).sum())
    p["within20"] = p.groupby(keys, observed=True)["within_selection"].transform(lambda s: s.shift(1).rolling(4, min_periods=4).sum())
    p["era"] = p.signal_date.map(era)

    rows = []
    strategies = ["EW", "RAW_TOP2", "SECTOR_CONFIRMED_TOP2"]
    prev_w: dict[tuple[str, str], dict[str, float]] = {}

    for (dt, universe), g0 in p.groupby(["signal_date", "universe"], observed=True):
        g = g0.dropna(subset=["raw20", "within20", "raw_ls"]).copy()
        if len(g) < 6:
            continue
        realized = {r.factor: float(r.raw_ls) for _, r in g.iterrows()}
        n_confirmed = int((g.within20 > 0).sum())
        for strategy in strategies:
            w = weight_vector(g, strategy)
            gross = sum(w[f] * realized.get(f, 0.0) for f in FACTORS)
            key = (universe, strategy)
            if key in prev_w:
                turnover = 0.5 * sum(abs(w[f] - prev_w[key][f]) for f in FACTORS)
            else:
                turnover = np.nan
            prev_w[key] = w
            cost = (turnover * COST_PER_TURNOVER) if np.isfinite(turnover) else 0.0
            rows.append({
                "signal_date": dt,
                "era": era(dt),
                "universe": universe,
                "strategy": strategy,
                "n_available_factors": len(g),
                "n_confirmed_factors": n_confirmed,
                "gross_return": gross,
                "turnover": turnover,
                "cost_proxy": cost,
                "net_return_10bp": gross - cost,
                **{f"w_{f}": w[f] for f in FACTORS},
            })

    ret = pd.DataFrame(rows)
    ret.to_csv(OUT / "date_level_strategy_returns.csv", index=False)

    summ = (ret.groupby(["era", "universe", "strategy"], observed=True)
            .agg(n=("gross_return", "size"),
                 mean_gross=("gross_return", "mean"),
                 sharpe_gross=("gross_return", sharpe),
                 mean_turnover=("turnover", "mean"),
                 mean_cost_proxy=("cost_proxy", "mean"),
                 mean_net_10bp=("net_return_10bp", "mean"),
                 sharpe_net_10bp=("net_return_10bp", sharpe),
                 mean_n_confirmed=("n_confirmed_factors", "mean"))
            .reset_index())
    summ.to_csv(OUT / "universe_era_strategy_summary.csv", index=False)

    wide = summ.pivot_table(index=["era", "universe"], columns="strategy",
                            values=["mean_gross", "sharpe_gross", "mean_net_10bp", "sharpe_net_10bp"])
    wide.columns = [f"{a}__{b}" for a, b in wide.columns]
    wide = wide.reset_index()
    wide["d_mean_vs_rawtop2"] = wide["mean_gross__SECTOR_CONFIRMED_TOP2"] - wide["mean_gross__RAW_TOP2"]
    wide["d_sharpe_vs_rawtop2"] = wide["sharpe_gross__SECTOR_CONFIRMED_TOP2"] - wide["sharpe_gross__RAW_TOP2"]
    wide["alpha_vs_ew"] = wide["mean_gross__SECTOR_CONFIRMED_TOP2"] - wide["mean_gross__EW"]
    wide["d_mean_net10_vs_rawtop2"] = wide["mean_net_10bp__SECTOR_CONFIRMED_TOP2"] - wide["mean_net_10bp__RAW_TOP2"]
    wide["d_sharpe_net10_vs_rawtop2"] = wide["sharpe_net_10bp__SECTOR_CONFIRMED_TOP2"] - wide["sharpe_net_10bp__RAW_TOP2"]
    wide.to_csv(OUT / "comparison_summary.csv", index=False)

    gate_rows = []
    prim = wide[wide.universe.isin(PRIMARY)]
    for e in ["2016-19", "2020-22", "2023-24", "2025", "2026"]:
        z = prim[prim.era.eq(e)]
        gate_rows.append({
            "era": e,
            "median_d_sharpe_vs_rawtop2": float(z.d_sharpe_vs_rawtop2.median()) if len(z) else np.nan,
            "positive_d_sharpe_universes": int((z.d_sharpe_vs_rawtop2 > 0).sum()),
            "median_d_mean_vs_rawtop2": float(z.d_mean_vs_rawtop2.median()) if len(z) else np.nan,
            "median_alpha_vs_ew": float(z.alpha_vs_ew.median()) if len(z) else np.nan,
            "median_d_sharpe_net10_vs_rawtop2": float(z.d_sharpe_net10_vs_rawtop2.median()) if len(z) else np.nan,
            "median_d_mean_net10_vs_rawtop2": float(z.d_mean_net10_vs_rawtop2.median()) if len(z) else np.nan,
        })
    gate = pd.DataFrame(gate_rows)
    gate.to_csv(OUT / "gate_summary.csv", index=False)

    vals = gate[gate.era.isin(["2020-22", "2023-24"])]
    pass_list = []
    for _, r in vals.iterrows():
        pass_list.append(bool(
            r.median_d_sharpe_vs_rawtop2 > 0
            and r.positive_d_sharpe_universes >= 2
            and r.median_d_mean_vs_rawtop2 > 0
            and r.median_alpha_vs_ew > 0
        ))
    primary_pass = len(pass_list) == 2 and all(pass_list)
    pd.DataFrame([{"primary_pass": primary_pass}]).to_csv(OUT / "primary_decision.csv", index=False)

    lines = ["# Stage 4 Fixed Sector-Confirmation Portfolio — Results", "", f"- Primary gate: **{'PASS' if primary_pass else 'FAIL'}**", ""]
    for _, r in gate.iterrows():
        lines.append(
            f"- {r.era}: dSharpe vs RAW_TOP2={r.median_d_sharpe_vs_rawtop2:+.3f} "
            f"({int(r.positive_d_sharpe_universes)}/3 positive), dMean={r.median_d_mean_vs_rawtop2:+.4%}, "
            f"alpha vs EW={r.median_alpha_vs_ew:+.4%}, net10 dSharpe={r.median_d_sharpe_net10_vs_rawtop2:+.3f}"
        )
    lines += ["", "No threshold/top-k/fallback tuning is permitted after this stage on the same sample."]
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
