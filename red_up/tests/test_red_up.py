"""Offline tests for red_up. No network, no credentials.

    python3 -m unittest discover -s red_up/tests

Everything that talks to Redivis lives in push.py/verify.py/plan.index_tables
and is exercised by the end-to-end procedure in red_up/README.md instead.
"""

from __future__ import annotations

import tempfile
import builtins
from unittest import mock
import unittest
from pathlib import Path

from red_up import cli
from red_up import plan as planning
from red_up.checks import check_all, check_schema, scan, validate_for_target
from red_up.discover import discover, table_name
from red_up.targets import (
    ConfigError,
    required_columns,
    Target,
    eligible,
    guess_target,
    load_registry,
    newest_shard,
    newest_text_shard,
    text_shards,
)

RESPONSE = "id,item,resp\n1,a,1\n2,a,0\n"
ITEMS = "table,item,item_text\nt,a,hello\n"


def write(directory: Path, name: str, body: str) -> Path:
    path = directory / name
    path.write_text(body)
    return path


class Registry(unittest.TestCase):
    """The dataset list is parsed from metadata/redivis_config.R, not restated."""

    def test_matches_the_authoritative_config(self):
        owner, targets = load_registry()
        self.assertEqual(owner, "datapages")
        names = [t.name for t in targets]
        core = [t.name for t in targets if t.kind == "core"]
        text = [t.name for t in text_shards(targets)]
        aux = [t.name for t in targets
               if t.kind == "aux" and not t.is_itemtext]

        # Both families are shard lists that grow, so assert their shape rather
        # than a frozen tail -- pinning the newest name here means every future
        # shard breaks this test for no reason.
        self.assertEqual(core[0], "item_response_warehouse")
        self.assertEqual(core[1:],
                         [f"item_response_warehouse_{i}" for i in range(2, len(core) + 1)])
        self.assertEqual(text[0], "irw_text")
        self.assertEqual(text[1:],
                         [f"irw_text_{i}" for i in range(2, len(text) + 1)])

        # The four plain aux datasets are a fixed set; item text is not among
        # them, because it is declared as IRW_TEXT_DATASETS.
        self.assertEqual(sorted(aux),
                         ["irw_competitions", "irw_meta", "irw_nominal", "irw_simsyn"])

        # Core first, then text shards, then the rest -- the menu order.
        self.assertEqual(names, core + text + aux)
        self.assertEqual(newest_shard(targets).name, core[-1])
        self.assertEqual(newest_text_shard(targets).name, text[-1])

    def test_item_text_declared_twice_is_refused(self):
        # The three "single source of truth" files drifted once (#1733).
        # Declaring item text in both places here is the same failure in one
        # file, so it must raise rather than silently pick one.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "redivis_config.R"
            path.write_text(
                'IRW_OWNER <- "datapages"\n'
                'IRW_CORE_DATASETS <- c("a")\n'
                'IRW_TEXT_DATASETS <- c("irw_text")\n'
                'IRW_AUX_DATASETS <- c(text = "irw_text")\n')
            with self.assertRaises(ConfigError) as caught:
                load_registry(path)
            self.assertIn("twice", str(caught.exception))

    def test_pairs_is_competitions(self):
        # There is no irw_pairs dataset and never has been; "pairs" is the
        # label, irw_competitions is the dataset.
        _, targets = load_registry()
        comp = next(t for t in targets if t.source == "comp")
        self.assertEqual(comp.name, "irw_competitions")
        self.assertIn("pairs", comp.label)

    def test_a_malformed_config_raises_rather_than_emptying_the_menu(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "redivis_config.R"
            bad.write_text('IRW_OWNER <- "datapages"\n')
            with self.assertRaises(ConfigError):
                load_registry(bad)

    def test_commented_out_names_are_not_picked_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "redivis_config.R"
            path.write_text(
                'IRW_OWNER <- "datapages"\n'
                'IRW_CORE_DATASETS <- c(\n  "a",\n  # "retired_shard",\n  "b"\n)\n'
                'IRW_TEXT_DATASETS <- c("irw_text")\n'
                'IRW_AUX_DATASETS <- c(meta = "irw_meta")\n')
            _, targets = load_registry(path)
            self.assertEqual([t.name for t in targets],
                             ["a", "b", "irw_text", "irw_meta"])


class TwoTextShards(unittest.TestCase):
    """The path that matters once `irw_text` hits Redivis' 1000-table cap.

    None of this is reachable through the live config yet -- IRW_TEXT_DATASETS
    has one entry. These tests exist so the second shard is a config edit on the
    day it is needed rather than a code change made under pressure.
    """

    CONFIG = (
        'IRW_OWNER <- "datapages"\n'
        'IRW_CORE_DATASETS <- c("w1", "w2")\n'
        'IRW_TEXT_DATASETS <- c("irw_text", "irw_text_2")\n'
        'IRW_AUX_DATASETS <- c(meta = "irw_meta")\n'
    )

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        path = Path(self.tmp.name) / "redivis_config.R"
        path.write_text(self.CONFIG)
        _, self.targets = load_registry(path)

    def test_both_shards_are_registered_oldest_first(self):
        self.assertEqual([t.name for t in text_shards(self.targets)],
                         ["irw_text", "irw_text_2"])

    def test_new_item_text_defaults_to_the_newest_shard(self):
        # Writing to the older shard would be invisible: clients resolve
        # newest-first, so a copy in irw_text_2 would shadow it.
        self.assertEqual(newest_text_shard(self.targets).name, "irw_text_2")
        self.assertEqual(
            guess_target([Path("x__items.csv")], self.targets).name, "irw_text_2")

    def test_response_data_is_unaffected_by_text_shards(self):
        self.assertEqual(newest_shard(self.targets).name, "w2")
        self.assertEqual(guess_target([Path("a.csv")], self.targets).name, "w2")

    def test_every_shard_accepts_item_text_and_only_item_text(self):
        for shard in text_shards(self.targets):
            self.assertIsNone(eligible(Path("x__items.csv"), shard))
            self.assertIsNotNone(eligible(Path("plain.csv"), shard))

    def test_a_table_already_in_the_older_shard_is_flagged_elsewhere(self):
        # The whole point: re-uploading into irw_text_2 would not replace the
        # copy in irw_text, it would shadow it. `found_in[-1]` is what
        # resolve_elsewhere() offers as the default "update it where it lives".
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "x__items.csv", ITEMS)
            reports = check_all([(path, table_name(path))])
        target = newest_text_shard(self.targets)
        index = {"x__items": ["irw_text"]}
        items = planning.build(reports, target, index)
        self.assertEqual(items[0].status, planning.ELSEWHERE)
        self.assertEqual(items[0].found_in[-1], "irw_text")

    def test_a_table_already_in_the_newest_shard_is_an_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "x__items.csv", ITEMS)
            reports = check_all([(path, table_name(path))])
        items = planning.build(reports, newest_text_shard(self.targets),
                               {"x__items": ["irw_text", "irw_text_2"]})
        self.assertEqual(items[0].status, planning.UPDATE)
        self.assertEqual(items[0].dataset, "irw_text_2")


