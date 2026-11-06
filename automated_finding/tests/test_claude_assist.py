"""irw_claude_assist.py: the code side of a Claude mapping (Step 2c).

Claude proposes; apply_mapping() executes. These tests pin the rules that
keep the code from quietly changing data on Claude's say-so: no response is
dropped for being out of range or non-numeric without QC failing, text
labels must cover every response, and only a high-confidence
not_item_response flag closes a row. Offline, synthetic; no Claude call.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import irw_claude_assist as ca  # noqa: E402


def _wide(n=120, seed=0):
    import random
    rng = random.Random(seed)
    return pd.DataFrame({
        "pid": [f"p{i}" for i in range(n)],
        "Age": [rng.randint(18, 70) for _ in range(n)],
        **{f"Q{k}": [rng.randint(1, 5) for _ in range(n)] for k in range(1, 6)},
        "Q_total": [0] * n,
    })


def _mapping(**over):
    m = {"decision": "map", "id_strategy": "column", "id_col": "pid",
         "scales": [{"out_suffix": "s", "item_cols": [f"Q{k}" for k in range(1, 6)],
                     "valid_min": 1, "valid_max": 5}],
         "cov_cols": {"Age": "cov_age"}, "exclude_cols": ["Q_total"],
         "sentinel_values": [], "confidence": "high"}
    m.update(over)
    return m


def _fails(result):
    return result["qc_detail"] if result["qc_errors"] else ""


class ApplyMapping(unittest.TestCase):
    def test_clean_mapping_melts_every_response(self):
        (r,) = ca.apply_mapping(_wide(), _mapping(), "x")
        self.assertEqual(r["rows"], 120 * 5)
        self.assertEqual(r["ids"], 120)
        self.assertEqual(r["items"], 5)
        self.assertEqual(list(r["df"].columns), ["id", "item", "resp", "cov_age"])
        self.assertNotIn("resp_out_of_range", r["qc_detail"] or "")

    def test_out_of_range_is_kept_and_fails_qc(self):
        df = _wide()
        df.loc[3, "Q2"] = 0
        (r,) = ca.apply_mapping(df, _mapping(), "x")
        self.assertEqual(r["rows"], 120 * 5)      # nothing filtered away
        self.assertIn("resp_out_of_range", _fails(r))

    def test_nonnumeric_text_fails_qc_instead_of_vanishing(self):
        df = _wide().astype({"Q1": object})
        df.loc[0, "Q1"] = "NA"
        (r,) = ca.apply_mapping(df, _mapping(), "x")
        self.assertIn("resp_nonnumeric", _fails(r))

    def test_blank_cells_are_missing_not_failures(self):
        df = _wide().astype({"Q1": object})
        df.loc[0, "Q1"] = None
        df.loc[1, "Q1"] = "  "
        (r,) = ca.apply_mapping(df, _mapping(), "x")
        self.assertNotIn("resp_nonnumeric", r["qc_detail"] or "")
        self.assertEqual(r["rows"], 120 * 5 - 2)

    def test_value_labels_map_text_responses(self):
        words = {1: "Strongly disagree", 2: "Disagree", 3: "Neutral",
                 4: "Agree", 5: "Strongly agree"}
        df = _wide()
        for k in range(1, 6):
            df[f"Q{k}"] = df[f"Q{k}"].map(lambda v: " " + words[v].upper() + " ")
        sc = _mapping()["scales"][0] | {"value_labels": {w: v for v, w in words.items()}}
        (r,) = ca.apply_mapping(df, _mapping(scales=[sc]), "x")
        self.assertEqual(r["rows"], 120 * 5)
        self.assertEqual((r["resp_min"], r["resp_max"]), (1.0, 5.0))

    def test_value_labels_missing_a_category_is_refused(self):
        df = _wide()
        df["Q1"] = df["Q1"].map({1: "a", 2: "b", 3: "c", 4: "d", 5: "e"})
        sc = {"out_suffix": "s", "item_cols": ["Q1"],
              "value_labels": {"a": 1, "b": 2, "c": 3, "d": 4}}
        with self.assertRaisesRegex(ValueError, "value_labels miss"):
            ca.apply_mapping(df, _mapping(scales=[sc]), "x")

    def test_row_index_with_an_existing_id_column(self):
        df = _wide().rename(columns={"pid": "id"})
        df.loc[1, "id"] = df.loc[0, "id"]          # unusable: not unique
        (r,) = ca.apply_mapping(df, _mapping(id_strategy="row_index"), "x")
        self.assertEqual(r["ids"], 120)

    def test_invented_column_is_rejected(self):
        sc = {"out_suffix": "s", "item_cols": ["Q1", "Q99"]}
        with self.assertRaisesRegex(ValueError, "not in file"):
            ca.apply_mapping(_wide(), _mapping(scales=[sc]), "x")

    def test_covariate_melted_as_item_fails(self):
        sc = {"out_suffix": "s", "item_cols": ["Q1", "Q2", "Age"],
              "valid_min": None, "valid_max": None}
        (r,) = ca.apply_mapping(_wide(), _mapping(scales=[sc], cov_cols={}), "x")
        self.assertIn("covariate_as_item", _fails(r))


class Verdicts(unittest.TestCase):
    def test_only_high_confidence_not_item_response_closes(self):
        f = {"status": "flagged_by_claude"}
        self.assertEqual(ca.verdict_for(f | {"flag_kind": "not_item_response",
                                             "confidence": "high"}),
                         "not_item_response")
        for kind, conf in [("not_item_response", "medium"),
                           ("wrong_file", "high"), ("below_floor", "high"),
                           ("other", "high"), ("", "high")]:
            self.assertEqual(ca.verdict_for(f | {"flag_kind": kind,
                                                 "confidence": conf}),
                             "needs_human", (kind, conf))

    def test_mapped_rows(self):
        self.assertEqual(ca.verdict_for({"status": "mapped", "qc_errors": 0}), "lead")
        self.assertEqual(ca.verdict_for({"status": "mapped", "qc_errors": 2}),
                         "needs_human")
        self.assertEqual(ca.verdict_for({"status": "mapping_invalid"}), "needs_human")
        self.assertEqual(ca.verdict_for({"status": "multiple_files"}), "not_checked")


class ParseAndLedger(unittest.TestCase):
    def test_parse_tolerates_fences_and_prose(self):
        self.assertEqual(ca._parse_mapping('```json\n{"decision": "flag"}\n```'),
                         {"decision": "flag"})
        self.assertEqual(ca._parse_mapping('Here it is:\n{"a": {"b": 1}}\nDone.'),
                         {"a": {"b": 1}})

    def test_ledger_replaces_a_rechecked_doi(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "leads", "ledger.csv")
            ca.append_ledger([{"doi": "10.1/A", "verdict": "needs_human"},
                              {"doi": "10.1/B", "verdict": "lead"}], path)
            ca.append_ledger([{"doi": "10.1/a", "verdict": "not_item_response"}], path)
            got = pd.read_csv(path, dtype=str)
            self.assertEqual(sorted(got["verdict"]), ["lead", "not_item_response"])
            self.assertEqual(ca.load_ledger_dois(path), {"10.1/a", "10.1/b"})

    def test_archive_rows_one_per_doi(self):
        with tempfile.TemporaryDirectory() as d:
            pd.DataFrame({"doi": ["10.1/A", "10.1/B"]}).to_csv(
                os.path.join(d, "human_review_x_2026-01-01.csv"), index=False)
            pd.DataFrame({"doi": ["10.1/a", ""]}).to_csv(
                os.path.join(d, "human_review_y_2026-01-02.csv"), index=False)
            pd.DataFrame({"doi": ["10.1/C"]}).to_csv(
                os.path.join(d, "googlesheet_humaneye.csv"), index=False)
            dois = sorted(r["doi"].lower() for r in ca.archive_rows(d))
            self.assertEqual(dois, ["10.1/a", "10.1/b"])


class AlreadyWorked(unittest.TestCase):
    def test_deposit_key(self):
        cases = {"10.17632/nr9388gbzf.1": "nr9388gbzf",
                 "10.5281/zenodo.14870714": "14870714",
                 "10.6084/m9.figshare.30995812.v1": "30995812",
                 "https://doi.org/10.7910/DVN/4Y3Y23": "4y3y23",
                 "10.1371/journal.pone.0273971": "pone.0273971",
                 "10.1/ab": ""}
        for doi, key in cases.items():
            self.assertEqual(ca.deposit_key(doi), key, doi)

    def test_finds_a_build_script_citing_the_deposit(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "data"))
            Path(root, "data", "x_2025.py").write_text(
                'URL = "https://zenodo.org/api/records/14870714/files/a.sav"\n')
            old = ca._WORKED_CORPUS
            try:
                ca._WORKED_CORPUS = None
                self.assertEqual(ca.already_worked("10.5281/zenodo.14870714", root),
                                 os.path.join("data", "x_2025.py"))
                self.assertEqual(ca.already_worked("10.5281/zenodo.1487071", root), "")
                self.assertEqual(ca.already_worked("10.5281/zenodo.148707140", root), "")
            finally:
                ca._WORKED_CORPUS = old
        self.assertEqual(ca.verdict_for({"status": "already_worked"}), "already_worked")


if __name__ == "__main__":
    unittest.main()
