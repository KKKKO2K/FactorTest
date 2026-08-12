from __future__ import annotations

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


base.load_liquidity = load_liquidity_long

if __name__ == "__main__":
    base.main()