class ElsewhereRouting(unittest.TestCase):
    """A cross-family name match must never become a cross-family upload.

    `found_in` spans core and item-text shards, so the newest dataset holding a
    name is not always one that may receive the file. Defaulting to it would
    write item text into a warehouse shard -- silently, under --yes.
    """

    def setUp(self):
        _, self.targets = load_registry()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _item(self, name, body, found_in):
        path = write(Path(self.tmp.name), name, body)
        reports = check_all([(path, table_name(path))])
        item = planning.Item(report=reports[0], status=planning.ELSEWHERE,
                             dataset=None, found_in=found_in)
        return item

    def test_item_text_is_not_routed_into_a_warehouse_shard(self):
        # The warehouse shard is the *newer* match, so the old "newest wins"
        # rule would have picked it and written item text into a warehouse.
        item = self._item("x__items.csv", ITEMS,
                          ["irw_text", "item_response_warehouse_3"])
        target = next(t for t in self.targets if t.is_itemtext)
        cli.resolve_elsewhere([item], target, self.targets, assume=True)
        self.assertEqual(item.dataset, "irw_text")

    def test_no_eligible_home_skips_instead_of_guessing(self):
        # The name exists only in a warehouse shard, which cannot hold __items.
        item = self._item("y__items.csv", ITEMS, ["item_response_warehouse_3"])
        target = next(t for t in self.targets if t.is_itemtext)
        cli.resolve_elsewhere([item], target, self.targets, assume=True)
        self.assertEqual(item.status, planning.SKIP)
        self.assertIsNone(item.dataset)
        self.assertIn("resolve by hand", item.note)

    def test_response_data_is_not_routed_into_a_text_shard(self):
        item = self._item("z.csv", RESPONSE, ["irw_text"])
        target = newest_shard(self.targets)
        cli.resolve_elsewhere([item], target, self.targets, assume=True)
        self.assertEqual(item.status, planning.SKIP)


