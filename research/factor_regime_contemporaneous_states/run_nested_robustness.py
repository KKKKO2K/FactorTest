from __future__ import annotations

import re
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
PANEL = OUT / "contemporaneous_state_vector.csv"
TRAIN_END = pd.Timestamp("2023-01-01")
BASE_FEATURES = ["MKT_RET_20D", "MKT_RET_60D", "MKT_VOL_20D", "MKT_DD_60D", "LIQ_5D_20D"]
FACTOR_CORE = ["ABS_CONFIRMED_BREADTH", "DEFENSIVE_WORKING_BREADTH", "WPLUS_PAIR_SHARE",
               "CONFLICT_PAIR_SHARE", "LEADER_STRENGTH_60D", "SPREAD_DISPERSION_20D"]
PERIODS = {
    "TRAIN": (pd.Timestamp("2016-01-01"), pd.Timestamp("2023-01-01")),
    "VALID_2023_2024": (pd.Timestamp("2023-01-01"), pd.Timestamp("2025-01-01")),
    "STRESS_2025": (pd.Timestamp("2025-01-01"), pd.Timestamp("2026-01-01")),
    "STRESS_2026": (pd.Timestamp("2026-01-01"), pd.Timestamp("2027-01-01")),
}
BASE_KS = (3, 4, 5)
SPLITS = ("KMEANS", "SCORE_MEDIAN")
MIN_SIDE = 8


def fit_base(g: pd.DataFrame, k: int) -> pd.DataFrame | None:
    z = g.dropna(subset=BASE_FEATURES).sort_values("date").copy()
    tr = z[z.date < TRAIN_END]
    if len(tr) < 200:
        return None
    sc = StandardScaler().fit(tr[BASE_FEATURES])
    km = KMeans(n_clusters=k, n_init=50, random_state=42).fit(sc.transform(tr[BASE_FEATURES]))
    raw_tr = km.labels_
    tmp = tr[["MKT_RET_60D", "MKT_RET_20D"]].copy(); tmp["raw"] = raw_tr
    order = tmp.groupby("raw").mean().sort_values(["MKT_RET_60D", "MKT_RET_20D"]).index.tolist()
    mp = {raw: i + 1 for i, raw in enumerate(order)}
    z["base_rank"] = [mp[x] for x in km.predict(sc.transform(z[BASE_FEATURES]))]
    z["base_state"] = "B" + z.base_rank.astype(str)
    # next state on full sequence
    nxt = z.base_rank.shift(-1)
    z["NEXT_UP"] = (nxt > z.base_rank).astype(float)
    z["NEXT_DOWN"] = (nxt < z.base_rank).astype(float)
    z["NEXT_SAME"] = (nxt == z.base_rank).astype(float)
    z.loc[nxt.isna(), ["NEXT_UP", "NEXT_DOWN", "NEXT_SAME"]] = np.nan
    z["base_role"] = np.where(z.base_rank == k, "STRONG", np.where(z.base_rank == 1, "EXTREME_LOW", "REPAIR_MID"))
    return z


def raw_health(g: pd.DataFrame) -> pd.Series:
    # Components already scaled similarly as shares except leader/dispersion; standardize on training before use externally.
    return g["ABS_CONFIRMED_BREADTH"] + g["WPLUS_PAIR_SHARE"] - g["DEFENSIVE_WORKING_BREADTH"] - g["CONFLICT_PAIR_SHARE"]


def assign_factor(g: pd.DataFrame, method: str) -> pd.DataFrame | None:
    z = g.dropna(subset=FACTOR_CORE).sort_values("date").copy()
    tr = z[z.date < TRAIN_END]
    if len(tr) < 40:
        return None
    sc = StandardScaler().fit(tr[FACTOR_CORE])
    xt = sc.transform(tr[FACTOR_CORE]); xa = sc.transform(z[FACTOR_CORE])
    if method == "KMEANS":
        km = KMeans(n_clusters=2, n_init=50, random_state=42).fit(xt)
        if pd.Series(km.labels_).value_counts().min() < 12:
            return None
        cent = pd.DataFrame(km.cluster_centers_, columns=FACTOR_CORE)
        score = cent["ABS_CONFIRMED_BREADTH"] + cent["WPLUS_PAIR_SHARE"] - cent["DEFENSIVE_WORKING_BREADTH"] - cent["CONFLICT_PAIR_SHARE"]
        high_raw = int(score.idxmax())
        pred = km.predict(xa)
        z["factor_substate"] = np.where(pred == high_raw, "F_HIGH", "F_LOW")
    else:
        # transparent continuous health score: z(abs confirmed)+z(pair confirmation)-z(defensive)-z(conflict)
        tr_std = pd.DataFrame(xt, columns=FACTOR_CORE, index=tr.index)
        all_std = pd.DataFrame(xa, columns=FACTOR_CORE, index=z.index)
        htr = tr_std["ABS_CONFIRMED_BREADTH"] + tr_std["WPLUS_PAIR_SHARE"] - tr_std["DEFENSIVE_WORKING_BREADTH"] - tr_std["CONFLICT_PAIR_SHARE"]
        hall = all_std["ABS_CONFIRMED_BREADTH"] + all_std["WPLUS_PAIR_SHARE"] - all_std["DEFENSIVE_WORKING_BREADTH"] - all_std["CONFLICT_PAIR_SHARE"]
        cut = float(htr.median())
        z["factor_substate"] = np.where(hall >= cut, "F_HIGH", "F_LOW")
    return z


