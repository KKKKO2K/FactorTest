# Regime-Conditioned Investment Action Research

Goal: identify what to hold, not merely name the regime. State definitions are contemporaneous and fixed before future returns are attached.
Weekly/non-overlap-style 5D forward returns are used for executable policy backtests; 20D is descriptive only. Policies are selected on 2016-2022 and frozen for 2023 onward.

## Policy definitions

- ABS_STATE: within each BASE x factor-health state, choose the TRAIN action with the highest positive-5D probability; go to cash if TRAIN win rate <=50% or mean <=0.
- ALPHA_STATE: within each state, choose the TRAIN factor action with the highest probability of beating the same-universe market.
- ABS_UNCOND / ALPHA_UNCOND: same selection without regime conditioning; these are the key controls.
- Dynamic actions: MARKET, equal-weight four family top portfolios (EW4), W+ family basket, positive-absolute family basket, current leader, and leader-or-rotate when leader is R- and an alternative W+ exists.

## 2023-2024 frozen-policy results

### K200
- MARKET: win 56%, mean5 +0.07%, beat-mkt 0%, excess +0.00%, CAGR +2.1%, MDD -18.5%
- EW4: win 53%, mean5 +0.18%, beat-mkt 49%, excess +0.11%, CAGR +8.1%, MDD -11.4%
- WPLUS: win 53%, mean5 +0.26%, beat-mkt 46%, excess +0.19%, CAGR +12.0%, MDD -12.4%
- LEADER: win 49%, mean5 +0.14%, beat-mkt 47%, excess +0.07%, CAGR +5.2%, MDD -17.3%
- LEADER_OR_ROTATE: win 49%, mean5 +0.14%, beat-mkt 47%, excess +0.08%, CAGR +5.7%, MDD -17.3%
- ABS_UNCOND: win 53%, mean5 +0.18%, beat-mkt 49%, excess +0.11%, CAGR +8.1%, MDD -11.4%
- ABS_STATE: win 15%, mean5 -0.01%, beat-mkt 44%, excess -0.08%, CAGR -0.6%, MDD -12.3%
- ALPHA_UNCOND: win 49%, mean5 +0.14%, beat-mkt 47%, excess +0.07%, CAGR +5.2%, MDD -17.3%
- ALPHA_STATE: win 52%, mean5 +0.20%, beat-mkt 49%, excess +0.13%, CAGR +8.7%, MDD -16.6%
### KOSDAQ
- MARKET: win 55%, mean5 +0.03%, beat-mkt 0%, excess +0.00%, CAGR -0.6%, MDD -28.3%
- EW4: win 59%, mean5 +0.16%, beat-mkt 53%, excess +0.13%, CAGR +4.7%, MDD -24.4%
- WPLUS: win 58%, mean5 +0.16%, beat-mkt 55%, excess +0.13%, CAGR +4.3%, MDD -24.9%
- LEADER: win 52%, mean5 -0.02%, beat-mkt 48%, excess -0.05%, CAGR -3.1%, MDD -30.8%
- LEADER_OR_ROTATE: win 52%, mean5 -0.02%, beat-mkt 48%, excess -0.05%, CAGR -3.0%, MDD -30.7%
- ABS_UNCOND: win 52%, mean5 -0.02%, beat-mkt 48%, excess -0.05%, CAGR -3.0%, MDD -30.7%
- ABS_STATE: win 55%, mean5 -0.03%, beat-mkt 51%, excess -0.06%, CAGR -3.3%, MDD -30.9%
- ALPHA_UNCOND: win 52%, mean5 -0.02%, beat-mkt 48%, excess -0.05%, CAGR -3.1%, MDD -30.8%
- ALPHA_STATE: win 56%, mean5 +0.05%, beat-mkt 53%, excess +0.02%, CAGR -0.1%, MDD -27.0%
### KOSDAQ_PLUS_KOSPI_EX_K200
- MARKET: win 53%, mean5 +0.04%, beat-mkt 0%, excess +0.00%, CAGR -0.4%, MDD -30.6%
- EW4: win 54%, mean5 +0.14%, beat-mkt 55%, excess +0.10%, CAGR +5.0%, MDD -28.5%
- WPLUS: win 56%, mean5 +0.10%, beat-mkt 53%, excess +0.06%, CAGR +2.7%, MDD -31.2%
- LEADER: win 55%, mean5 +0.03%, beat-mkt 51%, excess -0.01%, CAGR -1.0%, MDD -33.7%
- LEADER_OR_ROTATE: win 55%, mean5 +0.03%, beat-mkt 51%, excess -0.01%, CAGR -0.9%, MDD -33.6%
- ABS_UNCOND: win 53%, mean5 +0.11%, beat-mkt 56%, excess +0.07%, CAGR +3.3%, MDD -28.7%
- ABS_STATE: win 30%, mean5 +0.19%, beat-mkt 51%, excess +0.15%, CAGR +8.8%, MDD -9.4%
- ALPHA_UNCOND: win 55%, mean5 +0.03%, beat-mkt 51%, excess -0.01%, CAGR -0.9%, MDD -33.6%
- ALPHA_STATE: win 55%, mean5 -0.00%, beat-mkt 52%, excess -0.04%, CAGR -2.1%, MDD -32.6%
### KOSPI_ALL
- MARKET: win 55%, mean5 +0.08%, beat-mkt 0%, excess +0.00%, CAGR +2.5%, MDD -18.4%
- EW4: win 57%, mean5 +0.20%, beat-mkt 57%, excess +0.12%, CAGR +9.0%, MDD -13.7%
- WPLUS: win 57%, mean5 +0.29%, beat-mkt 60%, excess +0.21%, CAGR +13.4%, MDD -15.5%
- LEADER: win 55%, mean5 +0.19%, beat-mkt 55%, excess +0.12%, CAGR +8.4%, MDD -16.0%
- LEADER_OR_ROTATE: win 56%, mean5 +0.19%, beat-mkt 56%, excess +0.11%, CAGR +7.9%, MDD -16.0%
- ABS_UNCOND: win 57%, mean5 +0.28%, beat-mkt 57%, excess +0.21%, CAGR +13.3%, MDD -15.0%
- ABS_STATE: win 26%, mean5 -0.04%, beat-mkt 48%, excess -0.12%, CAGR -2.5%, MDD -12.8%
- ALPHA_UNCOND: win 57%, mean5 +0.29%, beat-mkt 60%, excess +0.21%, CAGR +13.4%, MDD -15.5%
- ALPHA_STATE: win 55%, mean5 +0.19%, beat-mkt 60%, excess +0.11%, CAGR +8.0%, MDD -15.9%
### KOSPI_EX_K200
- MARKET: win 53%, mean5 +0.05%, beat-mkt 0%, excess +0.00%, CAGR +1.2%, MDD -17.7%
- EW4: win 54%, mean5 +0.14%, beat-mkt 58%, excess +0.09%, CAGR +5.4%, MDD -16.7%
- WPLUS: win 56%, mean5 +0.19%, beat-mkt 58%, excess +0.14%, CAGR +7.6%, MDD -20.0%
- LEADER: win 54%, mean5 +0.15%, beat-mkt 53%, excess +0.10%, CAGR +5.5%, MDD -22.6%
- LEADER_OR_ROTATE: win 54%, mean5 +0.19%, beat-mkt 54%, excess +0.13%, CAGR +7.2%, MDD -20.3%
- ABS_UNCOND: win 56%, mean5 +0.19%, beat-mkt 58%, excess +0.14%, CAGR +7.6%, MDD -20.0%
- ABS_STATE: win 37%, mean5 +0.10%, beat-mkt 55%, excess +0.05%, CAGR +3.8%, MDD -14.6%
- ALPHA_UNCOND: win 54%, mean5 +0.14%, beat-mkt 58%, excess +0.09%, CAGR +5.4%, MDD -16.7%
- ALPHA_STATE: win 53%, mean5 +0.07%, beat-mkt 57%, excess +0.02%, CAGR +1.6%, MDD -21.6%
### KOSPI_KOSDAQ_ALL
- MARKET: win 52%, mean5 +0.01%, beat-mkt 0%, excess +0.00%, CAGR -0.7%, MDD -23.9%
- EW4: win 55%, mean5 +0.16%, beat-mkt 57%, excess +0.14%, CAGR +6.3%, MDD -23.6%
- WPLUS: win 52%, mean5 +0.06%, beat-mkt 55%, excess +0.05%, CAGR +1.3%, MDD -25.7%
- LEADER: win 47%, mean5 -0.02%, beat-mkt 45%, excess -0.04%, CAGR -3.0%, MDD -30.1%
- LEADER_OR_ROTATE: win 47%, mean5 +0.02%, beat-mkt 49%, excess +0.01%, CAGR -0.7%, MDD -26.8%
- ABS_UNCOND: win 52%, mean5 +0.01%, beat-mkt 0%, excess +0.00%, CAGR -0.7%, MDD -23.9%
- ABS_STATE: win 27%, mean5 +0.08%, beat-mkt 53%, excess +0.06%, CAGR +2.9%, MDD -12.5%
- ALPHA_UNCOND: win 47%, mean5 +0.02%, beat-mkt 49%, excess +0.01%, CAGR -0.7%, MDD -26.8%
- ALPHA_STATE: win 47%, mean5 +0.02%, beat-mkt 49%, excess +0.00%, CAGR -1.0%, MDD -29.6%

