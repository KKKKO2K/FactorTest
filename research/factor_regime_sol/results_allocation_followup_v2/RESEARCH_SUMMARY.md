# Factor Allocation Follow-up v2

Momentum = exact legacy weighted momentum. State information is fully observed before forward returns.
20D observations overlap on the 5D state grid; NW t-stats (lag 3) are descriptive, not untouched OOS proof.

## Sign persistence: current POS minus NEG -> future +20D preferred leg

| Sample | Universe | Momentum | Revision | Value | Flow |
|---|---|---:|---:|---:|---:|
| TRAIN_2016_2022 | K200 | +0.04% | -0.06% | +0.98% | +0.34% |
| TRAIN_2016_2022 | KOSPI_EX_K200 | -0.96% | +0.66% | +0.52% | +0.56% |
| TRAIN_2016_2022 | KOSDAQ | +0.52% | -0.39% | +0.63% | -1.35% |
| TRAIN_2016_2022 | KOSDAQ_PLUS_KOSPI_EX_K200 | -0.79% | -0.46% | +0.65% | -0.53% |
| TRAIN_2016_2022 | KOSPI_ALL | -0.40% | +0.50% | +1.04% | -0.21% |
| TRAIN_2016_2022 | KOSPI_KOSDAQ_ALL | -0.52% | -0.13% | +1.10% | -0.62% |
| POST_2023_PLUS | K200 | +1.11% | -0.33% | -1.71% | -0.98% |
| POST_2023_PLUS | KOSPI_EX_K200 | +1.76% | +0.18% | -1.96% | -1.05% |
| POST_2023_PLUS | KOSDAQ | +1.91% | +0.14% | -0.05% | +1.40% |
| POST_2023_PLUS | KOSDAQ_PLUS_KOSPI_EX_K200 | +2.91% | +1.59% | -2.32% | +0.11% |
| POST_2023_PLUS | KOSPI_ALL | +1.61% | +0.47% | -1.81% | -1.36% |
| POST_2023_PLUS | KOSPI_KOSDAQ_ALL | +2.44% | +1.92% | -2.38% | +0.68% |

## Momentum R-: pooled live-positive alternative basket vs staying in Momentum

