# Nested Regime Robustness

BASE market/liquidity KMeans K=3/4/5; factor substate tested with KMeans and a transparent TRAIN-median continuous factor-health score. No forward outcome enters classification.

## Predeclared cross-spec hypotheses

### KMEANS
- REPAIR_UP: specs=26, expected sign TRAIN 77%, 23-24 73%, TRAIN/VALID same sign 62%; median diff +7.52% -> +9.17%
- REPAIR_DOWN: specs=26, expected sign TRAIN 92%, 23-24 69%, TRAIN/VALID same sign 69%; median diff -4.48% -> -4.23%
- STRONG_RETURN: specs=13, expected sign TRAIN 77%, 23-24 62%, TRAIN/VALID same sign 69%; median diff -0.65% -> -0.22%
- STRONG_DOWNSIDE: specs=13, expected sign TRAIN 77%, 23-24 54%, TRAIN/VALID same sign 62%; median diff -0.86% -> -0.04%
### SCORE_MEDIAN
- REPAIR_UP: specs=33, expected sign TRAIN 82%, 23-24 79%, TRAIN/VALID same sign 73%; median diff +10.79% -> +15.33%
- REPAIR_DOWN: specs=33, expected sign TRAIN 76%, 23-24 27%, TRAIN/VALID same sign 27%; median diff -6.18% -> +0.00%
- STRONG_RETURN: specs=14, expected sign TRAIN 79%, 23-24 50%, TRAIN/VALID same sign 43%; median diff -0.55% -> +0.00%
- STRONG_DOWNSIDE: specs=14, expected sign TRAIN 79%, 23-24 50%, TRAIN/VALID same sign 43%; median diff -0.52% -> -0.00%

## Strongest exact TRAIN -> 2023-2024 stable relations

