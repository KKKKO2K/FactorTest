# Factor Regime Horizon Robustness

Purpose: compare nearby lookback definitions before building the 2x2 factor-breadth x liquidity-breadth regime map.
Factor breadth uses canonical factor long-short returns compounded over 5/10/20/40 trading days.
Liquidity breadth is the share of universe stocks whose recent average trading amount exceeds a strictly preceding baseline. Recent-window sensitivity holds the baseline at 20D (1/3/5/10/20 vs 20); baseline sensitivity holds the recent window at 5D (5 vs 10/20/40/60), with 20/60 as a slow anchor.
State low/high thresholds are fit on 2016-2022 TRAIN only and frozen for 2023+ OOS. Market target is the same universe. Forward horizons are 1/5/20D.
Selection principle: prefer TRAIN->OOS sign stability and a broad neighboring-horizon plateau, not the single largest OOS return spread.

## FACTOR_BREADTH

- FACTOR_20D: avg sign-stability 72%; median sign-confirmed OOS H-L +0.38%; median |OOS H-L| +0.57%
- FACTOR_40D: avg sign-stability 39%; median sign-confirmed OOS H-L -0.12%; median |OOS H-L| +0.21%
- FACTOR_10D: avg sign-stability 39%; median sign-confirmed OOS H-L -0.14%; median |OOS H-L| +0.27%
- FACTOR_5D: avg sign-stability 17%; median sign-confirmed OOS H-L -0.25%; median |OOS H-L| +0.31%

Forward 1D:
- FACTOR_20D: sign-stability 67%, confirmed OOS +0.03%, median |H-L| +0.08%
- FACTOR_40D: sign-stability 50%, confirmed OOS -0.05%, median |H-L| +0.21%
- FACTOR_10D: sign-stability 17%, confirmed OOS -0.14%, median |H-L| +0.20%
- FACTOR_5D: sign-stability 17%, confirmed OOS -0.22%, median |H-L| +0.31%

Forward 5D:
- FACTOR_20D: sign-stability 67%, confirmed OOS +0.38%, median |H-L| +0.57%
- FACTOR_40D: sign-stability 33%, confirmed OOS -0.12%, median |H-L| +0.12%
- FACTOR_10D: sign-stability 33%, confirmed OOS -0.14%, median |H-L| +0.27%
- FACTOR_5D: sign-stability 17%, confirmed OOS -0.25%, median |H-L| +0.25%

Forward 20D:
- FACTOR_20D: sign-stability 83%, confirmed OOS +1.73%, median |H-L| +2.10%
- FACTOR_10D: sign-stability 67%, confirmed OOS +0.90%, median |H-L| +0.90%
- FACTOR_40D: sign-stability 33%, confirmed OOS -0.25%, median |H-L| +0.52%
- FACTOR_5D: sign-stability 17%, confirmed OOS -0.56%, median |H-L| +0.64%

## LIQUIDITY_BREADTH

- LIQ_1D_VS_20D: avg sign-stability 72%; median sign-confirmed OOS H-L +1.18%; median |OOS H-L| +1.25%
- LIQ_5D_VS_10D: avg sign-stability 56%; median sign-confirmed OOS H-L +0.83%; median |OOS H-L| +0.83%
- LIQ_5D_VS_20D: avg sign-stability 56%; median sign-confirmed OOS H-L +1.34%; median |OOS H-L| +1.45%
- LIQ_5D_VS_40D: avg sign-stability 56%; median sign-confirmed OOS H-L -0.02%; median |OOS H-L| +0.86%
- LIQ_20D_VS_60D: avg sign-stability 56%; median sign-confirmed OOS H-L -0.58%; median |OOS H-L| +0.90%
- LIQ_5D_VS_60D: avg sign-stability 50%; median sign-confirmed OOS H-L +0.87%; median |OOS H-L| +0.87%
- LIQ_10D_VS_20D: avg sign-stability 50%; median sign-confirmed OOS H-L +0.58%; median |OOS H-L| +0.89%
- LIQ_3D_VS_20D: avg sign-stability 44%; median sign-confirmed OOS H-L +1.05%; median |OOS H-L| +1.15%
- LIQ_20D_VS_20D: avg sign-stability 39%; median sign-confirmed OOS H-L -0.00%; median |OOS H-L| +0.24%

