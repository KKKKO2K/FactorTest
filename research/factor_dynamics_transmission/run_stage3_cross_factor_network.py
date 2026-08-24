from __future__ import annotations

from itertools import permutations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "research/factor_regime_v1/results/factor_5d_returns.csv"
OUT = Path(__file__).resolve().parent / "results_stage3_cross_factor_network"
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = ["MOM1M", "MOM12_1", "OP12_REV", "OPFY1_REV", "PBR12MF", "PER12MF", "PRIVATE_FLOW", "FOREIGN_FLOW"]
PRIMITIVES = ["K200", "KOSPI_EX_K200", "KOSDAQ"]
PERIODS = ["DISC_2016_2019", "VAL_2020_2022", "CONF_2023_2024", "STRESS_2025", "STRESS_2026"]


def period_of(dt):
    y = pd.Timestamp(dt).year
    if y <= 2019: return "DISC_2016_2019"
    if y <= 2022: return "VAL_2020_2022"
    if y <= 2024: return "CONF_2023_2024"
    if y == 2025: return "STRESS_2025"
    return "STRESS_2026"


def ols(X, y):
    X = np.asarray(X, float); y = np.asarray(y, float)
    ok = np.isfinite(X).all(1) & np.isfinite(y)
    X, y = X[ok], y[ok]
    if len(y) < X.shape[1] + 8: return np.full(X.shape[1], np.nan)
    return np.linalg.lstsq(X, y, rcond=None)[0]


def mse(y, p):
    y = np.asarray(y, float); p = np.asarray(p, float)
    ok = np.isfinite(y) & np.isfinite(p)
    return float(np.mean((y[ok] - p[ok])**2)) if ok.sum() >= 6 else np.nan


def load_common_tape():
    f = pd.read_csv(SRC)
    f["date"] = pd.to_datetime(f.date)
    f = f[f.factor.isin(FACTORS) & f.universe.isin(PRIMITIVES)].copy()
    f["ls_return"] = pd.to_numeric(f.ls_return, errors="coerce")
    f = f.dropna(subset=["date", "factor", "universe", "ls_return"])
    d = f[f.date.dt.year <= 2019].groupby(["factor", "universe"]).ls_return.agg(["mean", "std"]).reset_index()
    d["std"] = d["std"].replace(0, np.nan)
    f = f.merge(d, on=["factor", "universe"], how="left")
    f["z"] = (f.ls_return - f["mean"]) / f["std"]
    x = f.pivot_table(index="date", columns=["factor", "universe"], values="z").sort_index()
    out = pd.DataFrame(index=x.index)
    for fac in FACTORS:
        cols = [(fac, u) for u in PRIMITIVES]
        if all(c in x.columns for c in cols):
            out[fac] = x[cols].mean(axis=1)
    return out.dropna(how="any")


def make_rows(tape, src, dst):
    g = pd.DataFrame({"date": tape.index, "src": tape[src].values, "dst": tape[dst].values})
    g["y"] = g.dst.shift(-1)
    g["target_date"] = g.date.shift(-1)
    g["period"] = g.target_date.map(lambda d: period_of(d) if pd.notna(d) else None)
    return g.dropna()


def designs(q):
    xb = np.column_stack([np.ones(len(q)), q.dst])
    xa = np.column_stack([np.ones(len(q)), q.dst, q.src])
    return xb, xa


def eval_edges(tape):
    rows = []
    cache = {}
    for src, dst in permutations(FACTORS, 2):
        q = make_rows(tape, src, dst)
        tr = q[q.period.eq("DISC_2016_2019")]
        xb, xa = designs(tr)
        bb, ba = ols(xb, tr.y), ols(xa, tr.y)
        cache[(src, dst)] = (q, bb, ba)
        for p in PERIODS:
            z = q[q.period.eq(p)]
            if len(z) < 6: continue
            xbz, xaz = designs(z)
            pb, pa = xbz @ bb, xaz @ ba
            mb, ma = mse(z.y, pb), mse(z.y, pa)
            rows.append({"source": src, "destination": dst, "period": p, "n": len(z),
                         "source_coef_discovery": float(ba[2]),
                         "baseline_mse": mb, "augmented_mse": ma,
                         "incremental_oos_r2": 1 - ma/mb if mb > 0 else np.nan})
    return pd.DataFrame(rows), cache


