from __future__ import annotations

import numpy as np
import pandas as pd

import run_nested_factor_regimes as base


def summarize_nested_fixed(nested: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    contrasts = []
    for (u, bs), g0 in nested.groupby(["universe", "base_state"]):
        g = g0.sort_values("date").copy()
        tr_ref = g[g.date < base.TRAIN_END]
        for period, (lo, hi) in base.PERIODS.items():
            p = g[(g.date >= lo) & (g.date < hi)]
            if p.empty:
                continue
            subs = {}
            for fs, q in p.groupby("factor_substate"):
                if len(q) < 5:
                    continue
                subs[fs] = q
                row = {"universe": u, "base_state": bs, "period": period, "factor_substate": fs, "n": len(q)}
                for c in base.BASE_FEATURES + base.FACTOR_CORE + base.OUTCOMES + ["NEXT_BASE_UP", "NEXT_BASE_DOWN", "NEXT_BASE_SAME"]:
                    row[c] = float(q[c].mean()) if q[c].notna().any() else np.nan
                rows.append(row)
            if "F_HIGH" in subs and "F_LOW" in subs and len(subs["F_HIGH"]) >= 8 and len(subs["F_LOW"]) >= 8:
                hiq, loq = subs["F_HIGH"], subs["F_LOW"]
                c = {"universe": u, "base_state": bs, "period": period,
                     "n_high": len(hiq), "n_low": len(loq),
                     "base_distance_z": base.standardized_distance(hiq, loq, base.BASE_FEATURES, tr_ref),
                     "factor_distance_z": base.standardized_distance(hiq, loq, base.FACTOR_CORE, tr_ref)}
                for col in base.OUTCOMES + ["NEXT_BASE_UP", "NEXT_BASE_DOWN", "NEXT_BASE_SAME"]:
                    c[f"{col}_high"] = float(hiq[col].mean())
                    c[f"{col}_low"] = float(loq[col].mean())
                    c[f"{col}_diff"] = c[f"{col}_high"] - c[f"{col}_low"]
                contrasts.append(c)
    return pd.DataFrame(rows), pd.DataFrame(contrasts)


def main_fixed() -> None:
    panel = pd.read_csv(base.PANEL)
    panel["date"] = pd.to_datetime(panel["date"])
    all_nested, all_meta, all_base = [], [], []
    for u, g in panel.groupby("universe"):
        fit = base.assign_base_states(g)
        if fit is None:
            continue
        z, bmeta = fit
        z = base.add_transition_targets(z)
        all_base.append(base.base_profiles(z, u, bmeta))
        nested, meta = base.fit_factor_substates(z, u)
        if not nested.empty:
            all_nested.append(nested)
        if not meta.empty:
            all_meta.append(meta)
    base_prof = pd.concat(all_base, ignore_index=True) if all_base else pd.DataFrame()
    nested = pd.concat(all_nested, ignore_index=True) if all_nested else pd.DataFrame()
    sub_meta = pd.concat(all_meta, ignore_index=True) if all_meta else pd.DataFrame()
    summary, contrasts = summarize_nested_fixed(nested) if not nested.empty else (pd.DataFrame(), pd.DataFrame())
    stability = base.stability_table(contrasts)

    base_prof.to_csv(base.OUT / "nested_base_profiles.csv", index=False, encoding="utf-8-sig")
    sub_meta.to_csv(base.OUT / "nested_factor_substate_meta.csv", index=False, encoding="utf-8-sig")
    nested.to_csv(base.OUT / "nested_state_assignments.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(base.OUT / "nested_state_summary.csv", index=False, encoding="utf-8-sig")
    contrasts.to_csv(base.OUT / "nested_factor_contrasts.csv", index=False, encoding="utf-8-sig")
    stability.to_csv(base.OUT / "nested_contrast_stability.csv", index=False, encoding="utf-8-sig")
    (base.OUT / "NESTED_RESEARCH_SUMMARY.md").write_text(base.write_summary(base_prof, sub_meta, contrasts, stability), encoding="utf-8")
    print(f"nested assignments: {len(nested):,}; contrasts: {len(contrasts):,}; stability rows: {len(stability):,}")


if __name__ == "__main__":
    main_fixed()
