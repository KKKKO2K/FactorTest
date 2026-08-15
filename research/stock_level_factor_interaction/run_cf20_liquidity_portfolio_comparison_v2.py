from pathlib import Path

import run_cf20_liquidity_portfolio_comparison as m

m.OUT = Path(__file__).resolve().parent / 'results_cf20_liquidity_portfolio_comparison_v2'
m.OUT.mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    m.main()
