from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PANEL = HERE / 'results_persistence_rotation/persistence_rotation_panel.csv'
LIQ = HERE.parent / 'factor_regime_v1/results/liquidity_states.csv'
OUT = HERE / 'results_continuous_tilt_selection_bias_audit'
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = [
    'MOM1M', 'MOM12_1', 'OP12_REV', 'OPFY1_REV',
    'PBR12MF', 'PER12MF', 'PRIVATE_FLOW', 'FOREIGN_FLOW'
]

# Entire Stage-1 predictor set, before any DEV/CONFIRM survivor selection.
PERSIST_ALL = [
    'BREADTH_20', 'BREADTH_60', 'DISPERSION_20', 'DISPERSION_60',
    'ABS_OPPORTUNITY_20', 'RANGE_20', 'LEADER_STRENGTH_20',
    'LOSER_WEAKNESS_20', 'WINNER_GAP_20', 'CROSS_HORIZON_RANK_CORR',
    'PREV_RANK_CORR_20', 'RANK_TURNOVER_20', 'BREADTH_CHANGE_20',
    'DISPERSION_CHANGE_20', 'AVG_PAIR_CORR_60', 'PC1_SHARE_60',
    'FACTOR_VOL_MEDIAN_60', 'SIGN_ALIGNMENT_20_60'
]

# Entire Stage-4A aggregate liquidity/participation set, before survivor selection.
LIQ_ALL = [
    'MKT_ACT5_BREADTH', 'MKT_ACT1_BREADTH', 'KOSDAQ_TA_SHARE',
    'FACTOR_TOP_ACT5_BREADTH_MEAN', 'FACTOR_TOP_MINUS_MKT_ACT5',
    'MKT_ACT5_CHANGE_4', 'MKT_ACT1_CHANGE_4', 'KOSDAQ_TA_SHARE_CHANGE_4',
    'FACTOR_TOP_ACT5_CHANGE_4', 'FACTOR_TOP_MINUS_MKT_ACT5_CHANGE_4'
]

COSTS = [0, 10, 30]
MAX_TILT = 0.25
PERIODS = {
    'DEV_2020_2022': (2020, 2022),
    'CONFIRM_2023_2024': (2023, 2024),
    'BULL_2025': (2025, 2025),
    'YTD_2026': (2026, 2026),
}


def spearman(x: pd.Series, y: pd.Series) -> float:
    z = pd.concat([x, y], axis=1).dropna()
    if len(z) < 10 or z.iloc[:, 0].nunique() < 2 or z.iloc[:, 1].nunique() < 2:
        return np.nan
    return float(z.iloc[:, 0].rank().corr(z.iloc[:, 1].rank()))


def standardize(train: pd.DataFrame, test: pd.DataFrame, cols: list[str]):
    a = train[cols].astype(float).copy()
    b = test[cols].astype(float).copy()
    lo = a.quantile(.01)
    hi = a.quantile(.99)
    a = a.clip(lo, hi, axis=1)
    b = b.clip(lo, hi, axis=1)
    med = a.median()
    a = a.fillna(med)
    b = b.fillna(med)
    mu = a.mean()
    sd = a.std(ddof=0).replace(0, 1.0)
    return (a - mu) / sd, (b - mu) / sd


def empirical_percentile(train_score: pd.Series, x: float) -> float:
    a = train_score.dropna().to_numpy(dtype=float)
    if len(a) == 0 or not np.isfinite(x):
        return 0.5
    return float((np.sum(a < x) + 0.5 * np.sum(a == x)) / len(a))


def period_of(year: int) -> str:
    if year <= 2022:
        return 'DEV_2020_2022'
    if year <= 2024:
        return 'CONFIRM_2023_2024'
    if year == 2025:
        return 'BULL_2025'
    return 'YTD_2026'


