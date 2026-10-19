"""The leads filter's licence test, which has now been wrong three ways.

0. It was cc0/cc-by/cc-by-sa only while `datastandard.md` had said since
   2026-10-01 that NC proceeds, and `check_license()` in irw_batch_updated.py
   had allowed NC all along. Aligned 2026-10-19 (ben-domingue): NC passes, ND
   does not. These cases are the ones that keep the two apart.

1. `"cc-by-nc".startswith("cc-by")` is true, so a naive prefix test passes NC
   (#3083 -- three CC BY-NC deposits reached a lead list that way).
2. OSF reports a licence by NAME, "CC-By Attribution-NonCommercial 4.0
   International", so a token test for {"nc","nd"} never fires on it while the
   prefix test passes it. Three OSF keys the ledger had correctly flagged
   `license_restricted` came back "open".
3. Zenodo's own licence id for CC0 1.0 is `cc-zero`, which fails a
   `startswith("cc0")` test, so every CC0 Zenodo deposit would read as
   unknown if the licence came straight from the API.

unittest, not pytest: CI runs `python -m unittest discover` over every test
directory (.github/workflows/tests.yml) and pytest is not installed there.
"""
import unittest

from remine_ledger import is_nc, licence_code, licence_ok

OPEN = [
    "cc0", "CC0 1.0", "CC0 1.0 Universal",
    "cc-zero",                                  # Zenodo's id for CC0 1.0
    "cc-zero-1.0",
    "cc-by", "cc-by-4.0", "CC-BY-4.0",
    "cc-by-sa", "CC-BY-SA-4.0",
    # Non-commercial, allowed since 2026-10-19; the NC carries into
    # Derived_License rather than disappearing.
    "cc-by-nc", "cc-by-nc-4.0", "cc-by-nc-sa", "CC-BY-NC-SA-4.0",
    "CC-By Attribution-NonCommercial 4.0 International",
    "CC-By Attribution-NonCommercial-ShareAlike 4.0 International",
    "<a href='http://creativecommons.org/licenses/by-nc/4.0/'>CC BY-NC</a>",
    "CC-By Attribution 4.0 International",      # OSF, by name
    "CC-By Attribution-ShareAlike 4.0 International",
    "http://creativecommons.org/publicdomain/zero/1.0/",
    "http://creativecommons.org/licenses/by-sa/4.0/",
    # a Dataverse installation may answer with a block of HTML (heiDATA)
    "Licensed under a <a href='http://creativecommons.org/licenses/by/4.0/'>"
    "Creative Commons Attribution 4.0 International License.</a>",
]

CLOSED = [
    "", "unknown", "all rights reserved", "all-rights-reserved",
    # ND forbids the reshaping IRW does, so it stops whatever else it carries.
    "cc-by-nd", "cc-by-nc-nd-4.0", "cc-by-nd-4.0",
    "CC-By Attribution-NoDerivatives 4.0 International",
    "CC-By Attribution-NonCommercial-NoDerivatives 4.0 International",
    "<a href='http://creativecommons.org/licenses/by-nc-nd/4.0/'>CC BY-NC-ND</a>",
]


class OpenLicencesPass(unittest.TestCase):
    def test_each(self):
        for lic in OPEN:
            with self.subTest(lic=lic):
                self.assertTrue(licence_ok(lic),
                                f"{lic!r} -> {licence_code(lic)!r}")


class RestrictedLicencesFail(unittest.TestCase):
    def test_each(self):
        for lic in CLOSED:
            with self.subTest(lic=lic):
                self.assertFalse(licence_ok(lic),
                                 f"{lic!r} -> {licence_code(lic)!r}")


class ZenodoCcZeroNormalises(unittest.TestCase):
    def test_cc_zero_is_cc0(self):
        self.assertEqual(licence_code("cc-zero"), "cc0")
        self.assertEqual(licence_code("CC-Zero"), "cc0")


class NcIsDistinguishedFromNd(unittest.TestCase):
    """NC is a lead; ND is not. The two must never be conflated."""

    def test_nc_detected_both_spellings(self):
        for lic in ("cc-by-nc", "cc-by-nc-sa",
                    "CC-By Attribution-NonCommercial 4.0 International"):
            with self.subTest(lic=lic):
                self.assertTrue(is_nc(lic))

    def test_nd_is_never_nc(self):
        for lic in ("cc-by-nd", "cc-by-nc-nd-4.0",
                    "CC-By Attribution-NoDerivatives 4.0 International"):
            with self.subTest(lic=lic):
                self.assertFalse(is_nc(lic), lic)
                self.assertFalse(licence_ok(lic), lic)

    def test_nc_is_a_lead(self):
        """The 2026-10-19 alignment: NC passes the filter, ND does not."""
        for lic in ("cc-by-nc", "cc-by-nc-sa",
                    "CC-By Attribution-NonCommercial 4.0 International"):
            with self.subTest(lic=lic):
                self.assertTrue(licence_ok(lic), lic)

    def test_open_licences_are_not_nc(self):
        for lic in ("cc-by", "cc0", "cc-zero", "cc-by-sa"):
            with self.subTest(lic=lic):
                self.assertFalse(is_nc(lic))


if __name__ == "__main__":
    unittest.main()
