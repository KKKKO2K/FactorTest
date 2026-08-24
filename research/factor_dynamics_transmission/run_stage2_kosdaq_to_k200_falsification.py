from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "research/factor_regime_v1/results/factor_5d_returns.csv"
OUT = Path(__file__).resolve().parent / "results_stage2_kosdaq_to_k200"
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = [
    "MOM1M", "MOM12_1", "OP12_REV", "OPFY1_REV",
    "PBR12MF", "PER12MF", "PRIVATE_FLOW", "FOREIGN_FLOW",
]
KQ = "KOSDAQ"
K2 = "K200"
EX = "KOSPI_EX_K200"
PRIMITIVES = [KQ, K2, EX]
PERIODS = ["DISC_2016_2019", "VAL_2020_2022", "CONF_2023_2024", "STRESS_2025", "STRESS_2026"]
HORIZONS = {
    "NEXT5": (1, 1),
    "GAP5": (2, 1),
    "NEXT10": (1, 2),
    "NEXT20": (1, 4),
}


def period_of(dt: pd.Timestamp) -> str:
    y = pd.Timestamp(dt).year
    if y <= 2019:
        return "DISC_2016_2019"
    if y <= 2022:
        return "VAL_2020_2022"
    if y <= 2024:
        return "CONF_2023_2024"
    if y == 2025:
        return "STRESS_2025"
    return "STRESS_2026"


def ols_fit(X, y):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(X).all(axis=1) & np.isfinite(y)
    X, y = X[ok], y[ok]
    if len(y) < X.shape[1] + 8:
        return np.full(X.shape[1], np.nan)
    return np.linalg.lstsq(X, y, rcond=None)[0]


def mse(y, p):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    ok = np.isfinite(y) & np.isfinite(p)
    if ok.sum() < 6:
        return np.nan
    return float(np.mean((y[ok] - p[ok]) ** 2))


def pred(X, beta):
    X = np.asarray(X, dtype=float)
    if not np.isfinite(beta).all():
        return np.full(len(X), np.nan)
    return X @ beta


def load_wide():
    f = pd.read_csv(SRC)
    f["date"] = pd.to_datetime(f["date"])
    f = f[f.factor.isin(FACTORS) & f.universe.isin(PRIMITIVES)].copy()
    f["ls_return"] = pd.to_numeric(f["ls_return"], errors="coerce")
    f = f.dropna(subset=["date", "factor", "universe", "ls_return"])

    # Discovery-only normalization per factor-universe.
    disc = f[f.date.dt.year <= 2019]
    s = disc.groupby(["factor", "universe"]).ls_return.agg(["mean", "std"]).reset_index()
    s["std"] = s["std"].replace(0, np.nan)
    f = f.merge(s, on=["factor", "universe"], how="left")
    f["z"] = (f.ls_return - f["mean"]) / f["std"]
    return f.dropna(subset=["z"])


def factor_matrix(f: pd.DataFrame, factor: str) -> pd.DataFrame:
    g = f[f.factor.eq(factor)]
    w = g.pivot(index="date", columns="universe", values="z").sort_index().reindex(columns=PRIMITIVES)
    return w.dropna(how="any")


def build_rows(w: pd.DataFrame, offset: int, length: int) -> pd.DataFrame:
    vals = w.to_numpy(dtype=float)
    dates = list(w.index)
    rows = []
    col = {u: i for i, u in enumerate(PRIMITIVES)}
    max_i = len(w) - (offset + length - 1)
    for i in range(max_i):
        target_idx = list(range(i + offset, i + offset + length))
        first_dt, last_dt = dates[target_idx[0]], dates[target_idx[-1]]
        if period_of(first_dt) != period_of(last_dt):
            continue
        y = float(vals[target_idx, col[K2]].sum())
        rows.append({
            "date": dates[i],
            "target_date": first_dt,
            "target_period": period_of(first_dt),
            "y": y,
            "k200_now": float(vals[i, col[K2]]),
            "kosdaq_now": float(vals[i, col[KQ]]),
            "ex_now": float(vals[i, col[EX]]),
        })
    return pd.DataFrame(rows)


