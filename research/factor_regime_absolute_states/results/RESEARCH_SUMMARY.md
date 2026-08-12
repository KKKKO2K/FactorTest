# Absolute-Confirmed Factor State Research

Core correction: factor 'working' is not defined from long-short spread alone. Each 20D state keeps preferred absolute return, opposite absolute return, and their cumulative-return difference.
Main relative state uses 20D preferred cumulative return minus 20D opposite cumulative return. The prior compounded-5D-LS definition is retained only as a diagnostic column.
State5: W+ = relative working and preferred absolute return > 0; W- = relative working but preferred absolute return <= 0; N = neutral; R+ / R- analogously split reverse states by preferred absolute sign.
Primary rotation labels: GENUINE_ROTATION = Momentum R- + Other W+; DEFENSIVE_ROTATION = Momentum R- + Other W-; BULLISH_STYLE_SHIFT = Momentum R+ + Other W+; BROAD_CONFIRMATION = Momentum W+ + Other W+.
Thresholds are fit on 2016-2022 TRAIN and frozen for 2023+. Q33 is main; Q25/Q50 are robustness. 2023+ is post-discovery validation, not untouched OOS.

## Refined breadth: same-universe market outcome

### K200
- RELATIVE_WORKING_BREADTH: TRAIN H-L +0.08% -> OOS +0.63%
- ABS_CONFIRMED_BREADTH: TRAIN H-L +0.08% -> OOS +1.25%
- BEARISH_REVERSE_BREADTH: TRAIN H-L +0.53% -> OOS +0.36%
- POSITIVE_ABS_BREADTH: TRAIN H-L -0.03% -> OOS +2.48%

### KOSPI_ALL
- RELATIVE_WORKING_BREADTH: TRAIN H-L +0.60% -> OOS +1.07%
- ABS_CONFIRMED_BREADTH: TRAIN H-L -0.12% -> OOS +1.53%
- DEFENSIVE_WORKING_BREADTH: TRAIN H-L +0.40% -> OOS -2.18%
- BEARISH_REVERSE_BREADTH: TRAIN H-L +0.58% -> OOS -0.28%
- POSITIVE_ABS_BREADTH: TRAIN H-L -0.22% -> OOS +1.73%

### KOSPI_EX_K200
- RELATIVE_WORKING_BREADTH: TRAIN H-L +0.11% -> OOS -1.37%
- ABS_CONFIRMED_BREADTH: TRAIN H-L +0.34% -> OOS -2.65%
- DEFENSIVE_WORKING_BREADTH: TRAIN H-L -0.36% -> OOS +0.25%
- BEARISH_REVERSE_BREADTH: TRAIN H-L -0.12% -> OOS +0.55%
- POSITIVE_ABS_BREADTH: TRAIN H-L +0.32% -> OOS -1.05%

### KOSDAQ
- RELATIVE_WORKING_BREADTH: TRAIN H-L -1.14% -> OOS -1.87%
- ABS_CONFIRMED_BREADTH: TRAIN H-L -2.58% -> OOS +1.09%
- DEFENSIVE_WORKING_BREADTH: TRAIN H-L +1.83% -> OOS -1.79%
- BEARISH_REVERSE_BREADTH: TRAIN H-L +0.93% -> OOS +1.61%
- POSITIVE_ABS_BREADTH: TRAIN H-L -1.40% -> OOS +0.49%

### KOSDAQ_PLUS_KOSPI_EX_K200
- RELATIVE_WORKING_BREADTH: TRAIN H-L -1.04% -> OOS -0.62%
- ABS_CONFIRMED_BREADTH: TRAIN H-L -1.89% -> OOS +1.37%
- DEFENSIVE_WORKING_BREADTH: TRAIN H-L +0.89% -> OOS -0.70%
- BEARISH_REVERSE_BREADTH: TRAIN H-L +0.77% -> OOS +0.85%
- POSITIVE_ABS_BREADTH: TRAIN H-L -1.17% -> OOS +0.17%

