from __future__ import annotations

from pathlib import Path
import itertools
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

FULL = ROOT / "research" / "factor_regime_full_state_map" / "results"
ABS = ROOT / "research" / "factor_regime_absolute_states" / "results"
V1 = ROOT / "research" / "factor_regime_v1" / "results"

FAMILIES = ("MOMENTUM", "REVISION", "VALUE", "FLOW")
PAIRS = list(itertools.combinations(FAMILIES, 2))
MIN_CELL = 5
MIN_CONTRAST = 8

PERIODS = {
    "EARLY_2016_2019": (pd.Timestamp("2016-01-01"), pd.Timestamp("2020-01-01")),
    "COVID_LIQUIDITY_2020_2021": (pd.Timestamp("2020-01-01"), pd.Timestamp("2022-01-01")),
    "BEAR_2022": (pd.Timestamp("2022-01-01"), pd.Timestamp("2023-01-01")),
    "FULL_2016_2022": (pd.Timestamp("2016-01-01"), pd.Timestamp("2023-01-01")),
}


def compound_forward(s: pd.Series, n: int) -> pd.Series:
    logs = np.log1p(s.clip(lower=-0.999999))
    return np.expm1(sum(logs.shift(-i) for i in range(1, n + 1)))


def compound_trailing(s: pd.Series, n: int) -> pd.Series:
    logs = np.log1p(s.clip(lower=-0.999999))
    return np.expm1(sum(logs.shift(i) for i in range(0, n)))


def load_market():
    m = pd.read_csv(V1 / "market_daily_returns.csv", index_col=0)
    m.index = pd.to_datetime(m.index)
    return m.sort_index()


