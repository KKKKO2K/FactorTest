# Train-Only Investment Playbook Validation

All state->family choices below are fit only on 2016-2022. 2023-2024 and 2025 are untouched by the choice rule. This replaces the exploratory look-ahead overlay.

## Frozen family-tilt choices

### TILT_0BP_W50
- K200 B2|F_LOW: REVISION; TRAIN edge +0.10%, pair-win 52%, n=73
- K200 B3|F_HIGH: FLOW; TRAIN edge +0.06%, pair-win 57%, n=51
- K200 B3|F_LOW: MOMENTUM; TRAIN edge +0.03%, pair-win 50%, n=86
- K200 B4|F_HIGH: VALUE; TRAIN edge +0.03%, pair-win 62%, n=26
- KOSDAQ B3|F_LOW: REVISION; TRAIN edge +0.18%, pair-win 52%, n=77
- KOSDAQ B4|F_HIGH: REVISION; TRAIN edge +0.26%, pair-win 54%, n=48
- KOSDAQ B4|F_LOW: REVISION; TRAIN edge +0.19%, pair-win 51%, n=63
- KOSDAQ_PLUS_KOSPI_EX_K200 B2|F_LOW: VALUE; TRAIN edge +0.15%, pair-win 52%, n=48
- KOSDAQ_PLUS_KOSPI_EX_K200 B3|F_LOW: REVISION; TRAIN edge +0.18%, pair-win 64%, n=73
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_HIGH: REVISION; TRAIN edge +0.26%, pair-win 60%, n=63
- KOSPI_ALL B2|F_LOW: FLOW; TRAIN edge +0.08%, pair-win 56%, n=68
- KOSPI_ALL B3|F_HIGH: VALUE; TRAIN edge +0.38%, pair-win 53%, n=45
- KOSPI_ALL B4|F_HIGH: REVISION; TRAIN edge +0.44%, pair-win 70%, n=44
- KOSPI_ALL B4|F_LOW: REVISION; TRAIN edge +0.05%, pair-win 51%, n=55
- KOSPI_EX_K200 B2|F_HIGH: VALUE; TRAIN edge +0.16%, pair-win 55%, n=38
- KOSPI_EX_K200 B2|F_LOW: REVISION; TRAIN edge +0.08%, pair-win 50%, n=80
- KOSPI_EX_K200 B3|F_HIGH: REVISION; TRAIN edge +0.36%, pair-win 66%, n=29
- KOSPI_EX_K200 B4|F_HIGH: REVISION; TRAIN edge +0.20%, pair-win 62%, n=29
- KOSPI_EX_K200 B4|F_LOW: MOMENTUM; TRAIN edge +0.26%, pair-win 54%, n=39
- KOSPI_KOSDAQ_ALL B2|F_HIGH: REVISION; TRAIN edge +0.39%, pair-win 59%, n=29
- KOSPI_KOSDAQ_ALL B2|F_LOW: FLOW; TRAIN edge +0.08%, pair-win 52%, n=56
- KOSPI_KOSDAQ_ALL B4|F_HIGH: VALUE; TRAIN edge +0.59%, pair-win 56%, n=25
### TILT_10BP_W55
- KOSDAQ_PLUS_KOSPI_EX_K200 B3|F_LOW: REVISION; TRAIN edge +0.18%, pair-win 64%, n=73
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_HIGH: REVISION; TRAIN edge +0.26%, pair-win 60%, n=63
- KOSPI_ALL B4|F_HIGH: REVISION; TRAIN edge +0.44%, pair-win 70%, n=44
- KOSPI_EX_K200 B2|F_HIGH: VALUE; TRAIN edge +0.16%, pair-win 55%, n=38
- KOSPI_EX_K200 B3|F_HIGH: REVISION; TRAIN edge +0.36%, pair-win 66%, n=29
- KOSPI_EX_K200 B4|F_HIGH: REVISION; TRAIN edge +0.20%, pair-win 62%, n=29
- KOSPI_KOSDAQ_ALL B2|F_HIGH: REVISION; TRAIN edge +0.39%, pair-win 59%, n=29
- KOSPI_KOSDAQ_ALL B4|F_HIGH: VALUE; TRAIN edge +0.59%, pair-win 56%, n=25
### TILT_20BP_W55
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_HIGH: REVISION; TRAIN edge +0.26%, pair-win 60%, n=63
- KOSPI_ALL B4|F_HIGH: REVISION; TRAIN edge +0.44%, pair-win 70%, n=44
- KOSPI_EX_K200 B3|F_HIGH: REVISION; TRAIN edge +0.36%, pair-win 66%, n=29
- KOSPI_KOSDAQ_ALL B2|F_HIGH: REVISION; TRAIN edge +0.39%, pair-win 59%, n=29
- KOSPI_KOSDAQ_ALL B4|F_HIGH: VALUE; TRAIN edge +0.59%, pair-win 56%, n=25
### TILT_20BP_W60
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_HIGH: REVISION; TRAIN edge +0.26%, pair-win 60%, n=63
- KOSPI_ALL B4|F_HIGH: REVISION; TRAIN edge +0.44%, pair-win 70%, n=44
- KOSPI_EX_K200 B3|F_HIGH: REVISION; TRAIN edge +0.36%, pair-win 66%, n=29
- KOSPI_KOSDAQ_ALL B4|F_HIGH: REVISION; TRAIN edge +0.42%, pair-win 80%, n=25

