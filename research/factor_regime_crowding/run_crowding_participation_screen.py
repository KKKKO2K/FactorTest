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

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
OUT.mkdir(parents=True, exist_ok=True)

MIXED = 'KOSDAQ_PLUS_KOSPI_EX_K200'
TARGET_FACTOR = 'OPFY1_REV'
TOPN = 20
STATE_PATH = ROOT / 'research/factor_regime_horizon_robustness/results/horizon_state_values.csv'
TEST_PATH = ROOT / 'research/factor_regime_horizon_robustness/results/horizon_tests.csv'
DAILY_PATH = ROOT / 'research/stock_level_factor_interaction/results_factor_level_finalists/daily_returns_text/MIXED_OPFY1_CF20.csv'

# Economic direction is pre-specified before looking at 2025/2026 outcomes.
# LOW_BAD = lack of participation; HIGH_BAD = crowding / heat / concentration.
FEATURE_DIRECTION = {
    'UNIVERSE_POS20_BREADTH': 'LOW_BAD',
    'SELECTED_POS20_BREADTH': 'LOW_BAD',
    'SELECTED_RET20_DISPERSION': 'HIGH_BAD',
    'SELECTED_TOP5_POS_CONC': 'HIGH_BAD',
    'SELECTED_ACT5_GT1_SHARE': 'HIGH_BAD',
    'SELECTED_ACT5_RANK_MEDIAN': 'HIGH_BAD',
    'HOLDING_RETENTION_4STATE': 'HIGH_BAD',
    'MOMENTUM_OVERLAP': 'HIGH_BAD',
    'OP12_OVERLAP': 'HIGH_BAD',
    'ALL_FACTOR_MULTIPLICITY': 'HIGH_BAD',
}


def sample_of(dt: pd.Timestamp) -> str:
    if dt.year <= 2019:
        return 'EARLY_2016_2019'
    if dt.year <= 2022:
        return 'LATE_2020_2022'
    if dt.year <= 2024:
        return 'OOS_2023_2024'
    if dt.year == 2025:
        return 'BULL_2025'
    return 'YTD_2026'


def trailing_compound(returns: pd.DataFrame, dt: pd.Timestamp, names, window: int = 20) -> pd.Series:
    if dt not in returns.index:
        return pd.Series(dtype=float)
    loc = returns.index.get_loc(dt)
    start = max(0, loc - window + 1)
    w = returns.iloc[start:loc + 1].reindex(columns=list(names))
    if len(w) < max(15, int(window * 0.75)):
        return pd.Series(index=list(names), dtype=float)
    valid = w.notna().sum(axis=0)
    z = w.clip(lower=-0.999999).fillna(0.0)
    out = (1.0 + z).prod(axis=0) - 1.0
    return out.where(valid >= max(15, int(window * 0.75)))


def load_factor_high_states() -> tuple[pd.DataFrame, float]:
    s = pd.read_csv(STATE_PATH)
    s['date'] = pd.to_datetime(s['date'])
    s = s[
        s['universe'].eq(MIXED)
        & s['predictor_type'].eq('FACTOR_BREADTH')
        & s['definition'].eq('FACTOR_20D')
    ][['date', 'value']].sort_values('date').drop_duplicates('date')

    t = pd.read_csv(TEST_PATH)
    q = t[
        t['universe'].eq(MIXED)
        & t['predictor_type'].eq('FACTOR_BREADTH')
        & t['definition'].eq('FACTOR_20D')
        & t['sample'].eq('TRAIN')
    ]
    if q.empty:
        raise RuntimeError('Could not recover frozen FACTOR_20D threshold')
    q2 = float(q['train_q2'].iloc[0])
    s['is_high'] = s['value'] >= q2 - 1e-12
    return s, q2


