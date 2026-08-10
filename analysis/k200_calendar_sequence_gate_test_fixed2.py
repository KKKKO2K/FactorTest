from pathlib import Path
import numpy as np
import pandas as pd

base_path = Path(__file__).resolve().parent / "k200_calendar_sequence_gate_test.py"
source = base_path.read_text(encoding="utf-8")
source = source.replace('summary[summary.sample == "test"]', 'summary[summary["sample"] == "test"]')
ns = {"__name__": "k200_calendar_sequence_gate_module", "__file__": str(base_path)}
exec(compile(source, str(base_path), "exec"), ns)

lab = ns["lab"]
START, END, STEP = ns["START"], ns["END"], ns["STEP"]


def build_true_calendar_panel(returns, basic_panels):
    trading = returns.loc[(returns.index >= START) & (returns.index <= END)].index
    schedule = list(trading[::STEP])
    available = sorted(pd.Timestamp(x) for x in basic_panels if pd.Timestamp(x) <= END)
    available_np = np.array(available, dtype="datetime64[ns]")
    asof_map = {}
    for dt in schedule:
        pos = np.searchsorted(available_np, np.datetime64(dt), side="right") - 1
        if pos >= 0:
            asof_map[pd.Timestamp(dt)] = available[int(pos)]
    scheduled_panels = {dt: basic_panels[eff] for dt, eff in asof_map.items()}

    glb = lab.build_panel.__globals__
    original_raw = glb["raw_snapshot"]
    original_step = glb["STEP"]
    original_start = glb["START"]
    original_end = glb["END"]

    def raw_scheduled(dt, universe, returns_, _scheduled, factor_cache):
        eff = asof_map[pd.Timestamp(dt)]
        f = original_raw(eff, universe, returns_, basic_panels, factor_cache)
        q = f.reset_index()
        q["date"] = pd.Timestamp(dt)
        return q.set_index(["date", "code"])

    try:
        glb["raw_snapshot"] = raw_scheduled
        glb["STEP"] = 1
        glb["START"] = START
        glb["END"] = END
        panel = lab.build_panel("K200", returns, scheduled_panels)
    finally:
        glb["raw_snapshot"] = original_raw
        glb["STEP"] = original_step
        glb["START"] = original_start
        glb["END"] = original_end

    schedule_map = pd.DataFrame([
        {
            "scheduled_date": dt,
            "factor_snapshot_date": eff,
            "calendar_day_staleness": int((dt - eff).days),
            "exact_snapshot": bool(dt == eff),
        }
        for dt, eff in asof_map.items()
    ])
    return panel, scheduled_panels, schedule_map


ns["build_true_calendar_panel"] = build_true_calendar_panel
ns["main"]()
