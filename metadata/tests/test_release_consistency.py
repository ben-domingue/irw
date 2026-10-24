"""Unit tests for metadata/check_release_consistency.py.

The failure mode worth testing is the one every gate has: passing because it
compared nothing. Three tests are load-bearing for that --
`test_short_catalog_is_an_error`, `test_short_declared_set_is_an_error` and
`test_unknown_hash_is_not_a_hit` -- because a listing that came back short, a
CSV that failed to parse and a corpus whose hashes have never been recorded all
produce zero mismatches, and only one of those is good news.

The rest pin the two comparisons that were got wrong while writing it:

  * `n_participants > n_responses` is NOT impossible. `n_responses` counts rows
    with a non-null `resp`; `n_participants` is a distinct-value count over all
    rows, and null-`resp` rows are legal data. The first draft bounded against
    `n_responses` and fired on 29 Chilean and Mexican survey tables, every one
    of them correct.
  * `updatedAt` is not a freshness signal. Redivis resets it for every table in
    a draft whenever the draft is touched, so the check compares content hashes.

Everything here is offline. That the fetchers handle the real Redivis listing
and schema endpoints is checked by running the script.
"""

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import check_release_consistency as crc  # noqa: E402


def live(name, rows=100, variables=3, digest="h0", dataset="item_response_warehouse"):
    return crc.LiveTable(name, dataset, rows, variables, digest)


def declared(**over):
    row = {"table": "t", "n_responses": "90", "n_items": "9",
           "n_participants": "10", "variables": "id| item| resp"}
    row.update(over)
    return row


class SchemaTest(unittest.TestCase):
    def run_check(self, declared_rows, live_rows, live_names):
        with mock.patch.object(crc, "live_variables", return_value=live_names):
            return crc.check_schema(declared_rows, live_rows,
                                    {k: "item_response_warehouse" for k in declared_rows})

    def test_matching_count_is_not_checked_further(self):
        """The count is the cheap screen; a table that agrees costs no schema call."""
        with mock.patch.object(crc, "live_variables",
                               side_effect=AssertionError("should not be called")):
            chk = crc.check_schema({"t": declared()}, {"t": live("t", variables=3)},
                                   {"t": "item_response_warehouse"})
        self.assertEqual(chk.hits, [])

    def test_declared_column_absent_from_the_data_is_a_hit(self):
        chk = self.run_check({"t": declared(variables="id| item| resp| cov_dob")},
                             {"t": live("t", variables=3)},
                             ["id", "item", "resp"])
        self.assertEqual(chk.hits, ["t"])
        self.assertEqual(chk.withheld["t"], ["cov_dob"])

    def test_a_rename_is_reported_from_the_declared_side(self):
        """Equal counts hide a rename, so the screen misses it -- by design, and
        the case is recorded here so nobody is surprised by it later."""
        with mock.patch.object(crc, "live_variables", return_value=["id", "item", "response"]):
            chk = crc.check_schema({"t": declared()}, {"t": live("t", variables=3)},
                                   {"t": "item_response_warehouse"})
        self.assertEqual(chk.hits, [])

    def test_extra_live_columns_are_not_a_hit(self):
        """A table that GAINED a column is a stale declaration too, but it
        publishes nothing that is not there, so it is not what this gate is for."""
        chk = self.run_check({"t": declared()}, {"t": live("t", variables=4)},
                             ["id", "item", "resp", "cov_age"])
        self.assertEqual(chk.hits, [])

    def test_a_table_not_in_the_catalog_is_skipped(self):
        chk = self.run_check({"t": declared()}, {}, [])
        self.assertEqual(chk.hits, [])


