"""script_match.py: the coverage audit finds scripts the way the MCP does."""
import csv
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("script_match", HERE / "script_match.py")
script_match = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script_match)


def test_exact_index_prefix_none(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "metadata").mkdir()
    for name in ("smith_2020_bfi.py", "jones_2021_battery.R", "imos_2018.r"):
        (tmp_path / "data" / name).write_text("x = 1\n")
    (tmp_path / "metadata" / "table_scripts.csv").write_text(
        "table,scripts\njones_2021_cesd,data/jones_2021_battery.R\n")
    tables = tmp_path / "tables.txt"
    tables.write_text("smith_2020_bfi\njones_2021_cesd\nsmith_2020_bfi_short\nimos_1984\n")
    out = tmp_path / "out.csv"
    assert script_match.main(["--repo", str(tmp_path), "--tables", str(tables), "--out", str(out)]) == 0
    got = {r["table"]: r["match"] for r in csv.DictReader(out.open())}
    # The exact-name case is the one table_scripts.csv leaves out by design.
    assert got == {"smith_2020_bfi": "exact", "jones_2021_cesd": "index",
                   "smith_2020_bfi_short": "prefix", "imos_1984": "none"}
