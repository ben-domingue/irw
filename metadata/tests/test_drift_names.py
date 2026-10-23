"""drift_report's duplicate-name check (#2151), offline.

The Redivis half is six list_tables() calls; what can go wrong is the logic
over their result, so that is what is tested here, on a hand-built index.

    python metadata/tests/test_drift_names.py -v
"""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import drift_report as d  # noqa: E402

SHARDS = ["item_response_warehouse", "item_response_warehouse_2",
          "item_response_warehouse_3"]


class Timestamps(unittest.TestCase):
    """Every timestamp the report prints is labelled UTC by a literal, so
    parse_iso has to deliver UTC whatever offset the source used (2026-10-23)."""

    def test_a_local_offset_is_converted_not_relabelled(self):
        # the real case: #3202's commit, git log %aI, PDT
        self.assertEqual(f"{d.parse_iso('2026-10-23T12:49:53-07:00'):%Y-%m-%d %H:%M}",
                         "2026-10-23 19:49")

    def test_z_and_explicit_utc_are_unchanged(self):
        for s in ("2026-10-23T17:55:02Z", "2026-10-23T17:55:02+00:00"):
            self.assertEqual(f"{d.parse_iso(s):%H:%M}", "17:55", s)

    def test_an_offsetless_stamp_is_read_as_utc_not_local(self):
        # naive input must not pick up the runner's zone, which is how a
        # relabel would creep back in
        self.assertEqual(f"{d.parse_iso('2026-10-23T12:49:53'):%H:%M}", "12:49")

    def test_the_delta_is_unchanged_by_the_conversion(self):
        # the bug was display-only: days_since reads the instant, so the same
        # moment in two offsets must give the same answer
        now = d.parse_iso("2026-10-23T19:49:53Z")
        a = d.days_since(d.parse_iso("2026-10-22T00:16:00Z"), now)
        b = d.days_since(d.parse_iso("2026-10-21T17:16:00-07:00"), now)
        self.assertAlmostEqual(a, b, places=9)
        self.assertAlmostEqual(a, 1.8, places=1)   # what the report prints


class Names(unittest.TestCase):
    def test_duplicate_listed_oldest_first_newest_resolves(self):
        index = {"zhou_2025_peer": ["item_response_warehouse_3", "item_response_warehouse"],
                 "alone": ["item_response_warehouse_2"]}
        dups = d.name_collisions(index, SHARDS)
        self.assertEqual(dups, {"zhou_2025_peer": [
            "item_response_warehouse.zhou_2025_peer",
            "item_response_warehouse_3.zhou_2025_peer"]})

    def test_case_only_duplicate_counts(self):
        index = {"Foo_2020": ["item_response_warehouse"],
                 "foo_2020": ["item_response_warehouse_2"]}
        self.assertIn("foo_2020", d.name_collisions(index, SHARDS))

    def test_clean_index_is_empty(self):
        self.assertEqual(d.name_collisions({"a": ["item_response_warehouse"]}, SHARDS), {})

    def test_metadata_pointing_at_the_shadowed_copy(self):
        index = {"moved": ["item_response_warehouse", "item_response_warehouse_3"],
                 "Stays": ["item_response_warehouse_2"]}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "metadata").mkdir()
            with (root / "metadata" / "metadata.csv").open("w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["table", "n_responses", "dataset"])
                w.writerow(["moved", "10", "item_response_warehouse"])
                w.writerow(["stays", "10", "item_response_warehouse_2"])
                w.writerow(["unlisted", "10", "item_response_warehouse"])
            out = d.metadata_elsewhere(root, index, SHARDS)
        self.assertEqual(out, [("moved", "item_response_warehouse",
                                "item_response_warehouse_3")])

    def test_skipped_without_credentials(self):
        c = d.check_name_collisions(Path("."), enabled=False)
        self.assertEqual(c.status, d.ERROR)


if __name__ == "__main__":
    unittest.main()
