"""The conjoint design records (data/conjoint/design_tables.csv, design_outcomes.csv)
and the attribute crosswalk (data/conjoint/crosswalk.csv).

Offline. Checks the codes each column may hold, that keys are unique, and that
every table the ledger (data/conjoint/candidates.csv) marks built or uploaded
has a design row. Whether every outcome COLUMN of a live table has an outcome
row needs the table schema, so 16_conjoint.R reports that when it runs.

Run: python metadata/tests/test_conj_design.py -v
"""
import csv
import re
import unittest
from pathlib import Path

CONJ = Path(__file__).resolve().parents[2] / "data" / "conjoint"

TABLE_COLS = ["table", "country", "display_language", "label_language", "restrictions",
              "level_weights", "restrictions_note", "attr_order", "survey_weight", "presentation",
              "task_source", "profile_source", "evidence"]
OUTCOME_COLS = ["table", "outcome", "type", "question", "opt_out", "scale_min", "scale_max",
                "low_anchor", "high_anchor", "evidence"]
SOURCE = {"recorded", "inferred", "unknown"}
ISO_LIST = re.compile(r"^(unknown|[a-z]{2,3}(;[a-z]{2,3})*)$")
COUNTRY_LIST = re.compile(r"^(unknown|[A-Z]{2}(;[A-Z]{2})*)$")
NAME = re.compile(r"^[a-z0-9_]+")


def read(name):
    with open(CONJ / name, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def ledger_tables():
    """Tables the ledger marks built or uploaded. A cell can carry a note after the
    name ("shandler_2023_cyberterror (replaces _us/_uk/_il)"); the name is the
    leading token."""
    _, rows = read("candidates.csv")
    out = set()
    for r in rows:
        if r["status"] in ("built", "uploaded"):
            for piece in r["tables"].split(";"):
                m = NAME.match(piece.strip())
                if m:
                    out.add(m.group(0))
    return out


class TablesFile(unittest.TestCase):
    def setUp(self):
        self.cols, self.rows = read("design_tables.csv")

    def test_columns(self):
        self.assertEqual(self.cols, TABLE_COLS)

    def test_unique(self):
        names = [r["table"] for r in self.rows]
        self.assertEqual(len(names), len(set(names)))

    def test_codes(self):
        for r in self.rows:
            t = r["table"]
            self.assertRegex(r["country"], COUNTRY_LIST, t)
            self.assertRegex(r["display_language"], ISO_LIST, t)
            self.assertRegex(r["label_language"], ISO_LIST, t)
            self.assertIn(r["restrictions"], {"none", "yes", "observed", "unknown"}, t)
            self.assertIn(r["level_weights"], {"uniform", "nonuniform", "observed", "unknown"}, t)
            needs = r["restrictions"] in ("yes", "observed") or r["level_weights"] == "nonuniform"
            quiet = r["restrictions"] in ("none", "unknown") and r["level_weights"] in ("uniform", "unknown")
            if needs:
                self.assertTrue(r["restrictions_note"], f"{t}: restrictions_note gives the rule or the weights")
            if quiet:
                self.assertFalse(r["restrictions_note"], f"{t}: restrictions_note with nothing to describe")
            self.assertIn(r["attr_order"], {"fixed", "respondent", "task", "unknown"}, t)
            self.assertIn(r["survey_weight"], {"kept", "none", "not_kept", "unknown"}, t)
            self.assertIn(r["presentation"], {"grid", "text", "image", "unknown"}, t)
            self.assertIn(r["task_source"], SOURCE, t)
            self.assertIn(r["profile_source"], SOURCE, t)

    def test_ledger_covered(self):
        missing = ledger_tables() - {r["table"] for r in self.rows}
        self.assertFalse(missing, f"built/uploaded tables with no design row: {sorted(missing)}")


class OutcomesFile(unittest.TestCase):
    def setUp(self):
        self.cols, self.rows = read("design_outcomes.csv")
        _, tabs = read("design_tables.csv")
        self.tables = {r["table"] for r in tabs}

    def test_columns(self):
        self.assertEqual(self.cols, OUTCOME_COLS)

    def test_unique(self):
        keys = [(r["table"], r["outcome"]) for r in self.rows]
        self.assertEqual(len(keys), len(set(keys)))

    def test_every_table_has_outcomes(self):
        self.assertEqual({r["table"] for r in self.rows}, self.tables)

    def test_codes(self):
        for r in self.rows:
            k = f'{r["table"]}:{r["outcome"]}'
            self.assertRegex(r["outcome"], r"^(choice|rating)(_[a-z0-9_]+)?$", k)
            self.assertEqual(r["type"], r["outcome"].split("_")[0], k)
            self.assertTrue(r["question"], k)
            if r["type"] == "choice":
                self.assertIn(r["opt_out"], {"yes", "no", "unknown"}, k)
                for c in ("scale_min", "scale_max", "low_anchor", "high_anchor"):
                    self.assertEqual(r[c], "", f"{k}: {c} is for ratings")
            else:
                self.assertEqual(r["opt_out"], "", k)
                lo, hi = float(r["scale_min"]), float(r["scale_max"])
                self.assertLess(lo, hi, k)
                self.assertTrue(r["low_anchor"] and r["high_anchor"], k)


#: concept -> the harmonized values it may take. A new concept is added here
#: with its values, and documented in data/conjoint/README.md.
CONCEPTS = {"profile_gender": {"female", "male"}}
CROSSWALK_COLS = ["concept", "table", "attribute", "level", "value", "signal", "evidence"]


class CrosswalkFile(unittest.TestCase):
    def setUp(self):
        self.cols, self.rows = read("crosswalk.csv")
        _, tabs = read("design_tables.csv")
        self.tables = {r["table"] for r in tabs}

    def test_columns(self):
        self.assertEqual(self.cols, CROSSWALK_COLS)

    def test_unique(self):
        keys = [(r["concept"], r["table"], r["attribute"], r["level"]) for r in self.rows]
        self.assertEqual(len(keys), len(set(keys)))

    def test_codes(self):
        for r in self.rows:
            k = f'{r["concept"]}:{r["table"]}:{r["attribute"]}:{r["level"]}'
            self.assertIn(r["concept"], CONCEPTS, k)
            self.assertIn(r["value"], CONCEPTS[r["concept"]], k)
            self.assertIn(r["signal"], {"explicit", "name", "photo"}, k)
            self.assertTrue(r["attribute"].startswith("attr_"), k)
            self.assertTrue(r["level"] and r["evidence"], k)
            self.assertIn(r["table"], self.tables, f"{k}: table has no design record")

    def test_one_attribute_per_table_and_concept(self):
        seen = {}
        for r in self.rows:
            seen.setdefault((r["concept"], r["table"]), set()).add(r["attribute"])
        many = {k: v for k, v in seen.items() if len(v) > 1}
        self.assertFalse(many, "a concept maps to one attribute per table")

    def test_contrast_exists(self):
        """A table where every level maps to one value has no contrast to estimate."""
        vals = {}
        for r in self.rows:
            vals.setdefault((r["concept"], r["table"]), set()).add(r["value"])
        flat = sorted(k for k, v in vals.items() if len(v) < 2)
        self.assertFalse(flat, f"no contrast: {flat}")


if __name__ == "__main__":
    unittest.main()