class Discovery(unittest.TestCase):
    def test_table_name_keeps_dots_and_double_underscores(self):
        # The old uploaders used split('.')[0], which truncated any name
        # containing a dot.
        self.assertEqual(table_name(Path("eufootball_2010-2020.csv")),
                         "eufootball_2010-2020")
        self.assertEqual(table_name(Path("v1.2_scale.csv")), "v1.2_scale")
        self.assertEqual(table_name(Path("foo__items.csv")), "foo__items")

    def test_non_csv_files_are_reported_not_silently_dropped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "a.csv", RESPONSE)
            write(root, "notes.R", "x")
            found = discover(root)
            self.assertEqual([p.name for p in found.csvs], ["a.csv"])
            self.assertEqual([p.name for p in found.skipped], ["notes.R"])


class TargetGuessing(unittest.TestCase):
    def setUp(self):
        _, self.targets = load_registry()

    def test_any_items_file_means_an_item_text_directory(self):
        # Item-text batches routinely carry provenance.csv/notes.csv beside the
        # real output, so a majority rule would send those to a shard.
        files = [Path("provenance.csv"), Path("notes.csv"), Path("audit.csv"),
                 Path("x__items.csv")]
        self.assertEqual(guess_target(files, self.targets).name,
                         newest_text_shard(self.targets).name)

    def test_plain_csvs_go_to_the_newest_shard(self):
        self.assertEqual(guess_target([Path("a.csv")], self.targets).name,
                         "item_response_warehouse_6")

    def test_eligibility_is_decided_by_the_target(self):
        text = next(t for t in self.targets if t.is_itemtext)
        shard = newest_shard(self.targets)
        self.assertIsNone(eligible(Path("x__items.csv"), text))
        self.assertIsNotNone(eligible(Path("notes.csv"), text))
        self.assertIsNone(eligible(Path("x.csv"), shard))
        self.assertIsNotNone(eligible(Path("x__items.csv"), shard))


class Checks(unittest.TestCase):
    def test_row_count_excludes_the_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "a.csv", RESPONSE)
            report = scan(path, "a")
            self.assertEqual(report.rows, 2)
            self.assertEqual(report.columns, ["id", "item", "resp"])
            self.assertTrue(report.ok)

    def test_a_file_with_no_required_columns_is_an_error(self):
        # notes.csv / provenance.csv must never become a Redivis table.
        _, targets = load_registry()
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "notes.csv", "note,author\nhi,me\n")
            report = scan(path, "notes")
            self.assertTrue(report.ok)          # scan itself does no schema check
            check_schema(report, newest_shard(targets))
            self.assertFalse(report.ok)

    def test_some_missing_columns_is_only_a_warning(self):
        _, targets = load_registry()
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "a.csv", "id,item\n1,a\n")
            report = scan(path, "a")
            check_schema(report, newest_shard(targets))
            self.assertTrue(report.ok)
            self.assertTrue(any("resp" in w for w in report.warnings))

    def test_schema_depends_on_the_destination(self):
        # irw_meta's thirteen tables each have their own schema, so requiring
        # id/item/resp there would reject every one of them.
        _, targets = load_registry()
        by_source = {t.source: t for t in targets}
        self.assertEqual(required_columns(newest_shard(targets)),
                         ("id", "item", "resp"))
        self.assertEqual(required_columns(by_source["nom"]), ("id", "item", "resp"))
        self.assertEqual(required_columns(by_source["text"]),
                         ("table", "item", "item_text"))
        self.assertEqual(required_columns(by_source["meta"]), ())
        self.assertEqual(required_columns(by_source["comp"]), ())
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "biblio.csv", "table,reference,url\nt,r,u\n")
            report = scan(path, "biblio")
            check_schema(report, by_source["meta"])
            self.assertTrue(report.ok)

    def test_empty_and_headerless_files_are_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(scan(write(Path(tmp), "a.csv", ""), "a").ok)
            self.assertFalse(scan(write(Path(tmp), "b.csv", "id,item,resp\n"), "b").ok)

    def test_uppercase_names_warn(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "Foo.csv", RESPONSE)
            self.assertTrue(any("lowercase" in w for w in scan(path, "Foo").warnings))

    def test_two_files_claiming_one_table_name_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "x").mkdir()
            (root / "y").mkdir()
            a = write(root / "x", "dup.csv", RESPONSE)
            b = write(root / "y", "dup.csv", RESPONSE)
            reports = check_all([(a, "dup"), (b, "dup")])
            self.assertTrue(all(not r.ok for r in reports))