Forward 1D:
- LIQ_20D_VS_60D: sign-stability 100%, confirmed OOS +0.08%, median |H-L| +0.08%
- LIQ_1D_VS_20D: sign-stability 50%, confirmed OOS +0.10%, median |H-L| +0.31%
- LIQ_20D_VS_20D: sign-stability 50%, confirmed OOS -0.00%, median |H-L| +0.09%
- LIQ_5D_VS_40D: sign-stability 33%, confirmed OOS -0.25%, median |H-L| +0.32%
- LIQ_5D_VS_60D: sign-stability 17%, confirmed OOS -0.18%, median |H-L| +0.26%
- LIQ_5D_VS_20D: sign-stability 17%, confirmed OOS -0.18%, median |H-L| +0.18%
- LIQ_10D_VS_20D: sign-stability 17%, confirmed OOS -0.23%, median |H-L| +0.23%
- LIQ_5D_VS_10D: sign-stability 0%, confirmed OOS -0.18%, median |H-L| +0.18%
- LIQ_3D_VS_20D: sign-stability 0%, confirmed OOS -0.28%, median |H-L| +0.28%

Forward 5D:
- LIQ_5D_VS_20D: sign-stability 83%, confirmed OOS +1.43%, median |H-L| +1.45%
- LIQ_5D_VS_10D: sign-stability 83%, confirmed OOS +0.83%, median |H-L| +0.83%
- LIQ_5D_VS_40D: sign-stability 83%, confirmed OOS +0.75%, median |H-L| +0.86%
- LIQ_1D_VS_20D: sign-stability 67%, confirmed OOS +1.18%, median |H-L| +1.25%
- LIQ_3D_VS_20D: sign-stability 67%, confirmed OOS +1.05%, median |H-L| +1.15%
- LIQ_5D_VS_60D: sign-stability 67%, confirmed OOS +0.87%, median |H-L| +0.87%
- LIQ_10D_VS_20D: sign-stability 67%, confirmed OOS +0.58%, median |H-L| +1.02%
- LIQ_20D_VS_60D: sign-stability 33%, confirmed OOS -0.58%, median |H-L| +0.90%
- LIQ_20D_VS_20D: sign-stability 17%, confirmed OOS -0.20%, median |H-L| +0.24%

Forward 20D:
- LIQ_1D_VS_20D: sign-stability 100%, confirmed OOS +1.92%, median |H-L| +1.92%
- LIQ_5D_VS_10D: sign-stability 83%, confirmed OOS +1.48%, median |H-L| +1.51%
- LIQ_5D_VS_60D: sign-stability 67%, confirmed OOS +1.72%, median |H-L| +1.72%
- LIQ_3D_VS_20D: sign-stability 67%, confirmed OOS +1.56%, median |H-L| +1.97%
- LIQ_5D_VS_20D: sign-stability 67%, confirmed OOS +1.34%, median |H-L| +2.19%
- LIQ_10D_VS_20D: sign-stability 67%, confirmed OOS +0.86%, median |H-L| +0.89%
- LIQ_20D_VS_20D: sign-stability 50%, confirmed OOS +0.17%, median |H-L| +0.55%
- LIQ_5D_VS_40D: sign-stability 50%, confirmed OOS -0.02%, median |H-L| +0.87%
- LIQ_20D_VS_60D: sign-stability 33%, confirmed OOS -2.25%, median |H-L| +2.53%

## Universe detail: 20D forward return

### K200
FACTOR_BREADTH:
- FACTOR_10D: TRAIN H-L +0.31%, OOS H-L +1.44%, same-sign=True
- FACTOR_40D: TRAIN H-L -0.08%, OOS H-L +0.47%, same-sign=False
- FACTOR_20D: TRAIN H-L -0.23%, OOS H-L +1.51%, same-sign=False
- FACTOR_5D: TRAIN H-L -0.13%, OOS H-L +1.83%, same-sign=False
LIQUIDITY_BREADTH:
- LIQ_5D_VS_60D: TRAIN H-L -0.66%, OOS H-L -2.48%, same-sign=True
- LIQ_1D_VS_20D: TRAIN H-L +0.40%, OOS H-L +2.41%, same-sign=True
- LIQ_20D_VS_20D: TRAIN H-L -0.78%, OOS H-L -2.20%, same-sign=True
- LIQ_5D_VS_40D: TRAIN H-L -0.58%, OOS H-L -0.48%, same-sign=True
- LIQ_10D_VS_20D: TRAIN H-L -0.48%, OOS H-L +0.90%, same-sign=False
- LIQ_3D_VS_20D: TRAIN H-L -0.62%, OOS H-L +1.00%, same-sign=False
- LIQ_5D_VS_10D: TRAIN H-L -0.39%, OOS H-L +1.49%, same-sign=False
- LIQ_5D_VS_20D: TRAIN H-L -0.85%, OOS H-L +2.42%, same-sign=False
- LIQ_20D_VS_60D: TRAIN H-L +0.53%, OOS H-L -4.82%, same-sign=False

