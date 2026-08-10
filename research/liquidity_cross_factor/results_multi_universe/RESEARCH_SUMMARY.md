# Trading-value overlays across market universes

Run date: 2026-08-10

Method:
- Point-in-time universes.
- 10-trading-day rebalance / holding period.
- Factor set: OP12 revision, OP FY1 revision, PBR 12MF, PER 12MF, 1M momentum, 12-1 momentum, private flow, foreign flow.
- Each raw factor is tested in both HIGH-good and LOW-good directions; overlay uplift is always measured versus the same-direction BASE.
- Portfolio sizes: Top10 / Top20; costs: 0 / 30 / 60 bps.
- TRAIN = 2016 through 2022; OOS = 2023 onward.
- `ACT1`: current trading amount / strictly prior 20D average.
- `ACT5`: recent 5D average trading amount / preceding non-overlapping 20D average.
- `ACT5_KEEP_TOP70`: remove the cross-sectional bottom 30% of ACT5, then select on the original factor.
- `RESID_TA_W10`: 10% weight on log trading amount residualized cross-sectionally on log market cap.
- Raw period output was intentionally not committed because it exceeds GitHub's 100MB single-file limit; compact summary outputs are the retained artifact.

## Main cross-universe conclusion

There are two distinct liquidity effects.

1. **Older / small-cap confirmation effect:** ACT1, turnover, and size-neutral residual trading amount were strongest in TRAIN, particularly in KOSDAQ and the non-K200 combined universe, but weakened materially after 2023.
2. **Recent low-activity-veto / large-liquid tilt:** ACT5 bottom-tail filtering, raw trading amount, and market-cap tilts generally strengthened after 2023. ACT5_KEEP_TOP70 is especially strong recently in K200 and non-K200 combined universes, but was not a stable historical KOSPI rule.

This argues against treating “trading value” as one factor. Short-horizon activity confirmation, stale-signal veto, raw liquidity, and size exposure should remain separate research objects.

## K200

| Overlay | Train improve share | Train median ann. delta | OOS improve share | OOS median ann. delta |
|---|---:|---:|---:|---:|
| TURNOVER_W10 | 65% | +0.78%p | 58% | +0.72%p |
| RESID_TA_W10 | 61% | +0.58%p | 59% | +0.45%p |
| RAW_TA_W10 | 49% | -0.12%p | 62% | +1.03%p |
| ACT1_W10 | 41% | -0.37%p | 44% | -0.36%p |
| MCAP_W10 | 39% | -0.41%p | 69% | +2.65%p |
| ACT5_W10 | 28% | -1.17%p | 54% | +0.57%p |
| ACT5_KEEP_TOP70 | 35% | -1.31%p | 73% | +2.88%p |
| ACT5_KEEP_TOP50 | 23% | -2.38%p | 62% | +2.45%p |

Interpretation: K200 has a modest persistent turnover / residual-liquidity effect, while the ACT5 stale-signal filter is a **recent regime effect**, not a historically persistent rule.

## KOSPI ex-K200

| Overlay | Train improve share | Train median ann. delta | OOS improve share | OOS median ann. delta |
|---|---:|---:|---:|---:|
| ACT1_W10 | 65% | +0.65%p | 57% | +1.08%p |
| RAW_TA_W10 | 58% | +0.25%p | 66% | +1.03%p |
| TURNOVER_W10 | 57% | +0.26%p | 66% | +0.98%p |
| RESID_TA_W10 | 52% | +0.08%p | 54% | +0.25%p |
| MCAP_W10 | 48% | -0.04%p | 66% | +0.75%p |
| ACT5_W10 | 34% | -0.82%p | 52% | +0.50%p |
| ACT5_KEEP_TOP70 | 27% | -1.77%p | 65% | +1.86%p |
| ACT5_KEEP_TOP50 | 19% | -4.07%p | 56% | +0.79%p |

Interpretation: ACT1 worked from the training period, but the ACT5 veto again changed from historically harmful to recently helpful.

## KOSPI all

| Overlay | Train improve share | Train median ann. delta | OOS improve share | OOS median ann. delta |
|---|---:|---:|---:|---:|
| TURNOVER_W10 | 62% | +0.41%p | 56% | +1.73%p |
| RESID_TA_W10 | 56% | +0.19%p | 54% | +0.44%p |
| MCAP_W10 | 47% | -0.16%p | 84% | +3.62%p |
| ACT1_W10 | 42% | -0.36%p | 61% | +0.95%p |
| RAW_TA_W10 | 41% | -0.30%p | 75% | +3.32%p |
| ACT5_W10 | 27% | -1.49%p | 49% | -0.13%p |
| ACT5_KEEP_TOP70 | 24% | -2.27%p | 46% | -0.79%p |
| ACT5_KEEP_TOP50 | 19% | -3.44%p | 68% | +3.23%p |

Interpretation: recent raw trading-value strength in KOSPI all is heavily entangled with market-cap / large-stock preference. The size-neutral residual effect is much smaller.

## KOSDAQ

