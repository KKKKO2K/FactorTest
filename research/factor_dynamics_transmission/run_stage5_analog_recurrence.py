from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"research/factor_regime_v1/results/factor_5d_returns.csv"
OUT=Path(__file__).resolve().parent/"results_stage5_analog_recurrence"
OUT.mkdir(parents=True,exist_ok=True)
FACTORS=["MOM1M","MOM12_1","OP12_REV","OPFY1_REV","PBR12MF","PER12MF","PRIVATE_FLOW","FOREIGN_FLOW"]
PRIMITIVES=["K200","KOSPI_EX_K200","KOSDAQ"]
REPS=["SNAPSHOT","PATH20"]
K=10
PERIODS=["VAL_2020_2022","CONF_2023_2024","STRESS_2025","STRESS_2026"]


def period_of(dt):
    y=pd.Timestamp(dt).year
    if y<=2019:return "DISC_2016_2019"
    if y<=2022:return "VAL_2020_2022"
    if y<=2024:return "CONF_2023_2024"
    if y==2025:return "STRESS_2025"
    return "STRESS_2026"


def rank_ic(a,b):
    a=pd.Series(a);b=pd.Series(b)
    if a.nunique()<2 or b.nunique()<2:return np.nan
    return float(a.rank().corr(b.rank()))


def relative(v):
    v=np.asarray(v,float);return v-np.mean(v)


def unit(v):
    v=np.asarray(v,float);n=np.linalg.norm(v)
    return v/n if n>0 else np.zeros_like(v)


def load_tape():
    f=pd.read_csv(SRC);f["date"]=pd.to_datetime(f.date)
    f=f[f.factor.isin(FACTORS)&f.universe.isin(PRIMITIVES)].copy();f["ls_return"]=pd.to_numeric(f.ls_return,errors="coerce")
    f=f.dropna(subset=["date","factor","universe","ls_return"])
    s=f[f.date.dt.year<=2019].groupby(["factor","universe"]).ls_return.agg(["mean","std"]).reset_index();s["std"]=s["std"].replace(0,np.nan)
    f=f.merge(s,on=["factor","universe"],how="left");f["z"]=(f.ls_return-f["mean"])/f["std"]
    w=f.pivot_table(index="date",columns=["factor","universe"],values="z").sort_index();t=pd.DataFrame(index=w.index)
    for fac in FACTORS:t[fac]=w[[(fac,u) for u in PRIMITIVES]].mean(axis=1)
    return t.dropna(how="any")


def make_states(tape):
    X=tape[FACTORS].to_numpy(float);dates=list(tape.index);snap=np.vstack([unit(relative(v)) for v in X]);rel=np.vstack([relative(v) for v in X])
    rows=[]
    for i in range(3,len(tape)-1):
        td=dates[i+1]
        if period_of(dates[i])!=period_of(td) and pd.Timestamp(td).year>2019:continue
        path=unit(snap[i-3:i+1].reshape(-1))
        rows.append({"i":i,"date":dates[i],"target_date":td,"period":period_of(td),"snapshot":snap[i],"path20":path,"target":rel[i+1],"current_rel":rel[i]})
    return rows


def library_and_queries(states):
    lib=[r for r in states if r["period"]=="DISC_2016_2019"]
    qry=[r for r in states if r["period"]!="DISC_2016_2019"]
    return lib,qry


def state_matrix(lib,rep):
    key="snapshot" if rep=="SNAPSHOT" else "path20"
    return np.vstack([r[key] for r in lib])


def neighbors(libX,qv):
    sims=libX@qv
    return np.argsort(sims)[-K:][::-1],np.sort(sims)[-K:][::-1]


def top2_overlap(p,y):
    a=set(np.argsort(p)[-2:]);b=set(np.argsort(y)[-2:]);return len(a&b)/2


