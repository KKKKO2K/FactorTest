from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = HERE / "results_stage0_structure/structure_panel.csv"
OUT = HERE / "results_stage1_minimal_predictability"
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = [
    "MOM1M", "MOM12_1", "OP12_REV", "OPFY1_REV",
    "PBR12MF", "PER12MF", "PRIVATE_FLOW", "FOREIGN_FLOW",
]

OPPORTUNITY_TARGET = "future_dispersion20"
OPPORTUNITY_PREDICTORS = [
    "dispersion20",
    "abs_opportunity20",
    "range20",
    "breadth20",
    "leader_abs_share20",
    "avg_pair_corr_60",
    "pc1_share_60",
    "rank_agreement_20_60",
    "current_cross_universe_coherence",
]

COHERENCE_TARGET = "future_cross_universe_coherence"
COHERENCE_PREDICTORS = [
    "current_cross_universe_coherence",
    "median_dispersion20",
    "median_abs_opportunity20",
    "median_avg_pair_corr_60",
    "median_pc1_share_60",
    "median_rank_agreement_20_60",
]


def era_of(dt: pd.Timestamp) -> str:
    y = dt.year
    if y <= 2019:
        return "DISCOVERY_2016_2019"
    if y <= 2022:
        return "VALIDATION_2020_2022"
    if y <= 2024:
        return "CONFIRM_2023_2024"
    if y == 2025:
        return "STRESS_2025"
    return "STRESS_2026"


def spearman(x: pd.Series | np.ndarray, y: pd.Series | np.ndarray) -> float:
    a = pd.Series(np.asarray(x, dtype=float))
    b = pd.Series(np.asarray(y, dtype=float))
    z = pd.concat([a.rename("x"), b.rename("y")], axis=1).dropna()
    if len(z) < 8 or z.x.nunique() < 3 or z.y.nunique() < 3:
        return np.nan
    return float(z.x.rank(method="average").corr(z.y.rank(method="average")))


def pair_rank_corr(a: np.ndarray, b: np.ndarray) -> float:
    return spearman(a, b)


def median_pair_coherence(g: pd.DataFrame, prefix: str) -> float:
    if len(g) < 4:
        return np.nan
    cols = [f"{prefix}_{f}" for f in FACTORS]
    vals = []
    g = g.drop_duplicates("universe").set_index("universe")
    universes = sorted(g.index)
    for a, b in combinations(universes, 2):
        xa = g.loc[a, cols].to_numpy(dtype=float)
        xb = g.loc[b, cols].to_numpy(dtype=float)
        r = pair_rank_corr(xa, xb)
        if np.isfinite(r):
            vals.append(r)
    return float(np.median(vals)) if vals else np.nan


