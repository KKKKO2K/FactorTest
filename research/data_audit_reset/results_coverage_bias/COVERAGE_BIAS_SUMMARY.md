# Factor Coverage Bias Audit

## Row universe vs value availability

### K200

| Factor | Row membership | Valid value | Valid given row |
|---|---:|---:|---:|
| FOREIGN_FLOW | 100.0% | 100.0% | 100.0% |
| MOM12_1 | 100.0% | 100.0% | 100.0% |
| MOM1M | 100.0% | 100.0% | 100.0% |
| OP12_REV | 100.0% | 88.0% | 88.1% |
| OPFY1_REV | 100.0% | 88.1% | 88.3% |
| PBR12MF | 100.0% | 89.1% | 89.2% |
| PER12MF | 100.0% | 86.8% | 87.0% |
| PRIVATE_FLOW | 100.0% | 100.0% | 100.0% |

### KOSPI_EX_K200

| Factor | Row membership | Valid value | Valid given row |
|---|---:|---:|---:|
| FOREIGN_FLOW | 32.7% | 32.3% | 98.6% |
| MOM12_1 | 32.7% | 32.4% | 99.0% |
| MOM1M | 32.7% | 32.4% | 99.0% |
| OP12_REV | 32.7% | 16.2% | 50.4% |
| OPFY1_REV | 32.7% | 16.7% | 52.0% |
| PBR12MF | 32.7% | 17.1% | 53.1% |
| PER12MF | 32.7% | 16.7% | 51.5% |
| PRIVATE_FLOW | 32.7% | 32.3% | 98.6% |

### KOSDAQ

| Factor | Row membership | Valid value | Valid given row |
|---|---:|---:|---:|
| FOREIGN_FLOW | 18.9% | 18.5% | 97.8% |
| MOM12_1 | 18.9% | 18.6% | 98.4% |
| MOM1M | 18.9% | 18.6% | 98.4% |
| OP12_REV | 18.9% | 9.6% | 50.0% |
| OPFY1_REV | 18.9% | 10.2% | 52.2% |
| PBR12MF | 18.9% | 10.2% | 52.4% |
| PER12MF | 18.9% | 9.9% | 50.4% |
| PRIVATE_FLOW | 18.9% | 18.5% | 97.8% |

## Size bias

Median valid-value coverage by market-cap quintile (Q1 smallest, Q5 largest):

### K200

| Factor | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---:|---:|---:|---:|---:|
| MOM1M | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| MOM12_1 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| OP12_REV | 67.5% | 84.6% | 92.3% | 97.4% | 100.0% |
| OPFY1_REV | 68.4% | 84.6% | 92.5% | 97.4% | 100.0% |
| PBR12MF | 68.4% | 87.2% | 94.7% | 97.4% | 100.0% |
| PER12MF | 66.7% | 84.6% | 92.3% | 92.3% | 97.5% |
| PRIVATE_FLOW | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| FOREIGN_FLOW | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

### KOSPI_EX_K200

| Factor | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---:|---:|---:|---:|---:|
| MOM1M | 0.0% | 0.0% | 0.0% | 61.7% | 100.0% |
| MOM12_1 | 0.0% | 0.0% | 0.0% | 61.7% | 100.0% |
| OP12_REV | 0.0% | 0.0% | 0.0% | 19.8% | 61.1% |
| OPFY1_REV | 0.0% | 0.0% | 0.0% | 20.8% | 63.1% |
| PBR12MF | 0.0% | 0.0% | 0.0% | 21.6% | 63.6% |
| PER12MF | 0.0% | 0.0% | 0.0% | 20.9% | 61.5% |
| PRIVATE_FLOW | 0.0% | 0.0% | 0.0% | 61.7% | 100.0% |
| FOREIGN_FLOW | 0.0% | 0.0% | 0.0% | 61.7% | 100.0% |

### KOSDAQ

| Factor | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---:|---:|---:|---:|---:|
| MOM1M | 0.0% | 0.0% | 0.0% | 0.0% | 92.9% |
| MOM12_1 | 0.0% | 0.0% | 0.0% | 0.0% | 92.9% |
| OP12_REV | 0.0% | 0.0% | 0.0% | 0.0% | 46.7% |
| OPFY1_REV | 0.0% | 0.0% | 0.0% | 0.0% | 49.5% |
| PBR12MF | 0.0% | 0.0% | 0.0% | 0.0% | 49.4% |
| PER12MF | 0.0% | 0.0% | 0.0% | 0.0% | 47.8% |
| PRIVATE_FLOW | 0.0% | 0.0% | 0.0% | 0.0% | 92.5% |
| FOREIGN_FLOW | 0.0% | 0.0% | 0.0% | 0.0% | 92.5% |

## Common row-set diagnostics

- Median pairwise Jaccard across the 8 factor row sets: 1.000
- Median minimum pairwise Jaccard on a date: 1.000
- MOM1M row set vs same-N top market-cap set median Jaccard: 0.978
- Median share of MOM1M listed rows that are in same-N top market-cap set: 98.9%
- Median market-cap percentile of MOM1M-covered listed stocks: 84.9%

## All-8 intersection by year

### K200
- 2016: 88.4%
- 2017: 86.5%
- 2018: 85.5%
- 2019: 84.9%
- 2020: 83.6%
- 2021: 83.1%
- 2022: 86.4%
- 2023: 86.8%
- 2024: 86.6%
- 2025: 84.8%
- 2026: 86.5%

### KOSPI_EX_K200
- 2016: 15.5%
- 2017: 16.2%
- 2018: 16.5%
- 2019: 14.6%
- 2020: 13.0%
- 2021: 16.3%
- 2022: 15.5%
- 2023: 13.9%
- 2024: 16.7%
- 2025: 17.1%
- 2026: 16.2%

### KOSDAQ
- 2016: 10.0%
- 2017: 9.4%
- 2018: 10.5%
- 2019: 8.5%
- 2020: 9.7%
- 2021: 11.1%
- 2022: 9.6%
- 2023: 9.0%
- 2024: 8.6%
- 2025: 8.3%
- 2026: 8.7%
