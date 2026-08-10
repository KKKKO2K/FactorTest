# MOM(12-1) × 1M Filter Research

## Purpose

Test whether the weak recent-return tail should be removed from a standard 12-1 momentum signal, and distinguish a hard zero filter from broader short-term-momentum conditioning.

This study is intentionally isolated from the existing FactorTest strategy branches. Source data under `source/` is read-only.

## Fixed baseline

- Repository baseline commit: `285ad0fd2a1b3175ef5c780f1e244ca2645bb47c`
- Working branch: `research/factor-lab-v2`
- Universe: KOSPI200 constituents point-in-time from `reference_snapshots/basic_info`
- Main signal: `source/factor_all_values/모멘텀(12-1)`
- Recent-return conditioning signal: `source/factor_all_values/단기모멘텀`
- Rebalance interval: every 10 trading days
- Forward holding horizon: next 10 trading days
- Benchmark: equal-weight point-in-time KOSPI200 universe
- Source files are never modified by the research code.

## Variants

1. `MOM12_1_BASE`
   - Rank all eligible KOSPI200 names by MOM(12-1).

2. `MOM12_1_1M_POS`
   - Keep only names with `단기모멘텀 > 0`.
   - Rank survivors by MOM(12-1).

3. `MOM12_1_1M_ABOVE_MEDIAN`
   - Keep only names at or above the cross-sectional median of `단기모멘텀`.
   - Rank survivors by MOM(12-1).

4. `MOM12_1_1M_KEEP_TOP70PCT`
   - Exclude the bottom 30% of `단기모멘텀` each rebalance date.
   - Rank survivors by MOM(12-1).

5. Continuous combinations
   - `MOM12_1_PLUS_1M_RANK_W10`
   - `MOM12_1_PLUS_1M_RANK_W20`
   - `MOM12_1_PLUS_1M_RANK_W30`
   - Score = `(1-w) * rank(MOM12-1) + w * rank(1M)`.

The threshold variants answer whether avoiding recent losers is enough. The continuous variants answer whether short-term momentum should be part of the ranking itself.

## Portfolio robustness grid

The runner evaluates each variant with:

- Top N: 5 / 10 / 20
- Weighting: equal-weight / linear rank-weight
- Transaction cost: 0 / 30 / 60 / 100 bps per one-way turnover

This avoids choosing a single portfolio-construction assumption before seeing whether the factor effect is robust.

## Outputs

`python research/momentum_12_1_short_filter/run_research.py`

writes to `research/momentum_12_1_short_filter/results/`:

- `period_returns.csv`: rebalance-period gross/net returns, benchmark, excess return, turnover, eligible count, rank IC
- `summary.csv`: annualized return, Sharpe, MDD, hit rate, average turnover, IC statistics
- `yearly_summary.csv`: calendar-year robustness
- `filter_diagnostics.csv`: how much each filter shrinks the universe and overlaps the baseline leaders

## Look-ahead convention

Signals at date `t` use only files dated `t`. Forward returns use the next 10 basic-info daily returns (`t+1 ... t+10`). No future factor value is used in ranking or filtering.
