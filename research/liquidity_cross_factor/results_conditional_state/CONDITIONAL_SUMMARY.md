# Conditional liquidity-state test

State tercile thresholds are estimated on 2016-2022 TRAIN only and frozen into 2023+ OOS.
H-L is the annualized arithmetic overlay uplift in HIGH state minus LOW state, always versus the same BASE.

## K200

### ACT1_W10
- MKT_ACT1_BREADTH: TRAIN H-L +0.23%, OOS H-L -6.86%; OOS positive-config 38%; same-sign=False
- FACTOR_TOP_ACT5_BREADTH: TRAIN H-L -0.47%, OOS H-L -5.11%; OOS positive-config 31%; same-sign=True
- MKT_ACT1: TRAIN H-L +0.61%, OOS H-L -3.03%; OOS positive-config 38%; same-sign=False
- MKT_ACT5_BREADTH: TRAIN H-L +2.16%, OOS H-L -2.35%; OOS positive-config 35%; same-sign=False
- FACTOR_TOP_TA_SHARE: TRAIN H-L -0.86%, OOS H-L +1.83%; OOS positive-config 57%; same-sign=False

### ACT5_KEEP_TOP70
- FACTOR_TOP_ACT5_BREADTH: TRAIN H-L -1.90%, OOS H-L -8.84%; OOS positive-config 32%; same-sign=True
- MKT_ACT5_BREADTH: TRAIN H-L -0.89%, OOS H-L -8.53%; OOS positive-config 19%; same-sign=True
- MKT_ACT1_BREADTH: TRAIN H-L -1.45%, OOS H-L -5.04%; OOS positive-config 38%; same-sign=True
- MKT_ACT1: TRAIN H-L -2.88%, OOS H-L -5.47%; OOS positive-config 22%; same-sign=True
- FACTOR_TOP_TA_SHARE: TRAIN H-L -4.01%, OOS H-L -3.44%; OOS positive-config 39%; same-sign=True

## KOSPI_EX_K200

### ACT1_W10
- MKT_ACT1_BREADTH: TRAIN H-L -1.82%, OOS H-L -7.13%; OOS positive-config 15%; same-sign=True
- MKT_ACT5: TRAIN H-L -1.46%, OOS H-L -3.12%; OOS positive-config 35%; same-sign=True
- FACTOR_TOP_TA_SHARE: TRAIN H-L -1.24%, OOS H-L +2.56%; OOS positive-config 54%; same-sign=False
- FACTOR_TOP_REL_ACT5: TRAIN H-L +0.29%, OOS H-L -2.24%; OOS positive-config 43%; same-sign=False
- MKT_ACT1: TRAIN H-L -0.92%, OOS H-L -1.62%; OOS positive-config 36%; same-sign=True

### ACT5_KEEP_TOP70
- FACTOR_TOP_TA_SHARE: TRAIN H-L -1.24%, OOS H-L +5.94%; OOS positive-config 68%; same-sign=False
- MKT_ACT1: TRAIN H-L -3.71%, OOS H-L -6.31%; OOS positive-config 28%; same-sign=True
- MKT_ACT1_BREADTH: TRAIN H-L +1.04%, OOS H-L -5.73%; OOS positive-config 19%; same-sign=False
- KOSDAQ_TA_SHARE: TRAIN H-L +1.76%, OOS H-L -3.28%; OOS positive-config 31%; same-sign=False
- FACTOR_TOP_ACT5_BREADTH: TRAIN H-L -2.17%, OOS H-L +2.23%; OOS positive-config 55%; same-sign=False

## KOSPI_ALL

### ACT1_W10
- MKT_ACT1_BREADTH: TRAIN H-L -0.25%, OOS H-L -7.85%; OOS positive-config 22%; same-sign=True
- FACTOR_TOP_ACT5_BREADTH: TRAIN H-L -2.12%, OOS H-L -5.87%; OOS positive-config 31%; same-sign=True
- FACTOR_TOP_TA_SHARE: TRAIN H-L -2.23%, OOS H-L +3.38%; OOS positive-config 70%; same-sign=False
- MKT_ACT5_BREADTH: TRAIN H-L +1.08%, OOS H-L -4.03%; OOS positive-config 38%; same-sign=False
- MKT_ACT1: TRAIN H-L -2.05%, OOS H-L -3.60%; OOS positive-config 38%; same-sign=True

