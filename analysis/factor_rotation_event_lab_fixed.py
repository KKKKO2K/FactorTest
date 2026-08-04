from pathlib import Path

source_path = Path(__file__).with_name("factor_rotation_event_lab.py")
source = source_path.read_text(encoding="utf-8")
old = '''    p["event_score"] = event_scores.max(axis=1, skipna=True)
    p["event_type"] = event_scores.idxmax(axis=1, skipna=True)
    p["event_any"] = event_scores.notna().any(axis=1)
'''
new = '''    p["event_score"] = event_scores.max(axis=1, skipna=True)
    p["event_any"] = event_scores.notna().any(axis=1)
    p["event_type"] = pd.Series(index=p.index, dtype="object")
    valid_event = p["event_any"]
    p.loc[valid_event, "event_type"] = event_scores.loc[valid_event].idxmax(axis=1)
'''
if old not in source:
    raise RuntimeError("Expected event-score block not found")
source = source.replace(old, new)
namespace = {"__name__": "__main__", "__file__": str(source_path)}
exec(compile(source, str(source_path), "exec"), namespace)
