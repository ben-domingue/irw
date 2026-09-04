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

from red_up import plan as planning
from red_up.checks import check_all, check_schema, scan
from red_up.discover import discover, table_name
from red_up.targets import (
    ConfigError,
    required_columns,
    Target,
    eligible,
    guess_target,
    load_registry,
    newest_shard,
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
        self.assertEqual(
            names[:6],
            [f"item_response_warehouse{s}" for s in ("", "_2", "_3", "_4", "_5", "_6")])
        self.assertEqual(
            sorted(names[6:]),
            ["irw_competitions", "irw_meta", "irw_nominal", "irw_simsyn", "irw_text"])
        self.assertEqual(newest_shard(targets).name, "item_response_warehouse_6")

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
                'IRW_AUX_DATASETS <- c(text = "irw_text")\n')
            _, targets = load_registry(path)
            self.assertEqual([t.name for t in targets], ["a", "b", "irw_text"])


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
        self.assertEqual(guess_target(files, self.targets).name, "irw_text")

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
            resolve_elsewhere(items, self.shard, assume=True)
            self.assertEqual(items[0].dataset, "item_response_warehouse_3")

    def test_a_published_over_length_name_is_grandfathered(self):
        """datastandard.md's 40-char cap, and the exception ruled 2026-09-03.

        130 live tables predate the rule, so enforcing it on the upload path
        meant a table already named too long could never be repaired for
        anything else -- three cov_age fixes were blocked that way (#1779).
        """
        long_name = "narcissism_schneider_2025_study1_koeberl_hsns"
        with tempfile.TemporaryDirectory() as tmp:
            reports = self._reports(tmp, [long_name])
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
            reports = self._reports(tmp, [long_name])
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
    def __init__(self, name, rows):
        self.name = name
        self.properties = {"numRows": rows}


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
            return [_Table(n, r) for n, r in src.items()]

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


def test_drafts_reports_no_draft(monkeypatch):
    now = _dt.datetime.now(_dt.timezone.utc)
    _fake_redivis(monkeypatch, versions=[_Version("v1.0", True, _ms(3, now))],
                  draft_tables={}, released_tables={"a__items": 10})
    assert _drafts.inspect("datapages", _target(), now)["has_draft"] is False


# --- the format-validator gate (#1703 sub-item 1.4) --------------------------

class ValidatorGate(unittest.TestCase):
    """red_up refuses a table the format validator blocks."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _csv(self, name, body):
        path = Path(self.tmp.name) / name
        path.write_text(body)
        return path

    def test_a_broken_table_is_blocked(self):
        path = self._csv("broken_2024_scale.csv", "id,item,resp\n1,a,x\n2,b,y\n3,c,z\n")
        report, = check_all([(path, "broken_2024_scale")])
        self.assertFalse(report.ok)
        self.assertTrue(any("resp_numeric" in e for e in report.errors), report.errors)

    def test_a_clean_table_passes(self):
        rows = "\n".join(f"{i},q{j},{(i + j) % 5 + 1}"
                         for i in range(1, 40) for j in range(1, 5))
        path = self._csv("ok_2024_scale.csv", "id,item,resp\n" + rows + "\n")
        report, = check_all([(path, "ok_2024_scale")])
        self.assertTrue(report.ok, report.errors)

    def test_a_cov_age_sentinel_warns_without_blocking(self):
        rows = "\n".join(f"{i},q{j},{(i + j) % 5 + 1},{999 if i == 1 else 40}"
                         for i in range(1, 40) for j in range(1, 5))
        path = self._csv("sentinel_2024_scale.csv", "id,item,resp,cov_age\n" + rows + "\n")
        report, = check_all([(path, "sentinel_2024_scale")])
        self.assertTrue(report.ok, "an already-live defect must not block (#1779)")
        self.assertTrue(any("cov_range" in w for w in report.warnings), report.warnings)

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
