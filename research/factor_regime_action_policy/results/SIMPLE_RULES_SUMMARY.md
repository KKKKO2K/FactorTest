# Simple Investment Rules from Factor Regimes

Core question: keep W+ stock selection fixed and use the contemporaneous regime only for exposure/switching/family tilts. No validation outcome enters rule definitions.

## 2023-2024 rule results

### K200
- ALWAYS_WPLUS: win 53%, mean5 +0.26%, excess +0.19%, CAGR +12.0%, MDD -12.4%
- ALWAYS_EW4: win 53%, mean5 +0.18%, excess +0.11%, CAGR +8.1%, MDD -11.4%
- F_LOW_MARKET: win 56%, mean5 +0.18%, excess +0.11%, CAGR +7.4%, MDD -13.5%
- REPAIR_F_LOW_MARKET: win 54%, mean5 +0.12%, excess +0.05%, CAGR +4.7%, MDD -13.5%
- B2_F_LOW_MARKET: win 54%, mean5 +0.26%, excess +0.19%, CAGR +11.9%, MDD -13.5%
- F_LOW_HALF: win 53%, mean5 +0.20%, excess +0.13%, CAGR +9.4%, MDD -9.7%
- REPAIR_F_LOW_HALF: win 53%, mean5 +0.15%, excess +0.08%, CAGR +6.7%, MDD -9.7%
- B2_F_LOW_HALF: win 53%, mean5 +0.24%, excess +0.17%, CAGR +11.0%, MDD -9.8%
- REPAIR_F_LOW_CASH: win 26%, mean5 +0.04%, excess -0.03%, CAGR +1.3%, MDD -10.7%
- B2_F_LOW_CASH: win 42%, mean5 +0.21%, excess +0.14%, CAGR +9.8%, MDD -7.2%
- B4_F_HIGH_HALF: win 53%, mean5 +0.24%, excess +0.17%, CAGR +10.8%, MDD -11.4%
- B4_MARKET: win 55%, mean5 +0.26%, excess +0.19%, CAGR +11.8%, MDD -13.4%
### KOSDAQ
- ALWAYS_WPLUS: win 58%, mean5 +0.16%, excess +0.13%, CAGR +4.3%, MDD -24.9%
- ALWAYS_EW4: win 59%, mean5 +0.16%, excess +0.13%, CAGR +4.7%, MDD -24.4%
- F_LOW_MARKET: win 56%, mean5 +0.04%, excess +0.01%, CAGR -0.6%, MDD -27.0%
- REPAIR_F_LOW_MARKET: win 58%, mean5 +0.13%, excess +0.10%, CAGR +3.1%, MDD -24.0%
- B2_F_LOW_MARKET: win 58%, mean5 +0.16%, excess +0.13%, CAGR +4.3%, MDD -24.9%
- F_LOW_HALF: win 58%, mean5 +0.07%, excess +0.04%, CAGR +1.6%, MDD -20.2%
- REPAIR_F_LOW_HALF: win 58%, mean5 +0.13%, excess +0.10%, CAGR +3.8%, MDD -20.5%
- B2_F_LOW_HALF: win 58%, mean5 +0.16%, excess +0.13%, CAGR +4.3%, MDD -24.9%
- REPAIR_F_LOW_CASH: win 33%, mean5 +0.10%, excess +0.07%, CAGR +2.7%, MDD -20.6%
- B2_F_LOW_CASH: win 58%, mean5 +0.16%, excess +0.13%, CAGR +4.3%, MDD -24.9%
- B4_F_HIGH_HALF: win 58%, mean5 +0.24%, excess +0.21%, CAGR +8.1%, MDD -25.2%
- B4_MARKET: win 56%, mean5 +0.14%, excess +0.11%, CAGR +3.4%, MDD -26.6%
### KOSDAQ_PLUS_KOSPI_EX_K200
- ALWAYS_WPLUS: win 56%, mean5 +0.10%, excess +0.06%, CAGR +2.7%, MDD -31.2%
- ALWAYS_EW4: win 54%, mean5 +0.14%, excess +0.10%, CAGR +5.0%, MDD -28.5%
- F_LOW_MARKET: win 53%, mean5 +0.02%, excess -0.02%, CAGR -1.6%, MDD -33.3%
- REPAIR_F_LOW_MARKET: win 56%, mean5 +0.06%, excess +0.02%, CAGR +0.2%, MDD -30.7%
- B2_F_LOW_MARKET: win 56%, mean5 +0.10%, excess +0.06%, CAGR +2.4%, MDD -31.9%
- F_LOW_HALF: win 56%, mean5 +0.11%, excess +0.07%, CAGR +4.1%, MDD -19.9%
- REPAIR_F_LOW_HALF: win 56%, mean5 +0.13%, excess +0.09%, CAGR +5.0%, MDD -20.3%
- B2_F_LOW_HALF: win 56%, mean5 +0.10%, excess +0.07%, CAGR +3.4%, MDD -26.7%
- REPAIR_F_LOW_CASH: win 31%, mean5 +0.15%, excess +0.11%, CAGR +6.7%, MDD -12.8%
- B2_F_LOW_CASH: win 48%, mean5 +0.11%, excess +0.07%, CAGR +3.8%, MDD -22.7%
- B4_F_HIGH_HALF: win 56%, mean5 +0.16%, excess +0.12%, CAGR +5.9%, MDD -28.9%
- B4_MARKET: win 53%, mean5 +0.10%, excess +0.06%, CAGR +2.8%, MDD -31.5%
### KOSPI_ALL
- ALWAYS_WPLUS: win 57%, mean5 +0.29%, excess +0.21%, CAGR +13.4%, MDD -15.5%
- ALWAYS_EW4: win 57%, mean5 +0.20%, excess +0.12%, CAGR +9.0%, MDD -13.7%
- F_LOW_MARKET: win 55%, mean5 +0.05%, excess -0.03%, CAGR +1.0%, MDD -17.6%
- REPAIR_F_LOW_MARKET: win 55%, mean5 +0.09%, excess +0.01%, CAGR +3.1%, MDD -17.6%
- B2_F_LOW_MARKET: win 56%, mean5 +0.26%, excess +0.18%, CAGR +11.5%, MDD -13.9%
- F_LOW_HALF: win 57%, mean5 +0.14%, excess +0.06%, CAGR +6.3%, MDD -9.8%
- REPAIR_F_LOW_HALF: win 57%, mean5 +0.15%, excess +0.07%, CAGR +6.5%, MDD -9.8%
- B2_F_LOW_HALF: win 57%, mean5 +0.26%, excess +0.18%, CAGR +12.1%, MDD -11.6%
- REPAIR_F_LOW_CASH: win 28%, mean5 +0.00%, excess -0.08%, CAGR -0.5%, MDD -9.8%
- B2_F_LOW_CASH: win 47%, mean5 +0.23%, excess +0.15%, CAGR +10.5%, MDD -11.5%
- B4_F_HIGH_HALF: win 57%, mean5 +0.32%, excess +0.25%, CAGR +15.6%, MDD -15.3%
- B4_MARKET: win 58%, mean5 +0.28%, excess +0.21%, CAGR +13.3%, MDD -15.9%
### KOSPI_EX_K200
- ALWAYS_WPLUS: win 56%, mean5 +0.19%, excess +0.14%, CAGR +7.6%, MDD -20.0%
- ALWAYS_EW4: win 54%, mean5 +0.14%, excess +0.09%, CAGR +5.4%, MDD -16.7%
- F_LOW_MARKET: win 53%, mean5 +0.09%, excess +0.04%, CAGR +3.1%, MDD -19.5%
- REPAIR_F_LOW_MARKET: win 53%, mean5 +0.09%, excess +0.04%, CAGR +2.9%, MDD -21.7%
- B2_F_LOW_MARKET: win 55%, mean5 +0.10%, excess +0.04%, CAGR +3.1%, MDD -22.1%
- F_LOW_HALF: win 56%, mean5 +0.14%, excess +0.09%, CAGR +6.1%, MDD -10.4%
- REPAIR_F_LOW_HALF: win 56%, mean5 +0.17%, excess +0.11%, CAGR +6.9%, MDD -14.1%
- B2_F_LOW_HALF: win 56%, mean5 +0.19%, excess +0.14%, CAGR +8.1%, MDD -15.8%
- REPAIR_F_LOW_CASH: win 32%, mean5 +0.14%, excess +0.09%, CAGR +5.9%, MDD -12.1%
- B2_F_LOW_CASH: win 44%, mean5 +0.19%, excess +0.14%, CAGR +8.3%, MDD -12.4%
- B4_F_HIGH_HALF: win 56%, mean5 +0.13%, excess +0.08%, CAGR +5.0%, MDD -20.0%
- B4_MARKET: win 54%, mean5 +0.15%, excess +0.10%, CAGR +6.1%, MDD -17.8%
### KOSPI_KOSDAQ_ALL
- ALWAYS_WPLUS: win 52%, mean5 +0.06%, excess +0.05%, CAGR +1.3%, MDD -25.7%
- ALWAYS_EW4: win 55%, mean5 +0.16%, excess +0.14%, CAGR +6.3%, MDD -23.6%
- F_LOW_MARKET: win 51%, mean5 +0.06%, excess +0.05%, CAGR +1.5%, MDD -25.6%
- REPAIR_F_LOW_MARKET: win 54%, mean5 +0.07%, excess +0.06%, CAGR +1.9%, MDD -25.6%
- B2_F_LOW_MARKET: win 51%, mean5 +0.03%, excess +0.02%, CAGR -0.0%, MDD -23.0%
- F_LOW_HALF: win 52%, mean5 +0.12%, excess +0.10%, CAGR +4.9%, MDD -14.9%
- REPAIR_F_LOW_HALF: win 52%, mean5 +0.08%, excess +0.06%, CAGR +2.6%, MDD -16.1%
- B2_F_LOW_HALF: win 52%, mean5 +0.10%, excess +0.09%, CAGR +3.7%, MDD -18.7%
- REPAIR_F_LOW_CASH: win 33%, mean5 +0.09%, excess +0.07%, CAGR +3.5%, MDD -10.9%
- B2_F_LOW_CASH: win 46%, mean5 +0.14%, excess +0.13%, CAGR +5.9%, MDD -14.5%
- B4_F_HIGH_HALF: win 52%, mean5 +0.06%, excess +0.05%, CAGR +1.2%, MDD -25.7%
- B4_MARKET: win 49%, mean5 +0.06%, excess +0.05%, CAGR +1.4%, MDD -25.9%

