from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "research/factor_regime_v1/results/factor_5d_returns.csv"
OUT = Path(__file__).resolve().parent / "results_stage2_opportunity_falsification"
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = [
    "MOM1M", "MOM12_1", "OP12_REV", "OPFY1_REV",
    "PBR12MF", "PER12MF", "PRIVATE_FLOW", "FOREIGN_FLOW",
]


def era_of(dt: pd.Timestamp) -> str:
    y = dt.year
    if y <= 2019:
        return "2016_2019"
    if y <= 2022:
        return "2020_2022"
    if y <= 2024:
        return "2023_2024"
    if y == 2025:
        return "2025"
    return "2026"


def compound_block(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    if a.ndim != 2 or np.isnan(a).any():
        return np.full(a.shape[1] if a.ndim == 2 else len(FACTORS), np.nan)
    if np.any(a <= -0.999999):
        return np.sum(a, axis=0)
    return np.prod(1.0 + a, axis=0) - 1.0


def dispersion(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    return float(np.std(x, ddof=1)) if np.isfinite(x).all() and len(x) >= 3 else np.nan


def spearman(x: pd.Series | np.ndarray, y: pd.Series | np.ndarray) -> float:
    a = pd.Series(np.asarray(x, dtype=float))
    b = pd.Series(np.asarray(y, dtype=float))
    z = pd.concat([a.rename("x"), b.rename("y")], axis=1).dropna()
    if len(z) < 8 or z.x.nunique() < 3 or z.y.nunique() < 3:
        return np.nan
    return float(z.x.rank(method="average").corr(z.y.rank(method="average")))


def load_data() -> pd.DataFrame:
    f = pd.read_csv(SRC)
    f["date"] = pd.to_datetime(f["date"])
    f = f[f.factor.isin(FACTORS)].copy()
    f["ls_return"] = pd.to_numeric(f["ls_return"], errors="coerce")
    return f.dropna(subset=["date", "universe", "factor", "ls_return"])


def build_panel(f: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for universe, g in f.groupby("universe"):
        w = g.pivot(index="date", columns="factor", values="ls_return").sort_index()
        if not set(FACTORS).issubset(w.columns):
            continue
        w = w[FACTORS]
        arr = w.to_numpy(dtype=float)
        dates = list(w.index)

        for i in range(11, len(w) - 12):
            hist60 = arr[i - 11:i + 1]
            cur20 = compound_block(arr[i - 3:i + 1])
            fwd10 = compound_block(arr[i + 1:i + 3])
            fwd20 = compound_block(arr[i + 1:i + 5])
            fwd40 = compound_block(arr[i + 1:i + 9])
            fwd60 = compound_block(arr[i + 1:i + 13])
            gap20 = compound_block(arr[i + 2:i + 6])
            blocks = [cur20, fwd10, fwd20, fwd40, fwd60, gap20]
            if not all(np.isfinite(x).all() for x in blocks):
                continue

            factor_vol = np.nanstd(hist60, axis=0, ddof=1)
            vol_scale = float(np.nanmedian(factor_vol))
            if not np.isfinite(vol_scale) or vol_scale <= 0:
                continue

            rec = {
                "date": dates[i],
                "era": era_of(dates[i]),
                "universe": universe,
                "current_dispersion20": dispersion(cur20),
                "future_dispersion10": dispersion(fwd10),
                "future_dispersion20": dispersion(fwd20),
                "future_dispersion40": dispersion(fwd40),
                "future_dispersion60": dispersion(fwd60),
                "gap5_future_dispersion20": dispersion(gap20),
                "current_dispersion20_norm": dispersion(cur20) / vol_scale,
                "future_dispersion20_norm": dispersion(fwd20) / vol_scale,
                "trailing_factor_vol_scale": vol_scale,
            }
            for j, factor in enumerate(FACTORS):
                keep = [k for k in range(len(FACTORS)) if k != j]
                rec[f"loo_{factor}_current20"] = dispersion(cur20[keep])
                rec[f"loo_{factor}_future20"] = dispersion(fwd20[keep])
            rows.append(rec)
    panel = pd.DataFrame(rows).sort_values(["universe", "date"]).reset_index(drop=True)
    panel["state_index"] = panel.groupby("universe").cumcount()
    panel["nonoverlap20"] = panel.state_index.mod(4).eq(0)
    return panel


def universe_ic_summary(panel: pd.DataFrame, xcol: str, ycol: str, nonoverlap: bool = False) -> pd.DataFrame:
    z0 = panel[panel.nonoverlap20].copy() if nonoverlap else panel.copy()
    rows = []
    for (era, universe), g in z0.groupby(["era", "universe"]):
        rows.append({
            "era": era,
            "universe": universe,
            "x": xcol,
            "y": ycol,
            "nonoverlap": nonoverlap,
            "n": len(g),
            "ic": spearman(g[xcol], g[ycol]),
        })
    return pd.DataFrame(rows)


def summarize_across_universes(long: pd.DataFrame, label: str) -> pd.DataFrame:
    rows = []
    for era, g in long.groupby("era"):
        vals = g.ic.dropna()
        rows.append({
            "test": label,
            "era": era,
            "median_ic": float(vals.median()) if len(vals) else np.nan,
            "positive_universes": int((vals > 0).sum()),
            "universe_count": int(len(vals)),
        })
    return pd.DataFrame(rows)


def build_horizon_results(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    longs = []
    for h in [10, 20, 40, 60]:
        x = universe_ic_summary(panel, "current_dispersion20", f"future_dispersion{h}")
        x["horizon"] = h
        longs.append(x)
    long = pd.concat(longs, ignore_index=True)
    rows = []
    for (h, era), g in long.groupby(["horizon", "era"]):
        vals = g.ic.dropna()
        rows.append({
            "horizon": h,
            "era": era,
            "median_ic": float(vals.median()) if len(vals) else np.nan,
            "positive_universes": int((vals > 0).sum()),
            "universe_count": len(vals),
        })
    return long, pd.DataFrame(rows)


def build_loo_results(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    longs = []
    for factor in FACTORS:
        x = universe_ic_summary(panel, f"loo_{factor}_current20", f"loo_{factor}_future20")
        x["excluded_factor"] = factor
        longs.append(x)
    long = pd.concat(longs, ignore_index=True)
    rows = []
    for (factor, era), g in long.groupby(["excluded_factor", "era"]):
        vals = g.ic.dropna()
        rows.append({
            "excluded_factor": factor,
            "era": era,
            "median_ic": float(vals.median()) if len(vals) else np.nan,
            "positive_universes": int((vals > 0).sum()),
            "universe_count": len(vals),
        })
    return long, pd.DataFrame(rows)


def build_aggregate_results(panel: pd.DataFrame) -> pd.DataFrame:
    g = panel.groupby(["date", "era"]).agg(
        current_dispersion20=("current_dispersion20", "median"),
        future_dispersion20=("future_dispersion20", "median"),
        current_dispersion20_norm=("current_dispersion20_norm", "median"),
        future_dispersion20_norm=("future_dispersion20_norm", "median"),
    ).reset_index()
    rows = []
    for era, z in g.groupby("era"):
        rows.append({
            "era": era,
            "aggregate_raw_ic": spearman(z.current_dispersion20, z.future_dispersion20),
            "aggregate_norm_ic": spearman(z.current_dispersion20_norm, z.future_dispersion20_norm),
            "n_dates": len(z),
        })
    return pd.DataFrame(rows)


def get_metric(df: pd.DataFrame, era: str, col: str) -> float:
    z = df[df.era.eq(era)]
    return float(z.iloc[0][col]) if len(z) else np.nan


def classify(primary: pd.DataFrame, gap: pd.DataFrame, norm: pd.DataFrame, nonoverlap: pd.DataFrame, loo: pd.DataFrame, agg: pd.DataFrame) -> tuple[bool, str]:
    hist_eras = ["2016_2019", "2020_2022", "2023_2024"]
    c1 = all(get_metric(primary, e, "median_ic") > 0 for e in hist_eras)
    c2 = all(get_metric(primary, e, "positive_universes") >= 4 for e in ["2020_2022", "2023_2024"])
    c3 = all(get_metric(gap, e, "median_ic") > 0 for e in ["2020_2022", "2023_2024"])
    c4 = all(get_metric(norm, e, "median_ic") > 0 for e in ["2020_2022", "2023_2024"])
    c5 = all(get_metric(nonoverlap, e, "median_ic") > 0 for e in ["2020_2022", "2023_2024"])

    good_loo = 0
    for factor in FACTORS:
        z = loo[loo.excluded_factor.eq(factor)]
        if get_metric(z, "2020_2022", "median_ic") > 0 and get_metric(z, "2023_2024", "median_ic") > 0:
            good_loo += 1
    c6 = good_loo >= 7
    c7 = all(get_metric(agg, e, "aggregate_raw_ic") > 0 for e in ["2020_2022", "2023_2024"])

    passed = all([c1, c2, c3, c4, c5, c6, c7])
    stress_vals = [get_metric(primary, "2025", "median_ic"), get_metric(primary, "2026", "median_ic")]
    recent_break = any(np.isfinite(x) and x < 0 for x in stress_vals)
    if passed and recent_break:
        label = "HISTORICALLY_ROBUST_RECENT_BREAK"
    elif passed:
        label = "HISTORICALLY_ROBUST"
    else:
        label = "REJECT_OR_CONDITIONAL"
    return passed, label


def fmt(x: float) -> str:
    return "NA" if not np.isfinite(x) else f"{x:+.3f}"


def make_report(hsum: pd.DataFrame, primary: pd.DataFrame, gap: pd.DataFrame, norm: pd.DataFrame, nonoverlap: pd.DataFrame, loo: pd.DataFrame, agg: pd.DataFrame, passed: bool, label: str) -> str:
    lines = [
        "# Stage 2 — Opportunity Clustering Falsification", "",
        "Primary hypothesis: current 20D cross-factor dispersion predicts future cross-factor dispersion.",
        "All robustness tests were pre-registered before this run. No portfolio rule is tested.", "",
        f"## Classification: {label}",
        f"- Historical robustness gate passed: {passed}", "",
        "## Primary 20D relation", "",
    ]
    for era in ["2016_2019", "2020_2022", "2023_2024", "2025", "2026"]:
        z = primary[primary.era.eq(era)]
        if len(z):
            r = z.iloc[0]
            lines.append(f"- {era}: median IC {fmt(r.median_ic)}, positive universes {int(r.positive_universes)}/{int(r.universe_count)}")

    lines += ["", "## Horizon robustness", ""]
    for h in [10, 20, 40, 60]:
        z = hsum[hsum.horizon.eq(h)]
        bits = []
        for era in ["2020_2022", "2023_2024", "2025", "2026"]:
            q = z[z.era.eq(era)]
            if len(q):
                bits.append(f"{era} {fmt(q.iloc[0].median_ic)}")
        lines.append(f"- Forward {h}D: " + "; ".join(bits))

    lines += ["", "## Falsification checks", ""]
    for name, df in [("Gap-5D", gap), ("Vol-normalized", norm), ("Non-overlap-20D", nonoverlap)]:
        v = get_metric(df, "2020_2022", "median_ic")
        c = get_metric(df, "2023_2024", "median_ic")
        s25 = get_metric(df, "2025", "median_ic")
        s26 = get_metric(df, "2026", "median_ic")
        lines.append(f"- {name}: 2020-22 {fmt(v)}, 2023-24 {fmt(c)}, 2025 {fmt(s25)}, 2026 {fmt(s26)}")

    good = []
    for factor in FACTORS:
        z = loo[loo.excluded_factor.eq(factor)]
        v = get_metric(z, "2020_2022", "median_ic")
        c = get_metric(z, "2023_2024", "median_ic")
        if v > 0 and c > 0:
            good.append(factor)
    lines.append(f"- Leave-one-factor-out positive in both validation periods: {len(good)}/8 ({', '.join(good)})")

    lines += ["", "## Cross-universe aggregate", ""]
    for era in ["2016_2019", "2020_2022", "2023_2024", "2025", "2026"]:
        z = agg[agg.era.eq(era)]
        if len(z):
            r = z.iloc[0]
            lines.append(f"- {era}: raw IC {fmt(r.aggregate_raw_ic)}, normalized IC {fmt(r.aggregate_norm_ic)}")

    lines += [
        "", "## Interpretation rule", "",
        "- A historical PASS with negative 2025/2026 is a recent structural break, not a production signal.",
        "- Do not search for a trading threshold from this output.",
        "- If historically robust, the next research question is what observable state explains persistence versus mean reversion in opportunity; if not robust, stop Factor Opportunity as a regime target.",
    ]
    return "\n".join(lines)


def main() -> None:
    f = load_data()
    panel = build_panel(f)

    hlong, hsum = build_horizon_results(panel)
    primary_long = hlong[hlong.horizon.eq(20)].copy()
    primary = summarize_across_universes(primary_long, "PRIMARY_20D")

    gap_long = universe_ic_summary(panel, "current_dispersion20", "gap5_future_dispersion20")
    gap = summarize_across_universes(gap_long, "GAP5_20D")

    norm_long = universe_ic_summary(panel, "current_dispersion20_norm", "future_dispersion20_norm")
    norm = summarize_across_universes(norm_long, "VOL_NORMALIZED_20D")

    non_long = universe_ic_summary(panel, "current_dispersion20", "future_dispersion20", nonoverlap=True)
    non = summarize_across_universes(non_long, "NONOVERLAP_20D")

    loo_long, loo = build_loo_results(panel)
    agg = build_aggregate_results(panel)
    passed, label = classify(primary, gap, norm, non, loo, agg)

    panel.to_csv(OUT / "opportunity_falsification_panel.csv", index=False, encoding="utf-8-sig")
    hlong.to_csv(OUT / "horizon_ic_by_universe.csv", index=False, encoding="utf-8-sig")
    hsum.to_csv(OUT / "horizon_summary.csv", index=False, encoding="utf-8-sig")
    gap_long.to_csv(OUT / "gap_ic_by_universe.csv", index=False, encoding="utf-8-sig")
    norm_long.to_csv(OUT / "normalized_ic_by_universe.csv", index=False, encoding="utf-8-sig")
    non_long.to_csv(OUT / "nonoverlap_ic_by_universe.csv", index=False, encoding="utf-8-sig")
    loo_long.to_csv(OUT / "leave_one_out_ic_by_universe.csv", index=False, encoding="utf-8-sig")
    loo.to_csv(OUT / "leave_one_out_summary.csv", index=False, encoding="utf-8-sig")
    agg.to_csv(OUT / "cross_universe_aggregate_summary.csv", index=False, encoding="utf-8-sig")

    text = make_report(hsum, primary, gap, norm, non, loo, agg, passed, label)
    (OUT / "RESEARCH_SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
