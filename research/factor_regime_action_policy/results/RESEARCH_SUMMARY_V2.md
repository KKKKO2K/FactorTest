# Regime-Conditioned Investment Action Research v2

Unconditional selection is now computed from raw TRAIN observations (not an unweighted average of state summaries). Cash periods are reported through participation plus active-only win rate.
State policies are regularized: 0/3/5PP means state-specific action is used only when its TRAIN win-rate (ABS) or beat-market-rate (ALPHA) advantage over the unconditional action is at least that threshold.

## 2023-2024 frozen-policy comparison

### K200
- MARKET: participation 100%, active win 56%, mean5 +0.07%, beat-mkt 0%, excess +0.00%, CAGR +2.1%, MDD -18.5%
- EW4: participation 100%, active win 53%, mean5 +0.18%, beat-mkt 49%, excess +0.11%, CAGR +8.1%, MDD -11.4%
- WPLUS: participation 100%, active win 53%, mean5 +0.26%, beat-mkt 46%, excess +0.19%, CAGR +12.0%, MDD -12.4%
- ABS_UNCOND: participation 100%, active win 56%, mean5 +0.07%, beat-mkt 0%, excess +0.00%, CAGR +2.1%, MDD -18.5%
- ABS_STATE_0PP: participation 32%, active win 48%, mean5 -0.01%, beat-mkt 44%, excess -0.08%, CAGR -0.6%, MDD -12.3%
- ABS_STATE_3PP: participation 32%, active win 48%, mean5 -0.01%, beat-mkt 44%, excess -0.08%, CAGR -0.6%, MDD -12.3%
- ABS_STATE_5PP: participation 32%, active win 48%, mean5 -0.01%, beat-mkt 44%, excess -0.08%, CAGR -0.6%, MDD -12.3%
- ALPHA_UNCOND: participation 100%, active win 49%, mean5 +0.14%, beat-mkt 47%, excess +0.07%, CAGR +5.2%, MDD -17.3%
- ALPHA_STATE_0PP: participation 100%, active win 52%, mean5 +0.18%, beat-mkt 45%, excess +0.11%, CAGR +7.6%, MDD -17.0%
- ALPHA_STATE_3PP: participation 100%, active win 52%, mean5 +0.18%, beat-mkt 45%, excess +0.11%, CAGR +7.6%, MDD -17.0%
- ALPHA_STATE_5PP: participation 100%, active win 52%, mean5 +0.18%, beat-mkt 45%, excess +0.11%, CAGR +7.6%, MDD -17.0%
### KOSDAQ
- MARKET: participation 100%, active win 55%, mean5 +0.03%, beat-mkt 0%, excess +0.00%, CAGR -0.6%, MDD -28.3%
- EW4: participation 100%, active win 59%, mean5 +0.16%, beat-mkt 53%, excess +0.13%, CAGR +4.7%, MDD -24.4%
- WPLUS: participation 100%, active win 58%, mean5 +0.16%, beat-mkt 55%, excess +0.13%, CAGR +4.3%, MDD -24.9%
- ABS_UNCOND: participation 100%, active win 52%, mean5 -0.02%, beat-mkt 48%, excess -0.05%, CAGR -3.0%, MDD -30.7%
- ABS_STATE_0PP: participation 100%, active win 52%, mean5 -0.02%, beat-mkt 48%, excess -0.05%, CAGR -3.0%, MDD -30.7%
- ABS_STATE_3PP: participation 100%, active win 52%, mean5 -0.02%, beat-mkt 48%, excess -0.05%, CAGR -3.0%, MDD -30.7%
- ABS_STATE_5PP: participation 100%, active win 52%, mean5 -0.02%, beat-mkt 48%, excess -0.05%, CAGR -3.0%, MDD -30.7%
- ALPHA_UNCOND: participation 100%, active win 52%, mean5 -0.02%, beat-mkt 48%, excess -0.05%, CAGR -3.0%, MDD -30.7%
- ALPHA_STATE_0PP: participation 100%, active win 52%, mean5 -0.02%, beat-mkt 48%, excess -0.05%, CAGR -3.0%, MDD -30.7%
- ALPHA_STATE_3PP: participation 100%, active win 52%, mean5 -0.02%, beat-mkt 48%, excess -0.05%, CAGR -3.0%, MDD -30.7%
- ALPHA_STATE_5PP: participation 100%, active win 52%, mean5 -0.02%, beat-mkt 48%, excess -0.05%, CAGR -3.0%, MDD -30.7%
### KOSDAQ_PLUS_KOSPI_EX_K200
- MARKET: participation 100%, active win 53%, mean5 +0.04%, beat-mkt 0%, excess +0.00%, CAGR -0.4%, MDD -30.6%
- EW4: participation 100%, active win 54%, mean5 +0.14%, beat-mkt 55%, excess +0.10%, CAGR +5.0%, MDD -28.5%
- WPLUS: participation 100%, active win 56%, mean5 +0.10%, beat-mkt 53%, excess +0.06%, CAGR +2.7%, MDD -31.2%
- ABS_UNCOND: participation 100%, active win 53%, mean5 +0.11%, beat-mkt 56%, excess +0.07%, CAGR +3.3%, MDD -28.7%
- ABS_STATE_0PP: participation 50%, active win 60%, mean5 +0.18%, beat-mkt 52%, excess +0.15%, CAGR +8.7%, MDD -8.9%
- ABS_STATE_3PP: participation 50%, active win 60%, mean5 +0.18%, beat-mkt 52%, excess +0.15%, CAGR +8.7%, MDD -8.9%
- ABS_STATE_5PP: participation 50%, active win 60%, mean5 +0.18%, beat-mkt 52%, excess +0.15%, CAGR +8.7%, MDD -8.9%
- ALPHA_UNCOND: participation 100%, active win 55%, mean5 +0.03%, beat-mkt 51%, excess -0.01%, CAGR -0.9%, MDD -33.6%
- ALPHA_STATE_0PP: participation 100%, active win 55%, mean5 -0.00%, beat-mkt 52%, excess -0.04%, CAGR -2.1%, MDD -32.6%
- ALPHA_STATE_3PP: participation 100%, active win 55%, mean5 -0.00%, beat-mkt 52%, excess -0.04%, CAGR -2.1%, MDD -32.6%
- ALPHA_STATE_5PP: participation 100%, active win 55%, mean5 -0.00%, beat-mkt 52%, excess -0.04%, CAGR -2.1%, MDD -32.6%
### KOSPI_ALL
- MARKET: participation 100%, active win 55%, mean5 +0.08%, beat-mkt 0%, excess +0.00%, CAGR +2.5%, MDD -18.4%
- EW4: participation 100%, active win 57%, mean5 +0.20%, beat-mkt 57%, excess +0.12%, CAGR +9.0%, MDD -13.7%
- WPLUS: participation 100%, active win 57%, mean5 +0.29%, beat-mkt 60%, excess +0.21%, CAGR +13.4%, MDD -15.5%
- ABS_UNCOND: participation 100%, active win 57%, mean5 +0.28%, beat-mkt 57%, excess +0.21%, CAGR +13.3%, MDD -15.0%
- ABS_STATE_0PP: participation 52%, active win 50%, mean5 -0.04%, beat-mkt 48%, excess -0.12%, CAGR -2.5%, MDD -12.8%
- ABS_STATE_3PP: participation 52%, active win 52%, mean5 +0.00%, beat-mkt 48%, excess -0.07%, CAGR -0.2%, MDD -9.4%
- ABS_STATE_5PP: participation 52%, active win 52%, mean5 +0.00%, beat-mkt 48%, excess -0.07%, CAGR -0.2%, MDD -9.4%
- ALPHA_UNCOND: participation 100%, active win 57%, mean5 +0.29%, beat-mkt 60%, excess +0.21%, CAGR +13.4%, MDD -15.5%
- ALPHA_STATE_0PP: participation 100%, active win 56%, mean5 +0.29%, beat-mkt 61%, excess +0.21%, CAGR +13.1%, MDD -15.6%
- ALPHA_STATE_3PP: participation 100%, active win 56%, mean5 +0.29%, beat-mkt 61%, excess +0.21%, CAGR +13.1%, MDD -15.6%
- ALPHA_STATE_5PP: participation 100%, active win 56%, mean5 +0.26%, beat-mkt 59%, excess +0.18%, CAGR +11.6%, MDD -15.5%
### KOSPI_EX_K200
- MARKET: participation 100%, active win 53%, mean5 +0.05%, beat-mkt 0%, excess +0.00%, CAGR +1.2%, MDD -17.7%
- EW4: participation 100%, active win 54%, mean5 +0.14%, beat-mkt 58%, excess +0.09%, CAGR +5.4%, MDD -16.7%
- WPLUS: participation 100%, active win 56%, mean5 +0.19%, beat-mkt 58%, excess +0.14%, CAGR +7.6%, MDD -20.0%
- ABS_UNCOND: participation 100%, active win 56%, mean5 +0.19%, beat-mkt 58%, excess +0.14%, CAGR +7.6%, MDD -20.0%
- ABS_STATE_0PP: participation 63%, active win 58%, mean5 +0.12%, beat-mkt 55%, excess +0.06%, CAGR +4.7%, MDD -12.9%
- ABS_STATE_3PP: participation 63%, active win 58%, mean5 +0.12%, beat-mkt 55%, excess +0.06%, CAGR +4.7%, MDD -12.9%
- ABS_STATE_5PP: participation 63%, active win 58%, mean5 +0.12%, beat-mkt 55%, excess +0.06%, CAGR +4.7%, MDD -12.9%
- ALPHA_UNCOND: participation 100%, active win 52%, mean5 +0.13%, beat-mkt 57%, excess +0.08%, CAGR +5.1%, MDD -17.6%
- ALPHA_STATE_0PP: participation 100%, active win 54%, mean5 +0.10%, beat-mkt 58%, excess +0.05%, CAGR +3.2%, MDD -18.4%
- ALPHA_STATE_3PP: participation 100%, active win 53%, mean5 +0.11%, beat-mkt 57%, excess +0.06%, CAGR +3.9%, MDD -18.2%
- ALPHA_STATE_5PP: participation 100%, active win 53%, mean5 +0.14%, beat-mkt 57%, excess +0.09%, CAGR +5.6%, MDD -17.6%
### KOSPI_KOSDAQ_ALL
- MARKET: participation 100%, active win 52%, mean5 +0.01%, beat-mkt 0%, excess +0.00%, CAGR -0.7%, MDD -23.9%
- EW4: participation 100%, active win 55%, mean5 +0.16%, beat-mkt 57%, excess +0.14%, CAGR +6.3%, MDD -23.6%
- WPLUS: participation 100%, active win 52%, mean5 +0.06%, beat-mkt 55%, excess +0.05%, CAGR +1.3%, MDD -25.7%
- ABS_UNCOND: participation 100%, active win 47%, mean5 +0.02%, beat-mkt 49%, excess +0.01%, CAGR -0.7%, MDD -26.8%
- ABS_STATE_0PP: participation 51%, active win 53%, mean5 +0.08%, beat-mkt 53%, excess +0.06%, CAGR +2.9%, MDD -12.5%
- ABS_STATE_3PP: participation 51%, active win 53%, mean5 +0.08%, beat-mkt 53%, excess +0.06%, CAGR +2.9%, MDD -12.5%
- ABS_STATE_5PP: participation 51%, active win 53%, mean5 +0.08%, beat-mkt 53%, excess +0.06%, CAGR +2.9%, MDD -12.5%
- ALPHA_UNCOND: participation 100%, active win 47%, mean5 +0.02%, beat-mkt 49%, excess +0.01%, CAGR -0.7%, MDD -26.8%
- ALPHA_STATE_0PP: participation 100%, active win 47%, mean5 +0.01%, beat-mkt 49%, excess -0.00%, CAGR -1.1%, MDD -29.8%
- ALPHA_STATE_3PP: participation 100%, active win 47%, mean5 +0.03%, beat-mkt 49%, excess +0.02%, CAGR -0.2%, MDD -27.9%
- ALPHA_STATE_5PP: participation 100%, active win 47%, mean5 +0.03%, beat-mkt 49%, excess +0.02%, CAGR -0.2%, MDD -27.9%

