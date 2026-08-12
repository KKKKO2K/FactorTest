# Binary Investment Decisions from Continuous Factor State

Low-dimensional tests only. No hard regime labels. W+ is intentionally excluded from these targets to avoid using a static Q33 definition inside early sequential training years.

Tasks: RISK = market vs cash; ALPHA = equal-weight four factor-family top portfolios (EW4) vs same-universe market. Models retrain once per year using only prior history.

## 5D historical walk-forward

### K200 — ALPHA — BULL_2025
- FACTOR_ONLY: mean +1.44%, win 73%, edge vs EW4 +0.25%, sign accuracy 59%, rank IC +0.01, MDD -10.7% (control -8.4%)
- FULL: mean +1.15%, win 65%, edge vs EW4 -0.04%, sign accuracy 45%, rank IC -0.14, MDD -10.7% (control -8.4%)
- MARKET_ONLY: mean +1.25%, win 63%, edge vs EW4 +0.06%, sign accuracy 55%, rank IC -0.07, MDD -6.9% (control -8.4%)
### K200 — ALPHA — DISCOVERY_2016_2022
- FACTOR_ONLY: mean +0.14%, win 53%, edge vs EW4 +0.05%, sign accuracy 53%, rank IC +0.17, MDD -27.5% (control -30.4%)
- FULL: mean +0.10%, win 54%, edge vs EW4 +0.01%, sign accuracy 52%, rank IC +0.10, MDD -28.7% (control -30.4%)
- MARKET_ONLY: mean -0.00%, win 53%, edge vs EW4 -0.09%, sign accuracy 51%, rank IC -0.03, MDD -33.8% (control -30.4%)
### K200 — ALPHA — NORMAL_2023_2024
- FACTOR_ONLY: mean +0.14%, win 54%, edge vs EW4 -0.04%, sign accuracy 47%, rank IC -0.06, MDD -13.0% (control -11.4%)
- FULL: mean +0.16%, win 55%, edge vs EW4 -0.02%, sign accuracy 52%, rank IC -0.02, MDD -13.0% (control -11.4%)
- MARKET_ONLY: mean +0.15%, win 58%, edge vs EW4 -0.03%, sign accuracy 45%, rank IC +0.10, MDD -13.8% (control -11.4%)
### K200 — ALPHA — YTD_2026
- FACTOR_ONLY: mean +0.81%, win 65%, edge vs EW4 +0.08%, sign accuracy 40%, rank IC -0.33, MDD -29.9% (control -26.1%)
- FULL: mean +0.32%, win 65%, edge vs EW4 -0.41%, sign accuracy 30%, rank IC -0.39, MDD -32.5% (control -26.1%)
- MARKET_ONLY: mean +0.56%, win 60%, edge vs EW4 -0.16%, sign accuracy 35%, rank IC -0.50, MDD -28.3% (control -26.1%)
### K200 — RISK — BULL_2025
- FACTOR_ONLY: mean +0.67%, win 43%, edge vs market -0.76%, sign accuracy 55%, rank IC -0.03, MDD -7.0% (control -8.6%)
- FULL: mean +0.76%, win 47%, edge vs market -0.67%, sign accuracy 59%, rank IC +0.01, MDD -6.6% (control -8.6%)
- MARKET_ONLY: mean +1.03%, win 53%, edge vs market -0.40%, sign accuracy 61%, rank IC +0.03, MDD -6.8% (control -8.6%)
### K200 — RISK — DISCOVERY_2016_2022
- FACTOR_ONLY: mean -0.31%, win 32%, edge vs market -0.31%, sign accuracy 43%, rank IC -0.16, MDD -40.2% (control -33.5%)
- FULL: mean -0.22%, win 28%, edge vs market -0.22%, sign accuracy 43%, rank IC -0.14, MDD -29.9% (control -33.5%)
- MARKET_ONLY: mean +0.08%, win 31%, edge vs market +0.08%, sign accuracy 49%, rank IC +0.03, MDD -24.5% (control -33.5%)
### K200 — RISK — NORMAL_2023_2024
- FACTOR_ONLY: mean -0.13%, win 26%, edge vs market -0.20%, sign accuracy 43%, rank IC -0.12, MDD -14.9% (control -18.5%)
- FULL: mean -0.15%, win 22%, edge vs market -0.21%, sign accuracy 41%, rank IC -0.12, MDD -16.5% (control -18.5%)
- MARKET_ONLY: mean +0.13%, win 26%, edge vs market +0.06%, sign accuracy 54%, rank IC -0.04, MDD -7.7% (control -18.5%)
### K200 — RISK — YTD_2026
- FACTOR_ONLY: mean +1.78%, win 60%, edge vs market +0.00%, sign accuracy 60%, rank IC +0.06, MDD -29.9% (control -29.9%)
- FULL: mean +1.78%, win 60%, edge vs market +0.00%, sign accuracy 60%, rank IC -0.16, MDD -29.9% (control -29.9%)
- MARKET_ONLY: mean +1.78%, win 60%, edge vs market +0.00%, sign accuracy 60%, rank IC -0.34, MDD -29.9% (control -29.9%)
### KOSDAQ — ALPHA — BULL_2025
- FACTOR_ONLY: mean +0.75%, win 69%, edge vs EW4 -0.23%, sign accuracy 58%, rank IC +0.01, MDD -10.7% (control -9.9%)
- FULL: mean +0.70%, win 69%, edge vs EW4 -0.28%, sign accuracy 53%, rank IC -0.07, MDD -10.7% (control -9.9%)
- MARKET_ONLY: mean +1.01%, win 71%, edge vs EW4 +0.03%, sign accuracy 69%, rank IC +0.04, MDD -9.9% (control -9.9%)
### KOSDAQ — ALPHA — DISCOVERY_2016_2022
- FACTOR_ONLY: mean -0.10%, win 58%, edge vs EW4 -0.11%, sign accuracy 51%, rank IC -0.09, MDD -40.7% (control -40.1%)
- FULL: mean -0.11%, win 58%, edge vs EW4 -0.11%, sign accuracy 52%, rank IC -0.10, MDD -40.9% (control -40.1%)
- MARKET_ONLY: mean -0.08%, win 58%, edge vs EW4 -0.08%, sign accuracy 52%, rank IC +0.04, MDD -40.9% (control -40.1%)
### KOSDAQ — ALPHA — NORMAL_2023_2024
- FACTOR_ONLY: mean +0.04%, win 56%, edge vs EW4 -0.12%, sign accuracy 41%, rank IC -0.15, MDD -26.5% (control -24.4%)
- FULL: mean -0.03%, win 56%, edge vs EW4 -0.18%, sign accuracy 37%, rank IC -0.15, MDD -28.1% (control -24.4%)
- MARKET_ONLY: mean +0.13%, win 58%, edge vs EW4 -0.03%, sign accuracy 51%, rank IC -0.01, MDD -24.4% (control -24.4%)
### KOSDAQ — ALPHA — YTD_2026
- FACTOR_ONLY: mean +1.58%, win 62%, edge vs EW4 -0.37%, sign accuracy 46%, rank IC -0.15, MDD -7.2% (control -6.8%)
- FULL: mean +1.58%, win 62%, edge vs EW4 -0.37%, sign accuracy 46%, rank IC -0.09, MDD -7.2% (control -6.8%)
- MARKET_ONLY: mean +1.54%, win 62%, edge vs EW4 -0.41%, sign accuracy 54%, rank IC -0.26, MDD -6.8% (control -6.8%)
### KOSDAQ — RISK — BULL_2025
- FACTOR_ONLY: mean +0.30%, win 24%, edge vs market -0.22%, sign accuracy 47%, rank IC -0.07, MDD -5.8% (control -13.5%)
- FULL: mean +0.33%, win 31%, edge vs market -0.18%, sign accuracy 49%, rank IC -0.04, MDD -7.4% (control -13.5%)
- MARKET_ONLY: mean +0.27%, win 36%, edge vs market -0.24%, sign accuracy 51%, rank IC -0.06, MDD -6.8% (control -13.5%)
### KOSDAQ — RISK — DISCOVERY_2016_2022
- FACTOR_ONLY: mean -0.08%, win 25%, edge vs market +0.11%, sign accuracy 48%, rank IC -0.11, MDD -30.0% (control -46.0%)
- FULL: mean -0.25%, win 28%, edge vs market -0.05%, sign accuracy 44%, rank IC -0.04, MDD -45.6% (control -46.0%)
- MARKET_ONLY: mean -0.11%, win 46%, edge vs market +0.08%, sign accuracy 55%, rank IC +0.02, MDD -39.5% (control -46.0%)
### KOSDAQ — RISK — NORMAL_2023_2024
- FACTOR_ONLY: mean -0.04%, win 23%, edge vs market -0.07%, sign accuracy 51%, rank IC +0.03, MDD -16.6% (control -28.3%)
- FULL: mean +0.09%, win 21%, edge vs market +0.06%, sign accuracy 51%, rank IC +0.08, MDD -12.8% (control -28.3%)
- MARKET_ONLY: mean +0.03%, win 25%, edge vs market -0.00%, sign accuracy 48%, rank IC +0.04, MDD -16.1% (control -28.3%)
### KOSDAQ — RISK — YTD_2026
- FACTOR_ONLY: mean -0.31%, win 15%, edge vs market -1.81%, sign accuracy 46%, rank IC -0.54, MDD -8.2% (control -9.0%)
- FULL: mean -0.02%, win 31%, edge vs market -1.52%, sign accuracy 38%, rank IC -0.08, MDD -8.4% (control -9.0%)
- MARKET_ONLY: mean +1.50%, win 46%, edge vs market +0.00%, sign accuracy 46%, rank IC +0.18, MDD -9.0% (control -9.0%)
### KOSDAQ_PLUS_KOSPI_EX_K200 — ALPHA — BULL_2025
- FACTOR_ONLY: mean +0.88%, win 67%, edge vs EW4 -0.08%, sign accuracy 53%, rank IC -0.17, MDD -10.0% (control -9.3%)
- FULL: mean +0.87%, win 69%, edge vs EW4 -0.09%, sign accuracy 53%, rank IC -0.10, MDD -10.0% (control -9.3%)
- MARKET_ONLY: mean +1.00%, win 69%, edge vs EW4 +0.04%, sign accuracy 67%, rank IC -0.06, MDD -8.5% (control -9.3%)
### KOSDAQ_PLUS_KOSPI_EX_K200 — ALPHA — DISCOVERY_2016_2022
- FACTOR_ONLY: mean +0.05%, win 60%, edge vs EW4 -0.03%, sign accuracy 57%, rank IC +0.05, MDD -35.9% (control -33.6%)
- FULL: mean +0.06%, win 59%, edge vs EW4 -0.02%, sign accuracy 56%, rank IC +0.03, MDD -37.1% (control -33.6%)
- MARKET_ONLY: mean +0.06%, win 59%, edge vs EW4 -0.01%, sign accuracy 58%, rank IC +0.07, MDD -35.3% (control -33.6%)
### KOSDAQ_PLUS_KOSPI_EX_K200 — ALPHA — NORMAL_2023_2024
- FACTOR_ONLY: mean +0.08%, win 56%, edge vs EW4 -0.06%, sign accuracy 45%, rank IC -0.08, MDD -30.1% (control -28.5%)
- FULL: mean +0.09%, win 56%, edge vs EW4 -0.05%, sign accuracy 46%, rank IC -0.04, MDD -29.3% (control -28.5%)
- MARKET_ONLY: mean +0.16%, win 55%, edge vs EW4 +0.02%, sign accuracy 58%, rank IC +0.13, MDD -27.5% (control -28.5%)
### KOSDAQ_PLUS_KOSPI_EX_K200 — ALPHA — YTD_2026
- FACTOR_ONLY: mean +0.95%, win 58%, edge vs EW4 +0.09%, sign accuracy 58%, rank IC +0.04, MDD -23.5% (control -22.4%)
- FULL: mean +0.73%, win 58%, edge vs EW4 -0.13%, sign accuracy 47%, rank IC -0.05, MDD -24.1% (control -22.4%)
- MARKET_ONLY: mean +0.80%, win 58%, edge vs EW4 -0.06%, sign accuracy 68%, rank IC +0.09, MDD -22.4% (control -22.4%)
### KOSDAQ_PLUS_KOSPI_EX_K200 — RISK — BULL_2025
- FACTOR_ONLY: mean +0.21%, win 18%, edge vs market -0.47%, sign accuracy 43%, rank IC -0.09, MDD -5.7% (control -10.9%)
- FULL: mean +0.06%, win 20%, edge vs market -0.62%, sign accuracy 39%, rank IC -0.14, MDD -6.3% (control -10.9%)
- MARKET_ONLY: mean +0.31%, win 29%, edge vs market -0.37%, sign accuracy 47%, rank IC -0.17, MDD -3.9% (control -10.9%)
### KOSDAQ_PLUS_KOSPI_EX_K200 — RISK — DISCOVERY_2016_2022
- FACTOR_ONLY: mean -0.24%, win 21%, edge vs market -0.18%, sign accuracy 40%, rank IC -0.13, MDD -34.5% (control -39.7%)
- FULL: mean -0.24%, win 25%, edge vs market -0.19%, sign accuracy 42%, rank IC -0.11, MDD -36.6% (control -39.7%)
- MARKET_ONLY: mean -0.20%, win 34%, edge vs market -0.15%, sign accuracy 52%, rank IC -0.01, MDD -39.4% (control -39.7%)
### KOSDAQ_PLUS_KOSPI_EX_K200 — RISK — NORMAL_2023_2024
- FACTOR_ONLY: mean +0.07%, win 26%, edge vs market +0.03%, sign accuracy 54%, rank IC +0.08, MDD -13.3% (control -30.6%)
- FULL: mean +0.15%, win 25%, edge vs market +0.12%, sign accuracy 56%, rank IC +0.09, MDD -13.6% (control -30.6%)
- MARKET_ONLY: mean +0.13%, win 19%, edge vs market +0.09%, sign accuracy 53%, rank IC +0.09, MDD -8.6% (control -30.6%)
### KOSDAQ_PLUS_KOSPI_EX_K200 — RISK — YTD_2026
- FACTOR_ONLY: mean +0.81%, win 26%, edge vs market +0.23%, sign accuracy 53%, rank IC -0.14, MDD -10.8% (control -23.3%)
- FULL: mean +1.47%, win 47%, edge vs market +0.89%, sign accuracy 58%, rank IC +0.29, MDD -10.8% (control -23.3%)
- MARKET_ONLY: mean +1.06%, win 42%, edge vs market +0.48%, sign accuracy 53%, rank IC +0.30, MDD -15.0% (control -23.3%)
### KOSPI_ALL — ALPHA — BULL_2025
- FACTOR_ONLY: mean +0.94%, win 63%, edge vs EW4 -0.07%, sign accuracy 43%, rank IC -0.16, MDD -9.4% (control -8.5%)
- FULL: mean +1.00%, win 65%, edge vs EW4 -0.01%, sign accuracy 47%, rank IC -0.16, MDD -8.3% (control -8.5%)
- MARKET_ONLY: mean +1.05%, win 65%, edge vs EW4 +0.04%, sign accuracy 49%, rank IC +0.00, MDD -8.2% (control -8.5%)
### KOSPI_ALL — ALPHA — DISCOVERY_2016_2022
- FACTOR_ONLY: mean +0.18%, win 54%, edge vs EW4 +0.06%, sign accuracy 56%, rank IC +0.22, MDD -25.7% (control -30.3%)
- FULL: mean +0.08%, win 50%, edge vs EW4 -0.04%, sign accuracy 51%, rank IC +0.10, MDD -28.8% (control -30.3%)
- MARKET_ONLY: mean -0.00%, win 50%, edge vs EW4 -0.13%, sign accuracy 49%, rank IC -0.02, MDD -30.2% (control -30.3%)
### KOSPI_ALL — ALPHA — NORMAL_2023_2024
- FACTOR_ONLY: mean +0.07%, win 57%, edge vs EW4 -0.13%, sign accuracy 47%, rank IC -0.12, MDD -14.3% (control -13.7%)
- FULL: mean +0.08%, win 56%, edge vs EW4 -0.12%, sign accuracy 47%, rank IC -0.07, MDD -14.4% (control -13.7%)
- MARKET_ONLY: mean +0.24%, win 58%, edge vs EW4 +0.04%, sign accuracy 55%, rank IC +0.15, MDD -13.0% (control -13.7%)
### KOSPI_ALL — ALPHA — YTD_2026
- FACTOR_ONLY: mean +1.38%, win 62%, edge vs EW4 +0.55%, sign accuracy 33%, rank IC -0.19, MDD -25.4% (control -21.5%)
- FULL: mean +1.18%, win 67%, edge vs EW4 +0.35%, sign accuracy 33%, rank IC -0.30, MDD -25.4% (control -21.5%)
- MARKET_ONLY: mean +0.95%, win 62%, edge vs EW4 +0.12%, sign accuracy 43%, rank IC -0.25, MDD -21.9% (control -21.5%)
### KOSPI_ALL — RISK — BULL_2025
- FACTOR_ONLY: mean +0.81%, win 43%, edge vs market -0.55%, sign accuracy 49%, rank IC -0.12, MDD -10.4% (control -8.6%)
- FULL: mean +0.83%, win 41%, edge vs market -0.53%, sign accuracy 49%, rank IC -0.10, MDD -7.1% (control -8.6%)
- MARKET_ONLY: mean +1.12%, win 51%, edge vs market -0.24%, sign accuracy 57%, rank IC +0.02, MDD -6.2% (control -8.6%)
### KOSPI_ALL — RISK — DISCOVERY_2016_2022
- FACTOR_ONLY: mean -0.07%, win 26%, edge vs market -0.06%, sign accuracy 49%, rank IC -0.06, MDD -24.4% (control -34.4%)
- FULL: mean -0.20%, win 21%, edge vs market -0.19%, sign accuracy 46%, rank IC -0.10, MDD -31.9% (control -34.4%)
- MARKET_ONLY: mean +0.00%, win 29%, edge vs market +0.01%, sign accuracy 47%, rank IC +0.00, MDD -22.4% (control -34.4%)
### KOSPI_ALL — RISK — NORMAL_2023_2024
- FACTOR_ONLY: mean +0.05%, win 31%, edge vs market -0.02%, sign accuracy 51%, rank IC +0.01, MDD -12.2% (control -18.4%)
- FULL: mean +0.03%, win 28%, edge vs market -0.04%, sign accuracy 51%, rank IC -0.03, MDD -12.7% (control -18.4%)
- MARKET_ONLY: mean +0.12%, win 24%, edge vs market +0.04%, sign accuracy 53%, rank IC -0.07, MDD -9.3% (control -18.4%)
### KOSPI_ALL — RISK — YTD_2026
- FACTOR_ONLY: mean +1.44%, win 48%, edge vs market -0.83%, sign accuracy 52%, rank IC -0.19, MDD -25.4% (control -25.4%)
- FULL: mean +2.27%, win 62%, edge vs market +0.00%, sign accuracy 62%, rank IC -0.16, MDD -25.4% (control -25.4%)
- MARKET_ONLY: mean +2.27%, win 62%, edge vs market +0.00%, sign accuracy 62%, rank IC -0.11, MDD -25.4% (control -25.4%)
### KOSPI_EX_K200 — ALPHA — BULL_2025
- FACTOR_ONLY: mean +0.76%, win 59%, edge vs EW4 -0.02%, sign accuracy 55%, rank IC +0.07, MDD -8.0% (control -8.5%)
- FULL: mean +0.70%, win 59%, edge vs EW4 -0.07%, sign accuracy 57%, rank IC -0.04, MDD -7.9% (control -8.5%)
- MARKET_ONLY: mean +0.77%, win 59%, edge vs EW4 -0.00%, sign accuracy 63%, rank IC -0.16, MDD -8.0% (control -8.5%)
### KOSPI_EX_K200 — ALPHA — DISCOVERY_2016_2022
- FACTOR_ONLY: mean +0.27%, win 55%, edge vs EW4 +0.03%, sign accuracy 56%, rank IC +0.12, MDD -30.3% (control -29.6%)
- FULL: mean +0.33%, win 56%, edge vs EW4 +0.09%, sign accuracy 56%, rank IC +0.18, MDD -31.6% (control -29.6%)
- MARKET_ONLY: mean +0.25%, win 58%, edge vs EW4 +0.01%, sign accuracy 53%, rank IC +0.09, MDD -29.7% (control -29.6%)
### KOSPI_EX_K200 — ALPHA — NORMAL_2023_2024
- FACTOR_ONLY: mean +0.11%, win 54%, edge vs EW4 -0.03%, sign accuracy 51%, rank IC +0.05, MDD -16.0% (control -16.7%)
- FULL: mean +0.06%, win 55%, edge vs EW4 -0.08%, sign accuracy 47%, rank IC +0.00, MDD -16.9% (control -16.7%)
- MARKET_ONLY: mean +0.09%, win 55%, edge vs EW4 -0.05%, sign accuracy 48%, rank IC -0.07, MDD -17.8% (control -16.7%)
### KOSPI_EX_K200 — ALPHA — YTD_2026
- FACTOR_ONLY: mean +1.50%, win 67%, edge vs EW4 -0.01%, sign accuracy 53%, rank IC -0.09, MDD -12.0% (control -12.0%)
- FULL: mean +1.54%, win 67%, edge vs EW4 +0.04%, sign accuracy 60%, rank IC +0.06, MDD -12.0% (control -12.0%)
- MARKET_ONLY: mean +1.50%, win 67%, edge vs EW4 +0.00%, sign accuracy 60%, rank IC +0.33, MDD -12.0% (control -12.0%)
### KOSPI_EX_K200 — RISK — BULL_2025
- FACTOR_ONLY: mean +0.14%, win 24%, edge vs market -0.46%, sign accuracy 45%, rank IC -0.09, MDD -4.9% (control -8.1%)
- FULL: mean +0.25%, win 33%, edge vs market -0.34%, sign accuracy 47%, rank IC -0.03, MDD -6.7% (control -8.1%)
- MARKET_ONLY: mean +0.28%, win 37%, edge vs market -0.32%, sign accuracy 53%, rank IC +0.03, MDD -10.5% (control -8.1%)
### KOSPI_EX_K200 — RISK — DISCOVERY_2016_2022
- FACTOR_ONLY: mean -0.17%, win 19%, edge vs market -0.24%, sign accuracy 45%, rank IC -0.14, MDD -29.6% (control -35.2%)
- FULL: mean -0.07%, win 21%, edge vs market -0.14%, sign accuracy 49%, rank IC -0.15, MDD -23.8% (control -35.2%)
- MARKET_ONLY: mean +0.00%, win 29%, edge vs market -0.07%, sign accuracy 50%, rank IC -0.11, MDD -15.8% (control -35.2%)
### KOSPI_EX_K200 — RISK — NORMAL_2023_2024
- FACTOR_ONLY: mean -0.01%, win 27%, edge vs market -0.06%, sign accuracy 51%, rank IC -0.06, MDD -13.2% (control -17.7%)
- FULL: mean -0.00%, win 23%, edge vs market -0.05%, sign accuracy 51%, rank IC +0.01, MDD -12.2% (control -17.7%)
- MARKET_ONLY: mean +0.05%, win 24%, edge vs market -0.00%, sign accuracy 54%, rank IC +0.08, MDD -12.2% (control -17.7%)
### KOSPI_EX_K200 — RISK — YTD_2026
- FACTOR_ONLY: mean +1.07%, win 60%, edge vs market -0.28%, sign accuracy 60%, rank IC +0.14, MDD -10.6% (control -10.6%)
- FULL: mean +1.36%, win 67%, edge vs market +0.00%, sign accuracy 67%, rank IC +0.08, MDD -10.6% (control -10.6%)
- MARKET_ONLY: mean +1.36%, win 67%, edge vs market +0.00%, sign accuracy 67%, rank IC -0.16, MDD -10.6% (control -10.6%)
### KOSPI_KOSDAQ_ALL — ALPHA — BULL_2025
- FACTOR_ONLY: mean +0.92%, win 67%, edge vs EW4 -0.14%, sign accuracy 41%, rank IC -0.34, MDD -10.3% (control -9.1%)
- FULL: mean +0.91%, win 65%, edge vs EW4 -0.15%, sign accuracy 41%, rank IC -0.32, MDD -10.3% (control -9.1%)
- MARKET_ONLY: mean +1.00%, win 73%, edge vs EW4 -0.06%, sign accuracy 51%, rank IC -0.09, MDD -9.6% (control -9.1%)
### KOSPI_KOSDAQ_ALL — ALPHA — DISCOVERY_2016_2022
- FACTOR_ONLY: mean +0.03%, win 57%, edge vs EW4 -0.05%, sign accuracy 47%, rank IC -0.07, MDD -35.1% (control -32.3%)
- FULL: mean +0.02%, win 57%, edge vs EW4 -0.06%, sign accuracy 51%, rank IC -0.06, MDD -31.4% (control -32.3%)
- MARKET_ONLY: mean +0.03%, win 54%, edge vs EW4 -0.06%, sign accuracy 53%, rank IC -0.03, MDD -34.2% (control -32.3%)
### KOSPI_KOSDAQ_ALL — ALPHA — NORMAL_2023_2024
- FACTOR_ONLY: mean +0.06%, win 52%, edge vs EW4 -0.09%, sign accuracy 50%, rank IC -0.10, MDD -23.1% (control -23.6%)
- FULL: mean +0.07%, win 54%, edge vs EW4 -0.09%, sign accuracy 47%, rank IC -0.05, MDD -21.5% (control -23.6%)
- MARKET_ONLY: mean +0.14%, win 59%, edge vs EW4 -0.01%, sign accuracy 53%, rank IC +0.08, MDD -20.5% (control -23.6%)
### KOSPI_KOSDAQ_ALL — ALPHA — YTD_2026
- FACTOR_ONLY: mean +2.05%, win 67%, edge vs EW4 +1.39%, sign accuracy 57%, rank IC +0.43, MDD -24.8% (control -25.8%)
- FULL: mean +1.36%, win 67%, edge vs EW4 +0.70%, sign accuracy 52%, rank IC +0.19, MDD -24.8% (control -25.8%)
- MARKET_ONLY: mean +0.66%, win 57%, edge vs EW4 +0.00%, sign accuracy 48%, rank IC +0.05, MDD -25.8% (control -25.8%)
### KOSPI_KOSDAQ_ALL — RISK — BULL_2025
- FACTOR_ONLY: mean +0.14%, win 27%, edge vs market -1.13%, sign accuracy 41%, rank IC -0.35, MDD -7.2% (control -9.1%)
- FULL: mean +0.37%, win 29%, edge vs market -0.90%, sign accuracy 45%, rank IC -0.31, MDD -9.2% (control -9.1%)
- MARKET_ONLY: mean +0.82%, win 45%, edge vs market -0.45%, sign accuracy 55%, rank IC -0.02, MDD -5.9% (control -9.1%)
### KOSPI_KOSDAQ_ALL — RISK — DISCOVERY_2016_2022
- FACTOR_ONLY: mean -0.14%, win 35%, edge vs market -0.12%, sign accuracy 49%, rank IC -0.11, MDD -32.9% (control -34.8%)
- FULL: mean -0.19%, win 29%, edge vs market -0.17%, sign accuracy 47%, rank IC -0.14, MDD -31.0% (control -34.8%)
- MARKET_ONLY: mean +0.04%, win 35%, edge vs market +0.06%, sign accuracy 52%, rank IC +0.01, MDD -22.0% (control -34.8%)
### KOSPI_KOSDAQ_ALL — RISK — NORMAL_2023_2024
- FACTOR_ONLY: mean -0.09%, win 24%, edge vs market -0.10%, sign accuracy 53%, rank IC +0.03, MDD -20.6% (control -23.9%)
- FULL: mean -0.08%, win 22%, edge vs market -0.09%, sign accuracy 52%, rank IC +0.03, MDD -19.5% (control -23.9%)
- MARKET_ONLY: mean +0.13%, win 23%, edge vs market +0.12%, sign accuracy 53%, rank IC -0.00, MDD -7.2% (control -23.9%)
### KOSPI_KOSDAQ_ALL — RISK — YTD_2026
- FACTOR_ONLY: mean +1.12%, win 48%, edge vs market -0.90%, sign accuracy 52%, rank IC -0.18, MDD -28.3% (control -24.8%)
- FULL: mean +2.02%, win 62%, edge vs market +0.00%, sign accuracy 62%, rank IC -0.26, MDD -24.8% (control -24.8%)
- MARKET_ONLY: mean +2.02%, win 62%, edge vs market +0.00%, sign accuracy 62%, rank IC -0.03, MDD -24.8% (control -24.8%)

