from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
INP = HERE / 'results_persistence_rotation/persistence_rotation_panel.csv'
OUT = HERE / 'results_persistence_policy'
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = [
    'MOM1M', 'MOM12_1', 'OP12_REV', 'OPFY1_REV',
    'PBR12MF', 'PER12MF', 'PRIVATE_FLOW', 'FOREIGN_FLOW'
]
# Frozen after Stage-1 screen: all seven relations that passed the predeclared
# gate for the economically direct TARGET_FACTOR_MOM_20 target.
FEATURES = [
    'CROSS_HORIZON_RANK_CORR', 'PC1_SHARE_60', 'LEADER_STRENGTH_20',
    'SIGN_ALIGNMENT_20_60', 'DISPERSION_CHANGE_20', 'BREADTH_20',
    'DISPERSION_20'
]
TARGET = 'TARGET_FACTOR_MOM_20'
COSTS = [0, 10, 30]
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
    lo = a.quantile(.01); hi = a.quantile(.99)
    a = a.clip(lo, hi, axis=1); b = b.clip(lo, hi, axis=1)
    med = a.median(); a = a.fillna(med); b = b.fillna(med)
    mu = a.mean(); sd = a.std(ddof=0).replace(0, 1.0)
    return (a-mu)/sd, (b-mu)/sd


def weights_for_row(r: pd.Series, mode: str) -> np.ndarray:
    cur = np.array([r[f'CUR20_{f}'] for f in FACTORS], dtype=float)
    order = np.argsort(cur)
    w = np.zeros(len(FACTORS), dtype=float)
    if mode == 'TOP2':
        w[order[-2:]] = .5
    elif mode == 'BOTTOM2':
        w[order[:2]] = .5
    elif mode == 'EW8':
        w[:] = 1/len(FACTORS)
    else:
        raise ValueError(mode)
    return w


def forward_return(r: pd.Series, w: np.ndarray) -> float:
    fwd = np.array([r[f'FWD20_{f}'] for f in FACTORS], dtype=float)
    return float(np.dot(w, fwd))