def forward_phase_average(daily: pd.DataFrame, state_dates: list[pd.Timestamp]) -> pd.DataFrame:
    daily = daily.copy()
    daily['date'] = pd.to_datetime(daily['date'])
    by_phase = {int(p): g.sort_values('date').set_index('date') for p, g in daily.groupby('phase')}
    rows = []
    for dt in state_dates:
        rec = {'date': dt}
        for rt, col in [('GROSS', 'gross_ret'), ('NET60', 'net60_ret')]:
            for h in (5, 10, 20):
                vals = []
                for phase, g in by_phase.items():
                    x = g.loc[g.index > dt, col].head(h)
                    if len(x) == h:
                        vals.append(float((1.0 + x).prod() - 1.0))
                rec[f'{rt}_FWD{h}'] = float(np.mean(vals)) if vals else np.nan
                rec[f'{rt}_FWD{h}_NPHASE'] = len(vals)
        rows.append(rec)
    return pd.DataFrame(rows)


def build_feature_panel(states: pd.DataFrame) -> pd.DataFrame:
    returns, mcap, k200 = base.load_basic()
    markets = multi.load_market_by_date()
    ta = base.load_trading_amount().reindex(index=mcap.index, columns=mcap.columns)
    act5 = base.build_liquidity_features(ta, mcap)['act5']
    files = {f: base.dated_files(path) for f, path in base.FACTORS.items()}

    state_dates = [d for d in states['date'] if d in returns.index and d in k200 and d in markets]
    holdings: dict[pd.Timestamp, dict[str, list[str]]] = {}
    universe_codes: dict[pd.Timestamp, pd.Index] = {}

    for dt in state_dates:
        codes = multi.universe_codes(MIXED, k200[dt], markets[dt])
        if len(codes) < 120:
            continue
        scores, others = core.build_scores(dt, codes, files)
        if set(scores) != set(core.FACTOR_FAMILY):
            continue
        by_factor = {}
        failed = False
        for f in core.FACTOR_FAMILY:
            names = core.top_names(0.8 * scores[f] + 0.2 * others[f], TOPN)
            if len(names) != TOPN:
                failed = True
                break
            by_factor[f] = names
        if failed:
            continue
        holdings[dt] = by_factor
        universe_codes[dt] = pd.Index(codes)

    valid_dates = sorted(holdings)
    pos = {d: i for i, d in enumerate(valid_dates)}
    rows = []
    for dt in valid_dates:
        by_factor = holdings[dt]
        names = by_factor[TARGET_FACTOR]
        codes = universe_codes[dt]

        sel_r20 = trailing_compound(returns, dt, names, 20).dropna()
        univ_r20 = trailing_compound(returns, dt, codes, 20).dropna()
        posret = sel_r20.clip(lower=0.0)
        pos_sum = float(posret.sum())
        top5_conc = float(posret.nlargest(5).sum() / pos_sum) if pos_sum > 0 else np.nan

        act = act5.loc[dt].reindex(codes) if dt in act5.index else pd.Series(index=codes, dtype=float)
        act_rank = pd.to_numeric(act, errors='coerce').rank(pct=True, method='average')
        sel_act = pd.to_numeric(act.reindex(names), errors='coerce').dropna()
        sel_rank = act_rank.reindex(names).dropna()

        i = pos[dt]
        retention = np.nan
        if i >= 4:
            old = set(holdings[valid_dates[i - 4]][TARGET_FACTOR])
            retention = len(old & set(names)) / TOPN

        mom_union = set(by_factor['MOM1M']) | set(by_factor['MOM12_1'])
        mom_overlap = len(set(names) & mom_union) / TOPN
        op12_overlap = len(set(names) & set(by_factor['OP12_REV'])) / TOPN

        other_factors = [f for f in core.FACTOR_FAMILY if f != TARGET_FACTOR]
        multiplicities = []
        for code in names:
            n = sum(code in set(by_factor[f]) for f in other_factors)
            multiplicities.append(n / len(other_factors))

        rows.append({
            'date': dt,
            'UNIVERSE_POS20_BREADTH': float((univ_r20 > 0).mean()) if len(univ_r20) else np.nan,
            'SELECTED_POS20_BREADTH': float((sel_r20 > 0).mean()) if len(sel_r20) else np.nan,
            'SELECTED_RET20_DISPERSION': float(sel_r20.std(ddof=1)) if len(sel_r20) >= 5 else np.nan,
            'SELECTED_TOP5_POS_CONC': top5_conc,
            'SELECTED_ACT5_GT1_SHARE': float((sel_act > 1.0).mean()) if len(sel_act) else np.nan,
            'SELECTED_ACT5_RANK_MEDIAN': float(sel_rank.median()) if len(sel_rank) else np.nan,
            'HOLDING_RETENTION_4STATE': retention,
            'MOMENTUM_OVERLAP': float(mom_overlap),
            'OP12_OVERLAP': float(op12_overlap),
            'ALL_FACTOR_MULTIPLICITY': float(np.mean(multiplicities)) if multiplicities else np.nan,
        })

    panel = pd.DataFrame(rows)
    panel = panel.merge(states[['date', 'value', 'is_high']], on='date', how='left')
    daily = pd.read_csv(DAILY_PATH)
    fwd = forward_phase_average(daily, panel['date'].tolist())
    panel = panel.merge(fwd, on='date', how='left')
    panel['sample'] = panel['date'].map(sample_of)
    panel.to_csv(OUT / 'crowding_feature_panel.csv', index=False, encoding='utf-8-sig')
    return panel


