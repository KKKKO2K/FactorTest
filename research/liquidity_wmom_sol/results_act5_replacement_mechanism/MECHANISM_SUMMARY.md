# ACT5 Bottom-30% Veto — Direct Replacement Mechanism

Base factor portfolio is either exact legacy Weighted Momentum or Weighted Momentum after the R1M>=0 veto.
ACT5 is recent 5D average trading amount divided by the preceding non-overlapping 20D average; cross-sectional bottom 30% is vetoed.
Removed and replacement names are paired in descending original factor rank; forward return is t+1...t+10 compounded.

## PRE_STRESS_2017_2024

| Universe | Factor | Event rate | Avg repl | Removed 10D | Added 10D | Pair Δ | Pair win | Event Δ | Event + | Phases |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K200 | WEIGHTED_MOM | 97.3% | 4.24 | +0.09% | +0.11% | +0.02% | 51.3% | +0.05% | 51.2% | 7/10 |
| K200 | WEIGHTED_MOM_R1M_GE0 | 95.9% | 3.80 | +0.32% | +0.30% | -0.02% | 51.2% | +0.02% | 51.4% | 6/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM | 99.1% | 4.74 | -0.35% | -0.06% | +0.29% | 52.8% | +0.15% | 53.0% | 6/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | 98.5% | 4.13 | -0.27% | +0.17% | +0.44% | 53.5% | +0.29% | 54.3% | 6/10 |
| KOSPI_ALL | WEIGHTED_MOM | 98.4% | 4.73 | -0.34% | -0.13% | +0.21% | 52.2% | +0.18% | 54.4% | 7/10 |
| KOSPI_ALL | WEIGHTED_MOM_R1M_GE0 | 98.1% | 4.18 | -0.31% | -0.01% | +0.30% | 52.6% | +0.34% | 54.1% | 8/10 |
| KOSDAQ | WEIGHTED_MOM | 98.7% | 4.42 | -0.19% | -0.00% | +0.19% | 53.2% | +0.16% | 52.0% | 5/10 |
| KOSDAQ | WEIGHTED_MOM_R1M_GE0 | 97.2% | 3.74 | -0.47% | +0.03% | +0.50% | 53.6% | +0.29% | 52.9% | 5/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM | 98.5% | 4.64 | -0.33% | +0.21% | +0.54% | 53.2% | +0.41% | 52.6% | 5/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM_R1M_GE0 | 97.3% | 4.06 | -0.47% | -0.07% | +0.41% | 53.6% | +0.41% | 53.1% | 7/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM | 98.2% | 4.31 | -0.56% | +0.30% | +0.86% | 53.4% | +0.78% | 53.4% | 8/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | 97.0% | 3.75 | -0.83% | -0.13% | +0.69% | 53.3% | +0.50% | 54.2% | 7/10 |

## EARLY_2017_2019

| Universe | Factor | Event rate | Avg repl | Removed 10D | Added 10D | Pair Δ | Pair win | Event Δ | Event + | Phases |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K200 | WEIGHTED_MOM | 96.9% | 4.14 | -0.01% | -0.04% | -0.03% | 49.5% | +0.07% | 50.0% | 7/10 |
| K200 | WEIGHTED_MOM_R1M_GE0 | 96.1% | 3.88 | +0.16% | -0.10% | -0.26% | 49.2% | -0.21% | 49.0% | 2/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM | 99.5% | 4.70 | -0.89% | -0.42% | +0.48% | 53.4% | +0.15% | 52.5% | 6/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | 98.5% | 4.10 | -0.81% | -0.34% | +0.47% | 52.9% | +0.09% | 54.2% | 5/10 |
| KOSPI_ALL | WEIGHTED_MOM | 98.8% | 4.58 | -1.32% | +0.04% | +1.36% | 54.5% | +1.20% | 60.4% | 9/10 |
| KOSPI_ALL | WEIGHTED_MOM_R1M_GE0 | 98.3% | 4.17 | -1.08% | -0.06% | +1.02% | 52.9% | +0.78% | 57.3% | 9/10 |
| KOSDAQ | WEIGHTED_MOM | 99.5% | 4.32 | +0.19% | +0.39% | +0.19% | 53.0% | -0.27% | 49.7% | 5/10 |
| KOSDAQ | WEIGHTED_MOM_R1M_GE0 | 98.3% | 3.71 | +0.21% | +0.39% | +0.18% | 51.9% | -0.63% | 49.9% | 4/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM | 98.6% | 4.64 | -0.23% | +0.57% | +0.80% | 54.8% | +0.56% | 53.3% | 8/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM_R1M_GE0 | 97.4% | 4.11 | -0.16% | +0.25% | +0.41% | 54.1% | +0.16% | 52.4% | 3/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM | 98.6% | 4.21 | -0.55% | +0.46% | +1.01% | 54.1% | +0.84% | 53.5% | 7/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | 97.8% | 3.69 | -0.61% | +0.14% | +0.75% | 53.8% | +0.49% | 56.3% | 7/10 |

