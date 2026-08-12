# Factor Pair-State Regime Research

Question: when momentum is WORKING/NEUTRAL/REVERSE, does another factor family being WORKING/NEUTRAL/REVERSE change subsequent market or factor outcomes?
Primary pairs are predeclared: MOM1M and MOM12_1 crossed with each Revision, Value, and Flow factor (12 pairs).
State variable = trailing 20D canonical factor long-short spread. Main state cut (Q33): for each universe/factor, WORKING if spread >= TRAIN 33rd percentile of |spread|, REVERSE if spread <= negative of that cut, otherwise NEUTRAL. Q25/Q50 are robustness definitions.
All state thresholds are fit on 2016-2022 TRAIN and frozen for 2023+ OOS. Future factor outcomes use the next non-overlapping 5D period or next four periods (~20D).
20D forward market/factor windows overlap across 5D state dates; inference is descriptive. This is post-discovery research, not untouched OOS.

## Main-cut (Q33) same-universe market outcomes

### K200

MOMENTUM_X_REVISION:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D +0.08%, +20D -0.03% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D +0.97%, +20D +4.27% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D -0.30%, +20D +2.46% (pairs=3)
- MOM W / Other R, OOS: median across constituent pairs market +5D +1.78%, +20D +0.68% (pairs=2)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.08%, +20D +0.48% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +1.07%, +20D +4.50% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.58%, +20D +0.42% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D +0.57%, +20D +2.87% (pairs=4)

MOMENTUM_X_VALUE:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D -0.11%, +20D +0.14% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D +0.90%, +20D +3.36% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +0.48%, +20D +1.01% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D +1.73%, +20D +6.29% (pairs=4)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.29%, +20D +0.84% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +1.65%, +20D +5.04% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +1.03%, +20D +1.24% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D -0.10%, +20D +1.42% (pairs=4)

MOMENTUM_X_FLOW:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D +0.12%, +20D +0.82% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D +1.12%, +20D +3.78% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +0.07%, +20D -0.15% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D +0.56%, +20D +1.33% (pairs=4)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.71%, +20D +1.39% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +0.68%, +20D +3.23% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.29%, +20D +0.95% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D +0.92%, +20D +3.01% (pairs=4)

### KOSPI_ALL

MOMENTUM_X_REVISION:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D -0.02%, +20D -0.10% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D +1.26%, +20D +5.19% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +0.78%, +20D +3.06% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D +0.77%, +20D -2.80% (pairs=3)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.01%, +20D +0.99% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +1.34%, +20D +3.05% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.51%, +20D +0.38% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D +0.42%, +20D +0.93% (pairs=4)

MOMENTUM_X_VALUE:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D -0.04%, +20D +0.56% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D +0.73%, +20D +2.73% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +0.07%, +20D +1.14% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D +1.09%, +20D +4.19% (pairs=4)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D -0.04%, +20D +0.56% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +1.01%, +20D +1.67% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.59%, +20D +1.18% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D +0.49%, +20D +1.55% (pairs=4)

MOMENTUM_X_FLOW:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D +0.21%, +20D +0.10% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D +0.92%, +20D +4.68% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +0.09%, +20D -0.17% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D +1.16%, +20D +3.25% (pairs=3)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.39%, +20D +1.73% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +0.49%, +20D +1.98% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.01%, +20D +1.16% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D +1.03%, +20D +2.31% (pairs=3)

### KOSPI_EX_K200

MOMENTUM_X_REVISION:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D +0.33%, +20D +0.14% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D +0.14%, +20D +1.48% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +1.09%, +20D +2.49% (pairs=3)
- MOM W / Other R, OOS: median across constituent pairs market +5D +0.02%, +20D -0.81% (pairs=4)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.03%, +20D -0.08% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +0.23%, +20D +2.57% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.27%, +20D +1.86% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D +0.85%, +20D +0.30% (pairs=4)

MOMENTUM_X_VALUE:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D +0.36%, +20D +1.03% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D +0.40%, +20D +2.60% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +0.27%, +20D +0.39% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D -0.07%, +20D -0.16% (pairs=4)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.26%, +20D +0.74% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D -0.03%, +20D -0.84% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.53%, +20D +0.77% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D +0.35%, +20D +2.39% (pairs=4)