def build_panel() -> pd.DataFrame:
    p = pd.read_csv(PANEL)
    p['date'] = pd.to_datetime(p['date'])

    l = pd.read_csv(LIQ)
    l['date'] = pd.to_datetime(l['date'])
    l = l.sort_values(['universe', 'date']).copy()
    l['FACTOR_TOP_MINUS_MKT_ACT5'] = l['FACTOR_TOP_ACT5_BREADTH_MEAN'] - l['MKT_ACT5_BREADTH']
    l['MKT_ACT5_CHANGE_4'] = l.groupby('universe')['MKT_ACT5_BREADTH'].diff(4)
    l['MKT_ACT1_CHANGE_4'] = l.groupby('universe')['MKT_ACT1_BREADTH'].diff(4)
    l['KOSDAQ_TA_SHARE_CHANGE_4'] = l.groupby('universe')['KOSDAQ_TA_SHARE'].diff(4)
    l['FACTOR_TOP_ACT5_CHANGE_4'] = l.groupby('universe')['FACTOR_TOP_ACT5_BREADTH_MEAN'].diff(4)
    l['FACTOR_TOP_MINUS_MKT_ACT5_CHANGE_4'] = l.groupby('universe')['FACTOR_TOP_MINUS_MKT_ACT5'].diff(4)

    z = p.merge(l[['date', 'universe'] + LIQ_ALL], on=['date', 'universe'], how='left')

    cur = z[[f'CUR20_{f}' for f in FACTORS]].to_numpy(dtype=float)
    fwd = z[[f'FWD20_{f}' for f in FACTORS]].to_numpy(dtype=float)
    top2_alpha = []
    for c, y in zip(cur, fwd):
        order = np.argsort(c)
        top = order[-2:]
        top2_alpha.append(float(np.mean(y[top]) - np.mean(y)))
    z['TARGET_TOP2_ALPHA_VS_EW8_20'] = top2_alpha
    return z


def top2_weights(r: pd.Series) -> np.ndarray:
    cur = np.array([r[f'CUR20_{f}'] for f in FACTORS], dtype=float)
    order = np.argsort(cur)
    w = np.zeros(len(FACTORS), dtype=float)
    w[order[-2:]] = 0.5
    return w


def ew8_weights() -> np.ndarray:
    return np.repeat(1 / len(FACTORS), len(FACTORS)).astype(float)


def blend_weights(r: pd.Series, lam: float) -> np.ndarray:
    ew = ew8_weights()
    top = top2_weights(r)
    return ew + lam * (top - ew)


def forward_return(r: pd.Series, w: np.ndarray) -> float:
    fwd = np.array([r[f'FWD20_{f}'] for f in FACTORS], dtype=float)
    return float(np.dot(w, fwd))


