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
import types
import unittest
from pathlib import Path
from unittest import mock

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

    def test_carried_forward_draft_is_declared_and_dates_stay_apart(self):
        # A read-only token cannot list `next`, so those rows come from the
        # previous snapshot. The header must say so, and `as of` must still
        # scrape the refresh date rather than the date rows were carried from.
        text = rlt.render([("t", "irw_text_2", "draft")], "2026-09-20",
                          ["irw_text_2"], "2026-09-19")
        out = Path(self.enterContext(tempfile.TemporaryDirectory()))
        f = out / "live_tables.csv"
        f.write_text(text)
        got, asof = rlt.read_snapshot(f)
        self.assertEqual(asof, "2026-09-20")
        self.assertEqual(got, {"t": "draft"})
        self.assertIn("data.edit", text)
        self.assertEqual([ln for ln in text.splitlines()
                          if not ln.startswith("#")][0], "table,shard,status")

    def test_read_rows_keeps_the_shard(self):
        # fetch() carries a shard's draft rows forward by shard, so the reader
        # has to give back the shard column, not just table -> status.
        out = Path(self.enterContext(tempfile.TemporaryDirectory()))
        f = out / "live_tables.csv"
        f.write_text(rlt.render([("a", "irw_text", "published"),
                                 ("b", "irw_text_2", "draft")], "2026-09-20"))
        self.assertEqual(rlt.read_rows(f),
                         [("a", "irw_text", "published"),
                          ("b", "irw_text_2", "draft")])

    def test_committed_snapshot_parses(self):
        # The file in the repo, read exactly as the checker reads it.
        snap, asof = rlt.read_snapshot(SRC / "itemtext" / "live_tables.csv")
        self.assertTrue(snap, "live_tables.csv is empty")
        self.assertTrue(asof, "live_tables.csv has no `as of` date")
        self.assertEqual(set(snap.values()) - {"published", "draft"}, set())
        # Bare names only: __items is the Redivis table name, not the name
        # provenance.csv, the dictionary or the issues page use.
        self.assertFalse([t for t in snap if t.endswith("__items")])


class DraftUnreadable(unittest.TestCase):
    """The 403 that killed the first scheduled CI run (#2247).

    Listing `next` needs a data.edit-scoped token; the Actions secret is
    read-only by design. That must not crash the refresh, and it must not
    quietly drop the draft rows either -- dropping them turns every table in
    the release window into a page ORPHAN.
    """

    def _fetch(self, listed, prior):
        shards = [types.SimpleNamespace(name="irw_text"),
                  types.SimpleNamespace(name="irw_text_2")]
        with mock.patch.object(rlt, "load_registry", return_value=("datapages", None)), \
             mock.patch.object(rlt, "text_shards", return_value=shards), \
             mock.patch.object(rlt, "read_rows", return_value=prior), \
             mock.patch.object(rlt, "_list", side_effect=listed):
            return rlt.fetch()

    def test_403_carries_the_draft_forward_instead_of_crashing(self):
        def listed(owner, shard, version):
            if version == "current":
                return {"pub_a"} if shard == "irw_text" else {"pub_b"}
            if shard == "irw_text":
                return None                       # no open draft: normal
            raise rlt.DraftUnreadable(shard)      # read-only token
        rows, unreadable = self._fetch(listed, [("staged", "irw_text_2", "draft")])
        self.assertEqual(unreadable, ["irw_text_2"])
        self.assertIn(("staged", "irw_text_2", "draft"), rows)
        self.assertIn(("pub_a", "irw_text", "published"), rows)

    def test_a_carried_row_that_has_since_been_released_is_dropped(self):
        # It is published now, so it is past the release window the carried row
        # was a claim about; keeping both would list it twice.
        def listed(owner, shard, version):
            if version == "current":
                return {"staged"} if shard == "irw_text_2" else set()
            if shard == "irw_text":
                return None
            raise rlt.DraftUnreadable(shard)
        rows, _ = self._fetch(listed, [("staged", "irw_text_2", "draft")])
        self.assertEqual([r for r in rows if r[0] == "staged"],
                         [("staged", "irw_text_2", "published")])

    # The exact message the 2026-09-20 run died on. Matching is on message
    # text, so it is pinned to the real wording rather than a paraphrase.
    MSG = ("[403 insufficient_scope] You have access to the underlying "
           "resource, but your current credentials are missing the required "
           "scope(s): data.edit")

    def _list_raising(self, msg, version):
        fake = types.ModuleType("redivis")

        def user(_owner):
            raise RuntimeError(msg)

        fake.user = user
        with mock.patch.dict(sys.modules, {"redivis": fake}):
            return rlt._list("datapages", "irw_text_2", version)

    def test_the_real_403_message_is_classified_as_unreadable(self):
        with self.assertRaises(rlt.DraftUnreadable):
            self._list_raising(self.MSG, "next")

    def test_the_same_403_on_current_is_not_swallowed(self):
        with self.assertRaises(RuntimeError):
            self._list_raising(self.MSG, "current")

    def test_a_403_on_current_still_fails_loudly(self):
        # Only the draft is optional. Losing the published side means the
        # snapshot is wrong about what a reader can fetch, and a wrong snapshot
        # is worse than no run.
        def listed(owner, shard, version):
            raise RuntimeError("[403 insufficient_scope] data.edit")
        with self.assertRaises(RuntimeError):
            self._fetch(listed, [])


if __name__ == "__main__":
    unittest.main()
