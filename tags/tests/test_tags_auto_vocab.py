"""Every enum cell in tags/tags_auto.csv is in the controlled vocabulary (#3322).

The weekly metadata pipeline halts in 03_tags.R on a `Construct type` or
`Sample` value outside TAG_VOCAB, and stage_tag_row.py refuses to stage one --
but a batch that appends to tags_auto.csv by hand bypasses the staging script,
and nothing read the file again until Monday. That is how #2961 (eleven
invented construct types, 2026-10-12) and #3322 ("Cognitive", plus nineteen
rows with prose in every enum column, 2026-10-30) each turned into a failed
pipeline run instead of a failed pull request.

This reads the committed file with the same vocabulary the staging script
enforces, so the two cannot drift apart, and runs in tests.yml on every PR.
"""
import csv
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "tags" / "tags_auto.csv"
STAGER = ROOT / "tags" / ".claude" / "skills" / "irw-auto-tag" / "scripts" / "stage_tag_row.py"


def load_stager():
    spec = importlib.util.spec_from_file_location("stage_tag_row", STAGER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TagsAutoVocabTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stager = load_stager()
        with open(CSV, newline="", encoding="utf-8") as f:
            cls.rows = list(csv.DictReader(f))

    def offenders(self, col):
        vocab = self.stager.ENUM_VOCAB[col]
        out = []
        for row in self.rows:
            cell = row[col]
            for old, new in self.stager.ENUM_RENAMES.items():
                cell = cell.replace(old, new)
            bad = [a.strip() for a in cell.split(",") if a.strip() and a.strip() not in vocab]
            if bad:
                out.append((row["table"], bad))
        return out

    def test_enum_columns_are_in_vocabulary(self):
        for col in self.stager.ENUM_VOCAB:
            with self.subTest(column=col):
                bad = self.offenders(col)
                self.assertEqual(
                    bad, [],
                    f"{len(bad)} row(s) carry a `{col}` value outside the controlled "
                    f"vocabulary {sorted(self.stager.ENUM_VOCAB[col])}. Pick a listed "
                    f"value, move the prose to Notes, or leave the cell blank; the "
                    f"pipeline halts on these (irw#2961, irw#3322). First few: {bad[:5]}",
                )

    def test_status_values(self):
        bad = [(r["table"], r["Status"]) for r in self.rows
               if r["Status"] not in self.stager.STATUS_VALUES]
        self.assertEqual(bad, [])

    def test_no_duplicate_tables(self):
        seen, dupes = set(), []
        for r in self.rows:
            if r["table"] in seen:
                dupes.append(r["table"])
            seen.add(r["table"])
        self.assertEqual(dupes, [], "stage_tag_row.py refuses these; a hand append does not")

    def test_line_endings_are_uniformly_crlf(self):
        """The file is CRLF throughout. A reader opened in text mode applies
        universal-newline translation, and writing it back rewrites every
        line as LF: two whole-file rewrites on 2026-10-30 were caught only by
        counting diff lines afterwards. Read in binary, so the check cannot
        make the same mistake."""
        raw = CSV.read_bytes()
        lines = raw.count(b"\n")
        crlf = raw.count(b"\r\n")
        self.assertEqual(
            crlf, lines,
            f"{lines - crlf} of {lines} line(s) end in bare LF; the file is CRLF "
            f"(see irw-csvs-are-crlf). Read and write it in binary or with newline=''.",
        )
        self.assertTrue(raw.endswith(b"\r\n"), "file does not end with a newline")

    def test_stager_vocab_matches_pipeline(self):
        """ENUM_VOCAB must mirror TAG_VOCAB in metadata/tag_normalize.R for
        the columns the pipeline halts on."""
        import re
        r_src = (ROOT / "metadata" / "tag_normalize.R").read_text(encoding="utf-8")
        block = r_src[r_src.index("TAG_VOCAB <- list("):]
        block = block[:block.index("\n)\n")]
        for col in ("sample", "construct type"):
            m = re.search(rf'"{col}" = c\((.*?)\)', block, re.S)
            r_vals = set(re.findall(r'"([^"]+)"', m.group(1)))
            py_vals = self.stager.ENUM_VOCAB[col[0].upper() + col[1:]]
            self.assertEqual(r_vals, py_vals, col)


if __name__ == "__main__":
    unittest.main()
