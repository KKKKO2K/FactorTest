# Cross-Universe Allocation and Stable Family Overlay

Disjoint sleeves: K200, KOSPI_EX_K200, KOSDAQ. Each sleeve uses its W+ family basket. Rules are contemporaneous and generic; no validation outcome is used to define the cross-universe weighting rules.

## Cross-sectional signal tests

- STRESS_2025 FHIGH_MINUS_FLOW: n=58, mean +0.48%, win 62%, median +0.43%
- STRESS_2025 STRONGER_BASE_MINUS_WEAKER: n=92, mean +0.43%, win 62%, median +0.39%
- STRESS_2026 FHIGH_MINUS_FLOW: n=17, mean +0.93%, win 59%, median +1.34%
- STRESS_2026 STRONGER_BASE_MINUS_WEAKER: n=26, mean +1.27%, win 58%, median +0.70%
- TRAIN_2016_2022 FHIGH_MINUS_FLOW: n=282, mean +0.09%, win 49%, median -0.13%
- TRAIN_2016_2022 STRONGER_BASE_MINUS_WEAKER: n=504, mean +0.19%, win 55%, median +0.21%
- VALID_2023_2024 FHIGH_MINUS_FLOW: n=95, mean -0.01%, win 46%, median -0.17%
- VALID_2023_2024 STRONGER_BASE_MINUS_WEAKER: n=140, mean -0.35%, win 38%, median -0.46%

## Allocation rule performance

### STRESS_2025
- EW3: win 67%, mean5 +0.89%, CAGR +49.0%, MDD -6.6%
- HEALTH_2X: win 64%, mean5 +0.93%, CAGR +51.9%, MDD -6.9%
- FHIGH_ONLY: win 62%, mean5 +1.02%, CAGR +57.6%, MDD -7.6%
- BASE_WEIGHT: win 64%, mean5 +0.91%, CAGR +50.6%, MDD -6.8%
- HEALTH_BASE: win 64%, mean5 +0.94%, CAGR +52.4%, MDD -6.9%
### STRESS_2026
- EW3: win 69%, mean5 +2.07%, CAGR +107.8%, MDD -7.1%
- HEALTH_2X: win 77%, mean5 +2.14%, CAGR +112.9%, MDD -7.1%
- FHIGH_ONLY: win 69%, mean5 +2.19%, CAGR +116.5%, MDD -7.1%
- BASE_WEIGHT: win 69%, mean5 +2.12%, CAGR +112.0%, MDD -7.0%
- HEALTH_BASE: win 69%, mean5 +2.16%, CAGR +114.9%, MDD -7.0%
### TRAIN_2016_2022
- EW3: win 56%, mean5 +0.09%, CAGR +2.2%, MDD -34.8%
- HEALTH_2X: win 56%, mean5 +0.10%, CAGR +2.5%, MDD -34.5%
- FHIGH_ONLY: win 56%, mean5 +0.11%, CAGR +2.6%, MDD -35.3%
- BASE_WEIGHT: win 56%, mean5 +0.10%, CAGR +2.7%, MDD -34.6%
- HEALTH_BASE: win 55%, mean5 +0.11%, CAGR +2.9%, MDD -34.3%
### VALID_2023_2024
- EW3: win 58%, mean5 +0.23%, CAGR +8.3%, MDD -15.7%
- HEALTH_2X: win 56%, mean5 +0.23%, CAGR +8.2%, MDD -14.9%
- FHIGH_ONLY: win 58%, mean5 +0.26%, CAGR +9.3%, MDD -13.1%
- BASE_WEIGHT: win 58%, mean5 +0.21%, CAGR +7.4%, MDD -16.3%
- HEALTH_BASE: win 58%, mean5 +0.21%, CAGR +7.3%, MDD -15.8%

## Family tilt stress check

