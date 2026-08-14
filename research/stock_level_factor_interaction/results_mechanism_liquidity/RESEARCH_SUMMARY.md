# W20 Mechanism + Incremental Liquidity Validation

The stock-selection rule is frozen: CF20 = 80% primary factor score + 20% consensus score from the other three factor families. Mechanism analysis uses the pre-existing Top20 / 10D reference specification. Liquidity analysis adds one predeclared feature only: ACT5 = recent 5D average trading amount / preceding 20D average trading amount.

## 1) Mechanism: what CF20 actually changes

### K200
- EARLY_2016_2019: portfolio +0.03%/10D; replace 12.6% of Top20; added +0.25% vs dropped -0.05% (replacement edge +0.29%); added primary rank 24.3 vs dropped 16.5; other-family score 0.69 vs 0.35; bootstrap P(delta>0) 83%
- LATE_2020_2022: portfolio -0.01%/10D; replace 13.4% of Top20; added +0.39% vs dropped +0.34% (replacement edge +0.06%); added primary rank 24.5 vs dropped 16.1; other-family score 0.69 vs 0.34; bootstrap P(delta>0) 44%
- NORMAL_2023_2024: portfolio +0.07%/10D; replace 12.8% of Top20; added +0.34% vs dropped -0.42% (replacement edge +0.79%); added primary rank 24.3 vs dropped 16.1; other-family score 0.68 vs 0.34; bootstrap P(delta>0) 91%

### KOSPI_EX_K200
- EARLY_2016_2019: portfolio +0.04%/10D; replace 8.5% of Top20; added +0.07% vs dropped -0.17% (replacement edge +0.22%); added primary rank 23.3 vs dropped 17.8; other-family score 0.69 vs 0.34; bootstrap P(delta>0) 88%
- LATE_2020_2022: portfolio +0.00%/10D; replace 11.4% of Top20; added +0.35% vs dropped +0.60% (replacement edge -0.25%); added primary rank 24.3 vs dropped 16.7; other-family score 0.70 vs 0.33; bootstrap P(delta>0) 51%
- NORMAL_2023_2024: portfolio +0.10%/10D; replace 12.4% of Top20; added +0.75% vs dropped +0.26% (replacement edge +0.47%); added primary rank 24.6 vs dropped 16.8; other-family score 0.72 vs 0.34; bootstrap P(delta>0) 95%

### KOSPI_ALL
- EARLY_2016_2019: portfolio +0.04%/10D; replace 21.0% of Top20; added -0.30% vs dropped -0.41% (replacement edge +0.11%); added primary rank 26.8 vs dropped 14.3; other-family score 0.70 vs 0.35; bootstrap P(delta>0) 73%
- LATE_2020_2022: portfolio +0.07%/10D; replace 23.9% of Top20; added +0.84% vs dropped +0.48% (replacement edge +0.35%); added primary rank 28.0 vs dropped 13.6; other-family score 0.70 vs 0.34; bootstrap P(delta>0) 79%
- NORMAL_2023_2024: portfolio +0.06%/10D; replace 24.6% of Top20; added +0.39% vs dropped +0.15% (replacement edge +0.24%); added primary rank 28.1 vs dropped 13.7; other-family score 0.70 vs 0.35; bootstrap P(delta>0) 67%

### KOSDAQ
- EARLY_2016_2019: portfolio +0.04%/10D; replace 10.6% of Top20; added +0.42% vs dropped -0.06% (replacement edge +0.45%); added primary rank 23.7 vs dropped 17.0; other-family score 0.70 vs 0.34; bootstrap P(delta>0) 90%
- LATE_2020_2022: portfolio +0.07%/10D; replace 17.2% of Top20; added +0.50% vs dropped +0.49% (replacement edge +0.03%); added primary rank 25.9 vs dropped 15.6; other-family score 0.71 vs 0.34; bootstrap P(delta>0) 77%
- NORMAL_2023_2024: portfolio +0.05%/10D; replace 17.4% of Top20; added +0.25% vs dropped +0.27% (replacement edge -0.01%); added primary rank 25.9 vs dropped 15.6; other-family score 0.69 vs 0.34; bootstrap P(delta>0) 68%

