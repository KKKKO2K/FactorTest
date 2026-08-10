# Factor Regime v1

Canonical-direction factor portfolios; top-minus-bottom 20% spread plus top-20% absolute return.
5-trading-day non-overlapping factor-return periods. State at t uses only factor returns realized through t.
State terciles are estimated on 2016-2022 TRAIN and frozen for 2023+ OOS. Market returns use prior-day market-cap weights.

## Factor correlation change

- K200: avg pairwise corr TRAIN +0.11 -> OOS +0.09
- KOSPI_EX_K200: avg pairwise corr TRAIN +0.05 -> OOS +0.07
- KOSPI_ALL: avg pairwise corr TRAIN +0.09 -> OOS +0.09
- KOSDAQ: avg pairwise corr TRAIN +0.07 -> OOS +0.06
- KOSPI_KOSDAQ_ALL: avg pairwise corr TRAIN +0.08 -> OOS +0.07
- KOSDAQ_PLUS_KOSPI_EX_K200: avg pairwise corr TRAIN +0.07 -> OOS +0.07

## Same-universe market: strongest sign-stable state relations

### K200

Horizon 1D:
- AVG_CORR_24P: TRAIN H-L -0.14%, OOS H-L -0.69% (t=-0.63); low/high means +0.87%/+0.18%; same-sign=True
- AVG_CORR_12P: TRAIN H-L -0.21%, OOS H-L -0.52% (t=-0.96); low/high means +0.72%/+0.20%; same-sign=True
- LEADER_STRENGTH_12P: TRAIN H-L +0.10%, OOS H-L +0.25% (t=+0.72); low/high means +0.03%/+0.28%; same-sign=True
- MKT_ACT1_BREADTH: TRAIN H-L -0.03%, OOS H-L -0.25% (t=-0.56); low/high means +0.23%/-0.02%; same-sign=True
- LEADER_CORRECTION_1P: TRAIN H-L -0.18%, OOS H-L -0.18% (t=-0.43); low/high means +0.31%/+0.13%; same-sign=True
Horizon 5D:
- DISPERSION_LS_4P: TRAIN H-L +0.77%, OOS H-L +1.16% (t=+1.70); low/high means +0.14%/+1.30%; same-sign=True
- LEADER_STRENGTH_12P: TRAIN H-L +0.48%, OOS H-L +0.78% (t=+1.18); low/high means +0.24%/+1.02%; same-sign=True
- ABS_BREADTH_4P: TRAIN H-L +0.20%, OOS H-L +0.70% (t=+0.97); low/high means +0.58%/+1.28%; same-sign=True
- OTHERS_ABS_BREADTH_4P: TRAIN H-L +0.15%, OOS H-L +0.65% (t=+1.00); low/high means +0.58%/+1.23%; same-sign=True
- LS_BREADTH_1P: TRAIN H-L -0.29%, OOS H-L +0.35% (t=+0.60); low/high means +0.72%/+1.08%; same-sign=False
Horizon 20D:
- DISPERSION_LS_4P: TRAIN H-L +1.94%, OOS H-L +2.48% (t=+1.58); low/high means +1.35%/+3.82%; same-sign=True
- LEADER_STRENGTH_12P: TRAIN H-L +0.98%, OOS H-L +2.26% (t=+1.64); low/high means +1.59%/+3.85%; same-sign=True
- MKT_ACT1_BREADTH: TRAIN H-L +0.30%, OOS H-L +2.22% (t=+1.26); low/high means +1.65%/+3.87%; same-sign=True
- KOSDAQ_TA_SHARE: TRAIN H-L -0.73%, OOS H-L -1.88% (t=-1.12); low/high means +3.71%/+1.83%; same-sign=True
- ORTHOGONAL_ABS_BREADTH_1P: TRAIN H-L +0.16%, OOS H-L +1.38% (t=+0.71); low/high means +2.56%/+3.94%; same-sign=True

### KOSPI_EX_K200

