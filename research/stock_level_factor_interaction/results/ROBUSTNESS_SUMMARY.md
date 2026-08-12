# Stock-Level Factor Interaction — Robustness Validation

This validation decomposes the previously matched 30-bps-net edge into gross stock-selection alpha and turnover/cost contribution. Inference uses 4-rebalance-date moving-block bootstrap on date-level factor-averaged deltas.

## Candidates with positive NET and GROSS edge in all three core blocks

- KOSDAQ_PLUS_KOSPI_EX_K200 SIBLING_W20: net +0.04% -> +0.13% -> +0.34%; gross +0.06% -> +0.15% -> +0.36%; positive families 2/4 -> 3/4 -> 2/4; 2025 net +0.29%; 2026 net +1.40%
- KOSPI_KOSDAQ_ALL SIBLING_W20: net +0.06% -> +0.28% -> +0.31%; gross +0.08% -> +0.29% -> +0.33%; positive families 3/4 -> 3/4 -> 3/4; 2025 net +0.38%; 2026 net +1.60%
- KOSDAQ_PLUS_KOSPI_EX_K200 CROSS_FAMILY_W10: net +0.03% -> +0.05% -> +0.10%; gross +0.04% -> +0.05% -> +0.10%; positive families 3/4 -> 3/4 -> 3/4; 2025 net +0.20%; 2026 net +0.09%
- KOSDAQ_PLUS_KOSPI_EX_K200 CROSS_FAMILY_W20: net +0.08% -> +0.17% -> +0.09%; gross +0.09% -> +0.19% -> +0.11%; positive families 3/4 -> 4/4 -> 3/4; 2025 net +0.43%; 2026 net +0.47%
- KOSPI_KOSDAQ_ALL CROSS_FAMILY_W20: net +0.13% -> +0.17% -> +0.06%; gross +0.15% -> +0.19% -> +0.08%; positive families 3/4 -> 4/4 -> 3/4; 2025 net +0.44%; 2026 net +1.10%
- K200 SIBLING_W20: net +0.02% -> +0.01% -> +0.04%; gross +0.02% -> +0.02% -> +0.05%; positive families 2/4 -> 3/4 -> 2/4; 2025 net +0.15%; 2026 net -0.07%
- KOSPI_ALL CROSS_FAMILY_W20: net +0.03% -> +0.06% -> +0.04%; gross +0.03% -> +0.07% -> +0.06%; positive families 2/4 -> 4/4 -> 3/4; 2025 net +0.26%; 2026 net +0.18%
- KOSDAQ CROSS_FAMILY_W20: net +0.04% -> +0.06% -> +0.04%; gross +0.04% -> +0.07% -> +0.05%; positive families 3/4 -> 3/4 -> 2/4; 2025 net +0.03%; 2026 net +0.53%
- KOSPI_ALL CROSS_FAMILY_W10: net +0.03% -> +0.06% -> +0.01%; gross +0.03% -> +0.06% -> +0.02%; positive families 4/4 -> 4/4 -> 3/4; 2025 net +0.27%; 2026 net +0.11%

## Block-bootstrap — core candidate overlays

