"""A banner row spanning the sheet must not crash the re-read hint.

Regression test for the defect the 2026-10-16 PMC monthly run exposed: four
cc-by candidates (peerj.5868, peerj.15304, s41598-024-70704-z,
s41598-018-30524-4) were recorded as flag `error` with the pandas message
"arg must be a list, tuple, 1-d array, or Series". Their supplements open
with a one-cell project banner, which read_excel carries across the row, so
`_alternative_reads`' `header=[0,1]` try flattened every column to the SAME
label; `df[c]` then returned a frame rather than a Series and
`_small_int_block` raised -- which `process_one` catches as `error`, retiring
a readable candidate. TODO.md had the same fault against 45 rows of the
2026-10-10/11/14/15 runs.

Offline and synthetic. The .xlsx case needs openpyxl and skips without it;
the unit cases around it do not.
"""
import io
import random
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from irw_triage_updated import (  # noqa: E402
    _alternative_reads, _dedupe_labels, _small_int_block, load_table,
    reread_hint, triage_dataset,
)

try:
    import openpyxl  # noqa: F401
    HAVE_OPENPYXL = True
except ImportError:
    HAVE_OPENPYXL = False


def _bannered_xlsx(n=120, items=8, seed=0):
    """An .xlsx whose row 1 is a project banner and row 2 the real header."""
    rng = random.Random(seed)
    header = ["id"] + [f"Item_{k}" for k in range(1, items + 1)]
    body = [[i] + [rng.randint(1, 4) for _ in range(items)]
            for i in range(1, n + 1)]
    banner = ["Project: Knowledge in college athletes"] + [""] * items
    buf = io.BytesIO()
    pd.DataFrame([header] + body).to_excel(buf, index=False, header=banner)
    return buf.getvalue()


class BannerHeaderReread(unittest.TestCase):
    def test_dedupe_labels_follows_the_read_csv_convention(self):
        self.assertEqual(_dedupe_labels(["a", "a", "b", "a"]),
                         ["a", "a.1", "b", "a.2"])

    def test_small_int_block_survives_duplicate_labels(self):
        """The crash itself: df[c] is a frame when a label repeats."""
        df = pd.DataFrame([[1, 2, 3, 1], [2, 3, 1, 2], [3, 1, 2, 3]] * 40,
                          columns=["q", "q", "q", "q"])
        self.assertEqual(len(_small_int_block(df)), 4)   # used to raise TypeError

    def test_small_int_block_is_unchanged_on_unique_labels(self):
        df = pd.DataFrame([[1, 2, 3, 1], [2, 3, 1, 2], [3, 1, 2, 3]] * 40,
                          columns=["a", "b", "c", "d"])
        self.assertEqual(_small_int_block(df), ["a", "b", "c", "d"])

    @unittest.skipUnless(HAVE_OPENPYXL, "openpyxl not installed")
    def test_alternative_reads_never_yield_duplicate_labels(self):
        for how, df in _alternative_reads(_bannered_xlsx(), "s001.xlsx"):
            self.assertFalse(df.columns.duplicated().any(),
                             f"{how} yielded duplicate column labels")

    @unittest.skipUnless(HAVE_OPENPYXL, "openpyxl not installed")
    def test_reread_hint_does_not_raise_on_a_bannered_sheet(self):
        """load_table's own header recovery may make the hint return None by
        design; what must never happen is the TypeError."""
        content = _bannered_xlsx()
        t = triage_dataset(load_table(content, filename="s001.xlsx"))
        try:
            reread_hint(content, "s001.xlsx", t)
        except TypeError as e:                     # pragma: no cover
            self.fail(f"reread_hint raised on a bannered sheet: {e}")


if __name__ == "__main__":
    unittest.main()
