from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
PANEL = OUT / "contemporaneous_state_vector.csv"
TRAIN_END = pd.Timestamp("2023-01-01")
BASE_K = 4
MIN_SUB_N = 15

BASE_FEATURES = ["MKT_RET_20D", "MKT_RET_60D", "MKT_VOL_20D", "MKT_DD_60D", "LIQ_5D_20D"]
FACTOR_CORE = [
    "ABS_CONFIRMED_BREADTH", "DEFENSIVE_WORKING_BREADTH", "WPLUS_PAIR_SHARE",
    "CONFLICT_PAIR_SHARE", "LEADER_STRENGTH_60D", "SPREAD_DISPERSION_20D",
]
OUTCOMES = ["MKT_FWD_5D", "MKT_FWD_20D", "MKT_FWD_DD20", "MKT_FWD_VOL20"]
PERIODS = {
    "TRAIN_2016_2022": (pd.Timestamp("2016-01-01"), pd.Timestamp("2023-01-01")),
    "NORMAL_2023_2024": (pd.Timestamp("2023-01-01"), pd.Timestamp("2025-01-01")),
    "STRONG_2025": (pd.Timestamp("2025-01-01"), pd.Timestamp("2026-01-01")),
    "HYPER_2026_YTD": (pd.Timestamp("2026-01-01"), pd.Timestamp("2027-01-01")),
}


def period_name(dt: pd.Timestamp) -> str:
    for name, (lo, hi) in PERIODS.items():
        if lo <= dt < hi:
            return name
    return "OTHER"


def assign_base_states(g: pd.DataFrame) -> tuple[pd.DataFrame, dict] | None:
    z = g.dropna(subset=BASE_FEATURES).sort_values("date").copy()
    tr = z[z.date < TRAIN_END].copy()
    if len(tr) < 200:
        return None
    scaler = StandardScaler().fit(tr[BASE_FEATURES])
    xt = scaler.transform(tr[BASE_FEATURES])
    xa = scaler.transform(z[BASE_FEATURES])
    model = KMeans(n_clusters=BASE_K, n_init=50, random_state=42)
    raw_tr = model.fit_predict(xt)
    raw_all = model.predict(xa)
    tmp = tr[["MKT_RET_60D", "MKT_RET_20D"]].copy()
    tmp["raw"] = raw_tr
    order = tmp.groupby("raw").mean().sort_values(["MKT_RET_60D", "MKT_RET_20D"]).index.tolist()
    mapping = {raw: f"B{i+1}" for i, raw in enumerate(order)}
    z["base_state"] = [mapping[x] for x in raw_all]
    tr["base_state"] = [mapping[x] for x in raw_tr]
    sil = float(silhouette_score(xt, raw_tr))
    same = float((z.base_state.iloc[1:].to_numpy() == z.base_state.iloc[:-1].to_numpy()).mean())
    meta = {"silhouette": sil, "persistence": same}
    return z, meta


def health_score(centroid: pd.Series) -> float:
    return float(centroid["ABS_CONFIRMED_BREADTH"] + centroid["WPLUS_PAIR_SHARE"]
                 - centroid["DEFENSIVE_WORKING_BREADTH"] - centroid["CONFLICT_PAIR_SHARE"])