## 2025 stress

### K200
- MARKET: win 71%, mean5 +1.42%, beat-mkt 0%, excess +0.00%, CAGR +97.4%, MDD -8.6%
- ABS_UNCOND: win 63%, mean5 +1.19%, beat-mkt 53%, excess -0.24%, CAGR +76.2%, MDD -8.4%
- ABS_STATE: win 35%, mean5 +0.78%, beat-mkt 45%, excess -0.64%, CAGR +45.2%, MDD -7.2%
- ALPHA_UNCOND: win 61%, mean5 +1.08%, beat-mkt 43%, excess -0.35%, CAGR +66.5%, MDD -10.0%
- ALPHA_STATE: win 63%, mean5 +1.13%, beat-mkt 51%, excess -0.29%, CAGR +71.5%, MDD -8.3%
### KOSDAQ
- MARKET: win 62%, mean5 +0.51%, beat-mkt 0%, excess +0.00%, CAGR +25.1%, MDD -13.5%
- ABS_UNCOND: win 62%, mean5 +1.03%, beat-mkt 58%, excess +0.51%, CAGR +57.3%, MDD -8.5%
- ABS_STATE: win 64%, mean5 +1.08%, beat-mkt 62%, excess +0.57%, CAGR +61.8%, MDD -8.3%
- ALPHA_UNCOND: win 62%, mean5 +1.03%, beat-mkt 58%, excess +0.51%, CAGR +57.3%, MDD -8.5%
- ALPHA_STATE: win 64%, mean5 +1.12%, beat-mkt 58%, excess +0.61%, CAGR +64.5%, MDD -10.3%
### KOSDAQ_PLUS_KOSPI_EX_K200
- MARKET: win 65%, mean5 +0.68%, beat-mkt 0%, excess +0.00%, CAGR +37.9%, MDD -10.9%
- ABS_UNCOND: win 69%, mean5 +1.07%, beat-mkt 65%, excess +0.39%, CAGR +67.4%, MDD -7.5%
- ABS_STATE: win 57%, mean5 +0.91%, beat-mkt 63%, excess +0.23%, CAGR +54.9%, MDD -5.8%
- ALPHA_UNCOND: win 71%, mean5 +1.17%, beat-mkt 73%, excess +0.49%, CAGR +75.0%, MDD -10.7%
- ALPHA_STATE: win 67%, mean5 +1.01%, beat-mkt 69%, excess +0.33%, CAGR +62.2%, MDD -9.2%
### KOSPI_ALL
- MARKET: win 65%, mean5 +1.36%, beat-mkt 0%, excess +0.00%, CAGR +91.7%, MDD -8.6%
- ABS_UNCOND: win 65%, mean5 +1.07%, beat-mkt 51%, excess -0.29%, CAGR +67.0%, MDD -7.8%
- ABS_STATE: win 51%, mean5 +0.78%, beat-mkt 41%, excess -0.58%, CAGR +45.4%, MDD -6.8%
- ALPHA_UNCOND: win 65%, mean5 +0.97%, beat-mkt 47%, excess -0.40%, CAGR +58.5%, MDD -7.5%
- ALPHA_STATE: win 63%, mean5 +0.89%, beat-mkt 45%, excess -0.47%, CAGR +52.9%, MDD -10.1%
### KOSPI_EX_K200
- MARKET: win 59%, mean5 +0.60%, beat-mkt 0%, excess +0.00%, CAGR +32.6%, MDD -8.1%
- ABS_UNCOND: win 61%, mean5 +0.77%, beat-mkt 55%, excess +0.18%, CAGR +44.4%, MDD -5.8%
- ABS_STATE: win 57%, mean5 +0.69%, beat-mkt 53%, excess +0.09%, CAGR +38.6%, MDD -6.7%
- ALPHA_UNCOND: win 59%, mean5 +0.78%, beat-mkt 61%, excess +0.18%, CAGR +44.7%, MDD -8.5%
- ALPHA_STATE: win 59%, mean5 +0.74%, beat-mkt 59%, excess +0.14%, CAGR +41.5%, MDD -10.8%
### KOSPI_KOSDAQ_ALL
- MARKET: win 67%, mean5 +1.27%, beat-mkt 0%, excess +0.00%, CAGR +83.6%, MDD -9.1%
- ABS_UNCOND: win 67%, mean5 +1.27%, beat-mkt 0%, excess +0.00%, CAGR +83.6%, MDD -9.1%
- ABS_STATE: win 39%, mean5 +0.68%, beat-mkt 39%, excess -0.59%, CAGR +38.8%, MDD -6.4%
- ALPHA_UNCOND: win 71%, mean5 +1.08%, beat-mkt 51%, excess -0.19%, CAGR +67.6%, MDD -11.1%
- ALPHA_STATE: win 69%, mean5 +1.01%, beat-mkt 49%, excess -0.26%, CAGR +62.3%, MDD -11.2%