### ACT5_KEEP_TOP70
- MKT_ACT1_BREADTH: TRAIN H-L -0.44%, OOS H-L -6.64%; OOS positive-config 25%; same-sign=True
- KOSDAQ_TA_SHARE: TRAIN H-L +1.77%, OOS H-L -4.12%; OOS positive-config 25%; same-sign=False
- MKT_ACT1: TRAIN H-L -2.69%, OOS H-L -3.33%; OOS positive-config 34%; same-sign=True
- MKT_ACT5_BREADTH: TRAIN H-L -0.85%, OOS H-L -2.97%; OOS positive-config 34%; same-sign=True
- FACTOR_TOP_ACT5_BREADTH: TRAIN H-L -0.33%, OOS H-L -2.50%; OOS positive-config 38%; same-sign=True

## KOSDAQ

### ACT1_W10
- KOSDAQ_TA_SHARE: TRAIN H-L +2.42%, OOS H-L -3.95%; OOS positive-config 41%; same-sign=False
- MKT_ACT1: TRAIN H-L -2.09%, OOS H-L +2.60%; OOS positive-config 66%; same-sign=False
- MKT_ACT5_BREADTH: TRAIN H-L -2.32%, OOS H-L -2.73%; OOS positive-config 40%; same-sign=True
- FACTOR_TOP_TA_SHARE: TRAIN H-L +0.07%, OOS H-L -2.51%; OOS positive-config 38%; same-sign=False
- MKT_ACT5: TRAIN H-L -0.34%, OOS H-L +1.92%; OOS positive-config 56%; same-sign=False

### ACT5_KEEP_TOP70
- MKT_ACT1: TRAIN H-L -5.02%, OOS H-L +3.89%; OOS positive-config 65%; same-sign=False
- MKT_ACT5: TRAIN H-L -2.25%, OOS H-L +3.52%; OOS positive-config 69%; same-sign=False
- KOSDAQ_TA_SHARE: TRAIN H-L +0.50%, OOS H-L +3.93%; OOS positive-config 56%; same-sign=True
- MKT_ACT1_BREADTH: TRAIN H-L -1.97%, OOS H-L +2.64%; OOS positive-config 61%; same-sign=False
- MKT_ACT5_BREADTH: TRAIN H-L -3.39%, OOS H-L +1.64%; OOS positive-config 53%; same-sign=False

## KOSPI_KOSDAQ_ALL

### ACT1_W10
- MKT_ACT1_BREADTH: TRAIN H-L -1.57%, OOS H-L -14.72%; OOS positive-config 26%; same-sign=True
- MKT_ACT1: TRAIN H-L -9.06%, OOS H-L -5.97%; OOS positive-config 38%; same-sign=True
- KOSDAQ_TA_SHARE: TRAIN H-L +1.16%, OOS H-L -2.75%; OOS positive-config 47%; same-sign=False
- MKT_ACT5: TRAIN H-L -10.08%, OOS H-L -2.39%; OOS positive-config 41%; same-sign=True
- FACTOR_TOP_REL_ACT5: TRAIN H-L -0.99%, OOS H-L -2.00%; OOS positive-config 47%; same-sign=True

### ACT5_KEEP_TOP70
- MKT_ACT5_BREADTH: TRAIN H-L -2.63%, OOS H-L -4.51%; OOS positive-config 34%; same-sign=True
- KOSDAQ_TA_SHARE: TRAIN H-L +2.57%, OOS H-L -4.03%; OOS positive-config 34%; same-sign=False
- FACTOR_TOP_REL_ACT5: TRAIN H-L +1.56%, OOS H-L -3.43%; OOS positive-config 41%; same-sign=False
- MKT_ACT5: TRAIN H-L -2.42%, OOS H-L -3.42%; OOS positive-config 41%; same-sign=True
- FACTOR_TOP_TA_SHARE: TRAIN H-L +1.20%, OOS H-L +2.15%; OOS positive-config 56%; same-sign=True

## KOSDAQ_PLUS_KOSPI_EX_K200