## Pair regimes: Q33 same-universe market outcomes

### K200
MOMENTUM_X_REVISION:
- GENUINE_ROTATION, TRAIN: median pair market +5D -0.03%, +20D +0.99% (pairs=4)
- GENUINE_ROTATION, OOS: median pair market +5D -0.42%, +20D +0.19% (pairs=2)
- DEFENSIVE_ROTATION, OOS: median pair market +5D +0.49%, +20D +9.24% (pairs=1)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D +0.18%, +20D +0.72% (pairs=4)
- BULLISH_STYLE_SHIFT, OOS: median pair market +5D +1.16%, +20D +3.85% (pairs=3)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D -0.13%, +20D -0.63% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D +1.60%, +20D +5.52% (pairs=4)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +0.40%, +20D +1.99% (pairs=4)
- BROAD_BREAKDOWN, OOS: median pair market +5D +0.64%, +20D +4.19% (pairs=4)
MOMENTUM_X_VALUE:
- GENUINE_ROTATION, TRAIN: median pair market +5D +0.30%, +20D +1.55% (pairs=4)
- GENUINE_ROTATION, OOS: median pair market +5D +1.20%, +20D +4.32% (pairs=3)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D -0.33%, +20D +0.06% (pairs=2)
- DEFENSIVE_ROTATION, OOS: median pair market +5D +1.77%, +20D +5.14% (pairs=3)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D +0.33%, +20D +0.39% (pairs=4)
- BULLISH_STYLE_SHIFT, OOS: median pair market +5D +1.78%, +20D +4.86% (pairs=2)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D +0.02%, +20D -0.18% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D +1.09%, +20D +5.74% (pairs=3)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +1.51%, +20D +3.35% (pairs=4)
- BROAD_BREAKDOWN, OOS: median pair market +5D -0.60%, +20D +5.47% (pairs=1)
MOMENTUM_X_FLOW:
- GENUINE_ROTATION, TRAIN: median pair market +5D +0.91%, +20D +2.63% (pairs=2)
- GENUINE_ROTATION, OOS: median pair market +5D -0.97%, +20D +1.11% (pairs=2)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D -0.19%, +20D +0.84% (pairs=3)
- DEFENSIVE_ROTATION, OOS: median pair market +5D +1.25%, +20D +2.53% (pairs=1)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D +0.74%, +20D +1.89% (pairs=4)
- BULLISH_STYLE_SHIFT, OOS: median pair market +5D +1.65%, +20D +2.21% (pairs=1)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D +0.13%, +20D -0.34% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D +1.47%, +20D +5.67% (pairs=4)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +0.11%, +20D +1.32% (pairs=3)
- BROAD_BREAKDOWN, OOS: median pair market +5D +1.01%, +20D +5.24% (pairs=2)