def discovery_stability(tape):
    rows = []
    for src, dst in permutations(FACTORS, 2):
        q = make_rows(tape, src, dst)
        vals = {}
        for label, yrs in [("2016_17", (2016, 2017)), ("2018_19", (2018, 2019))]:
            z = q[q.target_date.dt.year.between(*yrs)]
            _, xa = designs(z)
            b = ols(xa, z.y)
            vals[label] = float(b[2]) if np.isfinite(b[2]) else np.nan
        rows.append({"source": src, "destination": dst, "coef_2016_17": vals["2016_17"], "coef_2018_19": vals["2018_19"],
                     "same_sign": bool(np.sign(vals["2016_17"]) == np.sign(vals["2018_19"])) if np.isfinite(vals["2016_17"]) and np.isfinite(vals["2018_19"]) else False})
    return pd.DataFrame(rows)


def placebo(cache):
    rows = []
    for (src, dst), (q, bb, ba) in cache.items():
        for p in ["VAL_2020_2022", "CONF_2023_2024", "STRESS_2025", "STRESS_2026"]:
            z = q[q.period.eq(p)].reset_index(drop=True)
            if len(z) < 8: continue
            xb, xa = designs(z)
            mb = mse(z.y, xb @ bb)
            obs = 1 - mse(z.y, xa @ ba)/mb if mb > 0 else np.nan
            null = []
            s = z.src.to_numpy(float)
            for k in range(1, len(z)):
                zz = z.copy(); zz["src"] = np.roll(s, k)
                _, xas = designs(zz)
                null.append(1 - mse(z.y, xas @ ba)/mb if mb > 0 else np.nan)
            null = np.array([v for v in null if np.isfinite(v)])
            pval = (1 + np.sum(null >= obs))/(1 + len(null)) if len(null) else np.nan
            rows.append({"source": src, "destination": dst, "period": p, "observed_r2": obs,
                         "placebo_p": float(pval), "observed_percentile": float(np.mean(null < obs)) if len(null) else np.nan,
                         "placebo_q90": float(np.quantile(null, .9)) if len(null) else np.nan})
    return pd.DataFrame(rows)


def classify(results, stab, pl):
    rows = []
    r = results.set_index(["source", "destination", "period"])
    s = stab.set_index(["source", "destination"])
    pp = pl.set_index(["source", "destination", "period"])
    for src, dst in permutations(FACTORS, 2):
        try:
            val = float(r.loc[(src,dst,"VAL_2020_2022"), "incremental_oos_r2"])
            conf = float(r.loc[(src,dst,"CONF_2023_2024"), "incremental_oos_r2"])
            rev_val = float(r.loc[(dst,src,"VAL_2020_2022"), "incremental_oos_r2"])
            rev_conf = float(r.loc[(dst,src,"CONF_2023_2024"), "incremental_oos_r2"])
            stable = bool(s.loc[(src,dst), "same_sign"])
            pv = float(pp.loc[(src,dst,"VAL_2020_2022"), "placebo_p"])
            pc = float(pp.loc[(src,dst,"CONF_2023_2024"), "placebo_p"])
        except KeyError:
            continue
        passed = bool(val > 0 and conf > 0 and stable and pv <= .10 and pc <= .10)
        directional = bool(passed and val > rev_val and conf > rev_conf)
        rows.append({"source": src, "destination": dst, "status": "PASS" if passed else "FAIL", "directional": directional,
                     "val_r2": val, "conf_r2": conf, "reverse_val_r2": rev_val, "reverse_conf_r2": rev_conf,
                     "coef_sign_stable": stable, "val_placebo_p": pv, "conf_placebo_p": pc})
    return pd.DataFrame(rows).sort_values(["status","directional","conf_r2","val_r2"], ascending=[False,False,False,False]).reset_index(drop=True)


