# Nested Contemporaneous Regime Test

Question: after defining the current market/liquidity regime with only market trend, volatility, drawdown and trading-value breadth, do factor interactions split that same regime into economically distinct contemporaneous sub-regimes?

Procedure: KMeans BASE K=4 fit on 2016-2022 and frozen. Within each BASE state, KMeans K=2 is fit only on six factor-interaction variables and frozen. F_HIGH/F_LOW are ordered by a contemporaneous factor-health score; no forward outcome enters fitting or naming.

## BASE state profiles

### K200
- B1: n=5, ret60 -20.8%, vol20 61.0%, DD60 -23.2%, liq 57%; next20 +8.87%
- B2: n=97, ret60 -7.1%, vol20 17.5%, DD60 -9.3%, liq 39%; next20 +0.45%
- B3: n=137, ret60 +3.5%, vol20 14.1%, DD60 -2.9%, liq 31%; next20 -0.26%
- B4: n=94, ret60 +7.3%, vol20 12.7%, DD60 -1.2%, liq 56%; next20 +0.73%
### KOSPI_ALL
- B1: n=5, ret60 -20.9%, vol20 61.1%, DD60 -23.2%, liq 54%; next20 +9.98%
- B2: n=93, ret60 -7.4%, vol20 17.4%, DD60 -9.5%, liq 35%; next20 +0.49%
- B3: n=136, ret60 +3.5%, vol20 14.0%, DD60 -2.9%, liq 31%; next20 -0.06%
- B4: n=99, ret60 +6.7%, vol20 11.8%, DD60 -1.3%, liq 49%; next20 +0.25%
### KOSPI_EX_K200
- B1: n=35, ret60 -14.0%, vol20 32.7%, DD60 -16.9%, liq 35%; next20 +4.61%
- B2: n=118, ret60 -5.4%, vol20 15.3%, DD60 -7.8%, liq 32%; next20 -1.96%
- B3: n=108, ret60 +4.7%, vol20 10.9%, DD60 -1.7%, liq 47%; next20 +0.58%
- B4: n=71, ret60 +11.9%, vol20 16.9%, DD60 -1.9%, liq 28%; next20 +0.88%
### KOSDAQ
- B1: n=5, ret60 -18.1%, vol20 77.5%, DD60 -21.0%, liq 47%; next20 +18.72%
- B2: n=72, ret60 -11.7%, vol20 28.6%, DD60 -14.6%, liq 30%; next20 +1.65%
- B3: n=145, ret60 +3.4%, vol20 18.4%, DD60 -4.4%, liq 30%; next20 -0.42%
- B4: n=111, ret60 +6.8%, vol20 16.1%, DD60 -2.1%, liq 44%; next20 -0.33%

## Factor sub-state contrasts that survive TRAIN -> 2023-2024