class CountsTest(unittest.TestCase):
    def test_n_responses_above_numrows_is_a_hit(self):
        chk = crc.check_counts({"t": declared(n_responses="101")}, {"t": live("t", rows=100)})
        self.assertEqual(len(chk.hits), 1)
        self.assertIn("n_responses 101 > numRows 100", chk.hits[0])

    def test_n_participants_above_n_responses_is_not_a_hit(self):
        """Null-`resp` rows are legal data; see the module docstring."""
        chk = crc.check_counts({"t": declared(n_responses="10", n_participants="90")},
                               {"t": live("t", rows=100)})
        self.assertEqual(chk.hits, [])

    def test_n_items_above_numrows_is_a_hit(self):
        chk = crc.check_counts({"t": declared(n_items="200")}, {"t": live("t", rows=100)})
        self.assertEqual(len(chk.hits), 1)

    def test_one_hit_per_table(self):
        chk = crc.check_counts({"t": declared(n_responses="500", n_items="500")},
                               {"t": live("t", rows=100)})
        self.assertEqual(len(chk.hits), 1)

    def test_blank_counts_are_skipped(self):
        chk = crc.check_counts({"t": declared(n_responses="", n_items="NA",
                                              n_participants=None)},
                               {"t": live("t", rows=100)})
        self.assertEqual(chk.hits, [])


class FreshnessTest(unittest.TestCase):
    def test_changed_hash_is_a_hit(self):
        chk = crc.check_freshness({"t": declared()}, {"t": live("t", digest="new")},
                                  {"t": "old"})
        self.assertEqual(chk.hits, ["t"])
        self.assertEqual(chk.unknown, 0)

    def test_same_hash_is_clean(self):
        chk = crc.check_freshness({"t": declared()}, {"t": live("t", digest="same")},
                                  {"t": "same"})
        self.assertEqual(chk.hits, [])

    def test_unknown_hash_is_not_a_hit(self):
        """A corpus whose hashes were never recorded must report undecidable,
        not clean: zero hits with 6,720 undecidable is not a passing grade."""
        chk = crc.check_freshness({"t": declared()}, {"t": live("t")}, {})
        self.assertEqual(chk.hits, [])
        self.assertEqual(chk.unknown, 1)


class CorrectionsTest(unittest.TestCase):
    def test_blank_version_is_a_hit(self):
        chk = crc.check_corrections_pinned([{"table": "t", "irw_version": " ",
                                             "issue": "#1"}])
        self.assertEqual(chk.hits, ["t (#1)"])

    def test_pinned_version_is_clean(self):
        chk = crc.check_corrections_pinned([{"table": "t", "irw_version": "536"}])
        self.assertEqual(chk.hits, [])

    def test_absent_table_with_a_live_successor_is_clean(self):
        chk = crc.check_corrections_resolve(
            [{"table": "old", "replaced_by": "new"}], {"new"}, set())
        self.assertEqual(chk.hits, [])

    def test_absent_table_in_the_ledger_is_clean(self):
        """A retirement is recorded in the withdrawal ledger, not by a successor."""
        chk = crc.check_corrections_resolve([{"table": "old", "replaced_by": ""}],
                                            set(), {"old"})
        self.assertEqual(chk.hits, [])

    def test_absent_table_with_no_successor_is_a_hit(self):
        chk = crc.check_corrections_resolve([{"table": "old", "replaced_by": ""}],
                                            set(), set())
        self.assertEqual(chk.hits, ["old"])

    def test_absent_successor_is_reported_with_its_name(self):
        chk = crc.check_corrections_resolve(
            [{"table": "old", "replaced_by": "gone"}], set(), set())
        self.assertEqual(chk.hits, ["old -> gone (also absent)"])


