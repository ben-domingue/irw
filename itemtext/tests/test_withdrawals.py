"""itemtext/withdrawals.csv, the table-keyed withdrawal record (#2155).

Two things are checked. The ledger helper writes the shape the file promises
and refuses rows that would not say why a table left. And every withdrawal
script in tools/withdrawals/ has its rows in the committed ledger, so a new
withdrawal cannot merge while leaving nothing keyed by its tables' names.
Offline: nothing here imports redivis or runs a script.
"""

import csv
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SRC / "tools" / "withdrawals"))

import ledger  # noqa: E402

LEDGER = SRC / "itemtext" / "withdrawals.csv"
SCRIPTS = SRC / "tools" / "withdrawals"


class Helper(unittest.TestCase):
    def setUp(self):
        self.path = Path(self.enterContext(tempfile.TemporaryDirectory())) / "w.csv"

    def read(self):
        with self.path.open(newline="") as fh:
            return list(csv.DictReader(fh))

    def test_appends_one_row_per_table(self):
        ledger.record({"b__items", "a__items"}, dataset="irw_text", reason="rights",
                      family="PSS", refs="#1955", rows={"a__items": 40},
                      when="2026-09-27", path=self.path)
        ledger.record(["c"], dataset="item_response_warehouse_2", reason="duplicate",
                      when="2026-09-28", path=self.path)
        rows = self.read()
        self.assertEqual([r["table"] for r in rows], ["a__items", "b__items", "c"])
        self.assertEqual(rows[0]["rows"], "40")
        self.assertEqual(rows[1]["rows"], "")
        self.assertEqual(rows[0]["released"], "")
        self.assertEqual(list(rows[0]), ledger.COLUMNS)

    def test_refuses_rows_that_do_not_say_why(self):
        with self.assertRaises(ValueError):
            ledger.record(["x"], dataset="d", reason="because", path=self.path)
        with self.assertRaises(ValueError):
            ledger.record(["x"], dataset="d", reason="rights", path=self.path)
        with self.assertRaises(ValueError):
            ledger.record(["x"], dataset="d", reason="duplicate", kind="some",
                          path=self.path)
        self.assertFalse(self.path.exists())

    def test_script_path_is_recorded_repo_relative(self):
        ledger.record(["x"], dataset="d", reason="duplicate",
                      script=str(SCRIPTS / "withdraw_example.py"), path=self.path)
        self.assertEqual(self.read()[0]["script"],
                         "tools/withdrawals/withdraw_example.py")


class CommittedLedger(unittest.TestCase):
    def setUp(self):
        with LEDGER.open(newline="") as fh:
            self.rows = list(csv.DictReader(fh))

    def test_header(self):
        with LEDGER.open(newline="") as fh:
            self.assertEqual(next(csv.reader(fh)), ledger.COLUMNS)

    def test_every_row_says_why(self):
        for r in self.rows:
            with self.subTest(table=r["table"]):
                self.assertIn(r["reason"], ledger.REASONS)
                self.assertIn(r["kind"], ledger.KINDS)
                self.assertTrue(r["table"].strip())
                if r["reason"] == "rights":
                    self.assertTrue(r["family"], "a rights row names its register family")

    def test_every_withdrawal_script_has_rows(self):
        cited = {r["script"] for r in self.rows}
        for p in sorted(SCRIPTS.glob("*.py")):
            if p.name == "ledger.py":
                continue
            with self.subTest(script=p.name):
                self.assertIn(f"tools/withdrawals/{p.name}", cited,
                              "add this script's tables to itemtext/withdrawals.csv "
                              "(ledger.record), so each is findable by name")

    def test_rights_families_exist_in_the_register(self):
        with (SRC / "itemtext" / "instrument_rights_register.csv").open(newline="") as fh:
            families = {r["family"] for r in csv.DictReader(fh)}
        for r in self.rows:
            if r["reason"] == "rights":
                with self.subTest(table=r["table"]):
                    self.assertIn(r["family"], families)


if __name__ == "__main__":
    unittest.main()
