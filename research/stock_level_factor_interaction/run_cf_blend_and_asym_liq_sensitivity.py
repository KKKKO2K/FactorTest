from __future__ import annotations

from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/liquidity_cross_factor'))
sys.path.insert(0, str(ROOT / 'research/stock_level_factor_interaction'))
import run_cross_factor_liquidity as base
import run_multi_universe_liquidity as multi
import run_cf20_decomposition_liquidity_ranges as core

OUT = Path(__file__).resolve().parent / 'results_cf_blend_asym_liq_sensitivity'
OUT.mkdir(parents=True, exist_ok=True)

UNIVERSES = core.UNIVERSES
FAMILIES = core.FAMILIES
FACTOR_FAMILY = core.FACTOR_FAMILY
CORE = core.CORE
TOPN = 20
COSTS = (0, 30, 60)
BLEND_WEIGHTS_H10 = (0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50)
BLEND_WEIGHTS_ROBUST = (0.00, 0.10, 0.20, 0.30)
HORIZONS = (5, 10, 20)
LOW_CUTS = (0.05, 0.10, 0.20, 0.30)
RNG = np.random.default_rng(20260815)


def block_boot(x, block=4, nboot=6000):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 8:
        return np.array([])
    nb = int(np.ceil(n / block))
    starts = RNG.integers(0, n, size=(nboot, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    return x[idx.reshape(nboot, -1)[:, :n]].mean(axis=1)


def top_names(score: pd.Series, n=TOPN):
    return core.top_names(score, n)


def weights_for_horizon(h: int):
    return BLEND_WEIGHTS_H10 if h == 10 else BLEND_WEIGHTS_ROBUST


def liq_score_map(cf20: pd.Series, ar: pd.Series):
    out = {'CF20': cf20, 'VETO_TOP1_ONLY': cf20.where(ar <= 0.99)}
    for cut in LOW_CUTS:
        tag = int(round(cut * 100))
        out[f'VETO_LOW{tag:02d}'] = cf20.where(ar >= cut)
        out[f'VETO_TOP1_LOW{tag:02d}'] = cf20.where((ar >= cut) & (ar <= 0.99))
    return out


def load_inputs():
    returns, mcap, k200 = base.load_basic()
    markets = multi.load_market_by_date()
    ta = base.load_trading_amount()
    liq = base.build_liquidity_features(ta, mcap)
    files = {f: base.dated_files(path) for f, path in base.FACTORS.items()}
    return returns, k200, markets, ta, liq, files


def build_factor_paths(returns, k200, markets, ta, liq, files):
    blend_rows = []
    liq_rows = []

    for h in HORIZONS:
        fwd = base.forward_returns(returns, h)
        common = sorted(set(returns.index) & set(ta.index) & set(k200) & set(markets))
        dates = [d for d in common if d >= base.START and d in fwd.index][::h]
        blend_holdings = {}
        liq_holdings = {}
        weights = weights_for_horizon(h)

        for dt in dates:
            k = k200[dt]
            market = markets[dt]
            act5_full = liq['act5'].loc[dt] if dt in liq['act5'].index else pd.Series(dtype=float)

            for u in UNIVERSES:
                codes = multi.universe_codes(u, k, market)
                y = fwd.loc[dt].reindex(codes)
                if y.notna().sum() < (70 if u == 'K200' else 120):
                    continue
                scores, others = core.build_scores(dt, codes, files)
                if len(scores) < 8:
                    continue
                ar = pd.to_numeric(act5_full.reindex(codes), errors='coerce').rank(pct=True, method='average')

                for f, primary in scores.items():
                    other = others[f]
                    family = FACTOR_FAMILY[f]

                    for w in weights:
                        score = (1.0 - w) * primary + w * other
                        names = top_names(score)
                        if len(names) < TOPN:
                            continue
                        key = (h, u, f, w)
                        old = blend_holdings.get(key, [])
                        turn = 1.0 - len(set(old) & set(names)) / TOPN if old else 1.0
                        blend_rows.append({
                            'date': dt, 'sample': core.sample_of(dt), 'horizon': h,
                            'universe': u, 'factor': f, 'family': family, 'weight': w,
                            'gross': float(y.reindex(names).mean()), 'turnover': turn,
                        })
                        blend_holdings[key] = names

                    cf20 = 0.8 * primary + 0.2 * other
                    for strat, score in liq_score_map(cf20, ar).items():
                        names = top_names(score)
                        if len(names) < TOPN:
                            continue
                        key = (h, u, f, strat)
                        old = liq_holdings.get(key, [])
                        turn = 1.0 - len(set(old) & set(names)) / TOPN if old else 1.0
                        liq_rows.append({
                            'date': dt, 'sample': core.sample_of(dt), 'horizon': h,
                            'universe': u, 'factor': f, 'family': family, 'strategy': strat,
                            'gross': float(y.reindex(names).mean()), 'turnover': turn,
                        })
                        liq_holdings[key] = names

    return pd.DataFrame(blend_rows), pd.DataFrame(liq_rows)


def aggregate_daily(df: pd.DataFrame, id_col: str):
    cols = ['date', 'sample', 'horizon', 'universe', id_col]
    return df.groupby(cols, as_index=False).agg(gross=('gross', 'mean'), turnover=('turnover', 'mean'))


def matched_daily(daily: pd.DataFrame, id_col: str, baseline_value):
    b = daily[daily[id_col].eq(baseline_value)][
        ['date', 'sample', 'horizon', 'universe', 'gross', 'turnover']
    ].rename(columns={'gross': 'base_gross', 'turnover': 'base_turnover'})
    x = daily[~daily[id_col].eq(baseline_value)].merge(
        b, on=['date', 'sample', 'horizon', 'universe'], how='inner'
    )
    x['gross_delta'] = x.gross - x.base_gross
    x['turnover_delta'] = x.turnover - x.base_turnover
    for c in COSTS:
        x[f'net_delta_{c}'] = x.gross_delta - x.turnover_delta * c / 10000
    return x


def summarize_matched(x: pd.DataFrame, id_col: str):
    stats = []
    boots = []
    for key, g in x.groupby([id_col, 'universe', 'horizon', 'sample']):
        rec = dict(zip([id_col, 'universe', 'horizon', 'sample'], key))
        rec |= {
            'n_dates': len(g),
            'gross_delta': g.gross_delta.mean(),
            'turnover_delta': g.turnover_delta.mean(),
        }
        for c in COSTS:
            rec[f'net_delta_{c}'] = g[f'net_delta_{c}'].mean()
        stats.append(rec)
        for metric in ('gross_delta', 'net_delta_30', 'net_delta_60'):
            bs = block_boot(g.sort_values('date')[metric].to_numpy())
            if len(bs):
                boots.append(rec | {
                    'metric': metric, 'mean': g[metric].mean(),
                    'ci025': np.quantile(bs, 0.025), 'ci975': np.quantile(bs, 0.975),
                    'p_gt0': float((bs > 0).mean()),
                })
    return pd.DataFrame(stats), pd.DataFrame(boots)


def family_summary(raw: pd.DataFrame, id_col: str, baseline_value):
    b = raw[raw[id_col].eq(baseline_value)][
        ['date', 'sample', 'horizon', 'universe', 'factor', 'family', 'gross']
    ].rename(columns={'gross': 'base_gross'})
    x = raw[~raw[id_col].eq(baseline_value)].merge(
        b, on=['date', 'sample', 'horizon', 'universe', 'factor', 'family'], how='inner'
    )
    x['gross_delta'] = x.gross - x.base_gross
    return x.groupby([id_col, 'universe', 'horizon', 'sample', 'family'], as_index=False).agg(
        n_dates=('date', 'nunique'), gross_delta=('gross_delta', 'mean')
    )


def blend_plateau(stats: pd.DataFrame):
    z = stats[(stats.horizon == 10) & (stats['sample'].isin(CORE))].copy()
    out = []
    for w, g in z.groupby('weight'):
        by_u = g.groupby('universe').agg(
            positive_blocks=('net_delta_30', lambda s: int((s > 0).sum())),
            median_edge=('net_delta_30', 'median'),
            mean_edge=('net_delta_30', 'mean'),
        ).reset_index()
        out.append({
            'weight': w,
            'positive_cells': int((g.net_delta_30 > 0).sum()),
            'total_cells': len(g),
            'universes_all3_positive': int((by_u.positive_blocks == 3).sum()),
            'median_cell_net30': g.net_delta_30.median(),
            'mean_cell_net30': g.net_delta_30.mean(),
        })
    return pd.DataFrame(out).sort_values('weight')


def best_weight_diagnostic(stats: pd.DataFrame):
    # Diagnostic only: never use these in-sample winners as production choices.
    z = stats[(stats.horizon == 10) & (stats['sample'].isin(CORE))]
    rows = []
    for (u, s), g in z.groupby(['universe', 'sample']):
        q = g.sort_values('net_delta_30', ascending=False).iloc[0]
        rows.append({'universe': u, 'sample': s, 'best_weight_diag': q.weight, 'best_net30_diag': q.net_delta_30})
    return pd.DataFrame(rows)


def combo_vs_components(liq_stats: pd.DataFrame):
    rows = []
    keys = ['universe', 'horizon', 'sample']
    mp = {(r.strategy, r.universe, r.horizon, r['sample']): r for _, r in liq_stats.iterrows()}
    for cut in LOW_CUTS:
        tag = int(round(cut * 100))
        combo = f'VETO_TOP1_LOW{tag:02d}'
        low = f'VETO_LOW{tag:02d}'
        for u in UNIVERSES:
            for h in HORIZONS:
                for s in (*CORE, 'BULL_2025', 'YTD_2026'):
                    rc = mp.get((combo, u, h, s)); rt = mp.get(('VETO_TOP1_ONLY', u, h, s)); rl = mp.get((low, u, h, s))
                    if rc is None or rt is None or rl is None:
                        continue
                    rows.append({
                        'low_cut': cut, 'universe': u, 'horizon': h, 'sample': s,
                        'combo_net30': rc.net_delta_30,
                        'top1_only_net30': rt.net_delta_30,
                        'low_only_net30': rl.net_delta_30,
                        'combo_minus_best_component': rc.net_delta_30 - max(rt.net_delta_30, rl.net_delta_30),
                    })
    return pd.DataFrame(rows)


def report(blend_stats, plateau, best_diag, liq_stats, combo):
    L = [
        '# Cross-Family Blend Weight + Asymmetric ACT5 Veto Sensitivity', '',
        'No outcome-based fine tuning is used. Blend weights and ACT5 lower cutoffs are a coarse predeclared sensitivity grid. Primary reference remains Top20; H10 is the main blend-weight horizon.', '',
        '## 1) H10 Top20 blend-weight plateau vs primary-only baseline — 30bp net', '',
    ]
    for _, r in plateau.iterrows():
        L.append(f"- w={r.weight:.0%}: positive core cells {int(r.positive_cells)}/{int(r.total_cells)}, universes with all 3 core blocks positive {int(r.universes_all3_positive)}/6, median cell edge {r.median_cell_net30:+.2%}, mean {r.mean_cell_net30:+.2%}")
    L += ['', '### Universe-level core-block edges by weight (H10, 30bp net)', '']
    for u in UNIVERSES:
        L.append(f'#### {u}')
        z = blend_stats[(blend_stats.universe == u) & (blend_stats.horizon == 10) & (blend_stats["sample"].isin(CORE))]
        for w in BLEND_WEIGHTS_H10[1:]:
            q = z[z.weight.eq(w)]
            mp = {r['sample']: r.net_delta_30 for _, r in q.iterrows()}
            if all(s in mp for s in CORE):
                L.append(f"- w={w:.0%}: {mp[CORE[0]]:+.2%} -> {mp[CORE[1]]:+.2%} -> {mp[CORE[2]]:+.2%}")
    L += ['', '### Best-weight diagnostic only (not a selection rule)', '']
    for _, r in best_diag.iterrows():
        L.append(f"- {r.universe} {r['sample']}: best grid weight {r.best_weight_diag:.0%}, edge {r.best_net30_diag:+.2%}")

    L += ['', '## 2) Asymmetric ACT5 veto: top 1% + bottom n% removed from frozen CF20', '',
          'PASS means positive H10 30bp-net incremental edge vs CF20 in all three core blocks.', '']
    for cut in LOW_CUTS:
        tag = int(round(cut * 100))
        strat = f'VETO_TOP1_LOW{tag:02d}'
        L.append(f'### Top1% + Low{tag}% veto')
        for u in UNIVERSES:
            z = liq_stats[(liq_stats.strategy == strat) & (liq_stats.universe == u) & (liq_stats.horizon == 10)]
            mp = {r['sample']: r.net_delta_30 for _, r in z.iterrows()}
            if all(s in mp for s in CORE):
                ok = all(mp[s] > 0 for s in CORE)
                L.append(f"- {u}: {mp[CORE[0]]:+.2%} -> {mp[CORE[1]]:+.2%} -> {mp[CORE[2]]:+.2%}; {'PASS' if ok else 'FAIL'}")

    L += ['', '### Does the combination beat either tail veto alone? H10, 30bp net', '']
    for cut in LOW_CUTS:
        z = combo[(combo.low_cut == cut) & (combo.horizon == 10) & (combo['sample'].isin(CORE))]
        tag = int(round(cut * 100))
        if z.empty:
            continue
        L.append(f"- Low{tag}%: combo-minus-best-component median {z.combo_minus_best_component.median():+.2%}; positive cells {(z.combo_minus_best_component > 0).sum()}/{len(z)}")

    L += ['', '## Guardrails', '',
          '- Do not call the highest single grid weight optimal. The decision criterion is a broad plateau with cross-period/universe stability.',
          '- H5/H20 results and 2025/2026 are robustness/stress evidence; H10 Top20 is the primary blend sensitivity.',
          '- The asymmetric liquidity test is incremental to frozen CF20. Top1% and bottom-n cutoffs are cross-sectional ACT5 percentiles observed at each decision date.',
          '- Any later production rule should be chosen from a stable range, then frozen before full portfolio implementation.', '']
    return '\n'.join(L) + '\n'


def main():
    returns, k200, markets, ta, liq, files = load_inputs()
    blend_raw, liq_raw = build_factor_paths(returns, k200, markets, ta, liq, files)

    blend_daily = aggregate_daily(blend_raw, 'weight')
    liq_daily = aggregate_daily(liq_raw, 'strategy')
    blend_match = matched_daily(blend_daily, 'weight', 0.0)
    liq_match = matched_daily(liq_daily, 'strategy', 'CF20')

    blend_stats, blend_boot = summarize_matched(blend_match, 'weight')
    liq_stats, liq_boot = summarize_matched(liq_match, 'strategy')
    blend_fam = family_summary(blend_raw, 'weight', 0.0)
    liq_fam = family_summary(liq_raw, 'strategy', 'CF20')
    plateau = blend_plateau(blend_stats)
    best_diag = best_weight_diagnostic(blend_stats)
    combo = combo_vs_components(liq_stats)

    blend_daily.to_csv(OUT / 'blend_daily.csv', index=False)
    liq_daily.to_csv(OUT / 'asym_liq_daily.csv', index=False)
    blend_stats.to_csv(OUT / 'blend_summary.csv', index=False)
    blend_boot.to_csv(OUT / 'blend_bootstrap.csv', index=False)
    blend_fam.to_csv(OUT / 'blend_family.csv', index=False)
    plateau.to_csv(OUT / 'blend_plateau.csv', index=False)
    best_diag.to_csv(OUT / 'blend_best_weight_diagnostic.csv', index=False)
    liq_stats.to_csv(OUT / 'asym_liq_summary.csv', index=False)
    liq_boot.to_csv(OUT / 'asym_liq_bootstrap.csv', index=False)
    liq_fam.to_csv(OUT / 'asym_liq_family.csv', index=False)
    combo.to_csv(OUT / 'asym_combo_vs_components.csv', index=False)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(
        report(blend_stats, plateau, best_diag, liq_stats, combo), encoding='utf-8'
    )
    print(f'blend_factor_rows={len(blend_raw):,}; liq_factor_rows={len(liq_raw):,}; blend_specs={len(blend_stats):,}; liq_specs={len(liq_stats):,}')


if __name__ == '__main__':
    main()
