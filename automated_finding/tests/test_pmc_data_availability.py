"""Tests for the PMC connector's Data Availability handoff.

irw_discover_pmc.py used to stop at "the supplementary archive holds nothing
tabular" and retire the DOI, never reading the article's Data Availability
statement. That is the mistake #2191 fixed for PLOS at a cost of 395
recoverable candidates. These pin the JATS extraction (three markup shapes,
because publishers disagree), the handoff's fallbacks, and the shared-module
split that keeps the two connectors from importing each other. No network.
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import irw_batch_updated  # noqa: E402
import irw_discover_pmc  # noqa: E402

SEC = ('<body><sec sec-type="data-availability"><title>Data availability</title>'
       '<p>The data are available at <ext-link xlink:href="https://osf.io/nvek2/">'
       'https://osf.io/nvek2/</ext-link>.</p></sec></body>')
NOTES = ('<back><notes notes-type="data-availability"><title>Data Availability Statement</title>'
         '<p>All files are on figshare: https://doi.org/10.6084/m9.figshare.27092545</p>'
         '</notes></back>')
TITLED = ('<back><sec><title>Data Availability Statement</title>'
          '<p>Available from the corresponding author on reasonable request.</p></sec></back>')
NONE = "<body><sec><title>Methods</title><p>We ran a survey.</p></sec></body>"


class ExtractTest(unittest.TestCase):
    def test_sec_type(self):
        das = irw_discover_pmc.extract_data_availability(SEC)
        self.assertIn("osf.io/nvek2", das)
        self.assertNotIn("<", das)

    def test_notes_type(self):
        das = irw_discover_pmc.extract_data_availability(NOTES)
        self.assertIn("figshare.27092545", das)

    def test_title_fallback(self):
        das = irw_discover_pmc.extract_data_availability(TITLED)
        self.assertIn("corresponding author", das)

    def test_absent(self):
        self.assertEqual(irw_discover_pmc.extract_data_availability(NONE), "")
        self.assertEqual(irw_discover_pmc.extract_data_availability(""), "")


class HandoffTest(unittest.TestCase):
    def _handoff(self, xml, base=None):
        base = base if base is not None else {"doi": "10.1/x"}
        with mock.patch.object(irw_discover_pmc, "fetch_fulltext_xml", return_value=xml):
            return irw_discover_pmc._data_availability_handoff("PMC1", base, "si reason")

    def test_link_is_handed_to_the_shared_resolver(self):
        with mock.patch.object(irw_discover_pmc, "triage_external_link",
                               return_value={"flag": "human_assistance", "reasons": "r"}) as t:
            row = self._handoff(SEC)
        self.assertEqual(t.call_args[0][0], "https://osf.io/nvek2/")
        self.assertEqual(row["flag"], "human_assistance")

    def test_statement_and_link_are_recorded_on_the_row(self):
        base = {"doi": "10.1/x"}
        with mock.patch.object(irw_discover_pmc, "triage_external_link",
                               return_value={"flag": "good", "reasons": ""}):
            self._handoff(NOTES, base)
        self.assertIn("figshare", base["data_availability"])
        self.assertEqual(base["external_link"],
                         "https://doi.org/10.6084/m9.figshare.27092545")

    def test_statement_without_a_link_keeps_the_callers_verdict(self):
        self.assertIsNone(self._handoff(TITLED))

    def test_no_statement_keeps_the_callers_verdict(self):
        self.assertIsNone(self._handoff(NONE))

    def test_unfetchable_full_text_keeps_the_callers_verdict(self):
        with mock.patch.object(irw_discover_pmc, "fetch_fulltext_xml",
                               side_effect=OSError("502")):
            self.assertIsNone(
                irw_discover_pmc._data_availability_handoff("PMC1", {}, "si reason"))

    def test_unresolved_host_reports_the_si_failure_not_plos_wording(self):
        with mock.patch.object(irw_discover_pmc, "triage_external_link",
                               return_value={"flag": "external_unresolved",
                                             "reasons": "no tabular-format Supporting "
                                                        "Information file; data link on a "
                                                        "host with no resolver: https://x/y"}):
            row = self._handoff(SEC)
        self.assertTrue(row["reasons"].startswith("si reason | "))
        self.assertNotIn("Supporting Information", row["reasons"])


class SharedModuleTest(unittest.TestCase):
    def test_link_helpers_live_in_the_shared_module(self):
        for name in ("extract_external_link", "triage_external_link",
                     "strip_trailing_punctuation", "_landing_url"):
            self.assertTrue(hasattr(irw_batch_updated, name), name)

    def test_connectors_do_not_import_each_other(self):
        import re
        pmc = Path(irw_discover_pmc.__file__).read_text()
        # Statements only -- the file may mention the other connector in prose.
        self.assertIsNone(re.search(r"^\s*(?:from|import)\s+irw_discover_plos",
                                    pmc, re.MULTILINE))

    def test_new_columns_are_in_fieldnames(self):
        self.assertIn("data_availability", irw_discover_pmc.FIELDNAMES)
        self.assertIn("external_link", irw_discover_pmc.FIELDNAMES)


if __name__ == "__main__":
    unittest.main()
