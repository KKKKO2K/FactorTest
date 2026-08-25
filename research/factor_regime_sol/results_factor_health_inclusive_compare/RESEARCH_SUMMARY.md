# Factor Health: ex-target vs target-inclusive comparison

A/B use discrete-safe breadth thresholds; C uses TRAIN-frozen terciles. Primary lens is future +20D preferred-leg return.

Inclusive adds the target own state by construction, so any improvement must be interpreted as self-confirmation, not purely cross-factor information.

## Aggregate

| Def | Sample | Ex H-L | Inclusive H-L | Δ | Ex + | Inc + | Inc better |
|---|---|---:|---:|---:|---:|---:|---:|
| A | TRAIN_2017_2022 | +0.03% | -0.92% | -0.70% | 50% | 38% | 33% |
| A | POST_2023_PLUS | +0.74% | +0.93% | +0.17% | 67% | 79% | 62% |
| A | POST_2023_2024 | -0.17% | -0.36% | -0.32% | 40% | 40% | 40% |
| A | BULL_2025 | +1.78% | +1.58% | +0.26% | 83% | 88% | 62% |
| A | YTD_2026 | -0.89% | -1.84% | +0.69% | 45% | 40% | 60% |
| B | TRAIN_2017_2022 | -0.08% | -0.48% | -0.35% | 46% | 25% | 25% |
| B | POST_2023_PLUS | +0.11% | -0.07% | -0.30% | 58% | 46% | 25% |
| B | POST_2023_2024 | -0.47% | -1.48% | -0.40% | 38% | 17% | 29% |
| B | BULL_2025 | +0.33% | +0.40% | -0.31% | 55% | 59% | 41% |
| B | YTD_2026 | -0.72% | -0.85% | -0.66% | 41% | 41% | 32% |
| C | TRAIN_2017_2022 | -0.37% | -0.42% | +0.04% | 38% | 33% | 54% |
| C | POST_2023_PLUS | -0.64% | -0.18% | +0.11% | 33% | 38% | 54% |
| C | POST_2023_2024 | -1.49% | -1.41% | -0.30% | 12% | 17% | 46% |
| C | BULL_2025 | +0.35% | +0.51% | +0.36% | 52% | 61% | 65% |
| C | YTD_2026 | -0.32% | -1.07% | -0.69% | 39% | 35% | 39% |

## By target

