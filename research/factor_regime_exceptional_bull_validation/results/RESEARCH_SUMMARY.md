# 2025-2026 Exceptional Bull Regime Validation

Data through: 2026-08-04.
Purpose: separate 2023-2024 normal post-discovery validation from 2025 and 2026 YTD exceptional-bull behavior, and test whether factor-state effects survive conditioning on prior market strength.
All family states use the existing Q33 thresholds fit on 2016-2022 and frozen thereafter. 2023+ remains post-discovery validation, not pristine OOS.
20D forward returns overlap across 5D state dates; reported means are descriptive. Pair cells require n>=5; two-sided confirmation contrasts retain n>=8 per side.

## 1. Was 2025-2026 mechanically different?

- K200: NORMAL_2023_2024: prior60 +1.04%, next20 +0.26%, high-prior60 share 38% (n=97); EXCEPTIONAL_2025: prior60 +12.83%, next20 +6.08%, high-prior60 share 73% (n=49); EXCEPTIONAL_2026_YTD: prior60 +39.33%, next20 +6.77%, high-prior60 share 100% (n=25); EXCEPTIONAL_2025_2026: prior60 +21.78%, next20 +6.31%, high-prior60 share 82% (n=74)
- KOSPI_ALL: NORMAL_2023_2024: prior60 +1.11%, next20 +0.29%, high-prior60 share 38% (n=97); EXCEPTIONAL_2025: prior60 +12.34%, next20 +5.81%, high-prior60 share 73% (n=49); EXCEPTIONAL_2026_YTD: prior60 +37.64%, next20 +6.40%, high-prior60 share 100% (n=25); EXCEPTIONAL_2025_2026: prior60 +20.89%, next20 +6.01%, high-prior60 share 82% (n=74)
- KOSPI_EX_K200: NORMAL_2023_2024: prior60 +1.72%, next20 +0.56%, high-prior60 share 32% (n=97); EXCEPTIONAL_2025: prior60 +7.08%, next20 +2.47%, high-prior60 share 45% (n=49); EXCEPTIONAL_2026_YTD: prior60 +9.93%, next20 -0.02%, high-prior60 share 64% (n=25); EXCEPTIONAL_2025_2026: prior60 +8.04%, next20 +1.63%, high-prior60 share 51% (n=74)
- KOSDAQ: NORMAL_2023_2024: prior60 +0.66%, next20 +0.22%, high-prior60 share 42% (n=97); EXCEPTIONAL_2025: prior60 +6.24%, next20 +2.91%, high-prior60 share 67% (n=49); EXCEPTIONAL_2026_YTD: prior60 +9.60%, next20 -3.26%, high-prior60 share 72% (n=25); EXCEPTIONAL_2025_2026: prior60 +7.38%, next20 +0.83%, high-prior60 share 69% (n=74)

## 2. W+/W+ confirmation: raw return vs incremental return

The key distinction is raw next-20D return versus excess over the same-period unconditional market return. A large raw return with little excess is mostly bull-regime exposure, not incremental factor-state information.

### K200
- NORMAL_2023_2024: 5/6 family pairs available; median W+/W+ next20 -0.02%; median excess vs unconditional -0.29%; positive incremental pairs 2/5.
- EXCEPTIONAL_2025_2026: 6/6 family pairs available; median W+/W+ next20 +9.48%; median excess vs unconditional +3.16%; positive incremental pairs 6/6.
  - MOMENTUM_X_REVISION: 2023-24 raw -0.02%, excess -0.29%, n=19; 2025-26 raw +9.58%, excess +3.27%, n=29
  - REVISION_X_FLOW: 2023-24 raw +0.87%, excess +0.61%, n=12; 2025-26 raw +8.26%, excess +1.95%, n=29
  - MOMENTUM_X_FLOW: 2023-24 raw +0.56%, excess +0.30%, n=12; 2025-26 raw +9.37%, excess +3.06%, n=22
