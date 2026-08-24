from __future__ import annotations

from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "research/factor_regime_v1/results/factor_5d_returns.csv"
OUT = Path(__file__).resolve().parent / "results_stage4_pairwise_relative_value"
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = ["MOM1M", "MOM12_1", "OP12_REV", "OPFY1_REV", "PBR12MF", "PER12MF", "PRIVATE_FLOW", "FOREIGN_FLOW"]
PRIMITIVES = ["K200", "KOSPI_EX_K200", "KOSDAQ"]
SPECS = ["TRAIL20", "DISLOCATION"]
EVAL = ["VAL_2020_2022", "CONF_2023_2024", "STRESS_2025", "STRESS_2026"]


def period_of(dt):
    y = pd.Timestamp(dt).year
    if y <= 2019: return "DISC_2016_2019"
    if y <= 2022: return "VAL_2020_2022"
    if y <= 2024: return "CONF_2023_2024"
    if y == 2025: return "STRESS_2025"
    return "STRESS_2026"


def ols(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 12: return np.array([np.nan, np.nan])
    X = np.column_stack([np.ones(ok.sum()), x[ok]])
    return np.linalg.lstsq(X, y[ok], rcond=None)[0]


def mse(y, p):
    y = np.asarray(y,float); p=np.asarray(p,float)
    ok=np.isfinite(y)&np.isfinite(p)
    return float(np.mean((y[ok]-p[ok])**2)) if ok.sum()>=6 else np.nan


def load_tape():
    f=pd.read_csv(SRC); f["date"]=pd.to_datetime(f.date)
    f=f[f.factor.isin(FACTORS)&f.universe.isin(PRIMITIVES)].copy()
    f["ls_return"]=pd.to_numeric(f.ls_return,errors="coerce")
    f=f.dropna(subset=["date","factor","universe","ls_return"])
    s=f[f.date.dt.year<=2019].groupby(["factor","universe"]).ls_return.agg(["mean","std"]).reset_index()
    s["std"]=s["std"].replace(0,np.nan)
    f=f.merge(s,on=["factor","universe"],how="left")
    f["z"]=(f.ls_return-f["mean"])/f["std"]
    w=f.pivot_table(index="date",columns=["factor","universe"],values="z").sort_index()
    tape=pd.DataFrame(index=w.index)
    for fac in FACTORS:
        cols=[(fac,u) for u in PRIMITIVES]
        tape[fac]=w[cols].mean(axis=1)
    return tape.dropna(how="any")


def pair_rows(tape,a,b):
    d=(tape[a]-tape[b]).to_numpy(float); dates=list(tape.index); rows=[]
    for i in range(11,len(tape)-4):
        target_dates=dates[i+1:i+5]
        if period_of(target_dates[0])!=period_of(target_dates[-1]): continue
        trail20=float(d[i-3:i+1].sum()); trail60=float(d[i-11:i+1].sum())
        rows.append({"date":dates[i],"target_date":target_dates[0],"period":period_of(target_dates[0]),
                     "trail20":trail20,"dislocation":trail20-trail60/3.0,"fwd20":float(d[i+1:i+5].sum())})
    return pd.DataFrame(rows)


def evaluate(tape):
    rows=[]; caches={}; stabs=[]
    for a,b in combinations(FACTORS,2):
        q=pair_rows(tape,a,b)
        for spec in SPECS:
            col="trail20" if spec=="TRAIL20" else "dislocation"
            tr=q[q.period.eq("DISC_2016_2019")]
            beta=ols(tr[col],tr.fwd20); const_mean=float(tr.fwd20.mean())
            caches[(a,b,spec)]=(q,beta,const_mean)
            vals={}
            for label,yrs in [("2016_17",(2016,2017)),("2018_19",(2018,2019))]:
                z=tr[tr.target_date.dt.year.between(*yrs)]
                vals[label]=float(ols(z[col],z.fwd20)[1])
            stabs.append({"factor_a":a,"factor_b":b,"spec":spec,"beta_discovery":float(beta[1]),
                          "beta_2016_17":vals["2016_17"],"beta_2018_19":vals["2018_19"],
                          "same_sign":bool(np.sign(vals["2016_17"])==np.sign(vals["2018_19"]))})
            for p in ["DISC_2016_2019"]+EVAL:
                z=q[q.period.eq(p)]
                if len(z)<6: continue
                pred=beta[0]+beta[1]*z[col].to_numpy(float); base=np.repeat(const_mean,len(z))
                mb=mse(z.fwd20,base); mm=mse(z.fwd20,pred)
                rows.append({"factor_a":a,"factor_b":b,"spec":spec,"period":p,"n":len(z),
                             "beta_discovery":float(beta[1]),"incremental_oos_r2":1-mm/mb if mb>0 else np.nan})
    return pd.DataFrame(rows),pd.DataFrame(stabs),caches


def placebo(caches):
    rows=[]
    for (a,b,spec),(q,beta,const_mean) in caches.items():
        col="trail20" if spec=="TRAIL20" else "dislocation"
        for p in EVAL:
            z=q[q.period.eq(p)].reset_index(drop=True)
            if len(z)<8: continue
            base=np.repeat(const_mean,len(z)); mb=mse(z.fwd20,base)
            obs=1-mse(z.fwd20,beta[0]+beta[1]*z[col].to_numpy(float))/mb if mb>0 else np.nan
            x=z[col].to_numpy(float); null=[]
            for k in range(1,len(z)):
                xs=np.roll(x,k); null.append(1-mse(z.fwd20,beta[0]+beta[1]*xs)/mb if mb>0 else np.nan)
            null=np.array([v for v in null if np.isfinite(v)])
            rows.append({"factor_a":a,"factor_b":b,"spec":spec,"period":p,"observed_r2":obs,
                         "placebo_p":float((1+np.sum(null>=obs))/(1+len(null))) if len(null) else np.nan,
                         "observed_percentile":float(np.mean(null<obs)) if len(null) else np.nan,
                         "placebo_q90":float(np.quantile(null,.9)) if len(null) else np.nan})
    return pd.DataFrame(rows)


def classify(results,stabs,pl):
    rr=results.set_index(["factor_a","factor_b","spec","period"]); ss=stabs.set_index(["factor_a","factor_b","spec"]); pp=pl.set_index(["factor_a","factor_b","spec","period"])
    rows=[]
    for a,b in combinations(FACTORS,2):
        for spec in SPECS:
            try:
                val=float(rr.loc[(a,b,spec,"VAL_2020_2022"),"incremental_oos_r2"]); conf=float(rr.loc[(a,b,spec,"CONF_2023_2024"),"incremental_oos_r2"])
                beta=float(ss.loc[(a,b,spec),"beta_discovery"]); stable=bool(ss.loc[(a,b,spec),"same_sign"])
                pv=float(pp.loc[(a,b,spec,"VAL_2020_2022"),"placebo_p"]); pc=float(pp.loc[(a,b,spec,"CONF_2023_2024"),"placebo_p"])
            except KeyError: continue
            passed=bool(val>0 and conf>0 and stable and pv<=.10 and pc<=.10)
            if spec=="TRAIL20": mechanism="CONTINUATION" if beta>0 else "REVERSAL"
            else: mechanism="ACCELERATION" if beta>0 else "MEAN_REVERSION"
            rows.append({"factor_a":a,"factor_b":b,"spec":spec,"status":"PASS" if passed else "FAIL","mechanism":mechanism,
                         "beta_discovery":beta,"coef_sign_stable":stable,"val_r2":val,"conf_r2":conf,"val_placebo_p":pv,"conf_placebo_p":pc})
    return pd.DataFrame(rows).sort_values(["status","conf_r2","val_r2"],ascending=[False,False,False]).reset_index(drop=True)


def report(cls):
    p=cls[cls.status.eq("PASS")]
    L=["# Stage 4 — Pairwise Factor Relative-Value Dynamics","",f"- PASS pair/specs: {len(p)}/56",""]
    if len(p):
        L += ["## Passing relations",""]
        for r in p.itertuples(index=False):
            L.append(f"- {r.factor_a} vs {r.factor_b} / {r.spec}: {r.mechanism}; beta {r.beta_discovery:+.3f}; VAL R2 {r.val_r2:+.4f}; CONF {r.conf_r2:+.4f}; placebo p {r.val_placebo_p:.3f}/{r.conf_placebo_p:.3f}")
        fam=pd.concat([p.factor_a,p.factor_b]).value_counts()
        L += ["","## Factor recurrence among passing relations",""]
        for fac,n in fam.items(): L.append(f"- {fac}: {int(n)} passing pair/spec appearances")
    else:
        L.append("No pair/spec survives the full validation + confirmation + sign-stability + placebo gate.")
    L += ["","## Strongest near-misses",""]
    for r in cls[cls.status.eq("FAIL")].head(12).itertuples(index=False):
        L.append(f"- {r.factor_a} vs {r.factor_b} / {r.spec}: {r.mechanism}; VAL {r.val_r2:+.4f}; CONF {r.conf_r2:+.4f}; stable={r.coef_sign_stable}; p={r.val_placebo_p:.3f}/{r.conf_placebo_p:.3f}")
    L += ["","## Decision",""]
    if len(p):
        L.append("At least one pair-specific relative-value law survives. Next step is horizon falsification on only those exact pairs before any allocation test.")
    else:
        L.append("Simple linear pairwise continuation/dislocation dynamics do not survive. Stop linear lag engineering and reserve the next stage for explicitly exploratory nonlinear/rotation geometry rather than adding more ad hoc windows.")
    return "\n".join(L)


def main():
    tape=load_tape(); results,stabs,caches=evaluate(tape); pl=placebo(caches); cls=classify(results,stabs,pl)
    tape.to_csv(OUT/"primitive_common_factor_tape.csv",encoding="utf-8-sig")
    results.to_csv(OUT/"pair_spec_oos_results.csv",index=False,encoding="utf-8-sig")
    stabs.to_csv(OUT/"pair_spec_discovery_stability.csv",index=False,encoding="utf-8-sig")
    pl.to_csv(OUT/"pair_spec_placebo.csv",index=False,encoding="utf-8-sig")
    cls.to_csv(OUT/"pair_spec_classification.csv",index=False,encoding="utf-8-sig")
    text=report(cls); (OUT/"RESEARCH_SUMMARY.md").write_text(text,encoding="utf-8"); print(text)

if __name__=="__main__": main()
