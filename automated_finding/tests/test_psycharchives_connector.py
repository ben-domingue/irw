"""PsychArchives (ZPID) discovery connector and file resolver.

Added 2026-10-29 with from_psycharchives(). The repository had been reaching
us only through DataCite, where all 35 of its DOIs died as "licence unknown"
or `no_usable_file` -- so the two things worth pinning are the two that were
broken: that a record's DOI is recovered at all, and that `dc.rights.uri`
becomes the licence.

PsychArchives carries NO `dc.identifier.doi` field. The DOI is the
`dx.doi.org` member of a repeated `dc.identifier.uri` pair whose other member
is a handle, so a parser that keeps one value per key loses it -- which is
why _psycharchives_meta() keeps a list per key.

unittest, not pytest: CI runs `python -m unittest discover` over every test
directory (.github/workflows/tests.yml) and pytest is not installed there.
"""
import unittest
from unittest import mock

import irw_batch_updated as batch
import irw_discover_updated as disc


def _item(uuid="2f38b068-ed30-4dec-8bae-558bd4485172",
          handle="20.500.12034/2382", dctype="researchData",
          rights_uri="https://creativecommons.org/licenses/by-sa/4.0/"):
    return {
        "uuid": uuid,
        "handle": handle,
        "name": "Raw Data for: Psychometric analysis of a questionnaire",
        "metadata": [
            {"key": "dc.contributor.author", "value": "Chasiotis, A."},
            {"key": "dc.contributor.author", "value": "Wedderhoff, O."},
            {"key": "dc.identifier.uri",
             "value": f"https://hdl.handle.net/{handle}"},
            {"key": "dc.identifier.uri",
             "value": "http://dx.doi.org/10.23668/psycharchives.2771"},
            {"key": "dc.date.issued", "value": "2020"},
            {"key": "dc.rights", "value": "openAccess"},
            {"key": "dc.rights.uri", "value": rights_uri},
            {"key": "dc.type", "value": dctype},
        ],
    }


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class MetadataFlattening(unittest.TestCase):
    def test_repeated_keys_are_kept(self):
        md = disc._psycharchives_meta(_item())
        self.assertEqual(len(md["dc.identifier.uri"]), 2)
        self.assertEqual(len(md["dc.contributor.author"]), 2)

    def test_missing_key_is_empty(self):
        self.assertEqual(
            disc._psycharchives_first(disc._psycharchives_meta(_item()),
                                      "dc.identifier.doi"), "")


class DiscoveryHits(unittest.TestCase):
    def _hits(self, items, **kw):
        with mock.patch.object(disc.requests, "get",
                               return_value=_Resp({"items": items})):
            return list(disc.from_psycharchives("questionnaire",
                                                max_pages=1, per=50, **kw))

    def test_doi_comes_off_the_identifier_pair(self):
        hits = self._hits([_item()])
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].doi, "10.23668/psycharchives.2771")
        self.assertEqual(hits[0].source, "psycharchives")
        self.assertEqual(hits[0].published, "2020")

    def test_url_is_the_item_page_the_resolver_reads(self):
        self.assertEqual(
            self._hits([_item()])[0].url,
            "https://www.psycharchives.org/en/item/"
            "2f38b068-ed30-4dec-8bae-558bd4485172")

    def test_non_data_types_are_dropped_locally(self):
        # The server-side `dc.type equals researchData` filter is
        # approximate -- a `code` or `test` record leaks through roughly one
        # in twenty -- and ZPID's whole Open Test Archive is `test`, i.e.
        # blank instruments with no responses attached.
        self.assertEqual(self._hits([_item(dctype="code"),
                                     _item(dctype="test")]), [])

    def test_one_record_found_by_two_fields_is_yielded_once(self):
        # title and description.abstract are searched in separate passes.
        with mock.patch.object(disc.requests, "get",
                               return_value=_Resp({"items": [_item()]})):
            hits = list(disc.from_psycharchives("q", max_pages=1, per=50))
        self.assertEqual(len(hits), 1)

    def test_api_failure_is_a_source_outage_not_an_empty_result(self):
        with mock.patch.object(disc.requests, "get",
                               side_effect=RuntimeError("502")):
            with self.assertRaises(disc.SourceUnavailable):
                list(disc.from_psycharchives("q", max_pages=1, per=50))


