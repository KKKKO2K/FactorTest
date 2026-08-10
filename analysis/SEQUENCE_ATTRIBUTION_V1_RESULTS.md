# K200 Sequence Attribution v1 — Results

Branch: `analysis/k200-sequence-attribution-v1`
Correct full-calendar run: GitHub Actions `31367565588` (success)

## Scope

- Deterioration gate variants are excluded.
- Existing concentrated portfolio construction is unchanged.
- Existing leader activation / engine routing is unchanged.
- Sequence overlay only reweights names within the existing stock sleeve.
- True 10-trading-day calendar; 236 scheduled snapshots; OOS contains 77 completed periods.
- KOSPI200 benchmark horizon is aligned to the stock-return calendar.
- Transaction cost: 60 bp one-way turnover cost.

## OOS structural variants

| Variant | Strategy CAGR | Relative CAGR | IR | Strategy MDD | Relative MDD | Annual turnover |
|---|---:|---:|---:|---:|---:|---:|
| BASE | 57.5023% | 11.6198% | 0.7846 | -28.4317% | -15.2333% | 10.6118x |
| FLOW_ONLY | 57.9329% | 11.9249% | 0.7987 | -28.4070% | -15.0524% | 10.6166x |
| THREE_ONLY | 57.8004% | 11.8310% | 0.7977 | -28.3849% | -15.2345% | 10.6562x |
| DUAL_ONLY | 57.4991% | 11.6175% | 0.7839 | -28.3734% | -15.1927% | 10.6294x |
| FLOW_THREE | **58.2294%** | **12.1351%** | **0.8116** | -28.3604% | -15.0541% | 10.6601x |
| FLOW_DUAL | 57.9253% | 11.9195% | 0.7977 | -28.3491% | -15.0138% | 10.6348x |
| THREE_DUAL | 57.8034% | 11.8332% | 0.7972 | -28.3266% | -15.1903% | 10.6734x |
| ALL_CURRENT | 58.2280% | 12.1340% | 0.8109 | -28.3025% | -15.0116% | 10.6782x |

`FLOW_THREE` is marginally better than `ALL_CURRENT`. `DUAL_ONLY` is essentially identical to BASE, so `DUAL_REVISION` adds no demonstrated standalone edge here.

## OOS period-level overlay vs BASE

- ALL_CURRENT mean delta: +1.98 bp per 10D period; t-stat 1.60; bootstrap 95% CI roughly -0.17 bp to +4.66 bp.
- FLOW_THREE mean delta: +1.98 bp; t-stat 1.63; bootstrap 95% CI roughly -0.12 bp to +4.58 bp.
- FLOW_ONLY mean delta: +1.10 bp; t-stat 1.30.
- THREE_ONLY mean delta: +0.88 bp; t-stat 0.99.
- DUAL_ONLY: approximately zero.

The confidence intervals still include zero, so this is not statistically robust evidence by itself.

## Outlier dependence

ALL_CURRENT OOS overlay relative CAGR versus BASE:

- Full sample: +0.46%/yr.
- Drop best 1 period: +0.28%/yr.
- Drop best 3 periods: +0.03%/yr.
- Drop best 5 periods: -0.09%/yr.

The best single period contributes about 43% of the simple net delta; the best three periods contribute about 94%. The sequence edge is therefore materially top-period concentrated.

## Train versus OOS

Train has 155 completed periods.

| Variant | Train Strategy CAGR | Train Relative CAGR | Train IR | Overlay relative CAGR vs BASE |
|---|---:|---:|---:|---:|
| BASE | 7.5671% | 4.2935% | 0.4578 | — |
| FLOW_ONLY | 7.5700% | 4.2963% | 0.4554 | +0.003%/yr |
| THREE_ONLY | 7.2693% | 4.0048% | 0.4367 | -0.277%/yr |
| DUAL_ONLY | 7.5236% | 4.2513% | 0.4534 | -0.041%/yr |
| FLOW_THREE | 7.2749% | 4.0102% | 0.4346 | -0.272%/yr |
| ALL_CURRENT | 7.2402% | 3.9765% | 0.4309 | -0.304%/yr |

This is the main robustness problem. FLOW_ONLY is roughly neutral across train and positive OOS, while THREE_STAGE is negative in train and positive OOS. The current combined sequence therefore does not have stable full-history evidence.

## OOS state / engine attribution for ALL_CURRENT

- HIGH_DISPERSION: +5.39 bp mean per period across 15 periods; 60% hit rate.
- BROAD_RISK_ON: +2.52 bp across 32 periods.
- RISK_OFF: **-1.60 bp** across 12 periods.

By engine:

- REV_BREADTH_70: **+5.77 bp**, 14 periods, 64.3% hit rate — strongest and most consistent OOS bucket.
- LEADER5_80: +2.44 bp, 23 periods, but highly lumpy.
- VALUE_REV_30: +1.96 bp, 15 periods, median slightly negative.
- CONTRARIAN_70: **-1.92 bp**, 10 periods, median negative — sequence is harmful in this engine OOS.
- INDEX_ONLY: essentially zero as expected.

However, REV_BREADTH_70 sequence effects were negative in the train period, so the OOS strength there cannot yet be treated as a stable regime rule.

## Multiplier sensitivity (OOS)

Scaling all current sequence coefficients proportionally produced monotonic OOS improvement through 1.5x:

| Scale | Strategy CAGR | Relative CAGR | IR | Relative MDD |
|---|---:|---:|---:|---:|
| 0.50x | 57.8760% | 11.8846% | 0.7983 | -15.1132% |
| 0.75x | 58.0547% | 12.0113% | 0.8048 | -15.0604% |
| 1.00x | 58.2280% | 12.1340% | 0.8109 | -15.0116% |
| 1.25x | 58.3963% | 12.2533% | 0.8168 | -14.9666% |
| 1.50x | 58.5598% | 12.3692% | 0.8225 | -14.9251% |

But train moves monotonically in the opposite direction as scale rises. Therefore 1.5x should not be adopted from this OOS result; it is a warning that the apparent OOS edge is regime-sensitive / potentially overfit.

## Working conclusion

1. Drop `DUAL_REVISION` from the leading sequence candidate; it adds no standalone edge and slightly dilutes `FLOW_THREE` OOS.
2. `FLOW_REVISION` is the most defensible component because it is approximately neutral in train and positive OOS.
3. `THREE_STAGE` is the main source of train/OOS sign instability: negative in train, positive in OOS, especially through recent LEADER / high-dispersion episodes.
4. Do not promote global `FLOW_THREE` to production yet. The OOS gain is small, top-period concentrated, and not train-consistent.
5. Next sequence work should test whether `FLOW_REVISION` has stable cross-sample conditional value and whether THREE_STAGE represents a genuine post-2023 regime change rather than sample luck. Do this with rolling/walk-forward slices rather than optimizing on the existing OOS endpoint.
