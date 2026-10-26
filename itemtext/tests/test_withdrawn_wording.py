"""No tracked file may carry wording for a table withdrawn on rights grounds.

A rights withdrawal removes the item text from Redivis. It does not remove the
file it was staged from, and nothing checked. On 2026-10-26 thirteen tracked
files still carried such wording, including 11 verbatim PTCI stems inside a
verification harness and three whole `__items` tables in `batch_205` whose own
withdrawal notes read "sentence-level reproduction verified against item text"
(#3228, review R-40).

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
