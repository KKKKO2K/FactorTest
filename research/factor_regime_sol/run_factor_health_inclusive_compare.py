from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
IN = HERE / "results_factor_health_v2" / "factor_health_panel.csv"
OUT = HERE / "results_factor_health_inclusive_compare"
OUT.mkdir(parents=True, exist_ok=True)

TRAIN_END = pd.Timestamp("2023-01-01")
SAMPLES = {
    "TRAIN_2017_2022": (pd.Timestamp("2017-01-01"), pd.Timestamp("2022-12-31")),
    "POST_2023_PLUS": (pd.Timestamp("2023-01-01"), pd.Timestamp("2099-12-31")),
    "POST_2023_2024": (pd.Timestamp("2023-01-01"), pd.Timestamp("2024-12-31")),
    "BULL_2025": (pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
    "YTD_2026": (pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31")),
}


def nw_dummy_t(y: np.ndarray, d: np.ndarray, lag: int) -> tuple[float, float]:
    mask = np.isfinite(y) & np.isfinite(d)
    y = y[mask].astype(float); d = d[mask].astype(float)
    if len(y) < 12 or len(np.unique(d)) < 2:
        return np.nan, np.nan
    X = np.column_stack([np.ones(len(y)), d])
    try:
        inv = np.linalg.inv(X.T @ X)
    except np.linalg.LinAlgError:
        return np.nan, np.nan
    beta = inv @ (X.T @ y)
    e = y - X @ beta
    S = np.zeros((2,2))
    for i in range(len(y)):
        S += e[i]**2 * np.outer(X[i], X[i])
    for L in range(1, lag+1):
        w = 1-L/(lag+1)
        G = np.zeros((2,2))
        for i in range(L,len(y)):
            G += e[i]*e[i-L]*np.outer(X[i], X[i-L])
        S += w*(G+G.T)
    V = inv @ S @ inv
    se = math.sqrt(max(V[1,1],0.0))
    return float(beta[1]), float(beta[1]/se) if se>0 else np.nan


def add_inclusive(x: pd.DataFrame) -> pd.DataFrame:
    x = x.copy()
    own_w = x.target_state.eq("W+").astype(float)
    own_r = x.target_state.eq("R-").astype(float)
    x["SELF_A"] = own_w
    x["SELF_B"] = own_w - own_r
    x["FH_A_INCLUSIVE"] = (3.0*x.FH_A_HEALTHY_BREADTH + own_w) / 4.0
    x["FH_B_INCLUSIVE"] = (3.0*x.FH_B_NET_BREADTH + own_w - own_r) / 4.0

    x["SELF_C"] = np.nan
    for (u,t), g in x[x.date < TRAIN_END].groupby(["universe","target"]):
        s = g.target_spread20.dropna().astype(float)
        a = g.target_top_abs20.dropna().astype(float)
        if len(s)<20 or len(a)<20: continue
        smu, ssd = float(s.mean()), float(s.std(ddof=0))
        amu, asd = float(a.mean()), float(a.std(ddof=0))
        if not np.isfinite(ssd) or ssd<=1e-12: ssd=1.0
        if not np.isfinite(asd) or asd<=1e-12: asd=1.0
        m = (x.universe==u)&(x.target==t)
        zsp = ((x.loc[m,"target_spread20"]-smu)/ssd).clip(-4,4)
        zab = ((x.loc[m,"target_top_abs20"]-amu)/asd).clip(-4,4)
        x.loc[m,"SELF_C"] = 0.5*zsp + 0.5*zab
    x["FH_C_INCLUSIVE"] = (3.0*x.FH_C_CONTINUOUS + x.SELF_C) / 4.0
    return x


def freeze_terciles(x: pd.DataFrame, metrics: list[str]) -> dict[tuple[str,str,str], tuple[float,float]]:
    out={}
    tr=x[x.date<TRAIN_END]
    for (u,t),g in tr.groupby(["universe","target"]):
        for m in metrics:
            v=g[m].dropna()
            if len(v)<30 or v.nunique()<3: continue
            q1,q2=v.quantile([1/3,2/3]).tolist()
            if np.isfinite(q1) and np.isfinite(q2) and q1<q2:
                out[(u,t,m)]=(float(q1),float(q2))
    return out


def run_hl(x: pd.DataFrame, metrics: list[str], cuts: dict) -> pd.DataFrame:
    rows=[]
    for sample,(lo,hi) in SAMPLES.items():
        z0=x[(x.date>=lo)&(x.date<=hi)]
        for (u,t),g0 in z0.groupby(["universe","target"]):
            g0=g0.sort_values("date")
            for m in metrics:
                if (u,t,m) not in cuts: continue
                q1,q2=cuts[(u,t,m)]
                for h in (5,20):
                    for outcome in ("top","spread"):
                        ycol=f"{outcome}_fwd{h}"
                        z=g0[[m,ycol]].dropna().copy()
                        if len(z)<12: continue
                        b=np.where(z[m]<=q1,"LOW",np.where(z[m]>=q2,"HIGH","MID"))
                        keep=np.isin(b,["LOW","HIGH"])
                        z=z.loc[keep].copy(); b=np.asarray(b)[keep]
                        hi_y=z.loc[b=="HIGH",ycol]; lo_y=z.loc[b=="LOW",ycol]
                        if len(hi_y)<5 or len(lo_y)<5: continue
                        d=(b=="HIGH").astype(float)
                        beta,tstat=nw_dummy_t(z[ycol].to_numpy(float),d,3 if h==20 else 0)
                        rows.append({"sample":sample,"universe":u,"target":t,"metric":m,"horizon":h,"outcome":outcome,
                                     "n_high":len(hi_y),"n_low":len(lo_y),"high_mean":hi_y.mean(),"low_mean":lo_y.mean(),
                                     "high_minus_low":hi_y.mean()-lo_y.mean(),"nw_t":tstat,
                                     "high_positive_share":(hi_y>0).mean(),"low_positive_share":(lo_y>0).mean()})
    return pd.DataFrame(rows)


def partial_self(x: pd.DataFrame) -> pd.DataFrame:
    # Standardized regression: future top20 ~ ex-target health + own component.
    pairs=[("FH_A_HEALTHY_BREADTH","SELF_A","A"),("FH_B_NET_BREADTH","SELF_B","B"),("FH_C_CONTINUOUS","SELF_C","C")]
    rows=[]
    for sample,(lo,hi) in SAMPLES.items():
        z0=x[(x.date>=lo)&(x.date<=hi)]
        for (u,t),g0 in z0.groupby(["universe","target"]):
            for ex,selfc,label in pairs:
                z=g0[["top_fwd20",ex,selfc]].dropna().copy()
                if len(z)<30 or z[ex].std(ddof=0)<=1e-12 or z[selfc].std(ddof=0)<=1e-12: continue
                zex=(z[ex]-z[ex].mean())/z[ex].std(ddof=0)
                zself=(z[selfc]-z[selfc].mean())/z[selfc].std(ddof=0)
                X=np.column_stack([np.ones(len(z)),zex,zself]); y=z.top_fwd20.to_numpy(float)
                try: inv=np.linalg.inv(X.T@X)
                except np.linalg.LinAlgError: continue
                beta=inv@X.T@y; e=y-X@beta
                S=np.zeros((3,3))
                for i in range(len(y)): S+=e[i]**2*np.outer(X[i],X[i])
                for L in range(1,4):
                    w=1-L/4; G=np.zeros((3,3))
                    for i in range(L,len(y)): G+=e[i]*e[i-L]*np.outer(X[i],X[i-L])
                    S+=w*(G+G.T)
                V=inv@S@inv
                se0=math.sqrt(max(V[1,1],0)); se1=math.sqrt(max(V[2,2],0))
                rows.append({"sample":sample,"universe":u,"target":t,"family":label,"n":len(z),
                             "ex_beta_per_1sd":beta[1],"ex_t":beta[1]/se0 if se0>0 else np.nan,
                             "self_beta_per_1sd":beta[2],"self_t":beta[2]/se1 if se1>0 else np.nan})
    return pd.DataFrame(rows)


def aggregate_compare(hl: pd.DataFrame) -> pd.DataFrame:
    pairs=[("FH_A_HEALTHY_BREADTH","FH_A_INCLUSIVE","A"),("FH_B_NET_BREADTH","FH_B_INCLUSIVE","B"),("FH_C_CONTINUOUS","FH_C_INCLUSIVE","C")]
    rows=[]
    for ex,inc,label in pairs:
        for sample in SAMPLES:
            a=hl[(hl.metric==ex)&(hl.sample==sample)&(hl.horizon==20)&(hl.outcome=="top")]
            b=hl[(hl.metric==inc)&(hl.sample==sample)&(hl.horizon==20)&(hl.outcome=="top")]
            m=a.merge(b,on=["sample","universe","target","horizon","outcome"],suffixes=("_ex","_inc"))
            if m.empty: continue
            rows.append({"family":label,"sample":sample,"n_pairs":len(m),
                         "ex_median_hl":m.high_minus_low_ex.median(),"inc_median_hl":m.high_minus_low_inc.median(),
                         "inc_minus_ex_median":(m.high_minus_low_inc-m.high_minus_low_ex).median(),
                         "ex_positive_share":(m.high_minus_low_ex>0).mean(),"inc_positive_share":(m.high_minus_low_inc>0).mean(),
                         "inc_better_share":(m.high_minus_low_inc>m.high_minus_low_ex).mean()})
    return pd.DataFrame(rows)


def by_target(hl: pd.DataFrame) -> pd.DataFrame:
    pairs=[("FH_A_HEALTHY_BREADTH","FH_A_INCLUSIVE","A"),("FH_B_NET_BREADTH","FH_B_INCLUSIVE","B"),("FH_C_CONTINUOUS","FH_C_INCLUSIVE","C")]
    rows=[]
    for ex,inc,label in pairs:
        q=hl[(hl.horizon==20)&(hl.outcome=="top")]
        for sample in SAMPLES:
            for target in sorted(q.target.unique()):
                a=q[(q.metric==ex)&(q.sample==sample)&(q.target==target)]
                b=q[(q.metric==inc)&(q.sample==sample)&(q.target==target)]
                m=a.merge(b,on=["sample","universe","target","horizon","outcome"],suffixes=("_ex","_inc"))
                if m.empty: continue
                rows.append({"family":label,"sample":sample,"target":target,"n":len(m),
                             "ex_median_hl":m.high_minus_low_ex.median(),"inc_median_hl":m.high_minus_low_inc.median(),
                             "delta":(m.high_minus_low_inc-m.high_minus_low_ex).median()})
    return pd.DataFrame(rows)


def write_summary(agg: pd.DataFrame, bt: pd.DataFrame, ps: pd.DataFrame) -> str:
    lines=["# Factor Health: ex-target vs target-inclusive comparison","",
           "All HIGH/LOW bins use TRAIN-frozen terciles for an apples-to-apples comparison. Primary lens: future +20D preferred-leg return.","",
           "Inclusive identities:","- A_inc=(3*A_ex + 1[target W+])/4","- B_inc=(3*B_ex + 1[target W+] - 1[target R-])/4","- C_inc=(3*C_ex + target continuous health)/4","",
           "Thus any incremental predictive power from inclusive health necessarily comes from the target's own current state/health.","",
           "## Aggregate comparison across universe x target","",
           "| Definition | Sample | Ex median H-L | Inclusive median H-L | Δ median | Ex + share | Inc + share | Inc better |","|---|---|---:|---:|---:|---:|---:|---:|"]
    for _,r in agg.iterrows():
        lines.append(f"| {r.family} | {r['sample']} | {r.ex_median_hl:+.2%} | {r.inc_median_hl:+.2%} | {r.inc_minus_ex_median:+.2%} | {r.ex_positive_share:.0%} | {r.inc_positive_share:.0%} | {r.inc_better_share:.0%} |")
    lines += ["","## Median H-L by target","","| Def | Sample | Target | Ex | Inclusive | Δ |","|---|---|---|---:|---:|---:|"]
    for _,r in bt.iterrows():
        if r['sample'] in ("TRAIN_2017_2022","POST_2023_PLUS","POST_2023_2024","BULL_2025","YTD_2026"):
            lines.append(f"| {r.family} | {r['sample']} | {r.target} | {r.ex_median_hl:+.2%} | {r.inc_median_hl:+.2%} | {r.delta:+.2%} |")
    lines += ["","## Own-state incremental regression","",
              "Regression within each universe/target: future top20 ~ standardized ex-target health + standardized own-state component. Below are medians across cells.","",
              "| Def | Sample | Ex beta/1sd | Own beta/1sd | Own beta positive share |","|---|---|---:|---:|---:|"]
    for (fam,sample),g in ps.groupby(["family","sample"]):
        lines.append(f"| {fam} | {sample} | {g.ex_beta_per_1sd.median():+.2%} | {g.self_beta_per_1sd.median():+.2%} | {(g.self_beta_per_1sd>0).mean():.0%} |")
    return "\n".join(lines)+"\n"


def main():
    x=pd.read_csv(IN); x["date"]=pd.to_datetime(x.date)
    x=add_inclusive(x)
    metrics=["FH_A_HEALTHY_BREADTH","FH_A_INCLUSIVE","FH_B_NET_BREADTH","FH_B_INCLUSIVE","FH_C_CONTINUOUS","FH_C_INCLUSIVE"]
    cuts=freeze_terciles(x,metrics)
    hl=run_hl(x,metrics,cuts)
    ps=partial_self(x)
    agg=aggregate_compare(hl)
    bt=by_target(hl)
    x.to_csv(OUT/"inclusive_health_panel.csv",index=False,encoding="utf-8-sig")
    hl.to_csv(OUT/"high_low_comparison.csv",index=False,encoding="utf-8-sig")
    ps.to_csv(OUT/"own_state_incremental.csv",index=False,encoding="utf-8-sig")
    agg.to_csv(OUT/"aggregate_comparison.csv",index=False,encoding="utf-8-sig")
    bt.to_csv(OUT/"by_target_comparison.csv",index=False,encoding="utf-8-sig")
    (OUT/"RESEARCH_SUMMARY.md").write_text(write_summary(agg,bt,ps),encoding="utf-8")
    print(f"done hl={len(hl)} partial={len(ps)} aggregate={len(agg)}",flush=True)

if __name__=="__main__": main()
