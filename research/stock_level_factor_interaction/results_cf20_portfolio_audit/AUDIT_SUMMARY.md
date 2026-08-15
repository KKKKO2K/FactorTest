# CF20 Portfolio Audit

Purpose: reconcile legacy non-overlapping forward-return tests with the daily-NAV implementation before making any strategy-quality claim.

Legacy forward returns use the original implementation, where a stock with any missing daily return in the next 10 days has a NaN 10D return and is skipped by the cross-sectional mean. The audit zero-fill path instead matches the daily NAV convention: missing daily stock returns are treated as 0 while the position remains held.

Benchmarks below are lagged-membership / lagged-total-market-cap universe proxies constructed from the same stock return panel. They are sanity-check benchmarks, not official KOSPI/KOSDAQ/K200 index series; K200 in particular is not free-float weighted here.

## Exact tie-out: simulated daily NAV vs direct 10D holding return

- K200 CF20: PASS; sim-vs-direct max abs 8.882e-16; legacy-minus-direct mean -0.000%; legacy/direct mean abs gap 0.000%; same-phase gap exactly 10 returns 100.0%
- K200 PRIMARY8: PASS; sim-vs-direct max abs 8.812e-16; legacy-minus-direct mean -0.000%; legacy/direct mean abs gap 0.000%; same-phase gap exactly 10 returns 100.0%
- KOSDAQ CF20: PASS; sim-vs-direct max abs 1.277e-15; legacy-minus-direct mean -0.000%; legacy/direct mean abs gap 0.000%; same-phase gap exactly 10 returns 100.0%
- KOSDAQ PRIMARY8: PASS; sim-vs-direct max abs 9.159e-16; legacy-minus-direct mean -0.000%; legacy/direct mean abs gap 0.000%; same-phase gap exactly 10 returns 100.0%
- KOSDAQ_PLUS_KOSPI_EX_K200 CF20: PASS; sim-vs-direct max abs 7.772e-16; legacy-minus-direct mean -0.000%; legacy/direct mean abs gap 0.000%; same-phase gap exactly 10 returns 100.0%
- KOSDAQ_PLUS_KOSPI_EX_K200 PRIMARY8: PASS; sim-vs-direct max abs 8.431e-16; legacy-minus-direct mean -0.000%; legacy/direct mean abs gap 0.000%; same-phase gap exactly 10 returns 100.0%
- KOSPI_ALL CF20: PASS; sim-vs-direct max abs 9.853e-16; legacy-minus-direct mean -0.000%; legacy/direct mean abs gap 0.000%; same-phase gap exactly 10 returns 100.0%
- KOSPI_ALL PRIMARY8: PASS; sim-vs-direct max abs 8.743e-16; legacy-minus-direct mean -0.000%; legacy/direct mean abs gap 0.000%; same-phase gap exactly 10 returns 100.0%
- KOSPI_EX_K200 CF20: PASS; sim-vs-direct max abs 9.992e-16; legacy-minus-direct mean -0.000%; legacy/direct mean abs gap 0.000%; same-phase gap exactly 10 returns 100.0%
- KOSPI_EX_K200 PRIMARY8: PASS; sim-vs-direct max abs 9.680e-16; legacy-minus-direct mean -0.000%; legacy/direct mean abs gap 0.000%; same-phase gap exactly 10 returns 100.0%
- KOSPI_KOSDAQ_ALL CF20: PASS; sim-vs-direct max abs 9.021e-16; legacy-minus-direct mean -0.000%; legacy/direct mean abs gap 0.000%; same-phase gap exactly 10 returns 100.0%
- KOSPI_KOSDAQ_ALL PRIMARY8: PASS; sim-vs-direct max abs 8.882e-16; legacy-minus-direct mean -0.000%; legacy/direct mean abs gap 0.000%; same-phase gap exactly 10 returns 100.0%

## Absolute and benchmark-relative results — 2016-2024, NET30, median across 10 phases

### K200
- PRIMARY8: CAGR +0.99%; MDD -56.1%; Sharpe 0.15; Calmar 0.02; BM CAGR +2.74%; geometric excess CAGR -1.74%; IR -0.14; relative MDD -32.3%
- CF20: CAGR +1.84%; MDD -57.0%; Sharpe 0.19; Calmar 0.03; BM CAGR +2.74%; geometric excess CAGR -0.98%; IR -0.07; relative MDD -31.8%
- CF20 incremental: median dCAGR +0.71%; better CAGR phases 10/10; median dExcessCAGR +0.69%