### KOSPI_KOSDAQ_ALL
- EARLY_2016_2019: portfolio +0.15%/10D; replace 29.6% of Top20; added +0.37% vs dropped -0.07% (replacement edge +0.43%); added primary rank 30.0 vs dropped 12.8; other-family score 0.71 vs 0.36; bootstrap P(delta>0) 98%
- LATE_2020_2022: portfolio +0.19%/10D; replace 36.0% of Top20; added +0.72% vs dropped +0.19% (replacement edge +0.53%); added primary rank 33.1 vs dropped 12.2; other-family score 0.72 vs 0.36; bootstrap P(delta>0) 88%
- NORMAL_2023_2024: portfolio +0.08%/10D; replace 36.1% of Top20; added +0.31% vs dropped +0.20% (replacement edge +0.11%); added primary rank 33.4 vs dropped 12.2; other-family score 0.72 vs 0.36; bootstrap P(delta>0) 71%

### KOSDAQ_PLUS_KOSPI_EX_K200
- EARLY_2016_2019: portfolio +0.09%/10D; replace 19.1% of Top20; added +0.14% vs dropped -0.21% (replacement edge +0.35%); added primary rank 26.5 vs dropped 14.9; other-family score 0.71 vs 0.34; bootstrap P(delta>0) 97%
- LATE_2020_2022: portfolio +0.19%/10D; replace 26.7% of Top20; added +0.86% vs dropped -0.20% (replacement edge +1.06%); added primary rank 29.6 vs dropped 13.9; other-family score 0.72 vs 0.35; bootstrap P(delta>0) 94%
- NORMAL_2023_2024: portfolio +0.11%/10D; replace 26.8% of Top20; added +0.30% vs dropped +0.01% (replacement edge +0.30%); added primary rank 29.6 vs dropped 13.9; other-family score 0.72 vs 0.35; bootstrap P(delta>0) 78%

## Family breadth of the mechanism

- K200 EARLY_2016_2019: positive families 4/4; FLOW +0.04%, MOMENTUM +0.03%, REVISION +0.01%, VALUE +0.03%
- K200 LATE_2020_2022: positive families 1/4; FLOW -0.08%, MOMENTUM -0.00%, REVISION +0.05%, VALUE -0.01%
- K200 NORMAL_2023_2024: positive families 3/4; FLOW +0.09%, MOMENTUM -0.01%, REVISION +0.19%, VALUE +0.03%
- KOSPI_EX_K200 EARLY_2016_2019: positive families 4/4; FLOW +0.09%, MOMENTUM +0.02%, REVISION +0.03%, VALUE +0.01%
- KOSPI_EX_K200 LATE_2020_2022: positive families 2/4; FLOW -0.06%, MOMENTUM +0.07%, REVISION -0.03%, VALUE +0.03%
- KOSPI_EX_K200 NORMAL_2023_2024: positive families 4/4; FLOW +0.05%, MOMENTUM +0.29%, REVISION +0.02%, VALUE +0.03%
- KOSPI_ALL EARLY_2016_2019: positive families 2/4; FLOW +0.02%, MOMENTUM +0.20%, REVISION -0.04%, VALUE -0.05%
- KOSPI_ALL LATE_2020_2022: positive families 4/4; FLOW +0.07%, MOMENTUM +0.09%, REVISION +0.08%, VALUE +0.05%
- KOSPI_ALL NORMAL_2023_2024: positive families 3/4; FLOW -0.13%, MOMENTUM +0.10%, REVISION +0.05%, VALUE +0.22%
- KOSDAQ EARLY_2016_2019: positive families 3/4; FLOW +0.11%, MOMENTUM +0.07%, REVISION -0.05%, VALUE +0.04%
- KOSDAQ LATE_2020_2022: positive families 3/4; FLOW +0.05%, MOMENTUM -0.00%, REVISION +0.09%, VALUE +0.13%
- KOSDAQ NORMAL_2023_2024: positive families 2/4; FLOW -0.25%, MOMENTUM +0.49%, REVISION +0.05%, VALUE -0.09%
- KOSPI_KOSDAQ_ALL EARLY_2016_2019: positive families 3/4; FLOW +0.31%, MOMENTUM +0.31%, REVISION +0.03%, VALUE -0.08%
- KOSPI_KOSDAQ_ALL LATE_2020_2022: positive families 4/4; FLOW +0.21%, MOMENTUM +0.22%, REVISION +0.22%, VALUE +0.13%
- KOSPI_KOSDAQ_ALL NORMAL_2023_2024: positive families 3/4; FLOW +0.15%, MOMENTUM +0.27%, REVISION -0.29%, VALUE +0.21%
- KOSDAQ_PLUS_KOSPI_EX_K200 EARLY_2016_2019: positive families 3/4; FLOW +0.23%, MOMENTUM +0.11%, REVISION -0.04%, VALUE +0.07%
- KOSDAQ_PLUS_KOSPI_EX_K200 LATE_2020_2022: positive families 4/4; FLOW +0.21%, MOMENTUM +0.16%, REVISION +0.27%, VALUE +0.12%
- KOSDAQ_PLUS_KOSPI_EX_K200 NORMAL_2023_2024: positive families 3/4; FLOW -0.14%, MOMENTUM +0.34%, REVISION +0.10%, VALUE +0.14%