class Planning(unittest.TestCase):
    def setUp(self):
        _, self.targets = load_registry()
        self.shard = newest_shard(self.targets)

    def _reports(self, tmp, names):
        return check_all([(write(Path(tmp), f"{n}.csv", RESPONSE), n) for n in names])

    def _validated(self, tmp, names):
        """check_all + the format validator, in the order cli.py runs them.

        The validator moved out of check_all on 2026-09-03 (it is a check about
        the destination's schema, and check_all runs before a destination is
        chosen), so a name_length error only exists after validate_for_target.
        """
        reports = self._reports(tmp, names)
        for report in reports:
            validate_for_target(report, self.shard)
        return reports

    def test_classification(self):
        with tempfile.TemporaryDirectory() as tmp:
            reports = self._reports(tmp, ["fresh", "here", "older"])
            index = {
                "here": ["item_response_warehouse_6"],
                "older": ["item_response_warehouse", "item_response_warehouse_3"],
            }
            items = {i.table: i for i in planning.build(reports, self.shard, index)}
            self.assertEqual(items["fresh"].status, planning.NEW)
            self.assertEqual(items["here"].status, planning.UPDATE)
            # Present in an older shard: uploading into _6 would shadow it,
            # because clients resolve newest-first.
            self.assertEqual(items["older"].status, planning.ELSEWHERE)
            self.assertEqual(items["older"].found_in[-1], "item_response_warehouse_3")

    def test_elsewhere_defaults_to_updating_where_the_table_already_lives(self):
        from red_up.cli import resolve_elsewhere
        with tempfile.TemporaryDirectory() as tmp:
            reports = self._reports(tmp, ["older"])
            index = {"older": ["item_response_warehouse", "item_response_warehouse_3"]}
            items = planning.build(reports, self.shard, index)
            resolve_elsewhere(items, self.shard, self.targets, assume=True)
            self.assertEqual(items[0].dataset, "item_response_warehouse_3")

    def test_a_published_over_length_name_is_grandfathered(self):
        """datastandard.md's 40-char cap, and the exception ruled 2026-09-03.

        130 live tables predate the rule, so enforcing it on the upload path
        meant a table already named too long could never be repaired for
        anything else -- three cov_age fixes were blocked that way (#1779).
        """
        long_name = "narcissism_schneider_2025_study1_koeberl_hsns"
        with tempfile.TemporaryDirectory() as tmp:
            reports = self._validated(tmp, [long_name])
            self.assertTrue(any(e.startswith("name_length:") for e in reports[0].errors))
            items = planning.build(reports, self.shard,
                                   {long_name: ["item_response_warehouse_3"]})
            self.assertEqual(items[0].status, planning.ELSEWHERE)
            self.assertEqual(reports[0].errors, [])
            self.assertTrue(any("already published" in w
                                for w in reports[0].warnings))

    def test_a_new_over_length_name_is_still_blocked(self):
        long_name = "narcissism_schneider_2025_study1_koeberl_hsns"
        with tempfile.TemporaryDirectory() as tmp:
            reports = self._validated(tmp, [long_name])
            items = planning.build(reports, self.shard, {})
            self.assertEqual(items[0].status, planning.SKIP)
            self.assertTrue(any(e.startswith("name_length:") for e in reports[0].errors))

    def test_grandfathering_does_not_reach_any_other_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            reports = self._reports(tmp, ["published"])
            reports[0].errors.append("dup_id_item: 300 duplicate id+item rows")
            items = planning.build(reports, self.shard,
                                   {"published": ["item_response_warehouse"]})
            self.assertEqual(items[0].status, planning.SKIP)
            self.assertIn("dup_id_item: 300 duplicate id+item rows",
                          reports[0].errors)

    def test_ineligible_files_are_excluded_never_uploaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "x__items.csv", ITEMS)
            reports = check_all([(path, "x__items")])
            items = planning.build(reports, self.shard, {})
            self.assertEqual(items[0].status, planning.EXCLUDED)
            self.assertIsNone(items[0].dataset)


if __name__ == "__main__":
    unittest.main()


