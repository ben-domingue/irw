"""A banner row spanning the sheet must not crash the re-read hint.

Regression test for the defect the 2026-10-16 PMC monthly run exposed: four
cc-by candidates (peerj.5868, peerj.15304, s41598-024-70704-z,
s41598-018-30524-4) were recorded as flag `error` with the pandas message
"arg must be a list, tuple, 1-d array, or Series". Their supplements open
with a one-cell project banner, so `_alternative_reads`' `header=[0,1]`
try flattened every column to the SAME label, `df[c]` returned a frame
rather than a Series, and `_small_int_block` raised -- which `process_one`
catches as `error`, retiring a readable candidate. Offline, synthetic.
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


def _bannered_xlsx(n=120, items=8, seed=0):
    """An .xlsx whose row 1 is a project banner and row 2 the real header."""
    rng = random.Random(seed)
    header = ["id"] + [f"Item_{k}" for k in range(1, items + 1)]
    rows = [["Project: Knowledge in college athletes"] + [""] * items,
            header]
    for i in range(1, n + 1):
        rows.append([i] + [rng.randint(1, 4) for _ in range(items)])
    buf = io.BytesIO()
    pd.DataFrame(rows[1:]).to_excel(buf, index=False, header=rows[0])
    return buf.getvalue()


class BannerHeaderReread(unittest.TestCase):
    def test_dedupe_labels_follows_the_read_csv_convention(self):
        self.assertEqual(_dedupe_labels(["a", "a", "b", "a"]),
                         ["a", "a.1", "b", "a.2"])

    def test_alternative_reads_never_yield_duplicate_labels(self):
        content = _bannered_xlsx()
        for how, df in _alternative_reads(content, "s001.xlsx"):
            self.assertFalse(df.columns.duplicated().any(),
                             f"{how} yielded duplicate column labels")

    def test_small_int_block_survives_a_genuine_duplicate_header(self):
        df = pd.DataFrame([[1, 2, 3, 1], [2, 3, 1, 2], [3, 1, 2, 3]] * 40,
                          columns=["q", "q", "q", "q"])
        self.assertEqual(len(_small_int_block(df)), 4)

    def test_reread_hint_does_not_raise_on_a_bannered_sheet(self):
        """The crash was in reread_hint, so the hint call itself must return.

        load_table's own header=1 recovery may already make this synthetic
        file triage as `good`, in which case reread_hint returns None by
        design; what must never happen is the TypeError.
        """
        content = _bannered_xlsx()
        df = load_table(content, filename="s001.xlsx")
        t = triage_dataset(df)
        try:
            reread_hint(content, "s001.xlsx", t)   # used to raise TypeError
        except TypeError as e:                     # pragma: no cover
            self.fail(f"reread_hint raised on a bannered sheet: {e}")

if __name__ == "__main__":
    unittest.main()