## Consensus decile diagnostic inside primary Top40

- K200 EARLY_2016_2019: other-family D8-10 minus D1-3 within primary Top40 = -0.35%/10D
- K200 LATE_2020_2022: other-family D8-10 minus D1-3 within primary Top40 = +1.61%/10D
- K200 NORMAL_2023_2024: other-family D8-10 minus D1-3 within primary Top40 = -0.90%/10D
- KOSPI_EX_K200 EARLY_2016_2019: other-family D8-10 minus D1-3 within primary Top40 = +1.54%/10D
- KOSPI_EX_K200 LATE_2020_2022: other-family D8-10 minus D1-3 within primary Top40 = +0.21%/10D
- KOSPI_EX_K200 NORMAL_2023_2024: other-family D8-10 minus D1-3 within primary Top40 = +1.28%/10D
- KOSPI_ALL EARLY_2016_2019: other-family D8-10 minus D1-3 within primary Top40 = +1.69%/10D
- KOSPI_ALL LATE_2020_2022: other-family D8-10 minus D1-3 within primary Top40 = +1.05%/10D
- KOSPI_ALL NORMAL_2023_2024: other-family D8-10 minus D1-3 within primary Top40 = +1.17%/10D
- KOSDAQ EARLY_2016_2019: other-family D8-10 minus D1-3 within primary Top40 = -0.81%/10D
- KOSDAQ LATE_2020_2022: other-family D8-10 minus D1-3 within primary Top40 = +1.56%/10D
- KOSDAQ NORMAL_2023_2024: other-family D8-10 minus D1-3 within primary Top40 = -0.20%/10D
- KOSPI_KOSDAQ_ALL EARLY_2016_2019: other-family D8-10 minus D1-3 within primary Top40 = +0.35%/10D
- KOSPI_KOSDAQ_ALL LATE_2020_2022: other-family D8-10 minus D1-3 within primary Top40 = +0.94%/10D
- KOSPI_KOSDAQ_ALL NORMAL_2023_2024: other-family D8-10 minus D1-3 within primary Top40 = +0.37%/10D
- KOSDAQ_PLUS_KOSPI_EX_K200 EARLY_2016_2019: other-family D8-10 minus D1-3 within primary Top40 = +1.00%/10D
- KOSDAQ_PLUS_KOSPI_EX_K200 LATE_2020_2022: other-family D8-10 minus D1-3 within primary Top40 = +1.14%/10D
- KOSDAQ_PLUS_KOSPI_EX_K200 NORMAL_2023_2024: other-family D8-10 minus D1-3 within primary Top40 = +0.65%/10D