def design(q: pd.DataFrame, model: str):
    one = np.ones(len(q))
    if model == "M0":
        return np.column_stack([one, q.k200_now])
    if model == "MEX":
        return np.column_stack([one, q.k200_now, q.ex_now])
    if model == "MKQ":
        return np.column_stack([one, q.k200_now, q.kosdaq_now])
    if model == "MBOTH":
        return np.column_stack([one, q.k200_now, q.ex_now, q.kosdaq_now])
    raise ValueError(model)


def fit_models(q: pd.DataFrame):
    tr = q[q.target_period.eq("DISC_2016_2019")]
    return {m: ols_fit(design(tr, m), tr.y) for m in ["M0", "MEX", "MKQ", "MBOTH"]}


def evaluate_factor_horizons(f: pd.DataFrame):
    result_rows = []
    fit_rows = []
    row_cache = {}
    beta_cache = {}
    for factor in FACTORS:
        w = factor_matrix(f, factor)
        for hname, (offset, length) in HORIZONS.items():
            q = build_rows(w, offset, length)
            betas = fit_models(q)
            row_cache[(factor, hname)] = q
            beta_cache[(factor, hname)] = betas
            fit_rows.append({
                "factor": factor, "horizon": hname,
                "coef_kq_mkq": float(betas["MKQ"][2]),
                "coef_ex_mex": float(betas["MEX"][2]),
                "coef_ex_mboth": float(betas["MBOTH"][2]),
                "coef_kq_mboth": float(betas["MBOTH"][3]),
            })
            for p in PERIODS:
                z = q[q.target_period.eq(p)]
                if len(z) < 6:
                    continue
                mses = {}
                for m, b in betas.items():
                    mses[m] = mse(z.y, pred(design(z, m), b))
                unique_kq = 1 - mses["MBOTH"] / mses["MEX"] if mses["MEX"] > 0 else np.nan
                unique_ex = 1 - mses["MBOTH"] / mses["MKQ"] if mses["MKQ"] > 0 else np.nan
                simple_kq = 1 - mses["MKQ"] / mses["M0"] if mses["M0"] > 0 else np.nan
                simple_ex = 1 - mses["MEX"] / mses["M0"] if mses["M0"] > 0 else np.nan
                result_rows.append({
                    "factor": factor, "horizon": hname, "period": p, "n": len(z),
                    "mse_m0": mses["M0"], "mse_mex": mses["MEX"], "mse_mkq": mses["MKQ"], "mse_mboth": mses["MBOTH"],
                    "simple_kq_r2": simple_kq, "simple_ex_r2": simple_ex,
                    "unique_kq_r2": unique_kq, "unique_ex_r2": unique_ex,
                })
    return pd.DataFrame(result_rows), pd.DataFrame(fit_rows), row_cache, beta_cache


def aggregate(results: pd.DataFrame):
    rows = []
    for (h, p), g in results.groupby(["horizon", "period"]):
        rows.append({
            "horizon": h, "period": p, "n_factors": g.factor.nunique(),
            "median_simple_kq_r2": float(g.simple_kq_r2.median()),
            "median_unique_kq_r2": float(g.unique_kq_r2.median()),
            "positive_unique_kq_factors": int((g.unique_kq_r2 > 0).sum()),
            "median_unique_ex_r2": float(g.unique_ex_r2.median()),
            "positive_unique_ex_factors": int((g.unique_ex_r2 > 0).sum()),
            "median_kq_minus_ex_unique_r2": float((g.unique_kq_r2 - g.unique_ex_r2).median()),
        })
    return pd.DataFrame(rows)


