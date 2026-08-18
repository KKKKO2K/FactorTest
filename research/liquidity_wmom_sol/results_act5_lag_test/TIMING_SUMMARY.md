# ACT5 Timing Robustness — Same-Day vs 1-Day Lag

Exact legacy WMOM; Top20; mcap >= KRW 250bn; 10D hold; 10 staggered phases.
`ACT5_T`: recent 5D / preceding non-overlapping 20D through formation-date close.
`ACT5_LAG1`: the exact same ACT5 signal shifted by one trading day, so formation uses only information known at the prior close.

## PRE_STRESS_2017_2024

| Universe | Factor | Same-day Δ | Same-day wins | Lag1 Δ | Lag1 wins |
|---|---|---:|---:|---:|---:|
| K200 | WEIGHTED_MOM | -0.70% | 4/10 | -0.44% | 4/10 |
| K200 | WEIGHTED_MOM_R1M_GE0 | +1.25% | 6/10 | -0.49% | 4/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM | +1.14% | 7/10 | -0.16% | 4/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | +2.21% | 8/10 | +2.46% | 8/10 |
| KOSPI_ALL | WEIGHTED_MOM | +0.77% | 5/10 | +0.15% | 6/10 |
| KOSPI_ALL | WEIGHTED_MOM_R1M_GE0 | +1.86% | 8/10 | +0.50% | 5/10 |
| KOSDAQ | WEIGHTED_MOM | -0.40% | 4/10 | +0.22% | 6/10 |
| KOSDAQ | WEIGHTED_MOM_R1M_GE0 | +2.75% | 8/10 | +2.61% | 9/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM | +0.92% | 5/10 | +1.60% | 7/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM_R1M_GE0 | +0.07% | 6/10 | +0.25% | 5/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM | +2.86% | 9/10 | +2.38% | 10/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | +1.86% | 9/10 | +1.35% | 9/10 |

## EARLY_2017_2019

| Universe | Factor | Same-day Δ | Same-day wins | Lag1 Δ | Lag1 wins |
|---|---|---:|---:|---:|---:|
| K200 | WEIGHTED_MOM | -1.06% | 3/10 | -0.74% | 3/10 |
| K200 | WEIGHTED_MOM_R1M_GE0 | -1.78% | 1/10 | -0.63% | 2/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM | +0.54% | 6/10 | +2.52% | 6/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | +0.70% | 7/10 | +0.70% | 7/10 |
| KOSPI_ALL | WEIGHTED_MOM | +5.99% | 9/10 | +5.79% | 10/10 |
| KOSPI_ALL | WEIGHTED_MOM_R1M_GE0 | +4.16% | 8/10 | +4.32% | 8/10 |
| KOSDAQ | WEIGHTED_MOM | -0.70% | 4/10 | +2.49% | 7/10 |
| KOSDAQ | WEIGHTED_MOM_R1M_GE0 | +2.38% | 7/10 | +1.89% | 6/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM | +4.49% | 8/10 | +5.89% | 9/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM_R1M_GE0 | +0.66% | 6/10 | +1.42% | 8/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM | +5.44% | 8/10 | +5.59% | 10/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | +3.50% | 9/10 | +3.11% | 8/10 |

## LATE_2020_2022

| Universe | Factor | Same-day Δ | Same-day wins | Lag1 Δ | Lag1 wins |
|---|---|---:|---:|---:|---:|
| K200 | WEIGHTED_MOM | -0.17% | 4/10 | +0.03% | 5/10 |
| K200 | WEIGHTED_MOM_R1M_GE0 | +3.85% | 7/10 | +3.31% | 6/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM | -1.91% | 3/10 | -3.17% | 2/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | +1.08% | 7/10 | +4.45% | 6/10 |
| KOSPI_ALL | WEIGHTED_MOM | -1.27% | 3/10 | -3.38% | 2/10 |
| KOSPI_ALL | WEIGHTED_MOM_R1M_GE0 | -0.23% | 5/10 | -0.93% | 4/10 |
| KOSDAQ | WEIGHTED_MOM | -1.42% | 4/10 | -1.29% | 4/10 |
| KOSDAQ | WEIGHTED_MOM_R1M_GE0 | +2.96% | 6/10 | +3.44% | 7/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM | -0.21% | 5/10 | -0.72% | 4/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM_R1M_GE0 | +0.87% | 5/10 | -1.22% | 4/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM | +3.37% | 6/10 | -0.07% | 5/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | +2.48% | 6/10 | -0.24% | 4/10 |

