from __future__ import annotations

from pathlib import Path

import pandas as pd

import k200_liquidity_universe_expansion as liq

# Frozen follow-up: only REV_BREADTH uses the K200 + top-50 liquidity universe.
# VALUE_REV, CONTRARIAN, PYRAMID, LEADER and the K200 state/router remain unchanged.
liq.ADD_N = 50
liq.LABEL = "K200_LIQ20_PLUS_50"
liq.lad.ADD_N = 50
liq.lad.LABEL = liq.LABEL
liq.lad.ACTIVE = {"REV_BREADTH_70"}

OUT = Path(__file__).resolve().parent / "k200_revbreadth_liquidity_expansion_results"
OUT.mkdir(parents=True, exist_ok=True)
liq.OUT = OUT
liq.lad.OUT = OUT


if __name__ == "__main__":
    print(
        "Focused test: only REV_BREADTH_70 selects from K200 + top 50 KOSPI ex-K200 "
        "by trailing 20D average trading amount. All other production engines remain K200-only.",
        flush=True,
    )
    liq.lad.main()
    pd.DataFrame(liq._ELIGIBILITY_ROWS).sort_values("effective_snapshot_date").to_csv(
        OUT / "liquidity_eligibility_diagnostics.csv", index=False, encoding="utf-8-sig"
    )
