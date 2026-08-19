# Momentum R- -> Revision portfolio NAV backtest

Tradeable construction: decision uses factor state observed through close t; basket is formed ex-ante at close t and held from t+1. Equal-weight top quintile, mcap >= KRW 250bn, rebalance on the existing 5-trading-day state grid.

- MOM_BASE: always Momentum top quintile.
- RMINUS_TO_REV_ANY: Momentum R- -> Revision, no Revision sign filter.
- RMINUS_TO_REV_POS: Momentum R- -> Revision only when Revision trailing preferred-leg 20D return > 0.

Transaction cost = one-way turnover x 0/30/60 bp. 2023+ is researched post-sample, not untouched OOS.

## NET30: CAGR delta vs always-Momentum

| Sample | Universe | R- -> Rev ANY | R- -> Rev if Rev+ | Rev+ exposure |
|---|---|---:|---:|---:|
| TRAIN_2017_2022 | K200 | +2.27% | +0.17% | 10.0% |
| TRAIN_2017_2022 | KOSPI_EX_K200 | +5.94% | +3.61% | 17.9% |
| TRAIN_2017_2022 | KOSPI_ALL | +1.44% | -0.26% | 12.0% |
| TRAIN_2017_2022 | KOSDAQ | +2.86% | -1.28% | 10.7% |
| TRAIN_2017_2022 | KOSPI_KOSDAQ_ALL | +1.21% | +0.12% | 9.3% |
| TRAIN_2017_2022 | KOSDAQ_PLUS_KOSPI_EX_K200 | +4.08% | -0.02% | 10.0% |
| POST_2023_PLUS | K200 | +7.76% | +4.35% | 6.9% |
| POST_2023_PLUS | KOSPI_EX_K200 | +3.13% | +0.87% | 11.4% |
| POST_2023_PLUS | KOSPI_ALL | +2.78% | +1.68% | 9.7% |
| POST_2023_PLUS | KOSDAQ | +8.12% | +4.64% | 9.7% |
| POST_2023_PLUS | KOSPI_KOSDAQ_ALL | +8.25% | +5.86% | 9.1% |
| POST_2023_PLUS | KOSDAQ_PLUS_KOSPI_EX_K200 | +6.51% | +4.27% | 8.6% |
| POST_2023_2024 | K200 | +4.27% | +5.40% | 7.2% |
| POST_2023_2024 | KOSPI_EX_K200 | +10.49% | +2.85% | 17.5% |
| POST_2023_2024 | KOSPI_ALL | +3.67% | +1.50% | 13.4% |
| POST_2023_2024 | KOSDAQ | +9.13% | +2.52% | 7.2% |
| POST_2023_2024 | KOSPI_KOSDAQ_ALL | +9.18% | +3.85% | 8.2% |
| POST_2023_2024 | KOSDAQ_PLUS_KOSPI_EX_K200 | +9.84% | +2.68% | 8.2% |
| BULL_2025 | K200 | +22.75% | +2.97% | 8.2% |
| BULL_2025 | KOSPI_EX_K200 | -6.70% | -4.09% | 6.1% |
| BULL_2025 | KOSPI_ALL | +9.73% | +3.23% | 8.2% |
| BULL_2025 | KOSDAQ | +11.76% | +16.56% | 20.4% |
| BULL_2025 | KOSPI_KOSDAQ_ALL | +10.55% | +17.53% | 16.3% |
| BULL_2025 | KOSDAQ_PLUS_KOSPI_EX_K200 | +4.45% | +13.28% | 14.3% |
| YTD_2026 | K200 | +1.47% | -0.62% | 3.4% |
| YTD_2026 | KOSPI_EX_K200 | -8.31% | +0.00% | 0.0% |
| YTD_2026 | KOSPI_ALL | -10.85% | +0.00% | 0.0% |
| YTD_2026 | KOSDAQ | +0.26% | +0.00% | 0.0% |
| YTD_2026 | KOSPI_KOSDAQ_ALL | +1.58% | +0.00% | 0.0% |
| YTD_2026 | KOSDAQ_PLUS_KOSPI_EX_K200 | -2.23% | +0.00% | 0.0% |

## NET60: CAGR delta vs always-Momentum

