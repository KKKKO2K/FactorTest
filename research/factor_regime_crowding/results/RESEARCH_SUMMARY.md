# Crowding / Participation Regime Screen — Mixed OPFY1+CF20

- Frozen FACTOR_20D HIGH cutoff: 0.625.
- Candidate features are computed only from information available by the signal close; forward sleeve returns start the next trading day.
- Economic adverse direction is pre-specified: low participation is bad; high dispersion/concentration/activity/holding persistence/cross-factor overlap is bad.
- Feature cutoffs are TRAIN 2016-22 terciles only and frozen thereafter.
- A screen PASS requires adverse 20D Net60 forward return in both 2016-19 and 2020-22, same adverse sign in 2023-24, <=40% false-positive rate during healthy 2025 HIGH dates, and >=50% capture of negative 2026 HIGH dates.

## Results

- SELECTED_RET20_DISPERSION (HIGH_BAD, cutoff=0.1491): early d=+0.31%, late d=+1.24%, OOS d=+0.03%, 2025 flag=82%, 2026 negative capture=92%, 2026 bad mean=-9.19%; PASS=False
- UNIVERSE_POS20_BREADTH (LOW_BAD, cutoff=0.3215): early d=+0.64%, late d=-3.09%, OOS d=-4.43%, 2025 flag=18%, 2026 negative capture=50%, 2026 bad mean=-8.15%; PASS=False
- SELECTED_TOP5_POS_CONC (HIGH_BAD, cutoff=0.7184): early d=+1.83%, late d=-0.41%, OOS d=-0.88%, 2025 flag=23%, 2026 negative capture=50%, 2026 bad mean=-8.87%; PASS=False
- SELECTED_POS20_BREADTH (LOW_BAD, cutoff=0.6500): early d=-0.08%, late d=+0.76%, OOS d=-1.69%, 2025 flag=14%, 2026 negative capture=42%, 2026 bad mean=-12.75%; PASS=False
- SELECTED_ACT5_RANK_MEDIAN (HIGH_BAD, cutoff=0.6566): early d=+1.45%, late d=+0.84%, OOS d=-0.65%, 2025 flag=36%, 2026 negative capture=42%, 2026 bad mean=-8.06%; PASS=False
- SELECTED_ACT5_GT1_SHARE (HIGH_BAD, cutoff=0.5000): early d=+2.71%, late d=+1.26%, OOS d=-2.93%, 2025 flag=68%, 2026 negative capture=42%, 2026 bad mean=-9.48%; PASS=False
- OP12_OVERLAP (HIGH_BAD, cutoff=0.7500): early d=+2.37%, late d=+2.43%, OOS d=+6.49%, 2025 flag=5%, 2026 negative capture=25%, 2026 bad mean=-6.99%; PASS=False
- MOMENTUM_OVERLAP (HIGH_BAD, cutoff=0.4000): early d=-0.47%, late d=-3.22%, OOS d=+9.00%, 2025 flag=18%, 2026 negative capture=17%, 2026 bad mean=-16.34%; PASS=False
- HOLDING_RETENTION_4STATE (HIGH_BAD, cutoff=0.2500): early d=-1.44%, late d=-3.57%, OOS d=-2.80%, 2025 flag=9%, 2026 negative capture=0%, 2026 bad mean=NA; PASS=False
- ALL_FACTOR_MULTIPLICITY (HIGH_BAD, cutoff=0.2929): early d=+1.00%, late d=+0.82%, OOS d=+9.41%, 2025 flag=9%, 2026 negative capture=0%, 2026 bad mean=NA; PASS=False

## Passed features

- None.

## 2025 vs 2026 HIGH-state feature medians

- UNIVERSE_POS20_BREADTH: 2025 0.4702 vs 2026 0.2868
- SELECTED_POS20_BREADTH: 2025 0.8500 vs 2026 0.7000
- SELECTED_RET20_DISPERSION: 2025 0.2143 vs 2026 0.2747
- SELECTED_TOP5_POS_CONC: 2025 0.6059 vs 2026 0.7409
- SELECTED_ACT5_GT1_SHARE: 2025 0.5250 vs 2026 0.4105
- SELECTED_ACT5_RANK_MEDIAN: 2025 0.6458 vs 2026 0.6432
- HOLDING_RETENTION_4STATE: 2025 0.1500 vs 2026 0.1500
- MOMENTUM_OVERLAP: 2025 0.2500 vs 2026 0.2000
- OP12_OVERLAP: 2025 0.5750 vs 2026 0.6000
- ALL_FACTOR_MULTIPLICITY: 2025 0.2179 vs 2026 0.1964

## Guardrails

- This is a pre-specified feature screen, not permission to combine near-misses into a multivariate rule.
- 2025 is used only as a healthy-HIGH false-positive control; 2026 is a stress/capture check.
- Any passing single feature must next survive exact daily-NAV 10-phase Gross/Net30/Net60 testing before it can become an exposure rule.
- 2023+ remains robustness evidence rather than pristine untouched OOS because prior research iterations used later data.