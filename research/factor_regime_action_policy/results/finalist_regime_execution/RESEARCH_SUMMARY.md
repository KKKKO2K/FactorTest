# Mixed OPFY1+CF20 — Rebalance-Aligned Regime Execution Audit

This test keeps the regime signal definitions frozen and changes only execution timing.
REBAL10 policies update exposure only on the sleeve own H=10 stock-rebalance dates, using the latest signal available by that close.
The hybrid applies the crash transition to 0% immediately, but applies normal Breadth 100/50 changes only on stock-rebalance dates.
Allocator costs are still charged conservatively at the same 30/60 bps rate on exposure turnover.

## TRAIN_2016_2022 — NET60

- ALWAYS_100: CAGR +6.83%; Sharpe 0.40; MDD -49.12%; turn 13.80x (allocator 0.00x); avg target 100.0%; pos phases 10/10
- F_LOW_HALF_REBAL10: CAGR +1.68%; Sharpe 0.18; MDD -38.89%; turn 14.88x (allocator 4.72x); avg target 73.3%; pos phases 10/10
- FB20_HIGH_HALF_REBAL10: CAGR +4.43%; Sharpe 0.33; MDD -47.24%; turn 15.55x (allocator 5.05x); avg target 75.9%; pos phases 9/10
- CRASH_GUARD_REBAL10: CAGR +4.48%; Sharpe 0.31; MDD -48.17%; turn 15.73x (allocator 3.38x); avg target 89.2%; pos phases 10/10
- FB20_HALF_REBAL10_CRASH_IMMEDIATE: CAGR +2.44%; Sharpe 0.23; MDD -46.71%; turn 15.96x (allocator 7.09x); avg target 65.5%; pos phases 9/10

## OOS_2023_2024 — NET60

- ALWAYS_100: CAGR +2.43%; Sharpe 0.22; MDD -28.44%; turn 14.56x (allocator 0.00x); avg target 100.0%; pos phases 7/10
- F_LOW_HALF_REBAL10: CAGR +1.56%; Sharpe 0.18; MDD -18.89%; turn 13.76x (allocator 3.68x); avg target 68.1%; pos phases 7/10
- FB20_HIGH_HALF_REBAL10: CAGR -2.23%; Sharpe -0.02; MDD -23.15%; turn 15.33x (allocator 3.68x); avg target 79.2%; pos phases 2/10
- CRASH_GUARD_REBAL10: CAGR +4.73%; Sharpe 0.33; MDD -23.06%; turn 15.96x (allocator 2.32x); avg target 92.7%; pos phases 9/10
- FB20_HALF_REBAL10_CRASH_IMMEDIATE: CAGR -1.02%; Sharpe 0.04; MDD -19.77%; turn 15.77x (allocator 5.21x); avg target 72.7%; pos phases 4/10

## BULL_2025 — NET60

- ALWAYS_100: CAGR +67.60%; Sharpe 2.35; MDD -18.43%; turn 15.14x (allocator 0.00x); avg target 100.0%; pos phases 10/10
- F_LOW_HALF_REBAL10: CAGR +50.06%; Sharpe 2.23; MDD -14.10%; turn 16.31x (allocator 4.20x); avg target 81.7%; pos phases 10/10
- FB20_HIGH_HALF_REBAL10: CAGR +35.82%; Sharpe 1.72; MDD -18.43%; turn 15.70x (allocator 3.71x); avg target 77.8%; pos phases 10/10
- CRASH_GUARD_REBAL10: CAGR +43.22%; Sharpe 1.72; MDD -18.54%; turn 16.56x (allocator 2.60x); avg target 91.9%; pos phases 10/10
- FB20_HALF_REBAL10_CRASH_IMMEDIATE: CAGR +18.33%; Sharpe 1.14; MDD -14.41%; turn 16.58x (allocator 6.58x); avg target 68.2%; pos phases 10/10

## YTD_2026 — NET60