def build_decisions(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for u, g0 in panel.groupby('universe'):
        g = g0.sort_values('date').reset_index(drop=True).copy()
        g['nonoverlap'] = (np.arange(len(g)) % 4 == 0)

        for year in range(2020, int(g.date.dt.year.max()) + 1):
            tr = g[g.date < pd.Timestamp(f'{year}-01-01')].copy()
            te = g[g.date.dt.year.eq(year)].copy()
            if len(tr) < 80 or te.empty:
                continue

            pz_tr, pz_te = standardize(tr, te, PERSIST_ALL)
            p_dirs = {}
            for f in PERSIST_ALL:
                ic = spearman(tr[f], tr['TARGET_FACTOR_MOM_20'])
                p_dirs[f] = 1.0 if np.isfinite(ic) and ic >= 0 else -1.0
            p_dir = pd.Series(p_dirs)
            p_train_score = (pz_tr * p_dir).mean(axis=1)
            p_test_score = (pz_te * p_dir).mean(axis=1)

            lz_tr, lz_te = standardize(tr, te, LIQ_ALL)
            l_dirs = {}
            for f in LIQ_ALL:
                ic = spearman(tr[f], tr['TARGET_TOP2_ALPHA_VS_EW8_20'])
                l_dirs[f] = 1.0 if np.isfinite(ic) and ic >= 0 else -1.0
            l_dir = pd.Series(l_dirs)
            l_train_score = (lz_tr * l_dir).mean(axis=1)
            l_test_score = (lz_te * l_dir).mean(axis=1)

            p_train_pct = p_train_score.rank(pct=True, method='average')
            l_train_pct = l_train_score.rank(pct=True, method='average')
            c_train_score = 0.5 * p_train_pct + 0.5 * l_train_pct

            for idx, r in te.iterrows():
                if not bool(r['nonoverlap']):
                    continue

                pp = empirical_percentile(p_train_score, float(p_test_score.loc[idx]))
                lp = empirical_percentile(l_train_score, float(l_test_score.loc[idx]))
                cp_raw = 0.5 * pp + 0.5 * lp
                cp = empirical_percentile(c_train_score, cp_raw)

                lambdas = {
                    'PERSIST_ALL_CONT': MAX_TILT * (2 * pp - 1),
                    'LIQ_ALL_CONT': MAX_TILT * (2 * lp - 1),
                    'COMBINED_ALL_CONT': MAX_TILT * (2 * cp - 1),
                    'EW8': 0.0,
                }

                rec = {
                    'date': r.date,
                    'universe': u,
                    'eval_year': year,
                    'period': period_of(year),
                    'persist_pct': pp,
                    'liq_pct': lp,
                    'combined_pct': cp,
                }
                for model, lam in lambdas.items():
                    w = blend_weights(r, lam)
                    rec[f'{model}_lambda'] = float(lam)
                    rec[f'{model}_gross'] = forward_return(r, w)
                    for j, fac in enumerate(FACTORS):
                        rec[f'{model}_w_{fac}'] = float(w[j])
                rows.append(rec)

    return pd.DataFrame(rows).sort_values(['universe', 'date']).reset_index(drop=True)


def add_costs(decisions: pd.DataFrame) -> pd.DataFrame:
    models = ['PERSIST_ALL_CONT', 'LIQ_ALL_CONT', 'COMBINED_ALL_CONT', 'EW8']
    out = []
    for u, g0 in decisions.groupby('universe'):
        g = g0.sort_values('date').copy()
        for model in models:
            W = g[[f'{model}_w_{f}' for f in FACTORS]].to_numpy(dtype=float)
            prev = np.zeros(len(FACTORS))
            turns = []
            for w in W:
                turns.append(0.5 * float(np.abs(w - prev).sum()))
                prev = w
            g[f'{model}_turnover'] = turns
        for cost in COSTS:
            z = g.copy()
            z['cost_bps'] = cost
            for model in models:
                z[f'{model}_ret'] = z[f'{model}_gross'] - z[f'{model}_turnover'] * cost / 10000
            out.append(z)
    return pd.concat(out, ignore_index=True)


def perf(r: pd.Series) -> dict:
    r = r.dropna().astype(float)
    if len(r) < 3:
        return {'cagr': np.nan, 'sharpe': np.nan, 'mdd': np.nan}
    nav = (1 + r).cumprod()
    ppy = 252 / 20
    years = len(r) / ppy
    cagr = float(nav.iloc[-1] ** (1 / years) - 1) if years > 0 and nav.iloc[-1] > 0 else np.nan
    sd = r.std(ddof=1)
    sharpe = float(r.mean() / sd * math.sqrt(ppy)) if sd > 0 else np.nan
    mdd = float((nav / nav.cummax() - 1).min())
    return {'cagr': cagr, 'sharpe': sharpe, 'mdd': mdd}


def summarize(path: pd.DataFrame) -> pd.DataFrame:
    models = ['PERSIST_ALL_CONT', 'LIQ_ALL_CONT', 'COMBINED_ALL_CONT']
    rows = []
    for cost in COSTS:
        zc = path[path.cost_bps.eq(cost)]
        for pname, (a, b) in PERIODS.items():
            zp = zc[zc.eval_year.between(a, b)]
            for u, g in zp.groupby('universe'):
                if len(g) < 3:
                    continue
                ew = perf(g['EW8_ret'])
                for model in models:
                    pp = perf(g[f'{model}_ret'])
                    rows.append({
                        'model': model,
                        'universe': u,
                        'cost_bps': cost,
                        'period': pname,
                        'n_rebalances': len(g),
                        'cagr': pp['cagr'],
                        'sharpe': pp['sharpe'],
                        'mdd': pp['mdd'],
                        'ew8_cagr': ew['cagr'],
                        'ew8_sharpe': ew['sharpe'],
                        'ew8_mdd': ew['mdd'],
                        'delta_cagr_vs_ew8': pp['cagr'] - ew['cagr'],
                        'delta_sharpe_vs_ew8': pp['sharpe'] - ew['sharpe'],
                        'delta_mdd_vs_ew8': pp['mdd'] - ew['mdd'],
                        'avg_abs_lambda': float(g[f'{model}_lambda'].abs().mean()),
                        'annual_turnover': float(g[f'{model}_turnover'].mean() * (252 / 20)),
                    })
    return pd.DataFrame(rows)


def pct(x: float) -> str:
    return 'NA' if not np.isfinite(x) else f'{x:+.2%}'


def report(stats: pd.DataFrame) -> str:
    L = [
        '# Continuous Tilt Feature-Selection Bias Audit', '',
        '- Purpose: test whether the Stage-5 continuous-tilt result survives without using the DEV/CONFIRM survivor lists to choose inputs.',
        '- Persistence block uses all 18 predictors declared before Stage 1; liquidity block uses all 10 aggregate stock/liquidity features declared before Stage 4A.',
        '- No feature is removed because of 2020-24 performance. Only feature direction, standardization and percentile mapping are estimated from prior data each evaluation year.',
        '- Portfolio mapping is unchanged from Stage 5: EW8 + lambda*(TOP2-EW8), lambda in [-0.25,+0.25].',
        '- No max-tilt sweep, no threshold sweep, and no post-result feature pruning.', '',
        '## Predeclared robustness gate', '',
        '- At 10 bps: positive median Sharpe delta vs EW8 in DEV 2020-22 and CONFIRM 2023-24, with >=4/6 confirmation universes improving.',
        '- 2025/2026 are stress evidence only.', ''
    ]
    for cost in COSTS:
        L += [f'## Cost {cost} bps', '']
        for model in ['PERSIST_ALL_CONT', 'LIQ_ALL_CONT', 'COMBINED_ALL_CONT']:
            L.append(f'### {model}')
            for p in PERIODS:
                q = stats[(stats.cost_bps == cost) & (stats.period == p) & (stats.model == model)]
                if q.empty:
                    continue
                L.append(
                    f'- {p}: median ΔSharpe {q.delta_sharpe_vs_ew8.median():+.3f}; '
                    f'ΔCAGR {pct(q.delta_cagr_vs_ew8.median())}; '
                    f'ΔMDD {pct(q.delta_mdd_vs_ew8.median())}; '
                    f'better Sharpe {(q.delta_sharpe_vs_ew8 > 0).sum()}/{len(q)}; '
                    f'median |lambda| {q.avg_abs_lambda.median():.3f}; '
                    f'annual turnover {q.annual_turnover.median():.2f}'
                )
            L.append('')

    L += ['## Gate result at 10 bps', '']
    q10 = stats[stats.cost_bps.eq(10)]
    for model in ['PERSIST_ALL_CONT', 'LIQ_ALL_CONT', 'COMBINED_ALL_CONT']:
        dev = q10[(q10.model == model) & q10.period.eq('DEV_2020_2022')]
        con = q10[(q10.model == model) & q10.period.eq('CONFIRM_2023_2024')]
        gate = bool(
            len(dev) and len(con)
            and dev.delta_sharpe_vs_ew8.median() > 0
            and con.delta_sharpe_vs_ew8.median() > 0
            and (con.delta_sharpe_vs_ew8 > 0).sum() >= 4
        )
        L.append(
            f'- {model}: PASS={gate}; DEV {dev.delta_sharpe_vs_ew8.median():+.3f}; '
            f'CONFIRM {con.delta_sharpe_vs_ew8.median():+.3f}; '
            f'CONFIRM better {(con.delta_sharpe_vs_ew8 > 0).sum()}/{len(con)}'
        )
    L += ['', '## Interpretation', '',
          '- A PASS here is materially stronger evidence than Stage 5 because the predictor list itself no longer embeds the 2023-24 survivor screen.',
          '- A FAIL does not erase the underlying IC findings, but would downgrade Stage 5 to an exploratory survivor-selection result.']
    return '\n'.join(L)


def main():
    panel = build_panel()
    decisions = build_decisions(panel)
    path = add_costs(decisions)
    stats = summarize(path)
    decisions.to_csv(OUT / 'selection_bias_audit_decisions.csv', index=False, encoding='utf-8-sig')
    path.to_csv(OUT / 'selection_bias_audit_costed_path.csv', index=False, encoding='utf-8-sig')
    stats.to_csv(OUT / 'selection_bias_audit_summary.csv', index=False, encoding='utf-8-sig')
    text = report(stats)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