def evaluate(lib,qry):
    ylib=np.vstack([r["target"] for r in lib]);uncond=ylib.mean(axis=0);rows=[];cache={}
    for rep in REPS:
        libX=state_matrix(lib,rep);key="snapshot" if rep=="SNAPSHOT" else "path20"
        for qi,r in enumerate(qry):
            idx,sims=neighbors(libX,r[key]);pred=ylib[idx].mean(axis=0);y=r["target"];pers=r["current_rel"]
            rows.append({"representation":rep,"query_id":qi,"date":r["date"],"target_date":r["target_date"],"period":r["period"],
                         "analog_rank_ic":rank_ic(pred,y),"unconditional_rank_ic":rank_ic(uncond,y),"persistence_rank_ic":rank_ic(pers,y),
                         "analog_mse":float(np.mean((pred-y)**2)),"unconditional_mse":float(np.mean((uncond-y)**2)),"persistence_mse":float(np.mean((pers-y)**2)),
                         "analog_top2_overlap":top2_overlap(pred,y),"unconditional_top2_overlap":top2_overlap(uncond,y),"persistence_top2_overlap":top2_overlap(pers,y),
                         "mean_neighbor_similarity":float(np.mean(sims)),"max_neighbor_similarity":float(np.max(sims))})
            cache[(rep,qi)] = idx
    return pd.DataFrame(rows),cache,ylib,uncond


def summarize(rows):
    out=[]
    for (rep,p),g in rows.groupby(["representation","period"]):
        out.append({"representation":rep,"period":p,"n":len(g),
                    "median_analog_rank_ic":float(g.analog_rank_ic.median()),"median_unconditional_rank_ic":float(g.unconditional_rank_ic.median()),"median_persistence_rank_ic":float(g.persistence_rank_ic.median()),
                    "mean_analog_mse":float(g.analog_mse.mean()),"mean_unconditional_mse":float(g.unconditional_mse.mean()),"mean_persistence_mse":float(g.persistence_mse.mean()),
                    "mean_analog_top2_overlap":float(g.analog_top2_overlap.mean()),"mean_unconditional_top2_overlap":float(g.unconditional_top2_overlap.mean()),"mean_persistence_top2_overlap":float(g.persistence_top2_overlap.mean()),
                    "median_neighbor_similarity":float(g.mean_neighbor_similarity.median())})
    return pd.DataFrame(out)


def placebo(lib,qry,cache,ylib):
    rows=[];N=len(lib)
    for rep in REPS:
        for p in PERIODS:
            qs=[(qi,r) for qi,r in enumerate(qry) if r["period"]==p]
            if not qs:continue
            obs=[]
            for qi,r in qs:
                idx=cache[(rep,qi)];obs.append(rank_ic(ylib[idx].mean(axis=0),r["target"]))
            obs_med=float(np.nanmedian(obs));null=[]
            for shift in range(1,N):
                vals=[]
                for qi,r in qs:
                    idx=cache[(rep,qi)];shift_idx=(idx+shift)%N;vals.append(rank_ic(ylib[shift_idx].mean(axis=0),r["target"]))
                null.append(float(np.nanmedian(vals)))
            null=np.array([v for v in null if np.isfinite(v)])
            rows.append({"representation":rep,"period":p,"observed_median_rank_ic":obs_med,"n_placebo_shifts":len(null),
                         "placebo_p":float((1+np.sum(null>=obs_med))/(1+len(null))) if len(null) else np.nan,
                         "observed_percentile":float(np.mean(null<obs_med)) if len(null) else np.nan,"placebo_q90":float(np.quantile(null,.9)) if len(null) else np.nan,"placebo_median":float(np.median(null)) if len(null) else np.nan})
    return pd.DataFrame(rows)