# --- red_up.drafts -----------------------------------------------------------

import datetime as _dt

from red_up import drafts as _drafts


class _Version:
    def __init__(self, tag, released, created_ms):
        self.properties = {"tag": tag, "isReleased": released, "createdAt": created_ms}


class _Table:
    def __init__(self, name, rows, hash_=None):
        self.name = name
        self.properties = {"numRows": rows}
        if hash_ is not None:
            self.properties["hash"] = hash_


def _ms(days_ago, now):
    return int((now - _dt.timedelta(days=days_ago)).timestamp() * 1000)


def _fake_redivis(monkeypatch, versions, draft_tables, released_tables):
    """Stand in for the redivis module inside inspect()."""
    class _DS:
        def __init__(self, version=None):
            self._v = version

        def list_versions(self):
            return versions

        def list_tables(self):
            src = draft_tables if self._v == "next" else released_tables
            out = []
            for n, r in src.items():
                # a value may be a bare row count, or (rows, hash)
                rows, h = r if isinstance(r, tuple) else (r, None)
                out.append(_Table(n, rows, h))
            return out

    class _User:
        def dataset(self, name, version=None):
            return _DS(version)

    import sys, types
    mod = types.ModuleType("redivis")
    mod.user = lambda owner: _User()
    monkeypatch.setitem(sys.modules, "redivis", mod)


def _target(name="irw_text"):
    from red_up.targets import Target
    return Target(name=name, label="item text", kind="aux", source="text")


def test_drafts_reports_pending_and_age(monkeypatch):
    now = _dt.datetime.now(_dt.timezone.utc)
    _fake_redivis(
        monkeypatch,
        versions=[_Version("v1.0", True, _ms(10, now)), _Version("next", False, _ms(0.1, now))],
        draft_tables={"a__items": 10, "b__items": 20, "c__items": 5},
        released_tables={"a__items": 10, "b__items": 99},
    )
    r = _drafts.inspect("datapages", _target(), now)
    assert r["has_draft"] is True
    assert r["added"] == ["c__items"]
    assert r["changed"] == ["b__items"]
    assert r["removed"] == []
    assert r["pending"] == 2
    # age is time since the last RELEASE, not since the draft was touched
    assert 9.5 < r["days_since_release"] < 10.5


def test_drafts_ignores_a_draft_identical_to_the_release(monkeypatch):
    now = _dt.datetime.now(_dt.timezone.utc)
    _fake_redivis(
        monkeypatch,
        versions=[_Version("v1.0", True, _ms(30, now)), _Version("next", False, _ms(0.1, now))],
        draft_tables={"a__items": 10},
        released_tables={"a__items": 10},
    )
    r = _drafts.inspect("datapages", _target(), now)
    assert r["pending"] == 0, "an untouched draft is not a backlog, however old the release"


def test_drafts_sees_a_repair_that_keeps_the_row_count(monkeypatch):
    """The irw#1856 case: every repair preserves rows, so numRows sees nothing."""
    now = _dt.datetime.now(_dt.timezone.utc)
    _fake_redivis(
        monkeypatch,
        versions=[_Version("v47.0", True, _ms(2, now)), _Version("next", False, _ms(0.1, now))],
        draft_tables={"ravens_deboeck2012": (11622, "aaa"), "untouched": (100, "same")},
        released_tables={"ravens_deboeck2012": (11622, "bbb"), "untouched": (100, "same")},
    )
    r = _drafts.inspect("datapages", _target(), now)
    assert r["changed"] == ["ravens_deboeck2012"]
    assert r["pending"] == 1


def test_drafts_falls_back_to_rows_without_a_hash(monkeypatch):
    now = _dt.datetime.now(_dt.timezone.utc)
    _fake_redivis(
        monkeypatch,
        versions=[_Version("v1.0", True, _ms(3, now)), _Version("next", False, _ms(0.1, now))],
        draft_tables={"a__items": 10, "b__items": 20},
        released_tables={"a__items": 10, "b__items": 99},
    )
    r = _drafts.inspect("datapages", _target(), now)
    assert r["changed"] == ["b__items"]


def test_drafts_reports_no_draft(monkeypatch):
    now = _dt.datetime.now(_dt.timezone.utc)
    _fake_redivis(monkeypatch, versions=[_Version("v1.0", True, _ms(3, now))],
                  draft_tables={}, released_tables={"a__items": 10})
    assert _drafts.inspect("datapages", _target(), now)["has_draft"] is False