## NORMAL_2023_2024

| Universe | Factor | Same-day Δ | Same-day wins | Lag1 Δ | Lag1 wins |
|---|---|---:|---:|---:|---:|
| K200 | WEIGHTED_MOM | -2.40% | 3/10 | -2.30% | 3/10 |
| K200 | WEIGHTED_MOM_R1M_GE0 | +0.63% | 5/10 | -0.37% | 5/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM | +7.10% | 8/10 | +4.33% | 8/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | +1.21% | 8/10 | +2.52% | 7/10 |
| KOSPI_ALL | WEIGHTED_MOM | -2.54% | 4/10 | -6.74% | 3/10 |
| KOSPI_ALL | WEIGHTED_MOM_R1M_GE0 | -0.61% | 3/10 | -2.55% | 3/10 |
| KOSDAQ | WEIGHTED_MOM | +0.05% | 5/10 | -0.92% | 5/10 |
| KOSDAQ | WEIGHTED_MOM_R1M_GE0 | +2.98% | 6/10 | +4.38% | 8/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM | +2.02% | 6/10 | +0.85% | 5/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM_R1M_GE0 | -0.45% | 4/10 | +1.44% | 6/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM | +3.92% | 7/10 | +5.04% | 8/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | +3.19% | 6/10 | +5.33% | 7/10 |

## BULL_2025

| Universe | Factor | Same-day Δ | Same-day wins | Lag1 Δ | Lag1 wins |
|---|---|---:|---:|---:|---:|
| K200 | WEIGHTED_MOM | -14.58% | 0/10 | -14.01% | 2/10 |
| K200 | WEIGHTED_MOM_R1M_GE0 | -11.28% | 2/10 | -8.31% | 2/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM | -5.43% | 3/10 | -4.09% | 4/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | -3.87% | 4/10 | -2.69% | 5/10 |
| KOSPI_ALL | WEIGHTED_MOM | -5.43% | 2/10 | -2.96% | 4/10 |
| KOSPI_ALL | WEIGHTED_MOM_R1M_GE0 | -2.69% | 3/10 | -2.64% | 4/10 |
| KOSDAQ | WEIGHTED_MOM | +1.82% | 6/10 | -0.67% | 0/10 |
| KOSDAQ | WEIGHTED_MOM_R1M_GE0 | +0.54% | 6/10 | -5.32% | 3/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM | +5.18% | 7/10 | +6.15% | 8/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM_R1M_GE0 | -2.02% | 4/10 | -0.55% | 5/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM | +1.37% | 5/10 | -1.53% | 4/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | +3.91% | 6/10 | +1.98% | 7/10 |

## YTD_2026

| Universe | Factor | Same-day Δ | Same-day wins | Lag1 Δ | Lag1 wins |
|---|---|---:|---:|---:|---:|
| K200 | WEIGHTED_MOM | +20.46% | 9/10 | +18.06% | 9/10 |
| K200 | WEIGHTED_MOM_R1M_GE0 | +1.97% | 6/10 | +4.73% | 6/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM | +21.70% | 10/10 | +18.51% | 10/10 |
| KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | +30.78% | 10/10 | +29.65% | 10/10 |
| KOSPI_ALL | WEIGHTED_MOM | +20.27% | 10/10 | +24.62% | 9/10 |
| KOSPI_ALL | WEIGHTED_MOM_R1M_GE0 | +15.21% | 8/10 | +19.94% | 9/10 |
| KOSDAQ | WEIGHTED_MOM | -0.72% | 5/10 | +2.10% | 5/10 |
| KOSDAQ | WEIGHTED_MOM_R1M_GE0 | -0.79% | 5/10 | +5.87% | 6/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM | +15.72% | 8/10 | +22.29% | 8/10 |
| KOSPI_KOSDAQ_ALL | WEIGHTED_MOM_R1M_GE0 | +22.16% | 7/10 | +15.76% | 8/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM | +7.19% | 7/10 | +17.03% | 8/10 |
| KOSDAQ_PLUS_KOSPI_EX_K200 | WEIGHTED_MOM_R1M_GE0 | +1.18% | 5/10 | +2.90% | 7/10 |