| Sample | Universe | Horizon | Alt-Mom Δ | win rate | NW t | n |
|---|---|---:|---:|---:|---:|---:|
| TRAIN_2016_2022 | K200 | 5D | +0.40% | 57.4% | +1.99 | 47 |
| TRAIN_2016_2022 | K200 | 20D | +0.90% | 63.8% | +1.88 | 47 |
| TRAIN_2016_2022 | KOSPI_EX_K200 | 5D | +0.12% | 54.8% | +0.32 | 62 |
| TRAIN_2016_2022 | KOSPI_EX_K200 | 20D | +0.48% | 54.8% | +0.66 | 62 |
| TRAIN_2016_2022 | KOSDAQ | 5D | +0.40% | 50.0% | +1.03 | 44 |
| TRAIN_2016_2022 | KOSDAQ | 20D | +0.14% | 54.5% | +0.13 | 44 |
| TRAIN_2016_2022 | KOSDAQ_PLUS_KOSPI_EX_K200 | 5D | -0.05% | 46.7% | -0.11 | 45 |
| TRAIN_2016_2022 | KOSDAQ_PLUS_KOSPI_EX_K200 | 20D | +0.15% | 60.0% | +0.17 | 45 |
| TRAIN_2016_2022 | KOSPI_ALL | 5D | +0.02% | 42.6% | +0.07 | 54 |
| TRAIN_2016_2022 | KOSPI_ALL | 20D | +0.13% | 50.0% | +0.30 | 54 |
| TRAIN_2016_2022 | KOSPI_KOSDAQ_ALL | 5D | +0.22% | 45.7% | +0.58 | 46 |
| TRAIN_2016_2022 | KOSPI_KOSDAQ_ALL | 20D | +0.36% | 56.5% | +0.43 | 46 |
| POST_2023_PLUS | K200 | 5D | +0.82% | 75.0% | +2.89 | 24 |
| POST_2023_PLUS | K200 | 20D | +1.73% | 79.2% | +3.09 | 24 |
| POST_2023_PLUS | KOSPI_EX_K200 | 5D | +0.33% | 56.7% | +1.01 | 30 |
| POST_2023_PLUS | KOSPI_EX_K200 | 20D | +1.32% | 73.3% | +1.51 | 30 |
| POST_2023_PLUS | KOSDAQ | 5D | +0.62% | 54.5% | +1.34 | 22 |
| POST_2023_PLUS | KOSDAQ | 20D | +2.24% | 63.6% | +1.86 | 22 |
| POST_2023_PLUS | KOSDAQ_PLUS_KOSPI_EX_K200 | 5D | +0.57% | 69.6% | +1.62 | 23 |
| POST_2023_PLUS | KOSDAQ_PLUS_KOSPI_EX_K200 | 20D | +1.37% | 65.2% | +1.50 | 23 |
| POST_2023_PLUS | KOSPI_ALL | 5D | +0.90% | 67.9% | +2.27 | 28 |
| POST_2023_PLUS | KOSPI_ALL | 20D | +1.66% | 75.0% | +2.51 | 28 |
| POST_2023_PLUS | KOSPI_KOSDAQ_ALL | 5D | +0.36% | 67.7% | +0.89 | 31 |
| POST_2023_PLUS | KOSPI_KOSDAQ_ALL | 20D | +0.85% | 67.7% | +0.84 | 31 |
| POST_2023_2024 | K200 | 5D | +0.85% | 82.4% | +2.75 | 17 |
| POST_2023_2024 | K200 | 20D | +1.16% | 70.6% | +1.95 | 17 |
| POST_2023_2024 | KOSPI_EX_K200 | 5D | +0.65% | 62.5% | +1.80 | 24 |
| POST_2023_2024 | KOSPI_EX_K200 | 20D | +2.39% | 83.3% | +4.94 | 24 |
| POST_2023_2024 | KOSDAQ | 5D | +0.27% | 45.5% | +0.37 | 11 |
| POST_2023_2024 | KOSDAQ | 20D | +1.15% | 54.5% | +0.74 | 11 |
| POST_2023_2024 | KOSDAQ_PLUS_KOSPI_EX_K200 | 5D | +0.62% | 69.2% | +1.16 | 13 |
| POST_2023_2024 | KOSDAQ_PLUS_KOSPI_EX_K200 | 20D | +1.99% | 76.9% | +1.42 | 13 |
| POST_2023_2024 | KOSPI_ALL | 5D | +0.93% | 75.0% | +1.89 | 20 |
| POST_2023_2024 | KOSPI_ALL | 20D | +1.71% | 70.0% | +2.13 | 20 |
| POST_2023_2024 | KOSPI_KOSDAQ_ALL | 5D | +0.50% | 72.2% | +1.02 | 18 |
| POST_2023_2024 | KOSPI_KOSDAQ_ALL | 20D | +1.67% | 72.2% | +1.29 | 18 |
| BULL_2025 | KOSDAQ | 5D | +0.93% | 60.0% | +1.53 | 10 |
| BULL_2025 | KOSDAQ | 20D | +2.58% | 70.0% | +1.33 | 10 |
| BULL_2025 | KOSDAQ_PLUS_KOSPI_EX_K200 | 5D | +0.51% | 66.7% | +1.08 | 9 |
| BULL_2025 | KOSDAQ_PLUS_KOSPI_EX_K200 | 20D | -0.08% | 44.4% | -0.08 | 9 |
| BULL_2025 | KOSPI_KOSDAQ_ALL | 5D | +0.48% | 63.6% | +0.79 | 11 |
| BULL_2025 | KOSPI_KOSDAQ_ALL | 20D | +0.43% | 63.6% | +0.51 | 11 |

## Momentum R-: individual currently-positive alternative vs Momentum, +20D preferred leg