def split_discovery_coefficients(f: pd.DataFrame):
    rows = []
    for factor in FACTORS:
        w = factor_matrix(f, factor)
        q = build_rows(w, 1, 1)
        for label, years in [("DISC_2016_2017", (2016, 2017)), ("DISC_2018_2019", (2018, 2019))]:
            tr = q[q.target_date.dt.year.between(*years)]
            b = ols_fit(design(tr, "MBOTH"), tr.y)
            rows.append({
                "factor": factor, "split": label, "n": len(tr),
                "kq_coef": float(b[3]) if len(b) > 3 and np.isfinite(b[3]) else np.nan,
                "ex_coef": float(b[2]) if len(b) > 2 and np.isfinite(b[2]) else np.nan,
            })
    out = pd.DataFrame(rows)
    piv = out.pivot(index="factor", columns="split", values="kq_coef")
    if set(["DISC_2016_2017", "DISC_2018_2019"]).issubset(piv.columns):
        stab = pd.DataFrame({
            "factor": piv.index,
            "kq_coef_2016_17": piv["DISC_2016_2017"].values,
            "kq_coef_2018_19": piv["DISC_2018_2019"].values,
            "same_sign": np.sign(piv["DISC_2016_2017"].values) == np.sign(piv["DISC_2018_2019"].values),
        })
    else:
        stab = pd.DataFrame()
    return out, stab


def leave_one_factor_out(results: pd.DataFrame):
    base = results[results.horizon.eq("NEXT5")]
    rows = []
    for p in ["VAL_2020_2022", "CONF_2023_2024", "STRESS_2025", "STRESS_2026"]:
        g = base[base.period.eq(p)]
        for omit in FACTORS:
            q = g[~g.factor.eq(omit)]
            rows.append({
                "period": p, "omitted_factor": omit,
                "median_unique_kq_r2": float(q.unique_kq_r2.median()),
                "positive_factors": int((q.unique_kq_r2 > 0).sum()),
                "n_factors": len(q),
            })
    return pd.DataFrame(rows)


def time_shift_placebo(row_cache, beta_cache):
    factor_shift_rows = []
    edge_rows = []
    for p in ["VAL_2020_2022", "CONF_2023_2024", "STRESS_2025", "STRESS_2026"]:
        observed_by_factor = {}
        shifts_by_factor = {}
        min_n = None
        for factor in FACTORS:
            q = row_cache[(factor, "NEXT5")]
            z = q[q.target_period.eq(p)].reset_index(drop=True)
            if len(z) < 8:
                continue
            b_ex = beta_cache[(factor, "NEXT5")]["MEX"]
            b_both = beta_cache[(factor, "NEXT5")]["MBOTH"]
            p_ex = pred(design(z, "MEX"), b_ex)
            mse_ex = mse(z.y, p_ex)
            p_obs = pred(design(z, "MBOTH"), b_both)
            obs = 1 - mse(z.y, p_obs) / mse_ex if mse_ex > 0 else np.nan
            observed_by_factor[factor] = obs
            min_n = len(z) if min_n is None else min(min_n, len(z))
            vals = {}
            src = z.kosdaq_now.to_numpy(dtype=float)
            for k in range(1, len(z)):
                zz = z.copy()
                zz["kosdaq_now"] = np.roll(src, k)
                pp = pred(design(zz, "MBOTH"), b_both)
                vals[k] = 1 - mse(z.y, pp) / mse_ex if mse_ex > 0 else np.nan
                factor_shift_rows.append({
                    "period": p, "factor": factor, "shift": k, "shifted_unique_kq_r2": vals[k], "observed_unique_kq_r2": obs,
                })
            shifts_by_factor[factor] = vals

        if not observed_by_factor or min_n is None:
            continue
        observed_edge = float(np.nanmedian(list(observed_by_factor.values())))
        edge_shift_vals = []
        for k in range(1, min_n):
            vals = [shifts_by_factor[f].get(k, np.nan) for f in observed_by_factor]
            edge_shift_vals.append((k, float(np.nanmedian(vals))))
        null = np.array([v for _, v in edge_shift_vals if np.isfinite(v)], dtype=float)
        placebo_p = float((1 + np.sum(null >= observed_edge)) / (1 + len(null))) if len(null) else np.nan
        percentile = float(np.mean(null < observed_edge)) if len(null) else np.nan
        edge_rows.append({
            "period": p, "observed_median_unique_kq_r2": observed_edge,
            "n_placebo_shifts": len(null), "placebo_p_one_sided": placebo_p,
            "observed_percentile_vs_placebo": percentile,
            "placebo_median": float(np.median(null)) if len(null) else np.nan,
            "placebo_q90": float(np.quantile(null, 0.90)) if len(null) else np.nan,
        })
    return pd.DataFrame(factor_shift_rows), pd.DataFrame(edge_rows)


