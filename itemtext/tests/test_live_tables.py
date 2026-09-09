"""The snapshot file's shape, which check_issues_page.R parses (irw#1828).

Nothing here touches Redivis: `fetch()` is the only part that does, and it is
not what breaks. What breaks is the file contract between the writer here and
the reader in R -- the header line the date is scraped from, the `#` comments
the R side strips, and the `published`/`draft` split that decides whether a
table reads as live. Those are checkable offline, so they are checked on every
PR rather than the next time someone runs the refresh with a token.
"""

import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SRC / "itemtext"))

import refresh_live_tables as rlt  # noqa: E402


class RoundTrip(unittest.TestCase):
    def test_render_then_read(self):
        rows = [("a_table", "irw_text", "published"),
                ("b_table", "irw_text_2", "draft")]
        out = Path(self.enterContext(tempfile.TemporaryDirectory()))
        f = out / "live_tables.csv"
        f.write_text(rlt.render(rows, "2026-09-06"))
        got, asof = rlt.read_snapshot(f)
        self.assertEqual(got, {"a_table": "published", "b_table": "draft"})
        self.assertEqual(asof, "2026-09-06")

    def test_missing_file_is_not_an_error(self):
        # The R side falls back to the `uploaded` column when there is no
        # snapshot, and says so. That path must stay reachable.
        got, asof = rlt.read_snapshot(Path("/nonexistent/live_tables.csv"))
        self.assertEqual(got, {})
        self.assertIsNone(asof)

    def test_header_is_comments_then_one_csv_header(self):
        text = rlt.render([("t", "irw_text", "published")], "2026-09-06")
        lines = text.splitlines()
        # R strips `^#` and reads the rest as CSV, so every preamble line must
        # start with # and the first non-# line must be the column header.
        preamble = [ln for ln in lines if ln.startswith("#")]
        body = [ln for ln in lines if not ln.startswith("#")]
        self.assertTrue(preamble and all(" as of " in p or "status=" in p
                                         or "generated" in p for p in preamble))
        self.assertEqual(body[0], "table,shard,status")

    def test_committed_snapshot_parses(self):
        # The file in the repo, read exactly as the checker reads it.
        snap, asof = rlt.read_snapshot(SRC / "itemtext" / "live_tables.csv")
        self.assertTrue(snap, "live_tables.csv is empty")
        self.assertTrue(asof, "live_tables.csv has no `as of` date")
        self.assertEqual(set(snap.values()) - {"published", "draft"}, set())
        # Bare names only: __items is the Redivis table name, not the name
        # provenance.csv, the dictionary or the issues page use.
        self.assertFalse([t for t in snap if t.endswith("__items")])


if __name__ == "__main__":
    unittest.main()
