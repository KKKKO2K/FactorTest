# CF20 Liquidity Portfolio Comparison

CF20 is frozen. This stage converts the previously tested factor/liquidity rules into actual daily long-only portfolio NAVs.

Construction: 8 equal-notional factor sleeves; each sleeve holds Top20 equal-weight names. Duplicate names across sleeves receive proportionally larger aggregate weights. Rebalance every 10 trading days. All 10 possible rebalance phases are simulated.

Turnover is measured on the aggregate portfolio as 0.5 * sum(abs(target weight - pre-trade drifted weight)). Costs are charged at each rebalance. Headline comparisons use 30bp per one-way turnover; 0bp and 60bp are also saved.

Selection guardrail: liquidity metrics/cutoffs are frozen from prior stock-level, horizon, and phase tests. No portfolio metric is used to retune a cutoff.

## KOSPI_EX_K200 — 30bp, median across 10 phases

### PRE_STRESS_2016_2024
- ACT5_LOW10: CAGR +3.2%; MDD -58.5%; Sharpe 0.26; ann.turn 8.66x; worst-phase CAGR +1.9%
- TURNOVER20_TOP01_LOW10: CAGR +3.1%; MDD -57.8%; Sharpe 0.25; ann.turn 8.33x; worst-phase CAGR +2.3%
- TURNOVER20_TOP01: CAGR +3.0%; MDD -57.7%; Sharpe 0.25; ann.turn 8.28x; worst-phase CAGR +2.5%
- AMIHUD20_TOP05: CAGR +2.6%; MDD -58.9%; Sharpe 0.23; ann.turn 8.27x; worst-phase CAGR +2.0%
- ADV20_LOW10: CAGR +2.5%; MDD -59.0%; Sharpe 0.22; ann.turn 8.27x; worst-phase CAGR +1.9%
- CF20: CAGR +2.2%; MDD -58.9%; Sharpe 0.21; ann.turn 8.27x; worst-phase CAGR +1.7%

### NORMAL_2023_2024
- ACT5_LOW10: CAGR +8.9%; MDD -21.5%; Sharpe 0.55; ann.turn 8.88x; worst-phase CAGR +4.6%
- TURNOVER20_TOP01_LOW10: CAGR +7.8%; MDD -21.8%; Sharpe 0.49; ann.turn 8.58x; worst-phase CAGR +3.2%
- TURNOVER20_TOP01: CAGR +7.6%; MDD -21.1%; Sharpe 0.49; ann.turn 8.51x; worst-phase CAGR +3.8%
- ADV20_LOW10: CAGR +7.5%; MDD -21.7%; Sharpe 0.48; ann.turn 8.55x; worst-phase CAGR +3.3%
- AMIHUD20_TOP05: CAGR +7.5%; MDD -21.5%; Sharpe 0.48; ann.turn 8.52x; worst-phase CAGR +3.1%
- CF20: CAGR +6.1%; MDD -21.9%; Sharpe 0.41; ann.turn 8.53x; worst-phase CAGR +2.7%

### BULL_2025
- TURNOVER20_TOP01: CAGR +46.1%; MDD -13.5%; Sharpe 1.88; ann.turn 8.13x; worst-phase CAGR +41.8%
- ACT5_LOW10: CAGR +44.7%; MDD -13.9%; Sharpe 1.85; ann.turn 8.60x; worst-phase CAGR +38.8%
- TURNOVER20_TOP01_LOW10: CAGR +45.3%; MDD -13.8%; Sharpe 1.84; ann.turn 8.17x; worst-phase CAGR +41.5%
- CF20: CAGR +44.1%; MDD -14.3%; Sharpe 1.80; ann.turn 8.17x; worst-phase CAGR +40.1%
- ADV20_LOW10: CAGR +44.1%; MDD -14.3%; Sharpe 1.80; ann.turn 8.17x; worst-phase CAGR +40.1%
- AMIHUD20_TOP05: CAGR +43.9%; MDD -14.3%; Sharpe 1.79; ann.turn 8.18x; worst-phase CAGR +39.8%