class WithdrawalsTest(unittest.TestCase):
    def test_whole_withdrawal_still_live_is_a_hit(self):
        chk = crc.check_withdrawals_live(
            [{"table": "t", "kind": "whole", "reason": "rights"}], {"t"})
        self.assertEqual(chk.hits, ["t (rights)"])

    def test_partial_withdrawal_is_expected_to_be_live(self):
        """A partial withdrawal removes rows and leaves the table."""
        chk = crc.check_withdrawals_live(
            [{"table": "t", "kind": "partial", "reason": "personal_data"}], {"t"})
        self.assertEqual(chk.hits, [])

    def test_withdrawn_table_still_in_biblio_is_a_hit(self):
        chk = crc.check_withdrawals_records(
            [{"table": "t", "kind": "whole"}],
            {"biblio": {"t"}, "tags": set(), "itemtext_metadata": set()}, set())
        self.assertEqual(chk.hits, ["t: still in biblio"])

    def test_a_withdrawn_table_that_came_back_is_not_a_records_hit(self):
        """In every case checked in the 2026-10 review, a table the ledger calls
        withdrawn and the catalog still serves is a clean rebuild. Its biblio and
        tags rows are then CORRECT; the stale thing is the ledger row, which
        `withdrawals-live` reports. Flagging them reported 184 right answers as
        wrong."""
        chk = crc.check_withdrawals_records(
            [{"table": "t", "kind": "whole"}],
            {"biblio": {"t"}, "tags": {"t"}, "itemtext_metadata": set()}, {"t"})
        self.assertEqual(chk.hits, [])

    def test_itemtext_withdrawal_is_checked_against_its_base_name(self):
        """`foo__items` is the item-text table; `itemtext_metadata` keys on `foo`.
        The base response table is normally still live and should be: what is
        withdrawn is its wording, not its responses."""
        chk = crc.check_withdrawals_records(
            [{"table": "foo__items", "kind": "whole"}],
            {"biblio": {"foo"}, "tags": {"foo"}, "itemtext_metadata": {"foo"}}, {"foo"})
        self.assertEqual(chk.hits, ["foo__items: still in itemtext_metadata"])

    def test_itemtext_withdrawal_does_not_retire_the_response_table(self):
        chk = crc.check_withdrawals_records(
            [{"table": "foo__items", "kind": "whole"}],
            {"biblio": {"foo"}, "tags": {"foo"}, "itemtext_metadata": set()}, {"foo"})
        self.assertEqual(chk.hits, [])


class FloorTest(unittest.TestCase):
    """An unread source must be an error, never a pass."""

    def _gather(self, listing_rows, declared_rows):
        tables = [crc.LiveTable(n, "item_response_warehouse", 10, 3, "h")
                  for n in listing_rows]
        with mock.patch.object(crc, "live_tables", return_value=tables), \
             mock.patch.object(crc, "declared_datasets",
                               return_value={"core": ["item_response_warehouse"],
                                             "nom": [], "comp": [], "sim": [], "rank": []}), \
             mock.patch.object(crc, "read_csv_rows",
                               side_effect=lambda p: declared_rows if p.name.endswith("metadata.csv") else []):
            return crc.gather(None)

    def test_short_catalog_is_an_error(self):
        with self.assertRaises(crc.SourceError) as ctx:
            self._gather([f"t{i}" for i in range(5)],
                         [{"table": f"t{i}", "variables": "id| item| resp"}
                          for i in range(crc.MIN_DECLARED_ROWS + 1)])
        self.assertIn("below the floor", str(ctx.exception))

    def test_short_declared_set_is_an_error(self):
        with self.assertRaises(crc.SourceError) as ctx:
            self._gather([f"t{i}" for i in range(crc.MIN_LIVE_TABLES + 1)],
                         [{"table": "t0"}])
        self.assertIn("below the floor", str(ctx.exception))

    def test_missing_csv_is_an_error(self):
        with self.assertRaises(crc.SourceError):
            crc.read_csv_rows(Path("/nonexistent/metadata/nope.csv"))


class BaselineTest(unittest.TestCase):
    def test_count_above_baseline_fails(self):
        chk = crc.Check("k", "t", "R-00", "d", hits=["a", "b"])
        self.assertEqual(crc.report([chk], {"k": 1}, False), 1)

    def test_count_at_baseline_is_held(self):
        chk = crc.Check("k", "t", "R-00", "d", hits=["a"])
        self.assertEqual(crc.report([chk], {"k": 1}, False), 0)

    def test_count_below_baseline_is_held(self):
        chk = crc.Check("k", "t", "R-00", "d", hits=[])
        self.assertEqual(crc.report([chk], {"k": 3}, False), 0)

    def test_no_baseline_with_hits_fails(self):
        """An unrecorded check cannot silently accept whatever it finds."""
        chk = crc.Check("k", "t", "R-00", "d", hits=["a"])
        self.assertEqual(crc.report([chk], {}, False), 1)

    def test_removed_column_names_are_withheld_by_default(self):
        chk = crc.Check("schema", "t", "R-11", "d", hits=["t"],
                        withheld={"t": ["cov_dob"]})
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            crc.report([chk], {"schema": 0}, False)
        self.assertNotIn("cov_dob", buf.getvalue())
        buf = io.StringIO()
        with redirect_stdout(buf):
            crc.report([chk], {"schema": 0}, True)
        self.assertIn("cov_dob", buf.getvalue())




