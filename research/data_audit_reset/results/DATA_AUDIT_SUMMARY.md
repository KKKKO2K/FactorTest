# Source Data Audit — Reset

Content quality sampled every 5 basic-info trading dates, plus endpoints. File/date inventory is exhaustive.

## 1. File inventory

| Dataset | Files | First | Last | Missing vs basic calendar |
|---|---:|---|---|---:|
| MOM1M | 2599 | 2016-01-04 | 2026-08-07 | 0 |
| MOM12_1 | 2599 | 2016-01-04 | 2026-08-07 | 0 |
| OP12_REV | 2599 | 2016-01-04 | 2026-08-07 | 0 |
| OPFY1_REV | 2599 | 2016-01-04 | 2026-08-07 | 0 |
| PBR12MF | 2599 | 2016-01-04 | 2026-08-07 | 0 |
| PER12MF | 2599 | 2016-01-04 | 2026-08-07 | 0 |
| PRIVATE_FLOW | 2599 | 2016-01-04 | 2026-08-07 | 0 |
| FOREIGN_FLOW | 2599 | 2016-01-04 | 2026-08-07 | 0 |
| basic_info | 2599 | 2016-01-04 | 2026-08-07 | 0 |
| trading_amount | 2599 | 2016-01-04 | 2026-08-07 | 0 |
| universe_definition | 2599 | 2016-01-04 | 2026-08-07 | 0 |

## 2. Factor content quality

| Factor | Blank/invalid | Median rows | 5D rank persistence | Exact unchanged share |
|---|---:|---:|---:|---:|
| FOREIGN_FLOW | 1.7% | 664 | +0.776 | 0.8% |
| MOM12_1 | 1.4% | 664 | +0.968 | 0.5% |
| MOM1M | 1.4% | 664 | +0.725 | 0.8% |
| OP12_REV | 39.9% | 664 | +0.801 | 29.4% |
| OPFY1_REV | 38.1% | 664 | +0.813 | 35.0% |
| PBR12MF | 37.7% | 664 | +0.998 | 0.7% |
| PER12MF | 39.6% | 664 | +0.994 | 1.2% |
| PRIVATE_FLOW | 1.7% | 664 | +0.723 | 5.2% |

## 3. Factor coverage by primitive universe

Weighted valid FactorValue coverage across sampled dates:

| Factor | K200 | KOSPI ex-K200 | KOSDAQ |
|---|---:|---:|---:|
| MOM1M | 99.7% | 33.2% | 19.5% |
| MOM12_1 | 99.7% | 33.2% | 19.5% |
| OP12_REV | 88.1% | 16.1% | 9.7% |
| OPFY1_REV | 88.3% | 16.6% | 10.3% |
| PBR12MF | 89.0% | 17.0% | 10.3% |
| PER12MF | 86.6% | 16.5% | 9.9% |
| PRIVATE_FLOW | 99.7% | 33.1% | 19.4% |
| FOREIGN_FLOW | 99.7% | 33.1% | 19.4% |

## 4. All-8-factor intersection

| Universe | Weighted coverage | Median daily | P10 daily |
|---|---:|---:|---:|
| K200 | 85.5% | 85.4% | 82.8% |
| KOSPI_EX_K200 | 15.5% | 15.6% | 13.3% |
| KOSDAQ | 9.3% | 9.3% | 8.0% |
| KOSPI_ALL | 33.7% | 33.7% | 31.6% |
| KOSPI_KOSDAQ_ALL | 18.0% | 17.9% | 16.4% |
| KOSDAQ_PLUS_KOSPI_EX_K200 | 11.1% | 11.1% | 10.0% |

## 5. Reference-data quality

- Median listed KOSPI names: 748
- Median listed KOSDAQ names: 1347
- Median basic-info K200 count: 194
- Median basic vs universe_definition K200 symmetric difference: 0
- Median listed daily-return coverage: 100.0%
- Median listed positive-market-cap coverage: 100.0%
- Median listed trading-amount coverage: 100.0%
- Median listed positive trading-amount share: 98.1%
- universe_definition K200 set changes across all files: 47
- Longest consecutive files with identical K200 set: 246
- Share of consecutive universe-definition files with unchanged K200 set: 98.2%

## Audit interpretation rules

- `Blank/invalid` includes empty and non-numeric FactorValue cells.
- Coverage denominators use point-in-time KOSPI/KOSDAQ labels and K200 flag in `basic_info`, matching the current research loaders.
- `universe_definition` is audited independently to detect membership inconsistencies.
- The all-8 intersection is important for any model that requires every factor simultaneously; single-factor research should not unnecessarily impose this intersection.
- Factor-value scale is not compared across factors; only within-factor numeric quality and cross-sectional coverage are audited.