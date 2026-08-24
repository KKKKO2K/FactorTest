from __future__ import annotations

from itertools import permutations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "research/factor_regime_v1/results/factor_5d_returns.csv"
OUT = Path(__file__).resolve().parent / "results_stage1_propagation"
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = [
    "MOM1M", "MOM12_1", "OP12_REV", "OPFY1_REV",
    "PBR12MF", "PER12MF", "PRIVATE_FLOW", "FOREIGN_FLOW",
]
UNIVERSES = [
    "K200", "KOSDAQ", "KOSPI_EX_K200", "KOSPI_ALL",
    "KOSPI_KOSDAQ_ALL", "KOSDAQ_PLUS_KOSPI_EX_K200",
]
PERIODS = ["DISC_2016_2019", "VAL_2020_2022", "CONF_2023_2024", "STRESS_2025", "STRESS_2026"]


def period_of_date(dt: pd.Timestamp) -> str:
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


def spearman(a, b) -> float:
    z = pd.DataFrame({"a": pd.to_numeric(pd.Series(a), errors="coerce"),
                      "b": pd.to_numeric(pd.Series(b), errors="coerce")}).dropna()
    if len(z) < 6 or z.a.nunique() < 2 or z.b.nunique() < 2:
        return np.nan
    return float(z.a.rank(method="average").corr(z.b.rank(method="average")))


