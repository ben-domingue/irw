"""reserved.py: the keyed reserved-source guard. Uses a dummy key and a dummy
list in a temp dir, so it never needs the real key."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import reserved  # noqa: E402

KEY = "test-key-not-the-real-one"
SRC = ("https://doi.org/10.5281/zenodo.1234567\n"
       "https://osf.io/ab3cd/\n"
       "https://dataverse.example.org/dataset.xhtml?persistentId=doi:10.7910/DVN/TESTX1\n"
       "https://doi.org/10.6084/m9.figshare.7654321.v2\n")

MATCH = [
    "10.5281/zenodo.1234567",
    "see https://zenodo.org/records/1234567 for data",
    "https://zenodo.org/record/1234567",
    "DOI:10.5281/ZENODO.1234567.",
    "https://osf.io/ab3cd",
    "https://osf.io/AB3CD/files/",
    "https://doi.org/10.17605/OSF.IO/AB3CD",
    "doi:10.7910/DVN/TESTX1",
    "https://dataverse.example.org/dataset.xhtml?persistentId=doi:10.7910/DVN/TESTX1&version=2.0",
    "10.6084/m9.figshare.7654321.v1",              # other version, same deposit
    "https://figshare.com/articles/dataset/some_title/7654321",
]
NO_MATCH = [
    "10.5281/zenodo.1234568",
    "https://osf.io/ab3ce/",
    "https://dataverse.example.org/dataset.xhtml?persistentId=doi:10.7910/DVN/OTHER1",
    "https://dataverse.example.org/dataset.xhtml",
    "10.1371/journal.pone.0235154",
    "",
]


class Guarded(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.env = mock.patch.dict(os.environ, {
            "IRW_RESERVED_KEY": KEY,
            "IRW_RESERVED_DROP_LOG": str(self.tmp / "drops.log")})
        self.env.start()
        self.patches = [mock.patch.object(reserved, "DROP_LOG", self.tmp / "drops.log")]
        for p in self.patches:
            p.start()
        out = io.StringIO()
        with mock.patch.object(sys, "stdin", io.StringIO(SRC)), \
                contextlib.redirect_stdout(out):
            self.assertEqual(reserved.main(["hash-ids"]), 0)
        lst = self.tmp / "reserved.txt"
        lst.write_text(out.getvalue())
        p = mock.patch.object(reserved, "RESERVED_PATH", lst)
        p.start()
        self.patches.append(p)
        reserved._reset_cache()

    def tearDown(self):
        reserved._reset_cache()
        for p in self.patches:
            p.stop()
        self.env.stop()

    def test_matches_every_form(self):
        for t in MATCH:
            with self.subTest(t):
                self.assertTrue(reserved.text_is_reserved(t))

    def test_no_false_hits(self):
        for t in NO_MATCH:
            with self.subTest(t):
                self.assertFalse(reserved.text_is_reserved(t))

    def test_list_holds_no_plain_identifiers(self):
        text = reserved.RESERVED_PATH.read_text().lower()
        for frag in ("zenodo", "osf", "1234567", "testx1", "figshare"):
            self.assertNotIn(frag, text)

    def test_drop_reserved_is_silent_and_counted(self):
        rows = [{"doi": "10.5281/zenodo.1234567", "title": "x"},
                {"doi": "10.5281/zenodo.9", "title": "y"},
                {"url": "https://osf.io/ab3cd/", "title": "z"}]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            kept = reserved.drop_reserved(rows)
        self.assertEqual([r["title"] for r in kept], ["y"])
        self.assertEqual(out.getvalue(), "")
        self.assertTrue((self.tmp / "drops.log").read_text().strip().endswith("\t2"))

    def test_hit(self):
        class Hit:
            doi, url = "", "https://osf.io/ab3cd/"
        self.assertTrue(reserved.hit_is_reserved(Hit()))

    def test_fails_closed_without_key(self):
        with mock.patch.dict(os.environ, {"IRW_RESERVED_KEY": "",
                                          "IRW_RESERVED_KEY_FILE": "/nonexistent"}), \
                mock.patch.object(reserved, "DEFAULT_KEY_FILE", Path("/nonexistent")):
            reserved._reset_cache()
            with self.assertRaises(reserved.ReservedKeyMissing):
                reserved.text_is_reserved("10.1/x")

    def test_fails_closed_with_wrong_key(self):
        with mock.patch.dict(os.environ, {"IRW_RESERVED_KEY": "wrong"}):
            reserved._reset_cache()
            with self.assertRaises(reserved.ReservedKeyMissing):
                reserved.drop_reserved([{"doi": "10.1/x"}])

    def test_check_stdin_never_prints_the_match(self):
        err = io.StringIO()
        with mock.patch.object(sys, "stdin", io.StringIO("body: https://osf.io/ab3cd/")), \
                contextlib.redirect_stderr(err):
            self.assertEqual(reserved.main(["check-stdin"]), 1)
        self.assertNotIn("ab3cd", err.getvalue().lower())


class EmptyList(unittest.TestCase):
    def test_empty_list_needs_no_key(self):
        tmp = Path(tempfile.mkdtemp())
        with mock.patch.dict(os.environ, {"IRW_RESERVED_KEY": ""}), \
                mock.patch.object(reserved, "DEFAULT_KEY_FILE", tmp / "none"), \
                mock.patch.object(reserved, "RESERVED_PATH", tmp / "missing.txt"):
            reserved._reset_cache()
            self.assertEqual(reserved.drop_reserved([{"doi": "10.1/x"}]), [{"doi": "10.1/x"}])
        reserved._reset_cache()


# Every entry point that finds, triages, stages or sends candidates calls the
# guard. The CI diff check is the backstop; this keeps the early layer intact.
CALL_SITES = {
    "irw_discover_updated.py": "hit_is_reserved(",
    "irw_discover_plos.py": "row_is_reserved(",
    "irw_discover_pmc.py": "row_is_reserved(",
    "irw_discover_plos_monthly.py": "row_is_reserved(",
    "irw_discover_pmc_monthly.py": "row_is_reserved(",
    "irw_batch_updated.py": "drop_reserved(",
    "irw_claude_assist.py": "drop_reserved(",
    "stage_dict_row.py": "row_is_reserved(",
}


class CallSites(unittest.TestCase):
    def test_call_sites(self):
        for fname, call in sorted(CALL_SITES.items()):
            with self.subTest(fname):
                self.assertIn(call, (HERE / fname).read_text(),
                              f"{fname} lost its reserved guard")

    def test_cli_help(self):
        r = subprocess.run([sys.executable, str(HERE / "reserved.py"), "--help"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