## 2025 stress: selected simple controls

### K200
- ALWAYS_WPLUS: win 57%, mean5 +1.09%, excess -0.34%, CAGR +67.5%, MDD -8.2%
- REPAIR_F_LOW_MARKET: win 61%, mean5 +1.25%, excess -0.17%, CAGR +81.1%, MDD -9.2%
- REPAIR_F_LOW_HALF: win 57%, mean5 +1.01%, excess -0.41%, CAGR +61.9%, MDD -6.1%
- B2_F_LOW_MARKET: win 57%, mean5 +1.02%, excess -0.41%, CAGR +62.1%, MDD -8.2%
- B4_F_HIGH_HALF: win 57%, mean5 +0.75%, excess -0.67%, CAGR +43.3%, MDD -8.0%
### KOSDAQ
- ALWAYS_WPLUS: win 62%, mean5 +1.05%, excess +0.54%, CAGR +59.7%, MDD -10.1%
- REPAIR_F_LOW_MARKET: win 64%, mean5 +0.93%, excess +0.42%, CAGR +50.7%, MDD -13.8%
- REPAIR_F_LOW_HALF: win 62%, mean5 +1.03%, excess +0.51%, CAGR +58.4%, MDD -9.4%
- B2_F_LOW_MARKET: win 62%, mean5 +1.05%, excess +0.54%, CAGR +59.7%, MDD -10.1%
- B4_F_HIGH_HALF: win 62%, mean5 +0.86%, excess +0.34%, CAGR +46.5%, MDD -10.1%
### KOSDAQ_PLUS_KOSPI_EX_K200
- ALWAYS_WPLUS: win 69%, mean5 +1.13%, excess +0.46%, CAGR +72.2%, MDD -7.6%
- REPAIR_F_LOW_MARKET: win 67%, mean5 +1.13%, excess +0.45%, CAGR +71.8%, MDD -7.4%
- REPAIR_F_LOW_HALF: win 69%, mean5 +1.06%, excess +0.38%, CAGR +66.6%, MDD -5.7%
- B2_F_LOW_MARKET: win 69%, mean5 +1.14%, excess +0.47%, CAGR +73.0%, MDD -6.7%
- B4_F_HIGH_HALF: win 69%, mean5 +1.00%, excess +0.33%, CAGR +62.1%, MDD -7.6%
### KOSPI_ALL
- ALWAYS_WPLUS: win 65%, mean5 +0.97%, excess -0.40%, CAGR +58.5%, MDD -7.5%
- REPAIR_F_LOW_MARKET: win 67%, mean5 +0.95%, excess -0.41%, CAGR +57.1%, MDD -8.0%
- REPAIR_F_LOW_HALF: win 65%, mean5 +0.86%, excess -0.51%, CAGR +50.8%, MDD -5.1%
- B2_F_LOW_MARKET: win 65%, mean5 +0.91%, excess -0.45%, CAGR +54.2%, MDD -7.5%
- B4_F_HIGH_HALF: win 65%, mean5 +0.77%, excess -0.59%, CAGR +45.2%, MDD -6.8%
### KOSPI_EX_K200
- ALWAYS_WPLUS: win 61%, mean5 +0.77%, excess +0.18%, CAGR +44.4%, MDD -5.8%
- REPAIR_F_LOW_MARKET: win 59%, mean5 +0.66%, excess +0.06%, CAGR +36.5%, MDD -6.4%
- REPAIR_F_LOW_HALF: win 61%, mean5 +0.58%, excess -0.02%, CAGR +31.6%, MDD -6.3%
- B2_F_LOW_MARKET: win 61%, mean5 +0.75%, excess +0.15%, CAGR +42.4%, MDD -5.8%
- B4_F_HIGH_HALF: win 61%, mean5 +0.76%, excess +0.16%, CAGR +43.5%, MDD -5.8%
### KOSPI_KOSDAQ_ALL
- ALWAYS_WPLUS: win 67%, mean5 +1.02%, excess -0.25%, CAGR +62.8%, MDD -8.0%
- REPAIR_F_LOW_MARKET: win 65%, mean5 +0.89%, excess -0.38%, CAGR +53.0%, MDD -9.2%
- REPAIR_F_LOW_HALF: win 67%, mean5 +0.98%, excess -0.29%, CAGR +60.5%, MDD -5.7%
- B2_F_LOW_MARKET: win 67%, mean5 +0.96%, excess -0.31%, CAGR +58.3%, MDD -7.8%
- B4_F_HIGH_HALF: win 67%, mean5 +0.90%, excess -0.37%, CAGR +54.0%, MDD -8.0%