| Sample | Universe | R- -> Rev ANY | R- -> Rev if Rev+ | Rev+ exposure |
|---|---|---:|---:|---:|
| TRAIN_2017_2022 | K200 | +1.07% | -0.43% | 10.0% |
| TRAIN_2017_2022 | KOSPI_EX_K200 | +3.95% | +2.16% | 17.9% |
| TRAIN_2017_2022 | KOSPI_ALL | +0.09% | -1.02% | 12.0% |
| TRAIN_2017_2022 | KOSDAQ | +1.47% | -2.26% | 10.7% |
| TRAIN_2017_2022 | KOSPI_KOSDAQ_ALL | -0.10% | -0.70% | 9.3% |
| TRAIN_2017_2022 | KOSDAQ_PLUS_KOSPI_EX_K200 | +2.45% | -1.03% | 10.0% |
| POST_2023_PLUS | K200 | +6.37% | +3.59% | 6.9% |
| POST_2023_PLUS | KOSPI_EX_K200 | +1.58% | -0.35% | 11.4% |
| POST_2023_PLUS | KOSPI_ALL | +1.24% | +0.79% | 9.7% |
| POST_2023_PLUS | KOSDAQ | +5.68% | +3.46% | 9.7% |
| POST_2023_PLUS | KOSPI_KOSDAQ_ALL | +6.38% | +4.66% | 9.1% |
| POST_2023_PLUS | KOSDAQ_PLUS_KOSPI_EX_K200 | +4.51% | +3.23% | 8.6% |
| POST_2023_2024 | K200 | +3.11% | +4.78% | 7.2% |
| POST_2023_2024 | KOSPI_EX_K200 | +8.52% | +1.04% | 17.5% |
| POST_2023_2024 | KOSPI_ALL | +2.39% | +0.40% | 13.4% |
| POST_2023_2024 | KOSDAQ | +6.73% | +1.78% | 7.2% |
| POST_2023_2024 | KOSPI_KOSDAQ_ALL | +7.43% | +2.77% | 8.2% |
| POST_2023_2024 | KOSDAQ_PLUS_KOSPI_EX_K200 | +7.80% | +1.73% | 8.2% |
| BULL_2025 | K200 | +20.57% | +1.69% | 8.2% |
| BULL_2025 | KOSPI_EX_K200 | -7.63% | -4.72% | 6.1% |
| BULL_2025 | KOSPI_ALL | +7.99% | +2.45% | 8.2% |
| BULL_2025 | KOSDAQ | +7.75% | +12.70% | 20.4% |
| BULL_2025 | KOSPI_KOSDAQ_ALL | +7.93% | +14.87% | 16.3% |
| BULL_2025 | KOSDAQ_PLUS_KOSPI_EX_K200 | +1.89% | +11.06% | 14.3% |
| YTD_2026 | K200 | +0.47% | -1.08% | 3.4% |
| YTD_2026 | KOSPI_EX_K200 | -9.23% | +0.00% | 0.0% |
| YTD_2026 | KOSPI_ALL | -13.01% | +0.00% | 0.0% |
| YTD_2026 | KOSDAQ | -0.55% | +0.00% | 0.0% |
| YTD_2026 | KOSPI_KOSDAQ_ALL | +0.22% | +0.00% | 0.0% |
| YTD_2026 | KOSDAQ_PLUS_KOSPI_EX_K200 | -3.39% | +0.00% | 0.0% |

## NET30 detailed: KOSDAQ + KOSPI ex-K200

| Sample | Strategy | CAGR delta | Sharpe delta | MDD delta | Ann turnover delta | Revision exposure | R- decisions |
|---|---|---:|---:|---:|---:|---:|---:|
| BULL_2025 | RMINUS_TO_REV_ANY | +4.45% | +0.16 | -2.44% | +5.61x | 20.4% | 10 |
| BULL_2025 | RMINUS_TO_REV_POS | +13.28% | +0.36 | -1.35% | +3.74x | 14.3% | 10 |
| POST_2023_2024 | RMINUS_TO_REV_ANY | +9.84% | +0.39 | +7.68% | +5.65x | 26.8% | 26 |
| POST_2023_2024 | RMINUS_TO_REV_POS | +2.68% | +0.10 | +1.07% | +3.15x | 8.2% | 26 |
| POST_2023_PLUS | RMINUS_TO_REV_ANY | +6.51% | +0.18 | +1.76% | +5.52x | 24.6% | 43 |
| POST_2023_PLUS | RMINUS_TO_REV_POS | +4.27% | +0.12 | +0.30% | +2.79x | 8.6% | 43 |
| TRAIN_2017_2022 | RMINUS_TO_REV_ANY | +4.08% | +0.17 | +3.26% | +5.38x | 24.4% | 71 |
| TRAIN_2017_2022 | RMINUS_TO_REV_POS | -0.02% | -0.00 | -1.57% | +3.90x | 10.0% | 71 |
| YTD_2026 | RMINUS_TO_REV_ANY | -2.23% | -0.05 | +1.46% | +4.95x | 24.1% | 7 |
| YTD_2026 | RMINUS_TO_REV_POS | +0.00% | +0.00 | +0.00% | +0.00x | 0.0% | 7 |

## Decision frequency: KOSDAQ + KOSPI ex-K200

| Sample | Strategy | R- share | Rev positive within R- | Revision exposure |
|---|---|---:|---:|---:|
| TRAIN_2017_2022 | RMINUS_TO_REV_ANY | 24.4% | 40.8% | 24.4% |
| TRAIN_2017_2022 | RMINUS_TO_REV_POS | 24.4% | 40.8% | 10.0% |
| POST_2023_PLUS | RMINUS_TO_REV_ANY | 24.6% | 34.9% | 24.6% |
| POST_2023_PLUS | RMINUS_TO_REV_POS | 24.6% | 34.9% | 8.6% |
| POST_2023_2024 | RMINUS_TO_REV_ANY | 26.8% | 30.8% | 26.8% |
| POST_2023_2024 | RMINUS_TO_REV_POS | 26.8% | 30.8% | 8.2% |
| BULL_2025 | RMINUS_TO_REV_ANY | 20.4% | 70.0% | 20.4% |
| BULL_2025 | RMINUS_TO_REV_POS | 20.4% | 70.0% | 14.3% |
| YTD_2026 | RMINUS_TO_REV_ANY | 24.1% | 0.0% | 24.1% |
| YTD_2026 | RMINUS_TO_REV_POS | 24.1% | 0.0% | 0.0% |

## Basket diagnostics

| Universe | dates | avg Momentum N | avg Revision N | avg overlap / Momentum |
|---|---:|---:|---:|---:|
| K200 | 466 | 38.1 | 33.9 | 34.3% |
| KOSDAQ | 466 | 52.6 | 26.4 | 16.8% |
| KOSDAQ_PLUS_KOSPI_EX_K200 | 466 | 89.5 | 44.5 | 17.1% |
| KOSPI_ALL | 466 | 75.0 | 52.0 | 25.4% |
| KOSPI_EX_K200 | 466 | 36.5 | 17.7 | 16.7% |
| KOSPI_KOSDAQ_ALL | 466 | 128.0 | 78.8 | 21.5% |