def market_state_panel(market: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for u in market.columns:
        s = market[u].dropna().sort_index()
        f20 = compound_forward(s, 20)
        t20 = compound_trailing(s, 20)
        t60 = compound_trailing(s, 60)
        z = pd.DataFrame({"date": s.index, "universe": u, "mkt_fwd20": f20.values,
                          "mkt_trail20": t20.values, "mkt_trail60": t60.values})
        rows.append(z)
    return pd.concat(rows, ignore_index=True)


def label_period(dt: pd.Timestamp) -> str | None:
    for name, (a,b) in PERIODS.items():
        if name == "FULL_2016_2022":
            continue
        if a <= dt < b:
            return name
    return None


def market_baseline(mp: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for u,g in mp.groupby("universe"):
        for p,(a,b) in PERIODS.items():
            z=g[(g.date>=a)&(g.date<b)]
            if len(z):
                rows.append({"universe":u,"period":p,"n":len(z),
                             "trail20_mean":z.mkt_trail20.mean(),"trail60_mean":z.mkt_trail60.mean(),
                             "fwd20_mean":z.mkt_fwd20.mean(),"fwd20_median":z.mkt_fwd20.median(),
                             "fwd20_positive_share":(z.mkt_fwd20>0).mean()})
    return pd.DataFrame(rows)


def breadth_subperiod(mp: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame]:
    b = pd.read_csv(ABS / "refined_breadth_panel.csv")
    b["date"] = pd.to_datetime(b["date"])
    b = b.merge(mp,on=["date","universe"],how="left")
    metrics=["RELATIVE_WORKING_BREADTH","ABS_CONFIRMED_BREADTH","DEFENSIVE_WORKING_BREADTH",
             "BEARISH_REVERSE_BREADTH","POSITIVE_ABS_BREADTH"]
    rows=[]; cond=[]
    # prior60 terciles fit on early 2016-2019 by universe to avoid using 2020-22 future distribution
    cuts={}
    for u,g in b.groupby("universe"):
        tr=g[(g.date>=pd.Timestamp("2016-01-01"))&(g.date<pd.Timestamp("2020-01-01"))].mkt_trail60.dropna()
        if len(tr)>=40:
            cuts[u]=(tr.quantile(1/3),tr.quantile(2/3))
    for u,g in b.groupby("universe"):
        for p,(a,zend) in PERIODS.items():
            z=g[(g.date>=a)&(g.date<zend)].copy()
            if z.empty: continue
            for met in metrics:
                x=z[[met,"mkt_fwd20","mkt_trail60"]].dropna()
                if len(x)<20: continue
                q1,q2=x[met].quantile([1/3,2/3])
                lo=x[x[met]<=q1]; hi=x[x[met]>=q2]
                rows.append({"universe":u,"period":p,"state":met,"n_low":len(lo),"n_high":len(hi),
                             "low_fwd20":lo.mkt_fwd20.mean(),"high_fwd20":hi.mkt_fwd20.mean(),
                             "high_minus_low":hi.mkt_fwd20.mean()-lo.mkt_fwd20.mean(),
                             "low_prior60":lo.mkt_trail60.mean(),"high_prior60":hi.mkt_trail60.mean()})
                if u in cuts:
                    c1,c2=cuts[u]
                    zz=x.copy()
                    zz["prior60_bin"]=np.where(zz.mkt_trail60<=c1,"LOW",np.where(zz.mkt_trail60>=c2,"HIGH","MID"))
                    for bin_,w in zz.groupby("prior60_bin"):
                        if len(w)<15: continue
                        q1b,q2b=w[met].quantile([1/3,2/3])
                        l=w[w[met]<=q1b]; h=w[w[met]>=q2b]
                        if len(l)>=5 and len(h)>=5:
                            cond.append({"universe":u,"period":p,"state":met,"prior60_bin":bin_,
                                         "n_low":len(l),"n_high":len(h),"low_fwd20":l.mkt_fwd20.mean(),
                                         "high_fwd20":h.mkt_fwd20.mean(),"high_minus_low":h.mkt_fwd20.mean()-l.mkt_fwd20.mean()})
    return pd.DataFrame(rows),pd.DataFrame(cond)


def pair_subperiod(mp: pd.DataFrame) -> pd.DataFrame:
    s=pd.read_csv(FULL / "family_states_static.csv")
    s["date"]=pd.to_datetime(s["date"])
    s=s[s.cut_name=="Q33"].copy()
    rows=[]
    for a,b in PAIRS:
        aa=s[s.family==a][["date","universe","state6","member_same_sign_20d"]].rename(columns={"state6":"state_a","member_same_sign_20d":"agree_a"})
        bb=s[s.family==b][["date","universe","state6","member_same_sign_20d"]].rename(columns={"state6":"state_b","member_same_sign_20d":"agree_b"})
        x=aa.merge(bb,on=["date","universe"]).merge(mp,on=["date","universe"],how="left")
        for u,g in x.groupby("universe"):
            for p,(st,en) in PERIODS.items():
                z=g[(g.date>=st)&(g.date<en)]
                sig=z[(z.state_a=="W+")&(z.state_b=="W+")]
                oth=z[~((z.state_a=="W+")&(z.state_b=="W+"))]
                if len(sig)<MIN_CELL: continue
                rows.append({"universe":u,"period":p,"family_pair":f"{a}_X_{b}","n_signal":len(sig),"n_other":len(oth),
                             "signal_fwd20":sig.mkt_fwd20.mean(),"other_fwd20":oth.mkt_fwd20.mean(),
                             "diff_vs_other":sig.mkt_fwd20.mean()-oth.mkt_fwd20.mean(),
                             "unconditional_fwd20":z.mkt_fwd20.mean(),
                             "excess_vs_unconditional":sig.mkt_fwd20.mean()-z.mkt_fwd20.mean(),
                             "signal_prior60":sig.mkt_trail60.mean(),"agree_a":sig.agree_a.mean(),"agree_b":sig.agree_b.mean()})
    return pd.DataFrame(rows)


def revision_flow_contrast(mp: pd.DataFrame) -> pd.DataFrame:
    s=pd.read_csv(FULL / "family_states_static.csv")
    s["date"]=pd.to_datetime(s["date"])
    s=s[s.cut_name=="Q33"]
    r=s[s.family=="REVISION"][["date","universe","state6"]].rename(columns={"state6":"rev"})
    f=s[s.family=="FLOW"][["date","universe","state6"]].rename(columns={"state6":"flow"})
    x=r.merge(f,on=["date","universe"]).merge(mp,on=["date","universe"],how="left")
    rows=[]
    for u,g in x.groupby("universe"):
        for p,(a,b) in PERIODS.items():
            z=g[(g.date>=a)&(g.date<b)&(g.rev=="W+")]
            left=z[z.flow=="W+"]; right=z[z.flow.isin(["N+","N-"])]
            if len(left)>=MIN_CONTRAST and len(right)>=MIN_CONTRAST:
                rows.append({"universe":u,"period":p,"n_wplus":len(left),"n_neutral":len(right),
                             "wplus_fwd20":left.mkt_fwd20.mean(),"neutral_fwd20":right.mkt_fwd20.mean(),
                             "diff":left.mkt_fwd20.mean()-right.mkt_fwd20.mean(),
                             "wplus_prior60":left.mkt_trail60.mean(),"neutral_prior60":right.mkt_trail60.mean()})
    return pd.DataFrame(rows)


def write_summary(mb,br,pairs,rf,cond):
    L=["# 2016-2022 Historical Subperiod Validation","",
       "Purpose: test whether the 2016-2022 discovery block hides internal regime mixing. Calendar splits are descriptive: 2016-2019, 2020-2021, and 2022. Prior-60D market-state bins use tercile thresholds fit only on 2016-2019.",
       "Family states retain the existing Q33 thresholds fit on the full 2016-2022 discovery sample, so within-discovery state comparisons are diagnostic rather than untouched OOS.",""]
    L += ["## Market baselines",""]
    for u in ["K200","KOSPI_ALL","KOSPI_EX_K200","KOSDAQ"]:
        z=mb[(mb.universe==u)&(mb.period!="FULL_2016_2022")]
        if z.empty: continue
        vals="; ".join([f"{r.period}: trail60 {r.trail60_mean:+.2%}, next20 {r.fwd20_mean:+.2%}" for _,r in z.iterrows()])
        L.append(f"- {u}: {vals}")
    L += ["","## Breadth H-L by subperiod",""]
    for u in ["K200","KOSPI_ALL","KOSPI_EX_K200","KOSDAQ"]:
        for met in ["RELATIVE_WORKING_BREADTH","ABS_CONFIRMED_BREADTH","DEFENSIVE_WORKING_BREADTH"]:
            z=br[(br.universe==u)&(br.state==met)&(br.period!="FULL_2016_2022")]
            if z.empty: continue
            vals="; ".join([f"{r.period} {r.high_minus_low:+.2%}" for _,r in z.iterrows()])
            L.append(f"- {u} {met}: {vals}")
    L += ["","## W+/W+ pair effects — median excess vs same-period unconditional",""]
    for u in ["K200","KOSPI_ALL","KOSPI_EX_K200","KOSDAQ"]:
        for p in ["EARLY_2016_2019","COVID_LIQUIDITY_2020_2021","BEAR_2022"]:
            z=pairs[(pairs.universe==u)&(pairs.period==p)]
            if z.empty: continue
            L.append(f"- {u} {p}: {len(z)}/6 pairs, median excess {z.excess_vs_unconditional.median():+.2%}, positive {int((z.excess_vs_unconditional>0).sum())}/{len(z)}")
    L += ["","## Revision W+ -> Flow W+ vs Flow Neutral",""]
    if not rf.empty:
        for _,r in rf.iterrows():
            L.append(f"- {r.universe} {r.period}: diff {r['diff']:+.2%}, n {int(r.n_wplus)}/{int(r.n_neutral)}, prior60 {r.wplus_prior60:+.2%}/{r.neutral_prior60:+.2%}")
    L += ["","## Interpretation guardrail","",
          "- If calendar subperiod signs flip but same-prior60-bin signs are more stable, prefer market-state conditioning over calendar labels.",
          "- If both calendar and prior-market-state conditioning flip, treat the discovery-era relation as unstable rather than a structural signal.",
          "- Do not use the pooled 2016-2022 mean as evidence of stability unless the subperiod decomposition supports it.",""]
    return "\n".join(L)


def main():
    market=load_market(); mp=market_state_panel(market)
    mb=market_baseline(mp)
    br,cond=breadth_subperiod(mp)
    pairs=pair_subperiod(mp)
    rf=revision_flow_contrast(mp)
    mb.to_csv(OUT/"market_subperiod_baseline.csv",index=False,encoding="utf-8-sig")
    br.to_csv(OUT/"breadth_subperiods.csv",index=False,encoding="utf-8-sig")
    cond.to_csv(OUT/"breadth_prior60_conditioned.csv",index=False,encoding="utf-8-sig")
    pairs.to_csv(OUT/"wplus_pair_subperiods.csv",index=False,encoding="utf-8-sig")
    rf.to_csv(OUT/"revision_flow_subperiod_contrast.csv",index=False,encoding="utf-8-sig")
    (OUT/"RESEARCH_SUMMARY.md").write_text(write_summary(mb,br,pairs,rf,cond),encoding="utf-8")

if __name__=="__main__":
    main()