class FileResolution(unittest.TestCase):
    def _resolve(self, bitstreams, rights_uri=None, url=None):
        item = _item() if rights_uri is None else _item(rights_uri=rights_uri)
        payload = dict(item, bitstreams=bitstreams)
        with mock.patch.object(batch.requests, "get",
                               return_value=_Resp(payload)):
            return batch._psycharchives_files(
                url or "https://www.psycharchives.org/en/item/"
                       "2f38b068-ed30-4dec-8bae-558bd4485172", "")

    def test_rights_uri_becomes_an_open_licence(self):
        files, lic, over = self._resolve(
            [{"name": "data.csv", "sizeBytes": 1024,
              "retrieveLink": "/rest/bitstreams/abc/retrieve"}])
        self.assertEqual(batch.check_license(lic), ("cc-by-sa", False, False))
        self.assertEqual(
            files,
            [("https://www.psycharchives.org/rest/bitstreams/abc/retrieve",
              "data.csv", 1024)])
        self.assertEqual(over, [])

    def test_scientific_use_license_reads_as_unknown_and_so_skips(self):
        # restrictedAccess deposits -- 139 of the first 400 Research Data
        # records -- point dc.rights.uri at a signed-agreement document, not
        # a licence we can redistribute under.
        _, lic, _ = self._resolve(
            [], rights_uri="https://doi.org/10.23668/psycharchives.4988")
        self.assertTrue(batch.check_license(lic)[2])

    def test_non_tabular_bitstreams_are_ignored(self):
        files, _, _ = self._resolve(
            [{"name": "readme.pdf", "sizeBytes": 10,
              "retrieveLink": "/rest/bitstreams/p/retrieve"}])
        self.assertEqual(files, [])

    def test_oversized_file_is_reported_not_returned(self):
        files, _, over = self._resolve(
            [{"name": "huge.csv", "sizeBytes": batch.MAX_FILE_BYTES + 1,
              "retrieveLink": "/rest/bitstreams/h/retrieve"}])
        self.assertEqual(files, [])
        self.assertEqual(over, [("huge.csv", batch.MAX_FILE_BYTES + 1)])

    def test_handle_url_resolves_too(self):
        files, _, _ = self._resolve(
            [{"name": "d.csv", "sizeBytes": 5,
              "retrieveLink": "/rest/bitstreams/d/retrieve"}],
            url="https://hdl.handle.net/20.500.12034/2382")
        self.assertEqual(len(files), 1)

    def test_unrecognised_url_returns_nothing_rather_than_guessing(self):
        self.assertEqual(
            batch._psycharchives_files("https://www.psycharchives.org/", ""),
            ([], "", []))

    def test_host_dispatch_reaches_the_resolver(self):
        self.assertIs(
            batch._host_resolver("https://www.psycharchives.org/en/item/x"),
            batch._psycharchives_files)


class DataCiteDeduplication(unittest.TestCase):
    def test_zpid_publisher_is_skipped_now_it_has_its_own_connector(self):
        skip = disc._effective_datacite_skip()
        self.assertTrue(
            any(s in "leibniz institute for psychology (zpid)" for s in skip))

    def test_skip_lifts_when_the_connector_is_blocked(self):
        with mock.patch.object(disc, "blocked_sources",
                               return_value={"psycharchives"}):
            skip = disc._effective_datacite_skip()
        self.assertFalse(
            any(s in "leibniz institute for psychology (zpid)" for s in skip))


if __name__ == "__main__":
    unittest.main()
