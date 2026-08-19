# Mixed OPFY1+CF20 — Candidate-Specific Regime Diagnostics

Purpose: test whether the frozen Mixed FACTOR_20D signal predicts the exact finalist sleeve itself, rather than market or family-level proxy returns.
Forward sleeve returns start on the trading day after each state date. For each state date, the 10 H=10 phase forward returns are averaged first, so the sample count is state dates rather than treating phases as independent observations.
All results are descriptive; 2023+ is not pristine untouched OOS because prior research used later data for discovery.

## HIGH vs NON_HIGH — exact finalist forward return

### TRAIN_2016_2022
- 5D: HIGH +0.13% (n=167, pos=55%) vs NON_HIGH +0.22% (n=174, pos=58%); H-N -0.09%
- 10D: HIGH +0.26% (n=167, pos=58%) vs NON_HIGH +0.52% (n=174, pos=60%); H-N -0.26%
- 20D: HIGH +0.06% (n=167, pos=55%) vs NON_HIGH +1.59% (n=174, pos=61%); H-N -1.53%

### OOS_2023_2024
- 5D: HIGH -0.17% (n=39, pos=54%) vs NON_HIGH +0.27% (n=58, pos=60%); H-N -0.45%
- 10D: HIGH -0.19% (n=39, pos=46%) vs NON_HIGH +0.43% (n=58, pos=60%); H-N -0.63%
- 20D: HIGH +0.27% (n=39, pos=41%) vs NON_HIGH +0.31% (n=58, pos=60%); H-N -0.04%

### BULL_2025
- 5D: HIGH +1.67% (n=22, pos=64%) vs NON_HIGH +0.47% (n=27, pos=52%); H-N +1.20%
- 10D: HIGH +3.38% (n=22, pos=82%) vs NON_HIGH +0.80% (n=27, pos=44%); H-N +2.58%
- 20D: HIGH +4.79% (n=22, pos=82%) vs NON_HIGH +3.74% (n=27, pos=63%); H-N +1.05%

### YTD_2026
- 5D: HIGH -1.79% (n=19, pos=37%) vs NON_HIGH +3.45% (n=9, pos=67%); H-N -5.24%
- 10D: HIGH -4.01% (n=18, pos=22%) vs NON_HIGH +6.50% (n=9, pos=78%); H-N -10.51%
- 20D: HIGH -7.23% (n=16, pos=25%) vs NON_HIGH +10.67% (n=9, pos=89%); H-N -17.90%

## HIGH entry vs persistent HIGH — NET60

### TRAIN_2016_2022
- 5D: ENTRY -0.29% (n=48, pos=58%); PERSIST +0.30% (n=119, pos=54%)
- 10D: ENTRY -0.09% (n=48, pos=52%); PERSIST +0.40% (n=119, pos=61%)
- 20D: ENTRY +0.68% (n=48, pos=60%); PERSIST -0.19% (n=119, pos=53%)

### OOS_2023_2024
- 5D: ENTRY +0.83% (n=10, pos=70%); PERSIST -0.52% (n=29, pos=48%)
- 10D: ENTRY +0.40% (n=10, pos=50%); PERSIST -0.40% (n=29, pos=45%)
- 20D: ENTRY +0.14% (n=10, pos=50%); PERSIST +0.31% (n=29, pos=38%)

### BULL_2025
- 5D: ENTRY +0.91% (n=5, pos=40%); PERSIST +1.90% (n=17, pos=71%)
- 10D: ENTRY +4.61% (n=5, pos=80%); PERSIST +3.01% (n=17, pos=82%)
- 20D: ENTRY +5.31% (n=5, pos=60%); PERSIST +4.63% (n=17, pos=88%)

### YTD_2026
- 5D: ENTRY +0.58% (n=4, pos=75%); PERSIST -2.42% (n=15, pos=27%)
- 10D: ENTRY +1.64% (n=4, pos=50%); PERSIST -5.62% (n=14, pos=14%)
- 20D: ENTRY -4.12% (n=4, pos=50%); PERSIST -8.27% (n=12, pos=17%)

## HIGH x base-state — NET60 20D

### TRAIN_2016_2022
- HIGH|B1_B2: mean +0.92%, median +3.05%, pos 69%, n=32
- HIGH|B3: mean -0.86%, median -1.21%, pos 47%, n=83
- HIGH|B4: mean +1.12%, median +0.75%, pos 60%, n=50
- NON_HIGH: mean +1.59%, median +1.98%, pos 61%, n=174
- nan: mean -1.75%, median -1.75%, pos 50%, n=2

### OOS_2023_2024
- HIGH|B1_B2: mean -0.11%, median -0.65%, pos 30%, n=10
- HIGH|B3: mean +0.64%, median +0.02%, pos 50%, n=24
- HIGH|B4: mean -0.73%, median -2.62%, pos 20%, n=5
- NON_HIGH: mean +0.31%, median +0.47%, pos 60%, n=58

### BULL_2025
- HIGH|B1_B2: mean +10.52%, median +10.52%, pos 100%, n=2
- HIGH|B3: mean +4.67%, median +2.24%, pos 75%, n=8
- HIGH|B4: mean +3.91%, median +4.00%, pos 83%, n=12
- NON_HIGH: mean +3.74%, median +2.01%, pos 63%, n=27

### YTD_2026
- HIGH|B1_B2: mean -12.84%, median -11.70%, pos 0%, n=6
- HIGH|B3: mean +16.51%, median +16.51%, pos 100%, n=1
- HIGH|B4: mean -6.13%, median -6.69%, pos 33%, n=9
- NON_HIGH: mean +10.67%, median +15.25%, pos 89%, n=9

## Interpretation guardrails

- If HIGH is negative only in 2026 but not TRAIN / 2023-24 / 2025, treat it as a useful episode warning rather than a production exposure rule.
- If HIGH_ENTRY is more consistently adverse than HIGH_PERSIST across historical samples, a transition/event rule is more defensible than a persistent state throttle.
- If the sign depends strongly on B-state, return to nested conditioning before choosing an action rule.
- Do not tune new cutoffs or hold durations on 2026 in this diagnostic.
