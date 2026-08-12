# Profit-Probability and Position-Sizing Research

Objective is explicitly P(5D return > 0), not only average return. Family switches and sizing maps are fit on 2016-2022 only; 2023-2024/2025 are frozen evaluation.

## W+ states with adequate TRAIN and VALID samples

- KOSPI_EX_K200 B4|F_HIGH: TRAIN win 55%, mean +0.71% n=29 -> VALID win 88%, mean +1.24% n=8 -> 2025 57%/+0.22% n=7
- KOSPI_ALL B3|F_HIGH: TRAIN win 53%, mean +0.31% n=45 -> VALID win 71%, mean +0.52% n=21 -> 2025 67%/+0.70% n=9
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_LOW: TRAIN win 63%, mean +0.69% n=59 -> VALID win 67%, mean +0.30% n=12 -> 2025 78%/+0.95% n=9
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_HIGH: TRAIN win 60%, mean +0.19% n=63 -> VALID win 67%, mean -1.15% n=9 -> 2025 75%/+1.06% n=12
- KOSDAQ_PLUS_KOSPI_EX_K200 B3|F_HIGH: TRAIN win 55%, mean +0.11% n=67 -> VALID win 62%, mean +0.86% n=24 -> 2025 65%/+1.34% n=17
- K200 B3|F_HIGH: TRAIN win 45%, mean +0.08% n=51 -> VALID win 62%, mean +0.36% n=16 -> 2025 60%/+0.72% n=10
- KOSPI_ALL B3|F_LOW: TRAIN win 52%, mean -0.17% n=91 -> VALID win 61%, mean +0.71% n=31 -> 2025 44%/-0.05% n=9
- KOSPI_EX_K200 B3|F_LOW: TRAIN win 71%, mean +0.57% n=73 -> VALID win 61%, mean +0.26% n=18 -> 2025 64%/+0.71% n=14
- K200 B4|F_HIGH: TRAIN win 58%, mean +0.79% n=26 -> VALID win 60%, mean +0.42% n=10 -> 2025 62%/+1.57% n=21
- KOSPI_KOSDAQ_ALL B4|F_LOW: TRAIN win 70%, mean +0.67% n=84 -> VALID win 60%, mean -0.50% n=15 -> 2025 69%/+0.96% n=13
- KOSDAQ B4|F_HIGH: TRAIN win 56%, mean -0.01% n=48 -> VALID win 60%, mean -1.14% n=10 -> 2025 64%/+1.61% n=11
- KOSDAQ B4|F_LOW: TRAIN win 57%, mean +0.33% n=63 -> VALID win 58%, mean +0.69% n=12 -> 2025 44%/+0.17% n=9
- KOSDAQ B3|F_LOW: TRAIN win 60%, mean -0.10% n=77 -> VALID win 58%, mean +0.15% n=31 -> 2025 44%/+0.25% n=9
- KOSPI_KOSDAQ_ALL B3|F_HIGH: TRAIN win 49%, mean +0.14% n=57 -> VALID win 58%, mean +0.75% n=26 -> 2025 64%/+1.51% n=11
- KOSPI_ALL B2|F_LOW: TRAIN win 47%, mean -0.55% n=68 -> VALID win 56%, mean +0.38% n=16 -> 2025 100%/+3.69% n=3
- K200 B3|F_LOW: TRAIN win 49%, mean -0.23% n=86 -> VALID win 55%, mean +0.57% n=29 -> 2025 38%/-0.52% n=8
- KOSDAQ B3|F_HIGH: TRAIN win 51%, mean +0.39% n=68 -> VALID win 55%, mean +0.52% n=20 -> 2025 81%/+1.62% n=16
- KOSPI_EX_K200 B2|F_HIGH: TRAIN win 55%, mean -0.21% n=38 -> VALID win 54%, mean +0.54% n=13 -> 2025 0%/-0.56% n=1
- KOSPI_EX_K200 B2|F_LOW: TRAIN win 49%, mean -0.32% n=80 -> VALID win 52%, mean -0.03% n=21 -> 2025 67%/+1.54% n=6
- KOSDAQ_PLUS_KOSPI_EX_K200 B3|F_LOW: TRAIN win 53%, mean -0.17% n=73 -> VALID win 52%, mean -0.14% n=31 -> 2025 57%/+0.23% n=7
- KOSPI_EX_K200 B4|F_LOW: TRAIN win 51%, mean +0.25% n=39 -> VALID win 50%, mean +0.22% n=18 -> 2025 69%/+1.33% n=13
- KOSPI_KOSDAQ_ALL B3|F_LOW: TRAIN win 53%, mean -0.18% n=77 -> VALID win 50%, mean +0.22% n=24 -> 2025 60%/-0.17% n=10
- KOSPI_ALL B4|F_LOW: TRAIN win 65%, mean +0.47% n=55 -> VALID win 50%, mean +0.12% n=10 -> 2025 75%/+1.19% n=8
- KOSPI_KOSDAQ_ALL B2|F_HIGH: TRAIN win 69%, mean +0.52% n=29 -> VALID win 50%, mean -0.52% n=8 -> 2025 100%/+3.03% n=2
- K200 B2|F_LOW: TRAIN win 48%, mean -0.41% n=73 -> VALID win 48%, mean +0.23% n=21 -> 2025 100%/+3.85% n=3
- KOSDAQ_PLUS_KOSPI_EX_K200 B2|F_LOW: TRAIN win 56%, mean -0.45% n=48 -> VALID win 47%, mean -0.03% n=17 -> 2025 67%/+1.82% n=3
- KOSPI_EX_K200 B3|F_HIGH: TRAIN win 52%, mean +0.21% n=29 -> VALID win 46%, mean -0.61% n=13 -> 2025 50%/+0.06% n=8
- K200 B4|F_LOW: TRAIN win 65%, mean +0.51% n=68 -> VALID win 40%, mean -0.61% n=15 -> 2025 33%/+0.42% n=6
- KOSPI_KOSDAQ_ALL B2|F_LOW: TRAIN win 50%, mean -0.35% n=56 -> VALID win 38%, mean -0.47% n=16 -> 2025 67%/+1.65% n=3
- KOSPI_ALL B2|F_HIGH: TRAIN win 68%, mean +0.83% n=25 -> VALID win 38%, mean -0.65% n=8 -> 2025 100%/+2.13% n=1
- KOSPI_ALL B4|F_HIGH: TRAIN win 59%, mean +0.45% n=44 -> VALID win 36%, mean -0.61% n=11 -> 2025 63%/+0.99% n=19

