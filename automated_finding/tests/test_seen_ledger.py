"""The seen ledgers record each row's verdict, so an exclusion can be undone (irw#2222)."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import irw_batch_updated  # noqa: E402
import irw_discover_pmc  # noqa: E402
import irw_discover_plos  # noqa: E402
import seen_ledger  # noqa: E402


def _rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def test_new_ledger_gets_the_flag_column(tmp_path):
    p = str(tmp_path / "pmc.csv")
    irw_discover_pmc.append_seen_dois([("10.1/a", "no_usable_file"), ("10.1/b", "good")], p)
    header, rows = _rows(p)
    assert header == ["doi", "date", "flag"]
    assert [(r["doi"], r["flag"]) for r in rows] == [("10.1/a", "no_usable_file"), ("10.1/b", "good")]
    assert irw_discover_pmc.load_seen_dois(p) == {"10.1/a", "10.1/b"}


def test_old_two_column_ledger_is_upgraded_not_mixed(tmp_path):
    p = tmp_path / "plos.csv"
    p.write_bytes(b"doi,date\r\n10.1/old,2026-08-13\r\n")
    irw_discover_plos.append_seen_dois([("10.1/new", "human_assistance")], str(p))
    header, rows = _rows(p)
    assert header == ["doi", "date", "flag"]
    assert rows[0] == {"doi": "10.1/old", "date": "2026-08-13", "flag": ""}
    assert rows[1]["doi"] == "10.1/new" and rows[1]["flag"] == "human_assistance"
    assert b"\r" not in p.read_bytes()


def test_bare_keys_still_accepted(tmp_path):
    p = str(tmp_path / "repo.csv")
    irw_batch_updated.append_seen_keys(["10.5281/zenodo.1"], p)
    header, rows = _rows(p)
    assert header == ["key", "date", "flag"] and rows[0]["flag"] == ""
    assert irw_batch_updated.load_seen_keys(p) == {"10.5281/zenodo.1"}


def test_empty_append_writes_nothing(tmp_path):
    p = tmp_path / "pmc.csv"
    irw_discover_pmc.append_seen_dois([], str(p))
    assert not p.exists()


def test_drop_is_a_dry_run_unless_applied(tmp_path):
    p = str(tmp_path / "pmc.csv")
    seen_ledger.append_seen(p, "doi", [("10.1/a", "no_usable_file"), ("10.1/b", "good"),
                                       ("10.1/c", "no_usable_file")])
    assert seen_ledger.drop(p, "no_usable_file") == 2
    assert len(_rows(p)[1]) == 3
    seen_ledger.drop(p, "no_usable_file", apply=True)
    assert irw_discover_pmc.load_seen_dois(p) == {"10.1/b"}


def test_drop_before_date(tmp_path):
    p = tmp_path / "pmc.csv"
    p.write_text("doi,date,flag\n10.1/a,2026-09-01,no_usable_file\n10.1/b,2026-09-29,no_usable_file\n",
                 encoding="utf-8")
    seen_ledger.drop(str(p), "no_usable_file", before="2026-09-23", apply=True)
    assert irw_discover_pmc.load_seen_dois(str(p)) == {"10.1/b"}