## 2025 stress

### K200
- MARKET: participation 100%, active win 71%, mean5 +1.42%, excess +0.00%, CAGR +97.4%, MDD -8.6%
- WPLUS: participation 100%, active win 57%, mean5 +1.09%, excess -0.34%, CAGR +67.5%, MDD -8.2%
- ABS_UNCOND: participation 100%, active win 71%, mean5 +1.42%, excess +0.00%, CAGR +97.4%, MDD -8.6%
- ABS_STATE_3PP: participation 57%, active win 61%, mean5 +0.78%, excess -0.64%, CAGR +45.2%, MDD -7.2%
- ALPHA_UNCOND: participation 100%, active win 61%, mean5 +1.08%, excess -0.35%, CAGR +66.5%, MDD -10.0%
- ALPHA_STATE_3PP: participation 100%, active win 63%, mean5 +1.13%, excess -0.30%, CAGR +71.3%, MDD -8.2%
### KOSDAQ
- MARKET: participation 100%, active win 62%, mean5 +0.51%, excess +0.00%, CAGR +25.1%, MDD -13.5%
- WPLUS: participation 100%, active win 62%, mean5 +1.05%, excess +0.54%, CAGR +59.7%, MDD -10.1%
- ABS_UNCOND: participation 100%, active win 62%, mean5 +1.03%, excess +0.51%, CAGR +57.3%, MDD -8.5%
- ABS_STATE_3PP: participation 100%, active win 62%, mean5 +1.03%, excess +0.51%, CAGR +57.3%, MDD -8.5%
- ALPHA_UNCOND: participation 100%, active win 62%, mean5 +1.03%, excess +0.51%, CAGR +57.3%, MDD -8.5%
- ALPHA_STATE_3PP: participation 100%, active win 62%, mean5 +1.03%, excess +0.51%, CAGR +57.3%, MDD -8.5%
### KOSDAQ_PLUS_KOSPI_EX_K200
- MARKET: participation 100%, active win 65%, mean5 +0.68%, excess +0.00%, CAGR +37.9%, MDD -10.9%
- WPLUS: participation 100%, active win 69%, mean5 +1.13%, excess +0.46%, CAGR +72.2%, MDD -7.6%
- ABS_UNCOND: participation 100%, active win 69%, mean5 +1.07%, excess +0.39%, CAGR +67.4%, MDD -7.5%
- ABS_STATE_3PP: participation 80%, active win 72%, mean5 +0.88%, excess +0.20%, CAGR +52.8%, MDD -5.7%
- ALPHA_UNCOND: participation 100%, active win 71%, mean5 +1.17%, excess +0.49%, CAGR +75.0%, MDD -10.7%
- ALPHA_STATE_3PP: participation 100%, active win 67%, mean5 +1.01%, excess +0.33%, CAGR +62.2%, MDD -9.2%
### KOSPI_ALL
- MARKET: participation 100%, active win 65%, mean5 +1.36%, excess +0.00%, CAGR +91.7%, MDD -8.6%
- WPLUS: participation 100%, active win 65%, mean5 +0.97%, excess -0.40%, CAGR +58.5%, MDD -7.5%
- ABS_UNCOND: participation 100%, active win 65%, mean5 +1.07%, excess -0.29%, CAGR +67.0%, MDD -7.8%
- ABS_STATE_3PP: participation 76%, active win 68%, mean5 +0.82%, excess -0.54%, CAGR +48.1%, MDD -7.3%
- ALPHA_UNCOND: participation 100%, active win 65%, mean5 +0.97%, excess -0.40%, CAGR +58.5%, MDD -7.5%
- ALPHA_STATE_3PP: participation 100%, active win 63%, mean5 +0.88%, excess -0.48%, CAGR +51.8%, MDD -9.3%
### KOSPI_EX_K200
- MARKET: participation 100%, active win 59%, mean5 +0.60%, excess +0.00%, CAGR +32.6%, MDD -8.1%
- WPLUS: participation 100%, active win 61%, mean5 +0.77%, excess +0.18%, CAGR +44.4%, MDD -5.8%
- ABS_UNCOND: participation 100%, active win 61%, mean5 +0.77%, excess +0.18%, CAGR +44.4%, MDD -5.8%
- ABS_STATE_3PP: participation 86%, active win 62%, mean5 +0.60%, excess +0.00%, CAGR +32.6%, MDD -5.8%
- ALPHA_UNCOND: participation 100%, active win 59%, mean5 +0.83%, excess +0.24%, CAGR +48.6%, MDD -6.4%
- ALPHA_STATE_3PP: participation 100%, active win 59%, mean5 +0.85%, excess +0.26%, CAGR +50.1%, MDD -6.7%
### KOSPI_KOSDAQ_ALL
- MARKET: participation 100%, active win 67%, mean5 +1.27%, excess +0.00%, CAGR +83.6%, MDD -9.1%
- WPLUS: participation 100%, active win 67%, mean5 +1.02%, excess -0.25%, CAGR +62.8%, MDD -8.0%
- ABS_UNCOND: participation 100%, active win 71%, mean5 +1.08%, excess -0.19%, CAGR +67.6%, MDD -11.1%
- ABS_STATE_3PP: participation 53%, active win 73%, mean5 +0.68%, excess -0.59%, CAGR +38.8%, MDD -6.4%
- ALPHA_UNCOND: participation 100%, active win 71%, mean5 +1.08%, excess -0.19%, CAGR +67.6%, MDD -11.1%
- ALPHA_STATE_3PP: participation 100%, active win 71%, mean5 +1.11%, excess -0.16%, CAGR +69.9%, MDD -11.1%

