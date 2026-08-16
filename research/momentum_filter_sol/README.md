# Independent momentum filter study

## Isolation

- Branch: `research/factor-lab-sol`
- Frozen source baseline: `285ad0fd2a1b3175ef5c780f1e244ca2645bb47c`
- `source/factor_all_values/**` is read-only in this branch.
- Other research branches are read-only references only and are never modified.

## Question

Does excluding stocks with weak recent 1-month returns improve the existing 12-1 momentum selection, and is zero a genuinely useful cutoff rather than an arbitrary tuned threshold?

## Operational weighted-momentum baseline

Primary implementation:

- Signal: `모멘텀(12-1)`
- Top 20 stocks
- Linear rank weights, highest momentum receiving the largest weight
- Rebalance every 10 trading days
- Hold for the next 10 trading days
- Primary cost assumption: 60 bps per one-way turnover

Robustness:

- Top 10 / 20 / 30
- Equal weight and linear-rank weight
- 0 / 30 / 60 / 100 bps

## Recent 1M conditioning tests

1. `BASE`: no recent-return filter.
2. Absolute thresholds: recent 1M return > -10%, -5%, 0%, +5%, +10%.
3. Cross-sectional thresholds: remove bottom 10%, 20%, 30%, 40%, 50% of recent 1M return.
4. Continuous blends: add recent-1M rank at 10%, 20%, 30% weights to the 12-1 momentum rank.

This grid is designed to distinguish a true zero-threshold effect from a generic short-term-momentum interaction.

## Universes

Point-in-time universes from `reference_snapshots/basic_info`:

- KOSPI200
- KOSPI ex-KOSPI200
- KOSPI
- KOSDAQ
- KOSPI + KOSDAQ
- KOSDAQ + KOSPI ex-KOSPI200

## Timing / leakage control

Signal and universe membership are observed at date `t`. Portfolio return uses `t+1 ... t+10` daily returns. No future factor observation is used.

## Subperiod reporting

- `TRAIN_2016_2022`: 2016-04-01 through 2022-12-31
- `POST_2023`: 2023-01-01 onward

`POST_2023` is a descriptive post-period, not labeled as untouched OOS because related factor research has already inspected this period.

## Outputs

The workflow writes results under `research/momentum_filter_sol/results/`.

Primary decision file:

- `decision_table_top20_ranklinear_60bps.csv`

Additional files:

- `summary_train_post.csv`
- `paired_summary.csv`
- `period_returns.csv.gz`
- `paired_vs_base.csv.gz`
- `RESEARCH_SUMMARY.md`