- SCORE_MEDIAN KOSPI_EX_K200 K5 B5/STRONG NEXT_DOWN: -13.48% -> -57.50%; nmin 28/8; base dist 1.43/1.42z, factor dist 2.52/2.76z
- SCORE_MEDIAN K200 K4 B2/REPAIR_MID NEXT_UP: +12.99% -> +35.29%; nmin 42/10; base dist 0.83/1.34z, factor dist 1.73/2.62z
- SCORE_MEDIAN K200 K5 B2/REPAIR_MID NEXT_UP: +11.42% -> +31.25%; nmin 40/10; base dist 0.85/1.21z, factor dist 1.73/2.59z
- SCORE_MEDIAN KOSPI_ALL K4 B2/REPAIR_MID NEXT_UP: +1.71% -> +27.27%; nmin 46/11; base dist 1.05/1.28z, factor dist 1.83/2.09z
- KMEANS KOSPI_ALL K5 B2/REPAIR_MID NEXT_UP: +8.42% -> +25.00%; nmin 18/8; base dist 1.51/1.08z, factor dist 3.12/4.40z
- KMEANS KOSPI_KOSDAQ_ALL K5 B2/REPAIR_MID NEXT_UP: +13.12% -> +25.00%; nmin 26/8; base dist 1.55/0.92z, factor dist 2.68/2.75z
- KMEANS KOSPI_EX_K200 K4 B2/REPAIR_MID NEXT_UP: +7.43% -> +24.18%; nmin 38/13; base dist 0.61/0.70z, factor dist 2.64/2.45z
- SCORE_MEDIAN KOSPI_KOSDAQ_ALL K5 B3/REPAIR_MID NEXT_UP: +7.37% -> +23.75%; nmin 57/16; base dist 1.07/1.62z, factor dist 1.84/2.49z
- KMEANS KOSPI_ALL K3 B2/REPAIR_MID NEXT_UP: +23.21% -> +23.46%; nmin 24/11; base dist 1.12/0.72z, factor dist 3.55/2.75z
- SCORE_MEDIAN KOSDAQ_PLUS_KOSPI_EX_K200 K5 B4/REPAIR_MID NEXT_UP: +15.67% -> +23.33%; nmin 62/17; base dist 1.77/1.84z, factor dist 2.06/2.40z
- SCORE_MEDIAN KOSDAQ K5 B3/REPAIR_MID NEXT_UP: +21.54% -> +23.31%; nmin 56/19; base dist 1.49/1.68z, factor dist 2.06/2.01z
- SCORE_MEDIAN KOSPI_KOSDAQ_ALL K3 B2/REPAIR_MID NEXT_UP: +10.79% -> +23.28%; nmin 64/17; base dist 1.26/1.20z, factor dist 1.80/2.11z
- KMEANS KOSPI_EX_K200 K3 B2/REPAIR_MID NEXT_UP: +6.35% -> +23.25%; nmin 57/22; base dist 0.77/0.64z, factor dist 2.68/2.47z
- SCORE_MEDIAN KOSDAQ K4 B3/REPAIR_MID NEXT_UP: +19.04% -> +21.76%; nmin 72/24; base dist 1.38/1.76z, factor dist 2.10/2.13z
- SCORE_MEDIAN KOSPI_EX_K200 K3 B2/REPAIR_MID NEXT_UP: +9.01% -> +21.17%; nmin 74/22; base dist 1.37/1.19z, factor dist 1.94/1.74z
- SCORE_MEDIAN KOSPI_EX_K200 K4 B2/REPAIR_MID NEXT_DOWN: -5.08% -> -20.00%; nmin 59/15; base dist 1.46/1.01z, factor dist 1.90/1.68z
- SCORE_MEDIAN KOSDAQ_PLUS_KOSPI_EX_K200 K3 B2/REPAIR_MID NEXT_UP: +20.06% -> +18.92%; nmin 72/19; base dist 1.59/1.53z, factor dist 2.10/2.30z
- KMEANS KOSPI_ALL K4 B2/REPAIR_MID NEXT_UP: +10.35% -> +18.75%; nmin 25/8; base dist 1.27/1.03z, factor dist 2.99/3.12z
- SCORE_MEDIAN KOSPI_EX_K200 K4 B2/REPAIR_MID NEXT_UP: +16.95% -> +18.25%; nmin 59/15; base dist 1.46/1.01z, factor dist 1.90/1.68z
- KMEANS KOSDAQ_PLUS_KOSPI_EX_K200 K3 B2/REPAIR_MID NEXT_UP: +20.56% -> +18.10%; nmin 59/21; base dist 1.01/1.22z, factor dist 2.48/3.08z
- KMEANS KOSDAQ_PLUS_KOSPI_EX_K200 K4 B4/STRONG NEXT_DOWN: -0.35% -> -16.67%; nmin 59/9; base dist 0.76/1.42z, factor dist 2.38/3.79z
- SCORE_MEDIAN KOSDAQ_PLUS_KOSPI_EX_K200 K4 B2/REPAIR_MID NEXT_UP: +15.15% -> +16.67%; nmin 33/8; base dist 1.31/1.43z, factor dist 1.60/2.70z
- SCORE_MEDIAN KOSPI_KOSDAQ_ALL K4 B3/REPAIR_MID NEXT_UP: +11.65% -> +16.32%; nmin 62/18; base dist 1.20/1.99z, factor dist 1.86/2.24z
- SCORE_MEDIAN KOSDAQ_PLUS_KOSPI_EX_K200 K4 B3/REPAIR_MID NEXT_UP: +13.07% -> +15.33%; nmin 68/25; base dist 1.55/1.62z, factor dist 2.08/2.04z
- KMEANS KOSDAQ_PLUS_KOSPI_EX_K200 K4 B3/REPAIR_MID NEXT_UP: +16.15% -> +15.32%; nmin 67/24; base dist 1.02/1.14z, factor dist 2.43/2.92z
- KMEANS K200 K3 B3/STRONG NEXT_DOWN: -6.70% -> -14.74%; nmin 61/19; base dist 0.82/0.52z, factor dist 2.66/2.42z
- KMEANS KOSDAQ_PLUS_KOSPI_EX_K200 K5 B4/REPAIR_MID NEXT_UP: +11.28% -> +14.73%; nmin 60/22; base dist 1.30/1.10z, factor dist 2.46/3.20z
- KMEANS KOSPI_EX_K200 K4 B2/REPAIR_MID NEXT_DOWN: -8.75% -> -14.29%; nmin 38/13; base dist 0.61/0.70z, factor dist 2.64/2.45z
- SCORE_MEDIAN KOSDAQ K4 B2/REPAIR_MID NEXT_UP: +15.60% -> +14.29%; nmin 35/9; base dist 1.08/1.45z, factor dist 1.75/2.89z
- SCORE_MEDIAN KOSDAQ K5 B2/REPAIR_MID NEXT_UP: +13.95% -> +14.29%; nmin 34/9; base dist 1.06/1.45z, factor dist 1.72/3.00z
- SCORE_MEDIAN KOSDAQ K3 B2/REPAIR_MID NEXT_DOWN: -7.79% -> -13.81%; nmin 72/18; base dist 1.32/1.60z, factor dist 2.05/2.08z
- SCORE_MEDIAN KOSDAQ_PLUS_KOSPI_EX_K200 K4 B4/STRONG NEXT_DOWN: -15.52% -> -13.64%; nmin 57/10; base dist 0.88/1.35z, factor dist 2.01/2.62z
- SCORE_MEDIAN KOSPI_EX_K200 K5 B4/REPAIR_MID NEXT_UP: -5.68% -> -13.19%; nmin 44/13; base dist 1.33/1.17z, factor dist 1.80/1.91z
- SCORE_MEDIAN KOSDAQ_PLUS_KOSPI_EX_K200 K3 B2/REPAIR_MID NEXT_DOWN: -9.99% -> -13.09%; nmin 72/19; base dist 1.59/1.53z, factor dist 2.10/2.30z
- KMEANS KOSDAQ_PLUS_KOSPI_EX_K200 K4 B3/REPAIR_MID NEXT_DOWN: -4.99% -> -12.90%; nmin 67/24; base dist 1.02/1.14z, factor dist 2.43/2.92z
- KMEANS KOSPI_ALL K4 B3/REPAIR_MID NEXT_DOWN: -7.62% -> -12.90%; nmin 45/21; base dist 1.19/1.00z, factor dist 2.85/3.10z
- KMEANS KOSPI_EX_K200 K5 B3/REPAIR_MID NEXT_DOWN: -6.91% -> -12.50%; nmin 43/19; base dist 0.68/1.08z, factor dist 2.43/2.33z
- KMEANS KOSDAQ_PLUS_KOSPI_EX_K200 K5 B4/REPAIR_MID NEXT_DOWN: -3.97% -> -12.00%; nmin 60/22; base dist 1.30/1.10z, factor dist 2.46/3.20z
- KMEANS K200 K3 B2/REPAIR_MID NEXT_UP: +16.91% -> +11.65%; nmin 39/11; base dist 0.97/0.79z, factor dist 2.89/2.72z
- SCORE_MEDIAN KOSDAQ K3 B2/REPAIR_MID NEXT_UP: +21.08% -> +11.59%; nmin 72/18; base dist 1.32/1.60z, factor dist 2.05/2.08z

## 2025/2026 stress sign retention

- STRESS_2025 NEXT_UP: sign retained vs 2023-24 in 94% of 32 eligible specs
- STRESS_2025 NEXT_DOWN: sign retained vs 2023-24 in 62% of 32 eligible specs
- STRESS_2025 MKT_FWD_20D: sign retained vs 2023-24 in 44% of 32 eligible specs
- STRESS_2025 MKT_FWD_DD20: sign retained vs 2023-24 in 31% of 32 eligible specs

## Interpretation

- Structural evidence requires agreement across BASE K and factor-split definitions, not one chosen cluster solution.
- REPAIR_MID transition effects are the main contemporaneous-regime hypothesis; STRONG-state return/downside reversal is a separate maturity/crowding hypothesis.
- Stress years are not expected to preserve all signs; systematic breaks are themselves regime-dependence evidence.

