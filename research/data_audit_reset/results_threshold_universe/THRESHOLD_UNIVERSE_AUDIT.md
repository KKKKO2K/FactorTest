# PIT Market-Cap Cutoff Audit

User-specified intended universe: KOSPI/KOSDAQ stocks with PIT market cap >= 200 KRW bn.

- Sampled dates: 521 (every 5 basic-info dates + endpoint)
- Median factor rows: 664
- Median PIT cutoff-eligible rows: 792
- Median Jaccard: 0.8356
- Median factor precision vs cutoff: 99.73%
- Median cutoff recall in factor rows: 83.76%
- Median factor-only mismatch: 2
- Median cutoff-eligible missing factor: 124

Interpretation: a near-1.0 match validates the factor row universe as a point-in-time market-cap-threshold universe, not a top-N/current-survivor universe. Remaining mismatches should be understood from security-type or boundary timing rules before being treated as data defects.