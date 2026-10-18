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
    assert header == ["doi", "date", "flag", "refined_flag"]
    assert [(r["doi"], r["flag"]) for r in rows] == [("10.1/a", "no_usable_file"), ("10.1/b", "good")]
    assert all(r["refined_flag"] == "" for r in rows)
    assert irw_discover_pmc.load_seen_dois(p) == {"10.1/a", "10.1/b"}


def test_old_two_column_ledger_is_upgraded_not_mixed(tmp_path):
    p = tmp_path / "plos.csv"
    p.write_bytes(b"doi,date\r\n10.1/old,2026-08-13\r\n")
    irw_discover_plos.append_seen_dois([("10.1/new", "human_assistance")], str(p))
    header, rows = _rows(p)
    assert header == ["doi", "date", "flag", "refined_flag"]
    assert rows[0] == {"doi": "10.1/old", "date": "2026-08-13", "flag": "",
                       "refined_flag": ""}
    assert rows[1]["doi"] == "10.1/new" and rows[1]["flag"] == "human_assistance"
    assert b"\r" not in p.read_bytes()


def test_bare_keys_still_accepted(tmp_path):
    p = str(tmp_path / "repo.csv")
    irw_batch_updated.append_seen_keys(["10.5281/zenodo.1"], p)
    header, rows = _rows(p)
    assert header == ["key", "date", "flag", "refined_flag"]
    assert rows[0]["flag"] == "" and rows[0]["refined_flag"] == ""
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


# --- Step 2b's verdict reaches the ledger (irw#3051) ----------------------

def test_refined_flag_is_written_back(tmp_path):
    p = str(tmp_path / "repo.csv")
    seen_ledger.append_seen(p, "key", [("10.1/a", "human_assistance"),
                                       ("10.1/b", "human_assistance"),
                                       ("10.1/c", "good")])
    written, unmatched = seen_ledger.record_refined_flags(
        p, "key", {"10.1/a": "recoverable_format", "10.1/b": "not_item_response",
                   "10.1/zz": "human_review"})
    assert (written, unmatched) == (2, 1)
    rows = {r["key"]: r["refined_flag"] for r in _rows(p)[1]}
    assert rows == {"10.1/a": "recoverable_format",
                    "10.1/b": "not_item_response", "10.1/c": ""}


def test_refined_flag_does_not_overwrite_another_runs_verdict(tmp_path):
    p = str(tmp_path / "repo.csv")
    seen_ledger.append_seen(p, "key", [("10.1/a", "good")])
    assert seen_ledger.record_refined_flags(p, "key", {"10.1/a": "human_review"})[0] == 0
    assert _rows(p)[1][0]["refined_flag"] == ""


def test_refined_flag_matches_a_raw_versioned_doi_in_the_ledger(tmp_path):
    # The ledger predates canonical_doi() and holds per-version and
    # mixed-case keys; _key() hands Step 2b the collapsed, lowercased form.
    p = str(tmp_path / "repo.csv")
    seen_ledger.append_seen(p, "key", [
        ("10.6084/m9.figshare.123.v3", "human_assistance"),
        ("10.7910/DVN/ABC123", "human_assistance")])
    written, unmatched = seen_ledger.record_refined_flags(
        p, "key", {"10.6084/m9.figshare.123": "recoverable_format",
                   "10.7910/dvn/abc123": "worth_retrying"},
        normalize=irw_batch_updated._seen_key_norm)
    assert (written, unmatched) == (2, 0)
    assert [r["refined_flag"] for r in _rows(p)[1]] == ["recoverable_format",
                                                        "worth_retrying"]


def test_old_three_column_ledger_is_widened_by_the_write_back(tmp_path):
    p = tmp_path / "repo.csv"
    p.write_text("key,date,flag\n10.1/a,2026-09-01,human_assistance\n", encoding="utf-8")
    seen_ledger.record_refined_flags(str(p), "key", {"10.1/a": "worth_retrying"})
    header, rows = _rows(str(p))
    assert header == ["key", "date", "flag", "refined_flag"]
    assert rows[0]["refined_flag"] == "worth_retrying"


def test_drop_selects_on_the_refined_flag(tmp_path):
    p = str(tmp_path / "repo.csv")
    seen_ledger.append_seen(p, "key", [("10.1/a", "human_assistance"),
                                       ("10.1/b", "human_assistance")])
    seen_ledger.record_refined_flags(p, "key", {"10.1/a": "recoverable_format",
                                                "10.1/b": "not_item_response"})
    assert seen_ledger.drop(p, refined="recoverable_format") == 1
    seen_ledger.drop(p, refined="recoverable_format", apply=True)
    assert irw_batch_updated.load_seen_keys(p) == {"10.1/b"}


def test_chain_step2b_warns_when_no_ledger_is_passed(tmp_path, capsys):
    """A new entry point that forgets the ledger must say so, not go quiet."""
    import irw_retriage_ha
    t = tmp_path / "triage.csv"
    t.write_text("doi,flag\n10.1/a,human_assistance\n", encoding="utf-8")
    assert irw_retriage_ha.chain_step2b(str(t), run=False) is None
    assert "will NOT be recorded" in capsys.readouterr().err


def test_chain_step2b_passes_the_ledger_through_to_the_retriage_command(tmp_path, capsys):
    import irw_retriage_ha
    t = tmp_path / "triage.csv"
    t.write_text("doi,flag\n10.1/a,human_assistance\n", encoding="utf-8")
    irw_retriage_ha.chain_step2b(str(t), run=False, ledger="pmc_seen_dois.csv",
                                 key_field="doi")
    err = capsys.readouterr().err
    assert "--ledger pmc_seen_dois.csv --key-field doi" in err
    assert "will NOT be recorded" not in err


def test_chain_step2b_leaves_the_ledger_alone_on_a_remine(tmp_path, capsys):
    import irw_retriage_ha
    t = tmp_path / "triage.csv"
    t.write_text("doi,flag\n10.1/a,human_assistance\n", encoding="utf-8")
    irw_retriage_ha.chain_step2b(str(t), run=False, ledger="pmc_seen_dois.csv",
                                 key_field="doi", update_ledger=False)
    err = capsys.readouterr().err
    assert "--ledger" not in err and "will NOT be recorded" not in err


def test_retriage_output_is_keyed_the_way_the_ledger_was_written(tmp_path):
    """The glue: a retriage CSV carries doi/url/title, not the ledger key."""
    import irw_retriage_ha
    led = str(tmp_path / "repo.csv")
    seen_ledger.append_seen(led, "key", [
        ("10.6084/m9.figshare.9.v2", "human_assistance"),   # reached by doi
        ("https://osf.io/abcd/", "human_assistance"),       # reached by url
    ])
    out = tmp_path / "t.retriage_ha.csv"
    out.write_text(
        "source,title,url,doi,flag,refined_flag\n"
        "figshare,A,https://figshare.com/1,10.6084/m9.figshare.9,human_assistance,recoverable_format\n"
        "osf,B,https://osf.io/abcd/,,human_assistance,not_item_response\n",
        encoding="utf-8")
    written, unmatched = irw_retriage_ha.record_refined_flags(
        str(out), led, "key", key_of=irw_batch_updated._key,
        normalize=irw_batch_updated._seen_key_norm)
    assert (written, unmatched) == (2, 0)
    assert [r["refined_flag"] for r in _rows(led)[1]] == ["recoverable_format",
                                                          "not_item_response"]