| Def | Sample | Target | Ex | Inclusive | Δ |
|---|---|---|---:|---:|---:|
| A | TRAIN_2017_2022 | FLOW | -0.46% | -1.24% | -0.70% |
| A | TRAIN_2017_2022 | MOMENTUM | +0.03% | -1.39% | -2.01% |
| A | TRAIN_2017_2022 | REVISION | -0.32% | -0.96% | -0.76% |
| A | TRAIN_2017_2022 | VALUE | +0.40% | +1.02% | +0.56% |
| A | POST_2023_PLUS | FLOW | -0.05% | +0.24% | +0.98% |
| A | POST_2023_PLUS | MOMENTUM | +1.55% | +1.91% | +0.17% |
| A | POST_2023_PLUS | REVISION | +1.13% | +1.17% | +0.59% |
| A | POST_2023_PLUS | VALUE | +1.23% | +0.30% | -0.76% |
| A | POST_2023_2024 | FLOW | -0.06% | -0.78% | -0.46% |
| A | POST_2023_2024 | MOMENTUM | +0.23% | +0.09% | +0.31% |
| A | POST_2023_2024 | REVISION | +0.64% | +0.14% | -0.50% |
| A | POST_2023_2024 | VALUE | -0.82% | -1.11% | +0.19% |
| A | BULL_2025 | FLOW | +0.43% | +1.79% | +1.80% |
| A | BULL_2025 | MOMENTUM | +1.99% | +1.81% | -0.18% |
| A | BULL_2025 | REVISION | +0.90% | +1.58% | +0.84% |
| A | BULL_2025 | VALUE | +4.01% | +2.59% | -0.66% |
| A | YTD_2026 | FLOW | -2.09% | -1.95% | +2.61% |
| A | YTD_2026 | MOMENTUM | +1.47% | -0.58% | +2.40% |
| A | YTD_2026 | REVISION | +3.42% | +0.64% | +1.03% |
| A | YTD_2026 | VALUE | -0.76% | -6.43% | -2.39% |
| B | TRAIN_2017_2022 | FLOW | -0.71% | -1.03% | -0.18% |
| B | TRAIN_2017_2022 | MOMENTUM | -0.32% | -1.29% | -0.85% |
| B | TRAIN_2017_2022 | REVISION | +0.24% | -0.32% | -0.49% |
| B | TRAIN_2017_2022 | VALUE | +0.04% | -0.14% | -0.13% |
| B | POST_2023_PLUS | FLOW | -0.02% | -0.23% | -0.24% |
| B | POST_2023_PLUS | MOMENTUM | +0.21% | +1.34% | +0.72% |
| B | POST_2023_PLUS | REVISION | +0.46% | +0.24% | -0.19% |
| B | POST_2023_PLUS | VALUE | -0.06% | -0.99% | -1.45% |
| B | POST_2023_2024 | FLOW | -1.16% | -1.46% | -0.21% |
| B | POST_2023_2024 | MOMENTUM | +0.05% | +0.37% | +0.08% |
| B | POST_2023_2024 | REVISION | +0.16% | -0.73% | -0.36% |
| B | POST_2023_2024 | VALUE | -1.23% | -1.91% | -1.34% |
| B | BULL_2025 | FLOW | -1.02% | -0.18% | +0.05% |
| B | BULL_2025 | MOMENTUM | -1.05% | +0.33% | +1.38% |
| B | BULL_2025 | REVISION | +0.33% | -0.62% | -0.64% |
| B | BULL_2025 | VALUE | +3.81% | +2.02% | -1.42% |
| B | YTD_2026 | FLOW | +1.82% | -0.85% | -0.12% |
| B | YTD_2026 | MOMENTUM | -7.45% | -3.81% | +0.97% |
| B | YTD_2026 | REVISION | -0.62% | +2.55% | +0.79% |
| B | YTD_2026 | VALUE | -0.21% | -2.76% | -1.18% |
| C | TRAIN_2017_2022 | FLOW | -1.43% | -1.13% | +0.01% |
| C | TRAIN_2017_2022 | MOMENTUM | -0.54% | -1.23% | -0.46% |
| C | TRAIN_2017_2022 | REVISION | -0.12% | -0.28% | -0.23% |
| C | TRAIN_2017_2022 | VALUE | +0.12% | +0.16% | +0.08% |
| C | POST_2023_PLUS | FLOW | -1.49% | -1.07% | +0.43% |
| C | POST_2023_PLUS | MOMENTUM | -0.84% | +0.77% | +1.00% |
| C | POST_2023_PLUS | REVISION | +0.56% | +0.32% | -0.18% |
| C | POST_2023_PLUS | VALUE | -0.52% | -1.46% | -1.45% |
| C | POST_2023_2024 | FLOW | -2.13% | -2.06% | +0.23% |
| C | POST_2023_2024 | MOMENTUM | -1.29% | -0.22% | +0.71% |
| C | POST_2023_2024 | REVISION | -1.06% | -1.05% | -0.40% |
| C | POST_2023_2024 | VALUE | -1.43% | -2.25% | -1.30% |
| C | BULL_2025 | FLOW | -2.52% | -0.17% | +1.84% |
| C | BULL_2025 | MOMENTUM | -1.09% | +0.33% | +1.43% |
| C | BULL_2025 | REVISION | +0.53% | +0.47% | +0.17% |
| C | BULL_2025 | VALUE | +2.72% | +2.77% | -1.08% |
| C | YTD_2026 | FLOW | -1.58% | -1.01% | +0.57% |
| C | YTD_2026 | MOMENTUM | -3.11% | +0.70% | +3.62% |
| C | YTD_2026 | REVISION | +1.63% | +1.26% | -1.03% |
| C | YTD_2026 | VALUE | +0.48% | -2.99% | -3.65% |

## Own-state incremental regression

future top20 ~ standardized ex-target health + standardized own component

| Def | Sample | Ex beta | Own beta | Own positive share |
|---|---|---:|---:|---:|
| A | BULL_2025 | +0.49% | +0.42% | 62% |
| A | POST_2023_2024 | -0.38% | -0.20% | 38% |
| A | POST_2023_PLUS | +0.39% | +0.21% | 54% |
| A | TRAIN_2017_2022 | +0.08% | -0.26% | 42% |
| B | BULL_2025 | +0.34% | +0.55% | 58% |
| B | POST_2023_2024 | -0.35% | -0.21% | 21% |
| B | POST_2023_PLUS | +0.15% | +0.38% | 62% |
| B | TRAIN_2017_2022 | +0.08% | -0.06% | 46% |
| C | BULL_2025 | +1.15% | +0.04% | 54% |
| C | POST_2023_2024 | -0.66% | -0.61% | 17% |
| C | POST_2023_PLUS | -0.05% | +0.04% | 50% |
| C | TRAIN_2017_2022 | -0.13% | -0.33% | 25% |