### YTD_2026
- TURNOVER20_TOP01: CAGR -1.9%; MDD -37.7%; Sharpe 0.18; ann.turn 8.82x; worst-phase CAGR -9.3%
- ACT5_LOW10: CAGR -2.5%; MDD -37.4%; Sharpe 0.17; ann.turn 9.21x; worst-phase CAGR -10.2%
- TURNOVER20_TOP01_LOW10: CAGR -3.3%; MDD -38.7%; Sharpe 0.15; ann.turn 8.86x; worst-phase CAGR -10.8%
- ADV20_LOW10: CAGR -4.3%; MDD -37.9%; Sharpe 0.13; ann.turn 8.75x; worst-phase CAGR -10.6%
- AMIHUD20_TOP05: CAGR -4.4%; MDD -37.9%; Sharpe 0.13; ann.turn 8.75x; worst-phase CAGR -10.5%
- CF20: CAGR -5.7%; MDD -38.8%; Sharpe 0.10; ann.turn 8.73x; worst-phase CAGR -12.5%

### FULL_2016_2026
- TURNOVER20_TOP01: CAGR +6.3%; MDD -57.7%; Sharpe 0.39; ann.turn 8.29x; worst-phase CAGR +5.5%
- ACT5_LOW10: CAGR +6.1%; MDD -58.5%; Sharpe 0.38; ann.turn 8.68x; worst-phase CAGR +5.2%
- TURNOVER20_TOP01_LOW10: CAGR +6.1%; MDD -57.8%; Sharpe 0.38; ann.turn 8.36x; worst-phase CAGR +5.5%
- AMIHUD20_TOP05: CAGR +5.6%; MDD -58.9%; Sharpe 0.36; ann.turn 8.29x; worst-phase CAGR +4.9%
- ADV20_LOW10: CAGR +5.6%; MDD -59.0%; Sharpe 0.36; ann.turn 8.29x; worst-phase CAGR +4.8%
- CF20: CAGR +5.3%; MDD -58.9%; Sharpe 0.35; ann.turn 8.28x; worst-phase CAGR +4.4%

### Incremental vs CF20 baseline — PRE_STRESS_2016_2024

- TURNOVER20_TOP01_LOW10: median dCAGR +0.8%; CAGR better 10/10 phases; dSharpe 0.04 (10/10 better); MDD improvement +1.0% (10/10 better)
- TURNOVER20_TOP01: median dCAGR +0.8%; CAGR better 10/10 phases; dSharpe 0.04 (10/10 better); MDD improvement +1.2% (10/10 better)
- ACT5_LOW10: median dCAGR +0.6%; CAGR better 10/10 phases; dSharpe 0.03 (10/10 better); MDD improvement +0.2% (8/10 better)
- AMIHUD20_TOP05: median dCAGR +0.4%; CAGR better 10/10 phases; dSharpe 0.02 (10/10 better); MDD improvement +0.0% (5/10 better)
- ADV20_LOW10: median dCAGR +0.3%; CAGR better 10/10 phases; dSharpe 0.02 (10/10 better); MDD improvement -0.0% (4/10 better)

## KOSDAQ — 30bp, median across 10 phases

### PRE_STRESS_2016_2024
- TURNOVER20_TOP01_LOW30: CAGR +2.8%; MDD -47.5%; Sharpe 0.24; ann.turn 9.73x; worst-phase CAGR +0.6%
- TURNOVER20_LOW30: CAGR +2.5%; MDD -47.7%; Sharpe 0.23; ann.turn 9.74x; worst-phase CAGR +0.1%
- ACT5_LOW30: CAGR +2.3%; MDD -49.9%; Sharpe 0.22; ann.turn 11.45x; worst-phase CAGR +0.7%
- ACT1_LOW05: CAGR +2.3%; MDD -48.2%; Sharpe 0.22; ann.turn 9.67x; worst-phase CAGR +0.1%
- AMIHUD20_TOP05: CAGR +2.1%; MDD -48.4%; Sharpe 0.21; ann.turn 9.61x; worst-phase CAGR -0.2%
- CF20: CAGR +1.5%; MDD -49.2%; Sharpe 0.18; ann.turn 9.60x; worst-phase CAGR -0.9%

