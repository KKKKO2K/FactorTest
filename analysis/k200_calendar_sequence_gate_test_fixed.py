from pathlib import Path

base_path = Path(__file__).resolve().parent / "k200_calendar_sequence_gate_test.py"
source = base_path.read_text(encoding="utf-8")
source = source.replace('summary[summary.sample == "test"]', 'summary[summary["sample"] == "test"]')
ns = {"__name__": "__main__", "__file__": str(base_path)}
exec(compile(source, str(base_path), "exec"), ns)