def group_stats(x: pd.DataFrame, flag: pd.Series, fwd_col: str) -> dict:
    bad = x.loc[flag & x[fwd_col].notna(), fwd_col]
    rest = x.loc[(~flag) & x[fwd_col].notna(), fwd_col]
    return {
        'n_bad': len(bad),
        'n_rest': len(rest),
        'bad_mean': float(bad.mean()) if len(bad) else np.nan,
        'rest_mean': float(rest.mean()) if len(rest) else np.nan,
        'bad_minus_rest': float(bad.mean() - rest.mean()) if len(bad) and len(rest) else np.nan,
        'bad_positive_share': float((bad > 0).mean()) if len(bad) else np.nan,
    }


def run_screen(panel: pd.DataFrame) -> pd.DataFrame:
    high = panel[panel['is_high']].copy()
    train = high[high['date'] < pd.Timestamp('2023-01-01')]
    rows = []

    for feature, direction in FEATURE_DIRECTION.items():
        trv = train[feature].dropna()
        if len(trv) < 60:
            continue
        q1, q2 = trv.quantile([1 / 3, 2 / 3]).tolist()
        cutoff = float(q1 if direction == 'LOW_BAD' else q2)

        def flag_frame(x: pd.DataFrame) -> pd.Series:
            if direction == 'LOW_BAD':
                return x[feature].notna() & (x[feature] <= cutoff + 1e-12)
            return x[feature].notna() & (x[feature] >= cutoff - 1e-12)

        rec = {'feature': feature, 'direction': direction, 'train_cutoff': cutoff, 'train_q1': float(q1), 'train_q2': float(q2)}
        for sample in ('EARLY_2016_2019', 'LATE_2020_2022', 'OOS_2023_2024', 'BULL_2025', 'YTD_2026'):
            x = high[high['sample'].eq(sample)].copy()
            flag = flag_frame(x)
            st = group_stats(x, flag, 'NET60_FWD20')
            prefix = sample
            rec[f'{prefix}_n'] = int(x['NET60_FWD20'].notna().sum())
            rec[f'{prefix}_flag_rate'] = float(flag[x['NET60_FWD20'].notna()].mean()) if x['NET60_FWD20'].notna().any() else np.nan
            for k, v in st.items():
                rec[f'{prefix}_{k}'] = v

            if sample == 'YTD_2026':
                eligible = x['NET60_FWD20'].notna() & (x['NET60_FWD20'] < 0)
                rec['YTD_2026_negative_n'] = int(eligible.sum())
                rec['YTD_2026_negative_capture'] = float(flag[eligible].mean()) if eligible.any() else np.nan

        # Frozen confirmatory gate. Minimum cell sizes prevent tiny-tercile wins.
        rec['pass_early'] = bool(rec.get('EARLY_2016_2019_n_bad', 0) >= 8 and rec.get('EARLY_2016_2019_bad_minus_rest', np.nan) < 0)
        rec['pass_late'] = bool(rec.get('LATE_2020_2022_n_bad', 0) >= 8 and rec.get('LATE_2020_2022_bad_minus_rest', np.nan) < 0)
        rec['pass_oos'] = bool(rec.get('OOS_2023_2024_n_bad', 0) >= 6 and rec.get('OOS_2023_2024_bad_minus_rest', np.nan) < 0)
        rec['pass_2025_control'] = bool(rec.get('BULL_2025_flag_rate', 1.0) <= 0.40)
        rec['pass_2026_capture'] = bool(
            rec.get('YTD_2026_negative_capture', 0.0) >= 0.50
            and rec.get('YTD_2026_bad_mean', np.nan) < 0
        )
        rec['SCREEN_PASS'] = all(rec[k] for k in ('pass_early', 'pass_late', 'pass_oos', 'pass_2025_control', 'pass_2026_capture'))
        rows.append(rec)

    out = pd.DataFrame(rows).sort_values(['SCREEN_PASS', 'YTD_2026_negative_capture', 'BULL_2025_flag_rate'], ascending=[False, False, True])
    out.to_csv(OUT / 'crowding_feature_screen.csv', index=False, encoding='utf-8-sig')
    return out


