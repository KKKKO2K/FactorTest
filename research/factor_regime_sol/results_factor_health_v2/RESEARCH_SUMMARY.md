# Factor Health 2.0 — generalized ex-target test

Target family itself is excluded from health. This tests whether the *other* factor families contain useful information about a target factor's subsequent preferred-leg performance.

## Definitions

- FH-A Healthy Breadth = # W+ among the other 3 families / 3.
- FH-B Net Breadth = (# W+ - # R-) among the other 3 / 3; all other states are neutral.
- FH-C Continuous = mean across the other 3 of 0.5*z(20D spread)+0.5*z(20D preferred-leg absolute return); z parameters fit pre-2023 and frozen.
- Conflict is separate: at least one ex-target W+ and at least one ex-target R-.

Primary lens is HIGH-minus-LOW future 20D preferred-leg return. 20D points overlap on the 5D grid; NW lag-3 t-stats are descriptive.

## Aggregate robustness: 6 universes × 4 targets

| Metric | Pairs | Train median H-L | Post median H-L | Train + | Post + | + in both | Sign agreement |
|---|---:|---:|---:|---:|---:|---:|---:|
| FH_A_HEALTHY_BREADTH | 24 | +0.03% | +0.74% | 50% | 67% | 29% | 42% |
| FH_B_NET_BREADTH | 24 | -0.08% | +0.11% | 46% | 58% | 21% | 38% |
| FH_C_CONTINUOUS | 24 | -0.37% | -0.64% | 38% | 33% | 12% | 54% |

## Median H-L by target family across universes

| Metric | Sample | Momentum | Revision | Value | Flow |
|---|---|---:|---:|---:|---:|
| FH_A_HEALTHY_BREADTH | TRAIN_2017_2022 | +0.03% | -0.32% | +0.40% | -0.46% |
| FH_A_HEALTHY_BREADTH | POST_2023_PLUS | +1.55% | +1.13% | +1.23% | -0.05% |
| FH_A_HEALTHY_BREADTH | POST_2023_2024 | +0.47% | +0.43% | -0.93% | -0.23% |
| FH_A_HEALTHY_BREADTH | BULL_2025 | +1.99% | +0.90% | +4.01% | +0.43% |
| FH_A_HEALTHY_BREADTH | YTD_2026 | -2.97% | -1.89% | -2.20% | -2.53% |
| FH_B_NET_BREADTH | TRAIN_2017_2022 | -0.32% | +0.24% | +0.04% | -0.71% |
| FH_B_NET_BREADTH | POST_2023_PLUS | +0.21% | +0.46% | -0.06% | -0.02% |
| FH_B_NET_BREADTH | POST_2023_2024 | +0.05% | +0.16% | -1.23% | -1.16% |
| FH_B_NET_BREADTH | BULL_2025 | -1.05% | +0.33% | +3.81% | -1.02% |
| FH_B_NET_BREADTH | YTD_2026 | -7.45% | -0.62% | -0.21% | +1.82% |
| FH_C_CONTINUOUS | TRAIN_2017_2022 | -0.54% | -0.12% | +0.12% | -1.43% |
| FH_C_CONTINUOUS | POST_2023_PLUS | -0.84% | +0.56% | -0.52% | -1.49% |
| FH_C_CONTINUOUS | POST_2023_2024 | -1.29% | -1.06% | -1.43% | -2.13% |
| FH_C_CONTINUOUS | BULL_2025 | -1.09% | +0.53% | +2.72% | -2.52% |
| FH_C_CONTINUOUS | YTD_2026 | -3.11% | +1.63% | +0.48% | -1.58% |

## Strongest cells positive in both TRAIN and POST

| Metric | Universe | Target | Train H-L | Post H-L | Train t | Post t |
|---|---|---|---:|---:|---:|---:|
| FH_A_HEALTHY_BREADTH | K200 | MOMENTUM | +1.26% | +1.90% | +1.00 | +0.87 |
| FH_B_NET_BREADTH | KOSPI_ALL | REVISION | +1.16% | +1.01% | +0.79 | +0.57 |
| FH_A_HEALTHY_BREADTH | KOSPI_EX_K200 | MOMENTUM | +0.98% | +0.76% | +0.82 | +0.36 |
| FH_B_NET_BREADTH | KOSPI_EX_K200 | REVISION | +2.22% | +0.48% | +1.30 | +0.23 |
| FH_A_HEALTHY_BREADTH | KOSPI_ALL | VALUE | +0.37% | +2.36% | +0.35 | +1.40 |
| FH_A_HEALTHY_BREADTH | KOSPI_KOSDAQ_ALL | VALUE | +0.35% | +2.14% | +0.32 | +1.21 |
| FH_A_HEALTHY_BREADTH | KOSPI_ALL | FLOW | +0.33% | +0.62% | +0.29 | +0.40 |
| FH_A_HEALTHY_BREADTH | KOSPI_EX_K200 | VALUE | +1.01% | +0.32% | +0.92 | +0.19 |
| FH_B_NET_BREADTH | KOSPI_KOSDAQ_ALL | MOMENTUM | +0.25% | +0.39% | +0.15 | +0.20 |
| FH_A_HEALTHY_BREADTH | KOSDAQ | MOMENTUM | +0.19% | +3.01% | +0.12 | +1.24 |
| FH_C_CONTINUOUS | KOSPI_EX_K200 | REVISION | +0.17% | +0.65% | +0.11 | +0.31 |
| FH_B_NET_BREADTH | KOSPI_KOSDAQ_ALL | REVISION | +0.15% | +2.38% | +0.10 | +1.11 |
| FH_C_CONTINUOUS | KOSDAQ_PLUS_KOSPI_EX_K200 | VALUE | +0.08% | +1.20% | +0.07 | +0.85 |
| FH_C_CONTINUOUS | KOSPI_ALL | REVISION | +0.49% | +0.03% | +0.32 | +0.02 |
| FH_B_NET_BREADTH | KOSPI_ALL | VALUE | +0.20% | +0.03% | +0.17 | +0.02 |

## Conflict incremental test

Regression: future target return ~ FH-B Net Breadth + Conflict. A negative Conflict beta means cross-factor disagreement hurts after controlling for net breadth.

- TRAIN_2017_2022: median Conflict beta +0.06%; negative in 46% of cells; median NW t +0.05; n=24
- POST_2023_PLUS: median Conflict beta -0.37%; negative in 50% of cells; median NW t -0.19; n=24

## Selection rule

Prefer the simplest definition that keeps the same economic sign across TRAIN and POST and works across several target families/universes. FH-C is only worth keeping if it materially improves stability over FH-A/FH-B.

