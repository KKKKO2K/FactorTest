from __future__ import annotations

from pathlib import Path

import pandas as pd

import creative_factor_lab_v2 as calibrated

lab = calibrated.lab
lab.OUT = Path(__file__).resolve().parent / "creative_factor_results_v2_micro"
lab.OUT.mkdir(parents=True, exist_ok=True)
lab.UNIVERSES = ("KOSPI_EX_K200",)
lab.STEPS = (5,)
lab.COSTS = (60,)

# This focused run only needs tabular results; skip large feature-panel pickles.
pd.DataFrame.to_pickle = lambda self, *args, **kwargs: None

if __name__ == "__main__":
    lab.main()