Horizon 1D:
- ABS_BREADTH_4P: TRAIN H-L -0.08%, OOS H-L -0.35% (t=-1.00); low/high means +0.25%/-0.10%; same-sign=True
- LS_BREADTH_1P: TRAIN H-L -0.18%, OOS H-L -0.31% (t=-1.21); low/high means +0.27%/-0.04%; same-sign=True
- DISPERSION_LS_4P: TRAIN H-L -0.02%, OOS H-L -0.28% (t=-0.98); low/high means +0.18%/-0.09%; same-sign=True
- OTHERS_ABS_BREADTH_4P: TRAIN H-L -0.07%, OOS H-L -0.24% (t=-0.72); low/high means +0.15%/-0.10%; same-sign=True
- OTHERS_LS_BREADTH_4P: TRAIN H-L -0.01%, OOS H-L -0.19% (t=-0.75); low/high means +0.14%/-0.05%; same-sign=True
Horizon 5D:
- LEADER_STRENGTH_12P: TRAIN H-L -0.02%, OOS H-L -1.16% (t=-2.23); low/high means +0.81%/-0.35%; same-sign=True
- MKT_ACT1_BREADTH: TRAIN H-L +0.28%, OOS H-L +0.99% (t=+1.70); low/high means -0.06%/+0.93%; same-sign=True
- FACTOR_TOP_ACT5_BREADTH_MEAN: TRAIN H-L +0.29%, OOS H-L +0.71% (t=+1.23); low/high means -0.03%/+0.68%; same-sign=True
- MKT_ACT5_BREADTH: TRAIN H-L +0.73%, OOS H-L +0.52% (t=+0.83); low/high means +0.11%/+0.64%; same-sign=True
- OTHERS_ABS_BREADTH_4P: TRAIN H-L +0.39%, OOS H-L +0.43% (t=+0.71); low/high means -0.16%/+0.27%; same-sign=True
Horizon 20D:
- LEADER_STRENGTH_12P: TRAIN H-L -0.83%, OOS H-L -4.12% (t=-3.70); low/high means +2.99%/-1.14%; same-sign=True
- ORTHOGONAL_ABS_BREADTH_1P: TRAIN H-L +0.23%, OOS H-L +1.08% (t=+0.88); low/high means +0.69%/+1.77%; same-sign=True
- AVG_CORR_12P: TRAIN H-L +0.38%, OOS H-L +0.96% (t=+0.65); low/high means +0.57%/+1.53%; same-sign=True
- LS_BREADTH_4P: TRAIN H-L -0.50%, OOS H-L -0.77% (t=-0.77); low/high means +1.21%/+0.44%; same-sign=True
- OTHERS_LS_BREADTH_4P: TRAIN H-L -0.23%, OOS H-L -0.73% (t=-0.78); low/high means +1.44%/+0.70%; same-sign=True

### KOSPI_ALL

Horizon 1D:
- LEADER_CORRECTION_1P: TRAIN H-L -0.19%, OOS H-L -0.69% (t=-1.67); low/high means +0.57%/-0.11%; same-sign=True
- OTHERS_LS_BREADTH_4P: TRAIN H-L +0.00%, OOS H-L +0.47% (t=+1.34); low/high means -0.11%/+0.36%; same-sign=True
- AVG_CORR_24P: TRAIN H-L -0.17%, OOS H-L -0.46% (t=-0.50); low/high means +0.60%/+0.14%; same-sign=True
- MKT_ACT1_BREADTH: TRAIN H-L -0.08%, OOS H-L -0.42% (t=-0.97); low/high means +0.40%/-0.02%; same-sign=True
- AVG_CORR_12P: TRAIN H-L -0.16%, OOS H-L -0.34% (t=-0.69); low/high means +0.44%/+0.10%; same-sign=True
Horizon 5D:
- MKT_ACT5_BREADTH: TRAIN H-L +0.21%, OOS H-L +1.50% (t=+2.05); low/high means +0.07%/+1.57%; same-sign=True
- OTHERS_LS_BREADTH_4P: TRAIN H-L +0.14%, OOS H-L +0.78% (t=+1.34); low/high means +0.23%/+1.01%; same-sign=True
- ABS_BREADTH_4P: TRAIN H-L +0.18%, OOS H-L +0.58% (t=+0.75); low/high means +0.25%/+0.82%; same-sign=True
- DISPERSION_LS_4P: TRAIN H-L +0.59%, OOS H-L +0.51% (t=+0.71); low/high means +0.42%/+0.93%; same-sign=True
- LS_BREADTH_4P: TRAIN H-L +0.18%, OOS H-L +0.46% (t=+0.79); low/high means +0.42%/+0.88%; same-sign=True
Horizon 20D:
- LS_BREADTH_4P: TRAIN H-L +0.34%, OOS H-L +3.08% (t=+2.35); low/high means +1.15%/+4.22%; same-sign=True
- MKT_ACT1_BREADTH: TRAIN H-L +0.08%, OOS H-L +2.71% (t=+1.53); low/high means +2.00%/+4.71%; same-sign=True
- OTHERS_ABS_BREADTH_1P: TRAIN H-L +0.10%, OOS H-L +2.52% (t=+1.35); low/high means +1.70%/+4.23%; same-sign=True
- KOSDAQ_TA_SHARE: TRAIN H-L -0.70%, OOS H-L -1.67% (t=-1.02); low/high means +3.48%/+1.81%; same-sign=True
- ORTHOGONAL_ABS_BREADTH_1P: TRAIN H-L +0.09%, OOS H-L +1.59% (t=+0.82); low/high means +2.57%/+4.16%; same-sign=True

