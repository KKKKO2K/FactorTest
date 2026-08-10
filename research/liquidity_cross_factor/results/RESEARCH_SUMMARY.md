# Trading Value × Cross-Factor Research

Universe: point-in-time KOSPI200. Rebalance/holding: 10 trading days. OOS starts 2023-01-01.
Factor direction is chosen using only pre-2023 mean 10D rank IC and then frozen.
Trading activity features use only information available by rebalance-date close.

## Frozen factor directions

- OP12_REV: HIGH raw value is good; train IC 0.0209 (173 dates)
- OPFY1_REV: HIGH raw value is good; train IC 0.0136 (173 dates)
- PBR12MF: LOW raw value is good; train IC -0.0249 (173 dates)
- PER12MF: LOW raw value is good; train IC -0.0225 (173 dates)
- MOM1M: LOW raw value is good; train IC -0.0261 (173 dates)
- MOM12_1: LOW raw value is good; train IC -0.0192 (173 dates)
- PRIVATE_FLOW: HIGH raw value is good; train IC 0.0231 (173 dates)
- FOREIGN_FLOW: LOW raw value is good; train IC -0.0128 (173 dates)

## Overlay robustness — OOS 2023+

- ACT5_KEEP_TOP70: return improve 71%, Sharpe improve 71%, MDD improve 85%, median return delta 1.99%, median turnover delta 0.14
- ACT5_KEEP_TOP50: return improve 58%, Sharpe improve 58%, MDD improve 85%, median return delta 0.96%, median turnover delta 0.24
- TURNOVER_W10: return improve 56%, Sharpe improve 42%, MDD improve 31%, median return delta 0.87%, median turnover delta 0.02
- ACT5_W10: return improve 56%, Sharpe improve 56%, MDD improve 73%, median return delta 0.60%, median turnover delta 0.07
- RAW_TA_W10: return improve 56%, Sharpe improve 50%, MDD improve 25%, median return delta 0.53%, median turnover delta -0.00
- ACT1_W10: return improve 52%, Sharpe improve 52%, MDD improve 67%, median return delta 0.36%, median turnover delta 0.07
- ACT5_W20: return improve 46%, Sharpe improve 46%, MDD improve 81%, median return delta -0.28%, median turnover delta 0.20
- ACT5_MULTIPLY: return improve 31%, Sharpe improve 31%, MDD improve 77%, median return delta -3.80%, median turnover delta 0.27
- TURNOVER_W20: return improve 27%, Sharpe improve 23%, MDD improve 12%, median return delta -2.36%, median turnover delta 0.05
- ACT5_GT1: return improve 23%, Sharpe improve 29%, MDD improve 60%, median return delta -3.78%, median turnover delta 0.31
- ACT1_W20: return improve 12%, Sharpe improve 12%, MDD improve 60%, median return delta -4.37%, median turnover delta 0.20

## Per-factor key view — Top10 / 30 bps / OOS

- FOREIGN_FLOW: BASE 10.02% / Sh 0.44; best ACT5_KEEP_TOP50 13.92% / Sh 0.56; delta +3.91%
- MOM12_1: BASE -13.92% / Sh -0.31; best TURNOVER_W10 -10.14% / Sh -0.17; delta +3.78%
- MOM1M: BASE 8.23% / Sh 0.42; best ACT5_KEEP_TOP70 17.35% / Sh 0.76; delta +9.11%
- OP12_REV: BASE 20.99% / Sh 0.79; best ACT5_W20 27.79% / Sh 0.97; delta +6.80%
- OPFY1_REV: BASE 29.50% / Sh 1.12; best RAW_TA_W10 41.52% / Sh 1.38; delta +12.02%
- PBR12MF: BASE 20.57% / Sh 0.72; best ACT5_KEEP_TOP70 26.26% / Sh 0.94; delta +5.69%
- PER12MF: BASE 39.26% / Sh 1.44; best ACT5_KEEP_TOP70 39.15% / Sh 1.40; delta -0.11%
- PRIVATE_FLOW: BASE 22.27% / Sh 0.91; best ACT5_KEEP_TOP50 30.26% / Sh 1.19; delta +7.99%

## Standalone trading-value signals — Top10 / 30 bps / OOS

- RAW_HIGH: ann 17.07%, excess 2.76%, Sharpe 0.58, MDD -44.91%, turnover 0.40
- TURNOVER_LOW: ann -0.05%, excess -14.81%, Sharpe 0.08, MDD -21.24%, turnover 0.49
- ACT1_HIGH: ann -0.43%, excess -13.79%, Sharpe 0.12, MDD -28.02%, turnover 0.95
- TURNOVER_HIGH: ann -0.47%, excess -12.90%, Sharpe 0.17, MDD -42.36%, turnover 0.68
- RAW_LOW: ann -3.00%, excess -17.18%, Sharpe -0.07, MDD -28.25%, turnover 0.38
- ACT1_LOW: ann -7.90%, excess -20.34%, Sharpe -0.18, MDD -40.79%, turnover 0.85
- ACT5_LOW: ann -10.76%, excess -22.66%, Sharpe -0.31, MDD -42.39%, turnover 0.82
- ACT5_HIGH: ann -12.32%, excess -24.59%, Sharpe -0.36, MDD -41.47%, turnover 0.95