- KOSPI_KOSDAQ_ALL B2|F_HIGH REVISION: TRAIN +0.39% (n=29) -> VALID +1.00% (n=8) -> 2025 NA
- KOSDAQ B4|F_HIGH VALUE: TRAIN +0.14% (n=48) -> VALID +0.93% (n=10) -> 2025 -0.81% (n=11)
- KOSPI_ALL B4|F_HIGH REVISION: TRAIN +0.44% (n=44) -> VALID +0.86% (n=11) -> 2025 +0.25% (n=19)
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_HIGH VALUE: TRAIN +0.22% (n=63) -> VALID +0.84% (n=9) -> 2025 -0.73% (n=12)
- KOSPI_EX_K200 B3|F_HIGH REVISION: TRAIN +0.36% (n=29) -> VALID +0.66% (n=13) -> 2025 +0.11% (n=8)
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_HIGH REVISION: TRAIN +0.26% (n=63) -> VALID +0.62% (n=9) -> 2025 -0.04% (n=12)
- KOSPI_KOSDAQ_ALL B2|F_LOW VALUE: TRAIN +0.04% (n=56) -> VALID +0.59% (n=16) -> 2025 -0.37% (n=3)
- KOSDAQ B4|F_HIGH REVISION: TRAIN +0.26% (n=48) -> VALID +0.56% (n=10) -> 2025 +0.09% (n=11)
- KOSPI_KOSDAQ_ALL B4|F_LOW REVISION: TRAIN +0.05% (n=84) -> VALID +0.43% (n=15) -> 2025 +0.13% (n=13)
- K200 B4|F_HIGH REVISION: TRAIN +0.18% (n=26) -> VALID +0.40% (n=10) -> 2025 +0.14% (n=21)
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_LOW FLOW: TRAIN +0.12% (n=59) -> VALID +0.28% (n=12) -> 2025 -0.04% (n=9)
- KOSPI_ALL B4|F_LOW REVISION: TRAIN +0.05% (n=55) -> VALID +0.22% (n=10) -> 2025 +0.29% (n=8)
- KOSPI_EX_K200 B3|F_HIGH VALUE: TRAIN +0.18% (n=29) -> VALID +0.21% (n=13) -> 2025 +0.86% (n=8)
- KOSDAQ_PLUS_KOSPI_EX_K200 B2|F_LOW REVISION: TRAIN +0.02% (n=48) -> VALID +0.14% (n=17) -> 2025 +0.73% (n=3)
- KOSDAQ B3|F_LOW REVISION: TRAIN +0.18% (n=77) -> VALID +0.13% (n=31) -> 2025 +0.13% (n=9)
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_LOW REVISION: TRAIN +0.19% (n=59) -> VALID +0.12% (n=12) -> 2025 -0.26% (n=9)
- KOSDAQ_PLUS_KOSPI_EX_K200 B3|F_LOW REVISION: TRAIN +0.18% (n=73) -> VALID +0.10% (n=31) -> 2025 +0.70% (n=7)
- K200 B3|F_LOW MOMENTUM: TRAIN +0.03% (n=86) -> VALID +0.10% (n=29) -> 2025 +0.62% (n=8)
- KOSPI_KOSDAQ_ALL B3|F_LOW REVISION: TRAIN +0.05% (n=77) -> VALID +0.10% (n=24) -> 2025 +0.46% (n=10)
- K200 B3|F_HIGH VALUE: TRAIN +0.35% (n=51) -> VALID +0.09% (n=16) -> 2025 +0.23% (n=10)

## Conservative overlay candidates

- KOSPI_KOSDAQ_ALL B2|F_HIGH: tilt to REVISION
- KOSPI_ALL B4|F_HIGH: tilt to REVISION
- KOSPI_EX_K200 B3|F_HIGH: tilt to REVISION
- KOSPI_KOSDAQ_ALL B2|F_LOW: tilt to VALUE
- KOSDAQ B4|F_HIGH: tilt to REVISION
- KOSPI_KOSDAQ_ALL B4|F_LOW: tilt to REVISION
- K200 B4|F_HIGH: tilt to REVISION
- KOSPI_ALL B4|F_LOW: tilt to REVISION
- KOSPI_EX_K200 B3|F_HIGH: tilt to VALUE
- KOSDAQ_PLUS_KOSPI_EX_K200 B2|F_LOW: tilt to REVISION
- KOSDAQ B3|F_LOW: tilt to REVISION
- KOSDAQ_PLUS_KOSPI_EX_K200 B3|F_LOW: tilt to REVISION
- K200 B3|F_LOW: tilt to MOMENTUM
- KOSPI_KOSDAQ_ALL B3|F_LOW: tilt to REVISION
- K200 B3|F_HIGH: tilt to VALUE
- KOSDAQ_PLUS_KOSPI_EX_K200 B2|F_LOW: tilt to FLOW
- KOSPI_KOSDAQ_ALL B2|F_LOW: tilt to FLOW
- K200 B2|F_LOW: tilt to REVISION
- K200 B4|F_HIGH: tilt to VALUE
- KOSPI_EX_K200 B3|F_LOW: tilt to REVISION
- KOSPI_KOSDAQ_ALL B2|F_LOW: tilt to REVISION