### KOSDAQ

Horizon 1D:
- AVG_CORR_12P: TRAIN H-L +0.08%, OOS H-L +0.97% (t=+1.76); low/high means -0.44%/+0.53%; same-sign=True
- DISPERSION_LS_4P: TRAIN H-L +0.29%, OOS H-L +0.75% (t=+1.33); low/high means -0.56%/+0.19%; same-sign=True
- OTHERS_LS_BREADTH_4P: TRAIN H-L -0.02%, OOS H-L -0.16% (t=-0.51); low/high means +0.16%/-0.01%; same-sign=True
- KOSDAQ_TA_SHARE: TRAIN H-L +0.09%, OOS H-L +0.09% (t=+0.22); low/high means -0.09%/+0.00%; same-sign=True
- LS_BREADTH_4P: TRAIN H-L -0.04%, OOS H-L -0.08% (t=-0.24); low/high means +0.11%/+0.02%; same-sign=True
Horizon 5D:
- MKT_ACT5_BREADTH: TRAIN H-L +0.64%, OOS H-L +1.60% (t=+1.76); low/high means -0.52%/+1.08%; same-sign=True
- MKT_ACT1_BREADTH: TRAIN H-L +0.78%, OOS H-L +1.53% (t=+1.63); low/high means -0.40%/+1.12%; same-sign=True
- LS_BREADTH_4P: TRAIN H-L -0.35%, OOS H-L -0.89% (t=-1.44); low/high means +0.59%/-0.30%; same-sign=True
- AVG_CORR_24P: TRAIN H-L -0.57%, OOS H-L -0.88% (t=-0.76); low/high means +0.52%/-0.36%; same-sign=True
- OTHERS_LS_BREADTH_4P: TRAIN H-L -0.27%, OOS H-L -0.73% (t=-1.20); low/high means +0.57%/-0.16%; same-sign=True
Horizon 20D:
- AVG_CORR_24P: TRAIN H-L -0.94%, OOS H-L -3.44% (t=-1.47); low/high means +0.60%/-2.84%; same-sign=True
- DISPERSION_LS_4P: TRAIN H-L +1.95%, OOS H-L +3.03% (t=+2.01); low/high means -1.92%/+1.12%; same-sign=True
- LS_BREADTH_4P: TRAIN H-L -1.89%, OOS H-L -2.77% (t=-2.33); low/high means +1.81%/-0.96%; same-sign=True
- OTHERS_LS_BREADTH_4P: TRAIN H-L -1.83%, OOS H-L -2.55% (t=-2.13); low/high means +1.90%/-0.65%; same-sign=True
- MKT_ACT1_BREADTH: TRAIN H-L +1.22%, OOS H-L +1.48% (t=+0.79); low/high means -0.45%/+1.03%; same-sign=True

### KOSPI_KOSDAQ_ALL

