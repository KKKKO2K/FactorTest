# Factor-Level Finalist Daily-NAV Audit

Daily implementation matches the existing CF20 audit convention: positions selected on rebalance date are held from the next trading day; missing stock returns are zero-filled while the position remains held; one-way turnover is 0.5 * sum(abs(current-target)); costs are charged on rebalance turnover.

Finalist variants include BASE/CF20 pairs for PER and OPFY1 so overlay attribution remains explicit. PRIVATE_FLOW is tested as BASE only.

## 2016-2024 median across 10 phases

### KOSPI_ALL_PER_BASE
- GROSS: CAGR +8.48%; Sharpe 0.50; MDD -60.09%; Calmar 0.14; annual turnover 4.12x; positive phases 10/10
- NET30: CAGR +7.13%; Sharpe 0.44; MDD -60.91%; Calmar 0.12; annual turnover 4.12x; positive phases 10/10
- NET60: CAGR +5.80%; Sharpe 0.38; MDD -61.71%; Calmar 0.10; annual turnover 4.12x; positive phases 10/10

### KOSPI_ALL_PER_CF20
- GROSS: CAGR +8.82%; Sharpe 0.52; MDD -57.03%; Calmar 0.15; annual turnover 5.76x; positive phases 10/10
- NET30: CAGR +6.98%; Sharpe 0.43; MDD -58.37%; Calmar 0.12; annual turnover 5.76x; positive phases 10/10
- NET60: CAGR +5.16%; Sharpe 0.35; MDD -59.69%; Calmar 0.09; annual turnover 5.76x; positive phases 10/10

### KOSPI_ALL_PRIVATE_FLOW_BASE
- GROSS: CAGR +7.63%; Sharpe 0.44; MDD -51.57%; Calmar 0.15; annual turnover 14.35x; positive phases 10/10
- NET30: CAGR +3.11%; Sharpe 0.25; MDD -55.35%; Calmar 0.06; annual turnover 14.35x; positive phases 10/10
- NET60: CAGR -1.24%; Sharpe 0.06; MDD -58.66%; Calmar -0.02; annual turnover 14.35x; positive phases 4/10

### MIXED_PER_BASE
- GROSS: CAGR +6.65%; Sharpe 0.42; MDD -54.02%; Calmar 0.12; annual turnover 4.48x; positive phases 10/10
- NET30: CAGR +5.23%; Sharpe 0.35; MDD -55.07%; Calmar 0.10; annual turnover 4.48x; positive phases 10/10
- NET60: CAGR +3.82%; Sharpe 0.29; MDD -56.25%; Calmar 0.07; annual turnover 4.48x; positive phases 10/10

### MIXED_PER_CF20
- GROSS: CAGR +10.27%; Sharpe 0.58; MDD -51.62%; Calmar 0.19; annual turnover 5.86x; positive phases 10/10
- NET30: CAGR +8.37%; Sharpe 0.50; MDD -53.13%; Calmar 0.15; annual turnover 5.86x; positive phases 10/10
- NET60: CAGR +6.50%; Sharpe 0.41; MDD -54.60%; Calmar 0.12; annual turnover 5.86x; positive phases 10/10

### MIXED_OPFY1_BASE
- GROSS: CAGR +12.92%; Sharpe 0.63; MDD -46.80%; Calmar 0.27; annual turnover 13.76x; positive phases 10/10
- NET30: CAGR +8.34%; Sharpe 0.46; MDD -47.07%; Calmar 0.17; annual turnover 13.76x; positive phases 10/10
- NET60: CAGR +3.94%; Sharpe 0.28; MDD -48.92%; Calmar 0.08; annual turnover 13.76x; positive phases 10/10

### MIXED_OPFY1_CF20
- GROSS: CAGR +15.07%; Sharpe 0.71; MDD -46.47%; Calmar 0.32; annual turnover 13.95x; positive phases 10/10
- NET30: CAGR +10.34%; Sharpe 0.53; MDD -47.53%; Calmar 0.22; annual turnover 13.95x; positive phases 10/10
- NET60: CAGR +5.79%; Sharpe 0.36; MDD -49.12%; Calmar 0.12; annual turnover 13.95x; positive phases 10/10

## CF20 incremental — 2016-2024

### KOSPI_ALL_PER
- GROSS: median dCAGR +0.16%; dSharpe +0.01; dMDD +2.83%; dTurnover +1.63x; better CAGR phases 5/10
- NET30: median dCAGR -0.36%; dSharpe -0.01; dMDD +2.16%; dTurnover +1.63x; better CAGR phases 4/10
- NET60: median dCAGR -0.86%; dSharpe -0.04; dMDD +1.63%; dTurnover +1.63x; better CAGR phases 2/10

### MIXED_PER
- GROSS: median dCAGR +3.42%; dSharpe +0.15; dMDD +2.70%; dTurnover +1.39x; better CAGR phases 10/10
- NET30: median dCAGR +2.93%; dSharpe +0.13; dMDD +2.21%; dTurnover +1.39x; better CAGR phases 10/10
- NET60: median dCAGR +2.45%; dSharpe +0.11; dMDD +1.81%; dTurnover +1.39x; better CAGR phases 10/10

### MIXED_OPFY1
- GROSS: median dCAGR +2.84%; dSharpe +0.11; dMDD +0.17%; dTurnover +0.20x; better CAGR phases 9/10
- NET30: median dCAGR +2.68%; dSharpe +0.11; dMDD +0.02%; dTurnover +0.20x; better CAGR phases 9/10
- NET60: median dCAGR +2.54%; dSharpe +0.10; dMDD +0.23%; dTurnover +0.20x; better CAGR phases 9/10

## 2026 YTD stress diagnostic — NET60

- KOSPI_ALL_PER_BASE: CAGR +31.73%; Sharpe 0.92; MDD -18.05%; positive phases 10/10
- KOSPI_ALL_PER_CF20: CAGR +46.24%; Sharpe 1.14; MDD -17.94%; positive phases 10/10
- KOSPI_ALL_PRIVATE_FLOW_BASE: CAGR +29.82%; Sharpe 0.79; MDD -34.85%; positive phases 10/10
- MIXED_PER_BASE: CAGR +12.64%; Sharpe 0.51; MDD -26.86%; positive phases 10/10
- MIXED_PER_CF20: CAGR +8.07%; Sharpe 0.40; MDD -30.00%; positive phases 10/10
- MIXED_OPFY1_BASE: CAGR -23.70%; Sharpe -0.18; MDD -49.59%; positive phases 0/10
- MIXED_OPFY1_CF20: CAGR -4.09%; Sharpe 0.20; MDD -43.97%; positive phases 0/10

## Guardrails

- 2023+ is a robustness/stress slice, not a clean untouched OOS confirmation, because later data informed earlier research iterations.
- NET30/NET60 are turnover-proportional implementation-cost scenarios, not a full market-impact model.
- MDD here is true daily-NAV MDD for each factor sleeve, not the prior aggregate 8-sleeve portfolio MDD.
- Final production confirmation should still use frozen-rule/walk-forward logic per RESEARCH_ARCHITECTURE_V2.md.
