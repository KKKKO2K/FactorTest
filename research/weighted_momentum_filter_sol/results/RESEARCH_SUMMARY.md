# Exact weighted momentum × nonnegative 1M filter

Exact recovered signal:
`WEIGHTED_MOM = (12*R1M + 4*R3M + 2*R6M + R12M) / 17`

Calendar-month as-of horizons; market-cap >= KRW 250bn; descending Top20; equal-weight; 10 staggered 10-trading-day rebalance phases.
Pre-specified hypothesis: exclude only names with R1M < 0, i.e. retain R1M >= 0.

## NET30 comparison

### PRE_STRESS_2017_2024
- K200: BASE CAGR -10.05%, FILTER -9.11%, median Δ +0.20%; Sharpe -0.34->-0.30; MDD -61.5%->-59.8%; CAGR better 5/10 phases; excess better 5/10.
- KOSPI_EX_K200: BASE CAGR -12.68%, FILTER -11.37%, median Δ +1.20%; Sharpe -0.32->-0.28; MDD -74.4%->-73.5%; CAGR better 8/10 phases; excess better 8/10.
- KOSPI_ALL: BASE CAGR -14.80%, FILTER -13.22%, median Δ +0.41%; Sharpe -0.38->-0.33; MDD -75.5%->-74.6%; CAGR better 7/10 phases; excess better 7/10.
- KOSDAQ: BASE CAGR -4.74%, FILTER -2.36%, median Δ +2.05%; Sharpe 0.05->0.12; MDD -73.0%->-71.5%; CAGR better 6/10 phases; excess better 6/10.
- KOSPI_KOSDAQ_ALL: BASE CAGR -10.00%, FILTER -7.57%, median Δ +2.36%; Sharpe -0.08->-0.02; MDD -71.0%->-71.3%; CAGR better 9/10 phases; excess better 9/10.
- KOSDAQ_PLUS_KOSPI_EX_K200: BASE CAGR -9.26%, FILTER -6.91%, median Δ +2.22%; Sharpe -0.06->-0.01; MDD -73.7%->-70.3%; CAGR better 8/10 phases; excess better 8/10.

### EARLY_2017_2019
- K200: BASE CAGR -11.64%, FILTER -9.07%, median Δ +1.42%; Sharpe -0.57->-0.43; MDD -43.0%->-40.8%; CAGR better 6/10 phases; excess better 6/10.
- KOSPI_EX_K200: BASE CAGR -21.89%, FILTER -20.90%, median Δ +0.70%; Sharpe -0.90->-0.83; MDD -58.9%->-58.5%; CAGR better 5/10 phases; excess better 5/10.
- KOSPI_ALL: BASE CAGR -25.60%, FILTER -23.46%, median Δ +2.37%; Sharpe -1.07->-0.91; MDD -60.5%->-58.1%; CAGR better 9/10 phases; excess better 9/10.
- KOSDAQ: BASE CAGR +5.51%, FILTER +10.71%, median Δ +2.97%; Sharpe 0.33->0.48; MDD -50.9%->-50.6%; CAGR better 8/10 phases; excess better 8/10.
- KOSPI_KOSDAQ_ALL: BASE CAGR -8.44%, FILTER -5.63%, median Δ +2.94%; Sharpe -0.09->0.00; MDD -57.9%->-56.7%; CAGR better 8/10 phases; excess better 8/10.
- KOSDAQ_PLUS_KOSPI_EX_K200: BASE CAGR -6.65%, FILTER -4.46%, median Δ +2.94%; Sharpe -0.03->0.03; MDD -56.9%->-54.7%; CAGR better 9/10 phases; excess better 9/10.

### LATE_2020_2022
- K200: BASE CAGR -9.35%, FILTER -10.18%, median Δ -2.00%; Sharpe -0.24->-0.26; MDD -49.7%->-50.0%; CAGR better 3/10 phases; excess better 3/10.
- KOSPI_EX_K200: BASE CAGR -3.52%, FILTER -3.58%, median Δ +0.67%; Sharpe 0.05->0.05; MDD -49.4%->-48.2%; CAGR better 5/10 phases; excess better 5/10.
- KOSPI_ALL: BASE CAGR -8.02%, FILTER -9.59%, median Δ -0.73%; Sharpe -0.09->-0.14; MDD -53.2%->-50.9%; CAGR better 4/10 phases; excess better 4/10.
- KOSDAQ: BASE CAGR -13.31%, FILTER -10.46%, median Δ +1.81%; Sharpe -0.18->-0.10; MDD -62.6%->-60.0%; CAGR better 7/10 phases; excess better 7/10.
- KOSPI_KOSDAQ_ALL: BASE CAGR -10.65%, FILTER -7.95%, median Δ +2.77%; Sharpe -0.08->-0.02; MDD -59.2%->-57.2%; CAGR better 9/10 phases; excess better 9/10.
- KOSDAQ_PLUS_KOSPI_EX_K200: BASE CAGR -9.42%, FILTER -5.84%, median Δ +3.11%; Sharpe -0.06->0.03; MDD -57.3%->-54.9%; CAGR better 10/10 phases; excess better 10/10.