## Stable state-specific family tilts over WPLUS

- KOSPI_KOSDAQ_ALL B2|F_HIGH: REVISION - WPLUS +0.39% TRAIN -> +1.00% VALID; win-vs-W+ 59%->62%; n 29/8
- KOSDAQ B4|F_HIGH: VALUE - WPLUS +0.14% TRAIN -> +0.93% VALID; win-vs-W+ 54%->80%; n 48/10
- KOSPI_ALL B4|F_HIGH: REVISION - WPLUS +0.44% TRAIN -> +0.86% VALID; win-vs-W+ 70%->55%; n 44/11
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_HIGH: VALUE - WPLUS +0.22% TRAIN -> +0.84% VALID; win-vs-W+ 54%->56%; n 63/9
- KOSPI_EX_K200 B3|F_HIGH: REVISION - WPLUS +0.36% TRAIN -> +0.66% VALID; win-vs-W+ 66%->54%; n 29/13
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_HIGH: REVISION - WPLUS +0.26% TRAIN -> +0.62% VALID; win-vs-W+ 60%->56%; n 63/9
- KOSPI_KOSDAQ_ALL B2|F_LOW: VALUE - WPLUS +0.04% TRAIN -> +0.59% VALID; win-vs-W+ 45%->69%; n 56/16
- KOSDAQ B4|F_HIGH: REVISION - WPLUS +0.26% TRAIN -> +0.56% VALID; win-vs-W+ 54%->50%; n 48/10
- KOSPI_KOSDAQ_ALL B4|F_LOW: REVISION - WPLUS +0.05% TRAIN -> +0.43% VALID; win-vs-W+ 46%->60%; n 84/15
- K200 B4|F_HIGH: REVISION - WPLUS +0.18% TRAIN -> +0.40% VALID; win-vs-W+ 42%->50%; n 26/10
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_LOW: FLOW - WPLUS +0.12% TRAIN -> +0.28% VALID; win-vs-W+ 47%->67%; n 59/12
- KOSPI_ALL B4|F_LOW: REVISION - WPLUS +0.05% TRAIN -> +0.22% VALID; win-vs-W+ 51%->50%; n 55/10
- KOSPI_EX_K200 B3|F_HIGH: VALUE - WPLUS +0.18% TRAIN -> +0.21% VALID; win-vs-W+ 55%->38%; n 29/13
- KOSDAQ_PLUS_KOSPI_EX_K200 B2|F_LOW: REVISION - WPLUS +0.02% TRAIN -> +0.14% VALID; win-vs-W+ 38%->47%; n 48/17
- KOSDAQ B3|F_LOW: REVISION - WPLUS +0.18% TRAIN -> +0.13% VALID; win-vs-W+ 52%->52%; n 77/31
- KOSDAQ_PLUS_KOSPI_EX_K200 B4|F_LOW: REVISION - WPLUS +0.19% TRAIN -> +0.12% VALID; win-vs-W+ 41%->58%; n 59/12
- KOSDAQ_PLUS_KOSPI_EX_K200 B3|F_LOW: REVISION - WPLUS +0.18% TRAIN -> +0.10% VALID; win-vs-W+ 64%->58%; n 73/31
- K200 B3|F_LOW: MOMENTUM - WPLUS +0.03% TRAIN -> +0.10% VALID; win-vs-W+ 50%->48%; n 86/29
- KOSPI_KOSDAQ_ALL B3|F_LOW: REVISION - WPLUS +0.05% TRAIN -> +0.10% VALID; win-vs-W+ 49%->54%; n 77/24
- K200 B3|F_HIGH: VALUE - WPLUS +0.35% TRAIN -> +0.09% VALID; win-vs-W+ 49%->31%; n 51/16
- KOSDAQ_PLUS_KOSPI_EX_K200 B2|F_LOW: FLOW - WPLUS +0.09% TRAIN -> +0.05% VALID; win-vs-W+ 50%->47%; n 48/17
- KOSPI_KOSDAQ_ALL B2|F_LOW: FLOW - WPLUS +0.08% TRAIN -> +0.04% VALID; win-vs-W+ 52%->38%; n 56/16
- K200 B2|F_LOW: REVISION - WPLUS +0.10% TRAIN -> +0.03% VALID; win-vs-W+ 52%->48%; n 73/21
- K200 B4|F_HIGH: VALUE - WPLUS +0.03% TRAIN -> +0.02% VALID; win-vs-W+ 62%->40%; n 26/10
- KOSPI_EX_K200 B3|F_LOW: REVISION - WPLUS +0.29% TRAIN -> +0.02% VALID; win-vs-W+ 48%->39%; n 73/18
- KOSPI_KOSDAQ_ALL B2|F_LOW: REVISION - WPLUS +0.00% TRAIN -> +0.01% VALID; win-vs-W+ 50%->38%; n 56/16

## Interpretation discipline

- Promotion requires improvement versus ALWAYS_WPLUS, not merely versus the market.
- A rule that helps 2023-2024 but reverses in 2025 is regime-contingent, not a permanent allocation rule.
- Family tilts are candidates only when the same state/action contrast has the same positive sign in TRAIN and VALID with adequate n.

