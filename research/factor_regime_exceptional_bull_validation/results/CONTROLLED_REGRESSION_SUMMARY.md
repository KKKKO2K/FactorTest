# Continuous Market-Strength Controlled Regressions

Sample: 2023 onward only. Baseline regime is 2023-2024; 2025 and 2026 have separate level and signal-interaction dummies.
Controls: trailing 20D and trailing 60D same-universe market return. Outcome: next 20D same-universe market return.
Standard errors: HAC/Newey-West with 3 lags, reflecting approximately four overlapping 5D state observations in a 20D forward return.
W+/W+ pair coefficients are incremental versus all other pair states after controls. Breadth coefficients are per +25 percentage points.

## W+/W+ pair effect after continuous controls

- K200: median across 6 pairs — 2023-24 -0.48%; 2025 +0.28%; 2026 +4.81%. Positive pairs: 3/6, 4/6, 5/6.
  - MOMENTUM_X_FLOW: 23-24 +0.77% (t=+0.55); 2025 +0.20% (t=+0.06); 2026 +5.41% (t=+1.15)
  - MOMENTUM_X_REVISION: 23-24 +0.61% (t=+0.39); 2025 +0.36% (t=+0.10); 2026 +8.91% (t=+1.61)
  - MOMENTUM_X_VALUE: 23-24 -1.57% (t=-0.80); 2025 +5.29% (t=+2.00); 2026 -3.67% (t=-0.39)
  - REVISION_X_FLOW: 23-24 +1.12% (t=+0.89); 2025 -0.12% (t=-0.04); 2026 +4.20% (t=+0.83)
  - REVISION_X_VALUE: 23-24 -2.93% (t=-1.86); 2025 +3.57% (t=+1.43); 2026 +6.80% (t=+0.95)
  - VALUE_X_FLOW: 23-24 -1.80% (t=-1.49); 2025 -1.62% (t=-0.44); 2026 +3.56% (t=+0.38)
- KOSPI_ALL: median across 6 pairs — 2023-24 +0.77%; 2025 +2.22%; 2026 +2.45%. Positive pairs: 5/6, 5/6, 6/6.
  - MOMENTUM_X_FLOW: 23-24 +1.18% (t=+0.94); 2025 +2.26% (t=+0.74); 2026 +2.45% (t=+0.41)
  - MOMENTUM_X_REVISION: 23-24 +2.31% (t=+2.12); 2025 +2.18% (t=+0.76); 2026 +13.87% (t=+2.72)
  - MOMENTUM_X_VALUE: 23-24 +0.37% (t=+0.32); 2025 +4.18% (t=+1.68); 2026 +0.37% (t=+0.32)
  - REVISION_X_FLOW: 23-24 +2.22% (t=+1.81); 2025 +1.88% (t=+0.69); 2026 +2.45% (t=+0.42)
  - REVISION_X_VALUE: 23-24 -2.20% (t=-1.07); 2025 +4.41% (t=+2.04); 2026 +25.74% (t=+4.97)
  - VALUE_X_FLOW: 23-24 +0.17% (t=+0.12); 2025 -3.00% (t=-0.64); 2026 +0.17% (t=+0.12)
- KOSPI_EX_K200: median across 5 pairs — 2023-24 +1.12%; 2025 +0.89%; 2026 -5.95%. Positive pairs: 4/5, 5/5, 1/5.
  - MOMENTUM_X_FLOW: 23-24 +0.56% (t=+0.43); 2025 +1.10% (t=+0.46); 2026 -14.73% (t=-3.92)
  - MOMENTUM_X_REVISION: 23-24 +1.65% (t=+1.22); 2025 +0.67% (t=+0.34); 2026 -5.95% (t=-0.91)
  - REVISION_X_FLOW: 23-24 +1.12% (t=+0.69); 2025 +0.89% (t=+0.39); 2026 -10.13% (t=-1.98)
  - REVISION_X_VALUE: 23-24 +3.27% (t=+3.16); 2025 +4.96% (t=+2.18); 2026 +1.78% (t=+0.47)
  - VALUE_X_FLOW: 23-24 -1.02% (t=-0.43); 2025 +0.04% (t=+0.01); 2026 -2.21% (t=-0.49)