def classify(summary,pl):
    rows=[]
    for rep in REPS:
        s=summary[summary.representation.eq(rep)].set_index("period");p=pl[pl.representation.eq(rep)].set_index("period")
        try:
            gates=[]
            for era in ["VAL_2020_2022","CONF_2023_2024"]:
                r=s.loc[era]
                gates.append(r.mean_analog_mse<r.mean_unconditional_mse and r.mean_analog_mse<r.mean_persistence_mse and r.median_analog_rank_ic>r.median_unconditional_rank_ic and r.median_analog_rank_ic>r.median_persistence_rank_ic)
            primary=bool(all(gates));placebo_ok=bool(p.loc["VAL_2020_2022","placebo_p"]<=.10 and p.loc["CONF_2023_2024","placebo_p"]<=.10)
        except KeyError:
            primary=False;placebo_ok=False
        status="ROBUST_RECURRENT" if primary and placebo_ok else ("WEAK_RECURRENT" if primary else "NO_RECURRENCE")
        rows.append({"representation":rep,"status":status,"primary_gate":primary,"placebo_gate":placebo_ok})
    return pd.DataFrame(rows)


def report(summary,pl,cls):
    L=["# Stage 5 — Recurrent Factor Configurations / Analog Forecasting","",f"- Discovery analog library: 2016-2019 only",f"- Fixed neighbors: k={K}",""]
    for rep in REPS:
        c=cls[cls.representation.eq(rep)].iloc[0];L += [f"## {rep}: {c.status}",f"- Primary gate: {bool(c.primary_gate)}; placebo gate: {bool(c.placebo_gate)}"]
        for era in PERIODS:
            q=summary[(summary.representation.eq(rep))&summary.period.eq(era)]
            if q.empty:continue
            r=q.iloc[0];pv=pl[(pl.representation.eq(rep))&pl.period.eq(era)].iloc[0]
            L.append(f"- {era}: rank IC analog {r.median_analog_rank_ic:+.3f} vs unconditional {r.median_unconditional_rank_ic:+.3f} vs persistence {r.median_persistence_rank_ic:+.3f}; MSE {r.mean_analog_mse:.3f} vs {r.mean_unconditional_mse:.3f}/{r.mean_persistence_mse:.3f}; top2 {r.mean_analog_top2_overlap:.1%}; neighbor sim {r.median_neighbor_similarity:.3f}; placebo p={pv.placebo_p:.3f}")
        L.append("")
    robust=cls[cls.status.eq("ROBUST_RECURRENT")]
    L += ["## Decision",""]
    if len(robust):L.append("At least one recurrent-state representation survives. The factor panel contains local nonlinear temporal structure missed by linear regime/lead-lag tests. Next step should falsify only that fixed representation at alternative horizons before any allocation test.")
    elif (cls.status.eq("WEAK_RECURRENT")).any():L.append("Analog structure improves the baselines in both historical evaluation eras but does not survive the outcome-association placebo. Treat recurrence as suggestive, not a trading signal.")
    else:L.append("Neither snapshot nor 20D-path analog forecasting beats simple baselines robustly. The tested return-only panel has strong contemporaneous geometry but little stable temporal predictability even under a local nonlinear recurrence method.")
    return "\n".join(L)


def main():
    tape=load_tape();states=make_states(tape);lib,qry=library_and_queries(states);rows,cache,ylib,uncond=evaluate(lib,qry);summ=summarize(rows);pl=placebo(lib,qry,cache,ylib);cls=classify(summ,pl);text=report(summ,pl,cls)
    tape.to_csv(OUT/"primitive_common_factor_tape.csv",encoding="utf-8-sig");rows.to_csv(OUT/"analog_date_metrics.csv",index=False,encoding="utf-8-sig");summ.to_csv(OUT/"analog_period_summary.csv",index=False,encoding="utf-8-sig");pl.to_csv(OUT/"analog_outcome_placebo.csv",index=False,encoding="utf-8-sig");cls.to_csv(OUT/"analog_classification.csv",index=False,encoding="utf-8-sig");(OUT/"RESEARCH_SUMMARY.md").write_text(text,encoding="utf-8");print(text)

if __name__=="__main__":main()
