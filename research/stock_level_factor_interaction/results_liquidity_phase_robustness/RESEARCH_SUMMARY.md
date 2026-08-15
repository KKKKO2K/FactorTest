# H10 Liquidity Rebalance-Phase Robustness

Each candidate is frozen from the prior H10 screen. All 10 possible non-overlapping 10-trading-day rebalance offsets are evaluated.

Headline fields are mean edge across phases, worst phase, and positive phase count. 30bp turnover cost is included.

## KOSPI_EX_K200

### ACT5 LOW10
- EARLY_2016_2019: mean +0.01%; median +0.01%; worst -0.00%; +phases 9/10
- LATE_2020_2022: mean +0.00%; median +0.02%; worst -0.07%; +phases 6/10
- NORMAL_2023_2024: mean +0.07%; median +0.08%; worst +0.01%; +phases 10/10
- BULL_2025: mean +0.00%; median -0.02%; worst -0.07%; +phases 4/10
- YTD_2026: mean +0.16%; median +0.17%; worst +0.01%; +phases 10/10

### ADV20 LOW10
- EARLY_2016_2019: mean +0.00%; median +0.00%; worst -0.01%; +phases 5/10
- LATE_2020_2022: mean +0.01%; median +0.01%; worst -0.01%; +phases 8/10
- NORMAL_2023_2024: mean +0.03%; median +0.03%; worst +0.02%; +phases 10/10
- BULL_2025: mean +0.00%; median +0.00%; worst -0.01%; +phases 5/10
- YTD_2026: mean +0.07%; median +0.06%; worst +0.00%; +phases 10/10

### TURNOVER20 TOP01
- EARLY_2016_2019: mean +0.04%; median +0.03%; worst +0.02%; +phases 10/10
- LATE_2020_2022: mean +0.00%; median +0.01%; worst -0.02%; +phases 6/10
- NORMAL_2023_2024: mean +0.05%; median +0.05%; worst +0.01%; +phases 10/10
- BULL_2025: mean +0.07%; median +0.07%; worst +0.04%; +phases 10/10
- YTD_2026: mean +0.12%; median +0.09%; worst -0.06%; +phases 9/10

### TURNOVER20 TOP01_LOW10
- EARLY_2016_2019: mean +0.03%; median +0.03%; worst +0.00%; +phases 10/10
- LATE_2020_2022: mean +0.02%; median +0.02%; worst -0.01%; +phases 9/10
- NORMAL_2023_2024: mean +0.04%; median +0.04%; worst +0.01%; +phases 10/10
- BULL_2025: mean +0.05%; median +0.06%; worst +0.01%; +phases 10/10
- YTD_2026: mean +0.05%; median +0.06%; worst -0.17%; +phases 7/10

### AMIHUD20 TOP05
- EARLY_2016_2019: mean +0.01%; median +0.01%; worst -0.00%; +phases 7/10
- LATE_2020_2022: mean +0.01%; median +0.01%; worst -0.00%; +phases 9/10
- NORMAL_2023_2024: mean +0.03%; median +0.03%; worst +0.01%; +phases 10/10
- BULL_2025: mean -0.00%; median -0.00%; worst -0.03%; +phases 5/10
- YTD_2026: mean +0.06%; median +0.06%; worst -0.00%; +phases 9/10

## KOSDAQ

### ACT5 LOW30
- EARLY_2016_2019: mean +0.04%; median +0.05%; worst -0.04%; +phases 8/10
- LATE_2020_2022: mean +0.00%; median -0.01%; worst -0.11%; +phases 4/10
- NORMAL_2023_2024: mean +0.07%; median +0.06%; worst -0.01%; +phases 7/10
- BULL_2025: mean +0.07%; median +0.07%; worst +0.02%; +phases 10/10
- YTD_2026: mean -0.15%; median -0.07%; worst -0.73%; +phases 3/10

### TURNOVER20 LOW30
- EARLY_2016_2019: mean +0.07%; median +0.07%; worst +0.03%; +phases 10/10
- LATE_2020_2022: mean -0.01%; median -0.01%; worst -0.05%; +phases 4/10
- NORMAL_2023_2024: mean +0.10%; median +0.09%; worst +0.06%; +phases 10/10
- BULL_2025: mean +0.07%; median +0.07%; worst -0.01%; +phases 9/10
- YTD_2026: mean +0.01%; median -0.03%; worst -0.15%; +phases 4/10

### TURNOVER20 TOP01_LOW30
- EARLY_2016_2019: mean +0.08%; median +0.07%; worst +0.04%; +phases 10/10
- LATE_2020_2022: mean +0.01%; median +0.03%; worst -0.06%; +phases 7/10
- NORMAL_2023_2024: mean +0.11%; median +0.10%; worst +0.03%; +phases 10/10
- BULL_2025: mean +0.07%; median +0.08%; worst -0.05%; +phases 8/10
- YTD_2026: mean -0.03%; median -0.07%; worst -0.25%; +phases 4/10

### ACT1 LOW05
- EARLY_2016_2019: mean +0.05%; median +0.05%; worst +0.03%; +phases 10/10
- LATE_2020_2022: mean -0.00%; median +0.00%; worst -0.04%; +phases 5/10
- NORMAL_2023_2024: mean +0.03%; median +0.04%; worst -0.01%; +phases 9/10
- BULL_2025: mean +0.02%; median +0.01%; worst -0.01%; +phases 8/10
- YTD_2026: mean -0.00%; median -0.01%; worst -0.12%; +phases 5/10

### AMIHUD20 TOP05
- EARLY_2016_2019: mean +0.04%; median +0.04%; worst +0.03%; +phases 10/10
- LATE_2020_2022: mean +0.01%; median +0.01%; worst -0.01%; +phases 8/10
- NORMAL_2023_2024: mean +0.01%; median +0.01%; worst +0.00%; +phases 10/10
- BULL_2025: mean +0.01%; median +0.01%; worst -0.00%; +phases 9/10
- YTD_2026: mean -0.02%; median -0.01%; worst -0.04%; +phases 1/10

## Guardrails

- Phase robustness is diagnostic; no candidate/cutoff is changed based on the best phase.
- A production-worthy veto should not depend on one arbitrary rebalance offset. Mean and worst-phase behavior matter more than the best phase.
- Large intermediates are retained as GitHub-safe chunked gzip CSVs with manifests.
