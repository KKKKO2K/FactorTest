# Weighted Momentum Primary Recheck

This is the stage gate before CF20 or liquidity. No other factor is used in portfolio construction.

## Recovered definition

- `WEIGHTED_MOM = (12*R1M + 4*R3M + 2*R6M + R12M) / 17`
- Descending Top20; market-cap cutoff KRW 250bn.
- Equal-weight Top20 is used here to isolate the stock-selection signal; historical production weighting is not assumed.

## Source-value reconstruction

- CALENDAR_MONTH_ASOF: component RMSE 0.029pp; factor RMSE 0.023pp.
- TRADING_DAYS_21_63_126_252: component RMSE 8.369pp; factor RMSE 0.761pp.
- **Chosen convention: CALENDAR_MONTH_ASOF**, selected only by workbook fidelity.

## 2017-2024 NET30 — median across 10 phases

- K200: CAGR -10.05%; MDD -61.5%; Sharpe -0.34; Calmar -0.16; BM CAGR +2.00%; excess -11.75%; IR -0.63; relative MDD -65.6%; turnover 11.83x; positive CAGR phases 0/10; positive excess phases 0/10.
- KOSPI_EX_K200: CAGR -12.68%; MDD -74.4%; Sharpe -0.32; Calmar -0.17; BM CAGR +2.39%; excess -14.73%; IR -0.67; relative MDD -73.2%; turnover 11.25x; positive CAGR phases 0/10; positive excess phases 0/10.
- KOSPI_ALL: CAGR -14.80%; MDD -75.5%; Sharpe -0.38; Calmar -0.20; BM CAGR +1.99%; excess -16.42%; IR -0.58; relative MDD -77.1%; turnover 12.31x; positive CAGR phases 0/10; positive excess phases 0/10.
- KOSDAQ: CAGR -4.74%; MDD -73.0%; Sharpe 0.05; Calmar -0.07; BM CAGR +1.44%; excess -6.07%; IR -0.10; relative MDD -58.9%; turnover 11.77x; positive CAGR phases 0/10; positive excess phases 0/10.
- KOSPI_KOSDAQ_ALL: CAGR -10.00%; MDD -71.0%; Sharpe -0.08; Calmar -0.14; BM CAGR +1.89%; excess -11.66%; IR -0.20; relative MDD -68.8%; turnover 12.49x; positive CAGR phases 0/10; positive excess phases 0/10.
- KOSDAQ_PLUS_KOSPI_EX_K200: CAGR -9.26%; MDD -73.7%; Sharpe -0.06; Calmar -0.13; BM CAGR +1.53%; excess -10.70%; IR -0.22; relative MDD -65.8%; turnover 12.28x; positive CAGR phases 0/10; positive excess phases 0/10.

## Historical blocks — NET30

### EARLY_2017_2019
- K200: CAGR -11.64%; MDD -43.0%; Sharpe -0.57; excess -13.73%; IR -0.86; positive CAGR 0/10, excess 0/10.
- KOSPI_EX_K200: CAGR -21.89%; MDD -58.9%; Sharpe -0.90; excess -20.67%; IR -1.29; positive CAGR 0/10, excess 0/10.
- KOSPI_ALL: CAGR -25.60%; MDD -60.5%; Sharpe -1.07; excess -27.01%; IR -1.31; positive CAGR 0/10, excess 0/10.
- KOSDAQ: CAGR +5.51%; MDD -50.9%; Sharpe 0.33; excess +3.02%; IR 0.28; positive CAGR 9/10, excess 9/10.
- KOSPI_KOSDAQ_ALL: CAGR -8.44%; MDD -57.9%; Sharpe -0.09; excess -10.55%; IR -0.21; positive CAGR 0/10, excess 0/10.
- KOSDAQ_PLUS_KOSPI_EX_K200: CAGR -6.65%; MDD -56.9%; Sharpe -0.03; excess -7.67%; IR -0.16; positive CAGR 0/10, excess 0/10.

