"""Tests for the data/ script contract check. Offline, no network, no repo state."""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from irw_validate.contract import check_script, main  # noqa: E402

GOOD = '''
import pandas as pd
from irw_triage_updated import run_qc

df = pd.read_csv("raw_export_from_the_repository_2019.csv")
checks = run_qc(df)
assert not [c for c in checks if c.status == "fail"]
df.to_csv("author_2026_scale.csv", index=False)
'''

NO_VALIDATOR = '''
import pandas as pd
df = pd.read_csv("raw.csv")
df.to_csv("author_2026_scale.csv", index=False)
'''


def write(d, name, body):
    p = pathlib.Path(d) / name
    p.write_text(body)
    return p


class Contract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def checks(self, body, name="s_2026_x.py", **kw):
        return {f.check for f in check_script(write(self.tmp.name, name, body), **kw)}

    def test_a_conforming_script_is_clean(self):
        self.assertEqual(self.checks(GOOD), set())

    def test_an_input_filename_is_not_a_table_name(self):
        # the check once flagged 94 scripts for the length of a file they READ
        self.assertNotIn("name_length", self.checks(GOOD))

    def test_writing_without_validating_is_an_error(self):
        self.assertIn("no_validator", self.checks(NO_VALIDATOR))

    def test_validating_after_writing_is_not_a_gate(self):
        body = ('import pandas as pd\nfrom irw_triage_updated import run_qc\n'
                'df = pd.read_csv("r.csv")\ndf.to_csv("a_2026_x.csv")\nrun_qc(df)\n')
        self.assertIn("validator_after_write", self.checks(body))

    def test_a_local_absolute_path_is_an_error(self):
        body = GOOD.replace('"raw_export_from_the_repository_2019.csv"',
                            '"/Users/someone/Desktop/raw.csv"')
        self.assertIn("local_path", self.checks(body))

    def test_a_commented_out_local_path_is_ignored(self):
        body = GOOD + '\n# old: input_file = "/Users/someone/raw.csv"\n'
        self.assertNotIn("local_path", self.checks(body))

    def test_an_over_long_written_name_is_an_error(self):
        body = GOOD.replace("author_2026_scale.csv", "a" * 41 + ".csv")
        self.assertIn("name_length", self.checks(body))

    def test_a_name_assigned_to_a_variable_is_still_checked(self):
        body = GOOD.replace('df.to_csv("author_2026_scale.csv", index=False)',
                            f'out = "{"a" * 41}.csv"\ndf.to_csv(out, index=False)')
        self.assertIn("name_length", self.checks(body))

    def test_a_name_already_in_the_corpus_warns(self):
        got = self.checks(GOOD, corpus={"author_2026_scale"})
        self.assertIn("name_taken", got)

    def test_r_scripts_get_the_text_checks_only(self):
        body = 'd <- read.csv("/Users/someone/raw.csv")\n'
        got = self.checks(body, name="s_2026_x.R")
        self.assertEqual(got, {"local_path"})

    def test_a_file_that_does_not_parse_is_reported_not_crashed(self):
        self.assertIn("syntax", self.checks("def (:\n"))


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_added_files_block(self):
        p = write(self.tmp.name, "new_2026_x.py", NO_VALIDATOR)
        self.assertEqual(main(["--added", str(p)]), 1)

    def test_modified_files_never_block(self):
        # 776 of 843 existing scripts would fail no_validator; blocking on an
        # edit to one of them would stall the queue this check exists to unstick
        p = write(self.tmp.name, "old_2019_x.py", NO_VALIDATOR)
        self.assertEqual(main(["--modified", str(p)]), 0)

    def test_a_clean_added_file_passes(self):
        p = write(self.tmp.name, "new_2026_x.py", GOOD)
        self.assertEqual(main(["--added", str(p)]), 0)

    def test_nothing_to_check_is_success(self):
        self.assertEqual(main([]), 0)


if __name__ == "__main__":
    unittest.main()
