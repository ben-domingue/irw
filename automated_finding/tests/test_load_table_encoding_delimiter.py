"""Encoding and delimiter are independent defects, and a file can carry both.

Until 2026-10-21 `_read_tabular` could survive only one at a time. The first
read raised UnicodeDecodeError, its handler retried in latin-1 *with the
default comma*, and the ParserError that came back was raised from inside an
except block -- so the delimiter sniffing underneath never ran. A latin-1,
';'-delimited export was therefore unreadable even though each defect alone
was handled, and process_one() recorded a fully downloaded file as
`download_failed`.

Four rows of the 2026-10-21 repos sweep were this, among them
10.1371/journal.pone.0211929 (Bottesi IUS-R, 761 respondents x 361 items) and
10.7910/DVN/ZXQBC7. The non-UTF-8 byte has to land EARLY in those files --
before the first decimal comma -- which is what makes the first exception a
UnicodeDecodeError rather than a ParserError; `_european_csv` in
test_load_table_delimiter.py covers the ParserError-first order.

The second case here is the BIFF2/3/4 workbook: Excel 2.x-4.0, still emitted
by old survey tools, starts with a bare 0x0009 BOF record, matches neither
container pandas sniffs for, and so fails with "Excel file format cannot be
determined" on a file xlrd reads fine (10.7910/DVN/EL4KPR, Gries MFQ).

Offline, synthetic.
"""
import importlib.util
import io
import random
import sys
import unittest
from pathlib import Path

import pandas as pd

# xlrd is in OPTIONAL_READERS, so preflight_deps() installs it for a pipeline
# run -- but an environment that skipped that (the tests workflow, before
# #3158) would see this class ERROR rather than skip, which turned main red on
# an unrelated PR. Skip with a reason naming the package instead.
HAVE_XLRD = importlib.util.find_spec("xlrd") is not None

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from irw_triage_updated import load_table  # noqa: E402


def _latin1_semicolon_csv(n=300, items=6, seed=0):
    """';'-delimited, latin-1, with an accented byte in the HEADER.

    The accent in row 1 is the point: it makes the default UTF-8 read die as
    a UnicodeDecodeError before the parser ever reaches a row whose field
    count disagrees, which is the ordering the old code could not handle.
    `Altezza` and `Peso` carry the decimal commas, so the latin-1 retry at the
    default comma separator still fails -- as it does on the real files. Note
    that `Peso` is a whole number on most rows and fractional on others: read
    with ',' the rows then disagree about how many fields they have, which is
    what raises ParserError. Were the comma count constant, pandas would
    quietly read the leading field as an index and return a 1-column frame
    instead of failing.
    """
    rng = random.Random(seed)
    header = ["Età", "Altezza", "Peso", "Genere"]
    header += [f"IUS2_{k:02d}" for k in range(1, items + 1)]
    lines = [";".join(header)]
    for i in range(1, n + 1):
        vals = [str(rng.randint(18, 70)),
                "1,%02d" % rng.randint(47, 95),
                "%d,5" % rng.randint(45, 110) if i % 7 == 0
                else str(rng.randint(45, 110)),
                str(rng.randint(1, 2))]
        vals += [str(rng.randint(1, 5)) for _ in range(items)]
        lines.append(";".join(vals))
    return ("\r\n".join(lines) + "\r\n").encode("latin-1")


def _biff2_xls():
    """A minimal BIFF2 (Excel 2.x) worksheet: 0x0009 BOF, text + number cells."""
    out = bytearray()

    def rec(code, payload):
        out.extend(code.to_bytes(2, "little"))
        out.extend(len(payload).to_bytes(2, "little"))
        out.extend(payload)

    rec(0x0009, (0x0002).to_bytes(2, "little") + (0x0010).to_bytes(2, "little"))
    for col, text in enumerate(("id", "Item_1")):
        body = (0).to_bytes(2, "little") + col.to_bytes(2, "little")
        body += bytes([0, 0, 0]) + bytes([len(text)]) + text.encode("ascii")
        rec(0x0004, body)                                   # LABEL
    for row, (ident, resp) in enumerate(((1, 3), (2, 4)), start=1):
        for col, value in enumerate((ident, resp)):
            body = row.to_bytes(2, "little") + col.to_bytes(2, "little")
            body += bytes([0, 0, 0]) + value.to_bytes(2, "little")
            rec(0x0002, body)                               # INTEGER
    rec(0x000A, b"")                                        # EOF
    return bytes(out)


class Latin1SemicolonCsv(unittest.TestCase):
    def setUp(self):
        self.raw = _latin1_semicolon_csv()

    def test_premise_default_read_is_a_unicode_error(self):
        with self.assertRaises(UnicodeDecodeError):
            pd.read_csv(io.BytesIO(self.raw))

    def test_premise_latin1_with_comma_is_a_parser_error(self):
        # The old handler's retry. One column until the field counts disagree.
        with self.assertRaises(pd.errors.ParserError):
            pd.read_csv(io.BytesIO(self.raw), encoding="latin-1")

    def test_load_table_reads_it(self):
        df = load_table(self.raw, "s003.csv")
        self.assertEqual(df.shape, (300, 10))
        self.assertIn("IUS2_01", df.columns)
        self.assertEqual(sorted(df["IUS2_01"].unique()), [1, 2, 3, 4, 5])

    def test_decimal_comma_becomes_a_float(self):
        df = load_table(self.raw, "s003.csv")
        self.assertTrue(df["Altezza"].between(1.47, 1.95).all())

    def test_accented_header_survives(self):
        df = load_table(self.raw, "s003.csv")
        self.assertEqual(df.columns[0], "Età")


@unittest.skipUnless(HAVE_XLRD, "xlrd not installed: the BIFF2 .xls fallback "
                                 "cannot be exercised (it is in "
                                 "OPTIONAL_READERS; pip install xlrd)")
class Biff2Workbook(unittest.TestCase):
    def setUp(self):
        self.raw = _biff2_xls()

    def test_premise_pandas_cannot_sniff_it(self):
        with self.assertRaises(ValueError) as cm:
            pd.read_excel(io.BytesIO(self.raw))
        self.assertIn("engine", str(cm.exception).lower())

    def test_load_table_reads_it(self):
        df = load_table(self.raw, "legacy.xls")
        self.assertEqual(list(df.columns), ["id", "Item_1"])
        self.assertEqual(df["Item_1"].tolist(), [3, 4])


if __name__ == "__main__":
    unittest.main()
