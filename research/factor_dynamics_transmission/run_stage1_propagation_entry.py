from pathlib import Path

p = Path(__file__).resolve().parent / "run_stage1_propagation.py"
source = p.read_text(encoding="utf-8")
source = source.replace(
    "for r in cls.head(8).itertuples(index=False):",
    "for _, r in cls.head(8).iterrows():",
)
source = source.replace("PASS={r.pass}", "PASS={r['pass']}")
exec(compile(source, str(p), "exec"), {"__name__": "__main__", "__file__": str(p)})