## 2023-2024 overall performance vs WPLUS

### K200
- TILT_0BP_W50: switch 78%, mean5 +0.26%, edge -0.01%, beat-W+ 38%, CAGR +11.9%, MDD -11.5%
- TILT_10BP_W55: switch 0%, mean5 +0.26%, edge +0.00%, beat-W+ 0%, CAGR +12.0%, MDD -12.4%
- TILT_20BP_W55: switch 0%, mean5 +0.26%, edge +0.00%, beat-W+ 0%, CAGR +12.0%, MDD -12.4%
- TILT_20BP_W60: switch 0%, mean5 +0.26%, edge +0.00%, beat-W+ 0%, CAGR +12.0%, MDD -12.4%
### KOSDAQ
- TILT_0BP_W50: switch 73%, mean5 +0.28%, edge +0.11%, beat-W+ 36%, CAGR +9.3%, MDD -24.7%
- TILT_10BP_W55: switch 0%, mean5 +0.16%, edge +0.00%, beat-W+ 0%, CAGR +4.3%, MDD -24.9%
- TILT_20BP_W55: switch 0%, mean5 +0.16%, edge +0.00%, beat-W+ 0%, CAGR +4.3%, MDD -24.9%
- TILT_20BP_W60: switch 0%, mean5 +0.16%, edge +0.00%, beat-W+ 0%, CAGR +4.3%, MDD -24.9%
### KOSDAQ_PLUS_KOSPI_EX_K200
- TILT_0BP_W50: switch 59%, mean5 +0.19%, edge +0.09%, beat-W+ 33%, CAGR +8.1%, MDD -23.3%
- TILT_10BP_W55: switch 42%, mean5 +0.19%, edge +0.09%, beat-W+ 24%, CAGR +7.7%, MDD -26.6%
- TILT_20BP_W55: switch 9%, mean5 +0.16%, edge +0.06%, beat-W+ 5%, CAGR +6.0%, MDD -28.5%
- TILT_20BP_W60: switch 9%, mean5 +0.16%, edge +0.06%, beat-W+ 5%, CAGR +6.0%, MDD -28.5%
### KOSPI_ALL
- TILT_0BP_W50: switch 60%, mean5 +0.31%, edge +0.02%, beat-W+ 28%, CAGR +14.7%, MDD -14.9%
- TILT_10BP_W55: switch 11%, mean5 +0.39%, edge +0.10%, beat-W+ 6%, CAGR +19.3%, MDD -15.8%
- TILT_20BP_W55: switch 11%, mean5 +0.39%, edge +0.10%, beat-W+ 6%, CAGR +19.3%, MDD -15.8%
- TILT_20BP_W60: switch 11%, mean5 +0.39%, edge +0.10%, beat-W+ 6%, CAGR +19.3%, MDD -15.8%
### KOSPI_EX_K200
- TILT_0BP_W50: switch 80%, mean5 +0.14%, edge -0.05%, beat-W+ 34%, CAGR +5.2%, MDD -21.2%
- TILT_10BP_W55: switch 37%, mean5 +0.18%, edge -0.01%, beat-W+ 14%, CAGR +7.4%, MDD -19.6%
- TILT_20BP_W55: switch 14%, mean5 +0.28%, edge +0.09%, beat-W+ 8%, CAGR +12.5%, MDD -20.0%
- TILT_20BP_W60: switch 14%, mean5 +0.28%, edge +0.09%, beat-W+ 8%, CAGR +12.5%, MDD -20.0%
### KOSPI_KOSDAQ_ALL
- TILT_0BP_W50: switch 32%, mean5 +0.18%, edge +0.12%, beat-W+ 17%, CAGR +7.2%, MDD -21.2%
- TILT_10BP_W55: switch 16%, mean5 +0.18%, edge +0.11%, beat-W+ 10%, CAGR +7.0%, MDD -20.8%
- TILT_20BP_W55: switch 16%, mean5 +0.18%, edge +0.11%, beat-W+ 10%, CAGR +7.0%, MDD -20.8%
- TILT_20BP_W60: switch 7%, mean5 +0.10%, edge +0.04%, beat-W+ 6%, CAGR +3.2%, MDD -25.7%

