# 2016-2022 Historical Subperiod Validation

Purpose: test whether the 2016-2022 discovery block hides internal regime mixing. Calendar splits are descriptive: 2016-2019, 2020-2021, and 2022. Prior-60D market-state bins use tercile thresholds fit only on 2016-2019.
Family states retain the existing Q33 thresholds fit on the full 2016-2022 discovery sample, so within-discovery state comparisons are diagnostic rather than untouched OOS.

## Market baselines

- K200: EARLY_2016_2019: trail60 +0.89%, next20 +0.43%; COVID_LIQUIDITY_2020_2021: trail60 +4.85%, next20 +1.24%; BEAR_2022: trail60 -5.23%, next20 -1.29%
- KOSPI_ALL: EARLY_2016_2019: trail60 +0.74%, next20 +0.37%; COVID_LIQUIDITY_2020_2021: trail60 +5.05%, next20 +1.32%; BEAR_2022: trail60 -5.62%, next20 -1.41%
- KOSPI_EX_K200: EARLY_2016_2019: trail60 -0.49%, next20 -0.11%; COVID_LIQUIDITY_2020_2021: trail60 +7.13%, next20 +2.20%; BEAR_2022: trail60 -8.40%, next20 -2.27%
- KOSDAQ: EARLY_2016_2019: trail60 +0.46%, next20 +0.22%; COVID_LIQUIDITY_2020_2021: trail60 +6.31%, next20 +1.86%; BEAR_2022: trail60 -7.76%, next20 -2.08%

## Breadth H-L by subperiod

- K200 RELATIVE_WORKING_BREADTH: EARLY_2016_2019 -0.48%; COVID_LIQUIDITY_2020_2021 +1.78%; BEAR_2022 -0.41%
- K200 ABS_CONFIRMED_BREADTH: EARLY_2016_2019 -1.32%; COVID_LIQUIDITY_2020_2021 +2.51%; BEAR_2022 -2.71%
- K200 DEFENSIVE_WORKING_BREADTH: EARLY_2016_2019 +0.38%; COVID_LIQUIDITY_2020_2021 -1.10%; BEAR_2022 +3.14%
- KOSPI_ALL RELATIVE_WORKING_BREADTH: EARLY_2016_2019 -0.78%; COVID_LIQUIDITY_2020_2021 +1.88%; BEAR_2022 +1.94%
- KOSPI_ALL ABS_CONFIRMED_BREADTH: EARLY_2016_2019 -1.90%; COVID_LIQUIDITY_2020_2021 +3.13%; BEAR_2022 -3.94%
- KOSPI_ALL DEFENSIVE_WORKING_BREADTH: EARLY_2016_2019 +1.73%; COVID_LIQUIDITY_2020_2021 -0.92%; BEAR_2022 +2.66%
- KOSPI_EX_K200 RELATIVE_WORKING_BREADTH: EARLY_2016_2019 -0.14%; COVID_LIQUIDITY_2020_2021 +1.08%; BEAR_2022 +0.01%
- KOSPI_EX_K200 ABS_CONFIRMED_BREADTH: EARLY_2016_2019 -1.23%; COVID_LIQUIDITY_2020_2021 +1.81%; BEAR_2022 +0.22%
- KOSPI_EX_K200 DEFENSIVE_WORKING_BREADTH: EARLY_2016_2019 +0.74%; COVID_LIQUIDITY_2020_2021 -0.31%; BEAR_2022 -1.55%
- KOSDAQ RELATIVE_WORKING_BREADTH: EARLY_2016_2019 -1.50%; COVID_LIQUIDITY_2020_2021 -0.14%; BEAR_2022 +1.78%
- KOSDAQ ABS_CONFIRMED_BREADTH: EARLY_2016_2019 -1.97%; COVID_LIQUIDITY_2020_2021 -3.97%; BEAR_2022 -4.64%
- KOSDAQ DEFENSIVE_WORKING_BREADTH: EARLY_2016_2019 +0.89%; COVID_LIQUIDITY_2020_2021 +1.31%; BEAR_2022 +5.86%

## W+/W+ pair effects — median excess vs same-period unconditional

