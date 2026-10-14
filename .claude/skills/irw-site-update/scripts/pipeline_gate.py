#!/usr/bin/env python3
"""Decide whether a scheduled metadata-pipeline run has anything to do.

The pipeline runs Mondays and Thursdays (metadata-pipeline.yml). Monday always
runs: it carries the rolling re-check in 01_metadata.R that revisits a slice of
old tables each week, and nothing else refreshes those. Thursday exists only to
shorten the wait between a data PR merging and its metadata rows existing, so
it should run only when there IS such a table. Without this gate a Thursday
with nothing new still opens a pull request whose only diff is a status.json
timestamp and emptied per-run logs (#2342), and reviewing that is pure cost.

"Something new" means a table live in a core warehouse shard with no row in
metadata.csv, or a metadata.csv row whose table is no longer live. Only the
core shards are checked -- they are where almost all intake lands, and stage 12
uses the same definition. A new competitions, simsyn, nominal or conjoint table
with no core table alongside waits for Monday.

Fails OPEN: if Redivis cannot be listed, or the listing looks truncated, the
answer is "run" -- a wasted run costs an hour, a skipped one costs a week.

Usage:
    pipeline_gate.py [--metadata metadata/metadata.csv] [--min-live 1000]
Prints one line, `run=true` or `run=false`, followed by the reason, and writes
the same `run=` line to $GITHUB_OUTPUT when that is set.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CONFIG = REPO / "metadata" / "redivis_config.R"


def read_config() -> tuple[str, list[str]]:
    text = CONFIG.read_text()
    owner = re.search(r'IRW_OWNER\s*<-\s*"([^"]+)"', text).group(1)
    block = re.search(r"IRW_CORE_DATASETS\s*<-\s*c\((.*?)\)", text, re.S).group(1)
    shards = re.findall(r'"([^"]+)"', block)
    return owner, shards


def live_tables(owner: str, shards: list[str]) -> set[str]:
    import redivis  # installed by the workflow; imported late so --help works without it
    names: set[str] = set()
    for shard in shards:
        for t in redivis.organization(owner).dataset(shard).list_tables():
            names.add(t.properties["name"].strip().lower())
    return names


def described(path: Path) -> set[str]:
    with path.open(newline="") as fh:
        return {row["table"].strip().lower() for row in csv.DictReader(fh) if row.get("table")}


def decide(metadata: Path, min_live: int) -> tuple[bool, str]:
    owner, shards = read_config()
    try:
        live = live_tables(owner, shards)
    except Exception as e:  # noqa: BLE001 -- any failure means "run", see docstring
        return True, f"could not list the core shards ({type(e).__name__}: {e}); running"
    if len(live) < min_live:
        return True, f"listing returned only {len(live)} tables (expected >= {min_live}); running"
    have = described(metadata)
    new = sorted(live - have)
    gone = sorted(have - live)
    if not new and not gone:
        return False, f"{len(live)} live core tables, all described in {metadata.name}; nothing new since the last run"
    parts = []
    if new:
        parts.append(f"{len(new)} live table(s) without a metadata row: {', '.join(new[:20])}{' ...' if len(new) > 20 else ''}")
    if gone:
        parts.append(f"{len(gone)} metadata row(s) no longer live: {', '.join(gone[:20])}{' ...' if len(gone) > 20 else ''}")
    return True, "; ".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--metadata", type=Path, default=REPO / "metadata" / "metadata.csv")
    ap.add_argument("--min-live", type=int, default=1000)
    a = ap.parse_args()
    run, why = decide(a.metadata, a.min_live)
    line = f"run={'true' if run else 'false'}"
    print(f"{line}\n{why}")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(line + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