Horizon 1D:
- LEADER_CORRECTION_1P: TRAIN H-L -0.05%, OOS H-L -0.67% (t=-1.92); low/high means +0.64%/-0.03%; same-sign=True
- OTHERS_LS_BREADTH_4P: TRAIN H-L +0.10%, OOS H-L +0.27% (t=+0.89); low/high means -0.02%/+0.25%; same-sign=True
- DISPERSION_LS_4P: TRAIN H-L +0.04%, OOS H-L +0.23% (t=+0.52); low/high means -0.01%/+0.22%; same-sign=True
- AVG_CORR_24P: TRAIN H-L -0.20%, OOS H-L -0.19% (t=-0.22); low/high means +0.29%/+0.10%; same-sign=True
- LS_BREADTH_1P: TRAIN H-L -0.01%, OOS H-L -0.14% (t=-0.41); low/high means +0.21%/+0.07%; same-sign=True
Horizon 5D:
- MKT_ACT5_BREADTH: TRAIN H-L +0.25%, OOS H-L +1.83% (t=+2.27); low/high means +0.02%/+1.85%; same-sign=True
- MKT_ACT1_BREADTH: TRAIN H-L +0.20%, OOS H-L +1.55% (t=+2.06); low/high means +0.01%/+1.56%; same-sign=True
- FACTOR_TOP_ACT5_BREADTH_MEAN: TRAIN H-L +0.09%, OOS H-L +1.51% (t=+2.10); low/high means -0.18%/+1.33%; same-sign=True
- ABS_BREADTH_4P: TRAIN H-L +0.24%, OOS H-L +1.15% (t=+1.45); low/high means -0.25%/+0.90%; same-sign=True
- ORTHOGONAL_ABS_BREADTH_1P: TRAIN H-L +0.15%, OOS H-L +1.04% (t=+1.45); low/high means -0.00%/+1.03%; same-sign=True
Horizon 20D:
- MKT_ACT1_BREADTH: TRAIN H-L +0.83%, OOS H-L +3.61% (t=+1.98); low/high means +1.23%/+4.84%; same-sign=True
- FACTOR_TOP_ACT5_BREADTH_MEAN: TRAIN H-L +0.03%, OOS H-L +2.73% (t=+1.74); low/high means +0.74%/+3.48%; same-sign=True
- ORTHOGONAL_ABS_BREADTH_1P: TRAIN H-L +0.30%, OOS H-L +2.44% (t=+1.55); low/high means +1.14%/+3.58%; same-sign=True
- AVG_CORR_12P: TRAIN H-L -1.36%, OOS H-L -1.70% (t=-0.86); low/high means +4.14%/+2.44%; same-sign=True
- DISPERSION_LS_4P: TRAIN H-L +0.63%, OOS H-L +1.49% (t=+0.89); low/high means +1.30%/+2.79%; same-sign=True

### KOSDAQ_PLUS_KOSPI_EX_K200

Horizon 1D:
- ABS_BREADTH_4P: TRAIN H-L -0.07%, OOS H-L -0.45% (t=-1.12); low/high means +0.26%/-0.19%; same-sign=True
- OTHERS_ABS_BREADTH_4P: TRAIN H-L -0.07%, OOS H-L -0.45% (t=-1.06); low/high means +0.23%/-0.22%; same-sign=True
- DISPERSION_LS_4P: TRAIN H-L +0.29%, OOS H-L +0.09% (t=+0.30); low/high means +0.20%/+0.29%; same-sign=True
- KOSDAQ_TA_SHARE: TRAIN H-L +0.05%, OOS H-L +0.03% (t=+0.07); low/high means -0.05%/-0.03%; same-sign=True
- LS_BREADTH_4P: TRAIN H-L -0.01%, OOS H-L -0.01% (t=-0.04); low/high means +0.06%/+0.05%; same-sign=True
Horizon 5D:
- MKT_ACT1_BREADTH: TRAIN H-L +0.33%, OOS H-L +1.42% (t=+1.76); low/high means -0.39%/+1.03%; same-sign=True
- MKT_ACT5_BREADTH: TRAIN H-L +0.74%, OOS H-L +1.31% (t=+1.66); low/high means -0.34%/+0.97%; same-sign=True
- FACTOR_TOP_ACT5_BREADTH_MEAN: TRAIN H-L +1.09%, OOS H-L +1.10% (t=+1.50); low/high means -0.49%/+0.60%; same-sign=True
- OTHERS_LS_BREADTH_4P: TRAIN H-L -0.05%, OOS H-L -0.96% (t=-1.78); low/high means +0.70%/-0.26%; same-sign=True
- LEADER_CORRECTION_1P: TRAIN H-L +0.06%, OOS H-L +0.72% (t=+1.17); low/high means -0.10%/+0.62%; same-sign=True
Horizon 20D:
- LS_BREADTH_4P: TRAIN H-L -2.13%, OOS H-L -2.68% (t=-2.48); low/high means +1.84%/-0.84%; same-sign=True
- OTHERS_LS_BREADTH_4P: TRAIN H-L -1.34%, OOS H-L -2.28% (t=-2.09); low/high means +1.83%/-0.44%; same-sign=True
- MKT_ACT1_BREADTH: TRAIN H-L +1.32%, OOS H-L +1.58% (t=+0.94); low/high means -0.44%/+1.14%; same-sign=True
- MKT_ACT5_BREADTH: TRAIN H-L +0.71%, OOS H-L +1.56% (t=+0.98); low/high means -0.31%/+1.26%; same-sign=True
- ORTHOGONAL_ABS_BREADTH_1P: TRAIN H-L +0.68%, OOS H-L +1.33% (t=+1.02); low/high means -0.18%/+1.14%; same-sign=True

