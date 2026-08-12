# Nested Transition Block-Bootstrap

Moving-block bootstrap: 3000 replications, block length 4 consecutive 5D state dates (~20 trading days). State definitions are fixed; this tests sampling uncertainty, not model-selection uncertainty.

- K200 B3 NEXT_BASE_DOWN TRAIN_2016_2022: H-L -12.72%, 95% block CI [-22.83%, -2.89%], P(>0) 0%, P(<0) 100%, n H/L=51/86
- K200 B3 NEXT_BASE_DOWN VALID_2023_2024: H-L -7.54%, 95% block CI [-25.00%, +10.56%], P(>0) 19%, P(<0) 80%, n H/L=16/29
- K200 B3 NEXT_BASE_DOWN STRESS_2025: H-L -12.50%, 95% block CI [-40.00%, +0.00%], P(>0) 0%, P(<0) 69%, n H/L=10/8
- KOSPI_ALL B2 NEXT_BASE_UP TRAIN_2016_2022: H-L +10.35%, 95% block CI [-7.26%, +33.82%], P(>0) 86%, P(<0) 14%, n H/L=25/68
- KOSPI_ALL B2 NEXT_BASE_UP VALID_2023_2024: H-L +18.75%, 95% block CI [-12.50%, +57.14%], P(>0) 84%, P(<0) 11%, n H/L=8/16
- KOSPI_ALL B3 NEXT_BASE_DOWN TRAIN_2016_2022: H-L -7.62%, 95% block CI [-17.57%, +2.89%], P(>0) 7%, P(<0) 92%, n H/L=45/91
- KOSPI_ALL B3 NEXT_BASE_DOWN VALID_2023_2024: H-L -12.90%, 95% block CI [-26.92%, -2.86%], P(>0) 0%, P(<0) 99%, n H/L=21/31
- KOSPI_ALL B3 NEXT_BASE_DOWN STRESS_2025: H-L -11.11%, 95% block CI [-33.33%, +0.00%], P(>0) 0%, P(<0) 68%, n H/L=9/9
- KOSPI_EX_K200 B2 NEXT_BASE_UP TRAIN_2016_2022: H-L +7.43%, 95% block CI [-8.54%, +24.16%], P(>0) 81%, P(<0) 18%, n H/L=38/80
- KOSPI_EX_K200 B2 NEXT_BASE_UP VALID_2023_2024: H-L +24.18%, 95% block CI [-8.65%, +63.14%], P(>0) 93%, P(<0) 7%, n H/L=13/21
- KOSPI_EX_K200 B2 NEXT_BASE_DOWN TRAIN_2016_2022: H-L -8.75%, 95% block CI [-14.67%, -3.49%], P(>0) 0%, P(<0) 100%, n H/L=38/80
- KOSPI_EX_K200 B2 NEXT_BASE_DOWN VALID_2023_2024: H-L -14.29%, 95% block CI [-27.27%, +0.00%], P(>0) 0%, P(<0) 96%, n H/L=13/21
- KOSDAQ B3 NEXT_BASE_UP TRAIN_2016_2022: H-L +10.71%, 95% block CI [-2.03%, +23.70%], P(>0) 95%, P(<0) 5%, n H/L=68/77
- KOSDAQ B3 NEXT_BASE_UP VALID_2023_2024: H-L +7.10%, 95% block CI [-13.77%, +27.28%], P(>0) 74%, P(<0) 25%, n H/L=20/31
- KOSDAQ B3 NEXT_BASE_UP STRESS_2025: H-L +9.03%, 95% block CI [-26.19%, +41.24%], P(>0) 70%, P(<0) 28%, n H/L=16/9
- KOSDAQ B3 NEXT_BASE_DOWN TRAIN_2016_2022: H-L -5.63%, 95% block CI [-15.05%, +4.32%], P(>0) 13%, P(<0) 87%, n H/L=68/77
- KOSDAQ B3 NEXT_BASE_DOWN VALID_2023_2024: H-L -9.68%, 95% block CI [-17.65%, +0.00%], P(>0) 0%, P(<0) 96%, n H/L=20/31
- KOSDAQ B3 NEXT_BASE_DOWN STRESS_2025: H-L -11.11%, 95% block CI [-30.77%, +0.00%], P(>0) 0%, P(<0) 67%, n H/L=16/9
- KOSDAQ B3 MKT_FWD_DD20 TRAIN_2016_2022: H-L +0.53%, 95% block CI [-1.64%, +2.56%], P(>0) 68%, P(<0) 32%, n H/L=68/77
- KOSDAQ B3 MKT_FWD_DD20 VALID_2023_2024: H-L +2.38%, 95% block CI [-0.65%, +5.38%], P(>0) 93%, P(<0) 7%, n H/L=20/31
- KOSDAQ B3 MKT_FWD_DD20 STRESS_2025: H-L +2.55%, 95% block CI [-0.87%, +6.04%], P(>0) 91%, P(<0) 9%, n H/L=16/9
- KOSDAQ B4 MKT_FWD_20D TRAIN_2016_2022: H-L -2.60%, 95% block CI [-5.76%, +0.33%], P(>0) 5%, P(<0) 95%, n H/L=48/63
- KOSDAQ B4 MKT_FWD_20D VALID_2023_2024: H-L -1.52%, 95% block CI [-5.44%, +2.91%], P(>0) 22%, P(<0) 78%, n H/L=10/12
- KOSDAQ B4 MKT_FWD_20D STRESS_2025: H-L +1.86%, 95% block CI [-4.05%, +8.87%], P(>0) 69%, P(<0) 31%, n H/L=11/9
- KOSDAQ_PLUS_KOSPI_EX_K200 B3 NEXT_BASE_UP TRAIN_2016_2022: H-L +16.15%, 95% block CI [+1.90%, +30.29%], P(>0) 99%, P(<0) 1%, n H/L=67/73
- KOSDAQ_PLUS_KOSPI_EX_K200 B3 NEXT_BASE_UP VALID_2023_2024: H-L +15.32%, 95% block CI [-3.28%, +37.22%], P(>0) 94%, P(<0) 5%, n H/L=24/31
- KOSDAQ_PLUS_KOSPI_EX_K200 B3 NEXT_BASE_UP STRESS_2025: H-L +0.84%, 95% block CI [-36.91%, +40.00%], P(>0) 50%, P(<0) 48%, n H/L=17/7
- KOSDAQ_PLUS_KOSPI_EX_K200 B3 NEXT_BASE_DOWN TRAIN_2016_2022: H-L -4.99%, 95% block CI [-14.90%, +4.37%], P(>0) 14%, P(<0) 86%, n H/L=67/73
- KOSDAQ_PLUS_KOSPI_EX_K200 B3 NEXT_BASE_DOWN VALID_2023_2024: H-L -12.90%, 95% block CI [-25.81%, -3.03%], P(>0) 0%, P(<0) 99%, n H/L=24/31
- KOSDAQ_PLUS_KOSPI_EX_K200 B3 NEXT_BASE_DOWN STRESS_2025: H-L -14.29%, 95% block CI [-50.00%, +0.00%], P(>0) 0%, P(<0) 68%, n H/L=17/7
- KOSDAQ_PLUS_KOSPI_EX_K200 B4 MKT_FWD_20D TRAIN_2016_2022: H-L -0.91%, 95% block CI [-3.24%, +1.51%], P(>0) 22%, P(<0) 78%, n H/L=63/59
- KOSDAQ_PLUS_KOSPI_EX_K200 B4 MKT_FWD_20D VALID_2023_2024: H-L -0.97%, 95% block CI [-4.76%, +3.51%], P(>0) 31%, P(<0) 69%, n H/L=9/12
- KOSDAQ_PLUS_KOSPI_EX_K200 B4 MKT_FWD_20D STRESS_2025: H-L +1.85%, 95% block CI [-4.70%, +7.79%], P(>0) 68%, P(<0) 32%, n H/L=12/9

Interpretation: transition-probability rows are percentage-point differences. For future drawdown, a positive H-L means a less-negative/better downside path for F_HIGH; for future return, positive means higher return.