### ACT1_W10
- MKT_ACT1_BREADTH: TRAIN H-L -0.38%, OOS H-L -10.77%; OOS positive-config 31%; same-sign=True
- FACTOR_TOP_TA_SHARE: TRAIN H-L -0.90%, OOS H-L -5.10%; OOS positive-config 38%; same-sign=True
- FACTOR_TOP_REL_ACT5: TRAIN H-L -1.28%, OOS H-L -2.55%; OOS positive-config 44%; same-sign=True
- MKT_ACT1: TRAIN H-L -3.38%, OOS H-L -2.54%; OOS positive-config 41%; same-sign=True
- FACTOR_TOP_ACT5_BREADTH: TRAIN H-L -1.98%, OOS H-L -1.58%; OOS positive-config 42%; same-sign=True

### ACT5_KEEP_TOP70
- FACTOR_TOP_TA_SHARE: TRAIN H-L -0.31%, OOS H-L -5.75%; OOS positive-config 42%; same-sign=True
- MKT_ACT5: TRAIN H-L -5.67%, OOS H-L +4.18%; OOS positive-config 62%; same-sign=False
- MKT_ACT1_BREADTH: TRAIN H-L +0.88%, OOS H-L -5.12%; OOS positive-config 38%; same-sign=False
- FACTOR_TOP_REL_ACT5: TRAIN H-L -2.39%, OOS H-L +3.74%; OOS positive-config 66%; same-sign=False
- MKT_ACT5_BREADTH: TRAIN H-L -1.72%, OOS H-L -1.60%; OOS positive-config 41%; same-sign=True

# Cross-universe

## ACT1_W10
- MKT_ACT1_BREADTH: same-sign 67%; median TRAIN H-L -0.97%; median OOS H-L -7.49%; OOS positive-config 29%
- MKT_ACT1: same-sign 67%; median TRAIN H-L -2.07%; median OOS H-L -2.79%; OOS positive-config 38%
- FACTOR_TOP_ACT5_BREADTH: same-sign 100%; median TRAIN H-L -2.08%; median OOS H-L -1.50%; OOS positive-config 41%
- FACTOR_TOP_REL_ACT5: same-sign 67%; median TRAIN H-L -1.13%; median OOS H-L -1.76%; OOS positive-config 45%
- MKT_ACT5_BREADTH: same-sign 67%; median TRAIN H-L -1.24%; median OOS H-L -1.75%; OOS positive-config 43%
- KOSDAQ_TA_SHARE: same-sign 33%; median TRAIN H-L +1.07%; median OOS H-L -1.62%; OOS positive-config 46%
- FACTOR_TOP_TA_SHARE: same-sign 33%; median TRAIN H-L -0.89%; median OOS H-L +0.62%; OOS positive-config 49%
- MKT_ACT5: same-sign 33%; median TRAIN H-L -1.20%; median OOS H-L -0.49%; OOS positive-config 47%

## ACT5_KEEP_TOP70
- MKT_ACT1_BREADTH: same-sign 50%; median TRAIN H-L -0.95%; median OOS H-L -5.08%; OOS positive-config 35%
- MKT_ACT5_BREADTH: same-sign 83%; median TRAIN H-L -1.30%; median OOS H-L -2.28%; OOS positive-config 38%
- MKT_ACT1: same-sign 50%; median TRAIN H-L -3.78%; median OOS H-L -1.31%; OOS positive-config 44%
- FACTOR_TOP_TA_SHARE: same-sign 67%; median TRAIN H-L +0.40%; median OOS H-L -0.80%; OOS positive-config 47%
- FACTOR_TOP_ACT5_BREADTH: same-sign 67%; median TRAIN H-L -1.89%; median OOS H-L -0.66%; OOS positive-config 47%
- KOSDAQ_TA_SHARE: same-sign 17%; median TRAIN H-L +1.66%; median OOS H-L -1.79%; OOS positive-config 41%
- FACTOR_TOP_REL_ACT5: same-sign 33%; median TRAIN H-L +0.66%; median OOS H-L -0.80%; OOS positive-config 47%
- MKT_ACT5: same-sign 50%; median TRAIN H-L -1.91%; median OOS H-L -0.37%; OOS positive-config 48%