### KOSPI_EX_K200
FACTOR_BREADTH:
- FACTOR_40D: TRAIN H-L -1.26%, OOS H-L -1.40%, same-sign=True
- FACTOR_20D: TRAIN H-L -0.74%, OOS H-L -0.77%, same-sign=True
- FACTOR_10D: TRAIN H-L -0.13%, OOS H-L +0.01%, same-sign=False
- FACTOR_5D: TRAIN H-L +0.47%, OOS H-L -0.47%, same-sign=False
LIQUIDITY_BREADTH:
- LIQ_20D_VS_60D: TRAIN H-L +0.73%, OOS H-L +3.37%, same-sign=True
- LIQ_5D_VS_60D: TRAIN H-L +0.57%, OOS H-L +1.82%, same-sign=True
- LIQ_3D_VS_20D: TRAIN H-L +1.31%, OOS H-L +1.16%, same-sign=True
- LIQ_10D_VS_20D: TRAIN H-L +0.91%, OOS H-L +0.88%, same-sign=True
- LIQ_5D_VS_20D: TRAIN H-L +1.66%, OOS H-L +0.75%, same-sign=True
- LIQ_20D_VS_20D: TRAIN H-L +0.52%, OOS H-L +0.68%, same-sign=True
- LIQ_5D_VS_40D: TRAIN H-L +0.39%, OOS H-L +0.62%, same-sign=True
- LIQ_5D_VS_10D: TRAIN H-L +1.38%, OOS H-L +0.33%, same-sign=True
- LIQ_1D_VS_20D: TRAIN H-L +1.47%, OOS H-L +0.32%, same-sign=True

### KOSPI_ALL
FACTOR_BREADTH:
- FACTOR_20D: TRAIN H-L +0.25%, OOS H-L +3.08%, same-sign=True
- FACTOR_40D: TRAIN H-L -0.05%, OOS H-L +0.57%, same-sign=False
- FACTOR_10D: TRAIN H-L -0.08%, OOS H-L +0.60%, same-sign=False
- FACTOR_5D: TRAIN H-L -0.02%, OOS H-L +1.20%, same-sign=False
LIQUIDITY_BREADTH:
- LIQ_3D_VS_20D: TRAIN H-L +0.00%, OOS H-L +2.94%, same-sign=True
- LIQ_1D_VS_20D: TRAIN H-L +0.09%, OOS H-L +2.85%, same-sign=True
- LIQ_10D_VS_20D: TRAIN H-L +0.18%, OOS H-L +2.38%, same-sign=True
- LIQ_5D_VS_10D: TRAIN H-L +0.57%, OOS H-L +2.18%, same-sign=True
- LIQ_20D_VS_60D: TRAIN H-L +0.35%, OOS H-L +1.09%, same-sign=True
- LIQ_20D_VS_20D: TRAIN H-L -0.46%, OOS H-L -0.52%, same-sign=True
- LIQ_5D_VS_60D: TRAIN H-L -0.32%, OOS H-L +0.84%, same-sign=False
- LIQ_5D_VS_40D: TRAIN H-L -0.46%, OOS H-L +1.54%, same-sign=False
- LIQ_5D_VS_20D: TRAIN H-L -0.15%, OOS H-L +3.24%, same-sign=False

### KOSDAQ
FACTOR_BREADTH:
- FACTOR_20D: TRAIN H-L -1.76%, OOS H-L -2.77%, same-sign=True
- FACTOR_10D: TRAIN H-L -0.55%, OOS H-L -0.94%, same-sign=True
- FACTOR_5D: TRAIN H-L -0.39%, OOS H-L -0.68%, same-sign=True
- FACTOR_40D: TRAIN H-L -2.93%, OOS H-L +0.03%, same-sign=False
LIQUIDITY_BREADTH:
- LIQ_5D_VS_20D: TRAIN H-L +0.15%, OOS H-L +1.97%, same-sign=True
- LIQ_5D_VS_10D: TRAIN H-L +0.86%, OOS H-L +1.54%, same-sign=True
- LIQ_1D_VS_20D: TRAIN H-L +1.13%, OOS H-L +1.44%, same-sign=True
- LIQ_10D_VS_20D: TRAIN H-L -0.10%, OOS H-L +0.25%, same-sign=False
- LIQ_20D_VS_20D: TRAIN H-L -1.64%, OOS H-L +0.30%, same-sign=False
- LIQ_5D_VS_40D: TRAIN H-L -0.61%, OOS H-L +0.51%, same-sign=False
- LIQ_5D_VS_60D: TRAIN H-L -0.96%, OOS H-L +1.43%, same-sign=False
- LIQ_20D_VS_60D: TRAIN H-L -0.71%, OOS H-L +1.98%, same-sign=False
- LIQ_3D_VS_20D: TRAIN H-L -0.29%, OOS H-L +1.98%, same-sign=False

