"""A ';'-delimited file with decimal commas is read, not reported as a failed download.

Read with ',', such a file is one column until the first "1,6", where pandas
raises "Error tokenizing data. C error: Expected 1 fields in line N, saw 3".
load_table() used to let that escape, and process_one() recorded a readable,
fully downloaded file as `download_failed` (pone.0262960, STICSA). Offline,
synthetic.
"""
import random
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from irw_triage_updated import load_table  # noqa: E402


def _european_csv(n=600, items=8, imputed_row=400, seed=0):
    """1-4 items, ';'-delimited, one mean-imputed '1,6' and one blank ' ' cell."""
    rng = random.Random(seed)
    lines = [";".join(["id"] + [f"Item_{k}" for k in range(1, items + 1)])]
    for i in range(1, n + 1):
        vals = [str(rng.randint(1, 4)) for _ in range(items)]
        if i == imputed_row:
            vals[2] = "1,6"
        if i == imputed_row + 1:
            vals[5] = " "
        lines.append(";".join([str(i)] + vals))
    return ("\r\n".join(lines) + "\r\n").encode("utf-8-sig")


class EuropeanCsv(unittest.TestCase):
    def test_comma_read_really_fails(self):
        # Guards the premise: without the fallback this is a ParserError.
        import io
        with self.assertRaises(pd.errors.ParserError):
            pd.read_csv(io.BytesIO(_european_csv()))

    def test_semicolon_decimal_comma_file_loads(self):
        df = load_table(_european_csv(), filename="x_S1_Database.csv")
        self.assertEqual(df.shape, (600, 9))
        self.assertTrue(all(pd.api.types.is_numeric_dtype(df[c]) for c in df.columns))
        self.assertAlmostEqual(df.loc[399, "Item_3"], 1.6)
        self.assertTrue(pd.isna(df.loc[400, "Item_6"]))

    def test_plain_comma_csv_unchanged(self):
        df = load_table(b"id,a,b\n1,2,3\n2,3,4\n", filename="x.csv")
        self.assertEqual(list(df.columns), ["id", "a", "b"])
        self.assertEqual(df.shape, (2, 3))

    def test_unparseable_comma_file_still_raises(self):
        bad = b"a,b\n1,2\n" + b"1,2,3,4\n" * 3
        with self.assertRaises(pd.errors.ParserError):
            load_table(bad, filename="x.csv")


if __name__ == "__main__":
    unittest.main()
