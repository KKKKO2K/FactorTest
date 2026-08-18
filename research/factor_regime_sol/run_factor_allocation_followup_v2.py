from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
IN = HERE / "results"
OUT = HERE / "results_allocation_followup_v2"
OUT.mkdir(parents=True, exist_ok=True)

FAMILIES = ("MOMENTUM", "REVISION", "VALUE", "FLOW")
ALTS = ("REVISION", "VALUE", "FLOW")
SAMPLES = {
    "TRAIN_2016_2022": (pd.Timestamp("2016-01-01"), pd.Timestamp("2022-12-31")),
    "POST_2023_PLUS": (pd.Timestamp("2023-01-01"), pd.Timestamp("2099-12-31")),
    "POST_2023_2024": (pd.Timestamp("2023-01-01"), pd.Timestamp("2024-12-31")),
    "BULL_2025": (pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
    "YTD_2026": (pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31")),
}


def compound_forward(x: pd.DataFrame, n: int) -> pd.DataFrame:
    out = 1.0 + x.shift(-1)
    for i in range(2, n + 1):
        out *= 1.0 + x.shift(-i)
    return out - 1.0


def nw_tstat(x: pd.Series, lag: int) -> float:
    a = pd.Series(x).dropna().astype(float).to_numpy()
    n = len(a)
    if n < 8:
        return np.nan
    e = a - a.mean()
    gamma0 = float(np.dot(e, e) / n)
    s = gamma0
    L = min(lag, n - 2)
    for l in range(1, L + 1):
        gamma = float(np.dot(e[l:], e[:-l]) / n)
        s += 2.0 * (1.0 - l / (L + 1.0)) * gamma
    se = math.sqrt(max(s, 0.0) / n)
    return float(a.mean() / se) if se > 0 else np.nan


def stat_row(y: pd.Series, h: int) -> dict:
    y = pd.Series(y).dropna().astype(float)
    return {
        "n": len(y),
        "mean": float(y.mean()) if len(y) else np.nan,
        "median": float(y.median()) if len(y) else np.nan,
        "positive_share": float((y > 0).mean()) if len(y) else np.nan,
        "nw_tstat": nw_tstat(y, 0 if h == 5 else 3),
    }


def main():
    f = pd.read_csv(IN / "family_factor_5d.csv")
    f["date"] = pd.to_datetime(f["date"])
    p = pd.read_csv(IN / "state_panel.csv")
    p["date"] = pd.to_datetime(p["date"])

    top5 = f.pivot_table(index=["date", "universe"], columns="family", values="top_abs_5d").sort_index()
    spr5 = f.pivot_table(index=["date", "universe"], columns="family", values="spread_5d").sort_index()

    fw_rows = []
    for u in p["universe"].unique():
        t = top5.xs(u, level="universe").sort_index()
        s = spr5.xs(u, level="universe").sort_index()
        f5t, f5s = t.shift(-1), s.shift(-1)
        f20t, f20s = compound_forward(t, 4), compound_forward(s, 4)
        for dt in t.index:
            r = {"date": dt, "universe": u}
            for fam in FAMILIES:
                r[f"{fam}_top_fwd5"] = f5t.at[dt, fam] if fam in f5t.columns else np.nan
                r[f"{fam}_spread_fwd5"] = f5s.at[dt, fam] if fam in f5s.columns else np.nan
                r[f"{fam}_top_fwd20"] = f20t.at[dt, fam] if fam in f20t.columns else np.nan
                r[f"{fam}_spread_fwd20"] = f20s.at[dt, fam] if fam in f20s.columns else np.nan
            fw_rows.append(r)
    x = p.merge(pd.DataFrame(fw_rows), on=["date", "universe"], how="left")

    # A) Sign persistence: does a currently positive preferred leg predict the same family's future leg/spread?
    persist_rows = []
    for sample, (lo, hi) in SAMPLES.items():
        z0 = x[(x["date"] >= lo) & (x["date"] <= hi)]
        for u, zu in z0.groupby("universe"):
            for fam in FAMILIES:
                cur = f"{fam.lower()}_top_abs20"
                for h in (5, 20):
                    for metric in ("top", "spread"):
                        col = f"{fam}_{metric}_fwd{h}"
                        yp = zu.loc[zu[cur] > 0, col].dropna()
                        yn = zu.loc[zu[cur] <= 0, col].dropna()
                        if len(yp) < 8 or len(yn) < 8:
                            continue
                        sp, sn = stat_row(yp, h), stat_row(yn, h)
                        persist_rows.append({
                            "sample": sample, "universe": u, "family": fam, "horizon": h, "metric": metric,
                            "pos_n": sp["n"], "neg_n": sn["n"], "pos_mean": sp["mean"], "neg_mean": sn["mean"],
                            "pos_minus_neg": sp["mean"] - sn["mean"],
                            "pos_positive_share": sp["positive_share"], "neg_positive_share": sn["positive_share"],
                        })
    persist = pd.DataFrame(persist_rows)
    persist.to_csv(OUT / "sign_persistence_contrasts.csv", index=False, encoding="utf-8-sig")

    # B) Momentum R- individual alternatives and live-positive EW basket.
    ind_events, basket_events = [], []
    for r in x.itertuples(index=False):
        if getattr(r, "momentum_state") != "R-":
            continue
        pos_alts = [fam for fam in ALTS if getattr(r, f"{fam.lower()}_top_abs20") > 0]
        b = {"date": r.date, "universe": r.universe, "n_pos_alt": len(pos_alts), "meta_state": r.meta_state}
        for fam in ALTS:
            ie = {
                "date": r.date, "universe": r.universe, "family": fam,
                "current_positive": int(getattr(r, f"{fam.lower()}_top_abs20") > 0),
                "current_state": getattr(r, f"{fam.lower()}_state"),
            }
            for h in (5, 20):
                for metric in ("top", "spread"):
                    alt = getattr(r, f"{fam}_{metric}_fwd{h}")
                    mom = getattr(r, f"MOMENTUM_{metric}_fwd{h}")
                    ie[f"alt_{metric}_{h}"] = alt
                    ie[f"mom_{metric}_{h}"] = mom
                    ie[f"alt_minus_mom_{metric}_{h}"] = alt - mom if np.isfinite(alt) and np.isfinite(mom) else np.nan
            ind_events.append(ie)
        for h in (5, 20):
            for metric in ("top", "spread"):
                vals = [getattr(r, f"{fam}_{metric}_fwd{h}") for fam in pos_alts]
                vals = [v for v in vals if np.isfinite(v)]
                mom = getattr(r, f"MOMENTUM_{metric}_fwd{h}")
                alt = float(np.mean(vals)) if vals else np.nan
                b[f"pos_alt_{metric}_{h}"] = alt
                b[f"mom_{metric}_{h}"] = mom
                b[f"pos_minus_mom_{metric}_{h}"] = alt - mom if np.isfinite(alt) and np.isfinite(mom) else np.nan
        basket_events.append(b)

    ind = pd.DataFrame(ind_events)
    basket = pd.DataFrame(basket_events)
    ind.to_csv(OUT / "momentum_rminus_individual_events.csv", index=False, encoding="utf-8-sig")
    basket.to_csv(OUT / "momentum_rminus_basket_events.csv", index=False, encoding="utf-8-sig")

    ind_sum, basket_sum = [], []
    for sample, (lo, hi) in SAMPLES.items():
        zi0 = ind[(ind["date"] >= lo) & (ind["date"] <= hi)]
        zb0 = basket[(basket["date"] >= lo) & (basket["date"] <= hi)]
        for (u, fam, cp), z in zi0.groupby(["universe", "family", "current_positive"]):
            for h in (5, 20):
                for metric in ("top", "spread"):
                    col = f"alt_minus_mom_{metric}_{h}"
                    y = z[col].dropna()
                    if len(y) < 8:
                        continue
                    st = stat_row(y, h)
                    ind_sum.append({"sample": sample, "universe": u, "family": fam, "current_positive": int(cp),
                                    "horizon": h, "metric": metric, "series": "ALT_MINUS_MOM", **st})
                    ya = z[f"alt_{metric}_{h}"].dropna()
                    if len(ya) >= 8:
                        sa = stat_row(ya, h)
                        ind_sum.append({"sample": sample, "universe": u, "family": fam, "current_positive": int(cp),
                                        "horizon": h, "metric": metric, "series": "ALT", **sa})
        # pooled primary rule: Momentum R- and at least one currently positive alternative.
        zlive = zb0[zb0["n_pos_alt"] >= 1]
        for h in (5, 20):
            for metric in ("top", "spread"):
                for series, col in (("POS_ALT", f"pos_alt_{metric}_{h}"),
                                    ("MOM", f"mom_{metric}_{h}"),
                                    ("POS_ALT_MINUS_MOM", f"pos_minus_mom_{metric}_{h}")):
                    y = zlive[col].dropna()
                    if len(y) < 8:
                        continue
                    basket_sum.append({"sample": sample, "universe": u if False else None})
        for u, zu in zlive.groupby("universe"):
            for h in (5, 20):
                for metric in ("top", "spread"):
                    for series, col in (("POS_ALT", f"pos_alt_{metric}_{h}"),
                                        ("MOM", f"mom_{metric}_{h}"),
                                        ("POS_ALT_MINUS_MOM", f"pos_minus_mom_{metric}_{h}")):
                        y = zu[col].dropna()
                        if len(y) < 8:
                            continue
                        st = stat_row(y, h)
                        basket_sum.append({"sample": sample, "universe": u, "horizon": h, "metric": metric,
                                           "series": series, "n_pos_rule": ">=1", **st})
            # diagnostic by number of positive alternatives.
            for npos, zn in zu.groupby("n_pos_alt"):
                if npos < 1:
                    continue
                for h in (5, 20):
                    col = f"pos_minus_mom_top_{h}"
                    y = zn[col].dropna()
                    if len(y) < 8:
                        continue
                    st = stat_row(y, h)
                    basket_sum.append({"sample": sample, "universe": u, "horizon": h, "metric": "top",
                                       "series": "POS_ALT_MINUS_MOM_BY_N", "n_pos_rule": str(int(npos)), **st})

    # Remove placeholder rows if any.
    basket_sum = [r for r in basket_sum if r.get("universe") is not None]
    inds = pd.DataFrame(ind_sum)
    baskets = pd.DataFrame(basket_sum)
    inds.to_csv(OUT / "momentum_rminus_individual_summary.csv", index=False, encoding="utf-8-sig")
    baskets.to_csv(OUT / "momentum_rminus_basket_summary.csv", index=False, encoding="utf-8-sig")

    focus = ["K200", "KOSPI_EX_K200", "KOSDAQ", "KOSDAQ_PLUS_KOSPI_EX_K200", "KOSPI_ALL", "KOSPI_KOSDAQ_ALL"]
    lines = [
        "# Factor Allocation Follow-up v2", "",
        "Momentum = exact legacy weighted momentum. State information is fully observed before forward returns.",
        "20D observations overlap on the 5D state grid; NW t-stats (lag 3) are descriptive, not untouched OOS proof.", "",
        "## Sign persistence: current POS minus NEG -> future +20D preferred leg", "",
        "| Sample | Universe | Momentum | Revision | Value | Flow |", "|---|---|---:|---:|---:|---:|",
    ]
    for sample in ("TRAIN_2016_2022", "POST_2023_PLUS"):
        z = persist[(persist["sample"] == sample) & (persist["horizon"] == 20) & (persist["metric"] == "top")]
        for u in focus:
            d = z[z["universe"] == u].set_index("family")
            vals = [d.at[f, "pos_minus_neg"] if f in d.index else np.nan for f in FAMILIES]
            lines.append(f"| {sample} | {u} | " + " | ".join(f"{v:+.2%}" if np.isfinite(v) else "NA" for v in vals) + " |")
    lines += ["", "## Momentum R-: pooled live-positive alternative basket vs staying in Momentum", "",
              "| Sample | Universe | Horizon | Alt-Mom Δ | win rate | NW t | n |", "|---|---|---:|---:|---:|---:|---:|"]
    z = baskets[(baskets["series"] == "POS_ALT_MINUS_MOM") & (baskets["metric"] == "top") & (baskets["n_pos_rule"] == ">=1")]
    for sample in SAMPLES:
        for u in focus:
            for h in (5, 20):
                q = z[(z["sample"] == sample) & (z["universe"] == u) & (z["horizon"] == h)]
                if q.empty:
                    continue
                r = q.iloc[0]
                lines.append(f"| {sample} | {u} | {h}D | {r['mean']:+.2%} | {r['positive_share']:.1%} | {r['nw_tstat']:+.2f} | {int(r['n'])} |")
    lines += ["", "## Momentum R-: individual currently-positive alternative vs Momentum, +20D preferred leg", "",
              "| Sample | Universe | Alt | Δ | win rate | NW t | n |", "|---|---|---|---:|---:|---:|---:|"]
    z = inds[(inds["series"] == "ALT_MINUS_MOM") & (inds["metric"] == "top") & (inds["horizon"] == 20) & (inds["current_positive"] == 1)]
    for sample in SAMPLES:
        for u in focus:
            for fam in ALTS:
                q = z[(z["sample"] == sample) & (z["universe"] == u) & (z["family"] == fam)]
                if q.empty:
                    continue
                r = q.iloc[0]
                lines.append(f"| {sample} | {u} | {fam} | {r['mean']:+.2%} | {r['positive_share']:.1%} | {r['nw_tstat']:+.2f} | {int(r['n'])} |")
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"done persistence={len(persist)} individual_events={len(ind)} basket_events={len(basket)} individual_summary={len(inds)} basket_summary={len(baskets)}", flush=True)


if __name__ == "__main__":
    main()
