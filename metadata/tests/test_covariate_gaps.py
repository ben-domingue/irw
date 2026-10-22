"""The covariate-label gap auditor: does it see a gap, and does it stay quiet
about a table that is fine?

Why this exists at all: `cassidy_2024_*` shipped nine tables with ten coded,
fully labelled covariates under a batch log asserting no harvest was owed, and
nothing contradicted it. The harvest is a manual stage, so a script that is
never harvested produces no error, no empty file and no row anywhere -- the
gap is invisible by construction. `audit_gaps.py` makes it visible from the
committed record alone, and this pins the four things that would quietly break
it.

Offline, synthetic: every input is written into a tmp tree shaped like the
repo, so no test here reads the real 6,651-table metadata.
"""
import csv
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "metadata" / "covariate_labels" / "audit_gaps.py"


def write_csv(path: Path, rows: list[dict], fields: list[str], sep=",") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter=sep,
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


class Fixture:
    """A tmp tree with the six files audit_gaps.py reads, and nothing else."""

    def __init__(self, root: Path):
        self.root = root
        (root / "data").mkdir(parents=True, exist_ok=True)
        (root / "metadata" / "covariate_labels").mkdir(parents=True,
                                                       exist_ok=True)
        # audit_gaps.py resolves REPO from its own location, so it has to live
        # in the fixture rather than be pointed at it.
        dst = root / "metadata" / "covariate_labels" / "audit_gaps.py"
        dst.write_text(SCRIPT.read_text())
        self.script = dst

    def script_file(self, name: str, body: str) -> None:
        (self.root / "data" / name).write_text(body)

    def build(self, tables, cov_tables, scripts_for, labelled=(),
              coverage=(), empty=()):
        m = self.root / "metadata"
        write_csv(m / "metadata.csv", [{"table": t} for t in tables],
                  ["table"])
        write_csv(m / "table_scripts.csv",
                  [{"table": t, "scripts": s} for t, s in scripts_for.items()],
                  ["table", "scripts"])
        write_csv(m / "column_docs.csv",
                  [{"table": t, "column": "cov_gender"} for t in cov_tables]
                  + [{"table": t, "column": "resp"} for t in tables],
                  ["table", "column"])
        write_csv(m / "covariate_labels.csv",
                  [{"table": t, "covariate": "cov_gender", "code": "1",
                    "label": "male"} for t in labelled],
                  ["table", "covariate", "code", "label"])
        write_csv(m / "covariate_labels" / "coverage.csv", list(coverage),
                  ["table", "covariate", "script", "source_column", "status",
                   "reason", "n_codes", "n_labelled", "unlabelled_codes"])
        write_csv(m / "covariate_labels" / "harvest_empty.tsv",
                  [{"script": s, "recorded_exit": "1",
                    "in_harvest_status": "yes",
                    "why_empty": "the raw source file was not on disk",
                    "last_output_line": ""} for s in empty],
                  ["script", "recorded_exit", "in_harvest_status", "why_empty",
                   "last_output_line"], sep="\t")

    def run(self, *args):
        return subprocess.run([sys.executable, str(self.script), *args],
                              capture_output=True, text=True)

    def counts(self, *args) -> dict:
        """{class: n} parsed from the report.

        Parsed rather than string-matched: the first version of this test
        asserted on the exact column padding of the summary lines, which made
        seven tests fail on a cosmetic width and told us nothing.
        """
        import re
        out = self.run(*args).stdout
        return {m.group(1): int(m.group(2)) for m in
                re.finditer(r"^\s+(\w+)\s+(\d+) table\(s\)", out,
                            re.MULTILINE)}


SAV_PY = "import pyreadstat\nCOVS={'Gender':'cov_gender'}\n"
PLAIN_PY = "import pandas as pd\nCOVS={'Gender':'cov_gender'}\n"
SAV_R = 'library(haven)\nd <- read_sav("x.sav")\n'


