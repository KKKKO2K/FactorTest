# Cross-Family Conditional Payoff Ranking

This iteration removes the need to forecast absolute family returns. The target is each family future return minus the same-date four-family average, so common market shocks are removed.

## Walk-forward ranking vs equal-weight four-family basket

### K200 — BULL_2025
- FAMILY_STATE: n=49, edge vs EW4 -0.04%/5D, beat EW4 47%, best-family accuracy 31%, absolute win 63%
- FULL_INTERACTION: n=49, edge vs EW4 -0.01%/5D, beat EW4 39%, best-family accuracy 24%, absolute win 65%
- STATIC_FAMILY: n=49, edge vs EW4 +0.20%/5D, beat EW4 49%, best-family accuracy 27%, absolute win 69%
### K200 — DISCOVERY_2016_2022
- FAMILY_STATE: n=144, edge vs EW4 +0.08%/5D, beat EW4 55%, best-family accuracy 30%, absolute win 54%
- FULL_INTERACTION: n=144, edge vs EW4 -0.10%/5D, beat EW4 48%, best-family accuracy 22%, absolute win 53%
- STATIC_FAMILY: n=144, edge vs EW4 +0.03%/5D, beat EW4 51%, best-family accuracy 24%, absolute win 53%
### K200 — NORMAL_2023_2024
- FAMILY_STATE: n=97, edge vs EW4 +0.04%/5D, beat EW4 44%, best-family accuracy 24%, absolute win 52%
- FULL_INTERACTION: n=97, edge vs EW4 +0.04%/5D, beat EW4 43%, best-family accuracy 23%, absolute win 52%
- STATIC_FAMILY: n=97, edge vs EW4 +0.05%/5D, beat EW4 49%, best-family accuracy 29%, absolute win 56%
### K200 — YTD_2026
- FAMILY_STATE: n=20, edge vs EW4 +0.53%/5D, beat EW4 65%, best-family accuracy 45%, absolute win 65%
- FULL_INTERACTION: n=20, edge vs EW4 +0.14%/5D, beat EW4 50%, best-family accuracy 35%, absolute win 60%
- STATIC_FAMILY: n=20, edge vs EW4 +0.04%/5D, beat EW4 40%, best-family accuracy 25%, absolute win 55%
### KOSDAQ — BULL_2025
- FAMILY_STATE: n=45, edge vs EW4 -0.05%/5D, beat EW4 49%, best-family accuracy 22%, absolute win 62%
- FULL_INTERACTION: n=45, edge vs EW4 +0.14%/5D, beat EW4 53%, best-family accuracy 20%, absolute win 67%
- STATIC_FAMILY: n=45, edge vs EW4 +0.20%/5D, beat EW4 56%, best-family accuracy 24%, absolute win 69%
### KOSDAQ — DISCOVERY_2016_2022
- FAMILY_STATE: n=113, edge vs EW4 +0.10%/5D, beat EW4 52%, best-family accuracy 27%, absolute win 58%
- FULL_INTERACTION: n=113, edge vs EW4 +0.15%/5D, beat EW4 57%, best-family accuracy 29%, absolute win 58%
- STATIC_FAMILY: n=113, edge vs EW4 +0.13%/5D, beat EW4 55%, best-family accuracy 31%, absolute win 58%
### KOSDAQ — NORMAL_2023_2024
- FAMILY_STATE: n=73, edge vs EW4 +0.03%/5D, beat EW4 60%, best-family accuracy 30%, absolute win 56%
- FULL_INTERACTION: n=73, edge vs EW4 +0.16%/5D, beat EW4 59%, best-family accuracy 26%, absolute win 59%
- STATIC_FAMILY: n=73, edge vs EW4 +0.13%/5D, beat EW4 58%, best-family accuracy 22%, absolute win 59%
### KOSDAQ — YTD_2026
- FAMILY_STATE: n=13, edge vs EW4 +0.44%/5D, beat EW4 54%, best-family accuracy 31%, absolute win 69%
- FULL_INTERACTION: n=13, edge vs EW4 +1.21%/5D, beat EW4 69%, best-family accuracy 54%, absolute win 77%
- STATIC_FAMILY: n=13, edge vs EW4 +0.50%/5D, beat EW4 54%, best-family accuracy 46%, absolute win 69%
### KOSDAQ_PLUS_KOSPI_EX_K200 — BULL_2025
- FAMILY_STATE: n=49, edge vs EW4 -0.14%/5D, beat EW4 43%, best-family accuracy 29%, absolute win 61%
- FULL_INTERACTION: n=49, edge vs EW4 +0.14%/5D, beat EW4 53%, best-family accuracy 37%, absolute win 63%
- STATIC_FAMILY: n=49, edge vs EW4 +0.34%/5D, beat EW4 61%, best-family accuracy 37%, absolute win 71%
### KOSDAQ_PLUS_KOSPI_EX_K200 — DISCOVERY_2016_2022
- FAMILY_STATE: n=144, edge vs EW4 +0.14%/5D, beat EW4 51%, best-family accuracy 30%, absolute win 61%
- FULL_INTERACTION: n=144, edge vs EW4 +0.14%/5D, beat EW4 51%, best-family accuracy 28%, absolute win 62%
- STATIC_FAMILY: n=144, edge vs EW4 +0.16%/5D, beat EW4 56%, best-family accuracy 30%, absolute win 62%
### KOSDAQ_PLUS_KOSPI_EX_K200 — NORMAL_2023_2024
- FAMILY_STATE: n=96, edge vs EW4 -0.03%/5D, beat EW4 50%, best-family accuracy 15%, absolute win 58%
- FULL_INTERACTION: n=96, edge vs EW4 -0.03%/5D, beat EW4 48%, best-family accuracy 24%, absolute win 57%
- STATIC_FAMILY: n=96, edge vs EW4 +0.12%/5D, beat EW4 58%, best-family accuracy 22%, absolute win 57%
### KOSDAQ_PLUS_KOSPI_EX_K200 — YTD_2026
- FAMILY_STATE: n=19, edge vs EW4 -0.28%/5D, beat EW4 47%, best-family accuracy 32%, absolute win 63%
- FULL_INTERACTION: n=19, edge vs EW4 -0.93%/5D, beat EW4 32%, best-family accuracy 11%, absolute win 58%
- STATIC_FAMILY: n=19, edge vs EW4 +0.28%/5D, beat EW4 58%, best-family accuracy 32%, absolute win 63%
### KOSPI_ALL — BULL_2025
- FAMILY_STATE: n=49, edge vs EW4 -0.16%/5D, beat EW4 41%, best-family accuracy 18%, absolute win 59%
- FULL_INTERACTION: n=49, edge vs EW4 -0.10%/5D, beat EW4 41%, best-family accuracy 24%, absolute win 65%
- STATIC_FAMILY: n=49, edge vs EW4 +0.18%/5D, beat EW4 53%, best-family accuracy 31%, absolute win 73%
### KOSPI_ALL — DISCOVERY_2016_2022
- FAMILY_STATE: n=144, edge vs EW4 +0.13%/5D, beat EW4 53%, best-family accuracy 26%, absolute win 55%
- FULL_INTERACTION: n=144, edge vs EW4 +0.05%/5D, beat EW4 53%, best-family accuracy 26%, absolute win 49%
- STATIC_FAMILY: n=144, edge vs EW4 +0.11%/5D, beat EW4 54%, best-family accuracy 25%, absolute win 55%
### KOSPI_ALL — NORMAL_2023_2024
- FAMILY_STATE: n=97, edge vs EW4 +0.05%/5D, beat EW4 45%, best-family accuracy 21%, absolute win 57%
- FULL_INTERACTION: n=97, edge vs EW4 +0.05%/5D, beat EW4 44%, best-family accuracy 20%, absolute win 56%
- STATIC_FAMILY: n=97, edge vs EW4 +0.04%/5D, beat EW4 47%, best-family accuracy 25%, absolute win 59%
### KOSPI_ALL — YTD_2026
- FAMILY_STATE: n=21, edge vs EW4 +0.40%/5D, beat EW4 52%, best-family accuracy 29%, absolute win 62%
- FULL_INTERACTION: n=21, edge vs EW4 +0.29%/5D, beat EW4 52%, best-family accuracy 33%, absolute win 62%
- STATIC_FAMILY: n=21, edge vs EW4 +0.12%/5D, beat EW4 43%, best-family accuracy 24%, absolute win 57%
### KOSPI_EX_K200 — BULL_2025
- FAMILY_STATE: n=49, edge vs EW4 +0.10%/5D, beat EW4 53%, best-family accuracy 27%, absolute win 61%
- FULL_INTERACTION: n=49, edge vs EW4 -0.01%/5D, beat EW4 51%, best-family accuracy 16%, absolute win 61%
- STATIC_FAMILY: n=49, edge vs EW4 +0.23%/5D, beat EW4 61%, best-family accuracy 24%, absolute win 65%
### KOSPI_EX_K200 — DISCOVERY_2016_2022
- FAMILY_STATE: n=117, edge vs EW4 +0.21%/5D, beat EW4 57%, best-family accuracy 35%, absolute win 56%
- FULL_INTERACTION: n=117, edge vs EW4 +0.11%/5D, beat EW4 50%, best-family accuracy 28%, absolute win 58%
- STATIC_FAMILY: n=117, edge vs EW4 +0.28%/5D, beat EW4 60%, best-family accuracy 38%, absolute win 58%
### KOSPI_EX_K200 — NORMAL_2023_2024
- FAMILY_STATE: n=91, edge vs EW4 -0.14%/5D, beat EW4 40%, best-family accuracy 22%, absolute win 49%
- FULL_INTERACTION: n=91, edge vs EW4 -0.02%/5D, beat EW4 46%, best-family accuracy 25%, absolute win 53%
- STATIC_FAMILY: n=91, edge vs EW4 +0.04%/5D, beat EW4 46%, best-family accuracy 26%, absolute win 53%
### KOSPI_EX_K200 — YTD_2026
- FAMILY_STATE: n=15, edge vs EW4 +0.45%/5D, beat EW4 53%, best-family accuracy 47%, absolute win 60%
- FULL_INTERACTION: n=15, edge vs EW4 -0.29%/5D, beat EW4 33%, best-family accuracy 27%, absolute win 60%
- STATIC_FAMILY: n=15, edge vs EW4 +0.22%/5D, beat EW4 53%, best-family accuracy 40%, absolute win 60%
### KOSPI_KOSDAQ_ALL — BULL_2025
- FAMILY_STATE: n=49, edge vs EW4 +0.08%/5D, beat EW4 55%, best-family accuracy 29%, absolute win 69%
- FULL_INTERACTION: n=49, edge vs EW4 -0.03%/5D, beat EW4 47%, best-family accuracy 24%, absolute win 67%
- STATIC_FAMILY: n=49, edge vs EW4 +0.27%/5D, beat EW4 57%, best-family accuracy 20%, absolute win 73%
### KOSPI_KOSDAQ_ALL — DISCOVERY_2016_2022
- FAMILY_STATE: n=144, edge vs EW4 +0.11%/5D, beat EW4 54%, best-family accuracy 25%, absolute win 58%
- FULL_INTERACTION: n=144, edge vs EW4 +0.10%/5D, beat EW4 56%, best-family accuracy 24%, absolute win 59%
- STATIC_FAMILY: n=144, edge vs EW4 +0.12%/5D, beat EW4 55%, best-family accuracy 24%, absolute win 59%
### KOSPI_KOSDAQ_ALL — NORMAL_2023_2024
- FAMILY_STATE: n=96, edge vs EW4 +0.09%/5D, beat EW4 52%, best-family accuracy 21%, absolute win 54%
- FULL_INTERACTION: n=96, edge vs EW4 +0.02%/5D, beat EW4 50%, best-family accuracy 20%, absolute win 55%
- STATIC_FAMILY: n=96, edge vs EW4 +0.08%/5D, beat EW4 52%, best-family accuracy 20%, absolute win 55%
### KOSPI_KOSDAQ_ALL — YTD_2026
- FAMILY_STATE: n=21, edge vs EW4 +0.46%/5D, beat EW4 48%, best-family accuracy 38%, absolute win 57%
- FULL_INTERACTION: n=21, edge vs EW4 +0.39%/5D, beat EW4 57%, best-family accuracy 48%, absolute win 62%
- STATIC_FAMILY: n=21, edge vs EW4 +0.27%/5D, beat EW4 48%, best-family accuracy 29%, absolute win 52%

