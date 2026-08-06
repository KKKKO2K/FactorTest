from pathlib import Path

path = Path(__file__).with_name("k200_off_engine_lab.py")
source = path.read_text(encoding="utf-8")
source = source.replace('t=off[off.sample=="train"].copy()', 't=off[off["sample"]=="train"].copy()')
ns = {"__name__": "__main__", "__file__": str(path)}
exec(compile(source, str(path), "exec"), ns)