## TRAIN-only hit-rate family switching

### Require +5PP TRAIN hit-rate edge
#### VALID_2023_2024
- K200: switch 68%; win 53% vs W+ 53%; mean edge -0.04%; switched n=66, switched win 55% vs W+ 55%; CAGR +9.9%, MDD -12.8%
- KOSDAQ: switch 0%; win 58% vs W+ 58%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +4.3%, MDD -24.9%
- KOSDAQ_PLUS_KOSPI_EX_K200: switch 32%; win 56% vs W+ 56%; mean edge +0.03%; switched n=31, switched win 52% vs W+ 52%; CAGR +4.4%, MDD -27.5%
- KOSPI_ALL: switch 32%; win 58% vs W+ 57%; mean edge -0.12%; switched n=31, switched win 65% vs W+ 61%; CAGR +7.2%, MDD -14.3%
- KOSPI_EX_K200: switch 20%; win 56% vs W+ 56%; mean edge -0.04%; switched n=18, switched win 50% vs W+ 50%; CAGR +5.7%, MDD -21.7%
- KOSPI_KOSDAQ_ALL: switch 17%; win 52% vs W+ 52%; mean edge +0.00%; switched n=16, switched win 38% vs W+ 38%; CAGR +1.2%, MDD -28.0%
#### STRESS_2025
- K200: switch 43%; win 63% vs W+ 57%; mean edge +0.21%; switched n=21, switched win 71% vs W+ 57%; CAGR +85.3%, MDD -7.2%
- KOSDAQ: switch 0%; win 62% vs W+ 62%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +59.7%, MDD -10.1%
- KOSDAQ_PLUS_KOSPI_EX_K200: switch 14%; win 71% vs W+ 69%; mean edge +0.10%; switched n=7, switched win 71% vs W+ 57%; CAGR +80.9%, MDD -7.1%
- KOSPI_ALL: switch 18%; win 67% vs W+ 65%; mean edge +0.06%; switched n=9, switched win 56% vs W+ 44%; CAGR +62.8%, MDD -8.7%
- KOSPI_EX_K200: switch 27%; win 59% vs W+ 61%; mean edge -0.00%; switched n=13, switched win 62% vs W+ 69%; CAGR +43.8%, MDD -9.7%
- KOSPI_KOSDAQ_ALL: switch 6%; win 67% vs W+ 67%; mean edge +0.03%; switched n=3, switched win 67% vs W+ 67%; CAGR +64.8%, MDD -7.3%
### Require +10PP TRAIN hit-rate edge
#### VALID_2023_2024
- K200: switch 0%; win 53% vs W+ 53%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +12.0%, MDD -12.4%
- KOSDAQ: switch 0%; win 58% vs W+ 58%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +4.3%, MDD -24.9%
- KOSDAQ_PLUS_KOSPI_EX_K200: switch 0%; win 56% vs W+ 56%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +2.7%, MDD -31.2%
- KOSPI_ALL: switch 0%; win 57% vs W+ 57%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +13.4%, MDD -15.5%
- KOSPI_EX_K200: switch 0%; win 56% vs W+ 56%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +7.6%, MDD -20.0%
- KOSPI_KOSDAQ_ALL: switch 0%; win 52% vs W+ 52%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +1.3%, MDD -25.7%
#### STRESS_2025
- K200: switch 0%; win 57% vs W+ 57%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +67.5%, MDD -8.2%
- KOSDAQ: switch 0%; win 62% vs W+ 62%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +59.7%, MDD -10.1%
- KOSDAQ_PLUS_KOSPI_EX_K200: switch 0%; win 69% vs W+ 69%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +72.2%, MDD -7.6%
- KOSPI_ALL: switch 0%; win 65% vs W+ 65%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +58.5%, MDD -7.5%
- KOSPI_EX_K200: switch 0%; win 61% vs W+ 61%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +44.4%, MDD -5.8%
- KOSPI_KOSDAQ_ALL: switch 0%; win 67% vs W+ 67%; mean edge +0.00%; switched n=0, switched win nan% vs W+ nan%; CAGR +62.8%, MDD -8.0%