# --- the format-validator gate (#1703 sub-item 1.4) --------------------------

class ValidatorGate(unittest.TestCase):
    """red_up refuses a table the format validator blocks.

    The validator runs against a TARGET, not against a file in the abstract:
    it enforces id/item/resp, which is a statement about where the file is
    going. These tests therefore go through `validate_for_target` with a
    response target, the way cli.py does, rather than through `check_all`,
    which runs before a target has been chosen. See MetadataIsExemptFrom
    Validation below for why that distinction is load-bearing.
    """

    RESPONSE = Target(name="item_response_warehouse_5", label="response data",
                      kind="core")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _csv(self, name, body):
        path = Path(self.tmp.name) / name
        path.write_text(body)
        return path

    def _check(self, path, table, target=None):
        report, = check_all([(path, table)])
        validate_for_target(report, target or self.RESPONSE)
        return report

    def test_a_broken_table_is_blocked(self):
        path = self._csv("broken_2024_scale.csv", "id,item,resp\n1,a,x\n2,b,y\n3,c,z\n")
        report = self._check(path, "broken_2024_scale")
        self.assertFalse(report.ok)
        self.assertTrue(any("resp_numeric" in e for e in report.errors), report.errors)

    def test_a_clean_table_passes(self):
        rows = "\n".join(f"{i},q{j},{(i + j) % 5 + 1}"
                         for i in range(1, 40) for j in range(1, 5))
        path = self._csv("ok_2024_scale.csv", "id,item,resp\n" + rows + "\n")
        report = self._check(path, "ok_2024_scale")
        self.assertTrue(report.ok, report.errors)

    def test_a_cov_age_sentinel_blocks_the_upload(self):
        """Was warn-only until 2026-09-05; promoted to error by irw#1856.

        The old policy was that an already-live defect must not block. It held
        while nobody had decided the repair; 72 of the 81 are now repaired, so
        the gate refuses the defect at the door instead of adding a line to a
        log that 81 tables' worth of bad ages already scrolled past.
        """
        rows = "\n".join(f"{i},q{j},{(i + j) % 5 + 1},{999 if i == 1 else 40}"
                         for i in range(1, 40) for j in range(1, 5))
        path = self._csv("sentinel_2024_scale.csv", "id,item,resp,cov_age\n" + rows + "\n")
        report = self._check(path, "sentinel_2024_scale")
        self.assertFalse(report.ok, "an out-of-range cov_age must refuse the upload")
        self.assertTrue(any("cov_range" in e for e in report.errors), report.errors)

    def test_metadata_is_exempt_from_the_format_validator(self):
        """The regression that made every irw_meta upload a no-op (#1703).

        `irw_validate` enforces id/item/resp. Metadata tables have none of
        them and are exempt by design -- REQUIRED_COLUMNS["meta"] is empty.
        Between 2026-09-02 and 2026-09-03 the validator ran from `check_all`,
        before a target existed, so it failed all thirteen of them and red_up
        reported "nothing here belongs in irw_meta" while uploading zero rows.
        """
        meta = Target(name="irw_meta", label="metadata tables", kind="aux",
                      source="meta")
        path = self._csv("tags.csv",
                         "table,age range,sample\nfoo_2024,Adult (18+),Educational\n")
        report = self._check(path, "tags", target=meta)
        self.assertTrue(report.ok, report.errors)
        self.assertEqual([], report.errors)

    def test_a_target_with_required_columns_is_still_validated(self):
        """The exemption must not become a hole: response data still gets it."""
        path = self._csv("broken_2024_scale.csv",
                         "id,item,resp\n1,a,x\n2,b,y\n3,c,z\n")
        report = self._check(path, "broken_2024_scale")
        self.assertFalse(report.ok, "response data must still be validated")

    def test_a_missing_validator_blocks_rather_than_passes(self):
        import red_up.checks as checks_mod
        real_import = builtins.__import__

        def no_irw_validate(name, *a, **kw):
            if name.startswith("irw_validate"):
                raise ImportError("no pandas here")
            return real_import(name, *a, **kw)

        path = self._csv("x_2024_scale.csv", "id,item,resp\n1,a,1\n2,b,2\n")
        with mock.patch.object(builtins, "__import__", no_irw_validate):
            errors, warnings = checks_mod.run_validator(path)
        self.assertTrue(errors, "a missing validator must be an error, never a pass")
        self.assertIn("validator unavailable", errors[0])
