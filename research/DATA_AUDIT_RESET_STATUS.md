# Data Audit Reset — Corrected Status

## Scope
Read-only audit of `source/factor_all_values` on source SHA `02edffa087462a8354c25ee9c80537b64ad1210c`, updated after the user clarified the intended market-cap eligibility rule and point-in-time consensus construction.

## Canonical interpretation after clarification
The research universe is **not all listed stocks without a size screen**. It is a point-in-time investable universe formed by a market-cap floor, then split into K200 / KOSPI ex-K200 / KOSDAQ and their composites.

The user described the floor as roughly KRW 200bn. Empirical row-set matching across 521 sampled dates shows that the stored factor rows are in fact closest to a **KRW 250bn PIT market-cap cutoff**:
- 250bn cutoff median row-set Jaccard: 0.9735
- median precision: 98.77%
- median recall: 98.84%
- median factor-only mismatch: 8 names
- median cutoff-eligible missing factor row: 7 names

By comparison, a 200bn cutoff has median Jaccard 0.8356 and recall 83.76%.

Therefore the canonical universe should be treated as approximately:

> KOSPI/KOSDAQ stocks satisfying the PIT ~KRW 250bn market-cap eligibility screen, with subsequent market/K200 sub-universe splits.

The small residual mismatch near the boundary can reflect exact source timing, security-type rules, or cutoff conventions and should not be interpreted as a broad coverage defect.

## What is actually present
- 2,599 dated files per factor/reference dataset, 2016-01-04 through 2026-08-07, with no date gaps versus the basic-info calendar.
- 8 point-in-time factor raw-value snapshots: MOM1M, MOM12_1, OP12_REV, OPFY1_REV, PBR12MF, PER12MF, PRIVATE_FLOW, FOREIGN_FLOW.
- Daily basic info: market label, K200 flag, adjusted daily return, market cap.
- Daily trading amount: essentially complete for eligible/listed names.
- Separate daily universe-definition snapshot with K200 membership consistent with basic info.

## Correction 1 — prior 'non-K200 coverage defect' conclusion is withdrawn
The earlier audit compared factor rows against every listed KOSPI/KOSDAQ stock and therefore found only 32.7% row membership in KOSPI ex-K200 and 18.9% in KOSDAQ. That was the wrong denominator for the intended strategy universe.

Given the PIT market-cap eligibility rule, those omitted smaller stocks are **out of universe by design**. Accordingly:
- `KOSDAQ` means KOSDAQ names inside the eligible market-cap screen;
- `KOSPI_EX_K200` means eligible KOSPI names outside K200;
- composite universes are unions of the eligible sub-universes.

These are valid full universes **within the strategy's explicit investability screen**.

## Correction 2 — prior survivorship warning is withdrawn as a primary defect
The basic-info master is a static/superset row list: later IPOs already appear as rows in early files, while historical market labels/returns/market caps determine whether they are actually eligible at each date.

A static superset row master is not survivorship bias by itself. For this research, eligibility is determined point-in-time from market status and market cap. The user further clarified that names that eventually delist are below the investable market-cap cutoff and therefore would not be eligible for the strategy universe.

Thus the previous inference from the endpoint master row set to material survivorship bias was an over-interpretation and should not be used as a blocker.

## Correction 3 — estimate/revision factors are point-in-time
The user confirmed that the revision factors use the consensus snapshot that was actually available on each historical date. Therefore the earlier request for separate as-of provenance as a prerequisite is removed.

Missing OP revision / PER / PBR values should instead be interpreted mainly as **consensus availability / analyst-coverage missingness**, not as evidence of look-ahead or broken row coverage.

Observed valid-given-eligible-row rates remain economically relevant:
- K200: roughly 87-89% for OP revision / PER / PBR
- eligible KOSPI ex-K200 and KOSDAQ: materially lower for consensus-dependent factors
- Momentum and flow factors are near-complete conditional on eligibility

For cross-factor research, do not automatically force the all-8-factor intersection. Compare:
1. each factor on its native valid universe; and
2. a matched-consensus/common-coverage robustness sample when factor-to-factor comparability matters.

## Sector / industry mapping
The user supplied a stock-level `WICS업종명(중)` mapping alongside code/name/fiscal year-end.

Audit of the supplied mapping:
- master rows: 2,557
- distinct nonblank WICS middle-level categories: 29
- blank WICS labels: 14

This is sufficient for the initial sector-aware research layer:
- sector-neutral factor ranks / portfolios;
- factor alpha attribution into within-sector vs sector-allocation components;
- sector concentration and sector breadth diagnostics;
- cross-factor sector exposure overlap.

Blank classifications should be retained as `UNKNOWN` rather than dropping the stocks.

The supplied mapping appears to be a current/static classification. Historical PIT WICS is optional rather than required for the first research pass; it becomes useful only if historical sector reclassification itself materially affects results.

## Current data inventory — research-ready
### Stock/date primitives
- PIT adjusted daily stock return
- PIT market cap
- PIT market / K200 membership
- daily trading amount
- 8 PIT factor values
- current WICS middle-industry mapping

### Eligible universe
- empirical operating cutoff: ~KRW 250bn PIT market cap
- sub-universes: K200, eligible KOSPI ex-K200, eligible KOSDAQ, and their composites

### Time span
- 2016-01-04 through 2026-08-07

## Remaining data that would add the most research value
These are **not prerequisites** for restarting factor research.

### Highest incremental value
1. **Analyst coverage / consensus microstructure**
   - analyst count / estimate count
   - consensus dispersion
   - number of upward/downward revisions
   - age since latest estimate update
   - useful for distinguishing strong revision information from thin/noisy consensus and for modelling signal confidence.

2. **Earnings realization / event data**
   - quarterly actual OP/earnings
   - consensus immediately before result
   - earnings surprise
   - earnings announcement date
   - lets us test whether revision-factor strength reflects genuine information that converts into realized earnings rather than only price-correlated consensus movement.

3. **Raw investor-flow components**
   - daily foreign / pension / mutual fund / private / retail net buy values or ratios
   - current factor scores are useful, but raw flows allow persistence, acceleration, breadth, crowding and cross-investor confirmation to be studied without being locked to the existing factor transformation.

4. **Crowding / positioning data**
   - stock lending balance / utilization
   - short-sale balance or short-sale value
   - ownership / ETF-index exposure if available
   - especially useful for identifying when a statistically strong factor is already crowded and vulnerable to unwind.

### Useful but lower priority
5. Historical WICS classifications if strict PIT sector-neutralization becomes necessary.
6. Free-float market cap / free-float shares and trading-halt / price-limit flags for finer implementation modelling; daily trading amount already provides a strong liquidity input.
7. Official market / sector index return series for benchmark attribution. Market and sector proxies can already be built from the stock panel, so these are convenience/validation data rather than required inputs.
8. External market-state variables such as rates, FX and volatility indices only if the research question explicitly expands beyond stock/factor information.

## Research implication
The dataset is much more usable than the first audit interpretation suggested.

The correct starting point is now:

> **PIT ~KRW 250bn+ Korean equity universe × 8 factors × daily stock returns/market cap/trading amount × K200/market membership × WICS sector.**

This is sufficient to restart factor-selection research from stock-level primitives without waiting for a rebuilt full-market dataset.

The most important methodological caution is no longer survivorship. It is **factor-dependent signal availability**, especially the much thinner consensus coverage for revision/value factors outside K200. Future research should explicitly distinguish a factor's economic effect from the analyst-coverage universe on which that factor can be observed.