## Frozen state -> action map

### K200
- B2|F_HIGH ABS_STATE: LEADER
- B2|F_HIGH ALPHA_STATE: WPLUS
- B2|F_LOW ABS_STATE: CASH
- B2|F_LOW ALPHA_STATE: LEADER
- B3|F_HIGH ABS_STATE: CASH
- B3|F_HIGH ALPHA_STATE: LEADER
- B3|F_LOW ABS_STATE: CASH
- B3|F_LOW ALPHA_STATE: EW4
- B4|F_HIGH ABS_STATE: EW4
- B4|F_HIGH ALPHA_STATE: EW4
- B4|F_LOW ABS_STATE: WPLUS
- B4|F_LOW ALPHA_STATE: POSABS
### KOSDAQ
- B3|F_HIGH ABS_STATE: LEADER_OR_ROTATE
- B3|F_HIGH ALPHA_STATE: POSABS
- B3|F_LOW ABS_STATE: LEADER_OR_ROTATE
- B3|F_LOW ALPHA_STATE: LEADER_OR_ROTATE
- B4|F_HIGH ABS_STATE: LEADER
- B4|F_HIGH ALPHA_STATE: LEADER
- B4|F_LOW ABS_STATE: POSABS
- B4|F_LOW ALPHA_STATE: WPLUS
### KOSDAQ_PLUS_KOSPI_EX_K200
- B2|F_HIGH ABS_STATE: POSABS
- B2|F_HIGH ALPHA_STATE: LEADER_OR_ROTATE
- B2|F_LOW ABS_STATE: CASH
- B2|F_LOW ALPHA_STATE: LEADER
- B3|F_HIGH ABS_STATE: WPLUS
- B3|F_HIGH ALPHA_STATE: POSABS
- B3|F_LOW ABS_STATE: CASH
- B3|F_LOW ALPHA_STATE: POSABS
- B4|F_HIGH ABS_STATE: POSABS
- B4|F_HIGH ALPHA_STATE: LEADER
- B4|F_LOW ABS_STATE: LEADER
- B4|F_LOW ALPHA_STATE: LEADER
### KOSPI_ALL
- B2|F_HIGH ABS_STATE: POSABS
- B2|F_HIGH ALPHA_STATE: WPLUS
- B2|F_LOW ABS_STATE: CASH
- B2|F_LOW ALPHA_STATE: EW4
- B3|F_HIGH ABS_STATE: POSABS
- B3|F_HIGH ALPHA_STATE: LEADER_OR_ROTATE
- B3|F_LOW ABS_STATE: CASH
- B3|F_LOW ALPHA_STATE: EW4
- B4|F_HIGH ABS_STATE: WPLUS
- B4|F_HIGH ALPHA_STATE: LEADER
- B4|F_LOW ABS_STATE: LEADER
- B4|F_LOW ALPHA_STATE: LEADER
### KOSPI_EX_K200
- B2|F_HIGH ABS_STATE: CASH
- B2|F_HIGH ALPHA_STATE: EW4
- B2|F_LOW ABS_STATE: CASH
- B2|F_LOW ALPHA_STATE: LEADER_OR_ROTATE
- B3|F_HIGH ABS_STATE: LEADER_OR_ROTATE
- B3|F_HIGH ALPHA_STATE: LEADER_OR_ROTATE
- B3|F_LOW ABS_STATE: WPLUS
- B3|F_LOW ALPHA_STATE: POSABS
- B4|F_HIGH ABS_STATE: WPLUS
- B4|F_HIGH ALPHA_STATE: WPLUS
- B4|F_LOW ABS_STATE: LEADER_OR_ROTATE
- B4|F_LOW ALPHA_STATE: EW4
### KOSPI_KOSDAQ_ALL
- B2|F_HIGH ABS_STATE: EW4
- B2|F_HIGH ALPHA_STATE: EW4
- B2|F_LOW ABS_STATE: CASH
- B2|F_LOW ALPHA_STATE: LEADER
- B3|F_HIGH ABS_STATE: LEADER_OR_ROTATE
- B3|F_HIGH ALPHA_STATE: LEADER_OR_ROTATE
- B3|F_LOW ABS_STATE: CASH
- B3|F_LOW ALPHA_STATE: WPLUS
- B4|F_HIGH ABS_STATE: CASH
- B4|F_HIGH ALPHA_STATE: LEADER
- B4|F_LOW ABS_STATE: WPLUS
- B4|F_LOW ALPHA_STATE: LEADER

## Guardrails

- Gross factor-family top-portfolio returns do not contain exact constituent-level implementation costs. net10/net30 outputs subtract 10/30bp every active 5D rebalance as blunt stress tests, not precise cost estimates.
- Choosing among several actions within a state creates model-selection risk. The decisive comparison is state-conditioned policy vs its unconditional counterpart in 2023-2024 and 2025, not the best individual cell.
- 20D observations overlap and are descriptive. Policy performance is evaluated on 5D forward blocks.
- 2023+ has informed the broader research design, so it is post-discovery validation rather than pristine OOS.

