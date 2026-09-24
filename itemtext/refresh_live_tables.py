#!/usr/bin/env python3
"""Snapshot which item-text tables are actually live, so nothing has to remember.

    python3 itemtext/refresh_live_tables.py            # rewrite live_tables.csv
    python3 itemtext/refresh_live_tables.py --check    # exit 1 if it is out of date

Both modes also report where `extraction_batches/queue_state.csv` disagrees
with what is live (irw#2230). That report never changes the exit status.

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

WHY IT ALSO WATCHES THE QUEUE (irw#2230). A round takes `status=="pending"` to
mean no item text exists for a table, and that is not what it means -- it means
nobody has claimed the row. `preussmattsson_2022_ownership` was re-extracted on
the wrong item axis because of it, over the top of a correct published table,
and a sweep then found six more `pending` rows and one `blocked` row that were
already published. Six of those seven were inside a single claim. A round
runner that has to remember to cross-check is the same class of thing that
produced the defect, so the check lives here, where the live side is already in
hand and gets refreshed daily. It is REPORT-ONLY by design: it prints and
returns nothing, because the fix is always a judgement about one table and
never something a script should make.

Records the draft separately from the published version, because they answer
different questions. A table sitting in `next` is not something a reader can
fetch, so it is not live and does not yet owe an issues-page entry -- treating a
draft as live is how the batch_015 set read as published for the hours between
upload and release. But it is also not missing, and a checker that cannot tell
those apart cries wolf on every table in the release window. So each row carries
a `status` of `published` or `draft`.

Listing a draft needs a `data.edit`-scoped token, which is more than a snapshot
reader should hold: the CI job that runs this daily is given a read-only one, so
it gets a 403 on `next` and only ever sees the published side. That is not worth
failing over -- what CI gates on (a live table that owes the issues page an
entry) is computed from the published rows alone. So an unreadable draft is not
an error: the shard's `draft` rows are carried forward from the previous
snapshot unchanged, the header records that they were, and a refresh run with a
full-scope token (Ben's, during the bookkeeping pass) is what actually moves
them. Carrying forward is the conservative direction -- a stale `draft` row at
worst suppresses an ORPHAN warning for a table that was really released, while
dropping it would invent one for every table in the release window.
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


class DraftUnreadable(Exception):
    """The shard has a draft, but this token may not list it (needs data.edit)."""


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
            # Match on the lowercased message, not the snake_case code alone:
            # the client raises NotFoundError("Not found: datapages.irw_text:next"),
            # which contains neither `not_found` nor `404`, so a shard between
            # releases used to crash the whole refresh and leave the snapshot
            # stale. That is how live_tables.csv went 12 days without updating.
            low = msg.lower()
            if version == "next" and (
                "not_found" in low or "not found" in low or "404" in low
            ):
                return None
            # A read-only token can see `current` but not `next`; Redivis calls
            # that missing scope, not missing data. Distinguished from the case
            # above because they mean opposite things: no draft exists vs. a
            # draft may exist and this run cannot see it.
            if version == "next" and (
                "insufficient_scope" in low or "data.edit" in low
            ):
                raise DraftUnreadable(shard) from exc
            raise
    # Item-text tables end in __items; the bare name is what provenance.csv,
    # the dictionary and the issues page all use.
    return {n[: -len(SUFFIX)] if n.endswith(SUFFIX) else n for n in names}


def fetch() -> tuple[list[tuple[str, str, str]], list[str]]:
    """((bare table name, shard, status), shards whose draft could not be read)."""
    owner, targets = load_registry()
    rows: list[tuple[str, str, str]] = []
    unreadable: list[str] = []
    prior: list[tuple[str, str, str]] | None = None
    for shard in text_shards(targets):
        published = _list(owner, shard.name, "current") or set()
        rows += [(t, shard.name, "published") for t in published]
        try:
            draft = _list(owner, shard.name, "next")
        except DraftUnreadable:
            # Read-only token. Keep what the last full-scope refresh saw, minus
            # anything that has since been released -- a carried row is a claim
            # about the release window, and a published table is past it.
            unreadable.append(shard.name)
            if prior is None:
                prior = read_rows()
            rows += [(t, sh, st) for t, sh, st in prior
                     if sh == shard.name and st == "draft" and t not in published]
            continue
        if draft is not None:
            # Draft-only: uploaded, not yet released. A table the draft DROPS is
            # a staged withdrawal and stays `published` here -- it is still what
            # a reader can fetch today, which is what this file records.
            rows += [(t, shard.name, "draft") for t in draft - published]
    rows.sort()
    return rows, unreadable


QUEUE = HERE / "extraction_batches" / "queue_state.csv"


def read_queue(path: Path = QUEUE) -> dict[str, str]:
    """{table: status} from the extraction queue. Missing file -> {}."""
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as fh:
        return {r["table"]: r["status"] for r in csv.DictReader(fh)
                if r.get("table")}


def queue_divergence(live: dict[str, str],
                     queue: dict[str, str] | None = None) -> list[tuple[str, str]]:
    """Tables the queue calls unfinished that are in fact published (irw#2230).

    Returns [(table, queue status)]. Only this direction is reported, and the
    asymmetry is deliberate:

    * PUBLISHED but the queue says anything other than `done` -- reported. The
      queue is making a claim about the corpus that the corpus contradicts, and
      acting on it re-extracts a table that already has item text.
    * PUBLISHED with no queue row at all -- counted, not listed. The queue is an
      extraction worklist seeded from a candidate set, not a register of every
      table, so this is structural rather than a defect; it stands at several
      hundred and printing it every run would bury the line above.
    * `done` but not live -- NOT reported. That is the ordinary state of every
      batch between merging and upload, so it would fire on healthy work.
    """
    queue = read_queue() if queue is None else queue
    published = {t for t, st in live.items() if st == "published"}
    return sorted((t, queue[t]) for t in published
                  if t in queue and queue[t] != "done")


def report_divergence(live: dict[str, str]) -> None:
    """Print the queue/live divergence. Never raises, never changes exit status."""
    try:
        queue = read_queue()
    except Exception as exc:  # noqa: BLE001
        # A watcher that can break the thing it watches is worse than no
        # watcher: the snapshot refresh is the job here, and this is a comment
        # on it.
        print(f"NOTE: could not read {QUEUE.name} for the divergence check ({exc})")
        return
    if not queue:
        return
    drift = queue_divergence(live, queue)
    published = {t for t, st in live.items() if st == "published"}
    unlisted = len(published - set(queue))
    if drift:
        print(f"\nQUEUE DIVERGENCE: {len(drift)} table(s) are published but "
              f"queue_state.csv does not say `done` (irw#2230) --")
        for t, st in drift:
            print(f"  {t}: queue says {st}, but item text is published")
        print("  Item text already exists for these. Correct the queue row "
              "rather than extracting them.")
    if unlisted:
        print(f"\nNOTE: {unlisted} published table(s) have no queue_state row at "
              f"all. The queue is a worklist, not a register, so this is "
              f"expected; it is counted here only so a jump is visible.")


def render(rows: list[tuple[str, str, str]], asof: str,
           unreadable: list[str] | None = None,
           carried_from: str | None = None) -> str:
    head = [
        f"# item-text tables in the Redivis shards as of {asof}",
        "# status=published: a reader can fetch it. status=draft: uploaded, not released yet.",
        "# generated -- do not hand-edit; rerun itemtext/refresh_live_tables.py (irw#1828)",
    ]
    if unreadable:
        # Says so in the file itself, because the alternative is a `draft` row
        # whose date silently means something older than the header claims.
        head.append(
            "# draft not listable by this token (needs data.edit) for "
            + ", ".join(sorted(unreadable))
            + f"; its draft rows carried forward from the snapshot taken {carried_from}"
        )
    head.append("table,shard,status")
    return "\n".join(head + [f"{t},{sh},{st}" for t, sh, st in rows]) + "\n"


def read_rows(path: Path = OUT) -> list[tuple[str, str, str]]:
    """The snapshot's rows as (table, shard, status). Missing file -> []."""
    if not path.exists():
        return []
    body = [ln for ln in path.read_text().splitlines()
            if ln and not ln.startswith("#")]
    return [(r["table"], r["shard"], r["status"]) for r in csv.DictReader(body)]


def read_snapshot(path: Path = OUT) -> tuple[dict[str, str], str | None]:
    """{table: status} and the date it was taken. Missing file -> ({}, None)."""
    if not path.exists():
        return {}, None
    asof = None
    for line in path.read_text().splitlines():
        # The first `as of` line is the header date; a later comment may mention
        # an older date it carried rows forward from, which is not this one.
        if line.startswith("#") and " as of " in line:
            asof = line.rsplit(" as of ", 1)[1].strip()
            break
    return {t: st for t, _, st in read_rows(path)}, asof


def main() -> int:
    check = "--check" in sys.argv[1:]
    _, prior_asof = read_snapshot()
    rows, unreadable = fetch()
    if unreadable:
        print("WARNING: could not list the draft of "
              + ", ".join(sorted(unreadable))
              + " (token lacks data.edit); its draft rows are carried forward "
              + f"from the snapshot taken {prior_asof}. Rerun with a full-scope "
              + "token to move them.")
    if check:
        have, asof = read_snapshot()
        want = {t: st for t, _, st in rows}
        drift = sorted(set(want) | set(have))
        drift = [(t, have.get(t, "absent"), want.get(t, "absent"))
                 for t in drift if have.get(t, "absent") != want.get(t, "absent")]
        if not drift:
            print(f"live_tables.csv is current ({len(want)} tables, taken {asof})")
            report_divergence(want)
            return 0
        for t, was, now in drift:
            print(f"  {t}: snapshot says {was}, Redivis says {now}")
        print(f"\n{len(drift)} table(s) drifted -- rerun without --check")
        report_divergence(want)
        return 1
    OUT.write_text(render(rows, dt.date.today().isoformat(),
                          unreadable, prior_asof))
    n_pub = sum(1 for _, _, st in rows if st == "published")
    print(f"wrote {OUT.relative_to(SRC)}: {n_pub} published, "
          f"{len(rows) - n_pub} in draft")
    report_divergence({t: st for t, _, st in rows})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
