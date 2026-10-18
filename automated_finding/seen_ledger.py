"""The connectors' cross-run "seen" ledgers, with the verdict on each row.

pmc_seen_dois.csv, plos_seen_dois.csv and repo_triage_seen_keys.csv stop a
candidate from being downloaded and triaged twice. Until 2026-09-30 they held
only the key and a date, so a heuristic verdict such as `no_usable_file` --
wrong for 5 of a random 20 PMC rejects before the Data Availability fix --
retired a candidate forever with nothing recording why (irw#2222).

Each row now also carries the run's `flag`. Runs still skip every key in the
ledger, so nothing is re-downloaded, but an exclusion is reversible: when a
resolver improves, `drop` the rows carrying the flag it fixes and the next run
re-triages them.

    python seen_ledger.py drop pmc_seen_dois.csv --flag no_usable_file
    python seen_ledger.py drop pmc_seen_dois.csv --flag no_usable_file --before 2026-09-23 --apply

A fourth column, `refined_flag`, carries Step 2b's verdict on the rows the
run flagged `human_assistance`. Until 2026-10-18 it was written only to the
run's own triage CSV under the gitignored `runs/`, so a bucket such as
`recoverable_format` -- 46 of the 53 deposits shipped on 2026-10-15 came from
one -- existed nowhere a later run or a person would ever look, while its key
sat in the ledger making the candidate permanently skippable (irw#3051, the
same shape as irw#2203). `record_refined_flags()` writes it back, and `drop`
selects on it:

    python seen_ledger.py drop repo_triage_seen_keys.csv --refined-flag recoverable_format

Rows written before either column existed have a blank flag, except where a
run's output CSV still recorded the verdict (backfilled 2026-09-30).
"""
from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone


def _rewrite(path: str, fieldnames: list, rows: list) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def _read(path: str) -> tuple[list, list]:
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def _fieldnames(key_field: str) -> list:
    return [key_field, "date", "flag", "refined_flag"]


def _upgrade(path: str, key_field: str) -> list:
    """Bring `path`'s header up to the current columns, in place.

    A ledger written by an older checkout can be missing `flag` (pre
    2026-09-30) or `refined_flag` (pre 2026-10-18). Widening it before an
    append keeps one file from carrying rows of two different widths under a
    single header, which is what makes a short row read as the wrong column
    later."""
    fieldnames = _fieldnames(key_field)
    if not os.path.exists(path):
        return fieldnames
    header, existing = _read(path)
    if all(c in header for c in fieldnames):
        return header
    _rewrite(path, fieldnames,
             [{c: r.get(c, "") or "" for c in fieldnames} for r in existing])
    return fieldnames


def append_seen(path: str, key_field: str, items) -> None:
    """Append `items` -- each a key, or a (key, flag) pair -- dated today.

    `refined_flag` is left blank here: Step 2 writes the row, and Step 2b
    fills the refinement afterwards through `record_refined_flags()`."""
    rows = []
    for it in items:
        key, flag = (it, "") if isinstance(it, str) else it
        rows.append((key, flag or ""))
    if not rows:
        return
    fieldnames = _upgrade(path, key_field)
    file_exists = os.path.exists(path)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        if not file_exists:
            writer.writeheader()
        writer.writerows({key_field: k, "date": today, "flag": fl,
                          "refined_flag": ""} for k, fl in rows)


def record_refined_flags(path: str, key_field: str, refined: dict,
                         normalize=None) -> tuple:
    """Write Step 2b's verdicts into the ledger. Returns (written, unmatched).

    `refined` maps a ledger key to its refined flag. `normalize` is the
    caller's key rule (e.g. canonical_doi), applied to both sides, because a
    ledger predating it still holds raw per-version DOIs.

    Only rows that are currently blank or `human_assistance` are touched --
    re-running Step 2b over a triage CSV must not overwrite a verdict some
    other run reached about the same key."""
    if not refined or not os.path.exists(path):
        return 0, len(refined or {})
    norm = normalize or (lambda s: s)
    want = {norm(k): v for k, v in refined.items() if k and v}
    fieldnames = _upgrade(path, key_field)
    header, rows = _read(path)
    written, seen_keys = 0, set()
    for r in rows:
        k = norm(r.get(key_field, ""))
        if k not in want:
            continue
        seen_keys.add(k)
        if (r.get("flag") or "") not in ("", "human_assistance"):
            continue
        if (r.get("refined_flag") or "") == want[k]:
            continue
        r["refined_flag"] = want[k]
        written += 1
    if written:
        _rewrite(path, fieldnames, [{c: r.get(c, "") or "" for c in fieldnames}
                                    for r in rows])
    return written, len(want) - len(seen_keys)


def drop(path: str, flag: str | None = None, before: str | None = None,
         apply: bool = False, refined: str | None = None) -> int:
    """Remove rows carrying `flag` and/or `refined` (dated before `before`, if
    given) so the next run re-triages them. Dry run unless `apply`."""
    if not flag and not refined:
        raise SystemExit("pass --flag and/or --refined-flag")
    column = "refined_flag" if refined else "flag"
    header, rows = _read(path)
    if column not in header:
        raise SystemExit(f"{path} has no {column} column; nothing can be "
                         f"selected by that verdict")
    hit = [r for r in rows
           if (flag is None or r.get("flag") == flag)
           and (refined is None or r.get("refined_flag") == refined)
           and (before is None or (r.get("date") or "") < before)]
    want = ", ".join(f"{c}={v!r}" for c, v in
                     (("flag", flag), ("refined_flag", refined)) if v)
    print(f"{path}: {len(hit)} of {len(rows)} row(s) carry {want}"
          + (f" dated before {before}" if before else ""))
    if apply and hit:
        hit_ids = {id(r) for r in hit}
        _rewrite(path, header, [r for r in rows if id(r) not in hit_ids])
        print(f"removed {len(hit)}; the next run re-triages them")
    elif hit:
        print("dry run -- pass --apply to remove them")
    return len(hit)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("drop", help="remove rows by verdict so they are re-triaged")
    d.add_argument("path")
    d.add_argument("--flag", help="Step 2 verdict to select")
    d.add_argument("--refined-flag", dest="refined",
                   help="Step 2b verdict to select; combinable with --flag")
    d.add_argument("--before", help="only rows dated before this YYYY-MM-DD")
    d.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if a.cmd == "drop":
        drop(a.path, a.flag, a.before, a.apply, a.refined)


if __name__ == "__main__":
    main()
