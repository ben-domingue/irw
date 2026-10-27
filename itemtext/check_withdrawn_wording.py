#!/usr/bin/env python3
"""Tracked wording for a table withdrawn on rights grounds (#3228, review R-40).

WHY
---
A rights withdrawal removes the item text from Redivis. It does not remove the
file the text was staged from, and `itemtext/itemtables/` holds 4,394 tracked
files. On 2026-10-26 seven of them carried wording for tables withdrawn for
rights: three whole `__items.csv` tables staged in `batch_205`, and four
`verify_*.R` harnesses that quote the items they check -- one of them 11
verbatim PTCI stems. Two of the three CSVs are for withdrawals whose own note
reads "sentence-level reproduction verified against item text", so the wording
had been confirmed to reproduce the instrument, withdrawn for that reason, and
left in the repository.

The review expected these files to be harnesses with no wording, and 83 of 87
are. "Implies" is not "checked", which is why this is a check.

WHAT IT FLAGS
-------------
Two tests, both of which attribute wording to a table rather than guessing:

1. **By file name.** A tracked file under itemtext/ whose name matches a table
   withdrawn for `rights` or `unlicensed` (the `verify_` prefix and the
   `__items` suffix are stripped first), and which either is an `__items` CSV
   -- a whole wording table, flagged on its name alone -- or contains a quoted
   string shaped like an item stem.
2. **By the `table` column.** A tracked CSV carrying both `table` and
   `item_text` columns, where a row names a withdrawn table and its
   `item_text` is prose (three words or more). This is what caught the files
   whose NAME says nothing, such as a language-backfill snapshot. The
   three-word floor matters: `language_backfill/audit_2026-09-01.csv` stores
   verdict codes in `item_text` (`ADMIN`, `NEEDS_REVIEW`, `blank`) and is not
   wording.

The stem test is deliberately narrow. It is not a wording detector -- it cannot
read an instrument and decide what belongs to it -- it is a tripwire for the
one shape that showed up in practice, self-report items in English. A harness
discussing items without quoting them passes, which is what 83 of 87 do.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
`--broad` reports every tracked file that both names a withdrawn table and
contains item-stem prose, without attributing the two to each other. That
found 45 files on 2026-10-26 and is NOT a finding: most are a file naming one
withdrawn table while quoting an item belonging to another, and several quote
licence correspondence rather than items at all ("I hold the copyright to the
BFI and it is not in the public domain"). Attribution there needs a human, so
`--broad` is a review aid and is not what CI runs (#3228).

USAGE
    python3 itemtext/check_withdrawn_wording.py             # from the repo root
    python3 itemtext/check_withdrawn_wording.py --broad     # review aid, see above
exits 1 and names the files if any are found.
"""
import csv
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
WITHDRAWALS = ROOT / "itemtext" / "withdrawals.csv"
RIGHTS_REASONS = ("rights", "unlicensed")

#: First person, a handful of words, ending like a sentence. Matches the stems
#: that were actually found; does not pretend to generalise beyond them.
STEM = re.compile(
    r"^(I |My |When I |In most ways|I am |I feel|I enjoy|I have|I think|"
    r"It |Sometimes )",
    re.IGNORECASE,
)
QUOTED = re.compile(r"""["']([^"'\n]{20,200})["']""")


def withdrawn_for_rights():
    with open(WITHDRAWALS, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    names = set()
    for row in rows:
        if (row.get("reason") or "").strip().lower() not in RIGHTS_REASONS:
            continue
        #: A reinstated withdrawal is no longer a rights withdrawal: the grant
        #: arrived and the text is published again, so its wording may sit in
        #: the repo like any other table's.
        if (row.get("reinstated") or "").strip():
            continue
        table = re.sub(r"__items$", "", (row.get("table") or "")).lower()
        if table:
            names.add(table)
    return names


def tracked_itemtext_files():
    out = subprocess.run(
        ["git", "ls-files", "itemtext"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split("\n")
    return [p for p in out if p]


def table_of(path):
    name = path.rsplit("/", 1)[-1]
    name = re.sub(r"^verify_", "", name)
    name = re.sub(r"\.(R|r|csv|md|py|txt|json)$", "", name)
    return re.sub(r"__items$", "", name).lower()


def item_stems(path):
    text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
    found = set()
    for match in QUOTED.finditer(text):
        value = match.group(1).strip()
        if (
            STEM.match(value)
            and len(value.split()) >= 5
            and value[-1:] in ".?!"
        ):
            found.add(value)
    return sorted(found)


def wording_rows(path, names):
    """Rows whose own `table` column names a withdrawn table, with prose text."""
    try:
        with open(ROOT / path, encoding="utf-8-sig", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames or []
            if not ("item_text" in columns and "table" in columns):
                return set()
            found = set()
            for row in reader:
                table = re.sub(r"__items$", "", (row.get("table") or "")).lower()
                text = (row.get("item_text") or "").strip()
                # Three words or more: a verdict code like NEEDS_REVIEW is not
                # wording, and `item_text` is used for both in this tree.
                if table in names and len(text.split()) >= 3:
                    found.add(table)
            return found
    except (OSError, csv.Error):
        return set()


def main():
    names = withdrawn_for_rights()
    problems = []
    for path in tracked_itemtext_files():
        if path.endswith(".csv"):
            tables = wording_rows(path, names)
            if tables:
                problems.append((
                    path,
                    f"item_text rows for {len(tables)} withdrawn table(s): "
                    f"{', '.join(sorted(tables)[:3])}",
                ))
                continue
        if table_of(path) not in names:
            continue
        if path.endswith("__items.csv"):
            problems.append((path, "whole wording table for a rights withdrawal"))
            continue
        stems = item_stems(path)
        if stems:
            problems.append((
                path,
                f"{len(stems)} item stem(s) quoted, e.g. {stems[0]!r}",
            ))

    if "--broad" in sys.argv:
        print(
            "--broad: files that name a withdrawn table AND contain item-stem "
            "prose, with no attribution between the two. Read them; do not "
            "act in bulk.\n"
        )
        for path in tracked_itemtext_files():
            try:
                text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            named = [n for n in names if len(n) > 8 and n in text.lower()]
            if not named:
                continue
            stems = item_stems(path)
            if stems:
                print(f"  {path}\n      names {sorted(named)[:2]}, "
                      f"{len(stems)} stem(s), e.g. {stems[0][:70]!r}")

    if problems:
        print(
            f"{len(problems)} tracked file(s) carry wording for a table "
            f"withdrawn on rights grounds:",
            file=sys.stderr,
        )
        for path, why in problems:
            print(f"  {path}\n      {why}", file=sys.stderr)
        print(
            "\nA withdrawal removes the text from Redivis, not from the repo. "
            "Delete the file; see itemtext/fixes/3228_withdrawn_wording/.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        f"OK: no tracked file under itemtext/ carries wording for any of the "
        f"{len(names)} tables withdrawn for rights."
    )


if __name__ == "__main__":
    main()