| Overlay | Train improve share | Train median ann. delta | OOS improve share | OOS median ann. delta |
|---|---:|---:|---:|---:|
| ACT1_W10 | **75%** | **+1.79%p** | 53% | +0.28%p |
| ACT5_W10 | **75%** | **+1.16%p** | 58% | +0.88%p |
| ACT5_KEEP_TOP70 | 69% | +1.77%p | 61% | +1.57%p |
| RESID_TA_W10 | **68%** | **+1.51%p** | 52% | +0.16%p |
| RAW_TA_W10 | 65% | +0.50%p | 61% | +1.64%p |
| TURNOVER_W10 | **64%** | **+1.54%p** | 56% | +0.69%p |
| MCAP_W10 | 53% | +0.15%p | 56% | +0.35%p |
| ACT5_KEEP_TOP50 | 45% | -0.48%p | 66% | +3.10%p |

Interpretation: **this is the clearest example of a liquidity signal that was stronger in TRAIN and weakened recently.** ACT1 and size-neutral trading activity decay sharply, while the milder ACT5 bottom-30% veto remains positive in both samples.

## KOSPI + KOSDAQ all

| Overlay | Train improve share | Train median ann. delta | OOS improve share | OOS median ann. delta |
|---|---:|---:|---:|---:|
| RAW_TA_W10 | 65% | +1.56%p | 65% | +2.14%p |
| ACT1_W10 | **65%** | **+1.44%p** | 44% | **-0.97%p** |
| MCAP_W10 | 59% | +0.61%p | **84%** | **+3.46%p** |
| RESID_TA_W10 | **58%** | **+1.37%p** | 25% | **-2.83%p** |
| TURNOVER_W10 | **57%** | **+1.40%p** | 34% | **-2.51%p** |
| ACT5_KEEP_TOP70 | 53% | +0.11%p | 57% | +1.21%p |
| ACT5_W10 | 52% | +0.46%p | 36% | -2.93%p |

Interpretation: the old activity / turnover confirmation effect **reverses** after 2023 when ranking all KOSPI and KOSDAQ stocks together. Raw TA stays positive because it also changes market / size allocation; MCAP being even stronger reinforces that interpretation.

## KOSDAQ + KOSPI ex-K200

| Overlay | Train improve share | Train median ann. delta | OOS improve share | OOS median ann. delta |
|---|---:|---:|---:|---:|
| ACT1_W10 | **80%** | **+2.61%p** | 49% | **-0.20%p** |
| ACT5_W10 | 67% | +1.18%p | 53% | +0.49%p |
| RAW_TA_W10 | 64% | +1.00%p | **74%** | **+3.10%p** |
| ACT5_KEEP_TOP70 | 64% | +0.70%p | **74%** | **+3.07%p** |
| RESID_TA_W10 | **61%** | **+0.62%p** | 43% | **-1.06%p** |
| TURNOVER_W10 | 59% | +0.82%p | 50% | -0.07%p |
| MCAP_W10 | 55% | +0.59%p | 75% | +1.70%p |
| ACT5_KEEP_TOP50 | 53% | +0.56%p | 53% | +0.72%p |

Interpretation: another clear decay case for ACT1 / residual activity, while low-activity veto and raw-liquidity tilt strengthen substantially after 2023.

## ACT5_KEEP_TOP70 cross-universe

| Universe | Train improve | Train median delta | OOS improve | OOS median delta |
|---|---:|---:|---:|---:|
| K200 | 35% | -1.31%p | 73% | +2.88%p |
| KOSPI ex-K200 | 27% | -1.77%p | 65% | +1.86%p |
| KOSPI all | 24% | -2.27%p | 46% | -0.79%p |
| KOSDAQ | 69% | +1.77%p | 61% | +1.57%p |
| KOSPI + KOSDAQ all | 53% | +0.11%p | 57% | +1.21%p |
| KOSDAQ + KOSPI ex-K200 | 64% | +0.70%p | 74% | +3.07%p |

This makes the key structural point: ACT5 low-activity filtering was already useful in **KOSDAQ / non-K200 stocks**, but historically harmful in the KOSPI large-cap side. Its recent strength in K200 therefore looks like a regime change or diffusion of a small-cap liquidity-confirmation effect into large caps rather than a timeless K200 rule.

## Frozen train-direction OOS examples (Top10, 30 bps)

Selected examples only; “best” is descriptive and subject to multiple-testing bias.

- K200: PBR BASE 20.57% -> ACT5_KEEP_TOP70 26.26%; private flow 22.27% -> ACT5_KEEP_TOP50 30.26%.
- KOSPI ex-K200: PBR BASE 34.73% -> TURNOVER_W10 37.27%; private flow 23.67% -> ACT5_KEEP_TOP70 26.33%.
- KOSDAQ: OP12 revision 15.36% -> ACT5_KEEP_TOP50 30.90%; OPFY1 revision 10.32% -> 30.22%; private flow 7.01% -> ACT5_KEEP_TOP70 31.59%.
- KOSDAQ + KOSPI ex-K200: foreign flow -15.05% -> ACT5_KEEP_TOP70 10.83%; private flow 6.24% -> ACT5_W10 21.37%.

## Research implication

Next-stage liquidity work should not search for one universal trading-value score. It should test at least two separate state variables:

1. **Activity confirmation:** ACT1 / turnover / residual TA. Historically strongest in KOSDAQ and non-K200 stocks, but showing post-2023 decay.
2. **Stale-signal veto:** ACT5 low-activity tail filter. Persistent in KOSDAQ/non-K200 and newly strong in K200 after 2023.

These should then be connected to factor-regime variables rather than hard-coded as one permanent stock-selection rule.