def pct(x):
    return 'NA' if pd.isna(x) else f'{x:+.2%}'


def make_report(panel: pd.DataFrame, screen: pd.DataFrame, q2: float) -> str:
    lines = [
        '# Crowding / Participation Regime Screen — Mixed OPFY1+CF20', '',
        f'- Frozen FACTOR_20D HIGH cutoff: {q2:.3f}.',
        '- Candidate features are computed only from information available by the signal close; forward sleeve returns start the next trading day.',
        '- Economic adverse direction is pre-specified: low participation is bad; high dispersion/concentration/activity/holding persistence/cross-factor overlap is bad.',
        '- Feature cutoffs are TRAIN 2016-22 terciles only and frozen thereafter.',
        '- A screen PASS requires adverse 20D Net60 forward return in both 2016-19 and 2020-22, same adverse sign in 2023-24, <=40% false-positive rate during healthy 2025 HIGH dates, and >=50% capture of negative 2026 HIGH dates.',
        '', '## Results', '',
    ]
    for r in screen.itertuples(index=False):
        lines.append(
            f"- {r.feature} ({r.direction}, cutoff={r.train_cutoff:.4f}): "
            f"early d={pct(r.EARLY_2016_2019_bad_minus_rest)}, "
            f"late d={pct(r.LATE_2020_2022_bad_minus_rest)}, "
            f"OOS d={pct(r.OOS_2023_2024_bad_minus_rest)}, "
            f"2025 flag={r.BULL_2025_flag_rate:.0%}, "
            f"2026 negative capture={r.YTD_2026_negative_capture:.0%}, "
            f"2026 bad mean={pct(r.YTD_2026_bad_mean)}; PASS={bool(r.SCREEN_PASS)}"
        )

    passed = screen[screen['SCREEN_PASS']]
    lines += ['', '## Passed features', '']
    if passed.empty:
        lines.append('- None.')
    else:
        for f in passed['feature']:
            lines.append(f'- {f}')

    lines += [
        '', '## 2025 vs 2026 HIGH-state feature medians', '',
    ]
    high = panel[panel['is_high']]
    for f in FEATURE_DIRECTION:
        a = high.loc[high['sample'].eq('BULL_2025'), f].median()
        b = high.loc[high['sample'].eq('YTD_2026'), f].median()
        lines.append(f'- {f}: 2025 {a:.4f} vs 2026 {b:.4f}')

    lines += [
        '', '## Guardrails', '',
        '- This is a pre-specified feature screen, not permission to combine near-misses into a multivariate rule.',
        '- 2025 is used only as a healthy-HIGH false-positive control; 2026 is a stress/capture check.',
        '- Any passing single feature must next survive exact daily-NAV 10-phase Gross/Net30/Net60 testing before it can become an exposure rule.',
        '- 2023+ remains robustness evidence rather than pristine untouched OOS because prior research iterations used later data.',
    ]
    return '\n'.join(lines)


def main() -> None:
    states, q2 = load_factor_high_states()
    panel = build_feature_panel(states)
    screen = run_screen(panel)
    report = make_report(panel, screen, q2)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(report, encoding='utf-8')
    print(report)


if __name__ == '__main__':
    main()