class SeesAGap(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(__file__).parent / "_tmp_gaps"
        if self.tmp.exists():
            import shutil
            shutil.rmtree(self.tmp)
        self.fx = Fixture(self.tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_never_examined_is_reported(self):
        self.fx.script_file("a.py", SAV_PY)
        self.fx.build(tables=["a_1"], cov_tables=["a_1"],
                      scripts_for={"a_1": "data/a.py"})
        out = self.fx.run().stdout
        self.assertEqual(self.fx.counts()["never_examined"], 1)
        self.assertIn("a_1", out)

    def test_a_table_with_labels_is_not_reported(self):
        self.fx.script_file("a.py", SAV_PY)
        self.fx.build(tables=["a_1"], cov_tables=["a_1"],
                      scripts_for={"a_1": "data/a.py"}, labelled=["a_1"])
        self.assertEqual(self.fx.counts()["never_examined"], 0)

    def test_a_table_shipping_no_covariates_is_not_reported(self):
        # The filter that cut the first run's 902 down to 674. A table with no
        # cov_* column can never have a covariate label, and reporting it is
        # the noise that gets a check ignored.
        self.fx.script_file("a.py", SAV_PY)
        self.fx.build(tables=["a_1"], cov_tables=[],
                      scripts_for={"a_1": "data/a.py"})
        self.assertEqual(self.fx.counts()["never_examined"], 0)

    def test_a_script_that_reads_no_labelled_source_is_not_reported(self):
        self.fx.script_file("a.py", PLAIN_PY)
        self.fx.build(tables=["a_1"], cov_tables=["a_1"],
                      scripts_for={"a_1": "data/a.py"})
        self.assertEqual(self.fx.counts()["never_examined"], 0)

    def test_an_excluded_pair_is_considered_not_never_examined(self):
        # Exclusion for a RULE is recorded in coverage.csv and is fine; the
        # defect this script hunts is silence in both files.
        self.fx.script_file("a.py", SAV_PY)
        self.fx.build(tables=["a_1"], cov_tables=["a_1"],
                      scripts_for={"a_1": "data/a.py"},
                      coverage=[{"table": "a_1", "covariate": "cov_gender",
                                 "script": "data/a.py",
                                 "source_column": "Gender",
                                 "status": "excluded",
                                 "reason": "the script recoded this column",
                                 "n_codes": "2", "n_labelled": "2",
                                 "unlabelled_codes": ""}])
        c = self.fx.counts()
        self.assertEqual(c["never_examined"], 0)
        self.assertEqual(c["considered_none_kept"], 1)

    def test_an_empty_harvest_is_its_own_class(self):
        self.fx.script_file("a.py", SAV_PY)
        self.fx.build(tables=["a_1"], cov_tables=["a_1"],
                      scripts_for={"a_1": "data/a.py"}, empty=["a"])
        out = self.fx.run().stdout
        self.assertEqual(self.fx.counts()["harvest_empty"], 1)
        self.assertIn("not on disk", out)

    def test_an_r_script_is_its_own_class(self):
        # harvest.py cannot re-run R at all, so these need a manual.csv row
        # rather than a re-harvest -- a different action, hence a class.
        self.fx.script_file("a.r", SAV_R)
        self.fx.build(tables=["a_1"], cov_tables=["a_1"],
                      scripts_for={"a_1": "data/a.r"})
        out = self.fx.run().stdout
        self.assertEqual(self.fx.counts()["r_script"], 1)
        self.assertIn("manual.csv", out)


class Ratchet(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(__file__).parent / "_tmp_ratchet"
        if self.tmp.exists():
            import shutil
            shutil.rmtree(self.tmp)
        self.fx = Fixture(self.tmp)
        self.fx.script_file("a.py", SAV_PY)
        self.fx.script_file("b.py", SAV_PY)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_a_recorded_gap_passes(self):
        self.fx.build(tables=["a_1"], cov_tables=["a_1"],
                      scripts_for={"a_1": "data/a.py"})
        self.assertEqual(self.fx.run("--write").returncode, 0)
        self.assertEqual(self.fx.run("--ratchet").returncode, 0)

    def test_a_new_gap_fails(self):
        self.fx.build(tables=["a_1"], cov_tables=["a_1"],
                      scripts_for={"a_1": "data/a.py"})
        self.fx.run("--write")
        # b_1 goes live later and nobody harvested it: this is the cassidy_2024
        # shape, and it must not pass.
        self.fx.build(tables=["a_1", "b_1"], cov_tables=["a_1", "b_1"],
                      scripts_for={"a_1": "data/a.py", "b_1": "data/b.py"})
        r = self.fx.run("--ratchet")
        self.assertEqual(r.returncode, 1)
        self.assertIn("b_1", r.stderr)
        self.assertIn("newly in the covariate-label gap", r.stderr)

    def test_strict_fails_on_any_gap(self):
        self.fx.build(tables=["a_1"], cov_tables=["a_1"],
                      scripts_for={"a_1": "data/a.py"})
        self.assertEqual(self.fx.run("--strict").returncode, 1)


class StaysInSyncWithHarvest(unittest.TestCase):
    def test_the_python_reader_regex_matches_harvests(self):
        """Both files decide "reads a labelled source" and must agree.

        harvest.py picks its candidates with one regex and audit_gaps.py
        reports on the same population; if they drift, the auditor either
        reports scripts the harvest will never run or misses ones it would.
        """
        import re
        h = (REPO / "metadata" / "covariate_labels" / "harvest.py").read_text()
        a = SCRIPT.read_text()
        want = re.search(r'READS_LABELLED = re\.compile\(r"([^"]+)"\)', h)
        got = re.search(r'READS_PY = re\.compile\(r"([^"]+)"\)', a)
        self.assertIsNotNone(want, "harvest.py's READS_LABELLED moved")
        self.assertIsNotNone(got, "audit_gaps.py's READS_PY moved")
        self.assertEqual(want.group(1), got.group(1))


if __name__ == "__main__":
    unittest.main()