## Overlay performance

### K200 STRESS_2025
- WPLUS: win 57%, mean5 +1.09%, CAGR +67.5%, MDD -8.2%
- STABLE_TILT: win 61%, mean5 +1.35%, CAGR +90.8%, MDD -10.2%
### K200 VALID_2023_2024
- WPLUS: win 53%, mean5 +0.26%, CAGR +12.0%, MDD -12.4%
- STABLE_TILT: win 53%, mean5 +0.32%, CAGR +14.9%, MDD -14.5%
### KOSDAQ STRESS_2025
- WPLUS: win 62%, mean5 +1.05%, CAGR +59.7%, MDD -10.1%
- STABLE_TILT: win 69%, mean5 +1.10%, CAGR +63.4%, MDD -13.4%
### KOSDAQ VALID_2023_2024
- WPLUS: win 58%, mean5 +0.16%, CAGR +4.3%, MDD -24.9%
- STABLE_TILT: win 60%, mean5 +0.30%, CAGR +10.1%, MDD -24.5%
### KOSDAQ_PLUS_KOSPI_EX_K200 STRESS_2025
- WPLUS: win 69%, mean5 +1.13%, CAGR +72.2%, MDD -7.6%
- STABLE_TILT: win 71%, mean5 +1.22%, CAGR +80.1%, MDD -8.1%
### KOSDAQ_PLUS_KOSPI_EX_K200 VALID_2023_2024
- WPLUS: win 56%, mean5 +0.10%, CAGR +2.7%, MDD -31.2%
- STABLE_TILT: win 56%, mean5 +0.14%, CAGR +4.6%, MDD -28.6%
### KOSPI_ALL STRESS_2025
- WPLUS: win 65%, mean5 +0.97%, CAGR +58.5%, MDD -7.5%
- STABLE_TILT: win 71%, mean5 +1.11%, CAGR +70.2%, MDD -8.3%
### KOSPI_ALL VALID_2023_2024
- WPLUS: win 57%, mean5 +0.29%, CAGR +13.4%, MDD -15.5%
- STABLE_TILT: win 60%, mean5 +0.41%, CAGR +20.6%, MDD -15.8%
### KOSPI_EX_K200 STRESS_2025
- WPLUS: win 61%, mean5 +0.77%, CAGR +44.4%, MDD -5.8%
- STABLE_TILT: win 59%, mean5 +0.96%, CAGR +58.0%, MDD -6.5%
### KOSPI_EX_K200 VALID_2023_2024
- WPLUS: win 56%, mean5 +0.19%, CAGR +7.6%, MDD -20.0%
- STABLE_TILT: win 56%, mean5 +0.22%, CAGR +9.4%, MDD -21.7%
### KOSPI_KOSDAQ_ALL STRESS_2025
- WPLUS: win 67%, mean5 +1.02%, CAGR +62.8%, MDD -8.0%
- STABLE_TILT: win 69%, mean5 +1.22%, CAGR +80.0%, MDD -7.4%
### KOSPI_KOSDAQ_ALL VALID_2023_2024
- WPLUS: win 52%, mean5 +0.06%, CAGR +1.3%, MDD -25.7%
- STABLE_TILT: win 53%, mean5 +0.24%, CAGR +10.4%, MDD -23.0%

## Promotion rule

- Cross-universe allocation is useful only if the same generic health/base weighting improves EW3 in both TRAIN and 2023-2024 without a major 2025 reversal.
- A family overlay is useful only if the exact state/family excess over W+ is positive in TRAIN and 2023-2024 and remains positive in 2025 when sample size is adequate.

