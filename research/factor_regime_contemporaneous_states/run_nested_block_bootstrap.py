from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
INPUT = OUT / "nested_state_assignments.csv"
N_BOOT = 3000
BLOCK = 4
SEED = 42

TARGETS = [
    ("K200", "B3", "NEXT_BASE_DOWN"),
    ("KOSPI_ALL", "B2", "NEXT_BASE_UP"),
    ("KOSPI_ALL", "B3", "NEXT_BASE_DOWN"),
    ("KOSPI_EX_K200", "B2", "NEXT_BASE_UP"),
    ("KOSPI_EX_K200", "B2", "NEXT_BASE_DOWN"),
    ("KOSDAQ", "B3", "NEXT_BASE_UP"),
    ("KOSDAQ", "B3", "NEXT_BASE_DOWN"),
    ("KOSDAQ", "B3", "MKT_FWD_DD20"),
    ("KOSDAQ", "B4", "MKT_FWD_20D"),
    ("KOSDAQ_PLUS_KOSPI_EX_K200", "B3", "NEXT_BASE_UP"),
    ("KOSDAQ_PLUS_KOSPI_EX_K200", "B3", "NEXT_BASE_DOWN"),
    ("KOSDAQ_PLUS_KOSPI_EX_K200", "B4", "MKT_FWD_20D"),
]
PERIODS = {
    "TRAIN_2016_2022": (pd.Timestamp("2016-01-01"), pd.Timestamp("2023-01-01")),
    "VALID_2023_2024": (pd.Timestamp("2023-01-01"), pd.Timestamp("2025-01-01")),
    "STRESS_2025": (pd.Timestamp("2025-01-01"), pd.Timestamp("2026-01-01")),
}


def diff_stat(x: pd.DataFrame, state: str, outcome: str) -> tuple[float, int, int]:
    z = x[x.base_state == state]
    h = z[z.factor_substate == "F_HIGH"][outcome].dropna()
    l = z[z.factor_substate == "F_LOW"][outcome].dropna()
    if len(h) < 5 or len(l) < 5:
        return np.nan, len(h), len(l)
    return float(h.mean() - l.mean()), len(h), len(l)


def moving_block_sample(x: pd.DataFrame, rng: np.random.Generator, block: int) -> pd.DataFrame:
    n = len(x)
    if n <= block:
        return x.sample(n=n, replace=True, random_state=int(rng.integers(0, 2**31-1)))
    n_blocks = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=n_blocks)
    idx = []
    for s in starts:
        idx.extend([(s + j) % n for j in range(block)])
    return x.iloc[idx[:n]].copy()


def bootstrap_one(x: pd.DataFrame, state: str, outcome: str, seed: int) -> dict:
    point, nh, nl = diff_stat(x, state, outcome)
    if not np.isfinite(point):
        return {"point": point, "n_high": nh, "n_low": nl, "boot_n": 0}
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(N_BOOT):
        b = moving_block_sample(x, rng, BLOCK)
        v, bh, bl = diff_stat(b, state, outcome)
        if np.isfinite(v) and min(bh, bl) >= 5:
            vals.append(v)
    if len(vals) < 500:
        return {"point": point, "n_high": nh, "n_low": nl, "boot_n": len(vals)}
    a = np.asarray(vals)
    return {
        "point": point, "n_high": nh, "n_low": nl, "boot_n": len(a),
        "ci025": float(np.quantile(a, .025)), "ci975": float(np.quantile(a, .975)),
        "p_gt0": float((a > 0).mean()), "p_lt0": float((a < 0).mean()),
        "boot_median": float(np.median(a)),
    }


def main():
    df = pd.read_csv(INPUT)
    df["date"] = pd.to_datetime(df["date"])
    rows = []
    for i, (u, bs, outcome) in enumerate(TARGETS):
        gu = df[df.universe == u].sort_values("date")
        for j, (period, (lo, hi)) in enumerate(PERIODS.items()):
            x = gu[(gu.date >= lo) & (gu.date < hi)].copy()
            if x.empty:
                continue
            r = bootstrap_one(x, bs, outcome, SEED + i * 17 + j)
            rows.append({"universe": u, "base_state": bs, "outcome": outcome, "period": period,
                         "block_states": BLOCK, "n_boot_target": N_BOOT, **r})
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "nested_block_bootstrap.csv", index=False, encoding="utf-8-sig")

    lines = ["# Nested Transition Block-Bootstrap", "",
             f"Moving-block bootstrap: {N_BOOT} replications, block length {BLOCK} consecutive 5D state dates (~20 trading days). State definitions are fixed; this tests sampling uncertainty, not model-selection uncertainty.", ""]
    for _, r in out.iterrows():
        if not np.isfinite(r.get("ci025", np.nan)):
            continue
        lines.append(f"- {r.universe} {r.base_state} {r.outcome} {r.period}: H-L {r.point:+.2%}, 95% block CI [{r.ci025:+.2%}, {r.ci975:+.2%}], P(>0) {r.p_gt0:.0%}, P(<0) {r.p_lt0:.0%}, n H/L={int(r.n_high)}/{int(r.n_low)}")
    lines += ["", "Interpretation: transition-probability rows are percentage-point differences. For future drawdown, a positive H-L means a less-negative/better downside path for F_HIGH; for future return, positive means higher return.", ""]
    (OUT / "NESTED_BOOTSTRAP_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    print(len(out))

if __name__ == "__main__":
    main()
