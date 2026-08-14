from __future__ import annotations

from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/liquidity_cross_factor'))
import run_cross_factor_liquidity as base
import run_multi_universe_liquidity as multi

OUT = Path(__file__).resolve().parent / 'results_mechanism_liquidity'
OUT.mkdir(parents=True, exist_ok=True)

FAMILIES = {
    'MOMENTUM': ['MOM1M', 'MOM12_1'],
    'REVISION': ['OP12_REV', 'OPFY1_REV'],
    'VALUE': ['PBR12MF', 'PER12MF'],
    'FLOW': ['PRIVATE_FLOW', 'FOREIGN_FLOW'],
}
FACTOR_FAMILY = {f: fam for fam, members in FAMILIES.items() for f in members}
HIGH_GOOD = {
    'MOM1M': True, 'MOM12_1': True,
    'OP12_REV': True, 'OPFY1_REV': True,
    'PBR12MF': False, 'PER12MF': False,
    'PRIVATE_FLOW': True, 'FOREIGN_FLOW': True,
}
UNIVERSES = (
    'K200', 'KOSPI_EX_K200', 'KOSPI_ALL', 'KOSDAQ',
    'KOSPI_KOSDAQ_ALL', 'KOSDAQ_PLUS_KOSPI_EX_K200',
)
CORE = ('EARLY_2016_2019', 'LATE_2020_2022', 'NORMAL_2023_2024')
MECH_H = 10
MECH_TOPN = 20
LIQ_HORIZONS = (5, 10)
LIQ_TOPN = 20
COSTS = (0, 30, 60)
RNG = np.random.default_rng(20260814)


def sample_of(dt: pd.Timestamp) -> str:
    y = dt.year
    if y <= 2019:
        return 'EARLY_2016_2019'
    if y <= 2022:
        return 'LATE_2020_2022'
    if y <= 2024:
        return 'NORMAL_2023_2024'
    if y == 2025:
        return 'BULL_2025'
    return 'YTD_2026'


def rank_good(raw: pd.Series, high_good: bool) -> pd.Series:
    # 1.0 = best.
    return pd.to_numeric(raw, errors='coerce').rank(
        pct=True, method='average', ascending=True if high_good else False
    )