## Switched-state edge only

### VALID_2023_2024
- KOSPI_ALL TILT_20BP_W60: n=11, family-vs-W+ mean +0.86%, win 55%, absolute win 55%
- KOSPI_ALL TILT_20BP_W55: n=11, family-vs-W+ mean +0.86%, win 55%, absolute win 55%
- KOSPI_ALL TILT_10BP_W55: n=11, family-vs-W+ mean +0.86%, win 55%, absolute win 55%
- KOSPI_KOSDAQ_ALL TILT_20BP_W55: n=15, family-vs-W+ mean +0.73%, win 67%, absolute win 53%
- KOSPI_KOSDAQ_ALL TILT_10BP_W55: n=15, family-vs-W+ mean +0.73%, win 67%, absolute win 53%
- KOSPI_EX_K200 TILT_20BP_W60: n=13, family-vs-W+ mean +0.66%, win 54%, absolute win 46%
- KOSPI_EX_K200 TILT_20BP_W55: n=13, family-vs-W+ mean +0.66%, win 54%, absolute win 46%
- KOSDAQ_PLUS_KOSPI_EX_K200 TILT_20BP_W60: n=9, family-vs-W+ mean +0.62%, win 56%, absolute win 67%
- KOSDAQ_PLUS_KOSPI_EX_K200 TILT_20BP_W55: n=9, family-vs-W+ mean +0.62%, win 56%, absolute win 67%
- KOSPI_KOSDAQ_ALL TILT_20BP_W60: n=7, family-vs-W+ mean +0.52%, win 86%, absolute win 71%
- KOSPI_KOSDAQ_ALL TILT_0BP_W50: n=31, family-vs-W+ mean +0.37%, win 52%, absolute win 48%
- KOSDAQ_PLUS_KOSPI_EX_K200 TILT_10BP_W55: n=40, family-vs-W+ mean +0.22%, win 57%, absolute win 55%
- KOSDAQ TILT_0BP_W50: n=53, family-vs-W+ mean +0.15%, win 49%, absolute win 62%
- KOSDAQ_PLUS_KOSPI_EX_K200 TILT_0BP_W50: n=57, family-vs-W+ mean +0.15%, win 56%, absolute win 54%
- KOSPI_ALL TILT_0BP_W50: n=58, family-vs-W+ mean +0.03%, win 47%, absolute win 57%
- K200 TILT_0BP_W50: n=76, family-vs-W+ mean -0.01%, win 49%, absolute win 54%
- KOSPI_EX_K200 TILT_10BP_W55: n=34, family-vs-W+ mean -0.02%, win 38%, absolute win 59%
- KOSPI_EX_K200 TILT_0BP_W50: n=73, family-vs-W+ mean -0.06%, win 42%, absolute win 55%
### STRESS_2025
- KOSPI_KOSDAQ_ALL TILT_20BP_W60: n=10, family-vs-W+ mean +0.44%, win 70%, absolute win 80%
- KOSPI_ALL TILT_20BP_W55: n=19, family-vs-W+ mean +0.25%, win 63%, absolute win 74%
- KOSPI_ALL TILT_10BP_W55: n=19, family-vs-W+ mean +0.25%, win 63%, absolute win 74%
- KOSPI_ALL TILT_20BP_W60: n=19, family-vs-W+ mean +0.25%, win 63%, absolute win 74%
- KOSDAQ_PLUS_KOSPI_EX_K200 TILT_10BP_W55: n=19, family-vs-W+ mean +0.23%, win 58%, absolute win 74%
- K200 TILT_0BP_W50: n=42, family-vs-W+ mean +0.22%, win 50%, absolute win 62%
- KOSPI_ALL TILT_0BP_W50: n=39, family-vs-W+ mean +0.19%, win 56%, absolute win 79%
- KOSPI_EX_K200 TILT_10BP_W55: n=16, family-vs-W+ mean +0.19%, win 56%, absolute win 56%
- KOSPI_EX_K200 TILT_0BP_W50: n=35, family-vs-W+ mean +0.15%, win 57%, absolute win 60%
- KOSDAQ_PLUS_KOSPI_EX_K200 TILT_0BP_W50: n=22, family-vs-W+ mean +0.14%, win 55%, absolute win 73%
- KOSPI_EX_K200 TILT_20BP_W60: n=8, family-vs-W+ mean +0.11%, win 50%, absolute win 50%
- KOSPI_EX_K200 TILT_20BP_W55: n=8, family-vs-W+ mean +0.11%, win 50%, absolute win 50%
- KOSPI_KOSDAQ_ALL TILT_0BP_W50: n=15, family-vs-W+ mean -0.03%, win 47%, absolute win 67%
- KOSDAQ_PLUS_KOSPI_EX_K200 TILT_20BP_W55: n=12, family-vs-W+ mean -0.04%, win 42%, absolute win 75%
- KOSDAQ_PLUS_KOSPI_EX_K200 TILT_20BP_W60: n=12, family-vs-W+ mean -0.04%, win 42%, absolute win 75%
- KOSDAQ TILT_0BP_W50: n=29, family-vs-W+ mean -0.05%, win 34%, absolute win 62%
- KOSPI_KOSDAQ_ALL TILT_10BP_W55: n=12, family-vs-W+ mean -0.05%, win 50%, absolute win 67%
- KOSPI_KOSDAQ_ALL TILT_20BP_W55: n=12, family-vs-W+ mean -0.05%, win 50%, absolute win 67%

