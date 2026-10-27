"""Tests for --per-term-cap accounting on the scheduled PLOS/PMC runs.

Until 2026-10-27 every triaged row spent the term's budget, including the
inconclusive ones. `download_failed` is in INCONCLUSIVE_FLAGS and so is never
written to the seen ledger, which means the same unreachable deposits come
back every run: the 2026-10-27 weekly run lost 34 of 54 rows to a sandbox with
no route to osf.io or figshare, 14 of those DOIs had failed in all four
October runs, and the run reported 54 candidates while reaching a verdict on
20. The cap now counts only rows that reached a verdict, bounded by
ATTEMPTS_PER_CAP so an all-unreachable term still stops (irw#3256).

No network and no filesystem state: the query, the triage and the ledger are
all stubbed.
"""
import csv
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import irw_discover_plos_monthly as plos_monthly  # noqa: E402
import irw_discover_pmc_monthly as pmc_monthly  # noqa: E402
from irw_discover_updated import Hit  # noqa: E402


class CapAccountingTest(unittest.TestCase):
    """Drives one term's inner loop with a scripted sequence of flags."""

    def _run(self, mod, flags, cap, *, out_dir, terms=1):
        """Returns (rows written, DOIs offered to the ledger)."""
        hits_per_term = len(flags)
        seq = list(flags)

        def fake_query(term, journal):
            for i in range(hits_per_term):
                yield Hit(f"src:{journal}", f"t{i}", f"https://x/{term}/{i}",
                          f"10.1/{term}.{i}")

        def fake_triage(hit, pool):
            flag = seq.pop(0) if seq else "no_usable_file"
            return ({"source": "s", "journal": "j", "title": hit.title,
                     "doi": hit.doi, "url": hit.url, "flag": flag,
                     "reasons": ""}, pool)

        recorded = []
        out = Path(out_dir) / "out.csv"
        query_name = "from_plos" if mod is plos_monthly else "from_pmc"
        terms_attr = "HIGH_YIELD_TERMS"

        with mock.patch.object(mod, query_name, fake_query), \
             mock.patch.object(mod, "process_one_isolated", fake_triage), \
             mock.patch.object(mod, terms_attr, [f"term{i}" for i in range(terms)]), \
             mock.patch.object(mod, "load_seen_dois", lambda: set()), \
             mock.patch.object(mod, "_load_auto_exclusions", lambda: set()), \
             mock.patch.object(mod, "append_seen_dois", recorded.extend), \
             mock.patch.object(mod, "resolve_out_path", lambda *a: str(out)), \
             mock.patch.object(mod, "_append_log_rows", lambda *a, **k: None), \
             mock.patch.object(mod, "preflight_deps", lambda: None), \
             mock.patch("irw_retriage_ha.chain_step2b", lambda *a, **k: None), \
             mock.patch.object(sys, "argv",
                               ["x", "--mode", "weekly", "--per-term-cap", str(cap),
                                "--limit", "999"]):
            mod.main()

        with open(out, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f)), [d for d, _ in recorded]

    def test_inconclusive_rows_do_not_spend_the_cap(self):
        """Two failures then two verdicts: the cap of 2 is met by the verdicts."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            rows, ledgered = self._run(
                plos_monthly,
                ["download_failed", "download_failed", "no_usable_file", "good",
                 "good"],
                cap=2, out_dir=d)
        flags = [r["flag"] for r in rows]
        self.assertEqual(flags, ["download_failed", "download_failed",
                                 "no_usable_file", "good"])
        # Only the two conclusive rows reached the ledger.
        self.assertEqual(len(ledgered), 2)

    def test_all_unreachable_term_stops_at_the_attempt_bound(self):
        """A term whose every deposit fails must not walk its whole result set."""
        import tempfile
        cap = 3
        with tempfile.TemporaryDirectory() as d:
            rows, ledgered = self._run(
                plos_monthly, ["download_failed"] * 40, cap=cap, out_dir=d)
        self.assertEqual(len(rows), cap * plos_monthly.ATTEMPTS_PER_CAP)
        self.assertEqual(ledgered, [])

    def test_pmc_connector_has_the_same_accounting(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            rows, ledgered = self._run(
                pmc_monthly,
                ["download_failed", "license_lookup_failed", "good"],
                cap=1, out_dir=d)
        self.assertEqual([r["flag"] for r in rows],
                         ["download_failed", "license_lookup_failed", "good"])
        self.assertEqual(len(ledgered), 1)


if __name__ == "__main__":
    unittest.main()
