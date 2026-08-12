# Confirmatory CROSS_FAMILY_W20 Grid

Rule is frozen from the prior stock-level result: 80% primary factor stock score + 20% consensus score from the other three factor families. No weight optimization is performed here. Rebalance interval equals the forward horizon, so 5D/10D/20D observations are non-overlapping by construction.

## Core-block sign robustness by horizon / TopN

- K200 H5 Top10: gross -0.03%->+0.11%->+0.02%; net30 -0.04%->+0.10%->+0.01%; positive families 1/4->4/4->3/4; FAIL
- K200 H5 Top20: gross +0.01%->+0.00%->+0.05%; net30 +0.00%->+0.00%->+0.04%; positive families 3/4->3/4->4/4; PASS
- K200 H10 Top10: gross -0.11%->+0.18%->+0.09%; net30 -0.12%->+0.17%->+0.07%; positive families 1/4->4/4->3/4; FAIL
- K200 H10 Top20: gross +0.03%->-0.01%->+0.07%; net30 +0.02%->-0.01%->+0.07%; positive families 4/4->1/4->3/4; FAIL
- K200 H20 Top10: gross -0.16%->+0.26%->+0.22%; net30 -0.17%->+0.24%->+0.20%; positive families 1/4->4/4->3/4; FAIL
- K200 H20 Top20: gross +0.02%->+0.13%->-0.07%; net30 +0.02%->+0.12%->-0.07%; positive families 2/4->3/4->1/4; FAIL
- KOSDAQ H5 Top10: gross +0.06%->+0.00%->+0.03%; net30 +0.05%->-0.02%->+0.01%; positive families 4/4->2/4->2/4; FAIL
- KOSDAQ H5 Top20: gross +0.06%->+0.07%->+0.02%; net30 +0.06%->+0.07%->+0.01%; positive families 3/4->3/4->2/4; PASS
- KOSDAQ H10 Top10: gross +0.09%->+0.10%->-0.17%; net30 +0.08%->+0.08%->-0.19%; positive families 3/4->3/4->0/4; FAIL
- KOSDAQ H10 Top20: gross +0.04%->+0.07%->+0.05%; net30 +0.04%->+0.06%->+0.04%; positive families 3/4->3/4->2/4; PASS
- KOSDAQ H20 Top10: gross -0.03%->+0.19%->+0.17%; net30 -0.05%->+0.16%->+0.15%; positive families 1/4->3/4->3/4; FAIL
- KOSDAQ H20 Top20: gross +0.02%->-0.01%->+0.24%; net30 +0.02%->-0.02%->+0.23%; positive families 3/4->2/4->2/4; FAIL
- KOSDAQ_PLUS_KOSPI_EX_K200 H5 Top10: gross +0.19%->+0.11%->-0.03%; net30 +0.18%->+0.08%->-0.05%; positive families 4/4->4/4->2/4; FAIL
- KOSDAQ_PLUS_KOSPI_EX_K200 H5 Top20: gross +0.08%->+0.14%->+0.09%; net30 +0.07%->+0.13%->+0.07%; positive families 3/4->4/4->3/4; PASS
- KOSDAQ_PLUS_KOSPI_EX_K200 H10 Top10: gross +0.21%->+0.08%->-0.17%; net30 +0.19%->+0.04%->-0.20%; positive families 4/4->3/4->1/4; FAIL
- KOSDAQ_PLUS_KOSPI_EX_K200 H10 Top20: gross +0.09%->+0.19%->+0.11%; net30 +0.08%->+0.17%->+0.09%; positive families 3/4->4/4->3/4; PASS
- KOSDAQ_PLUS_KOSPI_EX_K200 H20 Top10: gross +0.11%->+0.65%->-0.33%; net30 +0.09%->+0.62%->-0.37%; positive families 3/4->3/4->1/4; FAIL
- KOSDAQ_PLUS_KOSPI_EX_K200 H20 Top20: gross -0.00%->+0.41%->+0.37%; net30 -0.01%->+0.39%->+0.35%; positive families 2/4->4/4->3/4; FAIL
- KOSPI_ALL H5 Top10: gross +0.15%->+0.08%->+0.14%; net30 +0.13%->+0.06%->+0.11%; positive families 4/4->3/4->2/4; PASS
- KOSPI_ALL H5 Top20: gross +0.05%->+0.06%->+0.06%; net30 +0.04%->+0.04%->+0.04%; positive families 2/4->3/4->4/4; PASS
- KOSPI_ALL H10 Top10: gross +0.15%->+0.17%->+0.38%; net30 +0.13%->+0.15%->+0.36%; positive families 4/4->4/4->3/4; PASS
- KOSPI_ALL H10 Top20: gross +0.03%->+0.07%->+0.06%; net30 +0.03%->+0.06%->+0.04%; positive families 2/4->4/4->3/4; PASS
- KOSPI_ALL H20 Top10: gross +0.18%->+0.57%->+0.06%; net30 +0.16%->+0.54%->+0.03%; positive families 4/4->3/4->2/4; PASS
- KOSPI_ALL H20 Top20: gross +0.00%->+0.26%->+0.02%; net30 -0.01%->+0.24%->+0.00%; positive families 1/4->4/4->2/4; FAIL
- KOSPI_EX_K200 H5 Top10: gross +0.09%->-0.05%->+0.10%; net30 +0.09%->-0.06%->+0.09%; positive families 3/4->2/4->4/4; FAIL
- KOSPI_EX_K200 H5 Top20: gross +0.03%->+0.01%->+0.03%; net30 +0.02%->+0.01%->+0.02%; positive families 3/4->3/4->3/4; PASS
- KOSPI_EX_K200 H10 Top10: gross +0.05%->-0.09%->+0.18%; net30 +0.04%->-0.11%->+0.16%; positive families 3/4->2/4->4/4; FAIL
- KOSPI_EX_K200 H10 Top20: gross +0.04%->+0.00%->+0.10%; net30 +0.04%->-0.00%->+0.09%; positive families 4/4->2/4->4/4; FAIL
- KOSPI_EX_K200 H20 Top10: gross -0.00%->-0.05%->+0.31%; net30 -0.01%->-0.06%->+0.29%; positive families 2/4->3/4->3/4; FAIL
- KOSPI_EX_K200 H20 Top20: gross +0.10%->+0.02%->+0.19%; net30 +0.10%->+0.01%->+0.18%; positive families 4/4->2/4->3/4; PASS
- KOSPI_KOSDAQ_ALL H5 Top10: gross +0.18%->+0.07%->-0.01%; net30 +0.16%->+0.04%->-0.04%; positive families 3/4->4/4->2/4; FAIL
- KOSPI_KOSDAQ_ALL H5 Top20: gross +0.13%->+0.12%->+0.10%; net30 +0.11%->+0.10%->+0.08%; positive families 3/4->4/4->3/4; PASS
- KOSPI_KOSDAQ_ALL H10 Top10: gross +0.09%->+0.13%->-0.13%; net30 +0.06%->+0.09%->-0.17%; positive families 3/4->4/4->1/4; FAIL
- KOSPI_KOSDAQ_ALL H10 Top20: gross +0.15%->+0.19%->+0.08%; net30 +0.13%->+0.17%->+0.06%; positive families 3/4->4/4->3/4; PASS
- KOSPI_KOSDAQ_ALL H20 Top10: gross +0.00%->+0.75%->+0.01%; net30 -0.03%->+0.70%->-0.04%; positive families 2/4->3/4->3/4; FAIL
- KOSPI_KOSDAQ_ALL H20 Top20: gross +0.01%->+0.56%->+0.19%; net30 -0.00%->+0.53%->+0.15%; positive families 2/4->4/4->3/4; FAIL

