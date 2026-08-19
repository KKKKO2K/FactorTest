# Mixed OPFY1+CF20 — Exact Daily-NAV Regime Overlay Audit

- Frozen TRAIN factor-breadth thresholds: q1=0.500, q2=0.625.
- FACTOR_20D is the fraction of available canonical factor long-short sleeves with positive compounded return over four 5D periods; at least five factors are required.
- A signal dated t is applied after the close of t, so it affects portfolio returns from the next trading day. No forward outcome enters the rule.
- Net30/Net60 use the finalist sleeve net returns and additionally charge the same bps on allocator turnover between the risky sleeve and cash.
- While a target is active, allocation is refreshed on regime signal dates; between signal dates the risky/cash weights are allowed to drift.

Policies:
- ALWAYS_100: finalist sleeve fully invested.
- F_LOW_HALF: legacy benchmark; 50% when nested factor_substate is F_LOW.
- FB20_HIGH_HALF: 50% when FACTOR_20D >= frozen TRAIN q2.
- CRASH_GUARD_ONLY: 0% only when base state is B1/B2 and Revision family state is W-/R-.
- FB20_HALF_PLUS_CRASH0: Breadth HIGH -> 50%; crash guard overrides to 0%; otherwise 100%.

## TRAIN_2016_2022 — median across 10 phases

- ALWAYS_100: CAGR +6.83%; Sharpe 0.40; MDD -49.12%; turnover 13.80x; avg target 100.0%; positive phases 10/10
- F_LOW_HALF: CAGR +1.91%; Sharpe 0.20; MDD -40.84%; turnover 17.05x; avg target 73.2%; positive phases 9/10
- FB20_HIGH_HALF: CAGR +2.13%; Sharpe 0.21; MDD -47.03%; turnover 17.58x; avg target 75.8%; positive phases 9/10
- CRASH_GUARD_ONLY: CAGR +4.26%; Sharpe 0.30; MDD -47.13%; turnover 16.99x; avg target 89.2%; positive phases 10/10
- FB20_HALF_PLUS_CRASH0: CAGR +0.63%; Sharpe 0.13; MDD -43.21%; turnover 18.56x; avg target 68.2%; positive phases 6/10

## OOS_2023_2024 — median across 10 phases

- ALWAYS_100: CAGR +2.43%; Sharpe 0.22; MDD -28.44%; turnover 14.56x; avg target 100.0%; positive phases 7/10
- F_LOW_HALF: CAGR +0.68%; Sharpe 0.12; MDD -18.71%; turnover 16.58x; avg target 68.4%; positive phases 6/10
- FB20_HIGH_HALF: CAGR +1.15%; Sharpe 0.16; MDD -20.36%; turnover 17.24x; avg target 79.7%; positive phases 6/10
- CRASH_GUARD_ONLY: CAGR +1.74%; Sharpe 0.19; MDD -23.33%; turnover 17.08x; avg target 91.8%; positive phases 7/10
- FB20_HALF_PLUS_CRASH0: CAGR -1.38%; Sharpe 0.02; MDD -19.12%; turnover 18.60x; avg target 74.5%; positive phases 3/10

## PRE_STRESS_2016_2024 — median across 10 phases

- ALWAYS_100: CAGR +5.79%; Sharpe 0.36; MDD -49.12%; turnover 13.95x; avg target 100.0%; positive phases 10/10
- F_LOW_HALF: CAGR +1.30%; Sharpe 0.16; MDD -40.84%; turnover 16.96x; avg target 72.1%; positive phases 10/10
- FB20_HIGH_HALF: CAGR +2.04%; Sharpe 0.20; MDD -47.03%; turnover 17.49x; avg target 76.6%; positive phases 8/10
- CRASH_GUARD_ONLY: CAGR +3.51%; Sharpe 0.27; MDD -47.13%; turnover 17.00x; avg target 89.8%; positive phases 10/10
- FB20_HALF_PLUS_CRASH0: CAGR +0.18%; Sharpe 0.10; MDD -43.92%; turnover 18.56x; avg target 69.6%; positive phases 6/10

## BULL_2025 — median across 10 phases

