"""Tests for the PLOS connector's Data Availability link triage.

Until 2026-09-15 a PLOS article with no tabular Supporting Information file
was flagged no_usable_file even when its Data Availability statement linked a
figshare/OSF deposit holding the data, and the seen-DOI ledger then retired it.
These pin the routing (which links reach a resolver, which get the distinct
external_unresolved flag), OSF guid handling, and that inconclusive rows stay
out of the ledger on the scheduled path. No network: every call is stubbed.
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import irw_batch_updated  # noqa: E402
import irw_discover_plos  # noqa: E402

BASE = {"source": "plos", "journal": "plosone", "title": "t",
        "doi": "10.1371/journal.pone.0000001", "url": "https://journals.plos.org/x"}


class RoutingTest(unittest.TestCase):
    def _run(self, link, landing):
        seen = {}

        def fake_deposit(row):
            seen["row"] = row
            return {"source": row["source"], "url": row["url"], "doi": row["doi"],
                    "title": "", "flag": "human_assistance", "reasons": "r",
                    "license": "cc-by", "n_responses": 10, "n_participants": 5,
                    "n_items": 2, "density": 1.0, "data_file": "d.sav"}

        with mock.patch.object(irw_discover_plos, "_landing_url", return_value=landing), \
             mock.patch.object(irw_batch_updated, "process_one", side_effect=fake_deposit):
            out = irw_discover_plos.triage_external_link(link, dict(BASE))
        return out, seen.get("row")

    def test_figshare_doi_reaches_resolver_and_keeps_plos_identity(self):
        out, row = self._run("https://doi.org/10.6084/m9.figshare.31933275",
                             "https://figshare.com/articles/dataset/x/31933275")
        self.assertEqual(row["url"], "https://figshare.com/articles/dataset/x/31933275")
        self.assertEqual(out["flag"], "human_assistance")
        self.assertEqual(out["doi"], BASE["doi"])
        self.assertEqual(out["source"], "plos")
        self.assertTrue(out["reasons"].startswith("via Data Availability link"))

    def test_non_harvard_dataverse_routes_by_source(self):
        landing = "https://datahub.tec.mx/dataset.xhtml?persistentId=doi:10.57687/FK2/DCVIJU"
        out, row = self._run("https://doi.org/10.57687/FK2/DCVIJU", landing)
        self.assertEqual(row["source"], "dataverse")
        self.assertEqual(row["doi"], "10.57687/FK2/DCVIJU")

    def test_unsupported_host_is_distinct_flag_not_no_usable_file(self):
        out, row = self._run("http://doi.org/10.4119/unibi/2788146",
                             "https://pub.uni-bielefeld.de/record/2788146")
        self.assertIsNone(row)
        self.assertEqual(out["flag"], "external_unresolved")

    def test_unresolvable_link_is_inconclusive(self):
        with mock.patch.object(irw_discover_plos, "_landing_url", side_effect=OSError("down")):
            out = irw_discover_plos.triage_external_link("https://doi.org/10.1/x", dict(BASE))
        self.assertIn(out["flag"], irw_discover_plos.INCONCLUSIVE_FLAGS)


class _Resp:
    def __init__(self, payload):
        self._p = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._p


class OsfGuidTest(unittest.TestCase):
    def test_file_guid_returns_that_file(self):
        def fake_get(url, **kw):
            if "/guids/3h5a7/" in url:
                return _Resp({"data": {"type": "files",
                                       "attributes": {"name": "data_repository.xlsx", "size": 10},
                                       "links": {"download": "https://osf.io/download/3h5a7/",
                                                 "move": "https://files.osf.io/v1/resources/uv7d2/providers/osfstorage/x"}}})
            if "/nodes/uv7d2/" in url:
                return _Resp({"data": {"relationships": {}}})
            raise AssertionError(url)
        with mock.patch.object(irw_batch_updated.requests, "get", side_effect=fake_get):
            files, _, _ = irw_batch_updated._osf_files("https://osf.io/3h5a7")
        self.assertEqual([f[1] for f in files], ["data_repository.xlsx"])

    def test_view_only_query_is_not_read_as_the_node_id(self):
        calls = []

        def fake_get(url, params=None, **kw):
            calls.append((url, dict(params or {})))
            if "/guids/" in url:
                return _Resp({"data": {"type": "nodes"}})
            if url.endswith("/nodes/ajkh4/"):
                return _Resp({"data": {"relationships": {}}})
            if "files/osfstorage" in url:
                return _Resp({"data": [
                    {"attributes": {"name": "Data", "kind": "folder"},
                     "relationships": {"files": {"links": {"related": {"href": "https://api.osf.io/sub/"}}}}}]})
            if url == "https://api.osf.io/sub/":
                return _Resp({"data": [
                    {"attributes": {"name": "wb.sav", "kind": "file", "size": 5},
                     "links": {"download": "https://osf.io/download/abc/"}}]})
            raise AssertionError(url)
        with mock.patch.object(irw_batch_updated.requests, "get", side_effect=fake_get):
            files, _, _ = irw_batch_updated._osf_files("https://osf.io/ajkh4/?view_only=KEY123")
        self.assertEqual(calls[0][0], "https://api.osf.io/v2/guids/ajkh4/")
        self.assertTrue(all(p.get("view_only") == "KEY123" for _, p in calls))
        self.assertEqual(files[0][0], "https://osf.io/download/abc/?view_only=KEY123")

    def test_bare_osf_root_has_no_guid(self):
        self.assertEqual(irw_batch_updated._osf_files("https://osf.io/"), ([], "", []))


if __name__ == "__main__":
    unittest.main()