MOMENTUM_X_FLOW:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D +0.10%, +20D +0.01% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D -0.07%, +20D +0.21% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +0.15%, +20D +0.15% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D -0.11%, +20D -0.01% (pairs=3)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.55%, +20D +1.92% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +0.48%, +20D +1.76% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D -0.21%, +20D +0.21% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D +1.10%, +20D -0.16% (pairs=3)

### KOSDAQ

MOMENTUM_X_REVISION:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D +0.39%, +20D -0.16% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D -0.59%, +20D -0.92% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +0.53%, +20D +0.14% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D +0.64%, +20D +2.24% (pairs=4)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.05%, +20D +1.51% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +0.20%, +20D +0.79% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.81%, +20D +1.58% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D -0.57%, +20D +0.24% (pairs=4)

MOMENTUM_X_VALUE:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D +0.02%, +20D -0.19% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D -0.00%, +20D -1.41% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +0.68%, +20D -0.66% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D +0.39%, +20D +1.68% (pairs=4)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.41%, +20D +0.93% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +0.06%, +20D +2.24% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.74%, +20D +2.29% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D +0.51%, +20D +1.15% (pairs=3)

MOMENTUM_X_FLOW:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D -0.27%, +20D +0.04% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D +0.08%, +20D -1.40% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +0.46%, +20D +0.08% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D +0.36%, +20D +0.92% (pairs=4)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.49%, +20D +0.95% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +0.52%, +20D +1.27% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.71%, +20D +2.92% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D -0.40%, +20D +0.16% (pairs=3)

### KOSDAQ_PLUS_KOSPI_EX_K200

MOMENTUM_X_REVISION:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D +0.40%, +20D -0.13% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D -0.27%, +20D +0.14% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +0.97%, +20D +3.12% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D -0.26%, +20D +0.70% (pairs=2)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.25%, +20D +1.56% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +0.32%, +20D +2.13% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.41%, +20D +1.05% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D -0.31%, +20D -0.56% (pairs=3)

MOMENTUM_X_VALUE:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D +0.75%, +20D +1.62% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D +0.08%, +20D -0.85% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D +0.11%, +20D +0.42% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D -0.18%, +20D +0.72% (pairs=4)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.35%, +20D +0.98% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D -0.07%, +20D +0.94% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.61%, +20D +2.92% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D +0.57%, +20D +1.74% (pairs=4)

MOMENTUM_X_FLOW:
- MOM W / Other W, TRAIN: median across constituent pairs market +5D +0.05%, +20D -0.51% (pairs=4)
- MOM W / Other W, OOS: median across constituent pairs market +5D -0.36%, +20D -0.70% (pairs=4)
- MOM W / Other R, TRAIN: median across constituent pairs market +5D -0.17%, +20D -0.36% (pairs=4)
- MOM W / Other R, OOS: median across constituent pairs market +5D -0.29%, +20D +1.66% (pairs=4)
- MOM R / Other W, TRAIN: median across constituent pairs market +5D +0.24%, +20D +0.24% (pairs=4)
- MOM R / Other W, OOS: median across constituent pairs market +5D +0.60%, +20D +1.92% (pairs=4)
- MOM R / Other R, TRAIN: median across constituent pairs market +5D +0.50%, +20D +2.45% (pairs=4)
- MOM R / Other R, OOS: median across constituent pairs market +5D -0.20%, +20D -0.35% (pairs=3)

## Predefined contrast stability

Positive MOM_W_OTHER_R_MINUS_N means that, conditional on momentum working, an outright reversal in the other factor predicts a higher outcome than the other factor merely being neutral. Negative means the reverse state is worse.
Positive MOM_R_MINUS_N_OTHER_W means that, conditional on the other factor working, an outright momentum reversal predicts a higher outcome than momentum merely being neutral.