### NORMAL_2023_2024
- TURNOVER20_LOW30: CAGR +5.1%; MDD -35.5%; Sharpe 0.32; ann.turn 10.24x; worst-phase CAGR +0.7%
- TURNOVER20_TOP01_LOW30: CAGR +4.9%; MDD -33.7%; Sharpe 0.32; ann.turn 10.23x; worst-phase CAGR +1.2%
- ACT1_LOW05: CAGR +4.4%; MDD -34.5%; Sharpe 0.30; ann.turn 10.17x; worst-phase CAGR -1.0%
- AMIHUD20_TOP05: CAGR +4.1%; MDD -34.5%; Sharpe 0.29; ann.turn 10.08x; worst-phase CAGR -2.1%
- ACT5_LOW30: CAGR +3.9%; MDD -33.9%; Sharpe 0.28; ann.turn 11.88x; worst-phase CAGR +0.8%
- CF20: CAGR +3.7%; MDD -34.5%; Sharpe 0.27; ann.turn 10.08x; worst-phase CAGR -2.6%

### BULL_2025
- ACT5_LOW30: CAGR +69.8%; MDD -15.3%; Sharpe 2.43; ann.turn 11.64x; worst-phase CAGR +64.1%
- AMIHUD20_TOP05: CAGR +68.1%; MDD -15.8%; Sharpe 2.37; ann.turn 10.17x; worst-phase CAGR +62.3%
- CF20: CAGR +68.0%; MDD -15.8%; Sharpe 2.37; ann.turn 10.17x; worst-phase CAGR +62.0%
- ACT1_LOW05: CAGR +67.7%; MDD -15.8%; Sharpe 2.37; ann.turn 10.20x; worst-phase CAGR +62.2%
- TURNOVER20_TOP01_LOW30: CAGR +72.2%; MDD -17.0%; Sharpe 2.36; ann.turn 10.40x; worst-phase CAGR +65.6%
- TURNOVER20_LOW30: CAGR +71.3%; MDD -16.8%; Sharpe 2.32; ann.turn 10.44x; worst-phase CAGR +67.3%

### YTD_2026
- ACT1_LOW05: CAGR +8.1%; MDD -44.6%; Sharpe 0.43; ann.turn 11.18x; worst-phase CAGR -8.4%
- TURNOVER20_TOP01_LOW30: CAGR +7.5%; MDD -45.9%; Sharpe 0.43; ann.turn 11.58x; worst-phase CAGR -9.2%
- TURNOVER20_LOW30: CAGR +7.2%; MDD -46.2%; Sharpe 0.42; ann.turn 11.55x; worst-phase CAGR -7.7%
- CF20: CAGR +7.4%; MDD -44.8%; Sharpe 0.42; ann.turn 11.10x; worst-phase CAGR -10.8%
- AMIHUD20_TOP05: CAGR +7.0%; MDD -44.8%; Sharpe 0.41; ann.turn 11.12x; worst-phase CAGR -11.4%
- ACT5_LOW30: CAGR +4.5%; MDD -43.5%; Sharpe 0.37; ann.turn 12.83x; worst-phase CAGR -11.6%

