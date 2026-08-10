# Universe × State × Engine Heterogeneity v1 — Results

## Question

Can K200, KOSPI ex-K200, and KOSDAQ legitimately use different stock-selection engines under the same market state, or does that flexibility mainly create overfit?

## Frozen design

- Common state: **K200 market-state label** on each true 10D signal date, applied to all three universes.
- Universes: `K200`, `KOSPI_EX_K200`, `KOSDAQ`.
- Candidate engine families: nine pre-existing Composite engines from `k200_off_engine_lab.py`.
- Every engine is normalized to **50% local cap-weight benchmark + 50% stock sleeve** so the test isolates engine identity rather than active-risk budget.
- Cost: existing 60bp one-way research cost assumption.
- Train: 2017-01-02 to 2023-05-25.
- OOS: 2023-05-26 onward.
- State→engine mapping is learned on Train only and frozen for OOS.
- Controls: pooled-common state map, K200-trained common map, universe-specific state map, pooled single best engine, universe-specific single best engine.
- Robustness: early-vs-late Train mapping stability, OOS cell robustness, cross-universe transfer, expanding walk-forward, circular/block bootstrap.

> This is a **diagnostic heterogeneity test**, not a replacement backtest for the production K200 router. The production K200 strategy also uses LARGE_LEAD filtering, Leader override, and state-dependent 30/50/70/80% active budgets. Those are deliberately removed here to isolate engine identity.

## Main OOS result

### Nine-engine candidate set

| Model | Universe | OOS Relative CAGR | IR | Relative MDD |
|---|---|---:|---:|---:|
| Pooled common state map | K200 | -5.00% | -0.481 | -30.48% |
| Universe-specific state map | K200 | -3.37% | -0.344 | -27.00% |
| Pooled single best engine (`REV_BREADTH_50`) | K200 | **+12.37%** | **1.333** | **-6.63%** |
| Universe-specific single best (`EVENT_META_50`) | K200 | -0.84% | -0.043 | -22.77% |
| Pooled common state map | KOSPI ex-K200 | -5.57% | -0.670 | -19.16% |
| Universe-specific state map | KOSPI ex-K200 | +4.98% | 0.572 | **-8.45%** |
| Pooled single best (`REV_BREADTH_50`) | KOSPI ex-K200 | +4.58% | 0.507 | -9.72% |
| Universe-specific single best (`QUALITY_TREND_50`) | KOSPI ex-K200 | **+5.17%** | 0.542 | -10.56% |
| Pooled common state map | KOSDAQ | +2.64% | 0.308 | -14.57% |
| Universe-specific state map | KOSDAQ | +1.76% | 0.247 | -14.58% |
| Pooled single best (`REV_BREADTH_50`) | KOSDAQ | **+12.31%** | **0.958** | **-11.14%** |
| Universe-specific single best (`REV_BREADTH_50`) | KOSDAQ | **+12.31%** | **0.958** | **-11.14%** |

The state-specific router is therefore **not consistently superior to a much simpler fixed-engine model**. KOSDAQ is the clearest example: the Train-selected universe-specific state router earns only +1.76% relative CAGR OOS while simply holding the Train-selected `REV_BREADTH_50` engine earns +12.31%.

## Does universe-specific routing beat pooled-common routing?

OOS paired delta, universe-specific state map minus pooled-common state map:

| Universe | Mean delta / 10D | 95% block-bootstrap CI | P(delta > 0) | Best-1 removed | Best-2 removed |
|---|---:|---:|---:|---:|---:|
| K200 | +6.4bp | -20.2 to +35.2bp | 67.1% | +0.7bp | -3.0bp |
| KOSPI ex-K200 | +44.2bp | -16.7 to +113.4bp | 91.4% | +36.2bp | +28.2bp |
| KOSDAQ | -4.3bp | -44.2 to +34.7bp | 41.3% | -8.3bp | -12.5bp |
| Pooled | +15.4bp | -11.4 to +45.3bp | 86.3% | +12.7bp | +9.9bp |

KOSPI ex-K200 is **suggestive**, but its confidence interval still crosses zero and the pattern does not generalize to K200 or KOSDAQ.

## Train mapping instability

Across the 18 universe × state cells, early-Train and late-Train chose the same engine in only **2/18 cells**.

- K200: 0/6 matches.
- KOSPI ex-K200: 2/6 matches.
- KOSDAQ: 0/6 matches.

