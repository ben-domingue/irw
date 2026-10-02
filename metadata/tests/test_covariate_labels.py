"""Tests for metadata/covariate_labels/build.py (#1775), plus checks on the
committed metadata/covariate_labels.csv. Run as a script, like
test_config_parity.py:

    python metadata/tests/test_covariate_labels.py -v
"""
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
META = HERE.parent
spec = importlib.util.spec_from_file_location("covlab_build", META / "covariate_labels" / "build.py")
cb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cb)

SCRIPT = '''
MAP = {"GENERO": "cov_gender", "CURSO": "cov_grade", "CENTRO": "cov_school",
       "SEXO": "cov_sex", "EDU": "cov_education", "INST": "cov_hospital", "TIPO": "cov_school_type"}
'''


def read(kind_labels, counts, columns=None):
    return {"ev": "read", "kind": "read_sav", "path": "/tmp/x.sav",
            "columns": columns if columns is not None else sorted(set(kind_labels) | set(counts)),
            "value_labels": kind_labels, "counts": counts}


def cov(values, counts, basis="ids"):
    return {"dtype": "float64", "n_unique": len(values), "values": values,
            "count_basis": basis, "counts": counts}


def write(table, covs):
    return {"ev": "write", "path": f"/x/{table}.csv", "ncol": 9, "has_item": True, "covs": covs}


class BuildTest(unittest.TestCase):
    def run_build(self, events, live=("t1",), rules=()):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "data").mkdir()
            (d / "logs").mkdir()
            (d / "data" / "s.py").write_text(SCRIPT)
            with open(d / "logs" / "s.jsonl", "w") as f:
                for e in events:
                    f.write(json.dumps(e) + "\n")
            rows, record, flagged = cb.build(d / "logs", set(live), list(rules), d / "data")
        return rows, {(r["table"], r["covariate"]): r for r in record}, flagged

    def test_verbatim_labels_for_shipped_codes_only(self):
        rows, rec, _ = self.run_build([
            read({"GENERO": {"1.0": "hombre", "2.0": "mujer", "9.0": "no contesta"}},
                 {"GENERO": {"1": 10, "2": 12, "9": 1}}),
            write("t1", {"cov_gender": cov(["1", "2"], {"1": 10, "2": 11})}),
        ])
        self.assertEqual([(r["code"], r["label"]) for r in rows], [("1", "hombre"), ("2", "mujer")])
        self.assertEqual(rec[("t1", "cov_gender")]["status"], "included")

    def test_swapped_codes_are_left_out(self):
        # source 1 = 30 rows, 2 = 10 rows; the table ships 1 on 10 ids and 2 on 30: a swap
        rows, rec, _ = self.run_build([
            read({"SEXO": {"1": "male", "2": "female"}}, {"SEXO": {"1": 30, "2": 10}}),
            write("t1", {"cov_sex": cov(["1", "2"], {"1": 10, "2": 30})}),
        ])
        self.assertEqual(rows, [])
        self.assertIn("recoded", rec[("t1", "cov_sex")]["reason"])

    def test_zero_one_recode_is_left_out(self):
        rows, rec, _ = self.run_build([
            read({"SEXO": {"1": "male", "2": "female"}}, {"SEXO": {"1": 30, "2": 10}}),
            write("t1", {"cov_sex": cov(["0", "1"], {"0": 30, "1": 10})}),
        ])
        self.assertEqual(rows, [])
        self.assertEqual(rec[("t1", "cov_sex")]["status"], "excluded")

    def test_partial_coverage_recorded(self):
        rows, rec, _ = self.run_build([
            read({"EDU": {"1": "primary", "2": "secondary", "3": "tertiary"}},
                 {"EDU": {"1": 5, "2": 5, "3": 5, "4": 2}}),
            write("t1", {"cov_education": cov(["1", "2", "3", "4"], {"1": 5, "2": 5, "3": 5, "4": 2})}),
        ])
        self.assertEqual([r["code"] for r in rows], ["1", "2", "3"])
        self.assertEqual(rec[("t1", "cov_education")]["unlabelled_codes"], "4")

    def test_named_institutions_withheld(self):
        rows, rec, flagged = self.run_build(
            [read({"CENTRO": {"1": "Ceip Esteiro", "2": "Recimil"}}, {"CENTRO": {"1": 3, "2": 4}}),
             write("t1", {"cov_school": cov(["1", "2"], {"1": 3, "2": 4})})],
            rules=[{"table_pattern": "t*", "covariate": "cov_school", "decision": "withhold"}])
        self.assertEqual({r["label"] for r in rows}, {cb.WITHHELD_LABEL})
        self.assertEqual([r["code"] for r in rows], ["1", "2"])
        self.assertEqual(rec[("t1", "cov_school")]["status"], "withheld")
        self.assertEqual(flagged, [])

    def test_unreviewed_institution_withheld_and_flagged(self):
        rows, _, flagged = self.run_build([
            read({"INST": {"1": "St Mary's", "2": "General"}}, {"INST": {"1": 3, "2": 4}}),
            write("t1", {"cov_hospital": cov(["1", "2"], {"1": 3, "2": 4})}),
        ])
        self.assertEqual({r["label"] for r in rows}, {cb.WITHHELD_LABEL})
        self.assertEqual(flagged, [("t1", "cov_hospital")])

    def test_label_heuristic_flags_institution_lists(self):
        labels = {"1": "Universiti Sains Malaysia", "2": "University of Malaya", "3": "IIUM university"}
        self.assertTrue(cb.institution_flag("cov_campus_x", labels))
        self.assertTrue(cb.institution_flag("cov_uni", labels))
        self.assertFalse(cb.institution_flag("cov_education",
                                             {"1": "Primary", "2": "High school", "3": "University degree"}))

    def test_reviewed_publish_keeps_labels(self):
        rows, _, flagged = self.run_build(
            [read({"TIPO": {"1": "public", "2": "private"}}, {"TIPO": {"1": 3, "2": 4}}),
             write("t1", {"cov_school_type": cov(["1", "2"], {"1": 3, "2": 4})})],
            rules=[{"table_pattern": "t1", "covariate": "cov_school_type", "decision": "publish"}])
        self.assertEqual([r["label"] for r in rows], ["public", "private"])
        self.assertEqual(flagged, [])

    def test_not_live_and_strings_skipped(self):
        rows, rec, _ = self.run_build([
            read({"GENERO": {"1": "hombre", "2": "mujer"}}, {"GENERO": {"1": 1, "2": 1}}),
            write("gone", {"cov_gender": cov(["1", "2"], {"1": 1, "2": 1})}),
            write("t1", {"cov_gender": cov(["hombre", "mujer"], {"hombre": 1, "mujer": 1})}),
        ])
        self.assertEqual(rows, [])
        self.assertEqual(rec, {})

    def test_second_file_unlabelled_is_left_out(self):
        # two studies feed cov_gender; only the first file labels its column
        rows, rec, _ = self.run_build([
            read({"GENERO": {"1": "hombre", "2": "mujer"}}, {"GENERO": {"1": 30, "2": 30}}),
            read({}, {}, columns=["GENERO", "x"]),
            write("t1", {"cov_gender": cov(["1", "2"], {"1": 20, "2": 20})}),
        ])
        self.assertEqual(rows, [])
        self.assertIn("another file", rec[("t1", "cov_gender")]["reason"])

    def test_other_mapped_column_unlabelled_is_left_out(self):
        script = 'A = {"GENERO": "cov_gender"}\nB = {"SEX2": "cov_gender"}\n'
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "data").mkdir()
            (d / "logs").mkdir()
            (d / "data" / "s.py").write_text(script)
            with open(d / "logs" / "s.jsonl", "w") as f:
                for e in (read({"GENERO": {"1": "hombre", "2": "mujer"}}, {"GENERO": {"1": 30, "2": 30}}),
                          read({}, {}, columns=["SEX2"]),
                          write("t1", {"cov_gender": cov(["1", "2"], {"1": 20, "2": 20})})):
                    f.write(json.dumps(e) + "\n")
            rows, record, _ = cb.build(d / "logs", {"t1"}, [], d / "data")
        self.assertEqual(rows, [])
        self.assertIn("SEX2", record[0]["reason"])

    def test_missing_only_labels_excluded(self):
        rows, rec, _ = self.run_build([
            read({"EDU": {"-9": "Missing", "99": "No answer"}}, {"EDU": {"1": 3, "2": 4, "-9": 1}}),
            write("t1", {"cov_education": cov(["-9", "1", "2"], {"1": 3, "2": 4, "-9": 1})}),
        ])
        self.assertEqual(rows, [])