## 2) Incremental ACT5 overlay on top of CF20

Main rule: CF20_ACT5_W10 = 90% CF20 + 10% ACT5 cross-sectional rank. The ACT5>1 version is diagnostic only and is not used to select a rule.

### K200
- H5 Top20: FAIL; EARLY_2016_2019 gross -0.01%, net30 -0.03%, net60 -0.06% | LATE_2020_2022 gross +0.01%, net30 -0.00%, net60 -0.02% | NORMAL_2023_2024 gross -0.05%, net30 -0.07%, net60 -0.09%
- H10 Top20: FAIL; EARLY_2016_2019 gross -0.04%, net30 -0.06%, net60 -0.08% | LATE_2020_2022 gross -0.03%, net30 -0.05%, net60 -0.07% | NORMAL_2023_2024 gross +0.01%, net30 -0.01%, net60 -0.03%

### KOSPI_EX_K200
- H5 Top20: PASS; EARLY_2016_2019 gross +0.02%, net30 +0.01%, net60 +0.00% | LATE_2020_2022 gross +0.04%, net30 +0.03%, net60 +0.02% | NORMAL_2023_2024 gross +0.05%, net30 +0.04%, net60 +0.03%
- H10 Top20: FAIL; EARLY_2016_2019 gross -0.04%, net30 -0.04%, net60 -0.05% | LATE_2020_2022 gross -0.05%, net30 -0.06%, net60 -0.08% | NORMAL_2023_2024 gross -0.05%, net30 -0.06%, net60 -0.08%

### KOSPI_ALL
- H5 Top20: FAIL; EARLY_2016_2019 gross -0.01%, net30 -0.04%, net60 -0.06% | LATE_2020_2022 gross -0.06%, net30 -0.08%, net60 -0.11% | NORMAL_2023_2024 gross +0.01%, net30 -0.02%, net60 -0.05%
- H10 Top20: FAIL; EARLY_2016_2019 gross -0.06%, net30 -0.09%, net60 -0.12% | LATE_2020_2022 gross -0.13%, net30 -0.16%, net60 -0.18% | NORMAL_2023_2024 gross +0.04%, net30 +0.01%, net60 -0.01%

### KOSDAQ
- H5 Top20: FAIL; EARLY_2016_2019 gross +0.02%, net30 +0.01%, net60 +0.00% | LATE_2020_2022 gross -0.05%, net30 -0.06%, net60 -0.08% | NORMAL_2023_2024 gross +0.11%, net30 +0.10%, net60 +0.08%
- H10 Top20: FAIL; EARLY_2016_2019 gross +0.05%, net30 +0.04%, net60 +0.03% | LATE_2020_2022 gross +0.03%, net30 +0.01%, net60 +0.00% | NORMAL_2023_2024 gross -0.06%, net30 -0.08%, net60 -0.09%

### KOSPI_KOSDAQ_ALL
- H5 Top20: FAIL; EARLY_2016_2019 gross +0.02%, net30 -0.01%, net60 -0.04% | LATE_2020_2022 gross -0.04%, net30 -0.07%, net60 -0.10% | NORMAL_2023_2024 gross +0.08%, net30 +0.05%, net60 +0.02%
- H10 Top20: FAIL; EARLY_2016_2019 gross +0.06%, net30 +0.03%, net60 +0.00% | LATE_2020_2022 gross +0.05%, net30 +0.02%, net60 -0.01% | NORMAL_2023_2024 gross +0.01%, net30 -0.02%, net60 -0.05%