### FULL_2016_2026
- TURNOVER20_TOP01_LOW30: CAGR +8.2%; MDD -47.5%; Sharpe 0.42; ann.turn 9.90x; worst-phase CAGR +6.2%
- ACT5_LOW30: CAGR +7.8%; MDD -49.9%; Sharpe 0.41; ann.turn 11.54x; worst-phase CAGR +5.3%
- TURNOVER20_LOW30: CAGR +7.8%; MDD -47.8%; Sharpe 0.40; ann.turn 9.90x; worst-phase CAGR +5.7%
- ACT1_LOW05: CAGR +7.6%; MDD -48.2%; Sharpe 0.40; ann.turn 9.81x; worst-phase CAGR +5.4%
- AMIHUD20_TOP05: CAGR +7.3%; MDD -48.4%; Sharpe 0.39; ann.turn 9.75x; worst-phase CAGR +5.6%
- CF20: CAGR +6.7%; MDD -49.2%; Sharpe 0.37; ann.turn 9.74x; worst-phase CAGR +5.0%

### Incremental vs CF20 baseline — PRE_STRESS_2016_2024

- TURNOVER20_TOP01_LOW30: median dCAGR +1.5%; CAGR better 10/10 phases; dSharpe 0.06 (10/10 better); MDD improvement +1.9% (9/10 better)
- TURNOVER20_LOW30: median dCAGR +1.0%; CAGR better 10/10 phases; dSharpe 0.04 (10/10 better); MDD improvement +1.4% (9/10 better)
- ACT1_LOW05: median dCAGR +0.8%; CAGR better 10/10 phases; dSharpe 0.03 (10/10 better); MDD improvement +0.8% (10/10 better)
- AMIHUD20_TOP05: median dCAGR +0.7%; CAGR better 10/10 phases; dSharpe 0.03 (10/10 better); MDD improvement +0.7% (10/10 better)
- ACT5_LOW30: median dCAGR +0.8%; CAGR better 6/10 phases; dSharpe 0.03 (6/10 better); MDD improvement -0.2% (2/10 better)

## NON_K200_50_50 — 30bp, median across 10 phases

### PRE_STRESS_2016_2024
- TURNOVER_RULE: CAGR +3.3%; MDD -52.4%; Sharpe 0.26; ann.turn 9.03x; worst-phase CAGR +2.2%
- TURNOVER_SIMPLE_DIAG: CAGR +3.1%; MDD -52.5%; Sharpe 0.25; ann.turn 9.01x; worst-phase CAGR +2.2%
- ACT5_RULE: CAGR +3.1%; MDD -54.0%; Sharpe 0.25; ann.turn 10.06x; worst-phase CAGR +1.5%
- AMIHUD_RULE: CAGR +2.6%; MDD -53.6%; Sharpe 0.23; ann.turn 8.94x; worst-phase CAGR +1.8%
- CF20_BASE: CAGR +2.1%; MDD -53.9%; Sharpe 0.21; ann.turn 8.94x; worst-phase CAGR +1.3%

### NORMAL_2023_2024
- ACT5_RULE: CAGR +7.1%; MDD -27.4%; Sharpe 0.44; ann.turn 10.38x; worst-phase CAGR +3.4%
- TURNOVER_RULE: CAGR +7.1%; MDD -27.9%; Sharpe 0.44; ann.turn 9.40x; worst-phase CAGR +4.6%
- TURNOVER_SIMPLE_DIAG: CAGR +6.9%; MDD -27.9%; Sharpe 0.43; ann.turn 9.38x; worst-phase CAGR +4.3%
- AMIHUD_RULE: CAGR +6.1%; MDD -27.8%; Sharpe 0.39; ann.turn 9.30x; worst-phase CAGR +3.3%
- CF20_BASE: CAGR +5.3%; MDD -27.8%; Sharpe 0.35; ann.turn 9.31x; worst-phase CAGR +2.8%

