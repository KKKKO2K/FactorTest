# Weighted Momentum R1M<0 Veto — Direct Replacement Mechanism

Mechanism test: at each formation close, compare legacy-WMOM Top20 names removed solely because `R1M < 0` with the next-best legacy-WMOM names admitted by the `R1M >= 0` gate.
Forward return is compounded `t+1 ... t+10`, matching the existing portfolio simulator's rebalance timing and missing-return convention.
When multiple names are replaced, removed and added names are paired in descending legacy-WMOM rank order.

## PRE_STRESS_2017_2024

| Universe | Event rate | Avg # repl | Removed fwd10 | Added fwd10 | Pair Δ | Pair win | Event Δ | Event +rate | Phase wins |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K200 | 56.6% | 1.43 | -0.64% | -0.42% | +0.22% | 52.2% | +0.36% | 52.1% | 5/10 |
| KOSPI_EX_K200 | 70.3% | 1.92 | -0.68% | -0.54% | +0.13% | 50.9% | +0.10% | 50.6% | 4/10 |
| KOSPI_ALL | 63.3% | 1.57 | -1.52% | -0.90% | +0.62% | 51.0% | +0.73% | 53.6% | 6/10 |
| KOSDAQ | 74.8% | 2.07 | -0.65% | -0.15% | +0.50% | 52.2% | +1.02% | 51.4% | 9/10 |
| KOSPI_KOSDAQ_ALL | 68.5% | 1.71 | -1.24% | +0.06% | +1.30% | 53.1% | +1.58% | 52.9% | 9/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | 70.5% | 1.79 | -1.19% | +0.11% | +1.30% | 52.0% | +1.49% | 53.7% | 9/10 |

## EARLY_2017_2019

| Universe | Event rate | Avg # repl | Removed fwd10 | Added fwd10 | Pair Δ | Pair win | Event Δ | Event +rate | Phase wins |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K200 | 47.4% | 1.04 | -1.09% | -0.59% | +0.50% | 51.7% | +0.56% | 51.8% | 7/10 |
| KOSPI_EX_K200 | 69.3% | 2.01 | -0.35% | -0.89% | -0.54% | 48.9% | -0.36% | 47.8% | 4/10 |
| KOSPI_ALL | 58.4% | 1.35 | -1.49% | -0.14% | +1.35% | 54.0% | +2.28% | 59.2% | 9/10 |
| KOSDAQ | 70.4% | 1.91 | -0.30% | +0.62% | +0.93% | 53.2% | +1.07% | 50.7% | 8/10 |
| KOSPI_KOSDAQ_ALL | 66.5% | 1.59 | -0.83% | +0.49% | +1.32% | 55.5% | +1.55% | 53.1% | 7/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | 68.6% | 1.74 | -0.92% | +0.26% | +1.18% | 53.6% | +0.92% | 55.8% | 8/10 |

## LATE_2020_2022

| Universe | Event rate | Avg # repl | Removed fwd10 | Added fwd10 | Pair Δ | Pair win | Event Δ | Event +rate | Phase wins |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K200 | 61.7% | 1.87 | -0.55% | -0.60% | -0.05% | 52.0% | +0.59% | 51.7% | 8/10 |
| KOSPI_EX_K200 | 70.0% | 1.94 | -1.08% | -0.75% | +0.32% | 53.4% | -0.31% | 51.7% | 5/10 |
| KOSPI_ALL | 66.4% | 1.81 | -1.78% | -1.28% | +0.50% | 50.8% | -0.09% | 49.9% | 5/10 |
| KOSDAQ | 79.3% | 2.20 | -1.79% | -0.83% | +0.96% | 53.1% | +1.74% | 52.6% | 7/10 |
| KOSPI_KOSDAQ_ALL | 73.0% | 1.81 | -1.89% | -0.12% | +1.77% | 53.2% | +2.44% | 53.6% | 8/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | 75.0% | 1.87 | -1.89% | -0.04% | +1.86% | 52.2% | +2.48% | 53.5% | 10/10 |

