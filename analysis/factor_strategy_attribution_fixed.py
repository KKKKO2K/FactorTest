from pathlib import Path

path = Path(__file__).with_name("factor_strategy_attribution.py")
source = path.read_text(encoding="utf-8")
old = '''spec = importlib.util.spec_from_file_location("lab", HERE / "factor_rotation_event_lab.py")
lab = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(lab)
base = lab.base
'''
new = '''import types
lab_path = HERE / "factor_rotation_event_lab.py"
lab_source = lab_path.read_text(encoding="utf-8")
old_event = """    p[\\"event_score\\"] = event_scores.max(axis=1, skipna=True)\n    p[\\"event_type\\"] = event_scores.idxmax(axis=1, skipna=True)\n    p[\\"event_any\\"] = event_scores.notna().any(axis=1)\n"""
new_event = """    p[\\"event_score\\"] = event_scores.max(axis=1, skipna=True)\n    p[\\"event_any\\"] = event_scores.notna().any(axis=1)\n    p[\\"event_type\\"] = pd.Series(index=p.index, dtype=\\"object\\")\n    valid_event = p[\\"event_any\\"]\n    p.loc[valid_event, \\"event_type\\"] = event_scores.loc[valid_event].idxmax(axis=1)\n"""
if old_event not in lab_source:
    raise RuntimeError("Expected event-score block not found")
lab_source = lab_source.replace(old_event, new_event)
lab_ns = {"__name__": "factor_rotation_event_lab_imported", "__file__": str(lab_path)}
exec(compile(lab_source, str(lab_path), "exec"), lab_ns)
lab = types.SimpleNamespace(**lab_ns)
base = lab.base
'''
if old not in source:
    raise RuntimeError("Expected attribution import block not found")
source = source.replace(old, new)
ns = {"__name__": "__main__", "__file__": str(path)}
exec(compile(source, str(path), "exec"), ns)
