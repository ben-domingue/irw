"""check_label_harvest.py (#2770): advisory, never failing."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("clh", HERE / "check_label_harvest.py")
clh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clh)


class CheckLabelHarvestTest(unittest.TestCase):
    def script(self, body):
        d = tempfile.mkdtemp()
        p = Path(d) / "data" / "foo_2026.R"
        p.parent.mkdir()
        p.write_text(body)
        clh.REPO = Path(d)
        return "data/foo_2026.R"

    def test_spss_reader_writing_covariates_without_labels_is_flagged(self):
        s = self.script('x <- haven::read_sav("a.sav")\ndf$cov_gender <- x$sex\n')
        self.assertTrue(clh.needs_harvest(s, set()))

    def test_already_harvested_is_not_flagged_even_with_no_labels_found(self):
        s = self.script('x <- haven::read_sav("a.sav")\ndf$cov_gender <- x$sex\n')
        self.assertFalse(clh.needs_harvest(s, {"foo_2026"}))

    def test_csv_reader_or_no_covariates_is_not_flagged(self):
        self.assertFalse(clh.needs_harvest(self.script('x <- read.csv("a.csv")\ndf$cov_g <- 1\n'), set()))
        self.assertFalse(clh.needs_harvest(self.script('x <- haven::read_sav("a.sav")\n'), set()))

    def test_listed_as_not_harvestable_is_not_flagged(self):
        s = self.script('x <- haven::read_sav("a.sav")\ndf$cov_gender <- x$sex\n')
        t = Path(tempfile.mkdtemp()) / "not_harvestable.tsv"
        t.write_text("script\treason\ndata/sub/foo_2026.R\tchecked by hand\n")
        clh.STATUS, clh.NOT_HARVESTABLE = Path("/nonexistent.tsv"), t
        self.assertFalse(clh.needs_harvest(s, clh.harvested()))

    def test_never_fails(self):
        s = self.script('x <- haven::read_sav("a.sav")\ndf$cov_gender <- x$sex\n')
        clh.STATUS = Path("/nonexistent.tsv")
        self.assertEqual(clh.main([s, "--annotate"]), 0)


if __name__ == "__main__":
    unittest.main()
