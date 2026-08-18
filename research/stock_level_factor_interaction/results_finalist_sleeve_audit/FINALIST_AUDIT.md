# Finalist Factor-Sleeve Daily NAV Audit

Exact daily-NAV simulation for the four finalist factor/universe pairs. Each sleeve holds 20 equal-weight names and rebalances every 10 trading days, with 10 staggered phases. Costs are charged on one-way turnover as turnover × 30bp or 60bp.

## 2016-2024 median across 10 phases

### KOSPI_ALL × PER12MF
- BASE GROSS: CAGR +8.48%; Sharpe 0.50; MDD -60.1%; worst-phase MDD -61.3%; turnover 4.12x/yr
- BASE NET30: CAGR +7.13%; Sharpe 0.44; MDD -60.9%; worst-phase MDD -62.1%; turnover 4.12x/yr
- BASE NET60: CAGR +5.80%; Sharpe 0.38; MDD -61.7%; worst-phase MDD -62.9%; turnover 4.12x/yr
- CF20 GROSS: CAGR +8.82%; Sharpe 0.52; MDD -57.0%; worst-phase MDD -59.7%; turnover 5.76x/yr
- CF20 NET30: CAGR +6.98%; Sharpe 0.43; MDD -58.4%; worst-phase MDD -60.9%; turnover 5.76x/yr
- CF20 NET60: CAGR +5.16%; Sharpe 0.35; MDD -59.7%; worst-phase MDD -62.4%; turnover 5.76x/yr
- CF20 incremental GROSS: median dCAGR +0.16%; CAGR wins 5/10; dSharpe +0.01; MDD improves 10/10
- CF20 incremental NET30: median dCAGR -0.36%; CAGR wins 4/10; dSharpe -0.01; MDD improves 10/10
- CF20 incremental NET60: median dCAGR -0.86%; CAGR wins 2/10; dSharpe -0.04; MDD improves 9/10

### KOSPI_ALL × PRIVATE_FLOW
- BASE GROSS: CAGR +7.63%; Sharpe 0.44; MDD -51.6%; worst-phase MDD -57.0%; turnover 14.35x/yr
- BASE NET30: CAGR +3.11%; Sharpe 0.25; MDD -55.3%; worst-phase MDD -59.9%; turnover 14.35x/yr
- BASE NET60: CAGR -1.24%; Sharpe 0.06; MDD -58.7%; worst-phase MDD -62.7%; turnover 14.35x/yr
- CF20 GROSS: CAGR +8.00%; Sharpe 0.45; MDD -54.5%; worst-phase MDD -60.8%; turnover 14.74x/yr
- CF20 NET30: CAGR +3.36%; Sharpe 0.26; MDD -57.9%; worst-phase MDD -63.7%; turnover 14.74x/yr
- CF20 NET60: CAGR -1.08%; Sharpe 0.07; MDD -61.1%; worst-phase MDD -66.4%; turnover 14.74x/yr
- CF20 incremental GROSS: median dCAGR +1.07%; CAGR wins 7/10; dSharpe +0.04; MDD improves 2/10
- CF20 incremental NET30: median dCAGR +0.95%; CAGR wins 6/10; dSharpe +0.04; MDD improves 2/10
- CF20 incremental NET60: median dCAGR +0.83%; CAGR wins 6/10; dSharpe +0.03; MDD improves 1/10

### KOSDAQ_PLUS_KOSPI_EX_K200 × PER12MF
- BASE GROSS: CAGR +6.65%; Sharpe 0.42; MDD -54.0%; worst-phase MDD -55.6%; turnover 4.48x/yr
- BASE NET30: CAGR +5.23%; Sharpe 0.35; MDD -55.1%; worst-phase MDD -56.7%; turnover 4.48x/yr
- BASE NET60: CAGR +3.82%; Sharpe 0.29; MDD -56.2%; worst-phase MDD -58.0%; turnover 4.48x/yr
- CF20 GROSS: CAGR +10.27%; Sharpe 0.58; MDD -51.6%; worst-phase MDD -54.5%; turnover 5.86x/yr
- CF20 NET30: CAGR +8.37%; Sharpe 0.50; MDD -53.1%; worst-phase MDD -55.9%; turnover 5.86x/yr
- CF20 NET60: CAGR +6.50%; Sharpe 0.41; MDD -54.6%; worst-phase MDD -57.3%; turnover 5.86x/yr
- CF20 incremental GROSS: median dCAGR +3.42%; CAGR wins 10/10; dSharpe +0.15; MDD improves 8/10
- CF20 incremental NET30: median dCAGR +2.93%; CAGR wins 10/10; dSharpe +0.13; MDD improves 8/10
- CF20 incremental NET60: median dCAGR +2.45%; CAGR wins 10/10; dSharpe +0.11; MDD improves 8/10