### MOMENTUM_X_REVISION
- MOM_W_OTHER_R_MINUS_N / a_fwd_20d_diff: sign-stability 64% (n=14), median TRAIN -0.63%, OOS -0.61%
- MOM_W_OTHER_R_MINUS_N / b_fwd_20d_diff: sign-stability 64% (n=14), median TRAIN -0.58%, OOS -0.54%
- MOM_W_OTHER_R_MINUS_N / mkt_5d_diff: sign-stability 64% (n=14), median TRAIN +0.88%, OOS +0.12%
- MOM_W_OTHER_R_MINUS_W / a_fwd_20d_diff: sign-stability 60% (n=15), median TRAIN +0.15%, OOS -1.19%
- MOM_W_OTHER_R_MINUS_W / b_fwd_20d_diff: sign-stability 60% (n=15), median TRAIN -1.33%, OOS -0.07%
- MOM_R_OTHER_W_MINUS_BOTH_W / a_fwd_20d_diff: sign-stability 58% (n=24), median TRAIN +0.16%, OOS -0.21%
- MOM_W_OTHER_R_MINUS_N / mkt_20d_diff: sign-stability 57% (n=14), median TRAIN +2.66%, OOS +0.01%
- MOM_W_OTHER_R_MINUS_W / mkt_5d_diff: sign-stability 53% (n=15), median TRAIN +0.52%, OOS +0.01%
- MOM_R_MINUS_N_OTHER_W / b_fwd_20d_diff: sign-stability 50% (n=24), median TRAIN -0.10%, OOS -0.31%
- MOM_R_OTHER_W_MINUS_BOTH_W / mkt_20d_diff: sign-stability 50% (n=24), median TRAIN +0.84%, OOS +0.56%
- MOM_R_MINUS_N_OTHER_W / a_fwd_20d_diff: sign-stability 46% (n=24), median TRAIN -0.17%, OOS +0.16%
- MOM_R_MINUS_N_OTHER_W / mkt_20d_diff: sign-stability 42% (n=24), median TRAIN +0.86%, OOS +0.46%
- MOM_R_OTHER_W_MINUS_BOTH_W / b_fwd_20d_diff: sign-stability 33% (n=24), median TRAIN -0.37%, OOS +0.36%
- MOM_R_MINUS_N_OTHER_W / mkt_5d_diff: sign-stability 25% (n=24), median TRAIN -0.08%, OOS -0.01%
- MOM_R_OTHER_W_MINUS_BOTH_W / mkt_5d_diff: sign-stability 25% (n=24), median TRAIN -0.16%, OOS +0.08%
- MOM_W_OTHER_R_MINUS_W / mkt_20d_diff: sign-stability 20% (n=15), median TRAIN +2.61%, OOS -2.72%

### MOMENTUM_X_VALUE
- MOM_R_MINUS_N_OTHER_W / mkt_5d_diff: sign-stability 83% (n=24), median TRAIN +0.49%, OOS +0.60%
- MOM_R_OTHER_W_MINUS_BOTH_W / mkt_20d_diff: sign-stability 71% (n=24), median TRAIN +0.41%, OOS +1.47%
- MOM_W_OTHER_R_MINUS_N / a_fwd_20d_diff: sign-stability 64% (n=22), median TRAIN -0.98%, OOS -0.97%
- MOM_W_OTHER_R_MINUS_W / mkt_5d_diff: sign-stability 62% (n=24), median TRAIN +0.09%, OOS +0.17%
- MOM_W_OTHER_R_MINUS_N / mkt_5d_diff: sign-stability 59% (n=22), median TRAIN +0.06%, OOS +0.66%
- MOM_R_OTHER_W_MINUS_BOTH_W / mkt_5d_diff: sign-stability 58% (n=24), median TRAIN +0.02%, OOS +0.00%
- MOM_R_OTHER_W_MINUS_BOTH_W / a_fwd_20d_diff: sign-stability 54% (n=24), median TRAIN +0.47%, OOS +0.55%
- MOM_R_MINUS_N_OTHER_W / b_fwd_20d_diff: sign-stability 54% (n=24), median TRAIN -0.52%, OOS -1.06%
- MOM_R_MINUS_N_OTHER_W / mkt_20d_diff: sign-stability 54% (n=24), median TRAIN +1.17%, OOS +2.31%
- MOM_R_OTHER_W_MINUS_BOTH_W / b_fwd_20d_diff: sign-stability 50% (n=24), median TRAIN +0.13%, OOS -1.62%
- MOM_W_OTHER_R_MINUS_W / b_fwd_20d_diff: sign-stability 50% (n=24), median TRAIN +0.35%, OOS +0.96%
- MOM_W_OTHER_R_MINUS_W / mkt_20d_diff: sign-stability 42% (n=24), median TRAIN -0.13%, OOS +2.56%
- MOM_W_OTHER_R_MINUS_N / mkt_20d_diff: sign-stability 41% (n=22), median TRAIN +0.90%, OOS +0.64%
- MOM_R_MINUS_N_OTHER_W / a_fwd_20d_diff: sign-stability 38% (n=24), median TRAIN -0.38%, OOS -0.56%
- MOM_W_OTHER_R_MINUS_W / a_fwd_20d_diff: sign-stability 38% (n=24), median TRAIN -0.40%, OOS +2.04%
- MOM_W_OTHER_R_MINUS_N / b_fwd_20d_diff: sign-stability 27% (n=22), median TRAIN -0.54%, OOS +1.15%