def standardized_distance(a: pd.DataFrame, b: pd.DataFrame, cols: list[str], ref: pd.DataFrame) -> float:
    sd = ref[cols].std(ddof=0).replace(0, np.nan)
    d = (a[cols].mean() - b[cols].mean()) / sd
    return float(np.sqrt(np.nansum(d.to_numpy() ** 2)))


def run(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for u, gu in panel.groupby("universe"):
        for k in BASE_KS:
            bz = fit_base(gu, k)
            if bz is None:
                continue
            for rank, gb in bz.groupby("base_rank"):
                for method in SPLITS:
                    fz = assign_factor(gb, method)
                    if fz is None:
                        continue
                    ref = fz[fz.date < TRAIN_END]
                    for per, (lo, hi) in PERIODS.items():
                        p = fz[(fz.date >= lo) & (fz.date < hi)]
                        hh = p[p.factor_substate == "F_HIGH"]
                        ll = p[p.factor_substate == "F_LOW"]
                        if len(hh) < MIN_SIDE or len(ll) < MIN_SIDE:
                            continue
                        row = {"universe": u, "base_k": k, "base_rank": int(rank), "base_state": f"B{rank}",
                               "base_role": "STRONG" if rank == k else ("EXTREME_LOW" if rank == 1 else "REPAIR_MID"),
                               "factor_method": method, "period": per, "n_high": len(hh), "n_low": len(ll),
                               "base_distance_z": standardized_distance(hh, ll, BASE_FEATURES, ref),
                               "factor_distance_z": standardized_distance(hh, ll, FACTOR_CORE, ref)}
                        for c in ["MKT_FWD_20D", "MKT_FWD_DD20", "NEXT_UP", "NEXT_DOWN"]:
                            row[f"{c}_high"] = float(hh[c].mean()); row[f"{c}_low"] = float(ll[c].mean())
                            row[f"{c}_diff"] = row[f"{c}_high"] - row[f"{c}_low"]
                        rows.append(row)
    return pd.DataFrame(rows)


def exact_stability(raw: pd.DataFrame) -> pd.DataFrame:
    keys = ["universe", "base_k", "base_rank", "base_role", "factor_method"]
    rows = []
    for key, g in raw.groupby(keys):
        tr = g[g.period == "TRAIN"]
        va = g[g.period == "VALID_2023_2024"]
        if tr.empty or va.empty:
            continue
        t, v = tr.iloc[0], va.iloc[0]
        for out in ["NEXT_UP", "NEXT_DOWN", "MKT_FWD_20D", "MKT_FWD_DD20"]:
            td, vd = t[f"{out}_diff"], v[f"{out}_diff"]
            rows.append({**dict(zip(keys, key)), "outcome": out, "train_diff": td, "valid_diff": vd,
                         "same_sign": float(np.sign(td) == np.sign(vd)),
                         "train_n_min": min(t.n_high, t.n_low), "valid_n_min": min(v.n_high, v.n_low),
                         "train_base_dist": t.base_distance_z, "valid_base_dist": v.base_distance_z,
                         "train_factor_dist": t.factor_distance_z, "valid_factor_dist": v.factor_distance_z})
    return pd.DataFrame(rows)


def hypothesis_aggregate(stab: pd.DataFrame) -> pd.DataFrame:
    specs = {
        "REPAIR_UP": ("REPAIR_MID", "NEXT_UP", 1),
        "REPAIR_DOWN": ("REPAIR_MID", "NEXT_DOWN", -1),
        "STRONG_RETURN": ("STRONG", "MKT_FWD_20D", -1),
        "STRONG_DOWNSIDE": ("STRONG", "MKT_FWD_DD20", -1),
    }
    rows = []
    for name, (role, outcome, expected) in specs.items():
        z = stab[(stab.base_role == role) & (stab.outcome == outcome)].copy()
        for method, gm in z.groupby("factor_method"):
            for u, gu in gm.groupby("universe"):
                rows.append({"hypothesis": name, "factor_method": method, "universe": u, "n_specs": len(gu),
                             "train_expected_share": float((np.sign(gu.train_diff) == expected).mean()),
                             "valid_expected_share": float((np.sign(gu.valid_diff) == expected).mean()),
                             "train_valid_same_sign_share": float(gu.same_sign.mean()),
                             "median_train_diff": float(gu.train_diff.median()), "median_valid_diff": float(gu.valid_diff.median())})
            rows.append({"hypothesis": name, "factor_method": method, "universe": "ALL_UNIVERSES", "n_specs": len(gm),
                         "train_expected_share": float((np.sign(gm.train_diff) == expected).mean()),
                         "valid_expected_share": float((np.sign(gm.valid_diff) == expected).mean()),
                         "train_valid_same_sign_share": float(gm.same_sign.mean()),
                         "median_train_diff": float(gm.train_diff.median()), "median_valid_diff": float(gm.valid_diff.median())})
    return pd.DataFrame(rows)


def stress_compare(raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    keys = ["universe", "base_k", "base_rank", "base_role", "factor_method"]
    for key, g in raw.groupby(keys):
        va = g[g.period == "VALID_2023_2024"]
        if va.empty:
            continue
        v = va.iloc[0]
        for stress in ["STRESS_2025", "STRESS_2026"]:
            ss = g[g.period == stress]
            if ss.empty:
                continue
            s = ss.iloc[0]
            for out in ["NEXT_UP", "NEXT_DOWN", "MKT_FWD_20D", "MKT_FWD_DD20"]:
                rows.append({**dict(zip(keys, key)), "stress_period": stress, "outcome": out,
                             "valid_diff": v[f"{out}_diff"], "stress_diff": s[f"{out}_diff"],
                             "same_sign": float(np.sign(v[f"{out}_diff"]) == np.sign(s[f"{out}_diff"])),
                             "stress_n_min": min(s.n_high, s.n_low)})
    return pd.DataFrame(rows)


def write_summary(agg: pd.DataFrame, stab: pd.DataFrame, stress: pd.DataFrame) -> str:
    lines = ["# Nested Regime Robustness", "",
             "BASE market/liquidity KMeans K=3/4/5; factor substate tested two ways: KMeans and a transparent TRAIN-median continuous factor-health score. No future outcome enters classification.", "",
             "## Predeclared cross-spec hypotheses", ""]
    for method in SPLITS:
        lines.append(f"### {method}")
        q = agg[(agg.factor_method == method) & (agg.universe == "ALL_UNIVERSES")]
        for _, r in q.iterrows():
            lines.append(f"- {r.hypothesis}: specs={int(r.n_specs)}, expected sign TRAIN {r.train_expected_share:.0%}, 23-24 {r.valid_expected_share:.0%}, TRAIN/VALID same sign {r.train_valid_same_sign_share:.0%}; median diff {r.median_train_diff:+.2%} -> {r.median_valid_diff:+.2%}")
    lines += ["", "## Strongest exact TRAIN -> 2023-2024 stable relations", ""]
    z = stab[(stab.same_sign == 1) & (stab.valid_n_min >= 8)].copy()
    z["score"] = z.valid_diff.abs()
    for _, r in z.sort_values("score", ascending=False).head(35).iterrows():
        lines.append(f"- {r.factor_method} {r.universe} K{int(r.base_k)} {r.base_state}/{r.base_role} {r.outcome}: {r.train_diff:+.2%} -> {r.valid_diff:+.2%}; nmin {int(r.train_n_min)}/{int(r.valid_n_min)}; base dist {r.train_base_dist:.2f}/{r.valid_base_dist:.2f}z, factor dist {r.train_factor_dist:.2f}/{r.valid_factor_dist:.2f}z")
    lines += ["", "## 2025/2026 stress sign retention", ""]
    if stress.empty:
        lines.append("- No stress cells retained at least 8 observations per factor substate.")
    else:
        for period in ["STRESS_2025", "STRESS_2026"]:
            q = stress[stress.stress_period == period]
            if q.empty: continue
            for out in ["NEXT_UP", "NEXT_DOWN", "MKT_FWD_20D", "MKT_FWD_DD20"]:
                x = q[q.outcome == out]
                if len(x): lines.append(f"- {period} {out}: sign retained vs 2023-24 in {x.same_sign.mean():.0%} of {len(x)} eligible specs")
    lines += ["", "## Interpretation", "",
             "- Structural evidence requires agreement across BASE K and factor-split definitions, not one chosen cluster solution.",
             "- REPAIR_MID transition effects are the main contemporaneous-regime hypothesis; STRONG-state return/downside reversal is a separate maturity/crowding hypothesis.",
             "- Stress years are not expected to preserve all signs; systematic breaks are themselves regime-dependence evidence.", ""]
    return "\n".join(lines) + "\n"


def main():
    p = pd.read_csv(PANEL); p["date"] = pd.to_datetime(p["date"])
    raw = run(p)
    stab = exact_stability(raw)
    agg = hypothesis_aggregate(stab)
    stress = stress_compare(raw)
    raw.to_csv(OUT / "nested_robustness_raw.csv", index=False, encoding="utf-8-sig")
    stab.to_csv(OUT / "nested_robustness_stability.csv", index=False, encoding="utf-8-sig")
    agg.to_csv(OUT / "nested_robustness_hypotheses.csv", index=False, encoding="utf-8-sig")
    stress.to_csv(OUT / "nested_robustness_stress.csv", index=False, encoding="utf-8-sig")
    (OUT / "NESTED_ROBUSTNESS_SUMMARY.md").write_text(write_summary(agg, stab, stress), encoding="utf-8")
    print(len(raw), len(stab), len(stress))

if __name__ == "__main__":
    main()
