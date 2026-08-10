# MOM12-1 × 1M Filter: automated result note

Fixed OOS split: `2023-01-01`. This cutoff is declared in code, not selected from results.
Key construction: Top10 / equal-weight / 30 bps one-way turnover cost.

## FULL

- MOM12_1_PLUS_1M_RANK_W10: ann 8.74%, Sharpe 0.41, MDD -60.82%, turnover 0.28
- MOM12_1_BASE: ann 7.33%, Sharpe 0.38, MDD -53.63%, turnover 0.22
- MOM12_1_1M_KEEP_TOP70PCT: ann 6.93%, Sharpe 0.37, MDD -64.55%, turnover 0.39
- MOM12_1_PLUS_1M_RANK_W20: ann 6.79%, Sharpe 0.36, MDD -65.71%, turnover 0.40
- MOM12_1_1M_ABOVE_MEDIAN: ann 5.87%, Sharpe 0.34, MDD -57.07%, turnover 0.45
- MOM12_1_PLUS_1M_RANK_W30: ann 5.69%, Sharpe 0.33, MDD -61.79%, turnover 0.45
- MOM12_1_1M_POS: ann 2.98%, Sharpe 0.25, MDD -64.35%, turnover 0.49

Paired uplift vs baseline:
- MOM12_1_PLUS_1M_RANK_W10: relative ann 1.31%, paired t 0.35, win 48.3%
- MOM12_1_1M_KEEP_TOP70PCT: relative ann -0.37%, paired t -0.15, win 47.5%
- MOM12_1_PLUS_1M_RANK_W20: relative ann -0.50%, paired t -0.18, win 47.5%
- MOM12_1_1M_ABOVE_MEDIAN: relative ann -1.36%, paired t -0.34, win 47.1%
- MOM12_1_PLUS_1M_RANK_W30: relative ann -1.52%, paired t -0.35, win 47.5%
- MOM12_1_1M_POS: relative ann -2.80%, paired t -0.62, win 44.7%

## OOS_2023_PLUS

- MOM12_1_PLUS_1M_RANK_W10: ann 51.73%, Sharpe 1.16, MDD -44.42%, turnover 0.28
- MOM12_1_PLUS_1M_RANK_W20: ann 49.81%, Sharpe 1.17, MDD -41.47%, turnover 0.38
- MOM12_1_PLUS_1M_RANK_W30: ann 46.62%, Sharpe 1.11, MDD -40.42%, turnover 0.43
- MOM12_1_1M_ABOVE_MEDIAN: ann 42.76%, Sharpe 1.05, MDD -42.14%, turnover 0.42
- MOM12_1_BASE: ann 41.96%, Sharpe 1.04, MDD -44.25%, turnover 0.20
- MOM12_1_1M_POS: ann 40.64%, Sharpe 1.04, MDD -35.08%, turnover 0.47
- MOM12_1_1M_KEEP_TOP70PCT: ann 39.88%, Sharpe 1.01, MDD -43.43%, turnover 0.37

Paired uplift vs baseline:
- MOM12_1_PLUS_1M_RANK_W10: relative ann 6.88%, paired t 0.93, win 50.0%
- MOM12_1_PLUS_1M_RANK_W20: relative ann 5.54%, paired t 0.56, win 47.7%
- MOM12_1_PLUS_1M_RANK_W30: relative ann 3.29%, paired t 0.29, win 48.8%
- MOM12_1_1M_ABOVE_MEDIAN: relative ann 0.57%, paired t 0.06, win 47.7%
- MOM12_1_1M_POS: relative ann -0.92%, paired t -0.14, win 44.2%
- MOM12_1_1M_KEEP_TOP70PCT: relative ann -1.46%, paired t -0.19, win 47.7%

## Robustness across 24 portfolio/cost configurations

- FULL / MOM12_1_PLUS_1M_RANK_W10: return beat 79%, Sharpe beat 75%, MDD improve 17%, median relative ann 1.20%
- FULL / MOM12_1_1M_ABOVE_MEDIAN: return beat 50%, Sharpe beat 42%, MDD improve 29%, median relative ann -0.40%
- FULL / MOM12_1_PLUS_1M_RANK_W30: return beat 50%, Sharpe beat 50%, MDD improve 25%, median relative ann -0.07%
- FULL / MOM12_1_PLUS_1M_RANK_W20: return beat 42%, Sharpe beat 38%, MDD improve 12%, median relative ann -0.35%
- FULL / MOM12_1_1M_KEEP_TOP70PCT: return beat 17%, Sharpe beat 17%, MDD improve 0%, median relative ann -2.38%
- FULL / MOM12_1_1M_POS: return beat 0%, Sharpe beat 0%, MDD improve 0%, median relative ann -4.36%
- OOS_2023_PLUS / MOM12_1_PLUS_1M_RANK_W30: return beat 96%, Sharpe beat 92%, MDD improve 100%, median relative ann 5.38%
- OOS_2023_PLUS / MOM12_1_PLUS_1M_RANK_W10: return beat 83%, Sharpe beat 83%, MDD improve 17%, median relative ann 7.16%
- OOS_2023_PLUS / MOM12_1_PLUS_1M_RANK_W20: return beat 75%, Sharpe beat 75%, MDD improve 79%, median relative ann 4.90%
- OOS_2023_PLUS / MOM12_1_1M_ABOVE_MEDIAN: return beat 67%, Sharpe beat 79%, MDD improve 100%, median relative ann 1.93%
- OOS_2023_PLUS / MOM12_1_1M_KEEP_TOP70PCT: return beat 17%, Sharpe beat 21%, MDD improve 71%, median relative ann -4.00%
- OOS_2023_PLUS / MOM12_1_1M_POS: return beat 12%, Sharpe beat 17%, MDD improve 88%, median relative ann -3.31%
