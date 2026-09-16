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

        with mock.patch.object(irw_batch_updated, "_landing_url", return_value=landing), \
             mock.patch.object(irw_batch_updated, "process_one", side_effect=fake_deposit):
            out = irw_batch_updated.triage_external_link(link, dict(BASE))
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
        with mock.patch.object(irw_batch_updated, "_landing_url", side_effect=OSError("down")):
            out = irw_batch_updated.triage_external_link("https://doi.org/10.1/x", dict(BASE))
        self.assertIn(out["flag"], irw_discover_plos.INCONCLUSIVE_FLAGS)


class _Resp:
    ok = True

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


class DataverseLicenseShapeTest(unittest.TestCase):
    def test_pre_5_10_string_license(self):
        payload = {"data": {"latestVersion": {"license": "CC0", "files": [
            {"dataFile": {"filename": "SAS-SV-Database.tab", "id": 7, "filesize": 9}}]}}}

        class R(_Resp):
            headers = {}
        with mock.patch.object(irw_batch_updated, "_dataverse_instance", return_value="https://datahub.tec.mx"), \
             mock.patch.object(irw_batch_updated.requests, "get", return_value=R(payload)):
            files, lic, _ = irw_batch_updated._dataverse_files("", "10.57687/FK2/DCVIJU")
        self.assertEqual(lic, "CC0")
        self.assertEqual(files[0][0], "https://datahub.tec.mx/api/access/datafile/7")


class LicenseNameTest(unittest.TestCase):
    """Spelled-out Creative Commons names, as OSF reports them.

    The 2026-09-15 backlog re-triage recorded 96 rows whose licence was an
    opaque OSF id; one (10.1371/journal.pone.0338082) was NC-SA, which has to
    block. An unreadable licence must never come out looking permissive.
    """

    def test_spelled_out_names(self):
        for raw, norm, blocked in [
            ("CC-By Attribution 4.0 International", "cc-by", False),
            ("CC-By Attribution-NonCommercial 4.0 International", "cc-by-nc", True),
            ("CC-BY Attribution-NonCommercial-ShareAlike 4.0 International", "cc-by-nc-sa", True),
            ("CC-By Attribution-NonCommercial-NoDerivatives 4.0 International", "cc-by-nc-nd", True),
            ("CC-By Attribution-ShareAlike 4.0 International", "cc-by-sa", False),
            ("CC0 1.0 Universal", "cc0", False),
            ("Creative Commons Attribution Non Commercial 4.0 International", "cc-by-nc", True),
        ]:
            got_norm, got_blocked, _ = irw_batch_updated.check_license(raw)
            self.assertEqual((got_norm, got_blocked), (norm, blocked), raw)

    def test_existing_forms_unchanged(self):
        for raw, norm in [("cc-by-4.0", "cc-by"), ("CC0", "cc0"),
                          ("https://creativecommons.org/licenses/by-nc/4.0/", "cc-by-nc"),
                          ("MIT License", "mit-license")]:
            self.assertEqual(irw_batch_updated.check_license(raw)[0], norm, raw)

    def test_opaque_id_is_never_open(self):
        _, blocked, unknown = irw_batch_updated.check_license("563c1cf88c5e4a3877f9e96a")
        self.assertTrue(unknown)
        self.assertFalse(blocked)

    def test_osf_license_prefers_embedded_name(self):
        payload = {"data": {"embeds": {"license": {"data": {"attributes": {
            "name": "CC-By Attribution-NonCommercial 4.0 International"}}}},
            "relationships": {"license": {"data": {"id": "563c1cf88c5e4a3877f9e96a"}}}}}
        with mock.patch.object(irw_batch_updated.requests, "get",
                               return_value=_Resp(payload)) as g:
            name = irw_batch_updated._osf_license("nodes", "abcde", {})
        self.assertEqual(g.call_args.kwargs["params"]["embed"], "license")
        self.assertTrue(irw_batch_updated.check_license(name)[1])

    def test_osf_license_falls_back_to_id(self):
        payload = {"data": {"relationships": {"license": {"data": {"id": "xyz"}}}}}
        with mock.patch.object(irw_batch_updated.requests, "get", return_value=_Resp(payload)):
            self.assertEqual(irw_batch_updated._osf_license("nodes", "abcde", {}), "xyz")