- KOSPI_EX_K200 B2 NEXT_BASE_UP: F_HIGH-F_LOW TRAIN +7.43%, 23-24 +24.18%; min n 38/13; base distance 0.61z/0.70z, factor distance 2.64z/2.45z
- KOSPI_ALL B2 NEXT_BASE_UP: F_HIGH-F_LOW TRAIN +10.35%, 23-24 +18.75%; min n 25/8; base distance 1.27z/1.03z, factor distance 2.99z/3.12z
- KOSDAQ_PLUS_KOSPI_EX_K200 B4 NEXT_BASE_DOWN: F_HIGH-F_LOW TRAIN -0.35%, 23-24 -16.67%; min n 59/9; base distance 0.76z/1.42z, factor distance 2.38z/3.79z
- KOSDAQ_PLUS_KOSPI_EX_K200 B3 NEXT_BASE_UP: F_HIGH-F_LOW TRAIN +16.15%, 23-24 +15.32%; min n 67/24; base distance 1.02z/1.14z, factor distance 2.43z/2.92z
- KOSPI_EX_K200 B2 NEXT_BASE_DOWN: F_HIGH-F_LOW TRAIN -8.75%, 23-24 -14.29%; min n 38/13; base distance 0.61z/0.70z, factor distance 2.64z/2.45z
- KOSDAQ_PLUS_KOSPI_EX_K200 B3 NEXT_BASE_DOWN: F_HIGH-F_LOW TRAIN -4.99%, 23-24 -12.90%; min n 67/24; base distance 1.02z/1.14z, factor distance 2.43z/2.92z
- KOSPI_ALL B3 NEXT_BASE_DOWN: F_HIGH-F_LOW TRAIN -7.62%, 23-24 -12.90%; min n 45/21; base distance 1.19z/1.00z, factor distance 2.85z/3.10z
- KOSDAQ B3 NEXT_BASE_DOWN: F_HIGH-F_LOW TRAIN -5.63%, 23-24 -9.68%; min n 68/20; base distance 0.97z/1.10z, factor distance 2.59z/2.60z
- K200 B3 NEXT_BASE_DOWN: F_HIGH-F_LOW TRAIN -12.72%, 23-24 -7.54%; min n 51/16; base distance 0.90z/0.88z, factor distance 2.70z/2.49z
- KOSDAQ B3 NEXT_BASE_UP: F_HIGH-F_LOW TRAIN +10.71%, 23-24 +7.10%; min n 68/20; base distance 0.97z/1.10z, factor distance 2.59z/2.60z
- KOSPI_KOSDAQ_ALL B2 NEXT_BASE_UP: F_HIGH-F_LOW TRAIN +9.73%, 23-24 +6.25%; min n 29/8; base distance 1.51z/0.80z, factor distance 2.68z/2.77z
- KOSPI_KOSDAQ_ALL B3 NEXT_BASE_DOWN: F_HIGH-F_LOW TRAIN -10.32%, 23-24 -4.49%; min n 57/24; base distance 0.91z/1.54z, factor distance 2.47z/2.87z
- K200 B4 NEXT_BASE_DOWN: F_HIGH-F_LOW TRAIN -6.90%, 23-24 -3.33%; min n 26/10; base distance 0.88z/0.36z, factor distance 2.72z/2.60z
- KOSDAQ B3 MKT_FWD_DD20: F_HIGH-F_LOW TRAIN +0.53%, 23-24 +2.38%; min n 68/20; base distance 0.97z/1.10z, factor distance 2.59z/2.60z
- KOSDAQ B4 MKT_FWD_DD20: F_HIGH-F_LOW TRAIN -2.37%, 23-24 -1.74%; min n 48/10; base distance 0.31z/1.43z, factor distance 2.22z/3.74z
- KOSPI_KOSDAQ_ALL B2 MKT_FWD_DD20: F_HIGH-F_LOW TRAIN +0.95%, 23-24 +1.56%; min n 29/8; base distance 1.51z/0.80z, factor distance 2.68z/2.77z
- KOSDAQ B4 MKT_FWD_20D: F_HIGH-F_LOW TRAIN -2.60%, 23-24 -1.52%; min n 48/10; base distance 0.31z/1.43z, factor distance 2.22z/3.74z
- KOSDAQ_PLUS_KOSPI_EX_K200 B4 MKT_FWD_DD20: F_HIGH-F_LOW TRAIN -1.13%, 23-24 -1.35%; min n 59/9; base distance 0.76z/1.42z, factor distance 2.38z/3.79z
- KOSPI_EX_K200 B2 MKT_FWD_DD20: F_HIGH-F_LOW TRAIN +0.87%, 23-24 +1.26%; min n 38/13; base distance 0.61z/0.70z, factor distance 2.64z/2.45z
- KOSPI_ALL B2 MKT_FWD_20D: F_HIGH-F_LOW TRAIN -0.54%, 23-24 -1.03%; min n 25/8; base distance 1.27z/1.03z, factor distance 2.99z/3.12z
- KOSDAQ_PLUS_KOSPI_EX_K200 B4 MKT_FWD_20D: F_HIGH-F_LOW TRAIN -0.91%, 23-24 -0.97%; min n 59/9; base distance 0.76z/1.42z, factor distance 2.38z/3.79z
- KOSPI_EX_K200 B3 MKT_FWD_DD20: F_HIGH-F_LOW TRAIN -0.63%, 23-24 -0.22%; min n 29/13; base distance 0.77z/0.81z, factor distance 2.76z/3.21z
- K200 B4 NEXT_BASE_UP: F_HIGH-F_LOW TRAIN +0.00%, 23-24 +0.00%; min n 26/10; base distance 0.88z/0.36z, factor distance 2.72z/2.60z
- KOSDAQ B4 NEXT_BASE_UP: F_HIGH-F_LOW TRAIN +0.00%, 23-24 +0.00%; min n 48/10; base distance 0.31z/1.43z, factor distance 2.22z/3.74z
- KOSDAQ_PLUS_KOSPI_EX_K200 B4 NEXT_BASE_UP: F_HIGH-F_LOW TRAIN +0.00%, 23-24 +0.00%; min n 59/9; base distance 0.76z/1.42z, factor distance 2.38z/3.79z
- KOSPI_ALL B4 NEXT_BASE_UP: F_HIGH-F_LOW TRAIN +0.00%, 23-24 +0.00%; min n 44/10; base distance 0.52z/0.63z, factor distance 2.65z/3.11z
- KOSPI_EX_K200 B4 NEXT_BASE_UP: F_HIGH-F_LOW TRAIN +0.00%, 23-24 +0.00%; min n 29/8; base distance 1.43z/1.01z, factor distance 2.89z/3.09z