### KOSPI_ALL
MOMENTUM_X_REVISION:
- GENUINE_ROTATION, TRAIN: median pair market +5D -0.04%, +20D +0.39% (pairs=4)
- GENUINE_ROTATION, OOS: median pair market +5D +0.31%, +20D -1.33% (pairs=2)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D +0.81%, +20D +1.80% (pairs=3)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D +0.11%, +20D +1.80% (pairs=4)
- BULLISH_STYLE_SHIFT, OOS: median pair market +5D +0.84%, +20D +1.64% (pairs=2)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D +0.04%, +20D -0.33% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D +1.66%, +20D +5.80% (pairs=4)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +0.95%, +20D +1.69% (pairs=4)
- BROAD_BREAKDOWN, OOS: median pair market +5D +0.87%, +20D +2.38% (pairs=4)
MOMENTUM_X_VALUE:
- GENUINE_ROTATION, TRAIN: median pair market +5D +0.20%, +20D +0.85% (pairs=4)
- GENUINE_ROTATION, OOS: median pair market +5D +0.55%, +20D +1.14% (pairs=3)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D +0.29%, +20D -0.02% (pairs=2)
- DEFENSIVE_ROTATION, OOS: median pair market +5D +1.93%, +20D +1.66% (pairs=2)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D -0.27%, +20D +0.73% (pairs=4)
- BULLISH_STYLE_SHIFT, OOS: median pair market +5D +0.78%, +20D +1.19% (pairs=2)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D -0.11%, +20D +0.06% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D +0.57%, +20D +3.09% (pairs=3)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +1.21%, +20D +2.67% (pairs=4)
- BROAD_BREAKDOWN, OOS: median pair market +5D -0.35%, +20D +4.00% (pairs=2)
MOMENTUM_X_FLOW:
- GENUINE_ROTATION, TRAIN: median pair market +5D +0.29%, +20D +1.16% (pairs=4)
- GENUINE_ROTATION, OOS: median pair market +5D +0.05%, +20D +2.45% (pairs=1)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D +0.29%, +20D +0.86% (pairs=4)
- DEFENSIVE_ROTATION, OOS: median pair market +5D +0.54%, +20D +1.22% (pairs=2)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D +0.88%, +20D +3.39% (pairs=4)
- BULLISH_STYLE_SHIFT, OOS: median pair market +5D +1.37%, +20D +3.93% (pairs=1)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D +0.10%, +20D -0.35% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D +1.81%, +20D +6.13% (pairs=4)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +0.28%, +20D +0.64% (pairs=3)
- BROAD_BREAKDOWN, OOS: median pair market +5D +1.17%, +20D +3.19% (pairs=3)

### KOSPI_EX_K200
MOMENTUM_X_REVISION:
- GENUINE_ROTATION, TRAIN: median pair market +5D -0.34%, +20D +0.23% (pairs=4)
- GENUINE_ROTATION, OOS: median pair market +5D -0.31%, +20D +0.55% (pairs=1)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D +0.23%, +20D -1.43% (pairs=4)
- DEFENSIVE_ROTATION, OOS: median pair market +5D -0.36%, +20D +2.18% (pairs=1)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D +0.54%, +20D +0.59% (pairs=4)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D +0.34%, +20D +0.40% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D +0.34%, +20D +1.14% (pairs=4)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +0.89%, +20D +2.66% (pairs=3)
- BROAD_BREAKDOWN, OOS: median pair market +5D +0.20%, +20D -1.67% (pairs=4)
MOMENTUM_X_VALUE:
- GENUINE_ROTATION, TRAIN: median pair market +5D +0.51%, +20D +1.80% (pairs=4)
- GENUINE_ROTATION, OOS: median pair market +5D -0.98%, +20D -2.43% (pairs=2)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D +0.81%, +20D -0.07% (pairs=4)
- DEFENSIVE_ROTATION, OOS: median pair market +5D -1.17%, +20D +0.20% (pairs=2)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D -0.14%, +20D +0.16% (pairs=3)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D +0.35%, +20D +1.12% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D +0.62%, +20D -0.11% (pairs=2)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +0.08%, +20D -0.08% (pairs=2)
- BROAD_BREAKDOWN, OOS: median pair market +5D +0.27%, +20D +4.46% (pairs=3)
MOMENTUM_X_FLOW:
- GENUINE_ROTATION, TRAIN: median pair market +5D +0.72%, +20D +2.24% (pairs=4)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D +0.49%, +20D +1.63% (pairs=4)
- DEFENSIVE_ROTATION, OOS: median pair market +5D -1.63%, +20D +0.87% (pairs=3)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D +0.56%, +20D +1.44% (pairs=4)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D -0.10%, +20D -1.18% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D +0.30%, +20D +0.04% (pairs=4)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D -0.15%, +20D +0.16% (pairs=4)
- BROAD_BREAKDOWN, OOS: median pair market +5D +0.06%, +20D +1.30% (pairs=2)