### BULL_2025
- ACT5_RULE: CAGR +56.6%; MDD -14.0%; Sharpe 2.29; ann.turn 10.15x; worst-phase CAGR +54.1%
- TURNOVER_RULE: CAGR +58.8%; MDD -14.7%; Sharpe 2.28; ann.turn 9.30x; worst-phase CAGR +54.3%
- TURNOVER_SIMPLE_DIAG: CAGR +58.8%; MDD -14.6%; Sharpe 2.28; ann.turn 9.30x; worst-phase CAGR +54.6%
- CF20_BASE: CAGR +55.6%; MDD -14.4%; Sharpe 2.24; ann.turn 9.17x; worst-phase CAGR +51.2%
- AMIHUD_RULE: CAGR +55.5%; MDD -14.4%; Sharpe 2.24; ann.turn 9.18x; worst-phase CAGR +51.2%

### YTD_2026
- TURNOVER_SIMPLE_DIAG: CAGR +3.4%; MDD -41.3%; Sharpe 0.33; ann.turn 10.24x; worst-phase CAGR -4.1%
- AMIHUD_RULE: CAGR +2.7%; MDD -40.8%; Sharpe 0.31; ann.turn 9.99x; worst-phase CAGR -7.3%
- ACT5_RULE: CAGR +2.5%; MDD -40.1%; Sharpe 0.30; ann.turn 11.05x; worst-phase CAGR -6.0%
- CF20_BASE: CAGR +2.2%; MDD -41.0%; Sharpe 0.30; ann.turn 9.97x; worst-phase CAGR -7.9%
- TURNOVER_RULE: CAGR +1.2%; MDD -41.7%; Sharpe 0.29; ann.turn 10.26x; worst-phase CAGR -4.3%

### FULL_2016_2026
- TURNOVER_RULE: CAGR +7.6%; MDD -52.4%; Sharpe 0.42; ann.turn 9.12x; worst-phase CAGR +6.4%
- TURNOVER_SIMPLE_DIAG: CAGR +7.4%; MDD -52.5%; Sharpe 0.41; ann.turn 9.10x; worst-phase CAGR +6.2%
- ACT5_RULE: CAGR +7.2%; MDD -54.0%; Sharpe 0.41; ann.turn 10.12x; worst-phase CAGR +5.9%
- AMIHUD_RULE: CAGR +6.9%; MDD -53.6%; Sharpe 0.40; ann.turn 9.02x; worst-phase CAGR +5.6%
- CF20_BASE: CAGR +6.3%; MDD -53.9%; Sharpe 0.38; ann.turn 9.01x; worst-phase CAGR +5.1%

### Incremental vs CF20 baseline — PRE_STRESS_2016_2024

- TURNOVER_RULE: median dCAGR +1.1%; CAGR better 10/10 phases; dSharpe 0.05 (10/10 better); MDD improvement +1.5% (10/10 better)
- TURNOVER_SIMPLE_DIAG: median dCAGR +0.9%; CAGR better 10/10 phases; dSharpe 0.04 (10/10 better); MDD improvement +1.4% (10/10 better)
- AMIHUD_RULE: median dCAGR +0.5%; CAGR better 10/10 phases; dSharpe 0.02 (10/10 better); MDD improvement +0.3% (10/10 better)
- ACT5_RULE: median dCAGR +0.9%; CAGR better 9/10 phases; dSharpe 0.04 (9/10 better); MDD improvement +0.1% (6/10 better)

## Interpretation guardrails

- This is a portfolio implementation test, not another cutoff search. A strategy that wins only in one phase or one stress year should not be promoted.
- Median-across-phase results are more important than the best single phase. Worst-phase CAGR/MDD are retained to expose timing dependence.
- KOSPI_EX_K200 and KOSDAQ results should be read separately before using the 50/50 combined portfolio because their liquidity mechanisms differ.
- Missing held-stock daily returns are treated as 0 for that day; the average missing-return weight is saved as a QA field.
- Exact aggregate target weights are saved strategy-by-strategy as chunked gzip CSVs; exact 20-name factor sleeves are saved compactly as one row per sleeve. Large daily NAV intermediates are also chunked with manifests.
