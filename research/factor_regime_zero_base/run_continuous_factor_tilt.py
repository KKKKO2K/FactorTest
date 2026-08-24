from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PANEL = HERE / 'results_persistence_rotation/persistence_rotation_panel.csv'
LIQ = HERE.parent / 'factor_regime_v1/results/liquidity_states.csv'
OUT = HERE / 'results_continuous_factor_tilt'
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = [
    'MOM1M', 'MOM12_1', 'OP12_REV', 'OPFY1_REV',
    'PBR12MF', 'PER12MF', 'PRIVATE_FLOW', 'FOREIGN_FLOW'
]
PERSIST_FEATURES = [
    'CROSS_HORIZON_RANK_CORR', 'PC1_SHARE_60', 'LEADER_STRENGTH_20',
    'SIGN_ALIGNMENT_20_60', 'DISPERSION_CHANGE_20', 'BREADTH_20',
    'DISPERSION_20'
]
LIQ_FEATURES = [
    'MKT_ACT1_BREADTH', 'MKT_ACT1_CHANGE_4', 'FACTOR_TOP_ACT5_BREADTH_MEAN'
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
    l['MKT_ACT1_CHANGE_4'] = l.groupby('universe')['MKT_ACT1_BREADTH'].diff(4)

    z = p.merge(
        l[['date', 'universe'] + LIQ_FEATURES],
        on=['date', 'universe'], how='left'
    )

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

            pz_tr, pz_te = standardize(tr, te, PERSIST_FEATURES)
            p_dirs = {}
            for f in PERSIST_FEATURES:
                ic = spearman(tr[f], tr['TARGET_FACTOR_MOM_20'])
                p_dirs[f] = 1.0 if np.isfinite(ic) and ic >= 0 else -1.0
            p_dir = pd.Series(p_dirs)
            p_train_score = (pz_tr * p_dir).mean(axis=1)
            p_test_score = (pz_te * p_dir).mean(axis=1)

            lz_tr, lz_te = standardize(tr, te, LIQ_FEATURES)
            l_dirs = {}
            for f in LIQ_FEATURES:
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

                ps = float(p_test_score.loc[idx])
                ls = float(l_test_score.loc[idx])
                pp = empirical_percentile(p_train_score, ps)
                lp = empirical_percentile(l_train_score, ls)
                cp_raw = 0.5 * pp + 0.5 * lp
                cp = empirical_percentile(c_train_score, cp_raw)

                lambdas = {
                    'PERSIST_CONT': MAX_TILT * (2 * pp - 1),
                    'LIQ_CONT': MAX_TILT * (2 * lp - 1),
                    'COMBINED_CONT': MAX_TILT * (2 * cp - 1),
                    'EW8': 0.0,
                    'TOP2': 1.0,
                }

                rec = {
                    'date': r.date,
                    'universe': u,
                    'eval_year': year,
                    'period': period_of(year),
                    'persist_score': ps,
                    'persist_pct': pp,
                    'liq_score': ls,
                    'liq_pct': lp,
                    'combined_pct': cp,
                    'target_top2_alpha_vs_ew8_20': float(r['TARGET_TOP2_ALPHA_VS_EW8_20']),
                }

                for model, lam in lambdas.items():
                    w = top2_weights(r) if model == 'TOP2' else blend_weights(r, lam)
                    rec[f'{model}_lambda'] = float(lam)
                    rec[f'{model}_gross'] = forward_return(r, w)
                    for j, fac in enumerate(FACTORS):
                        rec[f'{model}_w_{fac}'] = float(w[j])
                rows.append(rec)

    return pd.DataFrame(rows).sort_values(['universe', 'date']).reset_index(drop=True)


def add_costs(decisions: pd.DataFrame) -> pd.DataFrame:
    models = ['PERSIST_CONT', 'LIQ_CONT', 'COMBINED_CONT', 'EW8', 'TOP2']
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
    models = ['PERSIST_CONT', 'LIQ_CONT', 'COMBINED_CONT']
    rows = []
    for cost in COSTS:
        zc = path[path.cost_bps.eq(cost)]
        for pname, (a, b) in PERIODS.items():
            zp = zc[zc.eval_year.between(a, b)]
            for u, g in zp.groupby('universe'):
                if len(g) < 3:
                    continue
                ew = perf(g['EW8_ret'])
                top = perf(g['TOP2_ret'])
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
                        'top2_cagr': top['cagr'],
                        'top2_sharpe': top['sharpe'],
                        'delta_cagr_vs_ew8': pp['cagr'] - ew['cagr'],
                        'delta_sharpe_vs_ew8': pp['sharpe'] - ew['sharpe'],
                        'delta_mdd_vs_ew8': pp['mdd'] - ew['mdd'],
                        'delta_sharpe_vs_top2': pp['sharpe'] - top['sharpe'],
                        'avg_abs_lambda': float(g[f'{model}_lambda'].abs().mean()),
                        'avg_lambda': float(g[f'{model}_lambda'].mean()),
                        'annual_turnover': float(g[f'{model}_turnover'].mean() * (252 / 20)),
                    })
    return pd.DataFrame(rows)