### KOSDAQ
MOMENTUM_X_REVISION:
- GENUINE_ROTATION, TRAIN: median pair market +5D +0.10%, +20D -0.09% (pairs=4)
- GENUINE_ROTATION, OOS: median pair market +5D +0.32%, +20D +1.09% (pairs=2)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D +0.45%, +20D +2.96% (pairs=4)
- DEFENSIVE_ROTATION, OOS: median pair market +5D -1.14%, +20D -1.67% (pairs=1)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D -0.01%, +20D +1.19% (pairs=3)
- BULLISH_STYLE_SHIFT, OOS: median pair market +5D +0.82%, +20D +1.37% (pairs=3)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D -0.31%, +20D -1.31% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D -0.21%, +20D -0.35% (pairs=4)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +0.35%, +20D +0.50% (pairs=4)
MOMENTUM_X_VALUE:
- GENUINE_ROTATION, TRAIN: median pair market +5D -0.06%, +20D -0.19% (pairs=4)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D +0.42%, +20D +2.20% (pairs=4)
- DEFENSIVE_ROTATION, OOS: median pair market +5D +0.25%, +20D +3.05% (pairs=4)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D +1.24%, +20D +0.87% (pairs=3)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D +0.29%, +20D -0.74% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D -0.17%, +20D +2.62% (pairs=2)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +1.85%, +20D +6.50% (pairs=3)
- BROAD_BREAKDOWN, OOS: median pair market +5D +1.07%, +20D +2.48% (pairs=1)
MOMENTUM_X_FLOW:
- GENUINE_ROTATION, TRAIN: median pair market +5D -0.16%, +20D -0.61% (pairs=3)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D +0.66%, +20D +1.64% (pairs=4)
- DEFENSIVE_ROTATION, OOS: median pair market +5D +0.54%, +20D +0.25% (pairs=3)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D +0.87%, +20D +1.48% (pairs=3)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D -0.32%, +20D -1.16% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D -0.30%, +20D +0.04% (pairs=4)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +0.53%, +20D +2.91% (pairs=4)
- BROAD_BREAKDOWN, OOS: median pair market +5D -1.33%, +20D -1.05% (pairs=3)

### KOSDAQ_PLUS_KOSPI_EX_K200
MOMENTUM_X_REVISION:
- GENUINE_ROTATION, TRAIN: median pair market +5D -0.03%, +20D -0.26% (pairs=4)
- GENUINE_ROTATION, OOS: median pair market +5D -0.11%, +20D +1.10% (pairs=2)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D +0.38%, +20D +1.23% (pairs=4)
- DEFENSIVE_ROTATION, OOS: median pair market +5D -1.30%, +20D -0.16% (pairs=1)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D +0.70%, +20D +4.90% (pairs=4)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D -0.06%, +20D -1.40% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D +0.34%, +20D +0.56% (pairs=4)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +0.84%, +20D +2.39% (pairs=4)
- BROAD_BREAKDOWN, OOS: median pair market +5D -0.23%, +20D -1.60% (pairs=2)
MOMENTUM_X_VALUE:
- GENUINE_ROTATION, TRAIN: median pair market +5D +0.37%, +20D +0.64% (pairs=4)
- GENUINE_ROTATION, OOS: median pair market +5D -0.86%, +20D -2.79% (pairs=1)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D -0.07%, +20D +0.12% (pairs=4)
- DEFENSIVE_ROTATION, OOS: median pair market +5D -0.01%, +20D +2.26% (pairs=4)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D +0.37%, +20D +3.42% (pairs=3)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D +0.22%, +20D +0.24% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D +0.64%, +20D -0.12% (pairs=2)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D -2.10%, +20D -0.96% (pairs=1)
MOMENTUM_X_FLOW:
- GENUINE_ROTATION, TRAIN: median pair market +5D +1.07%, +20D -0.20% (pairs=2)
- DEFENSIVE_ROTATION, TRAIN: median pair market +5D -0.49%, +20D +0.08% (pairs=4)
- DEFENSIVE_ROTATION, OOS: median pair market +5D -0.04%, +20D +2.35% (pairs=2)
- BULLISH_STYLE_SHIFT, TRAIN: median pair market +5D +0.21%, +20D +0.67% (pairs=4)
- BROAD_CONFIRMATION, TRAIN: median pair market +5D -0.27%, +20D -1.80% (pairs=4)
- BROAD_CONFIRMATION, OOS: median pair market +5D +0.21%, +20D +0.67% (pairs=4)
- BROAD_BREAKDOWN, TRAIN: median pair market +5D +0.36%, +20D +1.84% (pairs=4)
- BROAD_BREAKDOWN, OOS: median pair market +5D +0.01%, +20D +1.71% (pairs=2)

