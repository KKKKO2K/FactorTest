from __future__ import annotations

import numpy as np
import pandas as pd

import run_contemporaneous_regimes as base


def load_liquidity_long() -> pd.DataFrame:
    x = pd.read_csv(base.HORIZON / "horizon_state_values.csv")
    x["date"] = pd.to_datetime(x["date"])
    required = {"date", "universe", "predictor_type", "definition", "value"}
    if not required.issubset(x.columns):
        raise ValueError(f"horizon_state_values schema mismatch: {sorted(x.columns)}")
    out = []
    for definition, label in (("LIQ_5D_VS_20D", "LIQ_5D_20D"), ("LIQ_1D_VS_20D", "LIQ_1D_20D")):
        z = x[(x.predictor_type == "LIQUIDITY_BREADTH") & (x.definition == definition)].copy()
        z = z.groupby(["date", "universe"], as_index=False).value.mean().rename(columns={"value": label})
        out.append(z)
    return out[0].merge(out[1], on=["date", "universe"], how="outer")


def write_summary_safe(diag: pd.DataFrame, outcomes: pd.DataFrame, period: pd.DataFrame,
                       same_market: pd.DataFrame, rule_sum: pd.DataFrame) -> str:
    lines = [
        "# Contemporaneous Market-Regime Research", "",
        "No forward return, future drawdown, or calendar-year label enters regime fitting. All features are observable through the state date.",
        "Primary test: fixed 5-state GMM. BASE uses market trend/volatility/drawdown plus 5D-vs-20D trading-value breadth; FULL adds factor absolute/relative breadth, family interactions, leader strength/dispersion, and leader-rotation flags.",
        "Models are fit on 2016-2022 and frozen for 2023 onward. K=3..6 is robustness only.", "",
        "## Incremental diagnostics: FULL vs BASE, K=5", "",
    ]
    d = diag[diag["k"] == base.PRIMARY_K].copy()
    for u in sorted(d["universe"].dropna().unique()):
        b = d[(d["universe"] == u) & (d["model"] == "BASE")]
        f = d[(d["universe"] == u) & (d["model"] == "FULL")]
        if b.empty or f.empty:
            continue
        br, fr = b.iloc[0], f.iloc[0]
        lines.append(
            f"- {u}: silhouette BASE {br['silhouette_train']:.2f} vs FULL {fr['silhouette_train']:.2f}; "
            f"persistence {br['persistence_all']:.0%} vs {fr['persistence_all']:.0%}; "
            f"post-2023 eta2 next20 {br['eta2_fwd20_post']:.2f} vs {fr['eta2_fwd20_post']:.2f}; "
            f"eta2 downside {br['eta2_fwd_dd20_post']:.2f} vs {fr['eta2_fwd_dd20_post']:.2f}; "
            f"BASE-only CV accuracy for FULL states {fr.get('base_cv_accuracy_for_full_state', np.nan):.0%} "
            f"vs majority {fr.get('base_majority_accuracy', np.nan):.0%}"
        )

    lines += ["", "## FULL-state future outcomes (attached after classification)", ""]
    if not outcomes.empty:
        z = outcomes[(outcomes["model"] == "FULL") & outcomes["sample"].isin(["TRAIN", "NORMAL_2023_2024", "POST_2023"])].copy()
        for u in sorted(z["universe"].unique()):
            lines.append(f"### {u}")
            for sample in ["TRAIN", "NORMAL_2023_2024", "POST_2023"]:
                q = z[(z["universe"] == u) & (z["sample"] == sample)].sort_values("state")
                if q.empty:
                    continue
                desc = "; ".join(
                    f"{r['state']}: n={int(r['n'])}, +20D {r['MKT_FWD_20D']:+.2%}, fwdDD {r['MKT_FWD_DD20']:+.2%}"
                    for _, r in q.iterrows()
                )
                lines.append(f"- {sample}: {desc}")

    lines += ["", "## Calendar-period composition of FULL states", ""]
    if not period.empty:
        pp = period[period["model"] == "FULL"].copy()
        preferred = ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"]
        for u in [x for x in preferred if x in pp["universe"].unique()]:
            lines.append(f"### {u}")
            for per in base.PERIODS:
                q = pp[(pp["universe"] == u) & (pp["period"] == per)].sort_values("share_within_period", ascending=False)
                if q.empty:
                    continue
                top = ", ".join(f"{r['state']} {r['share_within_period']:.0%}" for _, r in q.head(3).iterrows())
                lines.append(f"- {per}: {top}")

    lines += ["", "## Same-market / different-factor states in TRAIN", ""]
    if same_market.empty:
        lines.append("- None passed the predeclared screen: base centroid distance <=1.5z and factor centroid distance >=1.5z.")
    else:
        for _, r in same_market.sort_values("factor_distance_z", ascending=False).head(30).iterrows():
            lines.append(
                f"- {r['universe']} {r['state_a']}/{r['state_b']}: base distance {r['base_distance_z']:.2f}z, "
                f"factor distance {r['factor_distance_z']:.2f}z; next20 difference {r['fwd20_diff']:+.2%}"
            )

    lines += ["", "## Rule-based archetype check: 2023-2024", ""]
    if not rule_sum.empty:
        rr = rule_sum[rule_sum["sample"] == "NORMAL_2023_2024"].copy()
        for u in [x for x in ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"] if x in rr["universe"].unique()]:
            q = rr[rr["universe"] == u].sort_values("n", ascending=False)
            desc = "; ".join(f"{r['state']} n={int(r['n'])} +20D={r['fwd20']:+.2%}" for _, r in q.iterrows())
            lines.append(f"- {u}: {desc}")

    lines += ["", "## Guardrails", "",
              "- State IDs are ordered by TRAIN 60D market return, not named ex post as bull/bear.",
              "- Factor interaction is incremental only if FULL distinguishes economically different states that BASE cannot recover and those distinctions survive after 2022.",
              "- Future outcomes validate economic meaning; they never define the states.",
              "- 2025 and 2026 are kept separate in composition diagnostics.", ""]
    return "\n".join(lines) + "\n"


base.load_liquidity = load_liquidity_long
base.write_summary = write_summary_safe

if __name__ == "__main__":
    base.main()
