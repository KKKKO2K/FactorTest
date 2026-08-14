from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results_mechanism_liquidity'
SRC = OUT / 'mechanism_candidate_pool.csv'
RNG = np.random.default_rng(20260814)
CORE = ('EARLY_2016_2019','LATE_2020_2022','NORMAL_2023_2024')
BUCKETS = ('ALL_TOP40','TOP20','RANK21_40')


def block_boot(x, block=4, nboot=10000):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 8:
        return np.array([])
    nb = int(np.ceil(n / block))
    starts = RNG.integers(0, n, size=(nboot, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    return x[idx.reshape(nboot, -1)[:, :n]].mean(axis=1)


def factor_date_gaps(g):
    rows = []
    for (dt, f), x in g.groupby(['date','factor']):
        hi = x.loc[x.other_decile >= 8, 'fwd10'].dropna()
        lo = x.loc[x.other_decile <= 3, 'fwd10'].dropna()
        if len(hi) < 2 or len(lo) < 2:
            continue
        rows.append({'date':dt,'factor':f,'high':hi.mean(),'low':lo.mean(),'gap':hi.mean()-lo.mean(),
                     'n_high':len(hi),'n_low':len(lo)})
    return pd.DataFrame(rows)


def main():
    p = pd.read_csv(SRC, parse_dates=['date'])
    rows = []
    dec_rows = []
    for u in sorted(p.universe.unique()):
        for s in CORE:
            z0 = p[(p.universe==u)&(p['sample']==s)].copy()
            if z0.empty:
                continue
            for bucket in BUCKETS:
                if bucket == 'TOP20':
                    z = z0[z0.primary_bucket=='TOP20']
                elif bucket == 'RANK21_40':
                    z = z0[z0.primary_bucket=='RANK21_40']
                else:
                    z = z0
                fd = factor_date_gaps(z)
                if fd.empty:
                    continue
                d = fd.groupby('date').gap.mean().sort_index()
                bs = block_boot(d.to_numpy())
                rec = {'universe':u,'sample':s,'bucket':bucket,'n_dates':len(d),'mean_gap':d.mean(),
                       'positive_date_rate':(d>0).mean()}
                if len(bs):
                    rec.update({'ci025':np.quantile(bs,.025),'ci975':np.quantile(bs,.975),'p_gt0':(bs>0).mean()})
                rows.append(rec)

            # decile surface: factor-average within date first.
            for dec, zd in z0.groupby('other_decile'):
                fd = zd.groupby(['date','factor']).fwd10.mean().reset_index()
                dd = fd.groupby('date').fwd10.mean()
                dec_rows.append({'universe':u,'sample':s,'other_decile':int(dec),'n_dates':len(dd),
                                 'mean_fwd10':dd.mean()})

    r = pd.DataFrame(rows)
    dec = pd.DataFrame(dec_rows)
    r.to_csv(OUT/'consensus_surface_bootstrap.csv', index=False)
    dec.to_csv(OUT/'consensus_decile_surface_factor_neutral.csv', index=False)

    L = ['# W20 Cross-Family Consensus Surface — Bootstrap Validation','',
         'Universe/date/factor candidate pool is fixed as the primary factor Top40. High consensus = other-family deciles 8-10; low consensus = deciles 1-3. Returns are averaged within factor-date first, then across factors by date. 4-rebalance-date moving-block bootstrap with 10,000 resamples.','']
    for u in sorted(r.universe.unique()):
        L.append(f'## {u}')
        for s in CORE:
            z = r[(r.universe==u)&(r['sample']==s)]
            for bucket in BUCKETS:
                q = z[z.bucket==bucket]
                if q.empty: continue
                x=q.iloc[0]
                L.append(f"- {s} {bucket}: high-minus-low {x.mean_gap:+.2%}/10D; CI [{x.ci025:+.2%},{x.ci975:+.2%}], P>0 {x.p_gt0:.0%}, positive dates {x.positive_date_rate:.0%}, n={int(x.n_dates)}")
        L.append('')
    L += ['## Interpretation guardrail','',
          '- ALL_TOP40 tests whether cross-family consensus contains conditional stock-selection information given a strong primary score.',
          '- TOP20 asks whether consensus helps identify false positives already selected by the primary factor.',
          '- RANK21_40 asks whether consensus helps find overlooked candidates just outside the primary Top20.',
          '- No threshold is selected from these results; D8-10 vs D1-3 is a diagnostic surface contrast only.','']
    (OUT/'CONSENSUS_SURFACE_VALIDATION.md').write_text('\n'.join(L)+'\n', encoding='utf-8')
    print(f'bootstrap_rows={len(r)}, decile_rows={len(dec)}')

if __name__ == '__main__':
    main()
