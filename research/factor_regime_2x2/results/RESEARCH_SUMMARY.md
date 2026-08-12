# Factor Breadth x Liquidity Breadth 2x2

Primary specification: Factor breadth = trailing 20D canonical factor-spread breadth; Liquidity breadth = share of stocks whose recent 5D average trading amount exceeds the strictly preceding 20D average.
Primary quadrant split: TRAIN (2016-2022) median thresholds, frozen for 2023+ OOS. Extreme-tercile corners are a robustness check.
State labels: A = Factor HIGH / Liquidity HIGH; B = Factor HIGH / Liquidity LOW; C = Factor LOW / Liquidity HIGH; D = Factor LOW / Liquidity LOW.
Forward market returns are same-universe cap-weighted returns over +1D/+5D/+20D. 20D forward windows overlap across 5D state dates, so inference is descriptive.
Because the horizons were selected after inspecting 2023+ data, this is post-discovery validation, not untouched OOS.

## Primary median-split results

### KOSPI_ALL

TRAIN:
- +1D: A +0.04% (med +0.07%, +share 52%, n=86); B +0.01% (med -0.05%, +share 48%, n=97); C +0.07% (med +0.05%, +share 58%, n=85); D -0.15% (med +0.01%, +share 51%, n=73); order C > A > B > D
- +5D: A +0.15% (med +0.34%, +share 58%, n=86); B +0.12% (med +0.25%, +share 57%, n=97); C +0.15% (med +0.24%, +share 55%, n=85); D -0.15% (med +0.02%, +share 51%, n=73); order A > C > B > D
- +20D: A +0.02% (med +0.21%, +share 52%, n=86); B +0.92% (med +1.11%, +share 61%, n=97); C +1.02% (med +1.51%, +share 62%, n=85); D -0.64% (med +0.43%, +share 52%, n=73); order C > B > A > D

OOS:
- +1D: A +0.31% (med +0.62%, +share 63%, n=46); B +0.30% (med +0.28%, +share 59%, n=46); C -0.35% (med -0.18%, +share 46%, n=28); D +0.14% (med +0.13%, +share 56%, n=55); order A > B > D > C
- +5D: A +2.03% (med +1.59%, +share 67%, n=46); B -0.26% (med +0.03%, +share 50%, n=46); C +0.13% (med +0.34%, +share 52%, n=27); D +0.57% (med +0.61%, +share 60%, n=55); order A > D > C > B
- +20D: A +6.64% (med +5.04%, +share 78%, n=46); B +1.69% (med +1.36%, +share 59%, n=44); C +1.05% (med +0.19%, +share 52%, n=27); D +1.19% (med +1.03%, +share 61%, n=54); order A > B > D > C

OOS stage context (trailing 20D -> next 20D):
- A: trailing +7.36% -> next +6.64%
- B: trailing -0.12% -> next +1.69%
- C: trailing +5.14% -> next +1.05%
- D: trailing +1.93% -> next +1.19%

Key contrasts (TRAIN -> OOS):
- +5D A-D +0.30% -> +1.46%; C-B +0.03% -> +0.40%; interaction DiD -0.27% -> +2.72%
- +20D A-D +0.66% -> +5.45%; C-B +0.10% -> -0.64%; interaction DiD -2.56% -> +5.09%

Transition checks for the stage interpretation (median split):
- ~5D: C->A 25%->19%; B->D 19%->15%; A->A 49%->59%; D->D 49%->62%
- ~20D: C->A 32%->22%; B->D 24%->30%; A->A 19%->30%; D->D 12%->31%

### KOSDAQ

TRAIN:
- +1D: A +0.10% (med +0.09%, +share 51%, n=115); B -0.09% (med +0.14%, +share 55%, n=130); C +0.32% (med +0.22%, +share 57%, n=56); D -0.32% (med -0.16%, +share 35%, n=40); order C > A > B > D
- +5D: A +0.56% (med +0.60%, +share 57%, n=115); B -0.42% (med +0.05%, +share 52%, n=130); C +0.18% (med +0.77%, +share 64%, n=56); D +0.20% (med +0.30%, +share 57%, n=40); order A > D > C > B
- +20D: A +0.15% (med +0.20%, +share 53%, n=115); B +0.02% (med +0.66%, +share 53%, n=130); C +1.46% (med +1.38%, +share 61%, n=56); D +1.04% (med +0.22%, +share 50%, n=40); order C > D > A > B