## Cross-universe allocation edge vs EW3: moving-block bootstrap

- TRAIN_2016_2022 HEALTH_2X: edge +0.01%/5D, win 25%, 95% CI [-0.02%,+0.03%], P(edge>0) 72%, n=247
- TRAIN_2016_2022 FHIGH_ONLY: edge +0.02%/5D, win 25%, 95% CI [-0.07%,+0.10%], P(edge>0) 65%, n=247
- TRAIN_2016_2022 BASE_WEIGHT: edge +0.01%/5D, win 53%, 95% CI [+0.00%,+0.02%], P(edge>0) 99%, n=247
- TRAIN_2016_2022 HEALTH_BASE: edge +0.02%/5D, win 54%, 95% CI [-0.00%,+0.04%], P(edge>0) 97%, n=247
- VALID_2023_2024 HEALTH_2X: edge +0.00%/5D, win 33%, 95% CI [-0.06%,+0.06%], P(edge>0) 51%, n=73
- VALID_2023_2024 FHIGH_ONLY: edge +0.03%/5D, win 33%, 95% CI [-0.19%,+0.25%], P(edge>0) 63%, n=73
- VALID_2023_2024 BASE_WEIGHT: edge -0.02%/5D, win 41%, 95% CI [-0.05%,+0.01%], P(edge>0) 9%, n=73
- VALID_2023_2024 HEALTH_BASE: edge -0.02%/5D, win 40%, 95% CI [-0.07%,+0.03%], P(edge>0) 21%, n=73
- STRESS_2025 HEALTH_2X: edge +0.04%/5D, win 42%, 95% CI [-0.02%,+0.10%], P(edge>0) 92%, n=45
- STRESS_2025 FHIGH_ONLY: edge +0.13%/5D, win 42%, 95% CI [-0.09%,+0.35%], P(edge>0) 88%, n=45
- STRESS_2025 BASE_WEIGHT: edge +0.02%/5D, win 58%, 95% CI [-0.00%,+0.06%], P(edge>0) 94%, n=45
- STRESS_2025 HEALTH_BASE: edge +0.05%/5D, win 67%, 95% CI [-0.00%,+0.11%], P(edge>0) 97%, n=45
- STRESS_2026 HEALTH_2X: edge +0.07%/5D, win 38%, 95% CI [-0.11%,+0.23%], P(edge>0) 79%, n=13
- STRESS_2026 FHIGH_ONLY: edge +0.12%/5D, win 38%, 95% CI [-0.63%,+0.78%], P(edge>0) 64%, n=13
- STRESS_2026 BASE_WEIGHT: edge +0.05%/5D, win 69%, 95% CI [-0.01%,+0.11%], P(edge>0) 95%, n=13
- STRESS_2026 HEALTH_BASE: edge +0.09%/5D, win 69%, 95% CI [+0.01%,+0.17%], P(edge>0) 99%, n=13

## Decision rules

- Promote a family tilt only if TRAIN-only selection produces positive overall edge in 2023-2024 and switched-state edge remains positive; 2025 should not materially reverse.
- Promote cross-universe weighting only if edge vs EW3 is positive in TRAIN and VALID with reasonable bootstrap support; 2025/2026 are stress confirmation, not discovery.