- KOSDAQ: median across 3 pairs — 2023-24 -0.85%; 2025 +1.34%; 2026 -2.34%. Positive pairs: 1/3, 3/3, 1/3.
  - MOMENTUM_X_FLOW: 23-24 -0.85% (t=-0.49); 2025 +1.34% (t=+0.77); 2026 +1.57% (t=+0.34)
  - MOMENTUM_X_REVISION: 23-24 -1.62% (t=-0.99); 2025 +1.31% (t=+0.70); 2026 -6.04% (t=-1.21)
  - REVISION_X_FLOW: 23-24 +3.68% (t=+1.52); 2025 +2.27% (t=+1.10); 2026 -2.34% (t=-0.47)

## Breadth effect after continuous controls

- K200 RELATIVE_WORKING_BREADTH per +25pp: 23-24 -0.90% (t=-1.28); 2025 -0.67% (t=-0.45); 2026 +2.58% (t=+0.39)
- K200 ABS_CONFIRMED_BREADTH per +25pp: 23-24 -0.42% (t=-0.49); 2025 +1.28% (t=+1.19); 2026 +6.14% (t=+1.97)
- K200 DEFENSIVE_WORKING_BREADTH per +25pp: 23-24 -0.75% (t=-0.93); 2025 -4.02% (t=-2.43); 2026 -4.46% (t=-1.11)
- KOSPI_ALL RELATIVE_WORKING_BREADTH per +25pp: 23-24 -0.41% (t=-0.59); 2025 -0.99% (t=-0.49); 2026 +4.20% (t=+1.51)
- KOSPI_ALL ABS_CONFIRMED_BREADTH per +25pp: 23-24 +0.02% (t=+0.02); 2025 +1.10% (t=+0.84); 2026 +5.73% (t=+2.80)
- KOSPI_ALL DEFENSIVE_WORKING_BREADTH per +25pp: 23-24 -0.73% (t=-0.81); 2025 -2.69% (t=-1.76); 2026 -5.63% (t=-1.49)
- KOSPI_EX_K200 RELATIVE_WORKING_BREADTH per +25pp: 23-24 +0.11% (t=+0.19); 2025 +1.22% (t=+1.60); 2026 -7.72% (t=-4.24)
- KOSPI_EX_K200 ABS_CONFIRMED_BREADTH per +25pp: 23-24 -0.30% (t=-0.43); 2025 +0.16% (t=+0.15); 2026 -3.49% (t=-1.10)
- KOSPI_EX_K200 DEFENSIVE_WORKING_BREADTH per +25pp: 23-24 -0.32% (t=-0.32); 2025 +0.79% (t=+0.86); 2026 -5.97% (t=-2.47)
- KOSDAQ RELATIVE_WORKING_BREADTH per +25pp: 23-24 +0.34% (t=+0.40); 2025 +1.23% (t=+1.36); 2026 -9.55% (t=-3.59)
- KOSDAQ ABS_CONFIRMED_BREADTH per +25pp: 23-24 -0.30% (t=-0.35); 2025 +0.82% (t=+1.05); 2026 +0.65% (t=+0.20)
- KOSDAQ DEFENSIVE_WORKING_BREADTH per +25pp: 23-24 -1.21% (t=-1.25); 2025 -1.35% (t=-1.06); 2026 -9.21% (t=-3.07)

## Guardrails

- These are post-discovery controlled diagnostics, not untouched OOS estimates.
- The interaction structure tests regime dependence; it does not prove causality.
- Prefer consistency across pairs, cap tiers, calendar splits, and the earlier stratified same-prior60 comparisons over isolated t-statistics.

