#!/usr/bin/env python3
"""Summarise what a pipeline run changed, as markdown for the PR body.

A line-count diff is the wrong unit for these files: one added table can be
dozens of lines when its BibTeX spans them, and a changed field is easy to miss
inside a large addition. This reports what a reviewer actually needs -- rows
added, rows REMOVED, and existing rows whose content changed -- keyed the same
way run_pipeline.sh diffs them.

Removals are called out separately because they are the alarming case: every
run so far has removed nothing, and a table vanishing from metadata.csv means
it disappeared from Redivis.

Usage:  summarize_changes.py --ref HEAD --dir metadata
"""

from __future__ import annotations

import argparse
import csv
import io
import subprocess
import sys
from pathlib import Path

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

# Same keys run_pipeline.sh diffs on; `table` unless stated.
KEYS = {
    "collections.csv": ["collection"],
    "collection_members.csv": ["table", "collection"],
}

FILES = [
    "metadata.csv", "biblio.csv", "tags.csv", "nominal_tags.csv",
    "itemtext_metadata.csv", "collections.csv", "collection_members.csv",
    "comps_metadata.csv", "nominal_metadata.csv", "simsyn_metadata.csv",
    "comps_biblio.csv", "nominal_biblio.csv", "simsyn_biblio.csv",
]


def rows(text: str, keys: list[str]):
    out = {}
    for r in csv.DictReader(io.StringIO(text)):
        out[tuple((r.get(k) or "") for k in keys)] = r
    return out


def committed(ref: str, path: str) -> str | None:
    p = subprocess.run(["git", "show", f"{ref}:{path}"],
                       capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--dir", default="metadata", type=Path)
    args = ap.parse_args()

    lines, alarms = [], []
    for name in FILES:
        path = args.dir / name
        if not path.is_file():
            continue
        old_text = committed(args.ref, str(path))
        if old_text is None:
            lines.append(f"| `{name}` | _new file_ | | |")
            continue
        keys = KEYS.get(name, ["table"])
        old, new = rows(old_text, keys), rows(path.read_text(encoding="utf-8"), keys)
        added, removed = len(set(new) - set(old)), len(set(old) - set(new))
        changed = sum(1 for k in set(old) & set(new) if old[k] != new[k])
        if not (added or removed or changed):
            continue
        mark = " **&larr; removals**" if removed else ""
        lines.append(f"| `{name}` | {added} | {removed}{mark} | {changed} |")
        if removed:
            gone = sorted("/".join(k) for k in (set(old) - set(new)))[:10]
            alarms.append(f"- `{name}` lost {removed} row(s): " +
                          ", ".join(f"`{g}`" for g in gone) +
                          (" ..." if removed > 10 else ""))

    if not lines:
        print("_No keyed changes in any output._")
        return 0

    print("| file | rows added | rows removed | existing rows changed |")
    print("|---|---:|---:|---:|")
    print("\n".join(lines))
    if alarms:
        print("\n**Rows disappeared upstream — check these before merging:**\n")
        print("\n".join(alarms))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