## Incremental factor information over market/liquidity model

- ALPHA BULL_2025 FACTOR_ONLY: median delta edge -0.10%/5D; delta sign accuracy -9.2%; delta rank IC -0.070; universes=6
- ALPHA BULL_2025 FULL: median delta edge -0.09%/5D; delta sign accuracy -10.2%; delta rank IC -0.088; universes=6
- ALPHA DISCOVERY_2016_2022 FACTOR_ONLY: median delta edge +0.01%/5D; delta sign accuracy +0.9%; delta rank IC +0.007; universes=6
- ALPHA DISCOVERY_2016_2022 FULL: median delta edge +0.04%/5D; delta sign accuracy +0.7%; delta rank IC +0.033; universes=6
- ALPHA NORMAL_2023_2024 FACTOR_ONLY: median delta edge -0.08%/5D; delta sign accuracy -5.2%; delta rank IC -0.169; universes=6
- ALPHA NORMAL_2023_2024 FULL: median delta edge -0.07%/5D; delta sign accuracy -6.7%; delta rank IC -0.137; universes=6
- ALPHA YTD_2026 FACTOR_ONLY: median delta edge +0.20%/5D; delta sign accuracy -7.2%; delta rank IC +0.086; universes=6
- ALPHA YTD_2026 FULL: median delta edge +0.04%/5D; delta sign accuracy -6.3%; delta rank IC +0.026; universes=6
- RISK BULL_2025 FACTOR_ONLY: median delta edge -0.23%/5D; delta sign accuracy -7.1%; delta rank IC -0.094; universes=6
- RISK BULL_2025 FULL: median delta edge -0.26%/5D; delta sign accuracy -7.1%; delta rank IC -0.038; universes=6
- RISK DISCOVERY_2016_2022 FACTOR_ONLY: median delta edge -0.12%/5D; delta sign accuracy -5.7%; delta rank IC -0.117; universes=6
- RISK DISCOVERY_2016_2022 FULL: median delta edge -0.17%/5D; delta sign accuracy -5.9%; delta rank IC -0.095; universes=6
- RISK NORMAL_2023_2024 FACTOR_ONLY: median delta edge -0.07%/5D; delta sign accuracy -1.0%; delta rank IC -0.013; universes=6
- RISK NORMAL_2023_2024 FULL: median delta edge -0.07%/5D; delta sign accuracy -1.6%; delta rank IC +0.013; universes=6
- RISK YTD_2026 FACTOR_ONLY: median delta edge -0.56%/5D; delta sign accuracy -3.3%; delta rank IC -0.114; universes=6
- RISK YTD_2026 FULL: median delta edge +0.00%/5D; delta sign accuracy +0.0%; delta rank IC -0.026; universes=6

## Promotion criterion

- Factor interaction earns a practical role only if FACTOR_ONLY or FULL improves the market/liquidity model across multiple universes in 2023-24 and does not materially reverse in 2025.
- If not, the tactical regime/factor-interaction project should not be forced into an allocation rule; the robust output would instead be the negative result and any unconditional factor edge.