## 2023-24 block-bootstrap for passing specifications

- K200 H5 Top20 gross_delta: +0.05%; CI [-0.01%,+0.10%], P>0 96%, n=97
- K200 H5 Top20 net_30: +0.04%; CI [-0.01%,+0.09%], P>0 94%, n=97
- K200 H5 Top20 net_60: +0.04%; CI [-0.01%,+0.09%], P>0 92%, n=97
- KOSDAQ H5 Top20 gross_delta: +0.02%; CI [-0.09%,+0.13%], P>0 68%, n=97
- KOSDAQ H5 Top20 net_30: +0.01%; CI [-0.09%,+0.12%], P>0 61%, n=97
- KOSDAQ H5 Top20 net_60: +0.01%; CI [-0.10%,+0.11%], P>0 55%, n=97
- KOSDAQ H10 Top20 gross_delta: +0.05%; CI [-0.16%,+0.25%], P>0 67%, n=48
- KOSDAQ H10 Top20 net_30: +0.04%; CI [-0.17%,+0.24%], P>0 64%, n=48
- KOSDAQ H10 Top20 net_60: +0.03%; CI [-0.17%,+0.22%], P>0 59%, n=48
- KOSDAQ_PLUS_KOSPI_EX_K200 H5 Top20 gross_delta: +0.09%; CI [-0.06%,+0.23%], P>0 88%, n=97
- KOSDAQ_PLUS_KOSPI_EX_K200 H5 Top20 net_30: +0.07%; CI [-0.07%,+0.22%], P>0 84%, n=97
- KOSDAQ_PLUS_KOSPI_EX_K200 H5 Top20 net_60: +0.06%; CI [-0.09%,+0.20%], P>0 80%, n=97
- KOSDAQ_PLUS_KOSPI_EX_K200 H10 Top20 gross_delta: +0.11%; CI [-0.18%,+0.38%], P>0 78%, n=48
- KOSDAQ_PLUS_KOSPI_EX_K200 H10 Top20 net_30: +0.09%; CI [-0.19%,+0.37%], P>0 75%, n=48
- KOSDAQ_PLUS_KOSPI_EX_K200 H10 Top20 net_60: +0.07%; CI [-0.21%,+0.35%], P>0 71%, n=48
- KOSPI_ALL H5 Top10 gross_delta: +0.14%; CI [-0.10%,+0.38%], P>0 86%, n=97
- KOSPI_ALL H5 Top10 net_30: +0.11%; CI [-0.13%,+0.36%], P>0 83%, n=97
- KOSPI_ALL H5 Top10 net_60: +0.09%; CI [-0.15%,+0.34%], P>0 77%, n=97
- KOSPI_ALL H5 Top20 gross_delta: +0.06%; CI [-0.08%,+0.19%], P>0 80%, n=97
- KOSPI_ALL H5 Top20 net_30: +0.04%; CI [-0.08%,+0.17%], P>0 75%, n=97
- KOSPI_ALL H5 Top20 net_60: +0.03%; CI [-0.10%,+0.16%], P>0 70%, n=97
- KOSPI_ALL H10 Top10 gross_delta: +0.38%; CI [-0.01%,+0.77%], P>0 97%, n=48
- KOSPI_ALL H10 Top10 net_30: +0.36%; CI [-0.02%,+0.74%], P>0 97%, n=48
- KOSPI_ALL H10 Top10 net_60: +0.33%; CI [-0.05%,+0.71%], P>0 96%, n=48
- KOSPI_ALL H10 Top20 gross_delta: +0.06%; CI [-0.23%,+0.33%], P>0 65%, n=48
- KOSPI_ALL H10 Top20 net_30: +0.04%; CI [-0.25%,+0.30%], P>0 60%, n=48
- KOSPI_ALL H10 Top20 net_60: +0.02%; CI [-0.25%,+0.30%], P>0 57%, n=48
- KOSPI_ALL H20 Top10 gross_delta: +0.06%; CI [-0.42%,+0.64%], P>0 58%, n=24
- KOSPI_ALL H20 Top10 net_30: +0.03%; CI [-0.45%,+0.60%], P>0 52%, n=24
- KOSPI_ALL H20 Top10 net_60: -0.00%; CI [-0.48%,+0.55%], P>0 48%, n=24
- KOSPI_EX_K200 H5 Top20 gross_delta: +0.03%; CI [-0.06%,+0.11%], P>0 73%, n=97
- KOSPI_EX_K200 H5 Top20 net_30: +0.02%; CI [-0.06%,+0.10%], P>0 69%, n=97
- KOSPI_EX_K200 H5 Top20 net_60: +0.01%; CI [-0.07%,+0.10%], P>0 63%, n=97
- KOSPI_EX_K200 H20 Top20 gross_delta: +0.19%; CI [-0.07%,+0.46%], P>0 92%, n=24
- KOSPI_EX_K200 H20 Top20 net_30: +0.18%; CI [-0.07%,+0.46%], P>0 91%, n=24
- KOSPI_EX_K200 H20 Top20 net_60: +0.18%; CI [-0.09%,+0.46%], P>0 90%, n=24
- KOSPI_KOSDAQ_ALL H5 Top20 gross_delta: +0.10%; CI [-0.08%,+0.26%], P>0 88%, n=97
- KOSPI_KOSDAQ_ALL H5 Top20 net_30: +0.08%; CI [-0.08%,+0.25%], P>0 83%, n=97
- KOSPI_KOSDAQ_ALL H5 Top20 net_60: +0.06%; CI [-0.11%,+0.22%], P>0 77%, n=97
- KOSPI_KOSDAQ_ALL H10 Top20 gross_delta: +0.08%; CI [-0.27%,+0.40%], P>0 68%, n=48
- KOSPI_KOSDAQ_ALL H10 Top20 net_30: +0.06%; CI [-0.27%,+0.36%], P>0 62%, n=48
- KOSPI_KOSDAQ_ALL H10 Top20 net_60: +0.03%; CI [-0.31%,+0.35%], P>0 58%, n=48

## Stress behavior of passing 10D Top20 reference spec

- KOSDAQ: 2025 net30 +0.03% gross +0.04%; 2026 net30 +0.53% gross +0.54%
- KOSDAQ_PLUS_KOSPI_EX_K200: 2025 net30 +0.43% gross +0.44%; 2026 net30 +0.47% gross +0.49%
- KOSPI_ALL: 2025 net30 +0.26% gross +0.27%; 2026 net30 +0.18% gross +0.19%
- KOSPI_KOSDAQ_ALL: 2025 net30 +0.44% gross +0.46%; 2026 net30 +1.10% gross +1.13%

## Decision rule

- Promote the concept, not a precise parameter, only if the same frozen W20 rule remains positive across multiple TopN/horizon settings and the edge survives 30/60 bp costs.
- Top20/H10 remains the reference specification because it predates this confirmatory grid; superior grid cells are robustness evidence, not newly optimized choices.
- 2025/2026 are stress diagnostics only.