### NORMAL_2023_2024
- K200: BASE CAGR -9.19%, FILTER -9.99%, median Δ +0.19%; Sharpe -0.27->-0.31; MDD -28.6%->-27.9%; CAGR better 5/10 phases; excess better 5/10.
- KOSPI_EX_K200: BASE CAGR -8.79%, FILTER -9.01%, median Δ +1.66%; Sharpe -0.15->-0.17; MDD -60.6%->-58.5%; CAGR better 7/10 phases; excess better 7/10.
- KOSPI_ALL: BASE CAGR -6.22%, FILTER -6.66%, median Δ +0.87%; Sharpe -0.03->-0.06; MDD -58.2%->-55.9%; CAGR better 6/10 phases; excess better 6/10.
- KOSDAQ: BASE CAGR -10.52%, FILTER -12.11%, median Δ -3.16%; Sharpe -0.08->-0.12; MDD -54.4%->-55.8%; CAGR better 3/10 phases; excess better 3/10.
- KOSPI_KOSDAQ_ALL: BASE CAGR -8.92%, FILTER -9.63%, median Δ +0.14%; Sharpe -0.01->-0.04; MDD -59.1%->-59.9%; CAGR better 6/10 phases; excess better 6/10.
- KOSDAQ_PLUS_KOSPI_EX_K200: BASE CAGR -11.94%, FILTER -11.25%, median Δ +1.27%; Sharpe -0.11->-0.09; MDD -62.7%->-63.3%; CAGR better 6/10 phases; excess better 6/10.

### BULL_2025
- K200: BASE CAGR +55.01%, FILTER +47.85%, median Δ -11.29%; Sharpe 1.58->1.45; MDD -18.7%->-20.2%; CAGR better 2/10 phases; excess better 2/10.
- KOSPI_EX_K200: BASE CAGR +20.31%, FILTER +15.86%, median Δ -2.92%; Sharpe 0.75->0.63; MDD -21.2%->-22.2%; CAGR better 2/10 phases; excess better 2/10.
- KOSPI_ALL: BASE CAGR +28.49%, FILTER +30.08%, median Δ -1.84%; Sharpe 0.91->0.95; MDD -22.2%->-22.0%; CAGR better 2/10 phases; excess better 2/10.
- KOSDAQ: BASE CAGR +60.92%, FILTER +61.07%, median Δ +4.88%; Sharpe 1.54->1.57; MDD -22.4%->-21.6%; CAGR better 8/10 phases; excess better 8/10.
- KOSPI_KOSDAQ_ALL: BASE CAGR +54.55%, FILTER +59.55%, median Δ +3.24%; Sharpe 1.45->1.54; MDD -20.7%->-21.2%; CAGR better 7/10 phases; excess better 7/10.
- KOSDAQ_PLUS_KOSPI_EX_K200: BASE CAGR +39.01%, FILTER +43.39%, median Δ +0.51%; Sharpe 1.13->1.23; MDD -23.4%->-21.6%; CAGR better 7/10 phases; excess better 7/10.

### YTD_2026
- K200: BASE CAGR +60.83%, FILTER +120.47%, median Δ +59.31%; Sharpe 1.08->1.66; MDD -44.3%->-33.2%; CAGR better 10/10 phases; excess better 10/10.
- KOSPI_EX_K200: BASE CAGR -33.50%, FILTER -25.51%, median Δ +5.66%; Sharpe -0.38->-0.25; MDD -47.5%->-44.2%; CAGR better 10/10 phases; excess better 10/10.
- KOSPI_ALL: BASE CAGR -11.31%, FILTER +7.95%, median Δ +22.83%; Sharpe 0.16->0.43; MDD -48.2%->-42.0%; CAGR better 10/10 phases; excess better 10/10.
- KOSDAQ: BASE CAGR -15.50%, FILTER +9.62%, median Δ +27.99%; Sharpe 0.22->0.50; MDD -61.6%->-52.2%; CAGR better 10/10 phases; excess better 10/10.
- KOSPI_KOSDAQ_ALL: BASE CAGR -28.29%, FILTER -0.42%, median Δ +20.75%; Sharpe 0.00->0.37; MDD -61.8%->-56.4%; CAGR better 10/10 phases; excess better 10/10.
- KOSDAQ_PLUS_KOSPI_EX_K200: BASE CAGR -34.93%, FILTER -15.35%, median Δ +17.45%; Sharpe -0.11->0.18; MDD -64.0%->-57.4%; CAGR better 10/10 phases; excess better 10/10.

## Threshold sensitivity

Neighboring thresholds -10%, -5%, 0%, +5%, +10% use >= consistently. The 0% rule is pre-specified; neighbors test whether zero is special or part of a broader recent-momentum confirmation effect.
