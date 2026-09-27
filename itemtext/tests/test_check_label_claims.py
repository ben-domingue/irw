"""check_label_claims.py's two outcomes (#1745, #2049).

A positional script under a claimed data_labels exemption fails the run; the
same script under any other row only warns, and only when that row's evidence
never speaks to the ordering. Built on a throwaway data/ tree so the result
does not move with the live ledger.
"""

import csv
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SRC / "itemtext"))

import check_label_claims as clc  # noqa: E402

POSITIONAL_R = "d %>% group_by(id) %>% mutate(item = row_number())\n"
BY_NAME_R = "d %>% pivot_longer(-id, names_to = 'item', values_to = 'resp')\n"


class Screen(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (self.root / "data").mkdir()
        self.enterContext(mock.patch.object(clc, "ROOT", self.root))
        self.enterContext(mock.patch.object(clc, "DATA", self.root / "data"))

    def _run(self, rows, scripts, *flags):
        for name, body in scripts.items():
            (self.root / "data" / name).write_text(body)
        ledger = self.root / "mapping_verification.csv"
        with ledger.open("w", newline="") as fh:
            w = csv.DictWriter(fh, ["table", "batch", "mapping_basis", "uploaded",
                                    "route", "status", "evidence"])
            w.writeheader()
            for r in rows:
                w.writerow({"batch": "b", "uploaded": "2026-09-27", **r})
        out = io.StringIO()
        with redirect_stdout(out):
            code = clc.main(["x", str(ledger), *flags])
        return code, out.getvalue()

    def row(self, table, status, basis, evidence="", route=""):
        return {"table": table, "status": status, "mapping_basis": basis,
                "evidence": evidence, "route": route}

    def test_exemption_on_a_positional_script_still_fails(self):
        code, out = self._run([self.row("alpha_scale", "NOT_NEEDED", "data_labels")],
                              {"alpha_scale.R": POSITIONAL_R})
        self.assertEqual(code, 1)
        self.assertIn("[FLAG] alpha_scale", out)

    def test_verified_row_silent_on_order_warns_without_failing(self):
        code, out = self._run(
            [self.row("beta_scale", "VERIFIED", "paper_explicit",
                      evidence="Item wording matches the paper's appendix.")],
            {"beta_scale.R": POSITIONAL_R})
        self.assertEqual(code, 0)
        self.assertIn("[WARN] beta_scale (VERIFIED)", out)
        self.assertIn("1 WARN", out)

    def test_evidence_that_addresses_order_passes_quietly(self):
        for evidence in ("item k must be the k-th column after pivot_longer",
                         "surviving columns in file order = R1..C8",
                         "per-item means are mutually distinct, so every item is "
                         "distinguished from every other"):
            with self.subTest(evidence=evidence):
                code, out = self._run(
                    [self.row("gamma_scale", "VERIFIED", "paper_order",
                              evidence=evidence)],
                    {"gamma_scale.R": POSITIONAL_R})
                self.assertEqual(code, 0)
                self.assertNotIn("[WARN]", out)
                self.assertIn("1 evidence addresses the ordering", out)

    def test_in_order_to_is_not_order_evidence(self):
        code, out = self._run(
            [self.row("delta_scale", "PARTIAL", "paper_explicit",
                      evidence="Fetched the appendix in order to check wording.")],
            {"delta_scale.R": POSITIONAL_R})
        self.assertIn("[WARN] delta_scale", out)

    def test_route_column_counts_as_evidence(self):
        code, out = self._run(
            [self.row("eps_scale", "VERIFIED", "reconstructed",
                      evidence="132 of 132 match.",
                      route="route 9 response-frequency matching")],
            {"eps_scale.R": POSITIONAL_R})
        self.assertNotIn("[WARN]", out)

    def test_by_name_script_is_not_screened(self):
        code, out = self._run([self.row("zeta_scale", "VERIFIED", "paper_explicit")],
                              {"zeta_scale.R": BY_NAME_R})
        self.assertEqual(code, 0)
        self.assertIn("0 row(s) with a positional script", out)

    def test_unresolved_other_row_is_counted_not_failed(self):
        code, out = self._run([self.row("no_script_here", "VERIFIED", "paper_explicit")],
                              {})
        self.assertEqual(code, 0)
        self.assertIn("1 row(s) had no resolvable script", out)


if __name__ == "__main__":
    unittest.main()