Across all 18 cells, the median Spearman correlation between Train and OOS engine rankings is approximately **-0.03** (mean approximately **-0.12**). Only 8/18 cells have a positive ranking correlation.

This is strong evidence that the identity of the in-sample “best engine for a state” is unstable.

## Selected state cells: economic plausibility vs OOS behavior

Examples:

- `KOSPI_EX_K200 / BROAD_RISK_ON` selected `QUALITY_TREND_50` on Train and delivered **+67.5bp/10D** OOS. However the same engine also delivered +62.0bp in K200 and +43.1bp in KOSDAQ during the same state. This looks more like a broadly good OOS engine under BROAD_RISK_ON than an ex-K200-specific economic mechanism.
- `KOSDAQ / RISK_OFF` selected `ABSORPTION_50` and delivered +13.4bp/10D OOS. The same engine delivered +45.6bp in KOSPI ex-K200 and -1.1bp in K200. This **does** have a plausible small/mid-cap gradient (ownership-transfer / reversal / liquidity mechanism), but the Train mapping did not select it for KOSPI ex-K200 and the KOSDAQ cell loses robustness after its best period is removed.
- `K200 / BROAD_RISK_ON` selected `EVENT_META_50` on Train but delivered **-44.7bp/10D** OOS. `QUALITY_TREND_50`, not selected on Train, became the OOS winner.
- `K200 / RISK_OFF` selected `CONTRARIAN_50` and delivered -1.9bp/10D OOS; the same Contrarian engine was negative in ex-K200 and KOSDAQ Risk-Off as well. This does **not** invalidate the production `CONTRARIAN_70` rule because the production rule also requires `LARGE_LEAD` and uses a different risk budget/Leader hierarchy, all intentionally absent from this diagnostic.

## Reduced-candidate robustness: only the three core engine families

To test whether nine engine choices were creating excessive multiple-selection freedom, the same return matrix was re-evaluated using only:

- `VALUE_REV_50`
- `REV_BREADTH_50`
- `CONTRARIAN_50`
- `INDEX_ONLY`

The pooled Train map simplifies almost completely to:

- `REV_BREADTH_50` for BROAD_RISK_ON, HIGH_DISPERSION, HIGH_VOL_CHOP, NARROW_RISK_ON, and NEUTRAL.
- `CONTRARIAN_50` for RISK_OFF.

OOS results:

| Universe | Pooled-common 3-engine Rel CAGR | Universe-specific 3-engine Rel CAGR | Specific − Common mean /10D | Best-1 removed delta |
|---|---:|---:|---:|---:|
| K200 | **+11.81%** | +3.66% | **-33.2bp** | -44.4bp |
| KOSPI ex-K200 | **+5.87%** | +5.40% | -2.2bp | -5.0bp |
| KOSDAQ | **+10.10%** | +5.03% | **-19.1bp** | -27.2bp |

With the candidate freedom reduced, the apparent benefit of universe-specific state routing disappears completely. This materially strengthens the overfit interpretation.

## Decision

**Do not introduce universe-specific State→Engine mappings.**

The economic hypothesis is plausible, and a few individual cells are interesting, but the actual selection process fails the key pre-specified robustness tests:

1. universe-specific mapping does not consistently beat the pooled/common mapping;
2. state-specific mapping often fails to beat a single fixed engine;
3. early-vs-late Train engine identity is extremely unstable;
4. Train engine rankings have near-zero/negative relationship with OOS rankings;
5. reducing the candidate set to the three core engines eliminates the apparent universe-specific advantage.

Therefore the next planned step — **allowing each universe to redefine its own market state** — should **not** be run now. That adds another large layer of degrees of freedom after the simpler heterogeneity hypothesis failed, which would be classic data-mining escalation.

## Research flags, not production changes

Two observations may be worth monitoring on future unseen data rather than optimizing now:

1. `QUALITY_TREND` under `BROAD_RISK_ON` was strong across all three universes OOS. Because this was discovered after looking at OOS, it should be treated only as a forward research flag.
2. `ABSORPTION` under `RISK_OFF` showed a plausible K200 → ex-K200/KOSDAQ small/mid-cap gradient. Again, this was not stable enough ex ante to promote.

## Production implication

Keep the current K200 production Composite router unchanged. The present study says that **data-driven re-estimation of State→Engine rules by universe is not robust enough to justify extra complexity**; it does not say that different universes are economically identical.