## All 2023-2024 nested contrasts with adequate n

- K200 B4: n H/L=10/15, base distance 0.36z, factor distance 2.60z; next20 diff +2.28%, downside diff +0.32%, next-base-up diff +0.0%
- KOSDAQ_PLUS_KOSPI_EX_K200 B3: n H/L=24/31, base distance 1.14z, factor distance 2.92z; next20 diff +1.86%, downside diff +2.22%, next-base-up diff +15.3%
- KOSDAQ B3: n H/L=20/31, base distance 1.10z, factor distance 2.60z; next20 diff +1.84%, downside diff +2.38%, next-base-up diff +7.1%
- KOSPI_ALL B4: n H/L=11/10, base distance 0.63z, factor distance 3.11z; next20 diff +1.81%, downside diff +1.12%, next-base-up diff +0.0%
- KOSDAQ B4: n H/L=10/12, base distance 1.43z, factor distance 3.74z; next20 diff -1.52%, downside diff -1.74%, next-base-up diff +0.0%
- K200 B3: n H/L=16/29, base distance 0.88z, factor distance 2.49z; next20 diff -1.40%, downside diff -1.61%, next-base-up diff +16.8%
- KOSPI_ALL B3: n H/L=21/31, base distance 1.00z, factor distance 3.10z; next20 diff -1.27%, downside diff -0.97%, next-base-up diff -5.1%
- KOSPI_ALL B2: n H/L=8/16, base distance 1.03z, factor distance 3.12z; next20 diff -1.03%, downside diff -0.96%, next-base-up diff +18.8%
- KOSDAQ_PLUS_KOSPI_EX_K200 B4: n H/L=9/12, base distance 1.42z, factor distance 3.79z; next20 diff -0.97%, downside diff -1.35%, next-base-up diff +0.0%
- KOSPI_KOSDAQ_ALL B3: n H/L=26/24, base distance 1.54z, factor distance 2.87z; next20 diff -0.91%, downside diff -0.48%, next-base-up diff +6.7%
- KOSPI_EX_K200 B4: n H/L=8/18, base distance 1.01z, factor distance 3.09z; next20 diff +0.71%, downside diff +1.35%, next-base-up diff +0.0%
- KOSPI_KOSDAQ_ALL B2: n H/L=8/16, base distance 0.80z, factor distance 2.77z; next20 diff -0.45%, downside diff +1.56%, next-base-up diff +6.2%
- KOSPI_EX_K200 B2: n H/L=13/21, base distance 0.70z, factor distance 2.45z; next20 diff -0.35%, downside diff +1.26%, next-base-up diff +24.2%
- KOSPI_EX_K200 B3: n H/L=13/18, base distance 0.81z, factor distance 3.21z; next20 diff +0.19%, downside diff -0.22%, next-base-up diff -4.7%

## Interpretation rules

- The strongest evidence for incremental factor-state information is: small BASE-feature distance, large factor-feature distance, adequate samples, and same-direction TRAIN/2023-2024 differences in transition or downside/return outcomes.
- 2025 and 2026 are stress/regime diagnostics, not pooled validation.
- If no stable nested split survives, factor interaction is better treated as descriptive context rather than a standalone contemporaneous regime discriminator.