def pct(x: float) -> str:
    return 'NA' if not np.isfinite(x) else f'{x:+.2%}'


def report(stats: pd.DataFrame) -> str:
    L = [
        '# Continuous Factor Risk-Budget Tilt — Zero Base Stage 5', '',
        '- EW8 is always retained as the core portfolio.',
        '- Frozen mapping before this run: w = EW8 + lambda * (TOP2 - EW8), lambda bounded to [-0.25, +0.25].',
        '- Persistence block uses the seven Stage-1 factor-momentum survivors; liquidity/selectivity block uses MKT_ACT1_BREADTH, MKT_ACT1_CHANGE_4 and FACTOR_TOP_ACT5_BREADTH_MEAN.',
        '- Feature directions, standardization and empirical percentile maps use only prior data each evaluation year.',
        '- Combined tilt is equal-block Persistence / Liquidity; no threshold sweep and no max-tilt sweep.',
        '- Decisions are non-overlapping 20D; costs apply to one-way factor-sleeve turnover.',
        '- Primary benchmark is EW8. 2025/26 are stress evidence, not pristine untouched OOS.', '',
        '## Predeclared success gate', '',
        '- At 10 bps, a model must have positive median Sharpe delta vs EW8 in both DEV 2020-22 and CONFIRM 2023-24.',
        '- It must improve Sharpe in at least 4/6 universes in CONFIRM 2023-24.',
        '- 2025/2026-only success is insufficient.', ''
    ]

    for cost in COSTS:
        L += [f'## Cost {cost} bps', '']
        for model in ['PERSIST_CONT', 'LIQ_CONT', 'COMBINED_CONT']:
            L.append(f'### {model}')
            for p in PERIODS:
                q = stats[(stats.cost_bps == cost) & (stats.period == p) & (stats.model == model)]
                if q.empty:
                    continue
                L.append(
                    f'- {p}: median ΔSharpe vs EW8 {q.delta_sharpe_vs_ew8.median():+.3f}; '
                    f'ΔCAGR {pct(q.delta_cagr_vs_ew8.median())}; '
                    f'ΔMDD {pct(q.delta_mdd_vs_ew8.median())}; '
                    f'better Sharpe {(q.delta_sharpe_vs_ew8 > 0).sum()}/{len(q)} universes; '
                    f'median |lambda| {q.avg_abs_lambda.median():.3f}; '
                    f'median annual turnover {q.annual_turnover.median():.2f}'
                )
            L.append('')

    L += ['## Gate result at 10 bps', '']
    q10 = stats[stats.cost_bps.eq(10)]
    for model in ['PERSIST_CONT', 'LIQ_CONT', 'COMBINED_CONT']:
        dev = q10[(q10.model == model) & q10.period.eq('DEV_2020_2022')]
        con = q10[(q10.model == model) & q10.period.eq('CONFIRM_2023_2024')]
        gate = bool(
            len(dev) and len(con)
            and dev.delta_sharpe_vs_ew8.median() > 0
            and con.delta_sharpe_vs_ew8.median() > 0
            and (con.delta_sharpe_vs_ew8 > 0).sum() >= 4
        )
        L.append(
            f'- {model}: PASS={gate}; DEV median ΔSharpe {dev.delta_sharpe_vs_ew8.median():+.3f}; '
            f'CONFIRM {con.delta_sharpe_vs_ew8.median():+.3f}; '
            f'CONFIRM better universes {(con.delta_sharpe_vs_ew8 > 0).sum()}/{len(con)}'
        )

    L += ['', '## Interpretation rule', '',
          '- Do not change max tilt or percentile mapping after seeing this output.',
          '- If the continuous form passes, treat Factor Regime as a bounded active-risk budgeting signal rather than a discrete state classifier.',
          '- If it fails, the surviving IC remains useful for monitoring, but the next allocation research must add genuinely leader-specific raw stock information rather than retuning the same factor-return/liquidity aggregates.']
    return '\n'.join(L)


def main():
    panel = build_panel()
    decisions = build_decisions(panel)
    path = add_costs(decisions)
    stats = summarize(path)
    panel.to_csv(OUT / 'continuous_tilt_panel.csv', index=False, encoding='utf-8-sig')
    decisions.to_csv(OUT / 'continuous_tilt_decisions.csv', index=False, encoding='utf-8-sig')
    path.to_csv(OUT / 'continuous_tilt_costed_path.csv', index=False, encoding='utf-8-sig')
    stats.to_csv(OUT / 'continuous_tilt_summary.csv', index=False, encoding='utf-8-sig')
    text = report(stats)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
