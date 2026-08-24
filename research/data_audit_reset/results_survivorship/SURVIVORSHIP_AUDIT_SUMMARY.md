# Survivorship / Universe Lineage Audit

- First snapshot: 2016-01-04
- Last snapshot: 2026-08-07
- Basic master rows first/last: 2557 / 2557
- Basic master row-set endpoint Jaccard: 1.000
- Listed KOSPI+KOSDAQ first/last: 1647 / 2546
- 2016-listed names not listed at final date: 8
- Final-listed names not listed in 2016: 907
- Of 2016-listed exits, still present as rows in final basic master: 8/8
- Of post-2016 listed entries, already present as rows in first basic master: 907/907

Interpretation: a static/superset master row list is not itself survivorship bias if historical market-membership flags are point-in-time. The key evidence is whether both later entrants and later exits are represented with changing historical market status.

## Factor row-set endpoint turnover

| Factor | First | Last | Endpoint Jaccard | First-only | Last-only |
|---|---:|---:|---:|---:|---:|
| MOM1M | 664 | 730 | 0.907 | 1 | 67 |
| MOM12_1 | 664 | 730 | 0.907 | 1 | 67 |
| OP12_REV | 664 | 730 | 0.907 | 1 | 67 |
| OPFY1_REV | 664 | 730 | 0.907 | 1 | 67 |
| PBR12MF | 664 | 730 | 0.907 | 1 | 67 |
| PER12MF | 664 | 730 | 0.907 | 1 | 67 |
| PRIVATE_FLOW | 664 | 730 | 0.907 | 1 | 67 |
| FOREIGN_FLOW | 664 | 730 | 0.907 | 1 | 67 |

## Annual listed-universe lineage

| Year | Listed | KOSPI | KOSDAQ | K200 | Names later absent by final | Final names not yet listed |
|---|---:|---:|---:|---:|---:|---:|
| 2016 | 1716 | 686 | 1030 | 192 | 9 | 839 |
| 2017 | 1797 | 705 | 1092 | 192 | 9 | 758 |
| 2018 | 1892 | 722 | 1170 | 193 | 10 | 664 |
| 2019 | 1985 | 735 | 1250 | 192 | 10 | 571 |
| 2020 | 2065 | 743 | 1322 | 193 | 10 | 491 |
| 2021 | 2163 | 764 | 1399 | 195 | 11 | 394 |
| 2022 | 2242 | 770 | 1472 | 195 | 11 | 315 |
| 2023 | 2347 | 786 | 1561 | 197 | 11 | 210 |
| 2024 | 2445 | 800 | 1645 | 198 | 11 | 112 |
| 2025 | 2537 | 809 | 1728 | 200 | 11 | 20 |
| 2026 | 2546 | 807 | 1739 | 200 | 0 | 0 |