### LATE_2020_2022
- K200: CAGR -9.35%; MDD -49.7%; Sharpe -0.24; excess -9.63%; IR -0.46; positive CAGR 0/10, excess 0/10.
- KOSPI_EX_K200: CAGR -3.52%; MDD -49.4%; Sharpe 0.05; excess -6.77%; IR -0.22; positive CAGR 1/10, excess 0/10.
- KOSPI_ALL: CAGR -8.02%; MDD -53.2%; Sharpe -0.09; excess -8.48%; IR -0.21; positive CAGR 0/10, excess 0/10.
- KOSDAQ: CAGR -13.31%; MDD -62.6%; Sharpe -0.18; excess -14.25%; IR -0.41; positive CAGR 0/10, excess 0/10.
- KOSPI_KOSDAQ_ALL: CAGR -10.65%; MDD -59.2%; Sharpe -0.08; excess -11.14%; IR -0.18; positive CAGR 0/10, excess 0/10.
- KOSDAQ_PLUS_KOSPI_EX_K200: CAGR -9.42%; MDD -57.3%; Sharpe -0.06; excess -10.67%; IR -0.23; positive CAGR 0/10, excess 0/10.

### NORMAL_2023_2024
- K200: CAGR -9.19%; MDD -28.6%; Sharpe -0.27; excess -12.30%; IR -0.59; positive CAGR 0/10, excess 0/10.
- KOSPI_EX_K200: CAGR -8.79%; MDD -60.6%; Sharpe -0.15; excess -14.58%; IR -0.57; positive CAGR 0/10, excess 0/10.
- KOSPI_ALL: CAGR -6.22%; MDD -58.2%; Sharpe -0.03; excess -9.71%; IR -0.23; positive CAGR 0/10, excess 0/10.
- KOSDAQ: CAGR -10.52%; MDD -54.4%; Sharpe -0.08; excess -10.66%; IR -0.22; positive CAGR 0/10, excess 0/10.
- KOSPI_KOSDAQ_ALL: CAGR -8.92%; MDD -59.1%; Sharpe -0.01; excess -11.79%; IR -0.16; positive CAGR 1/10, excess 1/10.
- KOSDAQ_PLUS_KOSPI_EX_K200: CAGR -11.94%; MDD -62.7%; Sharpe -0.11; excess -13.89%; IR -0.30; positive CAGR 1/10, excess 1/10.

### BULL_2025
- K200: CAGR +55.01%; MDD -18.7%; Sharpe 1.58; excess -16.10%; IR -0.71; positive CAGR 10/10, excess 0/10.
- KOSPI_EX_K200: CAGR +20.31%; MDD -21.2%; Sharpe 0.75; excess -10.51%; IR -0.38; positive CAGR 10/10, excess 1/10.
- KOSPI_ALL: CAGR +28.49%; MDD -22.2%; Sharpe 0.91; excess -28.73%; IR -1.15; positive CAGR 10/10, excess 0/10.
- KOSDAQ: CAGR +60.92%; MDD -22.4%; Sharpe 1.54; excess +14.93%; IR 0.67; positive CAGR 10/10, excess 9/10.
- KOSPI_KOSDAQ_ALL: CAGR +54.55%; MDD -20.7%; Sharpe 1.45; excess -11.17%; IR -0.28; positive CAGR 10/10, excess 2/10.
- KOSDAQ_PLUS_KOSPI_EX_K200: CAGR +39.01%; MDD -23.4%; Sharpe 1.13; excess +0.44%; IR 0.16; positive CAGR 10/10, excess 5/10.

### YTD_2026
- K200: CAGR +60.83%; MDD -44.3%; Sharpe 1.08; excess -21.46%; IR -0.78; positive CAGR 10/10, excess 0/10.
- KOSPI_EX_K200: CAGR -33.50%; MDD -47.5%; Sharpe -0.38; excess -35.73%; IR -1.15; positive CAGR 0/10, excess 0/10.
- KOSPI_ALL: CAGR -11.31%; MDD -48.2%; Sharpe 0.16; excess -55.13%; IR -2.12; positive CAGR 3/10, excess 0/10.
- KOSDAQ: CAGR -15.50%; MDD -61.6%; Sharpe 0.22; excess +10.40%; IR 0.57; positive CAGR 1/10, excess 7/10.
- KOSPI_KOSDAQ_ALL: CAGR -28.29%; MDD -61.8%; Sharpe 0.00; excess -59.91%; IR -1.50; positive CAGR 0/10, excess 0/10.
- KOSDAQ_PLUS_KOSPI_EX_K200: CAGR -34.93%; MDD -64.0%; Sharpe -0.11; excess -22.18%; IR -0.10; positive CAGR 0/10, excess 1/10.

## Stage gate

- Only if this primary is independently credible should CF20 be tested on it.
- 2025/2026 are stress diagnostics, not untouched OOS.
- No other factor and no liquidity overlay enter this run.
- Large raw outputs are retained as gzip chunks plus manifests.