### KOSPI_EX_K200
- PRIMARY8: CAGR +1.38%; MDD -59.4%; Sharpe 0.17; Calmar 0.02; BM CAGR +1.46%; geometric excess CAGR -0.08%; IR 0.02; relative MDD -22.3%
- CF20: CAGR +1.78%; MDD -58.9%; Sharpe 0.19; Calmar 0.03; BM CAGR +1.46%; geometric excess CAGR +0.39%; IR 0.08; relative MDD -21.1%
- CF20 incremental: median dCAGR +0.60%; better CAGR phases 10/10; median dExcessCAGR +0.59%

### KOSPI_ALL
- PRIMARY8: CAGR +1.56%; MDD -58.4%; Sharpe 0.18; Calmar 0.03; BM CAGR +2.55%; geometric excess CAGR -0.92%; IR -0.04; relative MDD -35.6%
- CF20: CAGR +3.19%; MDD -57.4%; Sharpe 0.26; Calmar 0.06; BM CAGR +2.55%; geometric excess CAGR +0.59%; IR 0.09; relative MDD -31.8%
- CF20 incremental: median dCAGR +1.68%; better CAGR phases 10/10; median dExcessCAGR +1.63%

### KOSDAQ
- PRIMARY8: CAGR -0.61%; MDD -48.0%; Sharpe 0.10; Calmar -0.01; BM CAGR +0.63%; geometric excess CAGR -1.27%; IR -0.11; relative MDD -23.3%
- CF20: CAGR +1.20%; MDD -49.2%; Sharpe 0.17; Calmar 0.02; BM CAGR +0.63%; geometric excess CAGR +0.67%; IR 0.10; relative MDD -23.1%
- CF20 incremental: median dCAGR +1.99%; better CAGR phases 10/10; median dExcessCAGR +1.98%

### KOSPI_KOSDAQ_ALL
- PRIMARY8: CAGR +0.52%; MDD -55.5%; Sharpe 0.13; Calmar 0.01; BM CAGR +2.28%; geometric excess CAGR -1.73%; IR -0.08; relative MDD -27.0%
- CF20: CAGR +3.44%; MDD -55.2%; Sharpe 0.27; Calmar 0.06; BM CAGR +2.28%; geometric excess CAGR +1.13%; IR 0.16; relative MDD -24.4%
- CF20 incremental: median dCAGR +3.18%; better CAGR phases 10/10; median dExcessCAGR +3.11%

### KOSDAQ_PLUS_KOSPI_EX_K200
- PRIMARY8: CAGR -0.48%; MDD -55.2%; Sharpe 0.09; Calmar -0.01; BM CAGR +0.70%; geometric excess CAGR -1.10%; IR -0.11; relative MDD -19.9%
- CF20: CAGR +2.66%; MDD -53.7%; Sharpe 0.23; Calmar 0.05; BM CAGR +0.70%; geometric excess CAGR +2.04%; IR 0.25; relative MDD -18.0%
- CF20 incremental: median dCAGR +2.85%; better CAGR phases 10/10; median dExcessCAGR +2.83%

## Factor-sleeve diagnosis — 2016-2024 zero-fill gross CAGR, median across phases

### K200
- MOM1M: Primary -5.21% / Sharpe -0.17; CF20 -3.23% / Sharpe -0.05
- MOM12_1: Primary +2.00% / Sharpe 0.20; CF20 +2.11% / Sharpe 0.21
- OP12_REV: Primary +5.76% / Sharpe 0.36; CF20 +7.29% / Sharpe 0.45
- OPFY1_REV: Primary +7.59% / Sharpe 0.45; CF20 +7.72% / Sharpe 0.48
- PBR12MF: Primary +5.35% / Sharpe 0.34; CF20 +5.99% / Sharpe 0.37
- PER12MF: Primary +5.68% / Sharpe 0.36; CF20 +6.59% / Sharpe 0.40
- PRIVATE_FLOW: Primary +2.94% / Sharpe 0.25; CF20 +4.40% / Sharpe 0.32
- FOREIGN_FLOW: Primary +3.27% / Sharpe 0.27; CF20 +4.23% / Sharpe 0.30

### KOSPI_EX_K200
- MOM1M: Primary -11.28% / Sharpe -0.31; CF20 -7.89% / Sharpe -0.20
- MOM12_1: Primary -2.40% / Sharpe 0.07; CF20 +0.40% / Sharpe 0.16
- OP12_REV: Primary +15.04% / Sharpe 0.67; CF20 +13.38% / Sharpe 0.64
- OPFY1_REV: Primary +10.57% / Sharpe 0.53; CF20 +10.45% / Sharpe 0.55
- PBR12MF: Primary +6.54% / Sharpe 0.41; CF20 +6.84% / Sharpe 0.41
- PER12MF: Primary +4.85% / Sharpe 0.33; CF20 +3.99% / Sharpe 0.29
- PRIVATE_FLOW: Primary +7.03% / Sharpe 0.42; CF20 +7.57% / Sharpe 0.44
- FOREIGN_FLOW: Primary +1.14% / Sharpe 0.17; CF20 +1.83% / Sharpe 0.20