### MOMENTUM_X_FLOW
- MOM_W_OTHER_R_MINUS_N / mkt_5d_diff: sign-stability 77% (n=22), median TRAIN -0.06%, OOS -0.31%
- MOM_W_OTHER_R_MINUS_W / mkt_20d_diff: sign-stability 68% (n=22), median TRAIN +0.10%, OOS +0.32%
- MOM_R_OTHER_W_MINUS_BOTH_W / b_fwd_20d_diff: sign-stability 67% (n=24), median TRAIN -0.19%, OOS -1.26%
- MOM_W_OTHER_R_MINUS_N / mkt_20d_diff: sign-stability 59% (n=22), median TRAIN +0.14%, OOS +0.05%
- MOM_W_OTHER_R_MINUS_W / mkt_5d_diff: sign-stability 59% (n=22), median TRAIN -0.17%, OOS +0.20%
- MOM_R_MINUS_N_OTHER_W / a_fwd_20d_diff: sign-stability 58% (n=24), median TRAIN -0.14%, OOS -0.86%
- MOM_R_OTHER_W_MINUS_BOTH_W / mkt_20d_diff: sign-stability 58% (n=24), median TRAIN +1.23%, OOS -0.03%
- MOM_R_MINUS_N_OTHER_W / mkt_5d_diff: sign-stability 58% (n=24), median TRAIN +0.64%, OOS +0.34%
- MOM_W_OTHER_R_MINUS_N / a_fwd_20d_diff: sign-stability 55% (n=22), median TRAIN +0.41%, OOS -0.11%
- MOM_R_OTHER_W_MINUS_BOTH_W / a_fwd_20d_diff: sign-stability 54% (n=24), median TRAIN -0.51%, OOS -1.65%
- MOM_R_OTHER_W_MINUS_BOTH_W / mkt_5d_diff: sign-stability 54% (n=24), median TRAIN +0.39%, OOS +0.44%
- MOM_R_MINUS_N_OTHER_W / b_fwd_20d_diff: sign-stability 50% (n=24), median TRAIN -0.02%, OOS -0.53%
- MOM_W_OTHER_R_MINUS_N / b_fwd_20d_diff: sign-stability 50% (n=22), median TRAIN +0.29%, OOS -0.34%
- MOM_R_MINUS_N_OTHER_W / mkt_20d_diff: sign-stability 46% (n=24), median TRAIN +1.22%, OOS +0.07%
- MOM_W_OTHER_R_MINUS_W / a_fwd_20d_diff: sign-stability 41% (n=22), median TRAIN +0.71%, OOS +0.22%
- MOM_W_OTHER_R_MINUS_W / b_fwd_20d_diff: sign-stability 36% (n=22), median TRAIN +0.67%, OOS -0.54%

## Guardrails

- Pair states preserve information that breadth discards, but create more cells; cell counts and TRAIN/OOS direction stability matter more than the single best return.
- WORKING vs REVERSE is economically directional; NEUTRAL is a factor-specific dead zone calibrated only from TRAIN magnitude.
- The 12 primary pairs were fixed before this run. Do not promote an isolated pair solely because its OOS return is extreme.
- Breadth remains a useful low-dimensional benchmark; this layer asks whether the identity and sign of the working factors add information beyond the count.

