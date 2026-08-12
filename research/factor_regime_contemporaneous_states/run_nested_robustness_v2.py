from __future__ import annotations

import pandas as pd
import run_nested_robustness as base


def write_summary_safe(agg: pd.DataFrame, stab: pd.DataFrame, stress: pd.DataFrame) -> str:
    lines = ["# Nested Regime Robustness", "",
             "BASE market/liquidity KMeans K=3/4/5; factor substate tested with KMeans and a transparent TRAIN-median continuous factor-health score. No forward outcome enters classification.", "",
             "## Predeclared cross-spec hypotheses", ""]
    for method in base.SPLITS:
        lines.append(f"### {method}")
        q = agg[(agg["factor_method"] == method) & (agg["universe"] == "ALL_UNIVERSES")]
        for _, r in q.iterrows():
            lines.append(f"- {r['hypothesis']}: specs={int(r['n_specs'])}, expected sign TRAIN {r['train_expected_share']:.0%}, 23-24 {r['valid_expected_share']:.0%}, TRAIN/VALID same sign {r['train_valid_same_sign_share']:.0%}; median diff {r['median_train_diff']:+.2%} -> {r['median_valid_diff']:+.2%}")
    lines += ["", "## Strongest exact TRAIN -> 2023-2024 stable relations", ""]
    z = stab[(stab["same_sign"] == 1) & (stab["valid_n_min"] >= 8)].copy()
    z["score"] = z["valid_diff"].abs()
    for _, r in z.sort_values("score", ascending=False).head(40).iterrows():
        bs = f"B{int(r['base_rank'])}"
        lines.append(f"- {r['factor_method']} {r['universe']} K{int(r['base_k'])} {bs}/{r['base_role']} {r['outcome']}: {r['train_diff']:+.2%} -> {r['valid_diff']:+.2%}; nmin {int(r['train_n_min'])}/{int(r['valid_n_min'])}; base dist {r['train_base_dist']:.2f}/{r['valid_base_dist']:.2f}z, factor dist {r['train_factor_dist']:.2f}/{r['valid_factor_dist']:.2f}z")
    lines += ["", "## 2025/2026 stress sign retention", ""]
    if stress.empty:
        lines.append("- No stress cells retained at least 8 observations per factor substate.")
    else:
        for period in ["STRESS_2025", "STRESS_2026"]:
            q = stress[stress["stress_period"] == period]
            if q.empty:
                continue
            for out in ["NEXT_UP", "NEXT_DOWN", "MKT_FWD_20D", "MKT_FWD_DD20"]:
                x = q[q["outcome"] == out]
                if len(x):
                    lines.append(f"- {period} {out}: sign retained vs 2023-24 in {x['same_sign'].mean():.0%} of {len(x)} eligible specs")
    lines += ["", "## Interpretation", "",
             "- Structural evidence requires agreement across BASE K and factor-split definitions, not one chosen cluster solution.",
             "- REPAIR_MID transition effects are the main contemporaneous-regime hypothesis; STRONG-state return/downside reversal is a separate maturity/crowding hypothesis.",
             "- Stress years are not expected to preserve all signs; systematic breaks are themselves regime-dependence evidence.", ""]
    return "\n".join(lines) + "\n"


def main():
    p = pd.read_csv(base.PANEL); p["date"] = pd.to_datetime(p["date"])
    raw = base.run(p)
    stab = base.exact_stability(raw)
    agg = base.hypothesis_aggregate(stab)
    stress = base.stress_compare(raw)
    raw.to_csv(base.OUT / "nested_robustness_raw.csv", index=False, encoding="utf-8-sig")
    stab.to_csv(base.OUT / "nested_robustness_stability.csv", index=False, encoding="utf-8-sig")
    agg.to_csv(base.OUT / "nested_robustness_hypotheses.csv", index=False, encoding="utf-8-sig")
    stress.to_csv(base.OUT / "nested_robustness_stress.csv", index=False, encoding="utf-8-sig")
    (base.OUT / "NESTED_ROBUSTNESS_SUMMARY.md").write_text(write_summary_safe(agg, stab, stress), encoding="utf-8")
    print(len(raw), len(stab), len(stress))

if __name__ == "__main__":
    main()
