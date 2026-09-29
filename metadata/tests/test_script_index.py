"""Unit tests for metadata/13_script_index.py (#2494).

The three tables in the issue are the fixtures: two battery scripts named for
something other than the table they write, and a table renamed after its
script was written. Run as a script, like test_config_parity.py:
    python metadata/tests/test_script_index.py -v
"""

import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("script_index", HERE.parent / "13_script_index.py")
si = importlib.util.module_from_spec(spec)
spec.loader.exec_module(si)

SCRIPTS = {
    "data/liem_2024_env_stewardship.py": (
        "# NOTE (liem_2024_attitude_env): even items reversed.\n"
        "BLOCKS = {\n"
        '    "liem_2024_attitude_env": [f"ATE{i}" for i in range(1, 16)],\n'
        "}\n"
    ),
    "data/dopmeijer_2022_burnout_battery.py": (
        '    "dopmeijer_2022_loneliness": (cols, MAP_LON),\n'
    ),
    "data/weida_2020_financial_security.py": (
        "# Shipped as weida_2020_financial_security until #2198.\n"
        'OUT_NAME = "weida_2020_cesd10"\n'
    ),
    "data/alpha_depression.py": 'df.to_csv("alpha_depression.csv")\n',
    "data/notes_only.do": "* see also other_table for the follow-up wave\n",
    "data/two.R": 'write.csv(x, "shared_table.csv")\n',
    "data/three.py": 'NAME = "shared_table"\n',
}
TABLES = [
    "liem_2024_attitude_env",
    "dopmeijer_2022_loneliness",
    "weida_2020_cesd10",
    "alpha_depression",
    "other_table",
    "shared_table",
]


class ScriptIndexTest(unittest.TestCase):
    def setUp(self):
        self.index = si.build_index(TABLES, SCRIPTS)

    def test_the_three_tables_in_2494_are_mapped(self):
        self.assertEqual(self.index["liem_2024_attitude_env"], ["data/liem_2024_env_stewardship.py"])
        self.assertEqual(self.index["dopmeijer_2022_loneliness"], ["data/dopmeijer_2022_burnout_battery.py"])
        self.assertEqual(self.index["weida_2020_cesd10"], ["data/weida_2020_financial_security.py"])

    def test_exact_stem_matches_are_left_to_the_mcp(self):
        self.assertNotIn("alpha_depression", self.index)

    def test_a_comment_mention_does_not_count(self):
        self.assertNotIn("other_table", self.index)

    def test_every_script_naming_a_table_is_kept(self):
        self.assertEqual(self.index["shared_table"], ["data/three.py", "data/two.R"])

    def test_straggler_tables_are_catalogued(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp)
            (md / "metadata.csv").write_text("table,n\r\nliem_2024_attitude_env,1\r\n", encoding="utf-8")
            (md / "straggler_watch.tsv").write_text(
                "table\tfirst_seen\tlast_seen\tcycles\nweida_2020_cesd10\tx\ty\t1\n", encoding="utf-8")
            self.assertEqual(si.catalogued_tables(md), {"liem_2024_attitude_env", "weida_2020_cesd10"})


    def test_manual_rows_keep_only_tracked_scripts(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "table_scripts_manual.csv"
            f.write_text(
                "table,scripts\n"
                "himmelstein-number_series-2025,data/data_number_series.py\n"
                "gone_table,data/renamed_away.py\n",
                encoding="utf-8")
            manual = si.read_manual(f, ["data/data_number_series.py"])
        # A hyphenated, run-time-built name the token scan can never see (#2529).
        self.assertEqual(manual, {"himmelstein-number_series-2025": ["data/data_number_series.py"]})

    def test_missing_manual_file_is_empty(self):
        self.assertEqual(si.read_manual(Path("/nonexistent/x.csv"), []), {})

if __name__ == "__main__":
    unittest.main()
