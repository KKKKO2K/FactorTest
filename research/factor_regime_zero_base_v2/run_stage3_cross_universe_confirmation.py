from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = HERE / "results_stage0_structure/structure_panel.csv"
OUT = HERE / "results_stage3_cross_universe_confirmation"
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = [
    "MOM1M", "MOM12_1", "OP12_REV", "OPFY1_REV",
    "PBR12MF", "PER12MF", "PRIVATE_FLOW", "FOREIGN_FLOW",
]

SIGNALS = [
    "LOCAL_RANK20",
    "GLOBAL_MEAN_RANK20",
    "GLOBAL_TOP2_SHARE",
    "GLOBAL_POSITIVE_SHARE",
    "GLOBAL_MEAN_PAYOFF20",
    "NEG_GLOBAL_RANK_DISPERSION20",
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


def spearman(x: pd.Series | np.ndarray, y: pd.Series | np.ndarray) -> float:
    a = pd.Series(np.asarray(x, dtype=float))
    b = pd.Series(np.asarray(y, dtype=float))
    z = pd.concat([a.rename("x"), b.rename("y")], axis=1).dropna()
    if len(z) < 5 or z.x.nunique() < 3 or z.y.nunique() < 3:
        return np.nan
    return float(z.x.rank(method="average").corr(z.y.rank(method="average")))


def build_factor_panel() -> pd.DataFrame:
    p = pd.read_csv(SRC)
    p["date"] = pd.to_datetime(p["date"])
    rows = []

    for _, r in p.iterrows():
        cur = pd.Series({f: float(r[f"cur20_{f}"]) for f in FACTORS})
        fwd = pd.Series({f: float(r[f"fwd20_{f}"]) for f in FACTORS})
        cur_rank = cur.rank(pct=True, method="average")
        fwd_rank = fwd.rank(pct=True, method="average")
        top2 = set(cur.nlargest(2).index)
        for f in FACTORS:
            rows.append({
                "date": r.date,
                "universe": r.universe,
                "factor": f,
                "current_payoff20": cur[f],
                "future_payoff20": fwd[f],
                "LOCAL_RANK20": cur_rank[f],
                "future_rank20": fwd_rank[f],
                "local_top2": f in top2,
                "local_positive": cur[f] > 0,
            })

    x = pd.DataFrame(rows)
    g = x.groupby(["date", "factor"]).agg(
        GLOBAL_MEAN_RANK20=("LOCAL_RANK20", "mean"),
        GLOBAL_TOP2_SHARE=("local_top2", "mean"),
        GLOBAL_POSITIVE_SHARE=("local_positive", "mean"),
        GLOBAL_MEAN_PAYOFF20=("current_payoff20", "mean"),
        GLOBAL_RANK_DISPERSION20=("LOCAL_RANK20", "std"),
        universe_count=("universe", "nunique"),
    ).reset_index()
    g["NEG_GLOBAL_RANK_DISPERSION20"] = -g.GLOBAL_RANK_DISPERSION20
    x = x.merge(g, on=["date", "factor"], how="left")
    x["GLOBALLY_CONFIRMED"] = x.GLOBAL_TOP2_SHARE >= 0.50
    x["era"] = x.date.map(era_of)
    return x.sort_values(["date", "universe", "factor"]).reset_index(drop=True)


def daily_cross_sectional_ic(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (date, era, universe), g in panel.groupby(["date", "era", "universe"]):
        for signal in SIGNALS:
            rows.append({
                "date": date,
                "era": era,
                "universe": universe,
                "signal": signal,
                "ic_future_payoff": spearman(g[signal], g.future_payoff20),
                "ic_future_rank": spearman(g[signal], g.future_rank20),
            })
    return pd.DataFrame(rows)


def summarize_ic(ic: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (era, universe, signal), g in ic.groupby(["era", "universe", "signal"]):
        rows.append({
            "era": era,
            "universe": universe,
            "signal": signal,
            "n_dates": g.ic_future_payoff.notna().sum(),
            "median_daily_ic": float(g.ic_future_payoff.median()),
            "mean_daily_ic": float(g.ic_future_payoff.mean()),
            "positive_day_share": float((g.ic_future_payoff > 0).mean()),
        })
    return pd.DataFrame(rows)


def primary_summary(ics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for era in ["2016_2019", "2020_2022", "2023_2024", "2025", "2026"]:
        glob = ics[(ics.era.eq(era)) & ics.signal.eq("GLOBAL_MEAN_RANK20")].set_index("universe")
        loc = ics[(ics.era.eq(era)) & ics.signal.eq("LOCAL_RANK20")].set_index("universe")
        common = glob.index.intersection(loc.index)
        if len(common) == 0:
            continue
        gi = glob.loc[common, "median_daily_ic"]
        li = loc.loc[common, "median_daily_ic"]
        delta = gi - li
        rows.append({
            "era": era,
            "median_global_ic": float(gi.median()),
            "positive_global_universes": int((gi > 0).sum()),
            "universe_count": len(common),
            "median_local_ic": float(li.median()),
            "median_global_minus_local_ic": float(delta.median()),
            "global_beats_local_universes": int((delta > 0).sum()),
        })
    out = pd.DataFrame(rows)
    def row(era):
        z = out[out.era.eq(era)]
        return z.iloc[0] if len(z) else None
    v, c = row("2020_2022"), row("2023_2024")
    passed = bool(
        v is not None and c is not None
        and v.median_global_ic > 0.05 and c.median_global_ic > 0.05
        and v.positive_global_universes >= 4 and c.positive_global_universes >= 4
        and v.median_global_minus_local_ic > 0.02 and c.median_global_minus_local_ic > 0.02
    )
    out["PRIMARY_PASS"] = passed
    return out


def confirmed_spread(panel: pd.DataFrame) -> pd.DataFrame:
    z = panel[panel.local_top2].copy()
    rows = []
    for (era, universe), g in z.groupby(["era", "universe"]):
        yes = g[g.GLOBALLY_CONFIRMED].future_payoff20.dropna()
        no = g[~g.GLOBALLY_CONFIRMED].future_payoff20.dropna()
        valid = len(yes) >= 15 and len(no) >= 15
        rows.append({
            "era": era,
            "universe": universe,
            "n_confirmed": len(yes),
            "n_unconfirmed": len(no),
            "valid_cell": valid,
            "confirmed_mean_future": float(yes.mean()) if len(yes) else np.nan,
            "unconfirmed_mean_future": float(no.mean()) if len(no) else np.nan,
            "confirmed_minus_unconfirmed": float(yes.mean() - no.mean()) if valid else np.nan,
        })
    return pd.DataFrame(rows)


def confirmed_summary(spreads: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for era, g in spreads.groupby("era"):
        v = g[g.valid_cell & g.confirmed_minus_unconfirmed.notna()]
        rows.append({
            "era": era,
            "valid_universes": len(v),
            "median_spread": float(v.confirmed_minus_unconfirmed.median()) if len(v) else np.nan,
            "positive_universes": int((v.confirmed_minus_unconfirmed > 0).sum()),
        })
    out = pd.DataFrame(rows)
    def row(era):
        z = out[out.era.eq(era)]
        return z.iloc[0] if len(z) else None
    v, c = row("2020_2022"), row("2023_2024")
    passed = bool(
        v is not None and c is not None
        and v.median_spread > 0 and c.median_spread > 0
        and v.positive_universes >= 4 and c.positive_universes >= 4
        and v.valid_universes >= 4 and c.valid_universes >= 4
    )
    out["SECONDARY_PASS"] = passed
    return out


def diagnostic_summary(ics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for signal in ["GLOBAL_TOP2_SHARE", "GLOBAL_POSITIVE_SHARE", "GLOBAL_MEAN_PAYOFF20", "NEG_GLOBAL_RANK_DISPERSION20"]:
        for era in ["2016_2019", "2020_2022", "2023_2024", "2025", "2026"]:
            z = ics[(ics.signal.eq(signal)) & ics.era.eq(era)]
            vals = z.median_daily_ic.dropna()
            rows.append({
                "signal": signal,
                "era": era,
                "median_universe_ic": float(vals.median()) if len(vals) else np.nan,
                "positive_universes": int((vals > 0).sum()),
                "universe_count": len(vals),
            })
    return pd.DataFrame(rows)


def fmt(x: float) -> str:
    return "NA" if not np.isfinite(x) else f"{x:+.3f}"


def pct(x: float) -> str:
    return "NA" if not np.isfinite(x) else f"{x:+.2%}"


def make_report(primary: pd.DataFrame, confirm: pd.DataFrame, diag: pd.DataFrame) -> str:
    primary_pass = bool(primary.PRIMARY_PASS.iloc[0]) if len(primary) else False
    secondary_pass = bool(confirm.SECONDARY_PASS.iloc[0]) if len(confirm) else False
    lines = [
        "# Stage 3 — Cross-Universe Factor Confirmation", "",
        "Question: does factor strength confirmed across multiple universe definitions predict future factor payoff better than local strength alone?", "",
        f"## Primary global-rank confirmation: PASS={primary_pass}", "",
    ]
    for r in primary.itertuples(index=False):
        lines.append(
            f"- {r.era}: global IC {fmt(r.median_global_ic)} ({r.positive_global_universes}/{r.universe_count}); "
            f"local IC {fmt(r.median_local_ic)}; global-local {fmt(r.median_global_minus_local_ic)}; "
            f"global beats local {r.global_beats_local_universes}/{r.universe_count}"
        )

    lines += ["", f"## Local-top2 global confirmation: PASS={secondary_pass}", ""]
    for r in confirm.itertuples(index=False):
        lines.append(
            f"- {r.era}: valid universes {r.valid_universes}; confirmed-unconfirmed future payoff "
            f"{pct(r.median_spread)}; positive universes {r.positive_universes}/{r.valid_universes}"
        )

    lines += ["", "## Other cross-universe diagnostics", ""]
    for signal in ["GLOBAL_TOP2_SHARE", "GLOBAL_POSITIVE_SHARE", "GLOBAL_MEAN_PAYOFF20", "NEG_GLOBAL_RANK_DISPERSION20"]:
        z = diag[diag.signal.eq(signal)]
        bits = []
        for era in ["2020_2022", "2023_2024", "2025", "2026"]:
            q = z[z.era.eq(era)]
            if len(q):
                r = q.iloc[0]
                bits.append(f"{era} {fmt(r.median_universe_ic)} ({int(r.positive_universes)}/{int(r.universe_count)})")
        lines.append(f"- {signal}: " + "; ".join(bits))

    lines += ["", "## Decision rule", ""]
    if primary_pass or secondary_pass:
        lines.append("- Cross-universe confirmation contains incremental factor-level information and is eligible for a separate falsification stage before portfolio testing.")
    else:
        lines.append("- Cross-universe confirmation does not add robust predictive information. Stop further factor-return-only regime engineering on the current 8-factor panel.")
        lines.append("- Any next Factor Regime research must introduce genuinely new information: stock-level participation/overlap/liquidity or external market/macro state.")
    return "\n".join(lines)


def main() -> None:
    panel = build_factor_panel()
    daily_ic = daily_cross_sectional_ic(panel)
    ic_summary = summarize_ic(daily_ic)
    primary = primary_summary(ic_summary)
    spreads = confirmed_spread(panel)
    confirm = confirmed_summary(spreads)
    diag = diagnostic_summary(ic_summary)

    panel.to_csv(OUT / "factor_confirmation_panel.csv", index=False, encoding="utf-8-sig")
    daily_ic.to_csv(OUT / "daily_cross_sectional_ic.csv", index=False, encoding="utf-8-sig")
    ic_summary.to_csv(OUT / "ic_summary_by_universe.csv", index=False, encoding="utf-8-sig")
    primary.to_csv(OUT / "primary_global_rank_summary.csv", index=False, encoding="utf-8-sig")
    spreads.to_csv(OUT / "local_top2_confirmation_spreads.csv", index=False, encoding="utf-8-sig")
    confirm.to_csv(OUT / "local_top2_confirmation_summary.csv", index=False, encoding="utf-8-sig")
    diag.to_csv(OUT / "diagnostic_summary.csv", index=False, encoding="utf-8-sig")

    text = make_report(primary, confirm, diag)
    (OUT / "RESEARCH_SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