def build_global_panel(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dt, g in panel.groupby("date"):
        rec = {
            "date": pd.Timestamp(dt),
            "current_cross_universe_coherence": median_pair_coherence(g, "cur20"),
            "future_cross_universe_coherence": median_pair_coherence(g, "fwd20"),
            "median_dispersion20": float(g.dispersion20.median()),
            "median_abs_opportunity20": float(g.abs_opportunity20.median()),
            "median_avg_pair_corr_60": float(g.avg_pair_corr_60.median()),
            "median_pc1_share_60": float(g.pc1_share_60.median()),
            "median_rank_agreement_20_60": float(g.rank_agreement_20_60.median()),
        }
        rows.append(rec)
    out = pd.DataFrame(rows).sort_values("date")
    out["era"] = out.date.map(era_of)
    return out


def directed_hl(test: pd.DataFrame, predictor: str, target: str, q1: float, q2: float, direction: int) -> tuple[float, int, int]:
    lo = test.loc[test[predictor] <= q1, target].dropna()
    hi = test.loc[test[predictor] >= q2, target].dropna()
    if len(lo) < 5 or len(hi) < 5:
        return np.nan, len(lo), len(hi)
    raw = float(hi.mean() - lo.mean())
    return direction * raw, len(lo), len(hi)


def run_opportunity(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for universe, g0 in panel.groupby("universe"):
        g = g0.sort_values("date").copy()
        disc = g[g.era.eq("DISCOVERY_2016_2019")]
        for predictor in OPPORTUNITY_PREDICTORS:
            d = disc[[predictor, OPPORTUNITY_TARGET]].dropna()
            if len(d) < 60:
                continue
            disc_ic = spearman(d[predictor], d[OPPORTUNITY_TARGET])
            if not np.isfinite(disc_ic) or disc_ic == 0:
                continue
            direction = 1 if disc_ic > 0 else -1
            q1, q2 = d[predictor].quantile([1 / 3, 2 / 3]).tolist()
            for era in [
                "DISCOVERY_2016_2019", "VALIDATION_2020_2022", "CONFIRM_2023_2024",
                "STRESS_2025", "STRESS_2026"
            ]:
                z = g[g.era.eq(era)][[predictor, OPPORTUNITY_TARGET]].dropna()
                if len(z) < 10:
                    continue
                raw_ic = spearman(z[predictor], z[OPPORTUNITY_TARGET])
                dhl, nlo, nhi = directed_hl(z, predictor, OPPORTUNITY_TARGET, q1, q2, direction)
                rows.append({
                    "universe": universe,
                    "predictor": predictor,
                    "target": OPPORTUNITY_TARGET,
                    "era": era,
                    "n": len(z),
                    "discovery_ic": disc_ic,
                    "direction": direction,
                    "raw_ic": raw_ic,
                    "directed_ic": direction * raw_ic if np.isfinite(raw_ic) else np.nan,
                    "frozen_q1": q1,
                    "frozen_q2": q2,
                    "directed_high_low": dhl,
                    "n_low": nlo,
                    "n_high": nhi,
                })

    long = pd.DataFrame(rows)
    summary_rows = []
    for predictor, g in long.groupby("predictor"):
        rec = {"predictor": predictor, "target": OPPORTUNITY_TARGET}
        for era in ["VALIDATION_2020_2022", "CONFIRM_2023_2024", "STRESS_2025", "STRESS_2026"]:
            z = g[g.era.eq(era)]
            by_u_ic = z.groupby("universe").directed_ic.median()
            by_u_hl = z.groupby("universe").directed_high_low.median()
            rec[f"{era}_median_directed_ic"] = float(by_u_ic.median()) if len(by_u_ic) else np.nan
            rec[f"{era}_positive_universes"] = int((by_u_ic > 0).sum())
            rec[f"{era}_universe_count"] = int(by_u_ic.notna().sum())
            rec[f"{era}_median_directed_hl"] = float(by_u_hl.median()) if len(by_u_hl) else np.nan
        rec["PASS"] = bool(
            rec.get("VALIDATION_2020_2022_median_directed_ic", -np.inf) > 0.05
            and rec.get("CONFIRM_2023_2024_median_directed_ic", -np.inf) > 0.05
            and rec.get("VALIDATION_2020_2022_positive_universes", 0) >= 4
            and rec.get("CONFIRM_2023_2024_positive_universes", 0) >= 4
            and rec.get("VALIDATION_2020_2022_median_directed_hl", -np.inf) > 0
            and rec.get("CONFIRM_2023_2024_median_directed_hl", -np.inf) > 0
        )
        summary_rows.append(rec)
    summary = pd.DataFrame(summary_rows).sort_values(
        ["PASS", "CONFIRM_2023_2024_median_directed_ic"], ascending=[False, False]
    )
    return long, summary


def run_coherence(global_panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    disc = global_panel[global_panel.era.eq("DISCOVERY_2016_2019")]
    for predictor in COHERENCE_PREDICTORS:
        d = disc[[predictor, COHERENCE_TARGET]].dropna()
        if len(d) < 60:
            continue
        disc_ic = spearman(d[predictor], d[COHERENCE_TARGET])
        if not np.isfinite(disc_ic) or disc_ic == 0:
            continue
        direction = 1 if disc_ic > 0 else -1
        q1, q2 = d[predictor].quantile([1 / 3, 2 / 3]).tolist()
        for era in [
            "DISCOVERY_2016_2019", "VALIDATION_2020_2022", "CONFIRM_2023_2024",
            "STRESS_2025", "STRESS_2026"
        ]:
            z = global_panel[global_panel.era.eq(era)][[predictor, COHERENCE_TARGET]].dropna()
            if len(z) < 10:
                continue
            raw_ic = spearman(z[predictor], z[COHERENCE_TARGET])
            dhl, nlo, nhi = directed_hl(z, predictor, COHERENCE_TARGET, q1, q2, direction)
            rows.append({
                "predictor": predictor,
                "target": COHERENCE_TARGET,
                "era": era,
                "n": len(z),
                "discovery_ic": disc_ic,
                "direction": direction,
                "raw_ic": raw_ic,
                "directed_ic": direction * raw_ic if np.isfinite(raw_ic) else np.nan,
                "frozen_q1": q1,
                "frozen_q2": q2,
                "directed_high_low": dhl,
                "n_low": nlo,
                "n_high": nhi,
            })
    long = pd.DataFrame(rows)
    summary_rows = []
    for predictor, g in long.groupby("predictor"):
        rec = {"predictor": predictor, "target": COHERENCE_TARGET}
        for era in ["VALIDATION_2020_2022", "CONFIRM_2023_2024", "STRESS_2025", "STRESS_2026"]:
            z = g[g.era.eq(era)]
            rec[f"{era}_directed_ic"] = float(z.directed_ic.median()) if len(z) else np.nan
            rec[f"{era}_directed_hl"] = float(z.directed_high_low.median()) if len(z) else np.nan
        rec["PASS"] = bool(
            rec.get("VALIDATION_2020_2022_directed_ic", -np.inf) > 0.10
            and rec.get("CONFIRM_2023_2024_directed_ic", -np.inf) > 0.10
            and rec.get("VALIDATION_2020_2022_directed_hl", -np.inf) > 0
            and rec.get("CONFIRM_2023_2024_directed_hl", -np.inf) > 0
        )
        summary_rows.append(rec)
    summary = pd.DataFrame(summary_rows).sort_values(
        ["PASS", "CONFIRM_2023_2024_directed_ic"], ascending=[False, False]
    )
    return long, summary


def fmt(x: float) -> str:
    return "NA" if not np.isfinite(x) else f"{x:+.3f}"


def pct(x: float) -> str:
    return "NA" if not np.isfinite(x) else f"{x:+.2%}"


def make_report(opp: pd.DataFrame, coh: pd.DataFrame) -> str:
    lines = [
        "# Stage 1 — Minimal Predictability Test", "",
        "Targets and predictor sets were pre-registered in STAGE1_TARGETS.md before this run.",
        "Discovery 2016–19 is used only for sign and frozen terciles; PASS requires independent 2020–22 validation and 2023–24 confirmation.",
        "2025/2026 are stress slices and cannot create a PASS.", "",
        f"## Opportunity target: {int(opp.PASS.sum())} PASS of {len(opp)} predictors", "",
    ]
    for r in opp.itertuples(index=False):
        lines.append(
            f"- {r.predictor}: PASS={r.PASS}; "
            f"VAL IC {fmt(r.VALIDATION_2020_2022_median_directed_ic)} "
            f"({r.VALIDATION_2020_2022_positive_universes}/{r.VALIDATION_2020_2022_universe_count}); "
            f"CONF IC {fmt(r.CONFIRM_2023_2024_median_directed_ic)} "
            f"({r.CONFIRM_2023_2024_positive_universes}/{r.CONFIRM_2023_2024_universe_count}); "
            f"VAL H-L {pct(r.VALIDATION_2020_2022_median_directed_hl)}; "
            f"CONF H-L {pct(r.CONFIRM_2023_2024_median_directed_hl)}; "
            f"2025 IC {fmt(r.STRESS_2025_median_directed_ic)}; 2026 IC {fmt(r.STRESS_2026_median_directed_ic)}"
        )

    lines += ["", f"## Coherence target: {int(coh.PASS.sum())} PASS of {len(coh)} predictors", ""]
    for r in coh.itertuples(index=False):
        lines.append(
            f"- {r.predictor}: PASS={r.PASS}; "
            f"VAL IC {fmt(r.VALIDATION_2020_2022_directed_ic)}; "
            f"CONF IC {fmt(r.CONFIRM_2023_2024_directed_ic)}; "
            f"VAL H-L {fmt(r.VALIDATION_2020_2022_directed_hl)}; "
            f"CONF H-L {fmt(r.CONFIRM_2023_2024_directed_hl)}; "
            f"2025 IC {fmt(r.STRESS_2025_directed_ic)}; 2026 IC {fmt(r.STRESS_2026_directed_ic)}"
        )

    lines += [
        "", "## Interpretation discipline", "",
        "- No composite or portfolio rule is tested here.",
        "- Only PASS predictors are eligible for Stage 2 falsification tests.",
        "- If a target has no PASS predictor, stop that target rather than broadening the feature set.",
    ]
    return "\n".join(lines)


def main() -> None:
    panel = pd.read_csv(SRC)
    panel["date"] = pd.to_datetime(panel["date"])
    panel["era"] = panel.date.map(era_of)

    global_panel = build_global_panel(panel)
    panel = panel.merge(
        global_panel[["date", "current_cross_universe_coherence"]],
        on="date", how="left"
    )

    opp_long, opp_summary = run_opportunity(panel)
    coh_long, coh_summary = run_coherence(global_panel)

    global_panel.to_csv(OUT / "global_coherence_panel.csv", index=False, encoding="utf-8-sig")
    opp_long.to_csv(OUT / "opportunity_walkforward.csv", index=False, encoding="utf-8-sig")
    opp_summary.to_csv(OUT / "opportunity_summary.csv", index=False, encoding="utf-8-sig")
    coh_long.to_csv(OUT / "coherence_walkforward.csv", index=False, encoding="utf-8-sig")
    coh_summary.to_csv(OUT / "coherence_summary.csv", index=False, encoding="utf-8-sig")

    text = make_report(opp_summary, coh_summary)
    (OUT / "RESEARCH_SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
