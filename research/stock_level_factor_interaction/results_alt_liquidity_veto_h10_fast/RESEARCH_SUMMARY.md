# Alternative Liquidity Veto Sensitivity

CF20 is frozen. This test asks whether the ACT5 tail-veto result generalizes to other economically plausible liquidity measures. No outcome-based threshold tuning is used.

Metrics: ACT5 benchmark; ADV20 = 20D average trading amount; TURNOVER20 = 20D average trading amount / market cap; ACT1 = current trading amount / strictly-prior 20D average; AMIHUD20 = 20D average |return| / trading amount.

## H10 Top20 stable PASS specifications (30bp net vs CF20)

### ACT5
- KOSPI_EX_K200 TOP01_LOW05: +0.02%->+0.05%->+0.08%; positive-family counts {'EARLY_2016_2019': 3, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 2}
- KOSPI_EX_K200 TOP05_LOW05: +0.03%->+0.06%->+0.04%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 3}
- KOSDAQ TOP01_LOW30: +0.10%->+0.09%->+0.14%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 4}
- KOSDAQ TOP05_LOW05: +0.03%->+0.02%->+0.11%; positive-family counts {'EARLY_2016_2019': 3, 'LATE_2020_2022': 2, 'NORMAL_2023_2024': 4}
- KOSDAQ TOP05_LOW10: +0.01%->+0.01%->+0.11%; positive-family counts {'EARLY_2016_2019': 3, 'LATE_2020_2022': 2, 'NORMAL_2023_2024': 4}
- KOSDAQ TOP05_LOW20: +0.01%->+0.04%->+0.12%; positive-family counts {'EARLY_2016_2019': 2, 'LATE_2020_2022': 2, 'NORMAL_2023_2024': 4}
- KOSDAQ TOP05_LOW30: +0.07%->+0.13%->+0.16%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 4}
- KOSPI_KOSDAQ_ALL TOP01_LOW05: +0.05%->+0.04%->+0.02%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 4, 'NORMAL_2023_2024': 1}
- KOSPI_KOSDAQ_ALL TOP01_LOW30: +0.03%->+0.04%->+0.01%; positive-family counts {'EARLY_2016_2019': 3, 'LATE_2020_2022': 4, 'NORMAL_2023_2024': 2}
- KOSPI_KOSDAQ_ALL TOP05_LOW05: +0.02%->+0.02%->+0.08%; positive-family counts {'EARLY_2016_2019': 3, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 3}
- KOSPI_KOSDAQ_ALL TOP05_LOW20: +0.03%->+0.01%->+0.10%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 2, 'NORMAL_2023_2024': 3}
- KOSDAQ_PLUS_KOSPI_EX_K200 TOP05_LOW05: +0.05%->+0.10%->+0.08%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 4, 'NORMAL_2023_2024': 2}
- KOSDAQ_PLUS_KOSPI_EX_K200 TOP05_LOW10: +0.05%->+0.08%->+0.03%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 4, 'NORMAL_2023_2024': 2}
- KOSDAQ_PLUS_KOSPI_EX_K200 TOP05_LOW30: +0.06%->+0.05%->+0.11%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 3}
### ADV20
- KOSPI_ALL TOP01_LOW05: +0.01%->+0.01%->+0.01%; positive-family counts {'EARLY_2016_2019': 3, 'LATE_2020_2022': 4, 'NORMAL_2023_2024': 2}
- KOSPI_ALL TOP01_LOW10: +0.01%->+0.01%->+0.01%; positive-family counts {'EARLY_2016_2019': 3, 'LATE_2020_2022': 4, 'NORMAL_2023_2024': 2}
- KOSPI_ALL TOP01_LOW20: +0.01%->+0.02%->+0.01%; positive-family counts {'EARLY_2016_2019': 3, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 2}
- KOSPI_ALL TOP01_LOW30: +0.00%->+0.02%->+0.00%; positive-family counts {'EARLY_2016_2019': 2, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 3}
### TURNOVER20
- KOSPI_EX_K200 TOP01_LOW05: +0.06%->+0.03%->+0.05%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 3}
- KOSPI_EX_K200 TOP01_LOW10: +0.05%->+0.07%->+0.04%; positive-family counts {'EARLY_2016_2019': 3, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 3}
- KOSPI_ALL TOP01_LOW05: +0.02%->+0.04%->+0.01%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 2}
- KOSPI_ALL TOP01_LOW10: +0.03%->+0.06%->+0.00%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 2}
- KOSPI_ALL TOP05_LOW10: +0.01%->+0.01%->+0.04%; positive-family counts {'EARLY_2016_2019': 3, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 3}
- KOSDAQ TOP01_LOW05: +0.03%->+0.03%->+0.00%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 2, 'NORMAL_2023_2024': 2}
- KOSDAQ TOP01_LOW10: +0.07%->+0.06%->+0.00%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 2}
- KOSDAQ TOP01_LOW20: +0.07%->+0.07%->+0.02%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 3}
- KOSDAQ TOP01_LOW30: +0.11%->+0.05%->+0.06%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 4, 'NORMAL_2023_2024': 3}
- KOSDAQ TOP05_LOW20: +0.14%->+0.03%->+0.04%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 2, 'NORMAL_2023_2024': 3}
- KOSDAQ TOP05_LOW30: +0.18%->+0.02%->+0.07%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 1, 'NORMAL_2023_2024': 3}
- KOSPI_KOSDAQ_ALL TOP01_LOW05: +0.06%->+0.06%->+0.00%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 3, 'NORMAL_2023_2024': 2}
### ACT1
- KOSPI_EX_K200 TOP01_LOW05: +0.03%->+0.01%->+0.12%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 2, 'NORMAL_2023_2024': 4}
- KOSPI_EX_K200 TOP01_LOW10: +0.01%->+0.00%->+0.15%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 2, 'NORMAL_2023_2024': 3}
- KOSDAQ TOP01_LOW05: +0.05%->+0.01%->+0.03%; positive-family counts {'EARLY_2016_2019': 4, 'LATE_2020_2022': 4, 'NORMAL_2023_2024': 2}
- KOSDAQ TOP01_LOW10: +0.02%->+0.02%->+0.03%; positive-family counts {'EARLY_2016_2019': 3, 'LATE_2020_2022': 2, 'NORMAL_2023_2024': 2}
### AMIHUD20
- no combined top+bottom veto passes all three core blocks