### K200 SIBLING_W20
- EARLY_2016_2019: +0.02%/10D; 95% CI [-0.06%, +0.10%], P(edge>0) 66%, n=98
- LATE_2020_2022: +0.01%/10D; 95% CI [-0.12%, +0.15%], P(edge>0) 56%, n=75
- NORMAL_2023_2024: +0.04%/10D; 95% CI [-0.10%, +0.18%], P(edge>0) 73%, n=48
### KOSDAQ CROSS_FAMILY_W20
- EARLY_2016_2019: +0.04%/10D; 95% CI [-0.03%, +0.10%], P(edge>0) 88%, n=98
- LATE_2020_2022: +0.06%/10D; 95% CI [-0.11%, +0.23%], P(edge>0) 73%, n=75
- NORMAL_2023_2024: +0.04%/10D; 95% CI [-0.16%, +0.24%], P(edge>0) 64%, n=48
### KOSDAQ_PLUS_KOSPI_EX_K200 CROSS_FAMILY_W10
- EARLY_2016_2019: +0.03%/10D; 95% CI [-0.02%, +0.09%], P(edge>0) 89%, n=98
- LATE_2020_2022: +0.05%/10D; 95% CI [-0.06%, +0.16%], P(edge>0) 79%, n=75
- NORMAL_2023_2024: +0.10%/10D; 95% CI [-0.08%, +0.27%], P(edge>0) 86%, n=48
### KOSDAQ_PLUS_KOSPI_EX_K200 CROSS_FAMILY_W20
- EARLY_2016_2019: +0.08%/10D; 95% CI [-0.02%, +0.18%], P(edge>0) 95%, n=98
- LATE_2020_2022: +0.17%/10D; 95% CI [-0.06%, +0.41%], P(edge>0) 93%, n=75
- NORMAL_2023_2024: +0.09%/10D; 95% CI [-0.20%, +0.36%], P(edge>0) 74%, n=48
### KOSDAQ_PLUS_KOSPI_EX_K200 SIBLING_W20
- EARLY_2016_2019: +0.04%/10D; 95% CI [-0.08%, +0.17%], P(edge>0) 75%, n=98
- LATE_2020_2022: +0.13%/10D; 95% CI [-0.04%, +0.31%], P(edge>0) 93%, n=75
- NORMAL_2023_2024: +0.34%/10D; 95% CI [-0.00%, +0.67%], P(edge>0) 97%, n=48
### KOSPI_ALL CROSS_FAMILY_W10
- EARLY_2016_2019: +0.03%/10D; 95% CI [-0.03%, +0.09%], P(edge>0) 84%, n=98
- LATE_2020_2022: +0.06%/10D; 95% CI [-0.07%, +0.18%], P(edge>0) 81%, n=75
- NORMAL_2023_2024: +0.01%/10D; 95% CI [-0.14%, +0.15%], P(edge>0) 59%, n=48
### KOSPI_ALL CROSS_FAMILY_W20
- EARLY_2016_2019: +0.03%/10D; 95% CI [-0.09%, +0.14%], P(edge>0) 69%, n=98
- LATE_2020_2022: +0.06%/10D; 95% CI [-0.13%, +0.23%], P(edge>0) 74%, n=75
- NORMAL_2023_2024: +0.04%/10D; 95% CI [-0.23%, +0.31%], P(edge>0) 62%, n=48
### KOSPI_KOSDAQ_ALL CROSS_FAMILY_W20
- EARLY_2016_2019: +0.13%/10D; 95% CI [-0.00%, +0.26%], P(edge>0) 97%, n=98
- LATE_2020_2022: +0.17%/10D; 95% CI [-0.15%, +0.50%], P(edge>0) 85%, n=75
- NORMAL_2023_2024: +0.06%/10D; 95% CI [-0.28%, +0.39%], P(edge>0) 65%, n=48
### KOSPI_KOSDAQ_ALL SIBLING_W20
- EARLY_2016_2019: +0.06%/10D; 95% CI [-0.06%, +0.19%], P(edge>0) 85%, n=98
- LATE_2020_2022: +0.28%/10D; 95% CI [+0.07%, +0.49%], P(edge>0) 99%, n=75
- NORMAL_2023_2024: +0.31%/10D; 95% CI [-0.05%, +0.68%], P(edge>0) 95%, n=48

## Cost decomposition for CROSS_FAMILY_W20