## TRAIN-frozen unconditional actions

- K200 ABS_UNCOND: MARKET
- K200 ALPHA_UNCOND: LEADER
- KOSDAQ ABS_UNCOND: LEADER_OR_ROTATE
- KOSDAQ ALPHA_UNCOND: LEADER_OR_ROTATE
- KOSDAQ_PLUS_KOSPI_EX_K200 ABS_UNCOND: POSABS
- KOSDAQ_PLUS_KOSPI_EX_K200 ALPHA_UNCOND: LEADER_OR_ROTATE
- KOSPI_ALL ABS_UNCOND: POSABS
- KOSPI_ALL ALPHA_UNCOND: WPLUS
- KOSPI_EX_K200 ABS_UNCOND: WPLUS
- KOSPI_EX_K200 ALPHA_UNCOND: POSABS
- KOSPI_KOSDAQ_ALL ABS_UNCOND: LEADER_OR_ROTATE
- KOSPI_KOSDAQ_ALL ALPHA_UNCOND: LEADER_OR_ROTATE

## Decision criterion

- Regime conditioning earns promotion only where a regularized state policy improves 2023-2024 versus its unconditional control and does not catastrophically reverse in 2025.
- WPLUS and EW4 remain important simple controls: a complicated regime policy is not useful if it cannot beat them.
- Exact constituent turnover is still unavailable; net10/net30 are blunt every-rebalance stresses, not implementation-grade costs.