## NORMAL_2023_2024

| Universe | Event rate | Avg # repl | Removed fwd10 | Added fwd10 | Pair Δ | Pair win | Event Δ | Event +rate | Phase wins |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K200 | 62.8% | 1.36 | -0.30% | +0.13% | +0.43% | 53.2% | -0.19% | 53.1% | 4/10 |
| KOSPI_EX_K200 | 72.3% | 1.79 | -0.56% | +0.35% | +0.91% | 49.9% | +1.30% | 53.0% | 7/10 |
| KOSPI_ALL | 66.1% | 1.53 | -1.11% | -1.23% | -0.12% | 47.2% | -0.08% | 51.7% | 5/10 |
| KOSDAQ | 74.4% | 2.12 | +0.66% | -0.13% | -0.79% | 49.2% | -0.18% | 50.7% | 4/10 |
| KOSPI_KOSDAQ_ALL | 64.6% | 1.73 | -0.78% | -0.26% | +0.53% | 49.5% | +0.16% | 51.3% | 5/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | 66.7% | 1.76 | -0.47% | +0.12% | +0.59% | 49.5% | +0.68% | 50.9% | 5/10 |

## BULL_2025

| Universe | Event rate | Avg # repl | Removed fwd10 | Added fwd10 | Pair Δ | Pair win | Event Δ | Event +rate | Phase wins |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K200 | 53.1% | 1.42 | +4.21% | +0.89% | -3.31% | 41.9% | -3.61% | 40.2% | 2/10 |
| KOSPI_EX_K200 | 56.6% | 1.29 | +1.83% | +1.31% | -0.52% | 48.9% | -0.55% | 48.9% | 4/10 |
| KOSPI_ALL | 52.9% | 1.02 | +2.48% | +2.13% | -0.35% | 47.6% | -0.79% | 49.2% | 5/10 |
| KOSDAQ | 62.8% | 1.32 | -1.96% | +0.95% | +2.91% | 55.0% | +5.16% | 61.8% | 9/10 |
| KOSPI_KOSDAQ_ALL | 56.2% | 0.88 | -0.38% | +2.87% | +3.25% | 50.5% | +6.38% | 55.9% | 10/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | 59.9% | 0.97 | -1.76% | -0.36% | +1.40% | 50.2% | +2.89% | 53.8% | 7/10 |

## YTD_2026

| Universe | Event rate | Avg # repl | Removed fwd10 | Added fwd10 | Pair Δ | Pair win | Event Δ | Event +rate | Phase wins |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K200 | 59.8% | 2.48 | -8.03% | +0.90% | +8.93% | 68.6% | +6.23% | 64.6% | 8/10 |
| KOSPI_EX_K200 | 86.3% | 2.82 | -4.51% | -1.88% | +2.63% | 59.5% | +3.33% | 60.2% | 8/10 |
| KOSPI_ALL | 78.8% | 2.24 | -8.83% | -1.66% | +7.18% | 68.7% | +5.73% | 67.6% | 9/10 |
| KOSDAQ | 73.0% | 2.88 | -11.58% | -3.83% | +7.75% | 61.7% | +8.15% | 72.0% | 10/10 |
| KOSPI_KOSDAQ_ALL | 84.7% | 2.39 | -11.52% | -2.94% | +8.57% | 64.8% | +8.11% | 73.3% | 10/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | 84.7% | 2.72 | -10.91% | -2.80% | +8.11% | 65.3% | +10.53% | 74.1% | 10/10 |

## Interpretation

- `Pair Δ` is the stock-level added-minus-removed 10D return, weighting each replacement pair equally.
- `Event Δ` first averages simultaneous replacements within a date, then weights each replacement date equally.
- `Phase wins` tests timing robustness across the same 10 staggered 10-trading-day schedules; it is not an independence-based p-value.
- A positive result here supports the proposed veto mechanism directly; it does not by itself establish that 0% is uniquely optimal.