| Sample | Universe | Alt | Δ | win rate | NW t | n |
|---|---|---|---:|---:|---:|---:|
| TRAIN_2016_2022 | K200 | REVISION | +0.63% | 65.5% | +1.86 | 29 |
| TRAIN_2016_2022 | K200 | VALUE | +1.22% | 69.0% | +1.74 | 42 |
| TRAIN_2016_2022 | K200 | FLOW | +1.08% | 82.4% | +3.96 | 34 |
| TRAIN_2016_2022 | KOSPI_EX_K200 | REVISION | +1.95% | 71.2% | +2.46 | 52 |
| TRAIN_2016_2022 | KOSPI_EX_K200 | VALUE | -0.84% | 42.9% | -1.09 | 49 |
| TRAIN_2016_2022 | KOSPI_EX_K200 | FLOW | -1.14% | 39.0% | -1.69 | 41 |
| TRAIN_2016_2022 | KOSDAQ | REVISION | -0.15% | 61.3% | -0.16 | 31 |
| TRAIN_2016_2022 | KOSDAQ | VALUE | +0.65% | 53.7% | +0.44 | 41 |
| TRAIN_2016_2022 | KOSDAQ | FLOW | -1.68% | 36.4% | -1.09 | 22 |
| TRAIN_2016_2022 | KOSDAQ_PLUS_KOSPI_EX_K200 | REVISION | +1.42% | 79.3% | +2.86 | 29 |
| TRAIN_2016_2022 | KOSDAQ_PLUS_KOSPI_EX_K200 | VALUE | -0.36% | 56.1% | -0.32 | 41 |
| TRAIN_2016_2022 | KOSDAQ_PLUS_KOSPI_EX_K200 | FLOW | -0.61% | 47.6% | -0.78 | 21 |
| TRAIN_2016_2022 | KOSPI_ALL | REVISION | +0.80% | 68.6% | +2.15 | 35 |
| TRAIN_2016_2022 | KOSPI_ALL | VALUE | +0.15% | 46.7% | +0.23 | 45 |
| TRAIN_2016_2022 | KOSPI_ALL | FLOW | -0.27% | 41.7% | -0.76 | 36 |
| TRAIN_2016_2022 | KOSPI_KOSDAQ_ALL | REVISION | +1.33% | 77.8% | +3.23 | 27 |
| TRAIN_2016_2022 | KOSPI_KOSDAQ_ALL | VALUE | +0.06% | 58.5% | +0.06 | 41 |
| TRAIN_2016_2022 | KOSPI_KOSDAQ_ALL | FLOW | +0.17% | 61.9% | +0.36 | 21 |
| POST_2023_PLUS | K200 | REVISION | +2.49% | 91.7% | +3.64 | 12 |
| POST_2023_PLUS | K200 | VALUE | +1.50% | 66.7% | +1.66 | 18 |
| POST_2023_PLUS | K200 | FLOW | +1.42% | 69.2% | +1.69 | 13 |
| POST_2023_PLUS | KOSPI_EX_K200 | REVISION | +1.45% | 70.0% | +2.04 | 20 |
| POST_2023_PLUS | KOSPI_EX_K200 | VALUE | +1.55% | 76.2% | +1.37 | 21 |
| POST_2023_PLUS | KOSPI_EX_K200 | FLOW | +1.46% | 85.7% | +2.35 | 14 |
| POST_2023_PLUS | KOSDAQ | REVISION | +2.76% | 70.6% | +1.78 | 17 |
| POST_2023_PLUS | KOSDAQ | VALUE | +2.35% | 66.7% | +1.59 | 18 |
| POST_2023_PLUS | KOSDAQ | FLOW | +0.99% | 70.0% | +1.04 | 10 |
| POST_2023_PLUS | KOSDAQ_PLUS_KOSPI_EX_K200 | REVISION | +2.54% | 73.3% | +2.58 | 15 |
| POST_2023_PLUS | KOSDAQ_PLUS_KOSPI_EX_K200 | VALUE | +1.05% | 50.0% | +0.81 | 16 |
| POST_2023_PLUS | KOSPI_ALL | REVISION | +0.81% | 70.6% | +2.73 | 17 |
| POST_2023_PLUS | KOSPI_ALL | VALUE | +2.25% | 69.6% | +2.23 | 23 |
| POST_2023_PLUS | KOSPI_ALL | FLOW | +1.90% | 77.8% | +2.32 | 9 |
| POST_2023_PLUS | KOSPI_KOSDAQ_ALL | REVISION | +2.50% | 87.5% | +3.76 | 16 |
| POST_2023_PLUS | KOSPI_KOSDAQ_ALL | VALUE | +0.53% | 56.0% | +0.43 | 25 |
| POST_2023_PLUS | KOSPI_KOSDAQ_ALL | FLOW | +1.14% | 90.9% | +2.03 | 11 |
| POST_2023_2024 | K200 | VALUE | +0.35% | 50.0% | +0.58 | 12 |
| POST_2023_2024 | K200 | FLOW | +1.53% | 66.7% | +1.80 | 12 |
| POST_2023_2024 | KOSPI_EX_K200 | REVISION | +1.77% | 76.5% | +2.06 | 17 |
| POST_2023_2024 | KOSPI_EX_K200 | VALUE | +2.77% | 82.4% | +5.31 | 17 |
| POST_2023_2024 | KOSPI_EX_K200 | FLOW | +1.85% | 91.7% | +3.45 | 12 |
| POST_2023_2024 | KOSDAQ | VALUE | +1.15% | 55.6% | +0.48 | 9 |
| POST_2023_2024 | KOSDAQ | FLOW | +0.77% | 62.5% | +0.67 | 8 |
| POST_2023_2024 | KOSDAQ_PLUS_KOSPI_EX_K200 | REVISION | +2.88% | 87.5% | +2.15 | 8 |
| POST_2023_2024 | KOSDAQ_PLUS_KOSPI_EX_K200 | VALUE | +1.95% | 55.6% | +0.99 | 9 |
| POST_2023_2024 | KOSPI_ALL | REVISION | +0.73% | 61.5% | +1.88 | 13 |
| POST_2023_2024 | KOSPI_ALL | VALUE | +2.67% | 68.8% | +2.44 | 16 |
| POST_2023_2024 | KOSPI_KOSDAQ_ALL | REVISION | +2.39% | 87.5% | +3.07 | 8 |
| POST_2023_2024 | KOSPI_KOSDAQ_ALL | VALUE | +1.49% | 64.7% | +1.04 | 17 |
| BULL_2025 | KOSDAQ | REVISION | +3.79% | 80.0% | +1.87 | 10 |
| BULL_2025 | KOSDAQ | VALUE | +2.63% | 75.0% | +1.66 | 8 |
| BULL_2025 | KOSPI_KOSDAQ_ALL | REVISION | +2.61% | 87.5% | +2.21 | 8 |
