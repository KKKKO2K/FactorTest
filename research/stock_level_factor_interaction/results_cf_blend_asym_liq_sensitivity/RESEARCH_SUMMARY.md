# Cross-Family Blend Weight + Asymmetric ACT5 Veto Sensitivity

No outcome-based fine tuning is used. Blend weights and ACT5 lower cutoffs are a coarse predeclared sensitivity grid. Primary reference remains Top20; H10 is the main blend-weight horizon.

## 1) H10 Top20 blend-weight plateau vs primary-only baseline — 30bp net

- w=5%: positive core cells 13/18, universes with all 3 core blocks positive 2/6, median cell edge +0.01%, mean +0.01%
- w=10%: positive core cells 14/18, universes with all 3 core blocks positive 2/6, median cell edge +0.03%, mean +0.03%
- w=15%: positive core cells 17/18, universes with all 3 core blocks positive 5/6, median cell edge +0.04%, mean +0.06%
- w=20%: positive core cells 16/18, universes with all 3 core blocks positive 4/6, median cell edge +0.06%, mean +0.06%
- w=25%: positive core cells 14/18, universes with all 3 core blocks positive 2/6, median cell edge +0.04%, mean +0.05%
- w=30%: positive core cells 13/18, universes with all 3 core blocks positive 2/6, median cell edge +0.05%, mean +0.05%
- w=40%: positive core cells 15/18, universes with all 3 core blocks positive 4/6, median cell edge +0.05%, mean +0.07%
- w=50%: positive core cells 10/18, universes with all 3 core blocks positive 2/6, median cell edge +0.01%, mean +0.04%

### Universe-level core-block edges by weight (H10, 30bp net)

#### K200
- w=5%: +0.00% -> +0.01% -> +0.02%
- w=10%: -0.01% -> +0.02% -> +0.08%
- w=15%: +0.02% -> +0.00% -> +0.09%
- w=20%: +0.02% -> -0.01% -> +0.07%
- w=25%: +0.02% -> -0.00% -> +0.11%
- w=30%: +0.03% -> +0.03% -> +0.07%
- w=40%: +0.03% -> +0.06% -> +0.13%
- w=50%: +0.01% -> +0.08% -> +0.13%
#### KOSPI_EX_K200
- w=5%: +0.01% -> -0.00% -> -0.01%
- w=10%: -0.00% -> +0.01% -> +0.01%
- w=15%: +0.01% -> +0.02% -> +0.02%
- w=20%: +0.03% -> -0.00% -> +0.09%
- w=25%: +0.04% -> -0.05% -> +0.04%
- w=30%: +0.03% -> -0.07% -> +0.04%
- w=40%: +0.03% -> -0.02% -> +0.02%
- w=50%: -0.02% -> -0.11% -> -0.06%
#### KOSPI_ALL
- w=5%: +0.01% -> +0.01% -> +0.01%
- w=10%: +0.03% -> +0.06% -> +0.01%
- w=15%: +0.05% -> +0.04% -> -0.01%
- w=20%: +0.03% -> +0.06% -> +0.04%
- w=25%: +0.00% -> +0.09% -> +0.01%
- w=30%: -0.03% -> +0.07% -> -0.04%
- w=40%: -0.02% -> +0.10% -> -0.03%
- w=50%: -0.03% -> +0.12% -> -0.06%
#### KOSDAQ
- w=5%: +0.00% -> +0.02% -> -0.05%
- w=10%: +0.02% -> +0.03% -> -0.03%
- w=15%: +0.04% -> +0.06% -> +0.02%
- w=20%: +0.04% -> +0.06% -> +0.04%
- w=25%: +0.01% -> +0.07% -> -0.03%
- w=30%: +0.05% -> +0.07% -> -0.02%
- w=40%: +0.07% -> +0.10% -> +0.02%
- w=50%: +0.06% -> +0.04% -> +0.08%
#### KOSPI_KOSDAQ_ALL
- w=5%: +0.06% -> +0.05% -> -0.01%
- w=10%: +0.07% -> +0.12% -> -0.08%
- w=15%: +0.12% -> +0.19% -> +0.03%
- w=20%: +0.13% -> +0.17% -> +0.06%
- w=25%: +0.09% -> +0.21% -> -0.02%
- w=30%: +0.10% -> +0.26% -> -0.01%
- w=40%: +0.02% -> +0.36% -> +0.06%
- w=50%: +0.02% -> +0.35% -> -0.05%
#### KOSDAQ_PLUS_KOSPI_EX_K200
- w=5%: +0.05% -> +0.07% -> -0.02%
- w=10%: +0.04% -> +0.05% -> +0.10%
- w=15%: +0.06% -> +0.15% -> +0.10%
- w=20%: +0.08% -> +0.17% -> +0.09%
- w=25%: +0.11% -> +0.14% -> +0.09%
- w=30%: +0.14% -> +0.14% -> +0.07%
- w=40%: +0.06% -> +0.16% -> +0.05%
- w=50%: -0.02% -> +0.13% -> -0.00%

### Best-weight diagnostic only (not a selection rule)

