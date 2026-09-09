#!/usr/bin/env python3
"""Snapshot which item-text tables are actually live, so nothing has to remember.

    python3 itemtext/refresh_live_tables.py            # rewrite live_tables.csv
    python3 itemtext/refresh_live_tables.py --check    # exit 1 if it is out of date

Why this exists (irw#1828). `provenance.csv` carries an `uploaded` column that
is a hand-maintained mirror of a fact Redivis already holds. Whether a table is
live is not an opinion; it is one API call. Every stale row is someone having
done the upload and not come back to the CSV -- the failure mode
ARCHITECTURE.md's Rule 2 is about: prefer documentation that cannot go stale.

The column is not deleted, because it carries something Redivis genuinely
cannot reconstruct after the fact: *when*. A table's `createdAt` is not that
date -- opening a draft copies the whole dataset and resets those timestamps,
the same trap `red_up.drafts` documents for measuring draft age. That is why
five rows in #1828 were left blank rather than stamped with a date known to be
wrong. So `uploaded` stays the record of *when*, and *whether* moves here,
where it cannot lie.

The snapshot is committed rather than queried at check time on purpose:
`check_issues_page.R` runs with no credentials and no network, and that is a
real virtue -- it gates an upload wrap-up on a machine with no token. A
committed snapshot keeps that property and moves the staleness somewhere a diff
can see. The trade is that it is only as fresh as its last refresh, so the file
stamps its own date and the checker reports how old it is.

Records the draft separately from the published version, because they answer
different questions. A table sitting in `next` is not something a reader can
fetch, so it is not live and does not yet owe an issues-page entry -- treating a
draft as live is how the batch_015 set read as published for the hours between
upload and release. But it is also not missing, and a checker that cannot tell
those apart cries wolf on every table in the release window. So each row carries
a `status` of `published` or `draft`.
"""

from __future__ import annotations

import csv
import datetime as dt
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
sys.path.insert(0, str(SRC))

from red_up.targets import load_registry, text_shards  # noqa: E402

OUT = HERE / "live_tables.csv"
SUFFIX = "__items"


def _list(owner: str, shard: str, version: str) -> set[str] | None:
    """Bare table names in one version of one shard. None if it has no draft."""
    import redivis

    for attempt in range(6):
        try:
            ds = redivis.user(owner).dataset(shard, version=version)
            names = [t.name for t in ds.list_tables()]
            break
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            # Redivis rate-limits bursts; a 429 is transient and retrying is
            # cheaper than writing half a snapshot. A shard with no open draft
            # is not an error -- it is the normal state between releases.
            if "429" in msg and attempt < 5:
                time.sleep(15)
                continue
            if version == "next" and ("not_found" in msg or "404" in msg):
                return None
            raise
    # Item-text tables end in __items; the bare name is what provenance.csv,
    # the dictionary and the issues page all use.
    return {n[: -len(SUFFIX)] if n.endswith(SUFFIX) else n for n in names}


def fetch() -> list[tuple[str, str, str]]:
    """(bare table name, shard, status) for every item-text table."""
    owner, targets = load_registry()
    rows: list[tuple[str, str, str]] = []
    for shard in text_shards(targets):
        published = _list(owner, shard.name, "current") or set()
        draft = _list(owner, shard.name, "next")
        rows += [(t, shard.name, "published") for t in published]
        if draft is not None:
            # Draft-only: uploaded, not yet released. A table the draft DROPS is
            # a staged withdrawal and stays `published` here -- it is still what
            # a reader can fetch today, which is what this file records.
            rows += [(t, shard.name, "draft") for t in draft - published]
    rows.sort()
    return rows


def render(rows: list[tuple[str, str, str]], asof: str) -> str:
    head = [
        f"# item-text tables in the Redivis shards as of {asof}",
        "# status=published: a reader can fetch it. status=draft: uploaded, not released yet.",
        "# generated -- do not hand-edit; rerun itemtext/refresh_live_tables.py (irw#1828)",
        "table,shard,status",
    ]
    return "\n".join(head + [f"{t},{sh},{st}" for t, sh, st in rows]) + "\n"


def read_snapshot(path: Path = OUT) -> tuple[dict[str, str], str | None]:
    """{table: status} and the date it was taken. Missing file -> ({}, None)."""
    if not path.exists():
        return {}, None
    asof = None
    lines = path.read_text().splitlines()
    for line in lines:
        if line.startswith("#") and " as of " in line:
            asof = line.rsplit(" as of ", 1)[1].strip()
            break
    body = [ln for ln in lines if ln and not ln.startswith("#")]
    return {r["table"]: r["status"] for r in csv.DictReader(body)}, asof


def main() -> int:
    check = "--check" in sys.argv[1:]
    rows = fetch()
    if check:
        have, asof = read_snapshot()
        want = {t: st for t, _, st in rows}
        drift = sorted(set(want) | set(have))
        drift = [(t, have.get(t, "absent"), want.get(t, "absent"))
                 for t in drift if have.get(t, "absent") != want.get(t, "absent")]
        if not drift:
            print(f"live_tables.csv is current ({len(want)} tables, taken {asof})")
            return 0
        for t, was, now in drift:
            print(f"  {t}: snapshot says {was}, Redivis says {now}")
        print(f"\n{len(drift)} table(s) drifted -- rerun without --check")
        return 1
    OUT.write_text(render(rows, dt.date.today().isoformat()))
    n_pub = sum(1 for _, _, st in rows if st == "published")
    print(f"wrote {OUT.relative_to(SRC)}: {n_pub} published, "
          f"{len(rows) - n_pub} in draft")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