OOS:
- +1D: A -0.08% (med +0.64%, +share 62%, n=53); B +0.05% (med +0.13%, +share 55%, n=76); C -0.09% (med +0.06%, +share 50%, n=24); D +0.65% (med +0.49%, +share 68%, n=22); order D > B > A > C
- +5D: A +0.90% (med +0.85%, +share 58%, n=52); B -0.60% (med -0.63%, +share 43%, n=76); C +0.25% (med +0.69%, +share 58%, n=24); D +0.93% (med +1.32%, +share 68%, n=22); order D > A > C > B
- +20D: A +1.06% (med +1.24%, +share 65%, n=52); B -0.74% (med +0.25%, +share 55%, n=73); C +2.01% (med +2.29%, +share 58%, n=24); D +1.49% (med +2.11%, +share 55%, n=22); order C > D > A > B

OOS stage context (trailing 20D -> next 20D):
- A: trailing +4.59% -> next +1.06%
- B: trailing -3.04% -> next -0.74%
- C: trailing +6.47% -> next +2.01%
- D: trailing -0.27% -> next +1.49%

Key contrasts (TRAIN -> OOS):
- +5D A-D +0.35% -> -0.02%; C-B +0.60% -> +0.85%; interaction DiD +0.99% -> +2.19%
- +20D A-D -0.89% -> -0.43%; C-B +1.44% -> +2.74%; interaction DiD -0.28% -> +1.28%

Transition checks for the stage interpretation (median split):
- ~5D: C->A 29%->29%; B->D 10%->17%; A->A 54%->54%; D->D 35%->14%
- ~20D: C->A 30%->17%; B->D 15%->12%; A->A 27%->33%; D->D 0%->14%

## Horizon-neighbor robustness: OOS +20D median split

### KOSPI_ALL
- MAIN_F20_L5_20: A=+6.64%, B=+1.69%, C=+1.05%, D=+1.19%; order A > B > D > C; A-D +5.45%, C-B -0.64%
- ROBUST_F10_L5_20: A=+6.10%, B=+0.46%, C=+1.03%, D=+3.59%; order A > D > C > B; A-D +2.52%, C-B +0.57%
- ROBUST_F20_L1_20: A=+6.29%, B=+2.15%, C=+2.24%, D=+0.43%; order A > C > B > D; A-D +5.86%, C-B +0.09%

### KOSDAQ
- MAIN_F20_L5_20: A=+1.06%, B=-0.74%, C=+2.01%, D=+1.49%; order C > D > A > B; A-D -0.43%, C-B +2.74%
- ROBUST_F10_L5_20: A=+1.67%, B=-0.33%, C=+0.88%, D=-0.03%; order A > C > D > B; A-D +1.70%, C-B +1.20%
- ROBUST_F20_L1_20: A=+1.00%, B=-0.67%, C=+1.66%, D=+1.83%; order D > C > A > B; A-D -0.83%, C-B +2.33%

## Extreme-tercile robustness: MAIN specification, +20D

### KOSPI_ALL
- TRAIN: A=+0.15%(n=58), B=+1.18%(n=68), C=+0.44%(n=56), D=-0.64%(n=46); order B > C > A > D
- OOS: A=+6.59%(n=35), B=+1.60%(n=28), C=+1.15%(n=23), D=+0.84%(n=33); order A > B > C > D

### KOSDAQ
- TRAIN: A=-0.96%(n=46), B=+0.02%(n=63), C=+1.68%(n=68), D=+1.02%(n=51); order C > D > B > A
- OOS: A=-0.22%(n=20), B=-2.98%(n=34), C=+2.81%(n=22), D=+2.29%(n=28); order C > D > A > B

## Interpretation guardrails

- A high future return in C does not by itself prove 'early-cycle'; the C->A transition rate and trailing-return context are the direct stage checks.
- A weak future return in B does not by itself prove 'late-stage/crowding'; B->D transition and prior-return context are needed to support that label.
- A positive interaction DiD means the two breadth signals are complementary; a negative DiD means their information is more substitutive/rotation-like.
- Median quadrants are the primary exhaustive state map. Extreme-tercile corners are cleaner but use fewer observations.
- This is a regime-screening layer, not yet a production allocation rule.