def paths(cls):
    e = cls[(cls.status.eq("PASS")) & cls.directional]
    rows = []
    for a in e.itertuples(index=False):
        for b in e.itertuples(index=False):
            if a.destination == b.source and a.source != b.destination:
                rows.append({"path": f"{a.source} -> {a.destination} -> {b.destination}",
                             "edge1_val_r2": a.val_r2, "edge1_conf_r2": a.conf_r2,
                             "edge2_val_r2": b.val_r2, "edge2_conf_r2": b.conf_r2})
    return pd.DataFrame(rows).drop_duplicates() if rows else pd.DataFrame(columns=["path"])


def report(cls, pathdf):
    p = cls[cls.status.eq("PASS")]
    d = p[p.directional]
    L = ["# Stage 3 — Cross-Factor Directed Transmission Network", "",
         "Primary tape uses only K200, KOSPI ex-K200, and KOSDAQ common factor returns.",
         "All 56 directed edges were pre-registered before this run.", "",
         f"- PASS edges: {len(p)}/56", f"- DIRECTIONAL PASS edges: {len(d)}/56", ""]
    if len(d):
        L += ["## Directional passing edges", ""]
        for x in d.itertuples(index=False):
            L.append(f"- {x.source} -> {x.destination}: VAL R2 {x.val_r2:+.4f}, CONF {x.conf_r2:+.4f}; reverse VAL {x.reverse_val_r2:+.4f}, CONF {x.reverse_conf_r2:+.4f}; placebo p {x.val_placebo_p:.3f}/{x.conf_placebo_p:.3f}")
    if len(p) and not len(d):
        L += ["## Passing but non-directional edges", ""]
        for x in p.itertuples(index=False):
            L.append(f"- {x.source} -> {x.destination}: VAL {x.val_r2:+.4f}, CONF {x.conf_r2:+.4f}; reverse not dominated in both eras")
    L += ["", "## Two-edge paths", ""]
    if len(pathdf):
        for x in pathdf.itertuples(index=False): L.append(f"- {x.path}")
    else:
        L.append("- None")
    L += ["", "## Strongest near-misses", ""]
    for x in cls[cls.status.eq("FAIL")].head(10).itertuples(index=False):
        L.append(f"- {x.source} -> {x.destination}: VAL {x.val_r2:+.4f}, CONF {x.conf_r2:+.4f}, sign_stable={x.coef_sign_stable}, placebo p={x.val_placebo_p:.3f}/{x.conf_placebo_p:.3f}")
    L += ["", "## Decision", ""]
    if len(d):
        L.append("At least one cross-factor transmission edge survives the full pre-registered gate. Next run should falsify only those exact edges across horizons and impulse responses before any trading application.")
    elif len(p):
        L.append("Some pair dynamics survive, but not with clean directionality. Treat them as factor-pair interactions and move toward pairwise relative-value dynamics rather than a causal transmission chain.")
    else:
        L.append("No simple cross-factor lead/lag edge survives. Reject the directed-network hypothesis at 5D and move to pairwise factor relative-value dynamics, a different estimand based on spread behavior rather than directional forecasting.")
    return "\n".join(L)


def main():
    tape = load_common_tape()
    results, cache = eval_edges(tape)
    stab = discovery_stability(tape)
    pl = placebo(cache)
    cls = classify(results, stab, pl)
    pathdf = paths(cls)
    tape.to_csv(OUT/"primitive_common_factor_tape.csv", encoding="utf-8-sig")
    results.to_csv(OUT/"edge_oos_results.csv", index=False, encoding="utf-8-sig")
    stab.to_csv(OUT/"edge_discovery_sign_stability.csv", index=False, encoding="utf-8-sig")
    pl.to_csv(OUT/"edge_time_shift_placebo.csv", index=False, encoding="utf-8-sig")
    cls.to_csv(OUT/"edge_classification.csv", index=False, encoding="utf-8-sig")
    pathdf.to_csv(OUT/"two_edge_paths.csv", index=False, encoding="utf-8-sig")
    text = report(cls, pathdf)
    (OUT/"RESEARCH_SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)

if __name__ == "__main__": main()