- K200 BULL_2025: gross +0.25%, net +0.24%, turnover change +2.4%; cost contribution -0.01%
- K200 EARLY_2016_2019: gross +0.03%, net +0.02%, turnover change +0.9%; cost contribution -0.00%
- K200 LATE_2020_2022: gross -0.01%, net -0.01%, turnover change +1.7%; cost contribution -0.00%
- K200 NORMAL_2023_2024: gross +0.07%, net +0.07%, turnover change +1.3%; cost contribution -0.00%
- K200 YTD_2026: gross +0.28%, net +0.27%, turnover change +2.6%; cost contribution -0.01%
- KOSDAQ BULL_2025: gross +0.04%, net +0.03%, turnover change +3.3%; cost contribution -0.01%
- KOSDAQ EARLY_2016_2019: gross +0.04%, net +0.04%, turnover change +1.1%; cost contribution -0.00%
- KOSDAQ LATE_2020_2022: gross +0.07%, net +0.06%, turnover change +3.1%; cost contribution -0.01%
- KOSDAQ NORMAL_2023_2024: gross +0.05%, net +0.04%, turnover change +3.5%; cost contribution -0.01%
- KOSDAQ YTD_2026: gross +0.54%, net +0.53%, turnover change +5.2%; cost contribution -0.02%
- KOSDAQ_PLUS_KOSPI_EX_K200 BULL_2025: gross +0.44%, net +0.43%, turnover change +4.8%; cost contribution -0.01%
- KOSDAQ_PLUS_KOSPI_EX_K200 EARLY_2016_2019: gross +0.09%, net +0.08%, turnover change +3.8%; cost contribution -0.01%
- KOSDAQ_PLUS_KOSPI_EX_K200 LATE_2020_2022: gross +0.19%, net +0.17%, turnover change +6.1%; cost contribution -0.02%
- KOSDAQ_PLUS_KOSPI_EX_K200 NORMAL_2023_2024: gross +0.11%, net +0.09%, turnover change +5.6%; cost contribution -0.02%
- KOSDAQ_PLUS_KOSPI_EX_K200 YTD_2026: gross +0.49%, net +0.47%, turnover change +6.5%; cost contribution -0.02%
- KOSPI_ALL BULL_2025: gross +0.27%, net +0.26%, turnover change +4.5%; cost contribution -0.01%
- KOSPI_ALL EARLY_2016_2019: gross +0.03%, net +0.03%, turnover change +3.0%; cost contribution -0.01%
- KOSPI_ALL LATE_2020_2022: gross +0.07%, net +0.06%, turnover change +4.9%; cost contribution -0.01%
- KOSPI_ALL NORMAL_2023_2024: gross +0.06%, net +0.04%, turnover change +5.7%; cost contribution -0.02%
- KOSPI_ALL YTD_2026: gross +0.19%, net +0.18%, turnover change +5.1%; cost contribution -0.02%
- KOSPI_EX_K200 BULL_2025: gross +0.11%, net +0.11%, turnover change +1.2%; cost contribution -0.00%
- KOSPI_EX_K200 EARLY_2016_2019: gross +0.04%, net +0.04%, turnover change +0.7%; cost contribution -0.00%
- KOSPI_EX_K200 LATE_2020_2022: gross +0.00%, net -0.00%, turnover change +2.0%; cost contribution -0.01%
- KOSPI_EX_K200 NORMAL_2023_2024: gross +0.10%, net +0.09%, turnover change +2.3%; cost contribution -0.01%
- KOSPI_EX_K200 YTD_2026: gross +0.20%, net +0.19%, turnover change +3.3%; cost contribution -0.01%
- KOSPI_KOSDAQ_ALL BULL_2025: gross +0.46%, net +0.44%, turnover change +6.9%; cost contribution -0.02%
- KOSPI_KOSDAQ_ALL EARLY_2016_2019: gross +0.15%, net +0.13%, turnover change +5.7%; cost contribution -0.02%
- KOSPI_KOSDAQ_ALL LATE_2020_2022: gross +0.19%, net +0.17%, turnover change +8.2%; cost contribution -0.02%
- KOSPI_KOSDAQ_ALL NORMAL_2023_2024: gross +0.08%, net +0.06%, turnover change +8.7%; cost contribution -0.03%
- KOSPI_KOSDAQ_ALL YTD_2026: gross +1.13%, net +1.10%, turnover change +9.1%; cost contribution -0.03%

## Decision rule

- Do not call the overlay structural if net edge is produced only by lower turnover; gross edge must also be positive in 2016-19, 2020-22, and 2023-24.
- Prefer effects spread across multiple primary factor families. A single-family result is hypothesis-generating only.
- 2025/2026 remain stress diagnostics and are not used to select candidates.