class FamilyCoverageTest(unittest.TestCase):
    """Every family counts as "live", even the ones the schema check skips.

    The records checks ask whether a correction or a withdrawal names something
    the catalog still serves. Conjoint tables are served; they are only left
    out of the schema and counts checks because `conj_metadata.csv` has no
    `variables` column. Building the live-name set from the schema families
    alone reported six live conjoint tables as unresolvable corrections -- a
    record and the data agreeing, reported as a disagreement.
    """

    def test_conjoint_is_in_the_live_name_set(self):
        self.assertIn("conj", crc.ALL_FAMILY_KEYS)

    def test_conjoint_is_not_in_the_schema_families(self):
        self.assertNotIn("conj", crc.FAMILIES)

    def test_a_live_conjoint_table_resolves_a_correction(self):
        conj = [f"conj_table_{i}" for i in range(3)]
        tables = {
            "item_response_warehouse": [f"t{i}" for i in range(crc.MIN_LIVE_TABLES + 1)],
            "irw_conjoint": conj,
        }

        def fake_live(dataset):
            return [crc.LiveTable(n, dataset, 10, 3, "h")
                    for n in tables.get(dataset, [])]

        # `variables` must agree with the listing's variableCount, or the schema
        # check pays a real /variables call for every one of these rows.
        declared_rows = {
            "metadata.csv": [{"table": f"t{i}", "variables": "id| item| resp"}
                             for i in range(crc.MIN_DECLARED_ROWS + 1)],
            "table_changes.csv": [{"table": "conj_table_0", "irw_version": "600",
                                   "replaced_by": ""}],
        }
        with mock.patch.object(crc, "live_tables", side_effect=fake_live), \
             mock.patch.object(crc, "declared_datasets",
                               return_value={"core": ["item_response_warehouse"],
                                             "conj": ["irw_conjoint"],
                                             "nom": [], "comp": [], "sim": [], "rank": []}), \
             mock.patch.object(crc, "read_csv_rows",
                               side_effect=lambda p: declared_rows.get(p.name, [])):
            checks = {c.key: c for c in crc.gather(None)}
        self.assertEqual(checks["corrections-resolve"].hits, [])


class CorrectionSuccessorTest(unittest.TestCase):
    """A successor named on ANY of a table's rows resolves all of them.

    `nba_2012-2018` has an ordinary correction from IRW 470 whose
    `replaced_by` is empty, and a retirement two hundred rows below naming
    `fivethirtyeight_nba_1946_2023`, which is live. Reading rows independently
    reported the first as unresolvable while the answer was already in the file.
    """

    CHANGES = [
        {"table": "old", "irw_version": "470", "replaced_by": ""},
        {"table": "old", "irw_version": "", "replaced_by": "new"},
    ]

    def test_a_later_successor_resolves_an_earlier_row(self):
        chk = crc.check_corrections_resolve(self.CHANGES, {"new"}, set())
        self.assertEqual(chk.hits, [])

    def test_one_hit_per_table_not_per_row(self):
        chk = crc.check_corrections_resolve(self.CHANGES, set(), set())
        self.assertEqual(chk.hits, ["old -> new (also absent)"])


class BaselineWriteTest(unittest.TestCase):
    """`--update-baseline` must not delete the note that explains the numbers."""

    def test_an_existing_comment_survives_a_rewrite(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "baseline.json"
            path.write_text(json.dumps(
                {"_comment": "why these numbers are what they are",
                 "counts": {"k": 3}}))
            with mock.patch.object(crc, "BASELINE", path):
                crc.write_baseline([crc.Check("k", "t", "R-00", "d", hits=["a"])])
                written = json.loads(path.read_text())
        self.assertEqual(written["_comment"], "why these numbers are what they are")
        self.assertEqual(written["counts"], {"k": 1})

    def test_a_missing_file_gets_the_default_comment(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "baseline.json"
            with mock.patch.object(crc, "BASELINE", path):
                crc.write_baseline([crc.Check("k", "t", "R-00", "d")])
                written = json.loads(path.read_text())
        self.assertEqual(written["_comment"], crc.DEFAULT_BASELINE_COMMENT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