## Strong-leader correction events

Event = trailing ~60D factor leader strength in TRAIN-defined top tercile AND latest 5D leader spread return < 0.
High/low support is split with TRAIN medians. The key question is whether other factor portfolios staying positive matters for the next market return.

### K200
- OTHERS_ABS_BREADTH_4P, 20D: high-support +4.63% vs low-support +2.38%; diff +2.25%, t=+0.54, n=20/13
- ABS_BREADTH_1P, 20D: high-support +2.94% vs low-support +4.42%; diff -1.48%, t=-0.42, n=15/18
- OTHERS_ABS_BREADTH_4P, 1D: high-support -0.26% vs low-support +1.14%; diff -1.40%, t=-1.66, n=20/14
- ORTHOGONAL_ABS_BREADTH_1P, 1D: high-support -0.16% vs low-support +1.00%; diff -1.16%, t=-1.36, n=20/14
- OTHERS_ABS_BREADTH_1P, 5D: high-support +0.05% vs low-support +0.88%; diff -0.82%, t=-0.65, n=16/17
- ORTHOGONAL_ABS_BREADTH_1P, 20D: high-support +4.08% vs low-support +3.30%; diff +0.78%, t=+0.19, n=19/14
- OTHERS_ABS_BREADTH_1P, 1D: high-support +0.03% vs low-support +0.60%; diff -0.57%, t=-0.70, n=17/17
- ORTHOGONAL_ABS_BREADTH_1P, 5D: high-support +0.24% vs low-support +0.80%; diff -0.56%, t=-0.43, n=19/14

### KOSPI_EX_K200
- ORTHOGONAL_ABS_BREADTH_1P, 20D: high-support +3.39% vs low-support -2.82%; diff +6.21%, t=+2.68, n=10/10
- OTHERS_ABS_BREADTH_1P, 20D: high-support +3.65% vs low-support -2.47%; diff +6.13%, t=+2.66, n=9/11
- ABS_BREADTH_1P, 20D: high-support +3.65% vs low-support -2.47%; diff +6.13%, t=+2.66, n=9/11
- ORTHOGONAL_ABS_BREADTH_1P, 1D: high-support +0.80% vs low-support -2.53%; diff +3.33%, t=+2.71, n=11/10
- OTHERS_ABS_BREADTH_1P, 1D: high-support +0.83% vs low-support -2.26%; diff +3.08%, t=+2.64, n=10/11
- ABS_BREADTH_1P, 1D: high-support +0.83% vs low-support -2.26%; diff +3.08%, t=+2.64, n=10/11
- ORTHOGONAL_ABS_BREADTH_1P, 5D: high-support +0.96% vs low-support -2.03%; diff +2.99%, t=+2.34, n=10/10
- OTHERS_ABS_BREADTH_1P, 5D: high-support +0.76% vs low-support -1.60%; diff +2.35%, t=+1.73, n=9/11

### KOSPI_ALL
- OTHERS_ABS_BREADTH_4P, 20D: high-support +3.68% vs low-support +0.59%; diff +3.09%, t=+0.89, n=15/13
- OTHERS_ABS_BREADTH_1P, 20D: high-support +3.65% vs low-support +1.19%; diff +2.46%, t=+0.78, n=12/16
- OTHERS_ABS_BREADTH_4P, 5D: high-support +1.21% vs low-support -0.36%; diff +1.57%, t=+1.02, n=15/13
- ORTHOGONAL_ABS_BREADTH_1P, 5D: high-support -0.17% vs low-support +1.36%; diff -1.53%, t=-1.00, n=16/12
- ABS_BREADTH_1P, 5D: high-support +1.23% vs low-support +0.13%; diff +1.10%, t=+0.65, n=9/19
- OTHERS_ABS_BREADTH_1P, 5D: high-support -0.00% vs low-support +0.85%; diff -0.85%, t=-0.52, n=12/16
- ORTHOGONAL_ABS_BREADTH_1P, 20D: high-support +2.00% vs low-support +2.57%; diff -0.57%, t=-0.15, n=16/12
- OTHERS_ABS_BREADTH_4P, 1D: high-support +0.22% vs low-support +0.75%; diff -0.54%, t=-1.04, n=15/14