- ALWAYS_100: CAGR +67.60%; Sharpe 2.35; MDD -18.43%; turnover 15.14x; avg target 100.0%; positive phases 10/10
- F_LOW_HALF: CAGR +53.74%; Sharpe 2.34; MDD -12.29%; turnover 19.33x; avg target 81.0%; positive phases 10/10
- FB20_HIGH_HALF: CAGR +34.71%; Sharpe 1.67; MDD -18.43%; turnover 17.06x; avg target 77.3%; positive phases 10/10
- CRASH_GUARD_ONLY: CAGR +49.06%; Sharpe 1.97; MDD -14.32%; turnover 19.42x; avg target 93.8%; positive phases 10/10
- FB20_HALF_PLUS_CRASH0: CAGR +23.57%; Sharpe 1.34; MDD -14.19%; turnover 19.28x; avg target 72.1%; positive phases 10/10

## YTD_2026 — median across 10 phases

- ALWAYS_100: CAGR -4.09%; Sharpe 0.20; MDD -43.97%; turnover 15.92x; avg target 100.0%; positive phases 0/10
- F_LOW_HALF: CAGR -4.07%; Sharpe 0.14; MDD -29.84%; turnover 17.02x; avg target 75.5%; positive phases 0/10
- FB20_HIGH_HALF: CAGR +22.24%; Sharpe 0.75; MDD -26.26%; turnover 17.05x; avg target 66.3%; positive phases 10/10
- CRASH_GUARD_ONLY: CAGR +24.81%; Sharpe 0.74; MDD -16.98%; turnover 18.56x; avg target 63.3%; positive phases 10/10
- FB20_HALF_PLUS_CRASH0: CAGR +35.32%; Sharpe 1.23; MDD -8.76%; turnover 15.54x; avg target 44.6%; positive phases 10/10

## Incremental vs ALWAYS_100 — NET60

### TRAIN_2016_2022
- F_LOW_HALF: dCAGR -5.04%; dSharpe -0.21; dMDD +7.33%; dTurnover +3.30x; better CAGR 0/10, better MDD 10/10
- FB20_HIGH_HALF: dCAGR -5.11%; dSharpe -0.20; dMDD +0.93%; dTurnover +3.78x; better CAGR 0/10, better MDD 9/10
- CRASH_GUARD_ONLY: dCAGR -2.92%; dSharpe -0.12; dMDD +1.75%; dTurnover +3.18x; better CAGR 0/10, better MDD 9/10
- FB20_HALF_PLUS_CRASH0: dCAGR -6.17%; dSharpe -0.26; dMDD +5.77%; dTurnover +4.78x; better CAGR 0/10, better MDD 10/10

### OOS_2023_2024
- F_LOW_HALF: dCAGR -1.10%; dSharpe -0.09; dMDD +10.03%; dTurnover +2.01x; better CAGR 2/10, better MDD 10/10
- FB20_HIGH_HALF: dCAGR -0.55%; dSharpe -0.03; dMDD +9.65%; dTurnover +2.65x; better CAGR 2/10, better MDD 10/10
- CRASH_GUARD_ONLY: dCAGR -0.30%; dSharpe -0.02; dMDD +5.97%; dTurnover +2.69x; better CAGR 3/10, better MDD 10/10
- FB20_HALF_PLUS_CRASH0: dCAGR -2.94%; dSharpe -0.17; dMDD +9.42%; dTurnover +4.08x; better CAGR 1/10, better MDD 10/10

### PRE_STRESS_2016_2024
- F_LOW_HALF: dCAGR -4.34%; dSharpe -0.18; dMDD +7.33%; dTurnover +3.01x; better CAGR 0/10, better MDD 10/10
- FB20_HIGH_HALF: dCAGR -3.91%; dSharpe -0.17; dMDD +0.93%; dTurnover +3.53x; better CAGR 0/10, better MDD 9/10
- CRASH_GUARD_ONLY: dCAGR -2.22%; dSharpe -0.09; dMDD +1.75%; dTurnover +3.05x; better CAGR 0/10, better MDD 9/10
- FB20_HALF_PLUS_CRASH0: dCAGR -5.27%; dSharpe -0.24; dMDD +4.89%; dTurnover +4.61x; better CAGR 0/10, better MDD 10/10