def classify(agg: pd.DataFrame, loo: pd.DataFrame, placebo: pd.DataFrame):
    a = agg[(agg.horizon.eq("NEXT5"))].set_index("period")
    val = a.loc["VAL_2020_2022"]
    conf = a.loc["CONF_2023_2024"]
    primary = bool(
        val.median_unique_kq_r2 > 0 and conf.median_unique_kq_r2 > 0
        and val.positive_unique_kq_factors >= 5 and conf.positive_unique_kq_factors >= 5
        and val.median_unique_kq_r2 > val.median_unique_ex_r2
        and conf.median_unique_kq_r2 > conf.median_unique_ex_r2
    )
    loo_val = loo[loo.period.eq("VAL_2020_2022")]
    loo_conf = loo[loo.period.eq("CONF_2023_2024")]
    loo_stable = bool((loo_val.median_unique_kq_r2 > 0).all() and (loo_conf.median_unique_kq_r2 > 0).all())
    pl = placebo.set_index("period")
    placebo_ok = bool(
        "VAL_2020_2022" in pl.index and "CONF_2023_2024" in pl.index
        and pl.loc["VAL_2020_2022", "placebo_p_one_sided"] <= 0.10
        and pl.loc["CONF_2023_2024", "placebo_p_one_sided"] <= 0.10
    )
    if primary and loo_stable and placebo_ok:
        label = "ROBUST_DIRECTIONAL"
    elif not primary and (val.median_unique_kq_r2 <= 0 or conf.median_unique_kq_r2 <= 0):
        label = "COMMON_PROXY" if (val.median_simple_kq_r2 > 0 or conf.median_simple_kq_r2 > 0) else "REJECT"
    else:
        label = "WEAK_DIRECTIONAL"
    return label, primary, loo_stable, placebo_ok


