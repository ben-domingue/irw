"""Offline tests for the IRW version manifest. No network, no credentials.

    python3 -m unittest discover -s red_up/tests

The version properties here are shaped like the ones Redivis returns, and the
overwritten-timestamp fixtures are copied from the real shape of the damage:
a run of consecutive versions whose `releasedAt` all land inside one short
window long after they were created. See red_up/manifest.py.
"""

from __future__ import annotations

import datetime as dt
import tempfile
import unittest
from pathlib import Path

from red_up.manifest import (
    BRACKETED,
    EXACT,
    Release,
    build,
    classify,
    diverges,
    parse_date,
    read,
    snapshot,
    version_at,
    write,
)

DAY = 86_400_000
HOUR = 3_600_000
BASE = 1_700_000_000_000       # some moment in 2023


def version(dataset: str, index: int, tag: str, created: int,
            released: int | None, is_released: bool = True) -> dict:
    return {"_dataset": dataset, "index": index, "tag": tag,
            "createdAt": created, "releasedAt": released,
            "isReleased": is_released}


class Classify(unittest.TestCase):
    def test_genuine_history_is_exact(self):
        raw = [
            version("d", 0, "v1.0", BASE, BASE + HOUR),
            version("d", 1, "v1.1", BASE + 2 * DAY, BASE + 2 * DAY + HOUR),
            version("d", 2, "v2.0", BASE + 9 * DAY, BASE + 9 * DAY + HOUR),
        ]
        out = classify(raw)
        self.assertEqual([r.precision for r in out], [EXACT] * 3)
        self.assertEqual([r.tag for r in out], ["v1.0", "v1.1", "v2.0"])

    def test_drafts_are_dropped(self):
        """An unreleased draft cannot be fetched by a reader, so it is not a pin."""
        raw = [
            version("d", 0, "v1.0", BASE, BASE + HOUR),
            version("d", 1, "next", BASE + DAY, None, is_released=False),
        ]
        self.assertEqual([r.tag for r in classify(raw)], ["v1.0"])

    def test_overwritten_run_is_bracketed(self):
        """The real damage: releasedAt rewritten into one window years later.

        Redivis allows one draft at a time, so a version released *after* its
        successor's draft was opened is impossible -- that is what gives the
        rewrite away, with no date hardcoded anywhere.
        """
        migration = BASE + 900 * DAY
        raw = [
            version("d", 0, "v1.0", BASE, migration),
            version("d", 1, "v1.1", BASE + 30 * DAY, migration + 1000),
            version("d", 2, "v2.0", BASE + 90 * DAY, migration + 2000),
            # genuine again, well after the migration
            version("d", 3, "v3.0", migration + 5 * DAY, migration + 5 * DAY + HOUR),
        ]
        out = classify(raw)
        self.assertEqual([r.precision for r in out],
                         [BRACKETED, BRACKETED, BRACKETED, EXACT])

    def test_last_of_a_run_is_caught_by_the_window_pass(self):
        """v2.0 below has a genuine successor, so the ordering test misses it.

        Only the second pass -- it shares the migration's timestamp window with
        versions the first pass did flag -- catches it. This is the case that
        made a single-pass rule wrong on the real data by exactly two versions.
        """
        migration = BASE + 900 * DAY
        raw = [
            version("d", 0, "v1.0", BASE, migration),
            version("d", 1, "v1.1", BASE + 30 * DAY, migration + 1000),
            version("d", 2, "v2.0", BASE + 90 * DAY, migration + 2000),
            version("d", 3, "v3.0", migration + 60 * DAY, migration + 61 * DAY),
        ]
        out = classify(raw)
        self.assertEqual(out[2].precision, BRACKETED,
                         "the last version of an overwritten run must not pass "
                         "as exact just because its successor is genuine")

    def test_bracket_bounds(self):
        migration = BASE + 900 * DAY
        raw = [
            version("d", 0, "v1.0", BASE, migration),
            version("d", 1, "v1.1", BASE + 30 * DAY, migration + 1000),
        ]
        first = classify(raw)[0]
        self.assertEqual(first.released_at.timestamp() * 1000, BASE)
        self.assertEqual(first.released_before.timestamp() * 1000, BASE + 30 * DAY)

    def test_final_bracketed_version_has_an_open_upper_bound(self):
        migration = BASE + 900 * DAY
        raw = [
            version("d", 0, "v1.0", BASE, migration),
            version("d", 1, "v1.1", BASE + 30 * DAY, migration + 1000),
        ]
        self.assertIsNone(classify(raw)[1].released_before)


