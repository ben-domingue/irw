"""design_tables.csv survives a rebuild: rank_common.upsert_design keeps every column (#3330).

#3301 added `rules_jurisdiction` to data/rankings/design_tables.csv but not to
`DESIGN_COLUMNS`, so the next builder run would have dropped it from all 279 NSW rows
and test_rank_rules_join.py would have failed afterwards. These tests run the real
writer against a copy of the tracked file.

Offline. Run: python metadata/tests/test_rank_design_upsert.py -v
"""
import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RANKINGS = Path(__file__).resolve().parents[2] / "data" / "rankings"
sys.path.insert(0, str(RANKINGS))
import rank_common  # noqa: E402

NSW_KEY = "New South Wales (Legislative Assembly)"


class UpsertDesignTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.design = self.tmp / "design_tables.csv"
        shutil.copy(RANKINGS / "design_tables.csv", self.design)
        self._orig = rank_common.DESIGN
        rank_common.DESIGN = self.design
        with open(self.design, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.header = reader.fieldnames
            self.rows = list(reader)

    def tearDown(self):
        rank_common.DESIGN = self._orig
        shutil.rmtree(self.tmp)

    def _record(self, row):
        """A builder's record for an existing row: every column but the carried ones."""
        return {c: row[c] for c in rank_common.DESIGN_COLUMNS if c not in rank_common.CARRIED_COLUMNS}

    def test_columns_match_the_file(self):
        self.assertEqual(self.header, rank_common.DESIGN_COLUMNS)

    def test_noop_upsert_leaves_the_file_byte_identical(self):
        before = self.design.read_bytes()
        rank_common.upsert_design(self._record(self.rows[0]))
        self.assertEqual(self.design.read_bytes(), before)

    def test_rebuild_keeps_a_recorded_rules_key(self):
        nsw = [r for r in self.rows if r["rules_jurisdiction"] == NSW_KEY]
        self.assertEqual(len(nsw), 279)
        before = self.design.read_bytes()
        rank_common.upsert_design(self._record(nsw[0]))  # record does not set the key
        self.assertEqual(self.design.read_bytes(), before)

    def test_new_table_gets_a_blank_key(self):
        rec = self._record(self.rows[0])
        rec["table"] = "zz_test_new_table"
        rank_common.upsert_design(rec)
        with open(self.design, newline="", encoding="utf-8") as f:
            got = {r["table"]: r for r in csv.DictReader(f)}
        self.assertEqual(got["zz_test_new_table"]["rules_jurisdiction"], "")
        self.assertEqual(len(got), len(self.rows) + 1)

    def test_unknown_column_is_refused(self):
        rec = self._record(self.rows[0])
        rec["not_a_column"] = "x"
        with self.assertRaises(ValueError):
            rank_common.upsert_design(rec)

    def test_missing_required_column_is_refused(self):
        rec = self._record(self.rows[0])
        del rec["date"]
        with self.assertRaises(ValueError):
            rank_common.upsert_design(rec)


if __name__ == "__main__":
    unittest.main()
