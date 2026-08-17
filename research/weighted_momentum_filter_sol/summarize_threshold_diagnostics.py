from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "results_threshold"

df = pd.read_csv(OUT / "filter_diagnostics.csv", encoding="utf-8-sig", parse_dates=["date"])

def period_of(d):
    y = d.year
    if y <= 2019: return "EARLY_2017_2019"
    if y <= 2022: return "LATE_2020_2022"
    if y <= 2024: return "NORMAL_2023_2024"
    if y == 2025: return "BULL_2025"
    return "YTD_2026"

df["period"] = df.date.map(period_of)
df["eligible_retention"] = df.filtered_eligible / df.base_eligible.replace(0, pd.NA)
df["names_replaced"] = 20 - df.top20_overlap

rows = []
for (u, p, v), g in df.groupby(["universe", "period", "variant"]):
    valid = g[g.filtered_top20_valid.eq(1)]
    rows.append({
        "universe": u, "period": p, "variant": v, "n_dates": len(g),
        "avg_eligible_retention": g.eligible_retention.mean(),
        "median_eligible_retention": g.eligible_retention.median(),
        "filtered_top20_valid_rate": g.filtered_top20_valid.mean(),
        "avg_top20_overlap_when_valid": valid.top20_overlap.mean(),
        "avg_names_replaced_when_valid": valid.names_replaced.mean(),
        "median_names_replaced_when_valid": valid.names_replaced.median(),
    })

out = pd.DataFrame(rows)
out.to_csv(OUT / "threshold_diagnostics_summary.csv", index=False, encoding="utf-8-sig")

# 2017-2024 pooled view as a compact decision table.
core = df[df.date.dt.year.le(2024)].copy()
rows = []
for (u, v), g in core.groupby(["universe", "variant"]):
    valid = g[g.filtered_top20_valid.eq(1)]
    rows.append({
        "universe": u, "variant": v, "n_dates": len(g),
        "avg_eligible_retention": g.eligible_retention.mean(),
        "filtered_top20_valid_rate": g.filtered_top20_valid.mean(),
        "avg_names_replaced_when_valid": valid.names_replaced.mean(),
        "median_names_replaced_when_valid": valid.names_replaced.median(),
    })
pd.DataFrame(rows).to_csv(OUT / "threshold_diagnostics_2017_2024.csv", index=False, encoding="utf-8-sig")
