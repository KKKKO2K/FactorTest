from __future__ import annotations

import run_weighted_momentum_filter_exact as exact

# Primary hypothesis only: retain names with R1M >= 0 versus the unchanged weighted-momentum baseline.
# Neighboring thresholds are deferred to robustness after the primary result is established.
exact.m.THRESHOLDS_PCT = (0.0,)

if __name__ == "__main__":
    exact.main()