### KOSDAQ
- OTHERS_ABS_BREADTH_4P, 5D: high-support +1.03% vs low-support -2.20%; diff +3.23%, t=+1.31, n=8/7
- OTHERS_ABS_BREADTH_1P, 20D: high-support +1.76% vs low-support -1.20%; diff +2.95%, t=+0.81, n=9/6
- ABS_BREADTH_1P, 5D: high-support +0.94% vs low-support -1.73%; diff +2.67%, t=+1.17, n=7/8
- ORTHOGONAL_ABS_BREADTH_1P, 20D: high-support +1.61% vs low-support -0.60%; diff +2.21%, t=+0.68, n=8/7
- ORTHOGONAL_ABS_BREADTH_1P, 5D: high-support +0.40% vs low-support -1.49%; diff +1.89%, t=+0.74, n=8/7
- ORTHOGONAL_ABS_BREADTH_1P, 1D: high-support +0.94% vs low-support -0.43%; diff +1.37%, t=+1.95, n=9/7
- ABS_BREADTH_1P, 20D: high-support +1.29% vs low-support -0.05%; diff +1.34%, t=+0.45, n=7/8
- OTHERS_ABS_BREADTH_1P, 5D: high-support +0.05% vs low-support -1.27%; diff +1.31%, t=+0.45, n=9/6

### KOSPI_KOSDAQ_ALL
- ABS_BREADTH_1P, 20D: high-support +0.60% vs low-support +3.33%; diff -2.73%, t=-1.41, n=11/10
- ORTHOGONAL_ABS_BREADTH_1P, 20D: high-support +0.93% vs low-support +3.48%; diff -2.55%, t=-1.16, n=13/8
- OTHERS_ABS_BREADTH_1P, 20D: high-support +0.91% vs low-support +3.22%; diff -2.32%, t=-1.12, n=12/9
- OTHERS_ABS_BREADTH_4P, 5D: high-support +0.76% vs low-support -0.75%; diff +1.51%, t=+0.90, n=14/7
- ORTHOGONAL_ABS_BREADTH_1P, 5D: high-support +0.77% vs low-support -0.59%; diff +1.37%, t=+0.87, n=13/8
- OTHERS_ABS_BREADTH_4P, 20D: high-support +1.55% vs low-support +2.61%; diff -1.06%, t=-0.40, n=14/7
- ABS_BREADTH_1P, 5D: high-support +0.65% vs low-support -0.18%; diff +0.84%, t=+0.56, n=11/10
- OTHERS_ABS_BREADTH_1P, 5D: high-support +0.49% vs low-support -0.06%; diff +0.55%, t=+0.35, n=12/9

### KOSDAQ_PLUS_KOSPI_EX_K200
- OTHERS_ABS_BREADTH_4P, 5D: high-support +0.99% vs low-support -2.00%; diff +2.99%, t=+1.50, n=8/10
- OTHERS_ABS_BREADTH_4P, 20D: high-support +1.05% vs low-support -0.01%; diff +1.06%, t=+0.30, n=8/10
- ABS_BREADTH_1P, 5D: high-support -0.29% vs low-support -0.92%; diff +0.63%, t=+0.32, n=7/11
- OTHERS_ABS_BREADTH_4P, 1D: high-support +0.21% vs low-support +0.55%; diff -0.34%, t=-0.31, n=8/11
- ABS_BREADTH_1P, 1D: high-support +0.60% vs low-support +0.26%; diff +0.34%, t=+0.30, n=8/11
- ABS_BREADTH_1P, 20D: high-support +0.29% vs low-support +0.57%; diff -0.27%, t=-0.08, n=7/11
- OTHERS_ABS_BREADTH_1P, 5D: high-support -0.55% vs low-support -0.77%; diff +0.22%, t=+0.11, n=8/10
- ORTHOGONAL_ABS_BREADTH_1P, 5D: high-support -0.55% vs low-support -0.77%; diff +0.22%, t=+0.11, n=8/10

## Guardrails

- This is screening, not a production timing model.
- 20D forward returns overlap across 5D state dates, so naïve t-stats overstate formal significance.
- Only TRAIN/OOS sign-stable states should be eligible for a later small composite; do not select on OOS magnitude alone.

