#!/usr/bin/env python3
"""Tests for 20_k1.py (#3273, from #3232).

    python3 -m unittest metadata.tests.test_k1 -v
    python3 metadata/tests/test_k1.py

Nothing here touches Redivis. What is tested is the part that decides which
columns count as quasi-identifiers and what the rates mean -- the regex above
all, because the whole value of the column is that it is comparable with the
2026-10-28 baseline #3232 was decided on, and a quietly edited regex breaks
that without breaking anything that would fail.
"""

import importlib.util
import os
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("k1", HERE.parent / "20_k1.py")
k1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k1)


def row(*cols):
    return {"variables": "| ".join(("id", "item", "resp") + cols)}


class TestQiColumns(unittest.TestCase):
    def test_demographics_count(self):
        self.assertEqual(k1.qi_columns(row("cov_age", "cov_sex", "cov_education")),
                         ["cov_age", "cov_education", "cov_sex"])

    def test_experimental_columns_do_not_count(self):
        """Condition, study, group and sample are not quasi-identifiers: they
        say what was done to a respondent, not who they are."""
        self.assertEqual(k1.qi_columns(row("cov_condition", "cov_study",
                                           "cov_group", "cov_sample")), [])

    def test_required_columns_do_not_count(self):
        self.assertEqual(k1.qi_columns(row()), [])

    def test_dates_and_timestamps_count(self):
        """The 2026-10-28 widening. friedman's start and end timestamps were
        missing from its first reported 99.2%; a survey start time is close to
        a unique key, and the true figure is 100%."""
        self.assertEqual(
            k1.qi_columns(row("cov_startdate", "cov_enddate", "cov_sduration")),
            ["cov_enddate", "cov_sduration", "cov_startdate"])

    def test_the_bare_date_column_is_not_a_cov_column(self):
        """298 tables carry the standard-mandated second-precision `date`
        column. That is a standard question (#3232), not one of these: only
        `cov_*` names are considered here."""
        self.assertEqual(k1.qi_columns(row("date")), [])

    def test_age_variants_across_the_corpus_all_count(self):
        """cov_age is not one thing: months on an infant screener, birth year
        elsewhere, eight decimal places in teicher_2015."""
        for c in ("cov_age", "cov_age_m", "cov_birth_year", "cov_dob",
                  "cov_maternal_age"):
            self.assertEqual(k1.qi_columns(row(c)), [c], c)

    def test_separator_is_pipe_with_spaces_as_metadata_csv_writes_it(self):
        """metadata.csv stores `variables` as "id| item| cov_age" -- unstripped,
        the regex anchor never matches and every table reads as zero QIs."""
        self.assertEqual(k1.qi_columns({"variables": "id| item| resp| cov_age"}),
                         ["cov_age"])

    def test_missing_variables_is_not_fatal(self):
        self.assertEqual(k1.qi_columns({}), [])
        self.assertEqual(k1.qi_columns({"variables": None}), [])

    def test_duplicates_are_collapsed(self):
        self.assertEqual(k1.qi_columns(row("cov_age", "cov_age")), ["cov_age"])


class TestNoQiRow(unittest.TestCase):
    def test_no_quasi_identifier_means_nobody_is_alone(self):
        """One cell holding everyone: no respondent is unique on columns the
        table does not publish."""
        r = k1.no_qi_row({"table": "t", "_n_participants": 500.0})
        self.assertEqual(r["k1_prop"], "0")
        self.assertEqual(r["cells"], "1")
        self.assertEqual(r["status"], "no_qi")

    def test_a_single_respondent_is_alone_even_with_no_columns(self):
        r = k1.no_qi_row({"table": "t", "_n_participants": 1.0})
        self.assertEqual(r["k1_prop"], "1")

    def test_an_empty_table_is_blank_not_zero(self):
        r = k1.no_qi_row({"table": "t", "_n_participants": 0.0})
        self.assertEqual(r["k1_prop"], "")


class TestSummarise(unittest.TestCase):
    def test_no_stored_row_leaves_both_columns_blank(self):
        """A table not yet reached must be blank, not zero: 0 would read as
        'nobody is unique here', which is a finding, not an absence."""
        self.assertEqual(k1.summarise(None),
                         {"k1_prop": "", "n_quasi_identifiers": ""})

    def test_columns_come_straight_from_the_store(self):
        self.assertEqual(
            k1.summarise({"status": "ok", "k1_prop": "0.41", "n_qi": "5"}),
            {"k1_prop": "0.41", "n_quasi_identifiers": "5"})


class TestK1Sql(unittest.TestCase):
    def test_groups_by_every_quasi_identifier_backquoted(self):
        sql = k1.k1_sql("datapages", "irw_3", "t", ["cov_age", "cov_sex"])
        self.assertIn("GROUP BY `cov_age`, `cov_sex`", sql)

    def test_id_is_not_cast(self):
        """Stage 19 casts id to STRING because BigQuery refuses to PARTITION BY
        a FLOAT64. There is no window function here, and the baseline was
        measured uncast over 2,942 tables with no failures -- casting would be a
        silent change to a published number."""
        sql = k1.k1_sql("datapages", "irw_3", "t", ["cov_age"])
        self.assertIn("COUNT(DISTINCT id)", sql)
        self.assertNotIn("CAST(id", sql)

    def test_counts_respondents_not_cells_in_the_numerator(self):
        """SUM(IF(c=1,c,0)) sums cell sizes over cells of one, which is the
        number of respondents alone -- COUNT of those cells would be the same
        number by luck, and SUM(c) over all cells is the denominator."""
        sql = k1.k1_sql("datapages", "irw_3", "t", ["cov_age"])
        self.assertIn("SUM(IF(c=1,c,0)) AS k1", sql)
        self.assertIn("SUM(c) AS people", sql)

    def test_k_under_five_is_carried_too(self):
        self.assertIn("SUM(IF(c<5,c,0)) AS klt5",
                      k1.k1_sql("datapages", "irw_3", "t", ["cov_age"]))