## TRAIN-only probability sizing of W+

### VALID_2023_2024
#### K200
- SIZE_HIT55_125_75: avg exposure 0.91x, win 53%, mean5 +0.19%, CAGR +8.4%, MDD -13.0%, worst5 -6.0%
- SIZE_HIT55_150_50: avg exposure 0.82x, win 53%, mean5 +0.11%, CAGR +4.7%, MDD -15.7%, worst5 -7.2%
- SIZE_HIT60_125_75: avg exposure 0.86x, win 53%, mean5 +0.17%, CAGR +7.3%, MDD -11.9%, worst5 -6.0%
- SIZE_HIT60_150_50: avg exposure 0.72x, win 53%, mean5 +0.07%, CAGR +2.6%, MDD -14.8%, worst5 -7.2%
#### KOSDAQ
- SIZE_HIT55_125_75: avg exposure 0.83x, win 58%, mean5 +0.18%, CAGR +5.8%, MDD -19.2%, worst5 -9.2%
- SIZE_HIT55_150_50: avg exposure 0.66x, win 58%, mean5 +0.19%, CAGR +7.1%, MDD -13.3%, worst5 -6.1%
- SIZE_HIT60_125_75: avg exposure 0.75x, win 58%, mean5 +0.12%, CAGR +3.6%, MDD -18.9%, worst5 -9.2%
- SIZE_HIT60_150_50: avg exposure 0.50x, win 58%, mean5 +0.08%, CAGR +2.7%, MDD -12.7%, worst5 -6.1%
#### KOSDAQ_PLUS_KOSPI_EX_K200
- SIZE_HIT55_125_75: avg exposure 0.98x, win 56%, mean5 +0.15%, CAGR +5.1%, MDD -28.3%, worst5 -14.9%
- SIZE_HIT55_150_50: avg exposure 0.97x, win 56%, mean5 +0.19%, CAGR +7.3%, MDD -25.7%, worst5 -17.9%
- SIZE_HIT60_125_75: avg exposure 0.86x, win 56%, mean5 +0.04%, CAGR +0.1%, MDD -29.9%, worst5 -14.9%
- SIZE_HIT60_150_50: avg exposure 0.72x, win 56%, mean5 -0.02%, CAGR -2.7%, MDD -29.0%, worst5 -17.9%
#### KOSPI_ALL
- SIZE_HIT55_125_75: avg exposure 0.90x, win 57%, mean5 +0.16%, CAGR +6.9%, MDD -11.4%, worst5 -9.6%
- SIZE_HIT55_150_50: avg exposure 0.80x, win 57%, mean5 +0.03%, CAGR +0.5%, MDD -15.6%, worst5 -11.5%
- SIZE_HIT60_125_75: avg exposure 0.84x, win 57%, mean5 +0.20%, CAGR +9.0%, MDD -11.2%, worst5 -5.7%
- SIZE_HIT60_150_50: avg exposure 0.69x, win 57%, mean5 +0.10%, CAGR +4.5%, MDD -9.0%, worst5 -6.3%
#### KOSPI_EX_K200
- SIZE_HIT55_125_75: avg exposure 0.89x, win 56%, mean5 +0.22%, CAGR +9.7%, MDD -17.0%, worst5 -6.3%
- SIZE_HIT55_150_50: avg exposure 0.79x, win 56%, mean5 +0.25%, CAGR +11.6%, MDD -13.9%, worst5 -7.6%
- SIZE_HIT60_125_75: avg exposure 0.85x, win 56%, mean5 +0.17%, CAGR +7.1%, MDD -17.0%, worst5 -6.3%
- SIZE_HIT60_150_50: avg exposure 0.70x, win 56%, mean5 +0.15%, CAGR +6.3%, MDD -13.9%, worst5 -7.6%
#### KOSPI_KOSDAQ_ALL
- SIZE_HIT55_125_75: avg exposure 0.87x, win 52%, mean5 -0.01%, CAGR -2.1%, MDD -23.6%, worst5 -13.4%
- SIZE_HIT55_150_50: avg exposure 0.74x, win 52%, mean5 -0.09%, CAGR -5.6%, MDD -23.8%, worst5 -16.1%
- SIZE_HIT60_125_75: avg exposure 0.87x, win 52%, mean5 -0.01%, CAGR -2.1%, MDD -23.6%, worst5 -13.4%
- SIZE_HIT60_150_50: avg exposure 0.74x, win 52%, mean5 -0.09%, CAGR -5.6%, MDD -23.8%, worst5 -16.1%
### STRESS_2025
#### K200
- SIZE_HIT55_125_75: avg exposure 1.04x, win 57%, mean5 +1.21%, CAGR +77.0%, MDD -7.3%, worst5 -5.1%
- SIZE_HIT55_150_50: avg exposure 1.07x, win 57%, mean5 +1.33%, CAGR +86.6%, MDD -8.3%, worst5 -6.1%
- SIZE_HIT60_125_75: avg exposure 0.82x, win 57%, mean5 +0.87%, CAGR +52.0%, MDD -6.7%, worst5 -3.1%
- SIZE_HIT60_150_50: avg exposure 0.64x, win 57%, mean5 +0.66%, CAGR +37.5%, MDD -5.3%, worst5 -2.0%
#### KOSDAQ
- SIZE_HIT55_125_75: avg exposure 0.85x, win 62%, mean5 +0.81%, CAGR +43.1%, MDD -11.2%, worst5 -6.2%
- SIZE_HIT55_150_50: avg exposure 0.70x, win 62%, mean5 +0.56%, CAGR +27.8%, MDD -12.3%, worst5 -7.4%
- SIZE_HIT60_125_75: avg exposure 0.75x, win 62%, mean5 +0.79%, CAGR +42.6%, MDD -7.6%, worst5 -3.7%
- SIZE_HIT60_150_50: avg exposure 0.50x, win 62%, mean5 +0.53%, CAGR +27.0%, MDD -5.1%, worst5 -2.5%
#### KOSDAQ_PLUS_KOSPI_EX_K200
- SIZE_HIT55_125_75: avg exposure 1.14x, win 69%, mean5 +1.30%, CAGR +86.0%, MDD -7.6%, worst5 -4.0%
- SIZE_HIT55_150_50: avg exposure 1.28x, win 69%, mean5 +1.47%, CAGR +100.4%, MDD -7.6%, worst5 -4.8%
- SIZE_HIT60_125_75: avg exposure 0.96x, win 69%, mean5 +1.07%, CAGR +66.8%, MDD -7.1%, worst5 -4.0%
- SIZE_HIT60_150_50: avg exposure 0.93x, win 69%, mean5 +1.00%, CAGR +61.1%, MDD -6.6%, worst5 -4.8%
#### KOSPI_ALL
- SIZE_HIT55_125_75: avg exposure 1.04x, win 65%, mean5 +1.03%, CAGR +63.4%, MDD -6.4%, worst5 -5.9%
- SIZE_HIT55_150_50: avg exposure 1.07x, win 65%, mean5 +1.10%, CAGR +68.1%, MDD -7.3%, worst5 -7.1%
- SIZE_HIT60_125_75: avg exposure 0.84x, win 65%, mean5 +0.84%, CAGR +50.0%, MDD -5.6%, worst5 -3.5%
- SIZE_HIT60_150_50: avg exposure 0.68x, win 65%, mean5 +0.72%, CAGR +41.6%, MDD -5.5%, worst5 -3.3%
#### KOSPI_EX_K200
- SIZE_HIT55_125_75: avg exposure 0.96x, win 61%, mean5 +0.70%, CAGR +39.4%, MDD -6.9%, worst5 -4.3%
- SIZE_HIT55_150_50: avg exposure 0.93x, win 61%, mean5 +0.62%, CAGR +34.3%, MDD -8.2%, worst5 -4.3%
- SIZE_HIT60_125_75: avg exposure 0.89x, win 61%, mean5 +0.68%, CAGR +38.5%, MDD -6.9%, worst5 -4.3%
- SIZE_HIT60_150_50: avg exposure 0.79x, win 61%, mean5 +0.59%, CAGR +32.6%, MDD -8.2%, worst5 -4.3%
#### KOSPI_KOSDAQ_ALL
- SIZE_HIT55_125_75: avg exposure 0.90x, win 67%, mean5 +0.95%, CAGR +57.9%, MDD -7.3%, worst5 -3.9%
- SIZE_HIT55_150_50: avg exposure 0.81x, win 67%, mean5 +0.89%, CAGR +52.9%, MDD -6.6%, worst5 -4.7%
- SIZE_HIT60_125_75: avg exposure 0.90x, win 67%, mean5 +0.95%, CAGR +57.9%, MDD -7.3%, worst5 -3.9%
- SIZE_HIT60_150_50: avg exposure 0.81x, win 67%, mean5 +0.89%, CAGR +52.9%, MDD -6.6%, worst5 -4.7%

## Interpretation

- Sizing changes return magnitude, not the sign of a nonzero W+ period; therefore its role is expectancy/risk concentration, while family switching is the only tested mechanism aimed directly at increasing hit rate.
- High-probability states are actionable only when TRAIN and VALID both show elevated hit rate with adequate n; 2025 provides an additional stress check.