### KOSDAQ_PLUS_KOSPI_EX_K200 × OPFY1_REV
- BASE GROSS: CAGR +12.92%; Sharpe 0.63; MDD -46.8%; worst-phase MDD -49.1%; turnover 13.76x/yr
- BASE NET30: CAGR +8.34%; Sharpe 0.46; MDD -47.1%; worst-phase MDD -50.1%; turnover 13.76x/yr
- BASE NET60: CAGR +3.94%; Sharpe 0.28; MDD -48.9%; worst-phase MDD -54.3%; turnover 13.76x/yr
- CF20 GROSS: CAGR +15.07%; Sharpe 0.71; MDD -46.5%; worst-phase MDD -47.5%; turnover 13.95x/yr
- CF20 NET30: CAGR +10.34%; Sharpe 0.53; MDD -47.5%; worst-phase MDD -49.0%; turnover 13.95x/yr
- CF20 NET60: CAGR +5.79%; Sharpe 0.36; MDD -49.1%; worst-phase MDD -52.4%; turnover 13.95x/yr
- CF20 incremental GROSS: median dCAGR +2.84%; CAGR wins 9/10; dSharpe +0.11; MDD improves 6/10
- CF20 incremental NET30: median dCAGR +2.68%; CAGR wins 9/10; dSharpe +0.11; MDD improves 5/10
- CF20 incremental NET60: median dCAGR +2.54%; CAGR wins 9/10; dSharpe +0.10; MDD improves 5/10

## Recent diagnostics

### NORMAL_2023_2024
- KOSPI_ALL × PER12MF BASE: CAGR +13.61%; Sharpe 0.77; MDD -14.0%; positive phases 10/10
- KOSPI_ALL × PER12MF CF20: CAGR +12.85%; Sharpe 0.73; MDD -14.1%; positive phases 10/10
- KOSPI_ALL × PRIVATE_FLOW BASE: CAGR +15.34%; Sharpe 0.77; MDD -22.0%; positive phases 10/10
- KOSPI_ALL × PRIVATE_FLOW CF20: CAGR +14.30%; Sharpe 0.72; MDD -21.8%; positive phases 10/10
- KOSDAQ_PLUS_KOSPI_EX_K200 × PER12MF BASE: CAGR +5.81%; Sharpe 0.40; MDD -17.5%; positive phases 10/10
- KOSDAQ_PLUS_KOSPI_EX_K200 × PER12MF CF20: CAGR +10.85%; Sharpe 0.67; MDD -15.4%; positive phases 10/10
- KOSDAQ_PLUS_KOSPI_EX_K200 × OPFY1_REV BASE: CAGR +2.80%; Sharpe 0.24; MDD -29.0%; positive phases 7/10
- KOSDAQ_PLUS_KOSPI_EX_K200 × OPFY1_REV CF20: CAGR +6.97%; Sharpe 0.41; MDD -27.1%; positive phases 9/10

### BULL_2025
- KOSPI_ALL × PER12MF BASE: CAGR +70.30%; Sharpe 2.57; MDD -13.3%; positive phases 10/10
- KOSPI_ALL × PER12MF CF20: CAGR +75.38%; Sharpe 2.67; MDD -13.8%; positive phases 10/10
- KOSPI_ALL × PRIVATE_FLOW BASE: CAGR +57.32%; Sharpe 1.94; MDD -16.4%; positive phases 10/10
- KOSPI_ALL × PRIVATE_FLOW CF20: CAGR +64.99%; Sharpe 2.06; MDD -16.6%; positive phases 10/10
- KOSDAQ_PLUS_KOSPI_EX_K200 × PER12MF BASE: CAGR +36.88%; Sharpe 1.64; MDD -13.9%; positive phases 10/10
- KOSDAQ_PLUS_KOSPI_EX_K200 × PER12MF CF20: CAGR +38.56%; Sharpe 1.72; MDD -13.1%; positive phases 10/10
- KOSDAQ_PLUS_KOSPI_EX_K200 × OPFY1_REV BASE: CAGR +83.51%; Sharpe 2.65; MDD -19.7%; positive phases 10/10
- KOSDAQ_PLUS_KOSPI_EX_K200 × OPFY1_REV CF20: CAGR +75.34%; Sharpe 2.55; MDD -18.0%; positive phases 10/10

### YTD_2026
- KOSPI_ALL × PER12MF BASE: CAGR +33.41%; Sharpe 0.95; MDD -17.8%; positive phases 10/10
- KOSPI_ALL × PER12MF CF20: CAGR +49.35%; Sharpe 1.20; MDD -17.9%; positive phases 10/10
- KOSPI_ALL × PRIVATE_FLOW BASE: CAGR +35.30%; Sharpe 0.87; MDD -34.4%; positive phases 10/10
- KOSPI_ALL × PRIVATE_FLOW CF20: CAGR +38.12%; Sharpe 0.91; MDD -31.6%; positive phases 10/10
- KOSDAQ_PLUS_KOSPI_EX_K200 × PER12MF BASE: CAGR +14.25%; Sharpe 0.55; MDD -26.6%; positive phases 10/10
- KOSDAQ_PLUS_KOSPI_EX_K200 × PER12MF CF20: CAGR +10.07%; Sharpe 0.45; MDD -29.6%; positive phases 10/10
- KOSDAQ_PLUS_KOSPI_EX_K200 × OPFY1_REV BASE: CAGR -20.17%; Sharpe -0.10; MDD -49.1%; positive phases 0/10
- KOSDAQ_PLUS_KOSPI_EX_K200 × OPFY1_REV CF20: CAGR +0.43%; Sharpe 0.29; MDD -43.4%; positive phases 5/10