def ols_fit(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(X).all(axis=1) & np.isfinite(y)
    X = X[ok]
    y = y[ok]
    if len(y) < X.shape[1] + 8:
        return np.full(X.shape[1], np.nan)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def predict(X: np.ndarray, beta: np.ndarray) -> np.ndarray:
    if not np.isfinite(beta).all():
        return np.full(len(X), np.nan)
    return np.asarray(X, dtype=float) @ beta


def mse(y, p) -> float:
    z = pd.DataFrame({"y": y, "p": p}).dropna()
    if len(z) < 6:
        return np.nan
    return float(np.mean((z.y.to_numpy(dtype=float) - z.p.to_numpy(dtype=float)) ** 2))


def load_panel() -> pd.DataFrame:
    f = pd.read_csv(SRC)
    req = {"date", "universe", "factor", "ls_return"}
    miss = req - set(f.columns)
    if miss:
        raise ValueError(f"missing required columns: {sorted(miss)}")
    f["date"] = pd.to_datetime(f["date"])
    f = f[f.factor.isin(FACTORS) & f.universe.isin(UNIVERSES)].copy()
    f["ls_return"] = pd.to_numeric(f["ls_return"], errors="coerce")
    f = f.dropna(subset=["date", "universe", "factor", "ls_return"])
    return f.sort_values(["factor", "universe", "date"])


def discovery_normalize(f: pd.DataFrame) -> pd.DataFrame:
    x = f.copy()
    disc = x[x.date.dt.year <= 2019]
    stats = disc.groupby(["factor", "universe"]).ls_return.agg(["mean", "std"]).reset_index()
    stats["std"] = stats["std"].replace(0, np.nan)
    x = x.merge(stats, on=["factor", "universe"], how="left")
    x["z"] = (x.ls_return - x["mean"]) / x["std"]
    return x.dropna(subset=["z"])


def wide_factor(g: pd.DataFrame, value_col: str = "z") -> pd.DataFrame:
    return g.pivot(index="date", columns="universe", values=value_col).sort_index().reindex(columns=UNIVERSES)


def build_decomposition(x: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for factor, g in x.groupby("factor"):
        w = wide_factor(g, "z").dropna(how="any")
        if w.empty:
            continue
        common = w.mean(axis=1)
        local = w.sub(common, axis=0)
        for dt in w.index:
            rec = {"date": dt, "factor": factor, "period": period_of_date(dt), "common": float(common.loc[dt])}
            for u in UNIVERSES:
                rec[f"z_{u}"] = float(w.loc[dt, u])
                rec[f"local_{u}"] = float(local.loc[dt, u])
            rows.append(rec)
    return pd.DataFrame(rows).sort_values(["factor", "date"]).reset_index(drop=True)


def test_a_common_local(dec: pd.DataFrame):
    common_rows = []
    local_rows = []
    var_rows = []
    for factor, g0 in dec.groupby("factor"):
        g = g0.sort_values("date").copy()
        g["next_common"] = g.common.shift(-1)
        g["target_date"] = g.date.shift(-1)
        g["target_period"] = g.target_date.map(lambda d: period_of_date(d) if pd.notna(d) else None)
        for p in PERIODS:
            q = g[g.target_period.eq(p)]
            common_rows.append({
                "factor": factor, "period": p, "n": len(q),
                "common_next5_ic": spearman(q.common, q.next_common),
            })
            # Variance share is contemporaneous within the target-era rows.
            qv = g[g.period.eq(p)]
            if len(qv) >= 8:
                common_var = float(qv.common.var(ddof=1))
                total_vars = [float(qv[f"z_{u}"].var(ddof=1)) for u in UNIVERSES]
                den = float(np.mean(total_vars)) if total_vars else np.nan
                share = common_var / den if np.isfinite(den) and den > 0 else np.nan
            else:
                share = np.nan
            var_rows.append({"factor": factor, "period": p, "common_variance_share": share})

        for u in UNIVERSES:
            g[f"next_local_{u}"] = g[f"local_{u}"].shift(-1)
            for p in PERIODS:
                q = g[g.target_period.eq(p)]
                local_rows.append({
                    "factor": factor, "universe": u, "period": p, "n": len(q),
                    "local_next5_ic": spearman(q[f"local_{u}"], q[f"next_local_{u}"]),
                })
    return pd.DataFrame(common_rows), pd.DataFrame(local_rows), pd.DataFrame(var_rows)


def build_pair_rows(dec: pd.DataFrame, factor: str, src: str, dst: str) -> pd.DataFrame:
    g = dec[dec.factor.eq(factor)].sort_values("date").copy()
    if g.empty:
        return g
    g["target_date"] = g.date.shift(-1)
    g["target_period"] = g.target_date.map(lambda d: period_of_date(d) if pd.notna(d) else None)
    g["y"] = g[f"z_{dst}"].shift(-1)
    g["dst_now"] = g[f"z_{dst}"]
    g["src_now"] = g[f"z_{src}"]
    g["src_local_now"] = g[f"local_{src}"]
    g["dst_local_next"] = g[f"local_{dst}"].shift(-1)
    return g.dropna(subset=["target_date", "y", "dst_now", "src_now"])


def test_b_and_c(dec: pd.DataFrame):
    model_rows = []
    local_rows = []
    for factor in FACTORS:
        for src, dst in permutations(UNIVERSES, 2):
            g = build_pair_rows(dec, factor, src, dst)
            tr = g[g.target_period.eq("DISC_2016_2019")]
            if len(tr) < 30:
                continue
            Xb = np.column_stack([np.ones(len(tr)), tr.dst_now.to_numpy(dtype=float)])
            Xa = np.column_stack([np.ones(len(tr)), tr.dst_now.to_numpy(dtype=float), tr.src_now.to_numpy(dtype=float)])
            y = tr.y.to_numpy(dtype=float)
            bb = ols_fit(Xb, y)
            ba = ols_fit(Xa, y)
            src_coef = float(ba[2]) if len(ba) > 2 and np.isfinite(ba[2]) else np.nan

            for p in PERIODS:
                q = g[g.target_period.eq(p)]
                if len(q) < 6:
                    continue
                Xbq = np.column_stack([np.ones(len(q)), q.dst_now.to_numpy(dtype=float)])
                Xaq = np.column_stack([np.ones(len(q)), q.dst_now.to_numpy(dtype=float), q.src_now.to_numpy(dtype=float)])
                pb = predict(Xbq, bb)
                pa = predict(Xaq, ba)
                mb = mse(q.y, pb)
                ma = mse(q.y, pa)
                incr = 1 - ma / mb if np.isfinite(mb) and mb > 0 and np.isfinite(ma) else np.nan
                model_rows.append({
                    "factor": factor, "source": src, "destination": dst, "period": p,
                    "n": len(q), "source_coef_discovery": src_coef,
                    "baseline_mse": mb, "augmented_mse": ma,
                    "incremental_oos_r2": incr,
                    "baseline_prediction_ic": spearman(q.y, pb),
                    "augmented_prediction_ic": spearman(q.y, pa),
                })
                local_rows.append({
                    "factor": factor, "source": src, "destination": dst, "period": p,
                    "n": len(q),
                    "source_local_to_destination_local_next5_ic": spearman(q.src_local_now, q.dst_local_next),
                })
    return pd.DataFrame(model_rows), pd.DataFrame(local_rows)


def aggregate_edges(models: pd.DataFrame, local_diag: pd.DataFrame) -> pd.DataFrame:
    a = models.groupby(["source", "destination", "period"]).agg(
        n_factors=("factor", "nunique"),
        median_incremental_oos_r2=("incremental_oos_r2", "median"),
        mean_incremental_oos_r2=("incremental_oos_r2", "mean"),
        positive_factor_count=("incremental_oos_r2", lambda s: int((s > 0).sum())),
        median_source_coef=("source_coef_discovery", "median"),
        median_augmented_prediction_ic=("augmented_prediction_ic", "median"),
    ).reset_index()
    l = local_diag.groupby(["source", "destination", "period"]).agg(
        median_local_diffusion_ic=("source_local_to_destination_local_next5_ic", "median")
    ).reset_index()
    a = a.merge(l, on=["source", "destination", "period"], how="left")

    # Reverse-edge comparison in each period.
    rev = a[["source", "destination", "period", "median_incremental_oos_r2"]].rename(
        columns={"source": "destination", "destination": "source", "median_incremental_oos_r2": "reverse_median_incremental_oos_r2"}
    )
    a = a.merge(rev, on=["source", "destination", "period"], how="left")
    a["directional_advantage_vs_reverse"] = a.median_incremental_oos_r2 - a.reverse_median_incremental_oos_r2
    return a


def classify_edges(edge: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for src, dst in permutations(UNIVERSES, 2):
        q = edge[(edge.source.eq(src)) & (edge.destination.eq(dst))].set_index("period")
        if "VAL_2020_2022" not in q.index or "CONF_2023_2024" not in q.index:
            continue
        val = q.loc["VAL_2020_2022"]
        conf = q.loc["CONF_2023_2024"]
        passed = bool(
            val.median_incremental_oos_r2 > 0 and conf.median_incremental_oos_r2 > 0
            and val.positive_factor_count >= 5 and conf.positive_factor_count >= 5
        )
        directional = bool(
            passed
            and val.directional_advantage_vs_reverse > 0
            and conf.directional_advantage_vs_reverse > 0
        )
        rows.append({
            "source": src, "destination": dst,
            "pass": passed, "directional": directional,
            "val_median_incremental_oos_r2": float(val.median_incremental_oos_r2),
            "val_positive_factors": int(val.positive_factor_count),
            "conf_median_incremental_oos_r2": float(conf.median_incremental_oos_r2),
            "conf_positive_factors": int(conf.positive_factor_count),
            "val_advantage_vs_reverse": float(val.directional_advantage_vs_reverse),
            "conf_advantage_vs_reverse": float(conf.directional_advantage_vs_reverse),
            "val_local_diffusion_ic": float(val.median_local_diffusion_ic),
            "conf_local_diffusion_ic": float(conf.median_local_diffusion_ic),
        })
    return pd.DataFrame(rows).sort_values(
        ["pass", "directional", "conf_median_incremental_oos_r2", "val_median_incremental_oos_r2"],
        ascending=[False, False, False, False]
    ).reset_index(drop=True)


def summarize_common(common: pd.DataFrame, local: pd.DataFrame, varshare: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for p in PERIODS:
        c = common[common.period.eq(p)]
        l = local[local.period.eq(p)]
        v = varshare[varshare.period.eq(p)]
        rows.append({
            "period": p,
            "median_common_next5_ic": float(c.common_next5_ic.median()) if len(c) else np.nan,
            "positive_common_factor_count": int((c.common_next5_ic > 0).sum()),
            "median_local_next5_ic": float(l.local_next5_ic.median()) if len(l) else np.nan,
            "negative_local_series_count": int((l.local_next5_ic < 0).sum()),
            "median_common_variance_share": float(v.common_variance_share.median()) if len(v) else np.nan,
        })
    return pd.DataFrame(rows)


def report(common_summary: pd.DataFrame, cls: pd.DataFrame) -> str:
    L = [
        "# Stage 1 — Common/Local Factor Shocks and Cross-Universe Propagation", "",
        "This stage was pre-registered in `STAGE1_PROTOCOL.md` before results were viewed.",
        "No regime labels or portfolio rules are used.", "",
        "## Test A — Common versus local factor dynamics", "",
    ]
    for r in common_summary.itertuples(index=False):
        L.append(
            f"- {r.period}: median common next-5D IC {r.median_common_next5_ic:+.3f} "
            f"({r.positive_common_factor_count}/8 factors positive); median local next-5D IC {r.median_local_next5_ic:+.3f} "
            f"({r.negative_local_series_count}/48 local series negative); median common variance share {r.median_common_variance_share:.3f}"
        )

    passes = cls[cls["pass"]]
    directional = cls[cls.directional]
    L += ["", "## Test B — Directed same-factor universe propagation", "",
          f"- PASS edges: {len(passes)}/30",
          f"- Directional PASS edges: {len(directional)}/30", ""]

    if len(passes):
        L.append("### Passing edges")
        for r in passes.itertuples(index=False):
            tag = "DIRECTIONAL" if r.directional else "BIDIRECTIONAL/COMMON"
            L.append(
                f"- {r.source} -> {r.destination}: {tag}; "
                f"VAL median incremental OOS R2 {r.val_median_incremental_oos_r2:+.4f} ({r.val_positive_factors}/8 positive), "
                f"CONF {r.conf_median_incremental_oos_r2:+.4f} ({r.conf_positive_factors}/8); "
                f"reverse advantage VAL {r.val_advantage_vs_reverse:+.4f}, CONF {r.conf_advantage_vs_reverse:+.4f}; "
                f"local diffusion IC VAL {r.val_local_diffusion_ic:+.3f}, CONF {r.conf_local_diffusion_ic:+.3f}"
            )
    else:
        L.append("No directed universe edge passed the pre-registered validation + confirmation gate.")

    L += ["", "## Strongest non-passing edges by confirmation incremental OOS R2", ""]
    for r in cls.head(8).itertuples(index=False):
        L.append(
            f"- {r.source} -> {r.destination}: PASS={r.pass}; "
            f"VAL {r.val_median_incremental_oos_r2:+.4f} ({r.val_positive_factors}/8), "
            f"CONF {r.conf_median_incremental_oos_r2:+.4f} ({r.conf_positive_factors}/8), "
            f"reverse advantage CONF {r.conf_advantage_vs_reverse:+.4f}"
        )

    L += ["", "## Decision rule", ""]
    if len(directional):
        L.append(
            "At least one genuinely directional same-factor universe edge survives. Stage 2 should first falsify those exact edges with alternative horizons / gap tests before moving to cross-factor transmission."
        )
    elif len(passes):
        L.append(
            "Some edges add OOS information but do not dominate their reverse edges. Treat this as shared/common dynamics rather than directional propagation; Stage 2 should study common/local mechanisms, not a leader-follower story."
        )
    else:
        L.append(
            "Same-factor cross-universe propagation is rejected at the pre-registered edge level. Do not retune thresholds. Move to the next genuinely different question: cross-factor transmission or pairwise factor relative-value dynamics."
        )
    return "\n".join(L)


def main():
    raw = load_panel()
    x = discovery_normalize(raw)
    dec = build_decomposition(x)
    common, local, varshare = test_a_common_local(dec)
    models, local_diag = test_b_and_c(dec)
    edges = aggregate_edges(models, local_diag)
    cls = classify_edges(edges)
    common_summary = summarize_common(common, local, varshare)

    raw.to_csv(OUT / "input_factor_5d_returns_filtered.csv", index=False, encoding="utf-8-sig")
    dec.to_csv(OUT / "common_local_decomposition.csv", index=False, encoding="utf-8-sig")
    common.to_csv(OUT / "common_shock_continuation.csv", index=False, encoding="utf-8-sig")
    local.to_csv(OUT / "local_residual_continuation.csv", index=False, encoding="utf-8-sig")
    varshare.to_csv(OUT / "common_variance_share.csv", index=False, encoding="utf-8-sig")
    models.to_csv(OUT / "factor_edge_oos_models.csv", index=False, encoding="utf-8-sig")
    local_diag.to_csv(OUT / "factor_edge_local_diffusion.csv", index=False, encoding="utf-8-sig")
    edges.to_csv(OUT / "universe_edge_summary_by_period.csv", index=False, encoding="utf-8-sig")
    cls.to_csv(OUT / "universe_edge_classification.csv", index=False, encoding="utf-8-sig")
    common_summary.to_csv(OUT / "common_local_summary.csv", index=False, encoding="utf-8-sig")
    text = report(common_summary, cls)
    (OUT / "RESEARCH_SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