## Simple controls

- K200 BULL_2025: SPREAD20_LEADER -0.07%; SPREAD60_LEADER -0.11%; TOP20_LEADER -0.01%; WPLUS -0.12%
- K200 DISCOVERY_2016_2022: SPREAD20_LEADER +0.05%; SPREAD60_LEADER -0.01%; TOP20_LEADER -0.07%; WPLUS +0.03%
- K200 NORMAL_2023_2024: SPREAD20_LEADER +0.03%; SPREAD60_LEADER -0.05%; TOP20_LEADER +0.00%; WPLUS +0.14%
- K200 YTD_2026: SPREAD20_LEADER +0.37%; SPREAD60_LEADER -0.20%; TOP20_LEADER +0.16%; WPLUS -0.11%
- KOSDAQ BULL_2025: SPREAD20_LEADER +0.13%; SPREAD60_LEADER +0.05%; TOP20_LEADER +0.02%; WPLUS +0.09%
- KOSDAQ DISCOVERY_2016_2022: SPREAD20_LEADER +0.16%; SPREAD60_LEADER +0.18%; TOP20_LEADER +0.15%; WPLUS +0.11%
- KOSDAQ NORMAL_2023_2024: SPREAD20_LEADER -0.01%; SPREAD60_LEADER -0.18%; TOP20_LEADER -0.02%; WPLUS +0.01%
- KOSDAQ YTD_2026: SPREAD20_LEADER +0.77%; SPREAD60_LEADER +0.32%; TOP20_LEADER +0.58%; WPLUS +0.32%
- KOSDAQ_PLUS_KOSPI_EX_K200 BULL_2025: SPREAD20_LEADER +0.03%; SPREAD60_LEADER +0.20%; TOP20_LEADER +0.02%; WPLUS +0.23%
- KOSDAQ_PLUS_KOSPI_EX_K200 DISCOVERY_2016_2022: SPREAD20_LEADER +0.19%; SPREAD60_LEADER +0.16%; TOP20_LEADER +0.17%; WPLUS +0.13%
- KOSDAQ_PLUS_KOSPI_EX_K200 NORMAL_2023_2024: SPREAD20_LEADER +0.02%; SPREAD60_LEADER -0.11%; TOP20_LEADER +0.07%; WPLUS -0.07%
- KOSDAQ_PLUS_KOSPI_EX_K200 YTD_2026: SPREAD20_LEADER -0.38%; SPREAD60_LEADER +0.18%; TOP20_LEADER -0.19%; WPLUS +0.03%
- KOSPI_ALL BULL_2025: SPREAD20_LEADER -0.07%; SPREAD60_LEADER -0.11%; TOP20_LEADER -0.11%; WPLUS -0.05%
- KOSPI_ALL DISCOVERY_2016_2022: SPREAD20_LEADER +0.08%; SPREAD60_LEADER +0.01%; TOP20_LEADER -0.00%; WPLUS +0.07%
- KOSPI_ALL NORMAL_2023_2024: SPREAD20_LEADER +0.14%; SPREAD60_LEADER -0.01%; TOP20_LEADER +0.12%; WPLUS +0.14%
- KOSPI_ALL YTD_2026: SPREAD20_LEADER +0.26%; SPREAD60_LEADER -0.57%; TOP20_LEADER +0.28%; WPLUS +0.30%
- KOSPI_EX_K200 BULL_2025: SPREAD20_LEADER -0.14%; SPREAD60_LEADER +0.18%; TOP20_LEADER +0.06%; WPLUS -0.00%
- KOSPI_EX_K200 DISCOVERY_2016_2022: SPREAD20_LEADER +0.22%; SPREAD60_LEADER +0.04%; TOP20_LEADER +0.16%; WPLUS +0.12%
- KOSPI_EX_K200 NORMAL_2023_2024: SPREAD20_LEADER +0.09%; SPREAD60_LEADER +0.01%; TOP20_LEADER +0.10%; WPLUS +0.07%
- KOSPI_EX_K200 YTD_2026: SPREAD20_LEADER +0.17%; SPREAD60_LEADER -0.21%; TOP20_LEADER -0.51%; WPLUS +0.17%
- KOSPI_KOSDAQ_ALL BULL_2025: SPREAD20_LEADER -0.08%; SPREAD60_LEADER +0.02%; TOP20_LEADER -0.02%; WPLUS -0.05%
- KOSPI_KOSDAQ_ALL DISCOVERY_2016_2022: SPREAD20_LEADER +0.09%; SPREAD60_LEADER +0.11%; TOP20_LEADER +0.05%; WPLUS +0.09%
- KOSPI_KOSDAQ_ALL NORMAL_2023_2024: SPREAD20_LEADER +0.05%; SPREAD60_LEADER -0.18%; TOP20_LEADER -0.03%; WPLUS -0.16%
- KOSPI_KOSDAQ_ALL YTD_2026: SPREAD20_LEADER +0.11%; SPREAD60_LEADER -0.22%; TOP20_LEADER +0.05%; WPLUS -0.06%

## Stable simple family-level payoff surfaces

- None

## Guardrail

- A model is economically useful only if FAMILY_STATE or FULL_INTERACTION improves on both STATIC_FAMILY and simple leader controls in sequential walk-forward, not merely in one exceptional year.
- Stable surfaces are descriptive screens; they are not promoted into rules until an expanding threshold test confirms them.

