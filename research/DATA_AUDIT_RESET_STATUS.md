# Data Audit Reset — Status

## Scope
Read-only audit of `source/factor_all_values` on source SHA `02edffa087462a8354c25ee9c80537b64ad1210c`.

## What is actually present
- 2,599 dated files per factor/reference dataset, 2016-01-04 through 2026-08-07, with no date gaps versus the basic-info calendar.
- 8 factor raw-value snapshots: MOM1M, MOM12_1, OP12_REV, OPFY1_REV, PBR12MF, PER12MF, PRIVATE_FLOW, FOREIGN_FLOW.
- Daily basic info includes market label, K200 flag, adjusted return, market cap.
- Daily trading amount is present and essentially complete for listed names.
- A separate daily universe-definition snapshot agrees closely with basic-info K200 membership.

## Critical finding 1 — factor row universe is not the whole market
All 8 factor files share essentially the same row universe on a date (median pairwise row-set Jaccard 1.000). Median rows per factor file are ~664 and the row set is extremely close to a same-N top-market-cap screen (median Jaccard 0.978; 98.9% of covered listed names are in the same-N top-mcap set).

Median row membership coverage:
- K200: 100%
- KOSPI ex-K200: 32.7%
- KOSDAQ: 18.9%

Size structure:
- KOSPI ex-K200: Q1-Q3 market-cap quintiles have 0% factor row coverage; Q4 partial; Q5 essentially full for momentum/flow.
- KOSDAQ: Q1-Q4 have 0% factor row coverage; only Q5 is materially covered.

Therefore prior labels such as `KOSDAQ`, `KOSPI_EX_K200`, or `KOSPI_KOSDAQ_ALL` should not be interpreted as full-market factor tests. They are tests on the factor-covered large/mid-cap subset inside those market definitions.

## Critical finding 2 — fundamental/estimate factors have additional missingness
Conditional on being in the common factor row universe:
- K200 valid coverage is ~87-89% for OP revision / PER / PBR.
- KOSPI ex-K200 and KOSDAQ valid-given-row is only ~50-53% for those factors.
- Momentum and flow factors are ~98-100% valid conditional on row membership.

Thus all-8-factor intersection coverage is much narrower:
- K200 ~85.5%
- KOSPI ex-K200 ~15.5%
- KOSDAQ ~9.3%

Do not impose the all-8 intersection on single-factor studies unless economically required.

## Critical finding 3 — survivorship / master-universe lineage is not clean
The basic-info master has exactly 2,557 rows at both endpoints and endpoint row-set Jaccard 1.000. All 907 names that are listed at the final date but were not listed in 2016 already exist as rows in the 2016 master. By contrast only 8 names classified as listed in the first snapshot are not listed at the final snapshot.

The factor row universe is also extremely persistent: each factor has 664 rows at the first date and 730 at the last date, with 663 of the original 664 rows still present at the endpoint.

This structure is consistent with a current/superset security master backfilled through history and raises material survivorship concerns. It is not sufficient to prove every historical membership field is wrong, but it means historical-delisting completeness must be fixed or independently validated before treating long-horizon backtests as survivorship-free.

A sanity check is the known historical delisting of Hanjin Shipping (A117930) in 2017: it is not represented among the dataset's eight 2016-listed/final-not-listed names, which confirms at least one historically listed security is absent from the historical universe representation.

## What is reliable enough now
### Strongest
- Date alignment and daily continuity.
- Daily adjusted returns, market cap, trading amount for names present in the master.
- Internal K200 membership consistency between basic info and universe definition.
- Stock-level factor values for the common large/mid-cap row universe.

### Usable with explicit scope caveat
- K200 factor research, subject to survivorship/data-lineage validation.
- Non-K200 research only if renamed/redefined as `factor-covered large/mid-cap subset`, not full KOSPI ex-K200 / KOSDAQ.

### Not suitable for full-market claims yet
- Full KOSDAQ factor results.
- Full KOSPI ex-K200 factor results.
- Full KOSPI+KOSDAQ factor selection using the current factor snapshots.
- Any long-horizon claim that assumes complete historical delisted-security coverage.

## Data required before the next serious reset
### Priority 0 — required
1. **Point-in-time complete security master including delisted names**
   - code, name, security type, listing date, delisting date, market by date, K200 membership by date;
   - include securities that existed historically even if absent today.

2. **Full-universe factor snapshots or an explicit documented eligible-universe definition**
   - ideally every KOSPI/KOSDAQ ordinary share as of each date;
   - retain NA when a factor is unavailable rather than silently omitting the security row;
   - if the intended factor universe is top ~700 by market cap, encode that rule explicitly and stop calling it `ALL`.

3. **Point-in-time / as-of provenance for estimate-based factors**
   - exact source-field definitions;
   - whether historical values are true as-of snapshots or later-restated/backfilled histories;
   - observation timestamp / publication lag for FY1/12MF estimates and revisions.

### Priority 1 — highest incremental research value
4. **Point-in-time sector / industry classifications** (WICS/GICS/KRX)
   - needed to distinguish factor alpha from sector rotation and to run sector-neutral factor portfolios.

5. **Analyst coverage / estimate breadth / dispersion / revision counts**
   - especially for OPFY1/OP12, PER/PBR;
   - lets us distinguish `no signal because no analyst coverage` from a neutral factor value and study factor-confidence directly.

6. **Tradability / implementation fields**
   - free-float market cap or shares, volume, trading-halt/suspension flags, price-limit flags, preferably bid-ask spread or an impact proxy.

### Priority 2 — useful for richer factor-selection/crowding work
7. Raw investor-flow components (foreign, pension, institutional, private, retail) rather than only derived flow factors.
8. Short-sale / stock-lending balances and utilization for crowding / unwind-risk studies.
9. Ownership / index / ETF exposure if available, for crowding and mechanical-flow attribution.
10. Official KOSPI/KOSDAQ/K200 index returns and sector-index returns for cleaner benchmark attribution.

## Research implication
Before inventing another factor-selection model, the next decision should be one of two clean paths:

- **Path A: accept the current ~top-700 large/mid-cap coverage universe**, rename it explicitly, fix survivorship/as-of issues, and do research only within that scope; or
- **Path B: rebuild the raw factor snapshots for the full point-in-time KOSPI/KOSDAQ universe**, then restart broad-universe factor research.

The second path is necessary if the research question explicitly includes small/mid-cap KOSDAQ and KOSPI ex-K200 behavior.