### KOSPI_ALL
- NORMAL_2023_2024: 5/6 family pairs available; median W+/W+ next20 +0.74%; median excess vs unconditional +0.46%; positive incremental pairs 4/5.
- EXCEPTIONAL_2025_2026: 6/6 family pairs available; median W+/W+ next20 +9.61%; median excess vs unconditional +3.60%; positive incremental pairs 5/6.
  - MOMENTUM_X_REVISION: 2023-24 raw +1.30%, excess +1.01%, n=16; 2025-26 raw +10.33%, excess +4.32%, n=28
  - REVISION_X_FLOW: 2023-24 raw +1.43%, excess +1.14%, n=12; 2025-26 raw +7.62%, excess +1.61%, n=25
  - MOMENTUM_X_FLOW: 2023-24 raw +0.74%, excess +0.46%, n=17; 2025-26 raw +8.90%, excess +2.89%, n=19
### KOSPI_EX_K200
- NORMAL_2023_2024: 4/6 family pairs available; median W+/W+ next20 +1.05%; median excess vs unconditional +0.49%; positive incremental pairs 3/4.
- EXCEPTIONAL_2025_2026: 6/6 family pairs available; median W+/W+ next20 +0.44%; median excess vs unconditional -1.19%; positive incremental pairs 2/6.
  - MOMENTUM_X_REVISION: 2023-24 raw +1.54%, excess +0.98%, n=17; 2025-26 raw +0.44%, excess -1.19%, n=19
  - MOMENTUM_X_FLOW: 2023-24 raw +0.92%, excess +0.36%, n=20; 2025-26 raw -1.48%, excess -3.11%, n=15
  - REVISION_X_FLOW: 2023-24 raw +1.19%, excess +0.63%, n=14; 2025-26 raw -0.06%, excess -1.69%, n=18
### KOSDAQ
- NORMAL_2023_2024: 5/6 family pairs available; median W+/W+ next20 +0.82%; median excess vs unconditional +0.60%; positive incremental pairs 3/5.
- EXCEPTIONAL_2025_2026: 3/6 family pairs available; median W+/W+ next20 +1.38%; median excess vs unconditional +0.56%; positive incremental pairs 2/3.
  - MOMENTUM_X_REVISION: 2023-24 raw -0.92%, excess -1.13%, n=13; 2025-26 raw +0.21%, excess -0.61%, n=22
  - REVISION_X_FLOW: 2023-24 raw +3.11%, excess +2.90%, n=5; 2025-26 raw +1.46%, excess +0.64%, n=23
  - MOMENTUM_X_FLOW: 2023-24 raw -0.67%, excess -0.88%, n=6; 2025-26 raw +1.38%, excess +0.56%, n=19

## 3. Does W+/W+ add information after conditioning on prior 60D market state?

- K200 NORMAL_2023_2024: MID: median incremental +1.50% across 4 pairs; HIGH: median incremental -1.89% across 1 pairs
- K200 EXCEPTIONAL_2025_2026: HIGH: median incremental +3.04% across 6 pairs
- KOSPI_ALL NORMAL_2023_2024: MID: median incremental +1.40% across 3 pairs; HIGH: median incremental +0.90% across 2 pairs
- KOSPI_ALL EXCEPTIONAL_2025_2026: HIGH: median incremental +3.17% across 5 pairs
- KOSPI_EX_K200 NORMAL_2023_2024: MID: median incremental +2.67% across 3 pairs; HIGH: median incremental -1.53% across 3 pairs
- KOSPI_EX_K200 EXCEPTIONAL_2025_2026: MID: median incremental +0.50% across 3 pairs; HIGH: median incremental -3.20% across 5 pairs
- KOSDAQ NORMAL_2023_2024: MID: median incremental +2.75% across 1 pairs; HIGH: median incremental -2.04% across 1 pairs
- KOSDAQ EXCEPTIONAL_2025_2026: HIGH: median incremental -2.77% across 3 pairs

