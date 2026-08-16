from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = HERE / "results" / "filter_diagnostics.csv"
OUT = HERE / "results" / "filter_diagnostics_summary.csv"

df = pd.read_csv(SRC, encoding="utf-8-sig")
df["date"] = pd.to_datetime(df["date"])

def period(dt):
    if dt.year <= 2019:
        return "EARLY_2017_2019"
    if dt.year <= 2022:
        return "LATE_2020_2022"
    if dt.year <= 2024:
        return "NORMAL_2023_2024"
    if dt.year == 2025:
        return "BULL_2025"
    return "YTD_2026"

df["period"] = df.date.map(period)
pre = df[(df.date >= "2017-01-01") & (df.date <= "2024-12-31")].copy()
pre["period"] = "PRE_STRESS_2017_2024"
x = pd.concat([df, pre], ignore_index=True)
x["eligible_retention"] = x.filtered_eligible / x.base_eligible.replace(0, np.nan)
x["names_replaced"] = 20 - x.top20_overlap

summary = x.groupby(["universe", "period", "variant"], as_index=False).agg(
    n_dates=("date", "count"),
    avg_base_eligible=("base_eligible", "mean"),
    avg_filtered_eligible=("filtered_eligible", "mean"),
    avg_eligible_retention=("eligible_retention", "mean"),
    avg_top20_overlap=("top20_overlap", "mean"),
    median_top20_overlap=("top20_overlap", "median"),
    avg_names_replaced=("names_replaced", "mean"),
    median_names_replaced=("names_replaced", "median"),
    filtered_top20_valid_rate=("filtered_top20_valid", "mean"),
)
summary.to_csv(OUT, index=False, encoding="utf-8-sig")
print(summary.to_string(index=False))