## Rotation contrast stability

### MOMENTUM_X_REVISION
- BULLISH_SHIFT_MINUS_BROAD_CONFIRMATION / mkt_5d_diff: sign stability 50% (n=10), median TRAIN +0.45%, OOS -0.42%
- BULLISH_SHIFT_MINUS_BROAD_CONFIRMATION / mkt_20d_diff: sign stability 20% (n=10), median TRAIN +2.39%, OOS -2.86%
- GENUINE_ROTATION_MINUS_BROAD_CONFIRMATION / mkt_5d_diff: sign stability 45% (n=11), median TRAIN -0.07%, OOS -1.33%
- GENUINE_ROTATION_MINUS_BROAD_CONFIRMATION / mkt_20d_diff: sign stability 27% (n=11), median TRAIN +0.35%, OOS -5.07%

### MOMENTUM_X_VALUE
- GENUINE_MINUS_DEFENSIVE_ROTATION / mkt_5d_diff: sign stability 50% (n=4), median TRAIN +0.21%, OOS -0.43%
- GENUINE_MINUS_DEFENSIVE_ROTATION / mkt_20d_diff: sign stability 100% (n=4), median TRAIN +1.25%, OOS +1.16%
- GENUINE_ROTATION_MINUS_BROAD_CONFIRMATION / mkt_5d_diff: sign stability 50% (n=6), median TRAIN +0.27%, OOS -0.42%
- GENUINE_ROTATION_MINUS_BROAD_CONFIRMATION / mkt_20d_diff: sign stability 67% (n=6), median TRAIN +1.25%, OOS -2.50%
- BULLISH_SHIFT_MINUS_BROAD_CONFIRMATION / mkt_5d_diff: sign stability 50% (n=2), median TRAIN +0.11%, OOS -0.31%
- BULLISH_SHIFT_MINUS_BROAD_CONFIRMATION / mkt_20d_diff: sign stability 100% (n=2), median TRAIN -1.13%, OOS -2.54%

### MOMENTUM_X_FLOW
- GENUINE_MINUS_DEFENSIVE_ROTATION / mkt_5d_diff: sign stability 0% (n=1), median TRAIN +1.13%, OOS -2.25%
- GENUINE_MINUS_DEFENSIVE_ROTATION / mkt_20d_diff: sign stability 0% (n=1), median TRAIN +1.63%, OOS -0.55%
- GENUINE_ROTATION_MINUS_BROAD_CONFIRMATION / mkt_5d_diff: sign stability 0% (n=2), median TRAIN +0.34%, OOS -2.62%
- GENUINE_ROTATION_MINUS_BROAD_CONFIRMATION / mkt_20d_diff: sign stability 50% (n=2), median TRAIN +1.66%, OOS -5.64%
- BULLISH_SHIFT_MINUS_BROAD_CONFIRMATION / mkt_5d_diff: sign stability 33% (n=3), median TRAIN +1.42%, OOS -0.22%
- BULLISH_SHIFT_MINUS_BROAD_CONFIRMATION / mkt_20d_diff: sign stability 0% (n=3), median TRAIN +4.43%, OOS -2.43%

## Research-structure guardrails

- Do not call a relative W state 'bullish' without checking the absolute preferred leg.
- Do not call Momentum R + Other W a rotation until the absolute legs distinguish genuine rotation from defensive relative performance.
- Breadth is a summary layer, not the primitive state variable; preserve factor identity and both absolute legs first.
- The next validation stage should use expanding/rolling walk-forward thresholds rather than reusing 2023+ as an untouched OOS sample.