## LATE_2020_2022

| Universe | Factor | Event rate | Avg repl | Removed 10D | Added 10D | Pair Δ | Pair win | Event Δ | Event + | Phases |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K200 | WEIGHTED_MOM | 97.6% | 4.39 | -0.10% | +0.14% | +0.24% | 52.4% | +0.09% | 52.1% | 6/10 |
| K200 | WEIGHTED_MOM_R1M_GE0 | 95.6% | 3.78 | +0.31% | +0.43% | +0.12% | 51.9% | -0.15% | 52.2% | 4/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM | 98.7% | 4.82 | +0.38% | -0.03% | -0.41% | 51.6% | -0.97% | 49.7% | 1/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | 98.3% | 4.11 | +0.50% | +0.61% | +0.11% | 52.9% | -0.46% | 52.5% | 4/10 |
| KOSPI_ALL | WEIGHTED_MOM | 97.8% | 4.87 | +0.15% | -0.24% | -0.39% | 51.2% | -0.81% | 50.6% | 2/10 |
| KOSPI_ALL | WEIGHTED_MOM_R1M_GE0 | 97.5% | 4.20 | +0.11% | +0.11% | +0.01% | 52.9% | -0.17% | 52.3% | 4/10 |
| KOSDAQ | WEIGHTED_MOM | 99.2% | 4.83 | -0.71% | -0.58% | +0.13% | 52.9% | +0.53% | 53.4% | 7/10 |
| KOSDAQ | WEIGHTED_MOM_R1M_GE0 | 98.1% | 4.09 | -1.18% | -0.39% | +0.79% | 54.7% | +1.23% | 55.8% | 7/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM | 98.4% | 4.89 | -0.54% | -0.08% | +0.45% | 52.8% | +0.09% | 52.2% | 5/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM_R1M_GE0 | 97.3% | 4.26 | -0.93% | -0.31% | +0.62% | 54.0% | +0.51% | 52.3% | 7/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM | 97.8% | 4.66 | -0.54% | -0.09% | +0.45% | 52.7% | -0.01% | 52.1% | 6/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | 96.3% | 4.05 | -0.97% | -0.57% | +0.40% | 52.7% | +0.11% | 51.3% | 6/10 |

## NORMAL_2023_2024

| Universe | Factor | Event rate | Avg repl | Removed 10D | Added 10D | Pair Δ | Pair win | Event Δ | Event + | Phases |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K200 | WEIGHTED_MOM | 97.5% | 4.17 | +0.54% | +0.27% | -0.27% | 52.2% | -0.06% | 51.6% | 6/10 |
| K200 | WEIGHTED_MOM_R1M_GE0 | 96.1% | 3.70 | +0.58% | +0.72% | +0.14% | 53.0% | +0.59% | 53.6% | 7/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM | 99.2% | 4.68 | -0.67% | +0.43% | +1.10% | 53.7% | +1.85% | 58.8% | 10/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | 98.8% | 4.19 | -0.62% | +0.24% | +0.85% | 55.1% | +1.62% | 57.0% | 8/10 |
| KOSPI_ALL | WEIGHTED_MOM | 98.8% | 4.74 | +0.32% | -0.19% | -0.51% | 50.2% | +0.14% | 51.3% | 5/10 |
| KOSPI_ALL | WEIGHTED_MOM_R1M_GE0 | 98.6% | 4.18 | +0.22% | -0.12% | -0.33% | 51.8% | +0.44% | 52.1% | 7/10 |
| KOSDAQ | WEIGHTED_MOM | 96.7% | 3.94 | +0.14% | +0.43% | +0.29% | 54.3% | +0.25% | 53.5% | 5/10 |
| KOSDAQ | WEIGHTED_MOM_R1M_GE0 | 94.5% | 3.28 | -0.29% | +0.21% | +0.50% | 54.2% | +0.21% | 52.9% | 7/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM | 98.6% | 4.25 | -0.12% | +0.14% | +0.26% | 51.4% | +0.67% | 52.1% | 8/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM_R1M_GE0 | 97.1% | 3.68 | -0.19% | -0.16% | +0.03% | 52.0% | +0.63% | 55.4% | 8/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM | 98.2% | 3.94 | -0.60% | +0.77% | +1.37% | 53.4% | +1.87% | 55.2% | 9/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | 96.7% | 3.40 | -0.92% | +0.20% | +1.12% | 53.5% | +1.11% | 55.5% | 7/10 |

## BULL_2025

