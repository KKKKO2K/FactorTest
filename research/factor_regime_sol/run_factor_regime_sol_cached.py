from __future__ import annotations

from functools import lru_cache

import run_factor_regime_sol as r

# Each formation date loads the same six factor snapshots once and reuses them
# across all universes. Small cache is enough because dates are processed serially.
r.load_factor = lru_cache(maxsize=16)(r.load_factor)

if __name__ == "__main__":
    r.main()
