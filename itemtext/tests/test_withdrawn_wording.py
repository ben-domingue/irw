"""No tracked file may carry wording for a table we may not publish.

A rights withdrawal removes the item text from Redivis. It does not remove the
file it was staged from, and nothing checked. On 2026-10-26 thirteen tracked
files still carried such wording, including 11 verbatim PTCI stems inside a
verification harness and three whole `__items` tables in `batch_205` whose own
withdrawal notes read "sentence-level reproduction verified against item text"
(#3228, review R-40).

Widened 2026-10-28. `withdrawals.csv` only records text that SHIPPED and was
then pulled, so an instrument blocked at triage -- PROMIS, PANAS, the MLQ
translations, CAST-18 -- had no row and was invisible here. 33 more wording
CSVs were tracked for exactly that reason, found by intersecting the local
store's filenames with `git ls-files`. The check now also reads
`itemtext/blocked_wording_tables.csv`, which carries table names only.

This asserts the state, not the fix: it fails for any file the check finds, so
a future batch cannot re-stage one quietly.
"""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / "itemtext" / "check_withdrawn_wording.py"


class TestWithdrawnWording(unittest.TestCase):
    def test_the_local_store_is_not_a_path_inside_the_repo(self):
        """`data/itemtext/` here would be the public tree, not the store.

        The store is ~/Dropbox/projects/irw/data/itemtext/ and the repo root is
        src/, so the two paths read identically in prose and differ by one
        directory on disk. A gitignore entry stops an accidental `git add`;
        this stops a forced one, and fires even on an untracked directory so
        the mistake is caught before anything is staged.
        """
        self.assertFalse(
            (ROOT / "data" / "itemtext").exists(),
            msg=(
                "data/itemtext/ exists INSIDE the repo. The store of wording "
                "we may not publish belongs outside it, at "
                "~/Dropbox/projects/irw/data/itemtext/ (#3016). Move it."
            ),
        )

    def test_no_tracked_wording_for_a_rights_withdrawal(self):
        result = subprocess.run(
            [sys.executable, str(CHECK)],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(
            result.returncode, 0,
            msg=(
                "itemtext/check_withdrawn_wording.py found tracked wording for "
                "a table withdrawn on rights grounds:\n"
                + result.stdout + result.stderr
            ),
        )


if __name__ == "__main__":
    unittest.main()