def build_predictions(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for u, g in panel.groupby('universe'):
        g = g.sort_values('date').reset_index(drop=True)
        # Economic policy is evaluated on a non-overlapping 20D schedule.
        g['nonoverlap'] = (np.arange(len(g)) % 4 == 0)
        for year in range(2020, int(g.date.dt.year.max()) + 1):
            tr = g[g.date < pd.Timestamp(f'{year}-01-01')].copy()
            te = g[g.date.dt.year.eq(year)].copy()
            if len(tr) < 80 or te.empty:
                continue
            ztr, zte = standardize(tr, te, FEATURES)
            dirs = {}
            for feat in FEATURES:
                ic = spearman(tr[feat], tr[TARGET])
                dirs[feat] = 1.0 if np.isfinite(ic) and ic >= 0 else -1.0
            d = pd.Series(dirs)
            train_score = (ztr * d).mean(axis=1)
            test_score = (zte * d).mean(axis=1)
            q33, q67 = train_score.quantile([1/3, 2/3])
            for idx, r in te.iterrows():
                if not bool(r['nonoverlap']):
                    continue
                score = float(test_score.loc[idx])
                action = 'TOP2' if score >= q67 else ('BOTTOM2' if score <= q33 else 'EW8')
                w_policy = weights_for_row(r, action)
                w_top2 = weights_for_row(r, 'TOP2')
                rec = {
                    'date': r.date, 'universe': u, 'eval_year': year,
                    'score': score, 'train_q33': float(q33), 'train_q67': float(q67),
                    'action': action, 'target_factor_mom_20': float(r[TARGET]),
                    'policy_gross': forward_return(r, w_policy),
                }
                for mode in ['TOP2', 'BOTTOM2', 'EW8']:
                    w = weights_for_row(r, mode)
                    rec[f'{mode.lower()}_gross'] = forward_return(r, w)
                for j, fac in enumerate(FACTORS):
                    rec[f'w_{fac}'] = float(w_policy[j])
                    rec[f'top_w_{fac}'] = float(w_top2[j])
                rows.append(rec)
    return pd.DataFrame(rows).sort_values(['universe', 'date']).reset_index(drop=True)


def add_costs(path: pd.DataFrame) -> pd.DataFrame:
    out = []
    for u, g0 in path.groupby('universe'):
        g = g0.sort_values('date').copy()
        W = g[[f'w_{f}' for f in FACTORS]].to_numpy(dtype=float)
        prev = np.zeros(len(FACTORS))
        turns = []
        for w in W:
            turns.append(.5 * float(np.abs(w-prev).sum()))
            prev = w
        g['policy_turnover'] = turns

        TW = g[[f'top_w_{f}' for f in FACTORS]].to_numpy(dtype=float)
        prev = np.zeros(len(FACTORS))
        top_turns = []
        for w in TW:
            top_turns.append(.5 * float(np.abs(w-prev).sum()))
            prev = w
        g['top2_turnover'] = top_turns

        for cost in COSTS:
            z = g.copy()
            z['cost_bps'] = cost
            z['policy_ret'] = z.policy_gross - z.policy_turnover * cost/10000
            z['top2_ret'] = z.top2_gross - z.top2_turnover * cost/10000
            ew_turn = np.zeros(len(z))
            if len(ew_turn):
                ew_turn[0] = .5
            z['ew8_turnover'] = ew_turn
            z['ew8_ret'] = z.ew8_gross - z.ew8_turnover * cost/10000
            out.append(z)
    return pd.concat(out, ignore_index=True)


def perf(r: pd.Series) -> dict:
    r = r.dropna().astype(float)
    if len(r) < 3:
        return {'cagr': np.nan, 'sharpe': np.nan, 'mdd': np.nan}
    nav = (1+r).cumprod()
    periods_per_year = 252/20
    years = len(r)/periods_per_year
    cagr = float(nav.iloc[-1]**(1/years)-1) if years > 0 and nav.iloc[-1] > 0 else np.nan
    sd = r.std(ddof=1)
    sharpe = float(r.mean()/sd*math.sqrt(periods_per_year)) if sd > 0 else np.nan
    mdd = float((nav/nav.cummax()-1).min())
    return {'cagr': cagr, 'sharpe': sharpe, 'mdd': mdd}


def summarize(path: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cost in COSTS:
        zc = path[path.cost_bps.eq(cost)]
        for pname, (a, b) in PERIODS.items():
            zp = zc[zc.eval_year.between(a, b)]
            for u, g in zp.groupby('universe'):
                if len(g) < 3:
                    continue
                pp = perf(g.policy_ret); tp = perf(g.top2_ret); ep = perf(g.ew8_ret)
                rows.append({
                    'universe': u, 'cost_bps': cost, 'period': pname, 'n_rebalances': len(g),
                    'policy_cagr': pp['cagr'], 'policy_sharpe': pp['sharpe'], 'policy_mdd': pp['mdd'],
                    'top2_cagr': tp['cagr'], 'top2_sharpe': tp['sharpe'], 'top2_mdd': tp['mdd'],
                    'ew8_cagr': ep['cagr'], 'ew8_sharpe': ep['sharpe'], 'ew8_mdd': ep['mdd'],
                    'delta_cagr_vs_top2': pp['cagr']-tp['cagr'],
                    'delta_sharpe_vs_top2': pp['sharpe']-tp['sharpe'],
                    'delta_mdd_vs_top2': pp['mdd']-tp['mdd'],
                    'delta_cagr_vs_ew8': pp['cagr']-ep['cagr'],
                    'delta_sharpe_vs_ew8': pp['sharpe']-ep['sharpe'],
                    'action_top2_share': float((g.action=='TOP2').mean()),
                    'action_bottom2_share': float((g.action=='BOTTOM2').mean()),
                    'action_ew8_share': float((g.action=='EW8').mean()),
                    'annual_policy_turnover': float(g.policy_turnover.mean()*(252/20)),
                    'annual_top2_turnover': float(g.top2_turnover.mean()*(252/20)),
                    'target_sign_hit': float(((g.score >= 0) == (g.target_factor_mom_20 >= 0)).mean()),
                })
    return pd.DataFrame(rows)


def pct(x: float) -> str:
    return 'NA' if not np.isfinite(x) else f'{x:+.2%}'


def report(stats: pd.DataFrame) -> str:
    L = [
        '# Persistence / Rotation Stage 1b — Economic Policy Audit', '',
        '- Feature set is frozen to the seven Stage-1 PASS predictors for TARGET_FACTOR_MOM_20.',
        '- Each evaluation year estimates only feature standardization and predictor direction from prior data.',
        '- Composite top tercile -> current top-2 factors; bottom tercile -> current bottom-2 factors; middle -> equal-weight 8 factors.',
        '- Decisions are sampled every fourth 5D state so the 20D holding windows do not overlap.',
        '- Costs are charged on factor-sleeve one-way turnover. MDD is 20D-rebalance NAV MDD, not daily-NAV MDD.',
        '- 2025/2026 are stress evidence, not pristine untouched OOS because Stage 1 already inspected them.', ''
    ]
    for cost in COSTS:
        L += [f'## Cost {cost} bps', '']
        for p in PERIODS:
            q = stats[(stats.cost_bps==cost)&(stats.period==p)]
            if q.empty:
                continue
            L.append(
                f'- {p}: median ΔCAGR vs TOP2 {pct(q.delta_cagr_vs_top2.median())}; '
                f'ΔSharpe {q.delta_sharpe_vs_top2.median():+.3f}; '
                f'ΔMDD {pct(q.delta_mdd_vs_top2.median())}; '
                f'better Sharpe {(q.delta_sharpe_vs_top2>0).sum()}/{len(q)} universes; '
                f'median ΔSharpe vs EW8 {q.delta_sharpe_vs_ew8.median():+.3f}; '
                f'median sign-hit {q.target_sign_hit.median():.1%}'
            )
        L.append('')
    L += ['## 2025 / 2026 universe detail — 10 bps', '']
    q = stats[(stats.cost_bps==10)&(stats.period.isin(['BULL_2025','YTD_2026']))]
    for r in q.sort_values(['period','universe']).itertuples(index=False):
        L.append(
            f'- {r.period} {r.universe}: policy Sharpe {r.policy_sharpe:+.2f} vs TOP2 {r.top2_sharpe:+.2f} '
            f'(Δ {r.delta_sharpe_vs_top2:+.2f}); ΔCAGR {pct(r.delta_cagr_vs_top2)}; '
            f'actions TOP2/BOTTOM2/EW8 {r.action_top2_share:.0%}/{r.action_bottom2_share:.0%}/{r.action_ew8_share:.0%}'
        )
    L += ['', '## Interpretation rule', '',
          '- Do not tune score cutoffs after seeing these results. If policy improvement is broad in 2023-24 and survives both 2025 and 2026 stress, the persistence/rotation axis is economically actionable.',
          '- If predictive IC survives but policy value is unstable, retain persistence as a monitoring/risk state and proceed to Factor Opportunity.']
    return '\n'.join(L)


def main():
    p = pd.read_csv(INP)
    p['date'] = pd.to_datetime(p['date'])
    pred = build_predictions(p)
    path = add_costs(pred)
    stats = summarize(path)
    pred.to_csv(OUT/'policy_decisions_gross.csv', index=False, encoding='utf-8-sig')
    path.to_csv(OUT/'policy_path_costed.csv', index=False, encoding='utf-8-sig')
    stats.to_csv(OUT/'policy_summary.csv', index=False, encoding='utf-8-sig')
    text = report(stats)
    (OUT/'RESEARCH_SUMMARY.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