- K200 EARLY_2016_2019: 6/6 pairs, median excess -2.62%, positive 0/6
- K200 COVID_LIQUIDITY_2020_2021: 5/6 pairs, median excess +0.92%, positive 4/5
- KOSPI_ALL EARLY_2016_2019: 6/6 pairs, median excess -0.86%, positive 0/6
- KOSPI_ALL COVID_LIQUIDITY_2020_2021: 6/6 pairs, median excess -0.02%, positive 3/6
- KOSPI_EX_K200 EARLY_2016_2019: 5/6 pairs, median excess -0.99%, positive 0/5
- KOSPI_EX_K200 COVID_LIQUIDITY_2020_2021: 6/6 pairs, median excess -0.79%, positive 2/6
- KOSPI_EX_K200 BEAR_2022: 1/6 pairs, median excess +0.30%, positive 1/1
- KOSDAQ EARLY_2016_2019: 6/6 pairs, median excess -1.18%, positive 1/6
- KOSDAQ COVID_LIQUIDITY_2020_2021: 4/6 pairs, median excess -2.34%, positive 0/4

## Revision W+ -> Flow W+ vs Flow Neutral

- K200 EARLY_2016_2019: diff -3.48%, n 13/24, prior60 +2.64%/+3.97%
- K200 COVID_LIQUIDITY_2020_2021: diff -2.16%, n 18/13, prior60 +9.80%/+10.44%
- K200 FULL_2016_2022: diff -2.24%, n 33/38, prior60 +5.92%/+5.97%
- KOSDAQ EARLY_2016_2019: diff +1.28%, n 11/23, prior60 +1.27%/+0.50%
- KOSDAQ COVID_LIQUIDITY_2020_2021: diff -2.42%, n 9/8, prior60 +10.30%/+7.79%
- KOSDAQ FULL_2016_2022: diff -0.88%, n 24/31, prior60 +3.26%/+2.38%
- KOSDAQ_PLUS_KOSPI_EX_K200 EARLY_2016_2019: diff +0.93%, n 12/24, prior60 +2.24%/+2.22%
- KOSDAQ_PLUS_KOSPI_EX_K200 COVID_LIQUIDITY_2020_2021: diff -6.48%, n 16/8, prior60 +11.58%/+12.95%
- KOSDAQ_PLUS_KOSPI_EX_K200 FULL_2016_2022: diff -0.73%, n 32/35, prior60 +5.33%/+4.47%
- KOSPI_ALL EARLY_2016_2019: diff +1.06%, n 13/23, prior60 +2.91%/+4.37%
- KOSPI_ALL COVID_LIQUIDITY_2020_2021: diff +2.62%, n 21/12, prior60 +10.13%/+6.64%
- KOSPI_ALL FULL_2016_2022: diff +1.96%, n 38/40, prior60 +6.33%/+3.79%
- KOSPI_EX_K200 EARLY_2016_2019: diff -0.70%, n 15/22, prior60 +5.05%/+0.69%
- KOSPI_EX_K200 COVID_LIQUIDITY_2020_2021: diff -0.82%, n 24/11, prior60 +13.19%/+6.20%
- KOSPI_EX_K200 FULL_2016_2022: diff -0.12%, n 45/40, prior60 +8.07%/+0.39%
- KOSPI_KOSDAQ_ALL EARLY_2016_2019: diff +2.75%, n 11/22, prior60 +1.18%/+2.00%
- KOSPI_KOSDAQ_ALL COVID_LIQUIDITY_2020_2021: diff -2.34%, n 21/12, prior60 +8.68%/+13.33%
- KOSPI_KOSDAQ_ALL FULL_2016_2022: diff +1.00%, n 34/39, prior60 +5.51%/+4.88%

## Interpretation guardrail

- If calendar subperiod signs flip but same-prior60-bin signs are more stable, prefer market-state conditioning over calendar labels.
- If both calendar and prior-market-state conditioning flip, treat the discovery-era relation as unstable rather than a structural signal.
- Do not use the pooled 2016-2022 mean as evidence of stability unless the subperiod decomposition supports it.