def block_boot(x, block=4, nboot=4000):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 8:
        return np.array([])
    nb = int(np.ceil(n / block))
    starts = RNG.integers(0, n, size=(nboot, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    return x[idx.reshape(nboot, -1)[:, :n]].mean(axis=1)


def load_inputs():
    returns, mcap, k200 = base.load_basic()
    markets = multi.load_market_by_date()
    ta = base.load_trading_amount()
    liq = base.build_liquidity_features(ta, mcap)
    files = {f: base.dated_files(path) for f, path in base.FACTORS.items()}
    return returns, mcap, k200, markets, ta, liq, files


def build_factor_scores(dt, codes, files):
    raws = {f: base.load_factor(fs[dt]) for f, fs in files.items() if dt in fs}
    if len(raws) < 8:
        return {}, {}, {}
    scores = {f: rank_good(raws[f].reindex(codes), HIGH_GOOD[f]) for f in raws}
    fam = {
        name: pd.concat([scores[x] for x in members], axis=1).mean(axis=1)
        for name, members in FAMILIES.items()
    }
    others = {}
    for f in scores:
        ff = FACTOR_FAMILY[f]
        others[f] = pd.concat([v for name, v in fam.items() if name != ff], axis=1).mean(axis=1)
    return scores, fam, others


def top_names(s: pd.Series, n: int):
    x = s.replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)
    return x.head(n).index.tolist() if len(x) >= n else []


def run_mechanism(returns, k200, markets, files):
    fwd = base.forward_returns(returns, MECH_H)
    common = sorted(set(returns.index) & set(k200) & set(markets))
    dates = [d for d in common if d >= base.START and d in fwd.index][::MECH_H]
    event_rows = []
    cand_rows = []

    for dt in dates:
        k = k200[dt]
        market = markets[dt]
        for u in UNIVERSES:
            codes = multi.universe_codes(u, k, market)
            y = fwd.loc[dt].reindex(codes)
            minobs = 70 if u == 'K200' else 120
            if y.notna().sum() < minobs:
                continue
            scores, fam, others = build_factor_scores(dt, codes, files)
            if len(scores) < 8:
                continue
            for f, primary in scores.items():
                other = others[f]
                cf = 0.8 * primary + 0.2 * other
                b = top_names(primary, MECH_TOPN)
                c = top_names(cf, MECH_TOPN)
                if len(b) < MECH_TOPN or len(c) < MECH_TOPN:
                    continue
                bs, cs = set(b), set(c)
                kept = sorted(bs & cs)
                dropped = sorted(bs - cs)
                added = sorted(cs - bs)
                if len(dropped) != len(added):
                    continue

                p_rank = primary.rank(method='average', ascending=False)
                base_ret = float(y.reindex(b).mean())
                cf_ret = float(y.reindex(c).mean())
                def mean_idx(s, idx):
                    return float(s.reindex(idx).mean()) if idx else np.nan
                added_ret = mean_idx(y, added)
                dropped_ret = mean_idx(y, dropped)
                kept_ret = mean_idx(y, kept)
                repl_edge = added_ret - dropped_ret if added else 0.0
                replace_share = len(added) / MECH_TOPN

                event_rows.append({
                    'date': dt, 'sample': sample_of(dt), 'universe': u, 'factor': f,
                    'family': FACTOR_FAMILY[f], 'n_replace': len(added),
                    'replace_share': replace_share, 'base_return': base_ret,
                    'cf20_return': cf_ret, 'portfolio_delta': cf_ret - base_ret,
                    'added_return': added_ret, 'dropped_return': dropped_ret,
                    'kept_return': kept_ret, 'replacement_edge': repl_edge,
                    'identity_delta': replace_share * repl_edge,
                    'added_primary_score': mean_idx(primary, added),
                    'dropped_primary_score': mean_idx(primary, dropped),
                    'added_other_score': mean_idx(other, added),
                    'dropped_other_score': mean_idx(other, dropped),
                    'kept_other_score': mean_idx(other, kept),
                    'added_primary_rank': mean_idx(p_rank, added),
                    'dropped_primary_rank': mean_idx(p_rank, dropped),
                })

                # Candidate-pool anatomy: primary top 40 only; cross-family consensus is not used to define pool.
                pool = primary.dropna().sort_values(ascending=False).head(40).index
                for code in pool:
                    os = other.get(code, np.nan)
                    if not np.isfinite(os):
                        continue
                    decile = int(min(10, max(1, np.ceil(os * 10))))
                    pr = float(p_rank.get(code, np.nan))
                    cand_rows.append({
                        'date': dt, 'sample': sample_of(dt), 'universe': u, 'factor': f,
                        'family': FACTOR_FAMILY[f], 'code': code,
                        'primary_rank': pr,
                        'primary_bucket': 'TOP20' if pr <= 20 else 'RANK21_40',
                        'other_score': float(os), 'other_decile': decile,
                        'fwd10': float(y.get(code, np.nan)),
                        'base_selected': code in bs, 'cf20_selected': code in cs,
                    })

    events = pd.DataFrame(event_rows)
    cands = pd.DataFrame(cand_rows)
    events.to_csv(OUT / 'mechanism_events.csv', index=False)
    cands.to_csv(OUT / 'mechanism_candidate_pool.csv', index=False)
    return events, cands


def summarize_mechanism(events, cands):
    rows = []
    fam_rows = []
    boot_rows = []
    for key, g in events.groupby(['universe', 'sample']):
        d = g.groupby('date').agg(
            portfolio_delta=('portfolio_delta', 'mean'),
            replacement_edge=('replacement_edge', 'mean'),
            replace_share=('replace_share', 'mean'),
            added_return=('added_return', 'mean'),
            dropped_return=('dropped_return', 'mean'),
            kept_return=('kept_return', 'mean'),
            added_primary_rank=('added_primary_rank', 'mean'),
            dropped_primary_rank=('dropped_primary_rank', 'mean'),
            added_other_score=('added_other_score', 'mean'),
            dropped_other_score=('dropped_other_score', 'mean'),
        ).reset_index().sort_values('date')
        rows.append({
            'universe': key[0], 'sample': key[1], 'n_dates': len(d),
            **{c: float(d[c].mean()) for c in d.columns if c != 'date'}
        })
        for metric in ('portfolio_delta', 'replacement_edge'):
            bs = block_boot(d[metric].to_numpy())
            if len(bs):
                boot_rows.append({
                    'universe': key[0], 'sample': key[1], 'metric': metric,
                    'mean': float(d[metric].mean()), 'ci025': float(np.quantile(bs, .025)),
                    'ci975': float(np.quantile(bs, .975)), 'p_gt0': float((bs > 0).mean()),
                    'n_dates': len(d),
                })

    for key, g in events.groupby(['universe', 'sample', 'family']):
        d = g.groupby('date').agg(
            portfolio_delta=('portfolio_delta', 'mean'),
            replacement_edge=('replacement_edge', 'mean'),
            replace_share=('replace_share', 'mean'),
        )
        fam_rows.append({
            'universe': key[0], 'sample': key[1], 'family': key[2], 'n_dates': len(d),
            'portfolio_delta': float(d.portfolio_delta.mean()),
            'replacement_edge': float(d.replacement_edge.mean()),
            'replace_share': float(d.replace_share.mean()),
            'positive_date_rate': float((d.portfolio_delta > 0).mean()),
        })

    # Within the pre-defined primary top-40 candidate pool, ask whether other-family consensus sorts returns.
    dec_rows = []
    for key, g in cands.groupby(['universe', 'sample', 'other_decile']):
        d = g.groupby('date').agg(fwd10=('fwd10', 'mean'), cf_select=('cf20_selected', 'mean'))
        dec_rows.append({
            'universe': key[0], 'sample': key[1], 'other_decile': key[2], 'n_dates': len(d),
            'fwd10': float(d.fwd10.mean()), 'cf20_select_rate': float(d.cf_select.mean()),
        })

    summary = pd.DataFrame(rows)
    family = pd.DataFrame(fam_rows)
    boots = pd.DataFrame(boot_rows)
    dec = pd.DataFrame(dec_rows)
    summary.to_csv(OUT / 'mechanism_summary.csv', index=False)
    family.to_csv(OUT / 'mechanism_family_summary.csv', index=False)
    boots.to_csv(OUT / 'mechanism_bootstrap.csv', index=False)
    dec.to_csv(OUT / 'mechanism_consensus_deciles.csv', index=False)
    return summary, family, boots, dec


def run_liquidity(returns, mcap, k200, markets, ta, liq_frames, files):
    all_rows = []
    for h in LIQ_HORIZONS:
        fwd = base.forward_returns(returns, h)
        common = sorted(set(returns.index) & set(ta.index) & set(k200) & set(markets))
        dates = [d for d in common if d >= base.START and d in fwd.index][::h]
        holdings = {}
        for dt in dates:
            k = k200[dt]
            market = markets[dt]
            act5_full = liq_frames['act5'].loc[dt] if dt in liq_frames['act5'].index else pd.Series(dtype=float)
            for u in UNIVERSES:
                codes = multi.universe_codes(u, k, market)
                y = fwd.loc[dt].reindex(codes)
                minobs = 70 if u == 'K200' else 120
                if y.notna().sum() < minobs:
                    continue
                scores, fam, others = build_factor_scores(dt, codes, files)
                if len(scores) < 8:
                    continue
                act5 = act5_full.reindex(codes)
                act5_rank = base.pct_rank(act5, True)
                for f, primary in scores.items():
                    cf20 = 0.8 * primary + 0.2 * others[f]
                    liq10 = 0.9 * cf20 + 0.1 * act5_rank
                    gt1 = cf20.where(act5 > 1.0)
                    strat_scores = {
                        'CF20': cf20,
                        'CF20_ACT5_W10': liq10,
                        'CF20_ACT5_GT1_DIAG': gt1,
                    }
                    for strat, score in strat_scores.items():
                        names = top_names(score, LIQ_TOPN)
                        if len(names) < LIQ_TOPN:
                            continue
                        key = (h, u, f, strat)
                        old = holdings.get(key, [])
                        turn = 1.0 - len(set(old) & set(names)) / LIQ_TOPN if old else 1.0
                        gross = float(y.reindex(names).mean())
                        all_rows.append({
                            'date': dt, 'sample': sample_of(dt), 'horizon': h,
                            'universe': u, 'factor': f, 'family': FACTOR_FAMILY[f],
                            'strategy': strat, 'gross': gross, 'turnover': turn,
                            'mean_act5': float(act5.reindex(names).mean()),
                            'act5_gt1_share': float((act5.reindex(names) > 1).mean()),
                        })
                        holdings[key] = names
    p = pd.DataFrame(all_rows)
    p.to_csv(OUT / 'liquidity_portfolio_paths.csv', index=False)
    return p


def summarize_liquidity(p):
    basep = p[p.strategy.eq('CF20')][['date','sample','horizon','universe','factor','gross','turnover']].rename(
        columns={'gross':'base_gross','turnover':'base_turnover'}
    )
    o = p[p.strategy.ne('CF20')].merge(
        basep, on=['date','sample','horizon','universe','factor'], how='inner'
    )
    o['gross_delta'] = o.gross - o.base_gross
    o['turnover_delta'] = o.turnover - o.base_turnover
    for c in COSTS:
        o[f'net_delta_{c}'] = o.gross_delta - o.turnover_delta * c / 10000
    o.to_csv(OUT / 'liquidity_matched_deltas.csv', index=False)

    stats = []
    fam = []
    boots = []
    for key, g in o.groupby(['strategy','universe','horizon','sample']):
        d = g.groupby('date').agg(
            gross_delta=('gross_delta','mean'), turnover_delta=('turnover_delta','mean'),
            mean_act5=('mean_act5','mean'), act5_gt1_share=('act5_gt1_share','mean'),
            **{f'net_{c}':(f'net_delta_{c}','mean') for c in COSTS}
        ).reset_index().sort_values('date')
        rec = dict(zip(['strategy','universe','horizon','sample'], key))
        rec.update({'n_dates': len(d), 'gross_delta': float(d.gross_delta.mean()),
                    'turnover_delta': float(d.turnover_delta.mean()),
                    'mean_act5': float(d.mean_act5.mean()),
                    'act5_gt1_share': float(d.act5_gt1_share.mean())})
        for c in COSTS:
            rec[f'net_delta_{c}'] = float(d[f'net_{c}'].mean())
        stats.append(rec)
        for metric in ['gross_delta', 'net_30', 'net_60']:
            bs = block_boot(d[metric].to_numpy())
            if len(bs):
                boots.append(rec | {
                    'metric': metric, 'mean': float(d[metric].mean()),
                    'ci025': float(np.quantile(bs,.025)), 'ci975': float(np.quantile(bs,.975)),
                    'p_gt0': float((bs > 0).mean()),
                })

    for key, g in o.groupby(['strategy','universe','horizon','sample','family']):
        d = g.groupby('date').gross_delta.mean()
        fam.append(dict(zip(['strategy','universe','horizon','sample','family'], key)) | {
            'n_dates': len(d), 'gross_delta': float(d.mean()),
            'positive_date_rate': float((d > 0).mean()),
        })

    stats = pd.DataFrame(stats)
    fam = pd.DataFrame(fam)
    boots = pd.DataFrame(boots)
    stats.to_csv(OUT / 'liquidity_summary.csv', index=False)
    fam.to_csv(OUT / 'liquidity_family_summary.csv', index=False)
    boots.to_csv(OUT / 'liquidity_bootstrap.csv', index=False)
    return stats, fam, boots


def render_summary(mech, mech_fam, mech_boot, dec, liq, liq_fam, liq_boot):
    L = [
        '# W20 Mechanism + Incremental Liquidity Validation', '',
        'The stock-selection rule is frozen: CF20 = 80% primary factor score + 20% consensus score from the other three factor families. Mechanism analysis uses the pre-existing Top20 / 10D reference specification. Liquidity analysis adds one predeclared feature only: ACT5 = recent 5D average trading amount / preceding 20D average trading amount.', '',
        '## 1) Mechanism: what CF20 actually changes', ''
    ]
    for u in UNIVERSES:
        L.append(f'### {u}')
        for s in CORE:
            z = mech[(mech.universe==u)&(mech['sample'].eq(s))]
            if z.empty:
                continue
            r = z.iloc[0]
            b = mech_boot[(mech_boot.universe==u)&(mech_boot['sample'].eq(s))&(mech_boot.metric.eq('portfolio_delta'))]
            p = b.iloc[0].p_gt0 if not b.empty else np.nan
            L.append(
                f"- {s}: portfolio {r.portfolio_delta:+.2%}/10D; replace {r.replace_share:.1%} of Top20; "
                f"added {r.added_return:+.2%} vs dropped {r.dropped_return:+.2%} (replacement edge {r.replacement_edge:+.2%}); "
                f"added primary rank {r.added_primary_rank:.1f} vs dropped {r.dropped_primary_rank:.1f}; "
                f"other-family score {r.added_other_score:.2f} vs {r.dropped_other_score:.2f}; bootstrap P(delta>0) {p:.0%}"
            )
        L.append('')

    L += ['## Family breadth of the mechanism', '']
    for u in UNIVERSES:
        for s in CORE:
            z = mech_fam[(mech_fam.universe==u)&(mech_fam['sample'].eq(s))]
            if z.empty:
                continue
            pos = int((z.portfolio_delta > 0).sum())
            vals = ', '.join(f"{r.family} {r.portfolio_delta:+.2%}" for _, r in z.sort_values('family').iterrows())
            L.append(f'- {u} {s}: positive families {pos}/4; {vals}')
    L += ['', '## Consensus decile diagnostic inside primary Top40', '']
    for u in UNIVERSES:
        for s in CORE:
            z = dec[(dec.universe==u)&(dec['sample'].eq(s))]
            if z.empty:
                continue
            low = z[z.other_decile<=3].fwd10.mean()
            high = z[z.other_decile>=8].fwd10.mean()
            L.append(f'- {u} {s}: other-family D8-10 minus D1-3 within primary Top40 = {high-low:+.2%}/10D')

    L += ['', '## 2) Incremental ACT5 overlay on top of CF20', '',
          'Main rule: CF20_ACT5_W10 = 90% CF20 + 10% ACT5 cross-sectional rank. The ACT5>1 version is diagnostic only and is not used to select a rule.', '']
    main = liq[liq.strategy.eq('CF20_ACT5_W10')]
    for u in UNIVERSES:
        L.append(f'### {u}')
        for h in LIQ_HORIZONS:
            vals = []
            ok = True
            for s in CORE:
                z = main[(main.universe==u)&(main.horizon.eq(h))&(main['sample'].eq(s))]
                if z.empty:
                    ok = False
                    continue
                r = z.iloc[0]
                vals.append(f"{s} gross {r.gross_delta:+.2%}, net30 {r.net_delta_30:+.2%}, net60 {r.net_delta_60:+.2%}")
                if not (r.gross_delta > 0 and r.net_delta_30 > 0):
                    ok = False
            L.append(f"- H{h} Top20: {'PASS' if ok else 'FAIL'}; " + ' | '.join(vals))
        L.append('')

    L += ['## Main H10 family breadth + 2023-24 inference', '']
    for u in UNIVERSES:
        for s in CORE:
            z = liq_fam[(liq_fam.strategy.eq('CF20_ACT5_W10'))&(liq_fam.universe==u)&(liq_fam.horizon.eq(10))&(liq_fam['sample'].eq(s))]
            if not z.empty:
                L.append(f"- {u} {s}: positive families {int((z.gross_delta>0).sum())}/4")
        b = liq_boot[(liq_boot.strategy.eq('CF20_ACT5_W10'))&(liq_boot.universe==u)&(liq_boot.horizon.eq(10))&(liq_boot['sample'].eq('NORMAL_2023_2024'))&(liq_boot.metric.eq('net_30'))]
        if not b.empty:
            r = b.iloc[0]
            L.append(f"  - 2023-24 net30 bootstrap: {r['mean']:+.2%}; CI [{r.ci025:+.2%},{r.ci975:+.2%}], P>0 {r.p_gt0:.0%}, n={int(r.n_dates)}")

    L += ['', '## Stress only: 2025 / 2026 H10', '']
    for u in UNIVERSES:
        z = main[(main.universe==u)&(main.horizon.eq(10))]
        mp = {r['sample']: r for _, r in z.iterrows()}
        b = mp.get('BULL_2025'); y = mp.get('YTD_2026')
        if b is not None and y is not None:
            L.append(f"- {u}: 2025 net30 {b.net_delta_30:+.2%}; 2026 net30 {y.net_delta_30:+.2%}")

    L += ['', '## Decision rules', '',
          '- Mechanism is considered credible only when added names consistently have higher other-family consensus than dropped names and added-minus-dropped forward returns are positive across multiple core blocks/universes.',
          '- ACT5 is incremental only if the frozen H10/Top20 main overlay has positive gross and 30bp-net delta in all three core blocks. H5 is robustness, not a replacement specification.',
          '- Do not choose ACT5_GT1 based on these results; it is interpretation-only.',
          '- 2025 and 2026 are stress diagnostics only and cannot rescue a failed normal-history rule.',
          '- Signals use information through the rebalance date and forward returns begin on the following trading day.', '']
    return '\n'.join(L) + '\n'


def main():
    returns, mcap, k200, markets, ta, liq_frames, files = load_inputs()
    events, cands = run_mechanism(returns, k200, markets, files)
    mech, mech_fam, mech_boot, dec = summarize_mechanism(events, cands)
    p = run_liquidity(returns, mcap, k200, markets, ta, liq_frames, files)
    liq, liq_fam, liq_boot = summarize_liquidity(p)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(
        render_summary(mech, mech_fam, mech_boot, dec, liq, liq_fam, liq_boot), encoding='utf-8'
    )
    print(f'mechanism_events={len(events):,}, candidate_rows={len(cands):,}, liquidity_paths={len(p):,}')


if __name__ == '__main__':
    main()