class TestPlanBatches(unittest.TestCase):
    @staticmethod
    def t(name, resp=0):
        return {"table": name, "_n_responses": resp}

    def test_table_count_cap(self):
        b = k1.plan_batches([self.t(f"t{i}") for i in range(70)])
        self.assertEqual([len(x) for x in b], [30, 30, 10])

    def test_response_cap_splits_heavy_tables(self):
        big = k1.MAX_RESP_PER_BATCH // 2 + 1
        b = k1.plan_batches([self.t("a", big), self.t("b", big), self.t("c", big)])
        self.assertEqual([len(x) for x in b], [1, 1, 1])

    def test_one_oversized_table_still_gets_its_own_batch(self):
        b = k1.plan_batches([self.t("huge", k1.MAX_RESP_PER_BATCH * 10)])
        self.assertEqual([len(x) for x in b], [1])

    def test_queue_order_is_preserved(self):
        names = [f"t{i}" for i in range(40)]
        b = k1.plan_batches([self.t(n) for n in names])
        self.assertEqual([x["table"] for bb in b for x in bb], names)


class TestRegexIsPinned(unittest.TestCase):
    """The regex is a published constant, not an implementation detail.

    Every figure the column can be checked against -- the corpus median of
    18.9%, friedman at 100% -- is conditioned on this exact pattern, measured
    2026-10-28 (`oneoff/k-anonymity-3232/`). Editing it silently changes
    published numbers while breaking nothing that would fail, so the pattern
    itself is pinned here rather than any count derived from the corpus: a count
    would go stale the next time a table with three covariates is added, and a
    check that reddens on ordinary data merges is one whose baseline gets raised
    until it is silent.

    If you MEANT to change the regex, re-measure the corpus, update the figures
    in the stage header, `ARCHITECTURE.md` and `datastandard.md` with it, and
    then update this digest -- in that order."""

    BASELINE = "5e3f8f8e58b112b7"

    def test_quasi_identifier_pattern_has_not_been_edited(self):
        import hashlib
        got = hashlib.sha256(k1.QI.pattern.encode()).hexdigest()[:16]
        self.assertEqual(got, self.BASELINE,
                         "the quasi-identifier regex changed; see this test's "
                         "docstring before updating the digest")

    def test_the_date_arm_is_present(self):
        """Belt and braces on the one arm that is easy to lose, since it was
        added after the first run rather than with it."""
        for c in ("cov_startdate", "cov_enddate", "cov_sduration", "cov_time",
                  "cov_assess_date", "cov_date", "cov_timestamp"):
            self.assertTrue(k1.QI.match(c), c)


class TestCorpusBaseline(unittest.TestCase):
    """Opt-in reproduction of #3232's work set: K1_BASELINE=1 to run.

    run_k1.py selected 2,942 core tables as carrying three or more
    quasi-identifiers on 2026-10-28, and this stage reproduced that count
    exactly -- which is what established that the regex and the `variables`
    parse agree with the baseline. It is deliberately NOT a CI assertion: the
    count rises whenever a table with three covariates is ingested, and that is
    the corpus growing, not a defect."""

    def setUp(self):
        if not os.environ.get("K1_BASELINE"):
            self.skipTest("set K1_BASELINE=1 to check against the 2026-10-28 run")
        self.meta = k1.read_csv(k1.METADATA)
        if not self.meta:
            self.skipTest("no metadata.csv in this checkout")

    def test_three_or_more_qi_reproduces_2942_tables(self):
        n = sum(1 for r in self.meta if len(k1.qi_columns(r)) >= 3)
        self.assertEqual(n, 2942)


class TestFriedman(unittest.TestCase):
    """The single-table check #3273 names as the cheapest one available."""

    def setUp(self):
        meta = k1.read_csv(k1.METADATA)
        rows = [r for r in meta
                if r.get("table") == "friedman_2018_risks_discrimination"]
        if not rows:
            self.skipTest("friedman_2018_risks_discrimination not in this checkout")
        self.row = rows[0]

    def test_it_publishes_twelve_quasi_identifiers(self):
        """12, not 9: the three date and timestamp columns the first run missed.
        This is the table whose rate the widening moved from 99.2% to 100%."""
        qi = k1.qi_columns(self.row)
        self.assertEqual(len(qi), 12, qi)
        for c in ("cov_startdate", "cov_enddate", "cov_sduration"):
            self.assertIn(c, qi)

    def test_its_experimental_and_party_dummy_columns_are_excluded(self):
        """cov_democrat, cov_independent and cov_republican are the one-hot of
        cov_party, which is counted. Counting all four would weight party four
        times over and inflate the cell count for nothing."""
        qi = k1.qi_columns(self.row)
        for c in ("cov_democrat", "cov_independent", "cov_republican"):
            self.assertNotIn(c, qi)


if __name__ == "__main__":
    unittest.main()
