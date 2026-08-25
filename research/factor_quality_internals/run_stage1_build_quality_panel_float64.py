from __future__ import annotations

import numpy as np
import pandas as pd

import run_stage1_build_quality_panel as base


def build_daily_matrices_float64(
    dates: list[pd.Timestamp],
    basic_files: dict[pd.Timestamp, object],
    trading_files: dict[pd.Timestamp, object],
) -> tuple[pd.Index, np.ndarray, np.ndarray]:
    """Precision-only replacement for Stage 1 matrix loading.

    The original runner used float32 solely as a memory optimization. The frozen
    sector-decomposition panel was calculated at float64 precision, so the
    strict 1e-10 reconstruction QA should compare like-for-like. No research
    definition, sample, feature, or threshold is changed here.
    """
    master = base.load_basic(basic_files[dates[0]], need_meta=False).index
    code_to_pos = pd.Series(np.arange(len(master), dtype=int), index=master)
    ret = np.full((len(dates), len(master)), np.nan, dtype=np.float64)
    ta = np.full((len(dates), len(master)), np.nan, dtype=np.float64)

    for i, dt in enumerate(dates):
        b = base.load_basic(basic_files[dt], need_meta=False)
        pos = code_to_pos.reindex(b.index).dropna().astype(int)
        if len(pos):
            vals = b.reindex(pos.index).ret.to_numpy(dtype=float)
            ret[i, pos.to_numpy()] = vals

        t = base.load_trading(trading_files[dt])
        pos_t = code_to_pos.reindex(t.index).dropna().astype(int)
        if len(pos_t):
            vals_t = t.reindex(pos_t.index).to_numpy(dtype=float)
            ta[i, pos_t.to_numpy()] = vals_t

        if (i + 1) % 250 == 0 or i + 1 == len(dates):
            print(f"loaded float64 daily return/trading matrices {i+1}/{len(dates)}")

    return master, ret, ta


if __name__ == "__main__":
    base.build_daily_matrices = build_daily_matrices_float64
    base.main()