- K200 EARLY_2016_2019: best grid weight 40%, edge +0.03%
- K200 LATE_2020_2022: best grid weight 50%, edge +0.08%
- K200 NORMAL_2023_2024: best grid weight 40%, edge +0.13%
- KOSDAQ EARLY_2016_2019: best grid weight 40%, edge +0.07%
- KOSDAQ LATE_2020_2022: best grid weight 40%, edge +0.10%
- KOSDAQ NORMAL_2023_2024: best grid weight 50%, edge +0.08%
- KOSDAQ_PLUS_KOSPI_EX_K200 EARLY_2016_2019: best grid weight 30%, edge +0.14%
- KOSDAQ_PLUS_KOSPI_EX_K200 LATE_2020_2022: best grid weight 20%, edge +0.17%
- KOSDAQ_PLUS_KOSPI_EX_K200 NORMAL_2023_2024: best grid weight 15%, edge +0.10%
- KOSPI_ALL EARLY_2016_2019: best grid weight 15%, edge +0.05%
- KOSPI_ALL LATE_2020_2022: best grid weight 50%, edge +0.12%
- KOSPI_ALL NORMAL_2023_2024: best grid weight 20%, edge +0.04%
- KOSPI_EX_K200 EARLY_2016_2019: best grid weight 25%, edge +0.04%
- KOSPI_EX_K200 LATE_2020_2022: best grid weight 15%, edge +0.02%
- KOSPI_EX_K200 NORMAL_2023_2024: best grid weight 20%, edge +0.09%
- KOSPI_KOSDAQ_ALL EARLY_2016_2019: best grid weight 20%, edge +0.13%
- KOSPI_KOSDAQ_ALL LATE_2020_2022: best grid weight 40%, edge +0.36%
- KOSPI_KOSDAQ_ALL NORMAL_2023_2024: best grid weight 20%, edge +0.06%

## 2) Asymmetric ACT5 veto: top 1% + bottom n% removed from frozen CF20

PASS means positive H10 30bp-net incremental edge vs CF20 in all three core blocks.

### Top1% + Low5% veto
- K200: -0.01% -> -0.07% -> +0.08%; FAIL
- KOSPI_EX_K200: +0.02% -> +0.05% -> +0.08%; PASS
- KOSPI_ALL: +0.00% -> -0.00% -> +0.02%; FAIL
- KOSDAQ: +0.07% -> -0.04% -> +0.05%; FAIL
- KOSPI_KOSDAQ_ALL: +0.05% -> +0.04% -> +0.02%; PASS
- KOSDAQ_PLUS_KOSPI_EX_K200: +0.08% -> -0.00% -> +0.09%; FAIL
### Top1% + Low10% veto
- K200: -0.03% -> -0.09% -> +0.09%; FAIL
- KOSPI_EX_K200: +0.04% -> +0.03% -> -0.01%; FAIL
- KOSPI_ALL: +0.01% -> -0.09% -> -0.01%; FAIL
- KOSDAQ: +0.06% -> -0.03% -> +0.05%; FAIL
- KOSPI_KOSDAQ_ALL: +0.07% -> -0.01% -> +0.03%; FAIL
- KOSDAQ_PLUS_KOSPI_EX_K200: +0.09% -> -0.02% -> +0.06%; FAIL
### Top1% + Low20% veto
- K200: -0.05% -> -0.07% -> +0.07%; FAIL
- KOSPI_EX_K200: -0.02% -> -0.04% -> +0.01%; FAIL
- KOSPI_ALL: -0.05% -> -0.14% -> +0.03%; FAIL
- KOSDAQ: +0.06% -> -0.00% -> +0.07%; FAIL
- KOSPI_KOSDAQ_ALL: +0.06% -> -0.00% -> +0.05%; FAIL
- KOSDAQ_PLUS_KOSPI_EX_K200: +0.07% -> -0.04% -> -0.04%; FAIL
### Top1% + Low30% veto
- K200: -0.06% -> -0.10% -> +0.08%; FAIL
- KOSPI_EX_K200: -0.05% -> -0.12% -> -0.06%; FAIL
- KOSPI_ALL: -0.12% -> -0.13% -> +0.01%; FAIL
- KOSDAQ: +0.10% -> +0.09% -> +0.14%; PASS
- KOSPI_KOSDAQ_ALL: +0.03% -> +0.04% -> +0.01%; PASS
- KOSDAQ_PLUS_KOSPI_EX_K200: +0.07% -> -0.03% -> +0.05%; FAIL

### Does the combination beat either tail veto alone? H10, 30bp net

- Low5%: combo-minus-best-component median -0.01%; positive cells 7/18
- Low10%: combo-minus-best-component median -0.01%; positive cells 6/18
- Low20%: combo-minus-best-component median -0.04%; positive cells 5/18
- Low30%: combo-minus-best-component median -0.04%; positive cells 3/18

## Guardrails

- Do not call the highest single grid weight optimal. The decision criterion is a broad plateau with cross-period/universe stability.
- H5/H20 results and 2025/2026 are robustness/stress evidence; H10 Top20 is the primary blend sensitivity.
- The asymmetric liquidity test is incremental to frozen CF20. Top1% and bottom-n cutoffs are cross-sectional ACT5 percentiles observed at each decision date.
- Any later production rule should be chosen from a stable range, then frozen before full portfolio implementation.

