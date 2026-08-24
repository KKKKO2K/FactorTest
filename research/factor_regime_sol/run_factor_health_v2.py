from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
IN = HERE / "results"
OUT = HERE / "results_factor_health_v2"
OUT.mkdir(parents=True, exist_ok=True)

FAMILIES = ("MOMENTUM", "REVISION", "VALUE", "FLOW")
TRAIN_END = pd.Timestamp("2023-01-01")
SAMPLES = {
    "TRAIN_2017_2022": (pd.Timestamp("2017-01-01"), pd.Timestamp("2022-12-31")),
    "POST_2023_PLUS": (pd.Timestamp("2023-01-01"), pd.Timestamp("2099-12-31")),
    "POST_2023_2024": (pd.Timestamp("2023-01-01"), pd.Timestamp("2024-12-31")),
    "BULL_2025": (pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
    "YTD_2026": (pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31")),
}


def compound_forward(x: pd.DataFrame, n: int) -> pd.DataFrame:
    out = 1.0 + x.shift(-1)
    for i in range(2, n + 1):
        out = out * (1.0 + x.shift(-i))
    return out - 1.0


def spearman(x: pd.Series, y: pd.Series) -> float:
    z = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(z) < 8 or z.x.nunique() < 2 or z.y.nunique() < 2:
        return np.nan
    return float(z.x.rank().corr(z.y.rank()))


def nw_dummy_t(y: np.ndarray, d: np.ndarray, lag: int) -> tuple[float, float]:
    mask = np.isfinite(y) & np.isfinite(d)
    y = y[mask].astype(float); d = d[mask].astype(float)
    if len(y) < 12 or len(np.unique(d)) < 2:
        return np.nan, np.nan
    X = np.column_stack([np.ones(len(y)), d])
    try:
        xtx_inv = np.linalg.inv(X.T @ X)
    except np.linalg.LinAlgError:
        return np.nan, np.nan
    beta = xtx_inv @ (X.T @ y)
    e = y - X @ beta
    S = np.zeros((2, 2))
    for t in range(len(y)):
        xt = X[t:t+1].T
        S += (e[t] ** 2) * (xt @ xt.T)
    for L in range(1, lag + 1):
        w = 1.0 - L / (lag + 1.0)
        G = np.zeros((2, 2))
        for t in range(L, len(y)):
            G += e[t] * e[t-L] * np.outer(X[t], X[t-L])
        S += w * (G + G.T)
    V = xtx_inv @ S @ xtx_inv
    se = math.sqrt(max(V[1, 1], 0.0))
    return float(beta[1]), float(beta[1] / se) if se > 0 else np.nan


def family_state_value(state: str) -> tuple[int, int]:
    # Healthy = W+; Broken = R-. Other states are deliberately neutral.
    return (1 if state == "W+" else 0, 1 if state == "R-" else 0)


def build_forward(f: pd.DataFrame, universes: list[str]) -> pd.DataFrame:
    top5 = f.pivot_table(index=["date", "universe"], columns="family", values="top_abs_5d").sort_index()
    spr5 = f.pivot_table(index=["date", "universe"], columns="family", values="spread_5d").sort_index()
    rows = []
    for u in universes:
        t = top5.xs(u, level="universe").sort_index()
        s = spr5.xs(u, level="universe").sort_index()
        ft5, fs5 = t.shift(-1), s.shift(-1)
        ft20, fs20 = compound_forward(t, 4), compound_forward(s, 4)
        for dt in t.index:
            rec = {"date": dt, "universe": u}
            for fam in FAMILIES:
                rec[f"{fam}_top_fwd5"] = ft5.at[dt, fam] if fam in ft5.columns else np.nan
                rec[f"{fam}_spread_fwd5"] = fs5.at[dt, fam] if fam in fs5.columns else np.nan
                rec[f"{fam}_top_fwd20"] = ft20.at[dt, fam] if fam in ft20.columns else np.nan
                rec[f"{fam}_spread_fwd20"] = fs20.at[dt, fam] if fam in fs20.columns else np.nan
            rows.append(rec)
    return pd.DataFrame(rows)


def build_health_panel(p: pd.DataFrame, fw: pd.DataFrame) -> pd.DataFrame:
    x = p.merge(fw, on=["date", "universe"], how="left")

    # Train-frozen standardization for continuous family health.
    params = {}
    for u, g in x[x.date < TRAIN_END].groupby("universe"):
        for fam in FAMILIES:
            for metric in ("spread20", "top_abs20"):
                c = f"{fam.lower()}_{metric}"
                v = g[c].dropna().astype(float)
                mu = float(v.mean())
                sd = float(v.std(ddof=0))
                params[(u, fam, metric)] = (mu, sd if np.isfinite(sd) and sd > 1e-12 else 1.0)

    rows = []
    for r in x.itertuples(index=False):
        for target in FAMILIES:
            others = [f for f in FAMILIES if f != target]
            healthy = broken = 0
            fam_scores = []
            for fam in others:
                st = getattr(r, f"{fam.lower()}_state")
                h, b = family_state_value(st)
                healthy += h; broken += b
                u = r.universe
                smu, ssd = params.get((u, fam, "spread20"), (np.nan, np.nan))
                amu, asd = params.get((u, fam, "top_abs20"), (np.nan, np.nan))
                sp = getattr(r, f"{fam.lower()}_spread20")
                ab = getattr(r, f"{fam.lower()}_top_abs20")
                if np.isfinite(sp) and np.isfinite(ab) and np.isfinite(ssd) and np.isfinite(asd):
                    zsp = np.clip((sp-smu)/ssd, -4, 4)
                    zab = np.clip((ab-amu)/asd, -4, 4)
                    fam_scores.append(0.5*zsp + 0.5*zab)
            fh_a = healthy / 3.0
            fh_b = (healthy - broken) / 3.0
            fh_c = float(np.mean(fam_scores)) if fam_scores else np.nan
            conflict = int(healthy > 0 and broken > 0)
            rec = {
                "date": r.date, "universe": r.universe, "target": target,
                "FH_A_HEALTHY_BREADTH": fh_a,
                "FH_B_NET_BREADTH": fh_b,
                "FH_C_CONTINUOUS": fh_c,
                "CONFLICT": conflict,
                "other_wplus_n": healthy, "other_rminus_n": broken,
                "target_state": getattr(r, f"{target.lower()}_state"),
                "target_top_abs20": getattr(r, f"{target.lower()}_top_abs20"),
                "target_spread20": getattr(r, f"{target.lower()}_spread20"),
            }
            for h in (5, 20):
                rec[f"top_fwd{h}"] = getattr(r, f"{target}_top_fwd{h}")
                rec[f"spread_fwd{h}"] = getattr(r, f"{target}_spread_fwd{h}")
            rows.append(rec)
    hp = pd.DataFrame(rows)

    # C uses train terciles frozen by universe x target; retain explicit bins for auditability.
    hp["FH_C_BIN"] = "MID"
    for (u, target), g in hp[hp.date < TRAIN_END].groupby(["universe", "target"]):
        v = g.FH_C_CONTINUOUS.dropna()
        if len(v) < 30:
            continue
        q1, q2 = v.quantile([1/3, 2/3]).tolist()
        m = (hp.universe == u) & (hp.target == target)
        hp.loc[m & (hp.FH_C_CONTINUOUS <= q1), "FH_C_BIN"] = "LOW"
        hp.loc[m & (hp.FH_C_CONTINUOUS >= q2), "FH_C_BIN"] = "HIGH"
    return hp


def health_bin(df: pd.DataFrame, metric: str) -> pd.Series:
    if metric == "FH_A_HEALTHY_BREADTH":
        return pd.Series(np.where(df[metric] >= 2/3, "HIGH", np.where(df[metric] <= 1/3, "LOW", "MID")), index=df.index)
    if metric == "FH_B_NET_BREADTH":
        return pd.Series(np.where(df[metric] > 0, "HIGH", np.where(df[metric] < 0, "LOW", "MID")), index=df.index)
    return df["FH_C_BIN"].copy()


def summarize_health(hp: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metrics = ("FH_A_HEALTHY_BREADTH", "FH_B_NET_BREADTH", "FH_C_CONTINUOUS")
    hl_rows, ic_rows, conflict_rows = [], [], []
    for sample, (lo, hi) in SAMPLES.items():
        z0 = hp[(hp.date >= lo) & (hp.date <= hi)].copy()
        for (u, target), g0 in z0.groupby(["universe", "target"]):
            g0 = g0.sort_values("date")
            for h in (5, 20):
                for outcome in ("top", "spread"):
                    ycol = f"{outcome}_fwd{h}"
                    for metric in metrics:
                        ic_rows.append({
                            "sample": sample, "universe": u, "target": target, "horizon": h,
                            "outcome": outcome, "metric": metric, "n": int(g0[[metric,ycol]].dropna().shape[0]),
                            "spearman": spearman(g0[metric], g0[ycol]),
                        })
                        bins = health_bin(g0, metric)
                        sel = bins.isin(["HIGH", "LOW"]) & g0[ycol].notna()
                        gg = g0.loc[sel, ["date", ycol]].copy()
                        bb = bins.loc[sel]
                        if len(gg) < 12 or (bb == "HIGH").sum() < 5 or (bb == "LOW").sum() < 5:
                            continue
                        high = gg.loc[bb == "HIGH", ycol]
                        low = gg.loc[bb == "LOW", ycol]
                        d = (bb == "HIGH").astype(float).to_numpy()
                        beta, t = nw_dummy_t(gg[ycol].to_numpy(float), d, 3 if h == 20 else 0)
                        hl_rows.append({
                            "sample": sample, "universe": u, "target": target, "horizon": h,
                            "outcome": outcome, "metric": metric,
                            "n_high": int(len(high)), "n_low": int(len(low)),
                            "high_mean": float(high.mean()), "low_mean": float(low.mean()),
                            "high_minus_low": float(high.mean()-low.mean()), "nw_t": t,
                            "high_positive_share": float((high>0).mean()), "low_positive_share": float((low>0).mean()),
                        })

                    # Does conflict add information beyond simple net breadth? y = a + b*FH_B + c*Conflict.
                    z = g0[["date", ycol, "FH_B_NET_BREADTH", "CONFLICT"]].dropna().copy()
                    if len(z) >= 20 and z.CONFLICT.nunique() > 1:
                        X = np.column_stack([np.ones(len(z)), z.FH_B_NET_BREADTH.to_numpy(float), z.CONFLICT.to_numpy(float)])
                        y = z[ycol].to_numpy(float)
                        try:
                            inv = np.linalg.inv(X.T @ X)
                            beta = inv @ X.T @ y
                            e = y - X @ beta
                            lag = 3 if h == 20 else 0
                            S = np.zeros((3,3))
                            for i in range(len(y)):
                                S += e[i]**2 * np.outer(X[i], X[i])
                            for L in range(1, lag+1):
                                w = 1-L/(lag+1)
                                G = np.zeros((3,3))
                                for i in range(L,len(y)):
                                    G += e[i]*e[i-L]*np.outer(X[i],X[i-L])
                                S += w*(G+G.T)
                            V = inv @ S @ inv
                            se = math.sqrt(max(V[2,2],0.0))
                            conflict_rows.append({
                                "sample":sample,"universe":u,"target":target,"horizon":h,"outcome":outcome,
                                "n":len(z),"net_breadth_beta":float(beta[1]),"conflict_beta":float(beta[2]),
                                "conflict_nw_t":float(beta[2]/se) if se>0 else np.nan,
                            })
                        except np.linalg.LinAlgError:
                            pass
    return pd.DataFrame(hl_rows), pd.DataFrame(ic_rows), pd.DataFrame(conflict_rows)


def robustness_table(hl: pd.DataFrame, ic: pd.DataFrame) -> pd.DataFrame:
    # Primary lens = forward 20D preferred leg. Score signs across 6 universes x 4 targets.
    rows = []
    for metric in ("FH_A_HEALTHY_BREADTH", "FH_B_NET_BREADTH", "FH_C_CONTINUOUS"):
        tr = hl[(hl.metric==metric)&(hl.sample=="TRAIN_2017_2022")&(hl.horizon==20)&(hl.outcome=="top")]
        po = hl[(hl.metric==metric)&(hl.sample=="POST_2023_PLUS")&(hl.horizon==20)&(hl.outcome=="top")]
        m = tr.merge(po,on=["universe","target","horizon","outcome","metric"],suffixes=("_tr","_po"))
        if len(m):
            rows.append({
                "metric":metric,"n_pairs":len(m),
                "train_median_hl":float(m.high_minus_low_tr.median()),
                "post_median_hl":float(m.high_minus_low_po.median()),
                "train_positive_share":float((m.high_minus_low_tr>0).mean()),
                "post_positive_share":float((m.high_minus_low_po>0).mean()),
                "same_positive_share":float(((m.high_minus_low_tr>0)&(m.high_minus_low_po>0)).mean()),
                "sign_agreement_share":float((np.sign(m.high_minus_low_tr)==np.sign(m.high_minus_low_po)).mean()),
            })
    return pd.DataFrame(rows)


def write_summary(rob: pd.DataFrame, hl: pd.DataFrame, conflict: pd.DataFrame) -> str:
    lines = [
        "# Factor Health 2.0 — generalized ex-target test", "",
        "Goal: test whether the health of the *other* factor families predicts the future performance of any target primary factor. The target family itself is excluded from health to avoid circularity.", "",
        "## Candidate definitions", "",
        "- FH-A Healthy Breadth: # of other 3 families currently W+ / 3.",
        "- FH-B Net Breadth: (# W+ - # R-) among other 3 / 3. Other states are neutral.",
        "- FH-C Continuous: average across other 3 families of 0.5*z(20D spread) + 0.5*z(20D preferred-leg absolute return). z-scores are fit on pre-2023 history and frozen; individual z values are clipped at +/-4.",
        "- Conflict is separate, not embedded in the scalar: 1 when at least one ex-target family is W+ and at least one is R-.", "",
        "Primary comparison is HIGH-minus-LOW future 20D preferred-leg return. 20D observations overlap on the 5D state grid; NW lag-3 t-stats are descriptive.", "",
        "## Aggregate robustness across 6 universes x 4 target families", "",
        "| Metric | Pairs | Train median H-L | Post median H-L | Train + | Post + | + in both | Sign agreement |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _,r in rob.iterrows():
        lines.append(f"| {r.metric} | {int(r.n_pairs)} | {r.train_median_hl:+.2%} | {r.post_median_hl:+.2%} | {r.train_positive_share:.0%} | {r.post_positive_share:.0%} | {r.same_positive_share:.0%} | {r.sign_agreement_share:.0%} |")

    lines += ["", "## By target family — 20D preferred leg, median across universes", "",
              "| Metric | Sample | Momentum | Revision | Value | Flow |", "|---|---|---:|---:|---:|---:|"]
    for metric in rob.metric.tolist():
        for sample in ("TRAIN_2017_2022","POST_2023_PLUS","POST_2023_2024","BULL_2025","YTD_2026"):
            z=hl[(hl.metric==metric)&(hl.sample==sample)&(hl.horizon==20)&(hl.outcome=="top")]
            vals={f:(z[z.target==f].high_minus_low.median() if len(z[z.target==f]) else np.nan) for f in FAMILIES}
            lines.append(f"| {metric} | {sample} | {vals['MOMENTUM']:+.2%} | {vals['REVISION']:+.2%} | {vals['VALUE']:+.2%} | {vals['FLOW']:+.2%} |")

    lines += ["", "## Strongest stable target/universe cells", "",
              "Cells below require positive H-L in both TRAIN and POST_2023_PLUS; sorted by the smaller of the two effects.", "",
              "| Metric | Universe | Target | Train H-L | Post H-L | Train t | Post t |", "|---|---|---|---:|---:|---:|---:|"]
    tr=hl[(hl.sample=="TRAIN_2017_2022")&(hl.horizon==20)&(hl.outcome=="top")]
    po=hl[(hl.sample=="POST_2023_PLUS")&(hl.horizon==20)&(hl.outcome=="top")]
    m=tr.merge(po,on=["universe","target","horizon","outcome","metric"],suffixes=("_tr","_po"))
    m=m[(m.high_minus_low_tr>0)&(m.high_minus_low_po>0)].copy()
    if len(m):
        m["floor"]=m[["high_minus_low_tr","high_minus_low_po"]].min(axis=1)
        for _,r in m.sort_values("floor",ascending=False).head(20).iterrows():
            lines.append(f"| {r.metric} | {r.universe} | {r.target} | {r.high_minus_low_tr:+.2%} | {r.high_minus_low_po:+.2%} | {r.nw_t_tr:+.2f} | {r.nw_t_po:+.2f} |")

    lines += ["", "## Does simple conflict add information beyond FH-B?", "",
              "Conflict beta is from outcome ~ NetBreadth + Conflict. Negative is the expected sign if simultaneous W+ and R- disagreement is harmful.", ""]
    for sample in ("TRAIN_2017_2022","POST_2023_PLUS"):
        z=conflict[(conflict.sample==sample)&(conflict.horizon==20)&(conflict.outcome=="top")]
        if len(z):
            lines.append(f"- {sample}: median conflict beta {z.conflict_beta.median():+.2%}; negative share {(z.conflict_beta<0).mean():.0%}; median NW t {z.conflict_nw_t.median():+.2f}; n cells={len(z)}")
    lines += ["", "## Interpretation rule", "",
              "Prefer the simplest metric that keeps the same economic sign across TRAIN and POST and works across multiple target families/universes. Complexity is not promoted unless it materially improves stability over FH-A/FH-B.", ""]
    return "\n".join(lines)+"\n"


def main() -> None:
    f = pd.read_csv(IN / "family_factor_5d.csv")
    f["date"] = pd.to_datetime(f["date"])
    p = pd.read_csv(IN / "state_panel.csv")
    p["date"] = pd.to_datetime(p["date"])
    fw = build_forward(f, p.universe.unique().tolist())
    hp = build_health_panel(p, fw)
    hl, ic, conflict = summarize_health(hp)
    rob = robustness_table(hl, ic)
    hp.to_csv(OUT / "factor_health_panel.csv", index=False, encoding="utf-8-sig")
    hl.to_csv(OUT / "health_high_low_results.csv", index=False, encoding="utf-8-sig")
    ic.to_csv(OUT / "health_ic_results.csv", index=False, encoding="utf-8-sig")
    conflict.to_csv(OUT / "conflict_incremental_results.csv", index=False, encoding="utf-8-sig")
    rob.to_csv(OUT / "metric_robustness.csv", index=False, encoding="utf-8-sig")
    (OUT / "RESEARCH_SUMMARY.md").write_text(write_summary(rob,hl,conflict),encoding="utf-8")
    print(f"done panel={len(hp)} hl={len(hl)} ic={len(ic)} conflict={len(conflict)} robustness={len(rob)}", flush=True)


if __name__ == "__main__":
    main()