## Combination incremental value versus its two component vetoes

- ACT5: combo-minus-best-component median -0.02%; positive cells 41/144
- ADV20: combo-minus-best-component median -0.02%; positive cells 45/144
- TURNOVER20: combo-minus-best-component median -0.00%; positive cells 62/144
- ACT1: combo-minus-best-component median -0.04%; positive cells 19/144
- AMIHUD20: combo-minus-best-component median -0.06%; positive cells 21/144

## Metric-level one-sided veto stability, H10

### ACT5
- TOP01: stable in KOSPI_EX_K200, KOSDAQ_PLUS_KOSPI_EX_K200
- TOP05: stable in KOSPI_EX_K200, KOSDAQ, KOSPI_KOSDAQ_ALL, KOSDAQ_PLUS_KOSPI_EX_K200
- LOW05: stable in KOSPI_EX_K200, KOSPI_KOSDAQ_ALL
- LOW10: stable in KOSPI_EX_K200
- LOW20: stable in KOSDAQ
- LOW30: stable in KOSDAQ, KOSPI_KOSDAQ_ALL
### ADV20
- TOP01: stable in KOSPI_ALL
- LOW05: stable in KOSPI_EX_K200, KOSPI_ALL, KOSDAQ, KOSDAQ_PLUS_KOSPI_EX_K200
- LOW10: stable in KOSPI_EX_K200, KOSPI_ALL, KOSDAQ_PLUS_KOSPI_EX_K200
- LOW20: stable in KOSPI_EX_K200, KOSPI_ALL, KOSDAQ, KOSDAQ_PLUS_KOSPI_EX_K200
- LOW30: stable in KOSPI_EX_K200, KOSPI_ALL, KOSDAQ, KOSDAQ_PLUS_KOSPI_EX_K200
### TURNOVER20
- TOP01: stable in KOSPI_EX_K200, KOSPI_ALL, KOSPI_KOSDAQ_ALL, KOSDAQ_PLUS_KOSPI_EX_K200
- LOW05: stable in KOSPI_EX_K200, KOSPI_ALL
- LOW10: stable in KOSPI_EX_K200, KOSDAQ
- LOW20: stable in KOSDAQ
- LOW30: stable in KOSDAQ
### ACT1
- TOP01: stable in KOSDAQ_PLUS_KOSPI_EX_K200
- LOW05: stable in KOSDAQ
- LOW10: stable in KOSDAQ
- LOW20: stable in KOSDAQ
- LOW30: stable in KOSDAQ
### AMIHUD20
- TOP01: stable in KOSPI_EX_K200, KOSDAQ, KOSDAQ_PLUS_KOSPI_EX_K200
- TOP05: stable in KOSPI_EX_K200, KOSDAQ, KOSDAQ_PLUS_KOSPI_EX_K200

## Guardrails

- A PASS means positive H10 30bp-net incremental edge in all three historical core blocks for exactly the same metric/cutoff/universe.
- ACT5 is a benchmark, not a selection target. The key question is whether other metric families reproduce the same low-liquidity or extreme-activity quality-control effect.
- ADV20 and TURNOVER20 are liquidity-level measures; ACT1/ACT5 are activity-shock measures; AMIHUD20 is a price-impact illiquidity measure. Similar results across these groups would be stronger evidence of a general liquidity-quality mechanism.
- H5/H20 and 2025/2026 remain robustness/stress diagnostics and do not select cutoffs.