### KOSPI_ALL
- MOM1M: Primary -10.54% / Sharpe -0.28; CF20 -4.89% / Sharpe -0.09
- MOM12_1: Primary -2.31% / Sharpe 0.09; CF20 -0.05% / Sharpe 0.14
- OP12_REV: Primary +6.27% / Sharpe 0.37; CF20 +10.00% / Sharpe 0.53
- OPFY1_REV: Primary +10.20% / Sharpe 0.53; CF20 +10.85% / Sharpe 0.56
- PBR12MF: Primary +7.65% / Sharpe 0.44; CF20 +8.46% / Sharpe 0.47
- PER12MF: Primary +8.75% / Sharpe 0.49; CF20 +9.08% / Sharpe 0.51
- PRIVATE_FLOW: Primary +8.06% / Sharpe 0.46; CF20 +8.45% / Sharpe 0.48
- FOREIGN_FLOW: Primary +2.61% / Sharpe 0.23; CF20 +5.79% / Sharpe 0.37

### KOSDAQ
- MOM1M: Primary -3.37% / Sharpe 0.08; CF20 -2.31% / Sharpe 0.08
- MOM12_1: Primary -10.63% / Sharpe -0.15; CF20 -3.56% / Sharpe 0.05
- OP12_REV: Primary +13.42% / Sharpe 0.62; CF20 +14.42% / Sharpe 0.66
- OPFY1_REV: Primary +10.67% / Sharpe 0.53; CF20 +10.05% / Sharpe 0.53
- PBR12MF: Primary +2.48% / Sharpe 0.22; CF20 +3.22% / Sharpe 0.26
- PER12MF: Primary +2.81% / Sharpe 0.24; CF20 +4.74% / Sharpe 0.32
- PRIVATE_FLOW: Primary +3.16% / Sharpe 0.25; CF20 +3.82% / Sharpe 0.28
- FOREIGN_FLOW: Primary -3.80% / Sharpe -0.01; CF20 +0.34% / Sharpe 0.15

### KOSPI_KOSDAQ_ALL
- MOM1M: Primary -5.70% / Sharpe 0.01; CF20 -1.41% / Sharpe 0.10
- MOM12_1: Primary -16.03% / Sharpe -0.28; CF20 -5.50% / Sharpe -0.03
- OP12_REV: Primary +11.40% / Sharpe 0.59; CF20 +14.22% / Sharpe 0.72
- OPFY1_REV: Primary +12.92% / Sharpe 0.65; CF20 +13.32% / Sharpe 0.70
- PBR12MF: Primary +6.69% / Sharpe 0.40; CF20 +8.37% / Sharpe 0.46
- PER12MF: Primary +10.66% / Sharpe 0.57; CF20 +12.04% / Sharpe 0.63
- PRIVATE_FLOW: Primary +4.80% / Sharpe 0.31; CF20 +8.09% / Sharpe 0.43
- FOREIGN_FLOW: Primary -2.09% / Sharpe 0.04; CF20 +4.68% / Sharpe 0.31

### KOSDAQ_PLUS_KOSPI_EX_K200
- MOM1M: Primary -6.60% / Sharpe -0.02; CF20 -4.22% / Sharpe 0.01
- MOM12_1: Primary -13.64% / Sharpe -0.22; CF20 -6.40% / Sharpe -0.03
- OP12_REV: Primary +13.80% / Sharpe 0.64; CF20 +17.20% / Sharpe 0.78
- OPFY1_REV: Primary +13.39% / Sharpe 0.64; CF20 +15.44% / Sharpe 0.73
- PBR12MF: Primary +4.82% / Sharpe 0.33; CF20 +6.53% / Sharpe 0.40
- PER12MF: Primary +6.89% / Sharpe 0.41; CF20 +10.48% / Sharpe 0.57
- PRIVATE_FLOW: Primary +4.07% / Sharpe 0.28; CF20 +5.67% / Sharpe 0.35
- FOREIGN_FLOW: Primary -4.49% / Sharpe -0.02; CF20 +1.70% / Sharpe 0.20

## Audit guardrails

- If simulated daily NAV does not match the direct zero-fill 10D holding return, the portfolio implementation is invalid and must be fixed before interpretation.
- If simulated/direct tie but legacy differs materially, prior forward-return summaries and daily NAV are answering slightly different missing-data questions; both should be restated consistently.
- CF20 was originally validated as an incremental overlay versus each primary-factor sleeve. A weak equal-notional 8-sleeve aggregate does not contradict a positive incremental overlay, but it does invalidate any claim that the aggregate CF20 portfolio itself was previously proven to be a strong standalone strategy.
- Benchmark-relative results use internal cap-weighted proxies only; official index data should replace them before production-level attribution.