class TrailingPunctuationTest(unittest.TestCase):
    """A DOI scraped mid-sentence keeps the sentence's punctuation.

    "... available from https://doi.org/10.5061/dryad.j6g1c." resolved to a
    404 and the row was retired as external_unresolved. 13 of the 33 doi.org
    links in the 2026-09-15 backlog re-triage carried trailing punctuation;
    10 resolve once it is stripped.
    """

    def test_strips_sentence_punctuation(self):
        for raw, want in [
            ("https://doi.org/10.5061/dryad.j6g1c.", "https://doi.org/10.5061/dryad.j6g1c"),
            ("https://doi.org/10.18170/DVN/WBO7LK)", "https://doi.org/10.18170/DVN/WBO7LK"),
            ("https://doi.org/10.5683/SP3/S6XUE3.", "https://doi.org/10.5683/SP3/S6XUE3"),
            ("https://osf.io/abcde/,", "https://osf.io/abcde/"),
            ("https://doi.org/10.17863/CAM.121719);", "https://doi.org/10.17863/CAM.121719"),
        ]:
            self.assertEqual(irw_batch_updated.strip_trailing_punctuation(raw), want)

    def test_markdown_bracket_junk_is_cut(self):
        self.assertEqual(
            irw_batch_updated.strip_trailing_punctuation(
                "https://doi.org/10.5281/zenodo.17423755%5D(https:/doi.org/10.5281/zenodo.17423755"),
            "https://doi.org/10.5281/zenodo.17423755")

    def test_leaves_legitimate_urls_alone(self):
        for u in ["https://figshare.com/articles/dataset/x/31933275",
                  "https://osf.io/ajkh4/?view_only=13dbb2a2f98648499cbbe3cbbe8a439d",
                  "https://datahub.tec.mx/dataset.xhtml?persistentId=doi:10.57687/FK2/DCVIJU",
                  "https://doi.org/10.7910/DVN/UT9RVL"]:
            self.assertEqual(irw_batch_updated.strip_trailing_punctuation(u), u)

    def test_extractor_strips_before_storing(self):
        html = ('Data Availability:</strong> All data are available from '
                'https://doi.org/10.5061/dryad.j6g1c.</p>')
        avail = irw_discover_plos.extract_data_availability(html)
        m = irw_batch_updated._RE_URL.search(avail)
        self.assertEqual(irw_batch_updated.strip_trailing_punctuation(m.group(0)),
                         "https://doi.org/10.5061/dryad.j6g1c")


class FigshareIdTest(unittest.TestCase):
    """Legacy figshare URLs carry a trailing version segment.

    ".../articles/survey3a/7357034/1" was parsed as article 1, which 404s.
    Found 2026-09-16 while scoping the PMC gap; the deposit is live and CC BY.
    """

    def _id(self, url):
        seen = {}

        def fake_get(u, **kw):
            seen["url"] = u
            return _Resp({"license": {"name": "CC BY 4.0"}, "files": []})
        with mock.patch.object(irw_batch_updated.requests, "get", side_effect=fake_get):
            irw_batch_updated._figshare_files(url)
        return seen.get("url", "").rsplit("/", 1)[-1]

    def test_version_segment_is_not_the_id(self):
        self.assertEqual(self._id("https://figshare.com/articles/survey3a/7357034/1"), "7357034")
        self.assertEqual(self._id("https://figshare.com/articles/dataset/x/30913817/1"), "30913817")
        self.assertEqual(self._id("https://figshare.com/articles/dataset/n/6667499/2?file=1"), "6667499")

    def test_modern_and_bare_forms_unchanged(self):
        self.assertEqual(self._id("https://figshare.com/articles/dataset/Database_UDIFP-29/31933275"), "31933275")
        self.assertEqual(self._id("https://figshare.com/articles/An_examination/5544883"), "5544883")
        self.assertEqual(self._id("https://figshare.com/articles/dataset/x/27092545/"), "27092545")

    def test_no_article_id(self):
        self.assertEqual(irw_batch_updated._figshare_files("https://figshare.com/"), ([], "", []))


class DataverseProbeTest(unittest.TestCase):
    def test_version_endpoint_identifies_dataverse(self):
        with mock.patch.object(irw_batch_updated.requests, "get",
                               return_value=_Resp({"status": "OK", "data": {"version": "6.8"}})) as g:
            self.assertTrue(irw_batch_updated._is_dataverse_host("https://borealisdata.ca/collections/x"))
        self.assertEqual(g.call_args[0][0], "https://borealisdata.ca/api/info/version")

    def test_non_dataverse_host(self):
        with mock.patch.object(irw_batch_updated.requests, "get",
                               return_value=_Resp({"nope": 1})):
            self.assertFalse(irw_batch_updated._is_dataverse_host("https://data.ru.nl/collections/di/d"))

    def test_probe_failure_is_not_a_dataverse(self):
        with mock.patch.object(irw_batch_updated.requests, "get", side_effect=OSError("down")):
            self.assertFalse(irw_batch_updated._is_dataverse_host("https://example.org/x"))


if __name__ == "__main__":
    unittest.main()