def make_report(agg, fits, stability, loo, placebo):
    label, primary, loo_stable, placebo_ok = classify(agg, loo, placebo)
    L = [
        "# Stage 2 — KOSDAQ -> K200 Propagation Falsification", "",
        "This stage tests only the clean primitive-universe edge selected in Stage 1.",
        "Composite universes are excluded from the primary mechanism test.", "",
        f"## Classification: {label}", "",
        f"- Primary unique-control gate: {primary}",
        f"- Leave-one-factor-out stable: {loo_stable}",
        f"- Time-shift placebo gate: {placebo_ok}", "",
        "## Horizon summary", "",
    ]
    order = ["NEXT5", "GAP5", "NEXT10", "NEXT20"]
    for h in order:
        L.append(f"### {h}")
        for p in ["VAL_2020_2022", "CONF_2023_2024", "STRESS_2025", "STRESS_2026"]:
            q = agg[(agg.horizon.eq(h)) & (agg.period.eq(p))]
            if q.empty:
                continue
            r = q.iloc[0]
            L.append(
                f"- {p}: unique KOSDAQ R2 {r.median_unique_kq_r2:+.4f} ({int(r.positive_unique_kq_factors)}/8 positive); "
                f"unique ex-K200 R2 {r.median_unique_ex_r2:+.4f}; KQ-EX {r.median_kq_minus_ex_unique_r2:+.4f}; "
                f"simple KOSDAQ R2 {r.median_simple_kq_r2:+.4f}"
            )
        L.append("")

    L += ["## Discovery coefficient stability", ""]
    if not stability.empty:
        L.append(f"- KOSDAQ coefficient same sign in 2016-17 and 2018-19 for {int(stability.same_sign.sum())}/8 factors.")
        for r in stability.itertuples(index=False):
            L.append(f"- {r.factor}: 2016-17 {r.kq_coef_2016_17:+.3f}; 2018-19 {r.kq_coef_2018_19:+.3f}; same_sign={bool(r.same_sign)}")

    L += ["", "## Time-shift placebo", ""]
    for r in placebo.itertuples(index=False):
        L.append(
            f"- {r.period}: observed median unique KQ R2 {r.observed_median_unique_kq_r2:+.4f}; "
            f"placebo median {r.placebo_median:+.4f}; q90 {r.placebo_q90:+.4f}; "
            f"observed percentile {r.observed_percentile_vs_placebo:.1%}; p={r.placebo_p_one_sided:.3f}"
        )

    L += ["", "## Leave-one-factor-out", ""]
    for p in ["VAL_2020_2022", "CONF_2023_2024"]:
        q = loo[loo.period.eq(p)]
        if q.empty:
            continue
        L.append(
            f"- {p}: median across omissions {q.median_unique_kq_r2.median():+.4f}; "
            f"minimum omission median {q.median_unique_kq_r2.min():+.4f}; positive after all {int((q.median_unique_kq_r2 > 0).sum())}/8 omissions"
        )

    L += ["", "## Interpretation", ""]
    if label == "ROBUST_DIRECTIONAL":
        L.append("KOSDAQ contains a small but unusually time-aligned factor signal that leads K200 even after the contemporaneous ex-K200 factor tape is controlled. The next step is a mechanism/event-study test, not a portfolio backtest yet.")
    elif label == "WEAK_DIRECTIONAL":
        L.append("The KOSDAQ-leading pattern survives some controls but not all falsification checks. Keep it as a candidate dynamic, but do not call it a stable transmission law or tune it into a trading rule.")
    elif label == "COMMON_PROXY":
        L.append("Stage-1 KOSDAQ -> K200 improvement is largely explained by the broader non-K200/common factor tape. Treat KOSDAQ as a proxy, not a leader.")
    else:
        L.append("The clean primitive-universe propagation hypothesis is rejected. Move to the next distinct research question: cross-factor transmission or pairwise factor relative-value dynamics.")
    return "\n".join(L)


def main():
    f = load_wide()
    results, fits, row_cache, beta_cache = evaluate_factor_horizons(f)
    agg = aggregate(results)
    split, stability = split_discovery_coefficients(f)
    loo = leave_one_factor_out(results)
    factor_placebo, edge_placebo = time_shift_placebo(row_cache, beta_cache)
    text = make_report(agg, fits, stability, loo, edge_placebo)

    results.to_csv(OUT / "factor_horizon_results.csv", index=False, encoding="utf-8-sig")
    agg.to_csv(OUT / "horizon_aggregate.csv", index=False, encoding="utf-8-sig")
    fits.to_csv(OUT / "discovery_coefficients.csv", index=False, encoding="utf-8-sig")
    split.to_csv(OUT / "discovery_split_coefficients.csv", index=False, encoding="utf-8-sig")
    stability.to_csv(OUT / "discovery_coefficient_stability.csv", index=False, encoding="utf-8-sig")
    loo.to_csv(OUT / "leave_one_factor_out.csv", index=False, encoding="utf-8-sig")
    factor_placebo.to_csv(OUT / "time_shift_placebo_factor.csv", index=False, encoding="utf-8-sig")
    edge_placebo.to_csv(OUT / "time_shift_placebo_edge.csv", index=False, encoding="utf-8-sig")
    (OUT / "RESEARCH_SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