| Universe | Factor | Event rate | Avg repl | Removed 10D | Added 10D | Pair Δ | Pair win | Event Δ | Event + | Phases |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K200 | WEIGHTED_MOM | 97.5% | 3.70 | +3.15% | +1.38% | -1.76% | 44.6% | -1.06% | 47.9% | 4/10 |
| K200 | WEIGHTED_MOM_R1M_GE0 | 95.0% | 3.38 | +2.28% | +0.97% | -1.31% | 46.1% | -0.62% | 48.5% | 3/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM | 97.9% | 4.20 | +0.97% | +0.67% | -0.30% | 51.6% | +0.24% | 49.4% | 4/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | 97.9% | 3.78 | +0.51% | +0.58% | +0.07% | 52.3% | -0.11% | 49.8% | 4/10 |
| KOSPI_ALL | WEIGHTED_MOM | 96.3% | 3.65 | +2.11% | +1.52% | -0.59% | 48.8% | -0.48% | 49.8% | 2/10 |
| KOSPI_ALL | WEIGHTED_MOM_R1M_GE0 | 95.0% | 3.37 | +2.00% | +1.48% | -0.53% | 47.7% | +0.01% | 50.0% | 5/10 |
| KOSDAQ | WEIGHTED_MOM | 96.3% | 3.76 | +1.13% | +1.30% | +0.18% | 52.6% | +0.09% | 50.2% | 5/10 |
| KOSDAQ | WEIGHTED_MOM_R1M_GE0 | 97.1% | 3.42 | +2.07% | +2.09% | +0.02% | 51.9% | -0.10% | 49.8% | 4/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM | 98.8% | 3.71 | +1.16% | +2.31% | +1.16% | 49.4% | +0.89% | 48.5% | 7/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM_R1M_GE0 | 98.8% | 3.50 | +1.49% | +1.93% | +0.44% | 49.2% | -0.11% | 46.9% | 4/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM | 98.3% | 3.78 | +1.28% | +1.62% | +0.34% | 50.3% | -0.60% | 51.3% | 5/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | 98.3% | 3.50 | +1.73% | +2.40% | +0.67% | 51.8% | -0.25% | 53.8% | 4/10 |

## YTD_2026

| Universe | Factor | Event rate | Avg repl | Removed 10D | Added 10D | Pair Δ | Pair win | Event Δ | Event + | Phases |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| K200 | WEIGHTED_MOM | 97.1% | 3.54 | -1.85% | +1.59% | +3.44% | 58.4% | +4.04% | 62.4% | 9/10 |
| K200 | WEIGHTED_MOM_R1M_GE0 | 90.8% | 2.93 | +1.87% | +2.89% | +1.02% | 51.7% | +1.74% | 56.8% | 7/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM | 99.3% | 5.15 | -2.69% | +2.47% | +5.16% | 57.7% | +3.80% | 63.2% | 9/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | 96.1% | 4.07 | -1.19% | +4.44% | +5.63% | 56.5% | +4.20% | 63.9% | 9/10 |
| KOSPI_ALL | WEIGHTED_MOM | 99.3% | 4.09 | -4.03% | +0.37% | +4.40% | 58.8% | +5.04% | 64.0% | 10/10 |
| KOSPI_ALL | WEIGHTED_MOM_R1M_GE0 | 94.9% | 3.17 | -2.06% | +2.31% | +4.37% | 56.6% | +5.91% | 61.2% | 10/10 |
| KOSDAQ | WEIGHTED_MOM | 99.3% | 4.36 | +1.03% | -0.02% | -1.05% | 50.9% | -0.33% | 48.5% | 5/10 |
| KOSDAQ | WEIGHTED_MOM_R1M_GE0 | 89.6% | 3.43 | +4.31% | +1.26% | -3.04% | 51.5% | -0.37% | 46.7% | 6/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM | 99.3% | 4.53 | -0.63% | +2.98% | +3.61% | 58.8% | +3.14% | 58.1% | 7/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM_R1M_GE0 | 92.0% | 3.50 | +2.50% | +5.67% | +3.17% | 56.5% | +4.97% | 60.3% | 8/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM | 99.3% | 4.55 | +0.26% | +2.18% | +1.92% | 53.5% | +3.56% | 59.6% | 9/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | 92.0% | 3.58 | +2.66% | +2.58% | -0.08% | 53.7% | +2.87% | 56.3% | 7/10 |

## Interpretation

- Positive Pair/Event Delta means the ACT5 veto directly replaced stale-activity factor winners with names that subsequently outperformed over 10D.
- Comparing WEIGHTED_MOM with WEIGHTED_MOM_R1M_GE0 tests whether ACT5 adds information after the recent-price-trend veto.
- Phase wins are timing-robustness diagnostics, not independent statistical tests.