def release(dataset: str, tag: str, at: int, precision: str = EXACT) -> Release:
    when = dt.datetime.fromtimestamp(at / 1000, tz=dt.timezone.utc)
    return Release(dataset=dataset, tag=tag, index=0, created_at=when,
                   released_at=when, precision=precision)


ORDER = ["a", "b"]


class Build(unittest.TestCase):
    def test_snapshot_carries_unchanged_datasets_forward(self):
        rows = build([release("a", "v1", BASE),
                      release("b", "v1", BASE + DAY),
                      release("a", "v2", BASE + 2 * DAY)], ORDER)
        self.assertEqual({(r.release.dataset, r.release.tag)
                          for r in snapshot(rows, 3)},
                         {("a", "v2"), ("b", "v1")})

    def test_a_dataset_absent_before_its_first_release(self):
        """v1 predates dataset b entirely; inventing a pin for it would lie."""
        rows = build([release("a", "v1", BASE), release("b", "v1", BASE + DAY)],
                     ORDER)
        self.assertEqual([r.release.dataset for r in snapshot(rows, 1)], ["a"])

    def test_simultaneous_releases_are_one_irw_version(self):
        rows = build([release("a", "v1", BASE), release("b", "v1", BASE)], ORDER)
        self.assertEqual(max(r.irw_version for r in rows), 1)
        self.assertEqual(len(snapshot(rows, 1)), 2)

    def test_datasets_keep_registry_order_within_a_snapshot(self):
        rows = build([release("b", "v1", BASE), release("a", "v1", BASE + DAY)],
                     ORDER)
        self.assertEqual([r.release.dataset for r in snapshot(rows, 2)], ["a", "b"])


class Lookup(unittest.TestCase):
    def setUp(self):
        self.rows = build([release("a", "v1", BASE),
                           release("a", "v2", BASE + 10 * DAY)], ORDER)

    def test_version_at_returns_the_one_in_force(self):
        when = dt.datetime.fromtimestamp((BASE + 5 * DAY) / 1000, tz=dt.timezone.utc)
        self.assertEqual(version_at(self.rows, when), 1)

    def test_version_at_is_none_before_the_corpus_existed(self):
        when = dt.datetime.fromtimestamp((BASE - DAY) / 1000, tz=dt.timezone.utc)
        self.assertIsNone(version_at(self.rows, when))

    def test_parse_date_accepts_a_bare_day(self):
        self.assertEqual(parse_date("2026-08-01").year, 2026)

    def test_parse_date_rejects_nonsense(self):
        with self.assertRaises(ValueError):
            parse_date("last tuesday")


class RoundTrip(unittest.TestCase):
    def test_write_then_read_preserves_everything(self):
        rows = build([release("a", "v1", BASE, BRACKETED),
                      release("b", "v1", BASE + DAY)], ORDER)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.tsv"
            write(rows, path)
            back = read(path)
        self.assertEqual([(r.irw_version, r.release.dataset, r.release.tag,
                           r.release.precision) for r in back],
                         [(r.irw_version, r.release.dataset, r.release.tag,
                           r.release.precision) for r in rows])

    def test_read_of_a_missing_file_is_empty_not_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(read(Path(tmp) / "nope.tsv"), [])


class NeverRenumber(unittest.TestCase):
    """An IRW version number is a citation. It must never come to mean something
    else, so a rebuild that would change one has to be refused, not written."""

    def setUp(self):
        self.existing = build([release("a", "v1", BASE),
                               release("a", "v2", BASE + DAY)], ORDER)

    def test_appending_is_fine(self):
        fresh = build([release("a", "v1", BASE), release("a", "v2", BASE + DAY),
                       release("a", "v3", BASE + 2 * DAY)], ORDER)
        self.assertIsNone(diverges(self.existing, fresh))

    def test_an_earlier_release_appearing_would_renumber(self):
        """A version that shows up dated before ones already numbered shifts
        every number after it -- the case that silently repoints citations."""
        fresh = build([release("a", "v0", BASE - DAY), release("a", "v1", BASE),
                       release("a", "v2", BASE + DAY)], ORDER)
        self.assertIsNotNone(diverges(self.existing, fresh))

    def test_a_changed_tag_is_caught(self):
        fresh = build([release("a", "v1", BASE),
                       release("a", "v2-corrected", BASE + DAY)], ORDER)
        self.assertIsNotNone(diverges(self.existing, fresh))

    def test_a_disappearing_version_is_caught(self):
        fresh = build([release("a", "v1", BASE)], ORDER)
        self.assertIsNotNone(diverges(self.existing, fresh))


if __name__ == "__main__":
    unittest.main()