def fit_factor_substates(z: pd.DataFrame, universe: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    assigned = []
    meta = []
    for bs, g0 in z.groupby("base_state"):
        g = g0.dropna(subset=FACTOR_CORE).sort_values("date").copy()
        tr = g[g.date < TRAIN_END].copy()
        if len(tr) < 50:
            continue
        scaler = StandardScaler().fit(tr[FACTOR_CORE])
        xt = scaler.transform(tr[FACTOR_CORE])
        model = KMeans(n_clusters=2, n_init=50, random_state=42)
        raw_tr = model.fit_predict(xt)
        counts = pd.Series(raw_tr).value_counts()
        if counts.min() < MIN_SUB_N:
            continue
        raw_all = model.predict(scaler.transform(g[FACTOR_CORE]))
        cent = pd.DataFrame(model.cluster_centers_, columns=FACTOR_CORE)
        scores = {i: health_score(cent.loc[i]) for i in cent.index}
        low = min(scores, key=scores.get)
        mapping = {low: "F_LOW", 1 - low: "F_HIGH"}
        g["factor_substate"] = [mapping[x] for x in raw_all]
        assigned.append(g)
        meta.append({"universe": universe, "base_state": bs, "train_n": len(tr),
                     "low_n": int((raw_tr == low).sum()), "high_n": int((raw_tr != low).sum()),
                     "factor_silhouette": float(silhouette_score(xt, raw_tr)),
                     "factor_centroid_distance_z": float(np.linalg.norm(cent.loc[0] - cent.loc[1])),
                     "health_low": float(scores[low]), "health_high": float(scores[1-low])})
    return (pd.concat(assigned, ignore_index=True) if assigned else pd.DataFrame(), pd.DataFrame(meta))


def state_numeric(s: pd.Series) -> pd.Series:
    return s.str.extract(r"(\d+)", expand=False).astype(float)


def add_transition_targets(z: pd.DataFrame) -> pd.DataFrame:
    x = z.sort_values("date").copy()
    current = state_numeric(x.base_state)
    nxt = state_numeric(x.base_state.shift(-1))
    delta = nxt - current
    x["NEXT_BASE_UP"] = (delta > 0).astype(float)
    x["NEXT_BASE_DOWN"] = (delta < 0).astype(float)
    x["NEXT_BASE_SAME"] = (delta == 0).astype(float)
    x.loc[nxt.isna(), ["NEXT_BASE_UP", "NEXT_BASE_DOWN", "NEXT_BASE_SAME"]] = np.nan
    return x


def standardized_distance(a: pd.DataFrame, b: pd.DataFrame, cols: list[str], reference: pd.DataFrame) -> float:
    sd = reference[cols].std(ddof=0).replace(0, np.nan)
    diff = (a[cols].mean() - b[cols].mean()) / sd
    return float(np.sqrt(np.nansum(diff.to_numpy() ** 2)))


def summarize_nested(nested: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    contrasts = []
    for (u, bs), g0 in nested.groupby(["universe", "base_state"]):
        g = add_transition_targets(g0)
        tr_ref = g[g.date < TRAIN_END]
        for period, (lo, hi) in PERIODS.items():
            p = g[(g.date >= lo) & (g.date < hi)]
            if p.empty:
                continue
            subs = {}
            for fs, q in p.groupby("factor_substate"):
                if len(q) < 5:
                    continue
                subs[fs] = q
                row = {"universe": u, "base_state": bs, "period": period, "factor_substate": fs, "n": len(q)}
                for c in BASE_FEATURES + FACTOR_CORE + OUTCOMES + ["NEXT_BASE_UP", "NEXT_BASE_DOWN", "NEXT_BASE_SAME"]:
                    row[c] = float(q[c].mean()) if q[c].notna().any() else np.nan
                rows.append(row)
            if "F_HIGH" in subs and "F_LOW" in subs and len(subs["F_HIGH"]) >= 8 and len(subs["F_LOW"]) >= 8:
                hiq, loq = subs["F_HIGH"], subs["F_LOW"]
                c = {"universe": u, "base_state": bs, "period": period,
                     "n_high": len(hiq), "n_low": len(loq),
                     "base_distance_z": standardized_distance(hiq, loq, BASE_FEATURES, tr_ref),
                     "factor_distance_z": standardized_distance(hiq, loq, FACTOR_CORE, tr_ref)}
                for col in OUTCOMES + ["NEXT_BASE_UP", "NEXT_BASE_DOWN", "NEXT_BASE_SAME"]:
                    c[f"{col}_high"] = float(hiq[col].mean())
                    c[f"{col}_low"] = float(loq[col].mean())
                    c[f"{col}_diff"] = c[f"{col}_high"] - c[f"{col}_low"]
                contrasts.append(c)
    return pd.DataFrame(rows), pd.DataFrame(contrasts)


def stability_table(contrasts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if contrasts.empty:
        return pd.DataFrame()
    keys = ["universe", "base_state"]
    for key, g in contrasts.groupby(keys):
        tr = g[g.period == "TRAIN_2016_2022"]
        va = g[g.period == "NORMAL_2023_2024"]
        if tr.empty or va.empty:
            continue
        t, v = tr.iloc[0], va.iloc[0]
        for outcome in ["MKT_FWD_20D", "MKT_FWD_DD20", "NEXT_BASE_UP", "NEXT_BASE_DOWN"]:
            td = t[f"{outcome}_diff"]; vd = v[f"{outcome}_diff"]
            rows.append({"universe": key[0], "base_state": key[1], "outcome": outcome,
                         "train_diff": td, "valid_diff": vd,
                         "same_sign": float(np.sign(td) == np.sign(vd)),
                         "train_base_distance_z": t.base_distance_z, "valid_base_distance_z": v.base_distance_z,
                         "train_factor_distance_z": t.factor_distance_z, "valid_factor_distance_z": v.factor_distance_z,
                         "train_n_min": min(t.n_high, t.n_low), "valid_n_min": min(v.n_high, v.n_low)})
    return pd.DataFrame(rows)


def base_profiles(z: pd.DataFrame, universe: str, meta: dict) -> pd.DataFrame:
    rows = []
    z = add_transition_targets(z)
    for bs, g in z.groupby("base_state"):
        tr = g[g.date < TRAIN_END]
        rows.append({"universe": universe, "base_state": bs, "train_n": len(tr),
                     "base_silhouette": meta["silhouette"], "base_persistence": meta["persistence"],
                     **{c: float(tr[c].mean()) for c in BASE_FEATURES},
                     "MKT_FWD_20D": float(tr.MKT_FWD_20D.mean()), "MKT_FWD_DD20": float(tr.MKT_FWD_DD20.mean()),
                     "NEXT_BASE_UP": float(tr.NEXT_BASE_UP.mean()), "NEXT_BASE_DOWN": float(tr.NEXT_BASE_DOWN.mean())})
    return pd.DataFrame(rows)


def write_summary(base_prof: pd.DataFrame, sub_meta: pd.DataFrame, contrasts: pd.DataFrame, stability: pd.DataFrame) -> str:
    lines = [
        "# Nested Contemporaneous Regime Test", "",
        "Question: after defining the current market/liquidity regime with only market trend, volatility, drawdown and trading-value breadth, do factor interactions split that same regime into economically distinct contemporaneous sub-regimes?", "",
        "Procedure: KMeans BASE K=4 fit on 2016-2022 and frozen. Within each BASE state, KMeans K=2 is fit only on six factor-interaction variables and frozen. F_HIGH/F_LOW are ordered by a contemporaneous factor-health score; no forward outcome enters fitting or naming.", "",
        "## BASE state profiles", "",
    ]
    for u in [x for x in ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"] if x in base_prof.universe.unique()]:
        q = base_prof[base_prof.universe == u].sort_values("base_state")
        lines.append(f"### {u}")
        for _, r in q.iterrows():
            lines.append(f"- {r.base_state}: n={int(r.train_n)}, ret60 {r.MKT_RET_60D:+.1%}, vol20 {r.MKT_VOL_20D:.1%}, DD60 {r.MKT_DD_60D:+.1%}, liq {r.LIQ_5D_20D:.0%}; next20 {r.MKT_FWD_20D:+.2%}")

    lines += ["", "## Factor sub-state contrasts that survive TRAIN -> 2023-2024", ""]
    if stability.empty:
        lines.append("- No base-state/factor-substate contrast had enough observations in both TRAIN and 2023-2024.")
    else:
        s = stability[(stability.same_sign == 1) & (stability.valid_n_min >= 8)].copy()
        s["importance"] = s.valid_diff.abs()
        for _, r in s.sort_values("importance", ascending=False).head(30).iterrows():
            lines.append(f"- {r.universe} {r.base_state} {r.outcome}: F_HIGH-F_LOW TRAIN {r.train_diff:+.2%}, 23-24 {r.valid_diff:+.2%}; min n {int(r.train_n_min)}/{int(r.valid_n_min)}; base distance {r.train_base_distance_z:.2f}z/{r.valid_base_distance_z:.2f}z, factor distance {r.train_factor_distance_z:.2f}z/{r.valid_factor_distance_z:.2f}z")

    lines += ["", "## All 2023-2024 nested contrasts with adequate n", ""]
    if not contrasts.empty:
        q = contrasts[contrasts.period == "NORMAL_2023_2024"].copy()
        for _, r in q.sort_values("MKT_FWD_20D_diff", key=lambda x: x.abs(), ascending=False).head(25).iterrows():
            lines.append(f"- {r.universe} {r.base_state}: n H/L={int(r.n_high)}/{int(r.n_low)}, base distance {r.base_distance_z:.2f}z, factor distance {r.factor_distance_z:.2f}z; next20 diff {r.MKT_FWD_20D_diff:+.2%}, downside diff {r.MKT_FWD_DD20_diff:+.2%}, next-base-up diff {r.NEXT_BASE_UP_diff:+.1%}")

    lines += ["", "## Interpretation rules", "",
              "- The strongest evidence for incremental factor-state information is: small BASE-feature distance, large factor-feature distance, adequate samples, and same-direction TRAIN/2023-2024 differences in transition or downside/return outcomes.",
              "- 2025 and 2026 are stress/regime diagnostics, not pooled validation.",
              "- If no stable nested split survives, factor interaction is better treated as descriptive context rather than a standalone contemporaneous regime discriminator.", ""]
    return "\n".join(lines) + "\n"


def main() -> None:
    panel = pd.read_csv(PANEL)
    panel["date"] = pd.to_datetime(panel["date"])
    all_nested, all_meta, all_base = [], [], []
    for u, g in panel.groupby("universe"):
        fit = assign_base_states(g)
        if fit is None:
            continue
        z, bmeta = fit
        bp = base_profiles(z, u, bmeta)
        all_base.append(bp)
        nested, meta = fit_factor_substates(z, u)
        if not nested.empty:
            all_nested.append(nested)
        if not meta.empty:
            all_meta.append(meta)
    base_prof = pd.concat(all_base, ignore_index=True) if all_base else pd.DataFrame()
    nested = pd.concat(all_nested, ignore_index=True) if all_nested else pd.DataFrame()
    sub_meta = pd.concat(all_meta, ignore_index=True) if all_meta else pd.DataFrame()
    summary, contrasts = summarize_nested(nested) if not nested.empty else (pd.DataFrame(), pd.DataFrame())
    stability = stability_table(contrasts)

    base_prof.to_csv(OUT / "nested_base_profiles.csv", index=False, encoding="utf-8-sig")
    sub_meta.to_csv(OUT / "nested_factor_substate_meta.csv", index=False, encoding="utf-8-sig")
    nested.to_csv(OUT / "nested_state_assignments.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "nested_state_summary.csv", index=False, encoding="utf-8-sig")
    contrasts.to_csv(OUT / "nested_factor_contrasts.csv", index=False, encoding="utf-8-sig")
    stability.to_csv(OUT / "nested_contrast_stability.csv", index=False, encoding="utf-8-sig")
    (OUT / "NESTED_RESEARCH_SUMMARY.md").write_text(write_summary(base_prof, sub_meta, contrasts, stability), encoding="utf-8")
    print(f"nested assignments: {len(nested):,}; contrasts: {len(contrasts):,}; stability rows: {len(stability):,}")


if __name__ == "__main__":
    main()
