# Continuous Factor Payoff-Surface Research

Primary question: given only information observable at date t, which investable action has the better conditional payoff? Hard B2/B3/B4 and F_HIGH/F_LOW labels are excluded from predictors. Q33 family states are retained only to construct the W+ control basket.

## Data / design

- Panel rows: 2,805; date range 2016-04-01 to 2026-07-06.
- Actions: W+, EW4, market, Momentum, Revision, Value, Flow family top portfolios.
- Models: MARKET_ONLY, FACTOR_ONLY, FULL. Each universe is estimated separately with expanding yearly walk-forward. Ridge penalty is selected using the tail 25% of the then-available training history only.
- Objective for action models: predict each action minus W+ next-5D payoff. W+ remains the fallback unless predicted incremental payoff is positive.

## Walk-forward policy performance by historical sample

### K200 — BULL_2025
- FACTOR_ONLY: n=49, switch 90%, mean5 +1.03%, win 69%, edge vs W+ -0.06%, beat W+ 41%, MDD -10.3% (W+ -8.2%)
- FULL: n=49, switch 84%, mean5 +1.13%, win 71%, edge vs W+ +0.04%, beat W+ 41%, MDD -10.3% (W+ -8.2%)
- MARKET_ONLY: n=49, switch 69%, mean5 +1.08%, win 61%, edge vs W+ -0.00%, beat W+ 29%, MDD -8.6% (W+ -8.2%)
### K200 — DISCOVERY_2016_2022
- FACTOR_ONLY: n=144, switch 97%, mean5 +0.30%, win 56%, edge vs W+ +0.17%, beat W+ 51%, MDD -27.5% (W+ -31.5%)
- FULL: n=144, switch 97%, mean5 +0.06%, win 51%, edge vs W+ -0.07%, beat W+ 47%, MDD -30.4% (W+ -31.5%)
- MARKET_ONLY: n=144, switch 97%, mean5 +0.01%, win 51%, edge vs W+ -0.12%, beat W+ 42%, MDD -34.8% (W+ -31.5%)
### K200 — NORMAL_2023_2024
- FACTOR_ONLY: n=97, switch 91%, mean5 +0.14%, win 56%, edge vs W+ -0.13%, beat W+ 42%, MDD -15.7% (W+ -12.4%)
- FULL: n=97, switch 89%, mean5 +0.16%, win 56%, edge vs W+ -0.11%, beat W+ 39%, MDD -16.2% (W+ -12.4%)
- MARKET_ONLY: n=97, switch 95%, mean5 +0.24%, win 56%, edge vs W+ -0.02%, beat W+ 46%, MDD -13.1% (W+ -12.4%)
### K200 — YTD_2026
- FACTOR_ONLY: n=20, switch 95%, mean5 +1.50%, win 60%, edge vs W+ +0.86%, beat W+ 65%, MDD -17.1% (W+ -28.4%)
- FULL: n=20, switch 90%, mean5 +1.25%, win 70%, edge vs W+ +0.62%, beat W+ 55%, MDD -18.5% (W+ -28.4%)
- MARKET_ONLY: n=20, switch 100%, mean5 +1.04%, win 60%, edge vs W+ +0.41%, beat W+ 50%, MDD -24.6% (W+ -28.4%)
### KOSDAQ — BULL_2025
- FACTOR_ONLY: n=45, switch 71%, mean5 +1.02%, win 67%, edge vs W+ -0.03%, beat W+ 44%, MDD -10.1% (W+ -10.1%)
- FULL: n=45, switch 62%, mean5 +1.04%, win 64%, edge vs W+ -0.02%, beat W+ 36%, MDD -8.1% (W+ -10.1%)
- MARKET_ONLY: n=45, switch 64%, mean5 +1.14%, win 69%, edge vs W+ +0.09%, beat W+ 29%, MDD -12.5% (W+ -10.1%)
### KOSDAQ — DISCOVERY_2016_2022
- FACTOR_ONLY: n=113, switch 97%, mean5 +0.05%, win 57%, edge vs W+ +0.00%, beat W+ 42%, MDD -36.4% (W+ -39.4%)
- FULL: n=113, switch 93%, mean5 -0.13%, win 54%, edge vs W+ -0.18%, beat W+ 33%, MDD -41.9% (W+ -39.4%)
- MARKET_ONLY: n=113, switch 96%, mean5 -0.02%, win 56%, edge vs W+ -0.08%, beat W+ 43%, MDD -42.0% (W+ -39.4%)
### KOSDAQ — NORMAL_2023_2024
- FACTOR_ONLY: n=73, switch 92%, mean5 +0.23%, win 59%, edge vs W+ +0.07%, beat W+ 38%, MDD -22.6% (W+ -24.9%)
- FULL: n=73, switch 92%, mean5 +0.34%, win 63%, edge vs W+ +0.17%, beat W+ 42%, MDD -22.3% (W+ -24.9%)
- MARKET_ONLY: n=73, switch 93%, mean5 -0.05%, win 59%, edge vs W+ -0.21%, beat W+ 40%, MDD -24.0% (W+ -24.9%)
### KOSDAQ — YTD_2026
- FACTOR_ONLY: n=13, switch 77%, mean5 +1.34%, win 54%, edge vs W+ -0.90%, beat W+ 23%, MDD -7.0% (W+ -6.8%)
- FULL: n=13, switch 77%, mean5 +1.56%, win 54%, edge vs W+ -0.67%, beat W+ 23%, MDD -7.0% (W+ -6.8%)
- MARKET_ONLY: n=13, switch 100%, mean5 +2.14%, win 46%, edge vs W+ -0.09%, beat W+ 54%, MDD -7.6% (W+ -6.8%)
### KOSDAQ_PLUS_KOSPI_EX_K200 — BULL_2025
- FACTOR_ONLY: n=49, switch 90%, mean5 +0.97%, win 67%, edge vs W+ -0.16%, beat W+ 33%, MDD -13.3% (W+ -7.6%)
- FULL: n=49, switch 82%, mean5 +1.00%, win 69%, edge vs W+ -0.14%, beat W+ 33%, MDD -12.2% (W+ -7.6%)
- MARKET_ONLY: n=49, switch 78%, mean5 +1.25%, win 73%, edge vs W+ +0.12%, beat W+ 43%, MDD -11.1% (W+ -7.6%)
### KOSDAQ_PLUS_KOSPI_EX_K200 — DISCOVERY_2016_2022
- FACTOR_ONLY: n=144, switch 94%, mean5 +0.16%, win 60%, edge vs W+ +0.02%, beat W+ 44%, MDD -37.2% (W+ -37.1%)
- FULL: n=144, switch 88%, mean5 +0.10%, win 60%, edge vs W+ -0.04%, beat W+ 39%, MDD -39.3% (W+ -37.1%)
- MARKET_ONLY: n=144, switch 94%, mean5 +0.12%, win 60%, edge vs W+ -0.01%, beat W+ 47%, MDD -37.7% (W+ -37.1%)
### KOSDAQ_PLUS_KOSPI_EX_K200 — NORMAL_2023_2024
- FACTOR_ONLY: n=96, switch 96%, mean5 +0.09%, win 52%, edge vs W+ -0.01%, beat W+ 46%, MDD -34.0% (W+ -31.2%)
- FULL: n=96, switch 84%, mean5 +0.10%, win 54%, edge vs W+ +0.00%, beat W+ 41%, MDD -32.8% (W+ -31.2%)
- MARKET_ONLY: n=96, switch 84%, mean5 +0.32%, win 57%, edge vs W+ +0.22%, beat W+ 50%, MDD -28.5% (W+ -31.2%)
### KOSDAQ_PLUS_KOSPI_EX_K200 — YTD_2026
- FACTOR_ONLY: n=19, switch 100%, mean5 +0.73%, win 63%, edge vs W+ -0.16%, beat W+ 47%, MDD -24.2% (W+ -23.5%)
- FULL: n=19, switch 100%, mean5 -0.19%, win 53%, edge vs W+ -1.08%, beat W+ 32%, MDD -29.0% (W+ -23.5%)
- MARKET_ONLY: n=19, switch 53%, mean5 +0.74%, win 58%, edge vs W+ -0.15%, beat W+ 32%, MDD -23.4% (W+ -23.5%)
### KOSPI_ALL — BULL_2025
- FACTOR_ONLY: n=49, switch 84%, mean5 +1.10%, win 71%, edge vs W+ +0.14%, beat W+ 49%, MDD -7.2% (W+ -7.5%)
- FULL: n=49, switch 84%, mean5 +1.24%, win 71%, edge vs W+ +0.27%, beat W+ 51%, MDD -7.9% (W+ -7.5%)
- MARKET_ONLY: n=49, switch 61%, mean5 +1.12%, win 65%, edge vs W+ +0.15%, beat W+ 33%, MDD -7.3% (W+ -7.5%)
### KOSPI_ALL — DISCOVERY_2016_2022
- FACTOR_ONLY: n=144, switch 97%, mean5 +0.23%, win 51%, edge vs W+ +0.05%, beat W+ 48%, MDD -32.4% (W+ -31.8%)
- FULL: n=144, switch 94%, mean5 +0.15%, win 51%, edge vs W+ -0.03%, beat W+ 46%, MDD -29.5% (W+ -31.8%)
- MARKET_ONLY: n=144, switch 97%, mean5 +0.20%, win 53%, edge vs W+ +0.02%, beat W+ 47%, MDD -29.5% (W+ -31.8%)
### KOSPI_ALL — NORMAL_2023_2024
- FACTOR_ONLY: n=97, switch 89%, mean5 +0.07%, win 54%, edge vs W+ -0.22%, beat W+ 30%, MDD -15.8% (W+ -15.5%)
- FULL: n=97, switch 89%, mean5 +0.06%, win 53%, edge vs W+ -0.23%, beat W+ 29%, MDD -17.2% (W+ -15.5%)
- MARKET_ONLY: n=97, switch 91%, mean5 +0.34%, win 60%, edge vs W+ +0.05%, beat W+ 41%, MDD -11.1% (W+ -15.5%)
### KOSPI_ALL — YTD_2026
- FACTOR_ONLY: n=21, switch 95%, mean5 +1.42%, win 57%, edge vs W+ +0.36%, beat W+ 43%, MDD -19.6% (W+ -20.0%)
- FULL: n=21, switch 95%, mean5 +0.74%, win 57%, edge vs W+ -0.31%, beat W+ 43%, MDD -25.0% (W+ -20.0%)
- MARKET_ONLY: n=21, switch 95%, mean5 +1.17%, win 57%, edge vs W+ +0.11%, beat W+ 52%, MDD -19.9% (W+ -20.0%)
### KOSPI_EX_K200 — BULL_2025
- FACTOR_ONLY: n=49, switch 94%, mean5 +0.52%, win 59%, edge vs W+ -0.26%, beat W+ 33%, MDD -12.8% (W+ -5.8%)
- FULL: n=49, switch 88%, mean5 +0.54%, win 57%, edge vs W+ -0.24%, beat W+ 39%, MDD -12.7% (W+ -5.8%)
- MARKET_ONLY: n=49, switch 84%, mean5 +0.89%, win 63%, edge vs W+ +0.11%, beat W+ 47%, MDD -8.9% (W+ -5.8%)
### KOSPI_EX_K200 — DISCOVERY_2016_2022
- FACTOR_ONLY: n=117, switch 93%, mean5 +0.51%, win 56%, edge vs W+ +0.14%, beat W+ 48%, MDD -28.2% (W+ -27.3%)
- FULL: n=117, switch 91%, mean5 +0.54%, win 57%, edge vs W+ +0.16%, beat W+ 50%, MDD -23.5% (W+ -27.3%)
- MARKET_ONLY: n=117, switch 93%, mean5 +0.55%, win 58%, edge vs W+ +0.17%, beat W+ 50%, MDD -25.6% (W+ -27.3%)
### KOSPI_EX_K200 — NORMAL_2023_2024
- FACTOR_ONLY: n=91, switch 86%, mean5 -0.04%, win 49%, edge vs W+ -0.23%, beat W+ 29%, MDD -26.4% (W+ -20.0%)
- FULL: n=91, switch 91%, mean5 +0.04%, win 52%, edge vs W+ -0.15%, beat W+ 32%, MDD -21.9% (W+ -20.0%)
- MARKET_ONLY: n=91, switch 80%, mean5 +0.24%, win 54%, edge vs W+ +0.05%, beat W+ 32%, MDD -16.2% (W+ -20.0%)
### KOSPI_EX_K200 — YTD_2026
- FACTOR_ONLY: n=15, switch 100%, mean5 +1.56%, win 60%, edge vs W+ -0.06%, beat W+ 40%, MDD -12.2% (W+ -11.9%)
- FULL: n=15, switch 100%, mean5 +1.52%, win 60%, edge vs W+ -0.11%, beat W+ 33%, MDD -13.7% (W+ -11.9%)
- MARKET_ONLY: n=15, switch 100%, mean5 +1.72%, win 60%, edge vs W+ +0.09%, beat W+ 47%, MDD -12.3% (W+ -11.9%)
### KOSPI_KOSDAQ_ALL — BULL_2025
- FACTOR_ONLY: n=49, switch 80%, mean5 +1.03%, win 63%, edge vs W+ +0.01%, beat W+ 37%, MDD -11.6% (W+ -8.0%)
- FULL: n=49, switch 73%, mean5 +1.08%, win 63%, edge vs W+ +0.06%, beat W+ 39%, MDD -11.6% (W+ -8.0%)
- MARKET_ONLY: n=49, switch 65%, mean5 +1.18%, win 71%, edge vs W+ +0.16%, beat W+ 31%, MDD -9.6% (W+ -8.0%)
### KOSPI_KOSDAQ_ALL — DISCOVERY_2016_2022
- FACTOR_ONLY: n=144, switch 88%, mean5 -0.04%, win 54%, edge vs W+ -0.20%, beat W+ 35%, MDD -36.6% (W+ -36.2%)
- FULL: n=144, switch 89%, mean5 +0.03%, win 56%, edge vs W+ -0.13%, beat W+ 39%, MDD -32.5% (W+ -36.2%)
- MARKET_ONLY: n=144, switch 84%, mean5 +0.12%, win 56%, edge vs W+ -0.04%, beat W+ 40%, MDD -33.3% (W+ -36.2%)
### KOSPI_KOSDAQ_ALL — NORMAL_2023_2024
- FACTOR_ONLY: n=96, switch 83%, mean5 +0.06%, win 51%, edge vs W+ -0.00%, beat W+ 34%, MDD -24.7% (W+ -25.7%)
- FULL: n=96, switch 83%, mean5 -0.25%, win 51%, edge vs W+ -0.32%, beat W+ 29%, MDD -35.2% (W+ -25.7%)
- MARKET_ONLY: n=96, switch 89%, mean5 +0.18%, win 58%, edge vs W+ +0.12%, beat W+ 50%, MDD -23.1% (W+ -25.7%)
### KOSPI_KOSDAQ_ALL — YTD_2026
- FACTOR_ONLY: n=21, switch 95%, mean5 +1.84%, win 57%, edge vs W+ +1.22%, beat W+ 43%, MDD -19.6% (W+ -24.5%)
- FULL: n=21, switch 95%, mean5 +1.30%, win 57%, edge vs W+ +0.68%, beat W+ 43%, MDD -19.1% (W+ -24.5%)
- MARKET_ONLY: n=21, switch 95%, mean5 +1.00%, win 52%, edge vs W+ +0.38%, beat W+ 52%, MDD -25.6% (W+ -24.5%)