class ManualPairsTest(unittest.TestCase):
    M = dict(script="data/x.R", source_file="a.dta", source_column="sex")

    def test_manual_pairs_added_for_live_tables_only(self):
        rows, rec = [], []
        cb.add_manual(rows, rec, [dict(self.M, table="t1", covariate="cov_sex", code="2.0", label=" Female "),
                                  dict(self.M, table="t9", covariate="cov_sex", code="1", label="Male")], {"t1"})
        self.assertEqual(rows, [dict(table="t1", covariate="cov_sex", code="2", label="Female")])
        self.assertEqual(rec[0]["status"], "included")

    def test_harvested_pair_wins(self):
        rows = [dict(table="t1", covariate="cov_sex", code="1", label="hombre")]
        cb.add_manual(rows, [], [dict(self.M, table="t1", covariate="cov_sex", code="1", label="Male")], {"t1"})
        self.assertEqual([r["label"] for r in rows], ["hombre"])


class CommittedTableTest(unittest.TestCase):
    """The CSV the repo ships, against the rules build.py promises."""

    @classmethod
    def setUpClass(cls):
        with open(META / "covariate_labels.csv", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            cls.cols = r.fieldnames
            cls.rows = list(r)
        with open(META / "metadata.csv", encoding="utf-8-sig", newline="") as f:
            cls.live = {r["table"] for r in csv.DictReader(f)}
        with open(META / "covariate_labels" / "institutions.csv", encoding="utf-8", newline="") as f:
            cls.rules = list(csv.DictReader(f))

    def test_schema(self):
        self.assertEqual(self.cols, cb.COLUMNS)

    def test_no_duplicate_keys_and_no_blanks(self):
        keys = [(r["table"], r["covariate"], r["code"]) for r in self.rows]
        self.assertEqual(len(keys), len(set(keys)))
        for r in self.rows:
            self.assertTrue(all(r[c].strip() for c in cb.COLUMNS), r)
            self.assertTrue(r["covariate"].startswith("cov_"), r)

    def test_tables_are_live(self):
        self.assertEqual({r["table"] for r in self.rows} - self.live, set())

    def test_withheld_institutions_carry_no_names(self):
        for r in self.rows:
            if cb.institution_decision(r["table"], r["covariate"], self.rules) == "withhold":
                self.assertEqual(r["label"], cb.WITHHELD_LABEL, r)

    def test_ruled_cases_present(self):
        got = {(r["table"], r["covariate"]): r["label"] for r in self.rows if r["code"] == "1"}
        self.assertEqual(got.get(("estevez_2021_motiv", "cov_gender")), "hombre")
        self.assertEqual(got.get(("estevez_2021_motiv", "cov_school")), cb.WITHHELD_LABEL)


if __name__ == "__main__":
    unittest.main()
