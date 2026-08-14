from functools import lru_cache

import run_w20_mechanism_liquidity as research

# Pure execution optimization only: the same point-in-time factor file is reused
# across six universes. Cache a few recent dates; calculations and definitions
# remain identical to run_w20_mechanism_liquidity.py.
research.base.load_factor = lru_cache(maxsize=96)(research.base.load_factor)

if __name__ == '__main__':
    research.main()