## Incremental factor information test

- 2020 FACTOR_ONLY: median rank IC +0.085; median predicted-top vs bottom realized spread +0.29%
- 2021 FACTOR_ONLY: median rank IC +0.055; median predicted-top vs bottom realized spread +0.05%
- 2022 FACTOR_ONLY: median rank IC -0.034; median predicted-top vs bottom realized spread -0.03%
- 2023 FACTOR_ONLY: median rank IC -0.098; median predicted-top vs bottom realized spread -0.14%
- 2024 FACTOR_ONLY: median rank IC -0.029; median predicted-top vs bottom realized spread -0.18%
- 2025 FACTOR_ONLY: median rank IC -0.004; median predicted-top vs bottom realized spread -0.10%
- 2026 FACTOR_ONLY: median rank IC +0.040; median predicted-top vs bottom realized spread +0.17%
- 2020 FULL: median rank IC +0.093; median predicted-top vs bottom realized spread +0.20%
- 2021 FULL: median rank IC +0.070; median predicted-top vs bottom realized spread +0.03%
- 2022 FULL: median rank IC -0.070; median predicted-top vs bottom realized spread -0.13%
- 2023 FULL: median rank IC -0.055; median predicted-top vs bottom realized spread -0.13%
- 2024 FULL: median rank IC -0.007; median predicted-top vs bottom realized spread -0.11%
- 2025 FULL: median rank IC -0.016; median predicted-top vs bottom realized spread -0.05%
- 2026 FULL: median rank IC -0.013; median predicted-top vs bottom realized spread -0.27%
- 2020 MARKET_ONLY: median rank IC +0.012; median predicted-top vs bottom realized spread +0.06%
- 2021 MARKET_ONLY: median rank IC +0.053; median predicted-top vs bottom realized spread -0.01%
- 2022 MARKET_ONLY: median rank IC -0.057; median predicted-top vs bottom realized spread -0.10%
- 2023 MARKET_ONLY: median rank IC -0.048; median predicted-top vs bottom realized spread -0.15%
- 2024 MARKET_ONLY: median rank IC +0.040; median predicted-top vs bottom realized spread +0.23%
- 2025 MARKET_ONLY: median rank IC -0.064; median predicted-top vs bottom realized spread -0.18%
- 2026 MARKET_ONLY: median rank IC +0.032; median predicted-top vs bottom realized spread +0.04%

## Strongest stable univariate payoff surfaces

- None passed same-sign DISCOVERY and 2023-24 screen.

## Interpretation guardrails

- 2023-2024 has already informed the broader research program, so it is historical validation rather than pristine untouched OOS.
- 2025 and 2026 are reported separately because their market regimes are exceptional and should not be pooled into a generic recent sample.
- A useful finding requires either incremental FULL/FACTOR_ONLY walk-forward value over MARKET_ONLY, or a simple payoff surface whose sign and economic size persist across samples.
- This stage intentionally does not create a new discrete regime taxonomy.

