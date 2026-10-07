#!/usr/bin/env python3
"""Build metadata/table_scripts.csv: which data/ script names each table (#2494).

`get_processing_notes` (the irw MCP server, Python-pkg) finds a table's
processing script by NAME: an exact stem match, else a name-prefix match. That
misses every table whose script is named for something else -- a multi-table
battery script (`liem_2024_env_stewardship.py` writes `liem_2024_attitude_env`),
or a table renamed after its script was written (`weida_2020_financial_security.py`
writes `weida_2020_cesd10`, #2198). Before this index, 2,378 of 4,640 catalogued
tables came back `match: none`.

This file is the explicit map. For every catalogued table WITHOUT an exact
script-stem match (the MCP already handles those), it lists the data/ scripts
whose CODE names the table as a whole token. Comment lines do not count: a
script that says "see also X" does not build X. A table named by several
scripts is written with all of them, `|`-separated, and the MCP reports it as
ambiguous rather than guessing.

What it cannot see: names assembled at run time (`paste0(prefix, i)`,
`f"{stem}_{k}"`). Those tables keep whatever the prefix match gives them,
unless metadata/table_scripts_manual.csv (same `table,scripts` columns,
hand-maintained) maps them. A manual row replaces the computed one for its
table; a script it names that is not tracked under data/ is dropped with a
warning, so a renamed script cannot leave a dead path in the index. The first
rows are the himmelstein-<task>-2025 tables, whose names fpt_common.py builds
from each data_<task>.py's TASK_NAME (#2529).

Table names come from the four catalogue CSVs plus straggler_watch.tsv (tables
live on Redivis that have no metadata.csv row yet -- a freshly renamed table is
exactly that for a week). No credentials, no network: it reads files on disk,
so it is safe to run anywhere and reviewable offline.

Run as stage 13 of run_pipeline.sh, after 12. Standalone:
    python3 metadata/13_script_index.py [--repo DIR] [--out FILE]
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Set

# Keep in step with _SCRIPT_SUFFIX in Python-pkg src/irw/mcp.py: a script this
# index lists must be one the MCP would also accept as a script.
SCRIPT_SUFFIX = re.compile(r"\.(py|r|do|ipynb|txt)$", re.IGNORECASE)
TOKEN = re.compile(r"[A-Za-z0-9_]+")
# Python/R/shell `#`, Stata `*` and `//`.
COMMENT_PREFIXES = ("#", "*", "//")

CATALOGUES = (
    "metadata.csv",
    "comps_metadata.csv",
    "nominal_metadata.csv",
    "simsyn_metadata.csv",
    "conj_metadata.csv",   # written by 16_conjoint.R; absent until that stage runs
)


def catalogued_tables(metadata_dir: Path) -> Set[str]:
    tables: Set[str] = set()
    for name in CATALOGUES:
        path = metadata_dir / name
        if not path.exists():
            continue
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                table = (row.get("table") or "").strip()
                if table:
                    tables.add(table)
    watch = metadata_dir / "straggler_watch.tsv"
    if watch.exists():
        with watch.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                table = (row.get("table") or "").strip()
                if table:
                    tables.add(table)
    return tables


def data_scripts(repo: Path) -> List[str]:
    """Tracked scripts under data/, as repo-relative forward-slash paths.

    git ls-files, not a directory walk: the MCP reads the repository on GitHub,
    so an untracked local file must never be listed.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "-z", "--", "data"],
            check=True, capture_output=True,
        ).stdout.decode("utf-8")
        paths = [p for p in out.split("\0") if p]
    except (OSError, subprocess.CalledProcessError):
        paths = [
            Path(root, f).relative_to(repo).as_posix()
            for root, _, files in os.walk(repo / "data")
            for f in files
        ]
    return sorted(p for p in paths if SCRIPT_SUFFIX.search(p))


def stem(path: str) -> str:
    return SCRIPT_SUFFIX.sub("", path.rsplit("/", 1)[-1]).casefold()


def build_index(tables: Iterable[str], scripts: Dict[str, str]) -> Dict[str, List[str]]:
    """Map table -> scripts whose code names it. `scripts` is {path: text}.

    Tables with an exact script-stem match are left out: the MCP resolves those
    before it ever reads this index.
    """
    exact = {stem(p) for p in scripts}
    wanted = {t.casefold(): t for t in tables if t.casefold() not in exact}
    hits: Dict[str, Set[str]] = {}
    for path, text in scripts.items():
        for line in text.splitlines():
            if line.lstrip().startswith(COMMENT_PREFIXES):
                continue
            for token in TOKEN.findall(line):
                table = wanted.get(token.casefold())
                if table is not None:
                    hits.setdefault(table, set()).add(path)
    return {t: sorted(p) for t, p in sorted(hits.items())}


def read_manual(path: Path, listed: Iterable[str]) -> Dict[str, List[str]]:
    """Hand-maintained table -> scripts rows, keeping only tracked scripts."""
    if not path.exists():
        return {}
    known = set(listed)
    manual: Dict[str, List[str]] = {}
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            table = (row.get("table") or "").strip()
            paths = [p.strip() for p in (row.get("scripts") or "").split("|") if p.strip()]
            missing = [p for p in paths if p not in known]
            for p in missing:
                print(f"WARNING: {path.name}: {table} names {p}, not a tracked "
                      f"data/ script; dropped.", file=sys.stderr)
            kept = [p for p in paths if p in known]
            if table and kept:
                manual[table] = sorted(set(manual.get(table, [])) | set(kept))
    return manual


def write_index(index: Dict[str, List[str]], out: Path) -> None:
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["table", "scripts"])
        for table, paths in index.items():
            writer.writerow([table, "|".join(paths)])


def main(argv: List[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=here.parent)
    parser.add_argument("--out", type=Path, default=here / "table_scripts.csv")
    args = parser.parse_args(argv)

    tables = catalogued_tables(args.repo / "metadata")
    paths = data_scripts(args.repo)
    texts = {
        p: (args.repo / p).read_text(encoding="utf-8", errors="replace")
        for p in paths
    }
    index = build_index(tables, texts)
    manual = read_manual(args.repo / "metadata" / "table_scripts_manual.csv", paths)
    index.update(manual)
    index = dict(sorted(index.items()))
    write_index(index, args.out)
    multi = sum(1 for p in index.values() if len(p) > 1)
    print(
        f"table_scripts.csv: {len(index)} tables mapped to a script that names "
        f"them ({multi} named by more than one; {len(manual)} by hand), from "
        f"{len(tables)} catalogued "
        f"tables and {len(paths)} scripts."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