### KOSDAQ_PLUS_KOSPI_EX_K200
- H5 Top20: FAIL; EARLY_2016_2019 gross +0.03%, net30 +0.01%, net60 -0.01% | LATE_2020_2022 gross -0.05%, net30 -0.07%, net60 -0.10% | NORMAL_2023_2024 gross +0.20%, net30 +0.17%, net60 +0.15%
- H10 Top20: FAIL; EARLY_2016_2019 gross +0.05%, net30 +0.03%, net60 +0.01% | LATE_2020_2022 gross -0.03%, net30 -0.05%, net60 -0.08% | NORMAL_2023_2024 gross +0.04%, net30 +0.02%, net60 -0.01%

## Main H10 family breadth + 2023-24 inference

- K200 EARLY_2016_2019: positive families 0/4
- K200 LATE_2020_2022: positive families 1/4
- K200 NORMAL_2023_2024: positive families 3/4
  - 2023-24 net30 bootstrap: -0.01%; CI [-0.15%,+0.13%], P>0 47%, n=48
- KOSPI_EX_K200 EARLY_2016_2019: positive families 2/4
- KOSPI_EX_K200 LATE_2020_2022: positive families 1/4
- KOSPI_EX_K200 NORMAL_2023_2024: positive families 1/4
  - 2023-24 net30 bootstrap: -0.06%; CI [-0.21%,+0.08%], P>0 21%, n=48
- KOSPI_ALL EARLY_2016_2019: positive families 1/4
- KOSPI_ALL LATE_2020_2022: positive families 1/4
- KOSPI_ALL NORMAL_2023_2024: positive families 3/4
  - 2023-24 net30 bootstrap: +0.01%; CI [-0.23%,+0.29%], P>0 53%, n=48
- KOSDAQ EARLY_2016_2019: positive families 3/4
- KOSDAQ LATE_2020_2022: positive families 3/4
- KOSDAQ NORMAL_2023_2024: positive families 2/4
  - 2023-24 net30 bootstrap: -0.08%; CI [-0.27%,+0.11%], P>0 20%, n=48
- KOSPI_KOSDAQ_ALL EARLY_2016_2019: positive families 3/4
- KOSPI_KOSDAQ_ALL LATE_2020_2022: positive families 3/4
- KOSPI_KOSDAQ_ALL NORMAL_2023_2024: positive families 2/4
  - 2023-24 net30 bootstrap: -0.02%; CI [-0.24%,+0.21%], P>0 42%, n=48
- KOSDAQ_PLUS_KOSPI_EX_K200 EARLY_2016_2019: positive families 2/4
- KOSDAQ_PLUS_KOSPI_EX_K200 LATE_2020_2022: positive families 2/4
- KOSDAQ_PLUS_KOSPI_EX_K200 NORMAL_2023_2024: positive families 2/4
  - 2023-24 net30 bootstrap: +0.02%; CI [-0.20%,+0.24%], P>0 56%, n=48

## Stress only: 2025 / 2026 H10

- K200: 2025 net30 -0.15%; 2026 net30 -0.01%
- KOSPI_EX_K200: 2025 net30 +0.06%; 2026 net30 +0.30%
- KOSPI_ALL: 2025 net30 +0.05%; 2026 net30 +0.35%
- KOSDAQ: 2025 net30 +0.19%; 2026 net30 +0.05%
- KOSPI_KOSDAQ_ALL: 2025 net30 +0.10%; 2026 net30 -0.14%
- KOSDAQ_PLUS_KOSPI_EX_K200: 2025 net30 +0.10%; 2026 net30 +0.06%

## Decision rules

- Mechanism is considered credible only when added names consistently have higher other-family consensus than dropped names and added-minus-dropped forward returns are positive across multiple core blocks/universes.
- ACT5 is incremental only if the frozen H10/Top20 main overlay has positive gross and 30bp-net delta in all three core blocks. H5 is robustness, not a replacement specification.
- Do not choose ACT5_GT1 based on these results; it is interpretation-only.
- 2025 and 2026 are stress diagnostics only and cannot rescue a failed normal-history rule.
- Signals use information through the rebalance date and forward returns begin on the following trading day.

