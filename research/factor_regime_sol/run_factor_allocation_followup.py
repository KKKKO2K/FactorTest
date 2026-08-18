from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
IN = HERE / "results"
OUT = HERE / "results_allocation_followup"
OUT.mkdir(parents=True, exist_ok=True)

SPLIT = pd.Timestamp("2023-01-01")
FAMILIES = ("MOMENTUM", "REVISION", "VALUE", "FLOW")
SAMPLES = {
    "TRAIN_2016_2022": (pd.Timestamp("2016-01-01"), pd.Timestamp("2022-12-31")),
    "POST_2023_PLUS": (pd.Timestamp("2023-01-01"), pd.Timestamp("2099-12-31")),
    "POST_2023_2024": (pd.Timestamp("2023-01-01"), pd.Timestamp("2024-12-31")),
    "BULL_2025": (pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
    "YTD_2026": (pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31")),
}


def compound_rows(x: pd.DataFrame, n: int) -> pd.DataFrame:
    out = 1.0 + x.shift(-1)
    for i in range(2, n + 1):
        out = out * (1.0 + x.shift(-i))
    return out - 1.0


def tstat(x: pd.Series) -> float:
    x = x.dropna()
    if len(x) < 5:
        return np.nan
    sd = x.std(ddof=1)
    return float(x.mean() / (sd / math.sqrt(len(x)))) if sd > 0 else np.nan


def main():
    f = pd.read_csv(IN / "family_factor_5d.csv")
    f["date"] = pd.to_datetime(f["date"])
    p = pd.read_csv(IN / "state_panel.csv")
    p["date"] = pd.to_datetime(p["date"])

    # Forward realized family preferred-leg and spread returns from state date t.
    top5 = f.pivot_table(index=["date", "universe"], columns="family", values="top_abs_5d").sort_index()
    spr5 = f.pivot_table(index=["date", "universe"], columns="family", values="spread_5d").sort_index()

    # Compute within each universe to avoid MultiIndex shift crossing universe boundaries.
    fwd_rows = []
    for u in p.universe.unique():
        t = top5.xs(u, level="universe").sort_index()
        s = spr5.xs(u, level="universe").sort_index()
        ft5 = t.shift(-1); fs5 = s.shift(-1)
        ft20 = compound_rows(t, 4); fs20 = compound_rows(s, 4)
        for dt in t.index:
            row = {"date": dt, "universe": u}
            for fam in FAMILIES:
                row[f"{fam}_top_fwd5"] = ft5.at[dt, fam] if fam in ft5.columns else np.nan
                row[f"{fam}_spread_fwd5"] = fs5.at[dt, fam] if fam in fs5.columns else np.nan
                row[f"{fam}_top_fwd20"] = ft20.at[dt, fam] if fam in ft20.columns else np.nan
                row[f"{fam}_spread_fwd20"] = fs20.at[dt, fam] if fam in fs20.columns else np.nan
            fwd_rows.append(row)
    fw = pd.DataFrame(fwd_rows)
    x = p.merge(fw, on=["date", "universe"], how="left")

    # 1) Does current preferred-leg sign/state predict that same family's future return?
    persistence = []
    for sample, (lo, hi) in SAMPLES.items():
        z0 = x[(x.date >= lo) & (x.date <= hi)]
        for u, zu in z0.groupby("universe"):
            for fam in FAMILIES:
                stc = f"{fam.lower()}_state"
                abs_c = f"{fam.lower()}_top_abs20"
                for current_sign, mask in (("POS", zu[abs_c] > 0), ("NEG", zu[abs_c] <= 0)):
                    z = zu[mask]
                    for h in (5, 20):
                        for metric in ("top", "spread"):
                            c = f"{fam}_{metric}_fwd{h}"
                            y = z[c].dropna()
                            if len(y) < 8: continue
                            persistence.append({
                                "sample": sample, "universe": u, "family": fam, "current_abs_sign": current_sign,
                                "horizon": h, "metric": metric, "n": len(y), "mean": float(y.mean()),
                                "positive_share": float((y > 0).mean()), "tstat": tstat(y),
                            })
                for state, z in zu.groupby(stc):
                    if len(z) < 8: continue
                    for h in (5,20):
                        c = f"{fam}_top_fwd{h}"
                        y = z[c].dropna()
                        if len(y) < 8: continue
                        persistence.append({
                            "sample": sample, "universe": u, "family": fam, "current_abs_sign": f"STATE_{state}",
                            "horizon": h, "metric": "top", "n": len(y), "mean": float(y.mean()),
                            "positive_share": float((y > 0).mean()), "tstat": tstat(y),
                        })
    pers = pd.DataFrame(persistence)
    pers.to_csv(OUT / "family_persistence.csv", index=False, encoding="utf-8-sig")

    # 2) Momentum R-: basket of currently positive alternative families vs negative alternatives and Momentum.
    rot_rows = []
    for r in x.itertuples(index=False):
        if getattr(r, "momentum_state") != "R-":
            continue
        pos, neg = [], []
        for fam in ("REVISION", "VALUE", "FLOW"):
            cur = getattr(r, f"{fam.lower()}_top_abs20")
            (pos if cur > 0 else neg).append(fam)
        row = {"date": r.date, "universe": r.universe, "n_pos_alt": len(pos), "meta_state": r.meta_state}
        for h in (5,20):
            for metric in ("top","spread"):
                mom = getattr(r, f"MOMENTUM_{metric}_fwd{h}")
                pv = [getattr(r, f"{fam}_{metric}_fwd{h}") for fam in pos]
                nv = [getattr(r, f"{fam}_{metric}_fwd{h}") for fam in neg]
                row[f"mom_{metric}_{h}"] = mom
                row[f"pos_alt_{metric}_{h}"] = float(np.nanmean(pv)) if pv else np.nan
                row[f"neg_alt_{metric}_{h}"] = float(np.nanmean(nv)) if nv else np.nan
                row[f"pos_minus_mom_{metric}_{h}"] = row[f"pos_alt_{metric}_{h}"] - mom if np.isfinite(row[f"pos_alt_{metric}_{h}"]) and np.isfinite(mom) else np.nan
        rot_rows.append(row)
    rot = pd.DataFrame(rot_rows)
    rot.to_csv(OUT / "momentum_rminus_events.csv", index=False, encoding="utf-8-sig")

    summaries = []
    for sample, (lo, hi) in SAMPLES.items():
        z0 = rot[(rot.date >= lo) & (rot.date <= hi)]
        for (u, npos), z in z0.groupby(["universe", "n_pos_alt"]):
            for h in (5,20):
                for metric in ("top","spread"):
                    for c in (f"pos_alt_{metric}_{h}", f"neg_alt_{metric}_{h}", f"mom_{metric}_{h}", f"pos_minus_mom_{metric}_{h}"):
                        y = z[c].dropna()
                        if len(y) < 8: continue
                        summaries.append({
                            "sample": sample, "universe": u, "n_pos_alt": int(npos), "horizon": h,
                            "metric": metric, "series": c, "n": len(y), "mean": float(y.mean()),
                            "positive_share": float((y > 0).mean()), "tstat": tstat(y),
                        })
    sm = pd.DataFrame(summaries)
    sm.to_csv(OUT / "momentum_rminus_summary.csv", index=False, encoding="utf-8-sig")

    # Simple sign-persistence contrast: current POS minus NEG for same family.
    contrasts = []
    q = pers[pers.current_abs_sign.isin(["POS","NEG"])]
    keys = ["sample","universe","family","horizon","metric"]
    for key, g in q.groupby(keys):
        d = g.set_index("current_abs_sign")
        if "POS" not in d.index or "NEG" not in d.index: continue
        a,b = d.loc["POS"], d.loc["NEG"]
        contrasts.append(dict(zip(keys,key)) | {
            "pos_n": int(a.n), "neg_n": int(b.n), "pos_mean": float(a["mean"]), "neg_mean": float(b["mean"]),
            "pos_minus_neg": float(a["mean"]-b["mean"]),
            "pos_positive_share": float(a.positive_share), "neg_positive_share": float(b.positive_share),
        })
    con = pd.DataFrame(contrasts)
    con.to_csv(OUT / "sign_persistence_contrasts.csv", index=False, encoding="utf-8-sig")

    lines = ["# Factor-state allocation follow-up", "", "Does a positive preferred leg persist, and can live alternatives replace Momentum during Momentum R-?", ""]
    for sample in ("TRAIN_2016_2022","POST_2023_PLUS"):
        lines += [f"## {sample}: current preferred-leg POS minus NEG -> future +20D preferred leg", "", "| Universe | Family | POS-NEG | POS mean | NEG mean |", "|---|---|---:|---:|---:|"]
        z = con[(con.sample==sample)&(con.horizon==20)&(con.metric=="top")]
        for _, rr in z.iterrows():
            lines.append(f"| {rr.universe} | {rr.family} | {rr.pos_minus_neg:+.2%} | {rr.pos_mean:+.2%} | {rr.neg_mean:+.2%} |")
        lines.append("")
    lines += ["## Momentum R-: currently positive alternative basket minus Momentum, +20D preferred leg", "", "| Sample | Universe | # positive alts | Δ | n |", "|---|---|---:|---:|---:|"]
    z = sm[(sm.horizon==20)&(sm.metric=="top")&(sm.series=="pos_minus_mom_top_20")]
    for _, rr in z.iterrows():
        lines.append(f"| {rr['sample']} | {rr.universe} | {int(rr.n_pos_alt)} | {rr['mean']:+.2%} | {int(rr.n)} |")
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"done persistence={len(pers)} events={len(rot)} summaries={len(sm)}", flush=True)


if __name__ == "__main__":
    main()