- ALWAYS_100: CAGR -4.09%; Sharpe 0.20; MDD -43.97%; turn 15.92x (allocator 0.00x); avg target 100.0%; pos phases 0/10
- F_LOW_HALF_REBAL10: CAGR -9.60%; Sharpe 0.02; MDD -31.18%; turn 16.59x (allocator 4.82x); avg target 75.5%; pos phases 3/10
- FB20_HIGH_HALF_REBAL10: CAGR +15.91%; Sharpe 0.61; MDD -26.33%; turn 15.03x (allocator 4.53x); avg target 67.0%; pos phases 10/10
- CRASH_GUARD_REBAL10: CAGR +17.33%; Sharpe 0.58; MDD -20.42%; turn 15.95x (allocator 5.14x); avg target 66.3%; pos phases 8/10
- FB20_HALF_REBAL10_CRASH_IMMEDIATE: CAGR +21.88%; Sharpe 0.87; MDD -9.51%; turn 13.01x (allocator 6.46x); avg target 41.3%; pos phases 10/10

## Incremental vs ALWAYS_100 — NET60

### TRAIN_2016_2022
- F_LOW_HALF_REBAL10: dCAGR -4.20%, dSharpe -0.17, dMDD +9.80%, dTurn +1.16x; better CAGR 0/10, better MDD 10/10
- FB20_HIGH_HALF_REBAL10: dCAGR -3.20%, dSharpe -0.11, dMDD +2.48%, dTurn +1.78x; better CAGR 2/10, better MDD 7/10
- CRASH_GUARD_REBAL10: dCAGR -2.38%, dSharpe -0.09, dMDD +0.38%, dTurn +1.94x; better CAGR 0/10, better MDD 6/10
- FB20_HALF_REBAL10_CRASH_IMMEDIATE: dCAGR -4.81%, dSharpe -0.18, dMDD +2.26%, dTurn +2.15x; better CAGR 0/10, better MDD 5/10

### OOS_2023_2024
- F_LOW_HALF_REBAL10: dCAGR -0.75%, dSharpe -0.08, dMDD +9.39%, dTurn -0.88x; better CAGR 4/10, better MDD 10/10
- FB20_HIGH_HALF_REBAL10: dCAGR -4.01%, dSharpe -0.21, dMDD +8.64%, dTurn +0.80x; better CAGR 1/10, better MDD 10/10
- CRASH_GUARD_REBAL10: dCAGR +3.43%, dSharpe +0.16, dMDD +7.32%, dTurn +1.39x; better CAGR 10/10, better MDD 10/10
- FB20_HALF_REBAL10_CRASH_IMMEDIATE: dCAGR -1.89%, dSharpe -0.12, dMDD +8.43%, dTurn +1.22x; better CAGR 1/10, better MDD 9/10

### BULL_2025
- F_LOW_HALF_REBAL10: dCAGR -14.10%, dSharpe -0.02, dMDD +4.78%, dTurn +1.37x; better CAGR 0/10, better MDD 10/10
- FB20_HIGH_HALF_REBAL10: dCAGR -29.26%, dSharpe -0.60, dMDD +0.00%, dTurn +0.57x; better CAGR 0/10, better MDD 4/10
- CRASH_GUARD_REBAL10: dCAGR -15.14%, dSharpe -0.37, dMDD -0.00%, dTurn +1.49x; better CAGR 0/10, better MDD 3/10
- FB20_HALF_REBAL10_CRASH_IMMEDIATE: dCAGR -45.58%, dSharpe -1.13, dMDD +4.12%, dTurn +1.41x; better CAGR 0/10, better MDD 10/10

### YTD_2026
- F_LOW_HALF_REBAL10: dCAGR +6.29%, dSharpe +0.06, dMDD +13.46%, dTurn +0.74x; better CAGR 7/10, better MDD 10/10
- FB20_HIGH_HALF_REBAL10: dCAGR +26.67%, dSharpe +0.53, dMDD +18.08%, dTurn -0.83x; better CAGR 10/10, better MDD 10/10
- CRASH_GUARD_REBAL10: dCAGR +22.17%, dSharpe +0.39, dMDD +22.52%, dTurn +0.93x; better CAGR 10/10, better MDD 10/10
- FB20_HALF_REBAL10_CRASH_IMMEDIATE: dCAGR +36.58%, dSharpe +0.88, dMDD +33.50%, dTurn -2.54x; better CAGR 10/10, better MDD 10/10
