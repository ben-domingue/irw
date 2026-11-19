"""The covariance family's subject tags (data/covariance/tags.csv; README "Subject tags", #3645).

Offline. `construct_type` and `sample` take core's values (TAG_VOCAB in
metadata/tag_normalize.R, read from that file so the two cannot drift) plus the
cov additions below; `framework` takes the README's closed list. A table has at
most one tags row, and every row names a table recorded in matrices.csv.
Untagged tables are listed, not failed: new tables are tagged in batches.

Run: python metadata/tests/test_cov_tags.py -v
"""
import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COV = ROOT / "data" / "covariance"
TAG_COLS = ["table", "construct_type", "sample", "framework", "notes"]
#: README "Subject tags": values cov adds where core has none that fits.
#: Add a value there, here and in COV_TAG_EXTRA in 22_cov.R together.
COV_EXTRA = {"construct type": {"Socioeconomic/attainment"}, "sample": set()}
FRAMEWORKS = {"TPB", "RAA", "HAPA", "TAM", "UTAUT", "SCCT", "HBM", "status_attainment"}
FRAME = {"Representative", "Targeted/specific", "General/non-specific"}
EXCLUSIVE = {"AI/model", "Animal", "Non-person unit"}


def core_vocab():
    """TAG_VOCAB's two lists, parsed from tag_normalize.R."""
    src = (ROOT / "metadata" / "tag_normalize.R").read_text(encoding="utf-8")
    src = re.sub(r"##.*", "", src)
    out = {}
    for col in ("sample", "construct type"):
        m = re.search(r'"%s"\s*=\s*c\(([^)]*)\)' % re.escape(col), src)
        out[col] = set(re.findall(r'"([^"]+)"', m.group(1))) - {"NA"}
    return out


def read(name):
    with open(COV / name, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def atoms(cell):
    return [a.strip() for a in cell.split(",") if a.strip()]


class CovTags(unittest.TestCase):
    def setUp(self):
        self.cols, self.rows = read("tags.csv")
        vocab = core_vocab()
        self.allowed = {c: vocab[c] | COV_EXTRA[c] for c in vocab}

    def test_columns(self):
        self.assertEqual(self.cols, TAG_COLS)

    def test_unique(self):
        names = [r["table"] for r in self.rows]
        self.assertEqual(len(names), len(set(names)))

    def test_no_orphan_rows(self):
        """A tags row names a table that has a record. A recorded table WITHOUT a
        tags row is not a failure: intake PRs add tables faster than they are
        tagged, and tagging is done in batches (README, "Subject tags"). Those
        tables are printed here and reported by 22_cov.R."""
        _, rec = read("matrices.csv")
        recorded = {r["table"] for r in rec}
        tagged = {r["table"] for r in self.rows}
        self.assertFalse(tagged - recorded, f"tags rows with no record in matrices.csv: {sorted(tagged - recorded)}")
        untagged = sorted(recorded - tagged)
        if untagged:
            print(f"\n  note: {len(untagged)} recorded table(s) not yet tagged: {', '.join(untagged)}")

    def test_codes(self):
        for r in self.rows:
            t = r["table"]
            ct = atoms(r["construct_type"])
            self.assertTrue(ct, f"{t}: construct_type is blank")
            self.assertTrue(set(ct) <= self.allowed["construct type"], f"{t}: {r['construct_type']}")
            s = atoms(r["sample"])
            self.assertTrue(set(s) <= self.allowed["sample"], f"{t}: {r['sample']}")
            for a in (ct, s):
                self.assertEqual(len(a), len(set(a)), t)
            if r["framework"]:
                self.assertIn(r["framework"], FRAMEWORKS, t)

    def test_sample_rules(self):
        """Core's two enforced sample rules (vocab.md, #1760 and #2206)."""
        for r in self.rows:
            s = set(atoms(r["sample"]))
            if s & EXCLUSIVE:
                self.assertEqual(len(s), 1, f"{r['table']}: a respondent-type atom stands alone")
            if "General/non-specific" in s:
                self.assertFalse(s & (FRAME - {"General/non-specific"}),
                                 f"{r['table']}: General/non-specific with another frame atom")


if __name__ == "__main__":
    unittest.main()