### BULL_2025
- F_LOW_HALF: dCAGR -11.84%; dSharpe +0.03; dMDD +6.02%; dTurnover +3.97x; better CAGR 0/10, better MDD 10/10
- FB20_HIGH_HALF: dCAGR -31.24%; dSharpe -0.64; dMDD -0.00%; dTurnover +1.92x; better CAGR 0/10, better MDD 2/10
- CRASH_GUARD_ONLY: dCAGR -16.74%; dSharpe -0.29; dMDD +4.24%; dTurnover +3.72x; better CAGR 0/10, better MDD 10/10
- FB20_HALF_PLUS_CRASH0: dCAGR -42.32%; dSharpe -0.90; dMDD +4.31%; dTurnover +3.70x; better CAGR 0/10, better MDD 10/10

### YTD_2026
- F_LOW_HALF: dCAGR +0.72%; dSharpe -0.09; dMDD +14.07%; dTurnover +1.50x; better CAGR 6/10, better MDD 10/10
- FB20_HIGH_HALF: dCAGR +31.14%; dSharpe +0.57; dMDD +17.73%; dTurnover +1.21x; better CAGR 10/10, better MDD 10/10
- CRASH_GUARD_ONLY: dCAGR +30.06%; dSharpe +0.53; dMDD +26.20%; dTurnover +3.24x; better CAGR 10/10, better MDD 10/10
- FB20_HALF_PLUS_CRASH0: dCAGR +44.89%; dSharpe +1.09; dMDD +34.95%; dTurnover +0.16x; better CAGR 10/10, better MDD 10/10

## 2026 signal chronology

- 2026-04-07: breadth 37.5% (LOW); B=B2; Revision=R-; F=F_LOW; FB-half target=1.0; combined target=0.0
- 2026-04-14: breadth 62.5% (HIGH); B=B3; Revision=R+; F=F_LOW; FB-half target=0.5; combined target=0.5
- 2026-04-21: breadth 37.5% (LOW); B=B4; Revision=N+; F=F_LOW; FB-half target=1.0; combined target=1.0
- 2026-04-28: breadth 62.5% (HIGH); B=B4; Revision=W+; F=F_HIGH; FB-half target=0.5; combined target=0.5
- 2026-05-07: breadth 62.5% (HIGH); B=B4; Revision=W+; F=F_HIGH; FB-half target=0.5; combined target=0.5
- 2026-05-14: breadth 75.0% (HIGH); B=B4; Revision=W+; F=F_HIGH; FB-half target=0.5; combined target=0.5
- 2026-05-21: breadth 75.0% (HIGH); B=B2; Revision=W-; F=F_HIGH; FB-half target=0.5; combined target=0.0
- 2026-05-29: breadth 75.0% (HIGH); B=B2; Revision=W-; F=F_LOW; FB-half target=0.5; combined target=0.0
- 2026-06-08: breadth 75.0% (HIGH); B=B2; Revision=R-; F=F_LOW; FB-half target=0.5; combined target=0.0
- 2026-06-15: breadth 75.0% (HIGH); B=B2; Revision=N-; F=F_LOW; FB-half target=0.5; combined target=0.5
- 2026-06-22: breadth 50.0% (LOW); B=B2; Revision=R-; F=F_LOW; FB-half target=1.0; combined target=0.0
- 2026-06-29: breadth 75.0% (HIGH); B=B2; Revision=R-; F=F_LOW; FB-half target=0.5; combined target=0.0

## Guardrails

- 2023+ is robustness/stress evidence rather than pristine untouched OOS because later observations informed prior research iterations.
- The crash guard uses the Revision family state from the frozen nested/action-state panel, not an OPFY1-only state.
- This audit tests the frozen 62.5%-style breadth rule without optimizing persistence, alternative cutoffs, or exposure levels on 2026.
- A production PASS requires improvement that is not concentrated solely in 2026 and that survives Net30/Net60 and phase consistency checks.
