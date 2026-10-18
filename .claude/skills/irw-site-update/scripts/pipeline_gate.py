#!/usr/bin/env python3
"""Decide whether a scheduled metadata-pipeline run has anything to do.

The pipeline runs Mondays, Wednesdays and Fridays (metadata-pipeline.yml).
Monday always runs. The other slots run when EITHER of two things is true, and
a run does useful work in both cases:

1. Intake. A table is live in a core warehouse shard with no row in
   metadata.csv, or a metadata.csv row's table is no longer live. This is what
   the extra slots were added for in the first place: shortening the wait
   between a data PR merging and its metadata rows existing.

2. The rolling refresh is behind. 01_metadata.R re-checks `refresh.per.run`
   existing tables per run, oldest-first, and nothing else revisits them. That
   rotation only started surviving Actions runs on 2026-10-02 (#2785), so most
   of the corpus has never been re-checked, and the per-table statistics it
   computes are what a psychometric-property filter would be built on (#1710).
   A skipped slot is a skipped slice of the sweep, so sweep lag is a reason to
   run on its own.

Without any gate, a slot with nothing to do still opens a pull request whose
only diff is a status.json timestamp and emptied per-run logs (#2342), and
reviewing that is pure cost. That is still the case the gate exists to catch --
it is just no longer the only kind of work a run can have.

Only the core shards are checked for intake -- they are where almost all of it
lands, and stage 12 uses the same definition. A new competitions, simsyn,
nominal or conjoint table with no core table alongside waits for Monday.

Fails OPEN: if Redivis cannot be listed, or the listing looks truncated, the
answer is "run" -- a wasted run costs an hour, a skipped one costs a week. The
rotation check fails open too, and is evaluated FIRST because it needs no
network.

Usage:
    pipeline_gate.py [--metadata metadata/metadata.csv]
                     [--refresh-log metadata/metadata_refresh_log.csv]
                     [--max-refresh-age 50] [--min-live 1000]
Prints one line, `run=true` or `run=false`, followed by the reason, and writes
the same `run=` line to $GITHUB_OUTPUT when that is set.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
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


def refresh_ages(metadata: Path, refresh_log: Path, now: dt.datetime) -> tuple[int, float | None]:
    """How far behind the rolling refresh is.

    Returns (tables never refreshed, age in days of the oldest refresh), both
    computed over the tables metadata.csv actually describes -- a log entry for
    a table that has since been withdrawn is not sweep debt. The age is None
    when every described table is unrefreshed (nothing to be old).
    """
    have = described(metadata)
    last: dict[str, str] = {}
    if refresh_log.exists():
        with refresh_log.open(newline="") as fh:
            for row in csv.DictReader(fh):
                name = (row.get("table") or "").strip().lower()
                stamp = (row.get("refreshed_at") or "").strip()
                if name in have and stamp:
                    last[name] = stamp  # later entries win, as 01_metadata.R intends
    never = len(have - set(last))
    ages = []
    for stamp in last.values():
        try:
            when = dt.datetime.strptime(stamp[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        ages.append((now - when).total_seconds() / 86400.0)
    return never, (max(ages) if ages else None)


def rotation_behind(metadata: Path, refresh_log: Path, max_age_days: float,
                    now: dt.datetime | None = None) -> tuple[bool, str]:
    """Is the rolling refresh far enough behind to justify a run on its own?"""
    now = now or dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    try:
        never, oldest = refresh_ages(metadata, refresh_log, now)
    except Exception as e:  # noqa: BLE001 -- fail open, as the docstring says
        return True, f"could not read {refresh_log.name} ({type(e).__name__}: {e}); running"
    if never:
        return True, f"rolling refresh behind: {never} described table(s) never re-checked"
    if oldest is not None and oldest > max_age_days:
        return True, (f"rolling refresh behind: oldest re-check is {oldest:.0f} days old "
                      f"(limit {max_age_days:.0f})")
    age = "n/a" if oldest is None else f"{oldest:.0f}d"
    return False, f"rolling refresh current (oldest re-check {age}, limit {max_age_days:.0f}d)"


def decide(metadata: Path, min_live: int, refresh_log: Path,
           max_refresh_age: float) -> tuple[bool, str]:
    ##checked first: no network, and it is true for most of the corpus right now
    behind, why_rotation = rotation_behind(metadata, refresh_log, max_refresh_age)
    if behind:
        return True, why_rotation
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
        return False, (f"{len(live)} live core tables, all described in {metadata.name}; "
                       f"nothing new since the last run, and {why_rotation}")
    parts = []
    if new:
        parts.append(f"{len(new)} live table(s) without a metadata row: {', '.join(new[:20])}{' ...' if len(new) > 20 else ''}")
    if gone:
        parts.append(f"{len(gone)} metadata row(s) no longer live: {', '.join(gone[:20])}{' ...' if len(gone) > 20 else ''}")
    return True, "; ".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--metadata", type=Path, default=REPO / "metadata" / "metadata.csv")
    ap.add_argument("--refresh-log", type=Path,
                    default=REPO / "metadata" / "metadata_refresh_log.csv")
    ##50 days, not one sweep length: at refresh.per.run=400 and three runs a
    ##week a full sweep is ~15 runs, ~35 days, so the oldest re-check sits near
    ##35 days by construction and a tighter limit would make this clause always
    ##true -- which would quietly turn the gate off. 50 means "the sweep has
    ##fallen about half a cycle behind", a real signal rather than a
    ##restatement of the schedule. It needs revisiting if refresh.per.run or
    ##the cron changes.
    ap.add_argument("--max-refresh-age", type=float, default=50.0)
    ap.add_argument("--min-live", type=int, default=1000)
    a = ap.parse_args()
    run, why = decide(a.metadata, a.min_live, a.refresh_log, a.max_refresh_age)
    line = f"run={'true' if run else 'false'}"
    print(f"{line}\n{why}")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(line + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