### KOSPI_KOSDAQ_ALL
FACTOR_BREADTH:
- FACTOR_10D: TRAIN H-L +0.29%, OOS H-L +0.86%, same-sign=True
- FACTOR_20D: TRAIN H-L -0.13%, OOS H-L -0.36%, same-sign=True
- FACTOR_5D: TRAIN H-L -0.25%, OOS H-L +0.60%, same-sign=False
- FACTOR_40D: TRAIN H-L -0.88%, OOS H-L +1.18%, same-sign=False
LIQUIDITY_BREADTH:
- LIQ_3D_VS_20D: TRAIN H-L +0.08%, OOS H-L +4.50%, same-sign=True
- LIQ_5D_VS_20D: TRAIN H-L +0.15%, OOS H-L +4.40%, same-sign=True
- LIQ_1D_VS_20D: TRAIN H-L +0.90%, OOS H-L +4.12%, same-sign=True
- LIQ_5D_VS_10D: TRAIN H-L +0.79%, OOS H-L +2.92%, same-sign=True
- LIQ_5D_VS_60D: TRAIN H-L +0.01%, OOS H-L +2.88%, same-sign=True
- LIQ_10D_VS_20D: TRAIN H-L +0.21%, OOS H-L +2.87%, same-sign=True
- LIQ_20D_VS_20D: TRAIN H-L -0.96%, OOS H-L +0.19%, same-sign=False
- LIQ_20D_VS_60D: TRAIN H-L -0.41%, OOS H-L +2.52%, same-sign=False
- LIQ_5D_VS_40D: TRAIN H-L -0.24%, OOS H-L +2.67%, same-sign=False

### KOSDAQ_PLUS_KOSPI_EX_K200
FACTOR_BREADTH:
- FACTOR_20D: TRAIN H-L -2.15%, OOS H-L -2.68%, same-sign=True
- FACTOR_10D: TRAIN H-L -0.22%, OOS H-L -2.14%, same-sign=True
- FACTOR_40D: TRAIN H-L -2.26%, OOS H-L -0.10%, same-sign=True
- FACTOR_5D: TRAIN H-L -0.65%, OOS H-L +0.51%, same-sign=False
LIQUIDITY_BREADTH:
- LIQ_3D_VS_20D: TRAIN H-L +0.95%, OOS H-L +1.96%, same-sign=True
- LIQ_5D_VS_20D: TRAIN H-L +1.07%, OOS H-L +1.93%, same-sign=True
- LIQ_5D_VS_60D: TRAIN H-L +0.25%, OOS H-L +1.63%, same-sign=True
- LIQ_5D_VS_10D: TRAIN H-L +1.26%, OOS H-L +1.42%, same-sign=True
- LIQ_1D_VS_20D: TRAIN H-L +1.51%, OOS H-L +1.38%, same-sign=True
- LIQ_5D_VS_40D: TRAIN H-L +0.16%, OOS H-L +1.12%, same-sign=True
- LIQ_10D_VS_20D: TRAIN H-L +0.42%, OOS H-L +0.85%, same-sign=True
- LIQ_20D_VS_20D: TRAIN H-L -0.84%, OOS H-L +0.58%, same-sign=False
- LIQ_20D_VS_60D: TRAIN H-L -0.14%, OOS H-L +2.53%, same-sign=False

## Guardrails

- This is a horizon robustness screen, not an optimization exercise. Do not choose a definition solely because it has the largest OOS H-L.
- 20D forward returns overlap across 5D state dates; t-stats are descriptive.
- If adjacent lookbacks behave similarly, prefer the simpler/slower definition unless responsiveness is economically important.
- Any 2x2 regime test performed after this screen is post-discovery validation, not pristine OOS.