## 4. Breadth decomposition by period

- K200 RELATIVE_WORKING_BREADTH: 2023-24 H-L -0.99% (n 42/37); 2025-26 H-L -4.46% (n 52/9)
- K200 ABS_CONFIRMED_BREADTH: 2023-24 H-L -2.19% (n 39/42); 2025-26 H-L +2.37% (n 53/16)
- KOSPI_ALL RELATIVE_WORKING_BREADTH: 2023-24 H-L +0.59% (n 45/38); 2025-26 H-L -3.28% (n 49/13)
- KOSPI_ALL ABS_CONFIRMED_BREADTH: 2023-24 H-L -1.68% (n 39/37); 2025-26 H-L +3.41% (n 49/20)
- KOSPI_ALL DEFENSIVE_WORKING_BREADTH: 2023-24 H-L +1.99% (n 34/63); 2025-26 H-L -7.21% (n 20/54)
- KOSPI_EX_K200 RELATIVE_WORKING_BREADTH: 2023-24 H-L +0.35% (n 42/40); 2025-26 H-L -3.98% (n 33/26)
- KOSPI_EX_K200 ABS_CONFIRMED_BREADTH: 2023-24 H-L -1.41% (n 37/39); 2025-26 H-L -4.39% (n 34/25)
- KOSPI_EX_K200 DEFENSIVE_WORKING_BREADTH: 2023-24 H-L +1.29% (n 38/59); 2025-26 H-L -1.02% (n 20/54)
- KOSDAQ RELATIVE_WORKING_BREADTH: 2023-24 H-L +0.10% (n 39/45); 2025-26 H-L -4.59% (n 37/24)
- KOSDAQ ABS_CONFIRMED_BREADTH: 2023-24 H-L -0.89% (n 28/50); 2025-26 H-L +4.02% (n 39/17)
- KOSDAQ DEFENSIVE_WORKING_BREADTH: 2023-24 H-L +1.18% (n 38/59); 2025-26 H-L -6.87% (n 17/57)

## 5. Generalized leader rotation, de-duplicated to one market event

Previous leader summaries counted alternative families as separate rows. Here market timing uses one observation per date x universe x leader; alternative-family returns are averaged only within the selected event regime.

- K200 NORMAL_2023_2024: all breaks n=5, next20 +1.00%, prior60 +3.90%; DEFENSIVE_ROTATION n=3 next20 +2.96% alt+20 +7.99%
- KOSPI_ALL NORMAL_2023_2024: all breaks n=10, next20 +1.48%, prior60 +2.73%; GENUINE_ROTATION n=4 next20 +2.16% alt+20 +2.93%; DEFENSIVE_ROTATION n=3 next20 +3.30% alt+20 +4.43%; NO_CLEAR_ROTATION n=3 next20 -1.24% alt+20 +1.67%
- KOSPI_ALL EXCEPTIONAL_2025_2026: all breaks n=3, next20 -16.68%, prior60 +49.43%
- KOSPI_EX_K200 NORMAL_2023_2024: all breaks n=5, next20 +0.39%, prior60 +2.37%
- KOSDAQ NORMAL_2023_2024: all breaks n=6, next20 +1.78%, prior60 +7.48%; DEFENSIVE_ROTATION n=6 next20 +1.78% alt+20 +2.44%

## 6. Interpretation rules

- Treat 2025-2026 as an exceptional-bull stress regime, not as part of the normal validation average.
- For W+/W+ and breadth, prioritize incremental return versus same-period unconditional return and same prior-60D market bin, not raw return.
- If a relation exists only in 2025-2026 or disappears after prior-market conditioning, classify it as regime amplification / coincident confirmation rather than a general market-timing signal.
- If a relation remains in 2023-2024 and within comparable prior-market bins, it is a stronger candidate for structural factor-state information.
- Leader-rotation market timing must use unique leader-break events; alternative rows are appropriate for factor-allocation analysis, not independent market observations.

