"""Unit tests for metadata/check_client_reach.py (ben-domingue/irw#3091, item 8).

The failure mode worth testing is the one the script exists to catch, inverted:
a check that reports every client current because it compared nothing. Two
tests are load-bearing for that -- `test_empty_catalog_is_an_error` and
`test_short_catalog_is_an_error` -- because an unread catalog and a complete
one are indistinguishable from the output alone.

Everything here is offline. That the fetchers handle the real CRAN tarball,
PyPI sdist and Redivis catalog is checked by running the script, which the
drift report does daily.
"""

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import check_client_reach as ccr  # noqa: E402


def catalog(*rows: tuple) -> str:
    """A catalog response. Each row is (reference, refid, version|None, public)."""
    results = []
    for ref, refid, version, public in rows:
        scoped = f"{ref}:{refid}" + (f":{version}" if version else "")
        results.append({"scopedReference": scoped,
                        "publicAccessLevel": "data" if public else "overview",
                        "tableCount": 100})
    return json.dumps({"results": results})


def filler(n: int) -> tuple:
    """Datasets that are not IRW shards, to clear the catalog floor."""
    return tuple((f"other_dataset_{i}", "abcd", "v1_0", True) for i in range(n))


class LiveShardsTest(unittest.TestCase):
    def live(self, payload: str):
        with mock.patch.object(ccr, "fetch", return_value=payload):
            return ccr.live_shards()

    def test_unpublished_shard_is_not_live(self):
        """Two fields in scopedReference means no published version."""
        live = self.live(catalog(("item_response_warehouse_8", "xyz1", None, True),
                                 *filler(25)))
        self.assertNotIn("item_response_warehouse_8", live)

    def test_private_shard_is_not_live(self):
        live = self.live(catalog(("item_response_warehouse_8", "xyz1", "v1_0", False),
                                 *filler(25)))
        self.assertNotIn("item_response_warehouse_8", live)

    def test_reference_comes_from_scoped_reference(self):
        live = self.live(catalog(("irw_rank", "aaaa", "v1_2", True), *filler(25)))
        self.assertEqual(live["irw_rank"].version, "v1_2")

    def test_empty_catalog_is_an_error(self):
        """The cheapest way to make this check green is to compare nothing."""
        with self.assertRaises(ccr.ReachError):
            self.live(json.dumps({"results": []}))

    def test_short_catalog_is_an_error(self):
        with self.assertRaises(ccr.ReachError):
            self.live(catalog(*filler(ccr.MIN_LIVE_DATASETS - 1)))

    def test_missing_results_array_is_an_error(self):
        with self.assertRaises(ccr.ReachError):
            self.live(json.dumps({"nothing": True}))


class GapTest(unittest.TestCase):
    def setUp(self):
        with mock.patch.object(ccr, "fetch", return_value=catalog(
                ("item_response_warehouse", "as2e", "v74_0", True),
                ("item_response_warehouse_7", "ej0d", "v1_3", True),
                ("irw_text", "bbbb", "v9_0", True),
                ("irw_brand_new_family", "cccc", "v1_0", True),
                *filler(25))):
            self.live = ccr.live_shards()

    def client(self, datasets, discovery=False):
        c = ccr.Client("x", "client", version="1.0", discovery=discovery,
                       datasets=set(datasets))
        c.missing = ccr.gaps(c, self.live)
        return c

    def test_a_shard_extending_a_configured_family_is_a_gap(self):
        c = self.client(["item_response_warehouse", "irw_text"])
        self.assertEqual([s.reference for s in c.missing],
                         ["item_response_warehouse_7"])

    def test_a_new_family_is_not_a_gap(self):
        """No client adopts a new family silently, so it is not this check's question."""
        c = self.client(["item_response_warehouse", "item_response_warehouse_7",
                         "irw_text"])
        self.assertEqual(c.missing, [])
        self.assertEqual(c.status, ccr.CURRENT)

    def test_a_gap_without_discovery_is_silent(self):
        c = self.client(["item_response_warehouse", "irw_text"], discovery=False)
        self.assertEqual(c.status, ccr.SILENT)

    def test_a_gap_with_discovery_is_loud(self):
        c = self.client(["item_response_warehouse", "irw_text"], discovery=True)
        self.assertEqual(c.status, ccr.LOUD)

    def test_an_errored_client_is_never_current(self):
        c = ccr.Client("x", "client", error="CRAN did not answer")
        self.assertEqual(c.status, ccr.ERROR)


class FamilyTest(unittest.TestCase):
    def test_numeric_suffix_is_the_shard(self):
        self.assertEqual(ccr.family_of("item_response_warehouse_7"),
                         "item_response_warehouse")
        self.assertEqual(ccr.family_of("irw_conjoint_2"), "irw_conjoint")

    def test_a_name_with_no_suffix_is_its_own_family(self):
        self.assertEqual(ccr.family_of("irw_rank"), "irw_rank")

    def test_a_trailing_word_is_not_a_suffix(self):
        """`irw_textual` must not read as a shard of `irw_text`."""
        self.assertNotEqual(ccr.family_of("irw_textual"), "irw_text")


class ParserFloorTest(unittest.TestCase):
    def test_a_config_parsed_to_nothing_is_an_error(self):
        """Delegated to check_config_parity's floor; verify it still propagates."""
        with self.assertRaises(ccr.ReachError):
            ccr._parse_config("IRW_CORE_DATASETS <- c()\n",
                              ccr.ccp.parse_rpkg_config, "test", ".R")


if __name__ == "__main__":
    unittest.main(verbosity=2)
