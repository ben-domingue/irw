"""Work out, and describe, exactly what an upload would do before it does it.

The interesting part is `ELSEWHERE`. Which shard a table lives in is not
predictable from its name, and both client packages search the shards
newest-first and return the first match (ARCHITECTURE.md section 2). So
uploading an existing table into a *newer* shard does not replace it -- it
shadows it, leaving two divergent copies with no error and no suspicious row
count. The only way to notice is to look across every shard first, which is
what `index_tables` does.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from .checks import FileReport
from .targets import Target, eligible

NEW = "NEW"
UPDATE = "UPDATE"
ELSEWHERE = "ELSEWHERE"
SKIP = "SKIP"
EXCLUDED = "EXCLUDED"


@dataclass
class Item:
    report: FileReport
    status: str
    #: Where it will actually go. None means skip.
    dataset: str | None
    #: Datasets that already hold a table of this name.
    found_in: list[str]
    #: Why it was excluded or skipped, shown verbatim.
    note: str = ""

    @property
    def path(self) -> Path:
        return self.report.path

    @property
    def table(self) -> str:
        return self.report.table


def index_tables(owner: str, dataset_names: list[str]) -> dict[str, list[str]]:
    """Map table name -> the datasets holding it, across `dataset_names`.

    list_tables() already returns every Table with its properties populated,
    so there is no per-table .get() here. That round-trip used to cost 0.283s
    x 567 tables -- about 2.7 minutes of pure overhead per run, before a byte
    was uploaded. Datasets are queried in parallel; each call is I/O-bound.
    """
    import redivis

    def fetch(name: str) -> tuple[str, list[str]]:
        dataset = redivis.organization(owner).dataset(name)
        return name, [t.properties["name"] for t in dataset.list_tables()]

    index: dict[str, list[str]] = {}
    with ThreadPoolExecutor(max_workers=min(8, len(dataset_names) or 1)) as pool:
        for name, tables in pool.map(fetch, dataset_names):
            for table in tables:
                index.setdefault(table, []).append(name)
    # Keep the caller's dataset order (oldest shard first) rather than
    # whichever thread finished first.
    order = {name: i for i, name in enumerate(dataset_names)}
    for table in index:
        index[table].sort(key=lambda n: order[n])
    return index


#: `datastandard.md` caps a table name at 40 characters, and `irw_validate`
#: raises that as an error. 130 live tables predate the rule -- the longest is
#: 65 characters -- so enforcing it on the upload path means a table that is
#: already named too long can never be repaired for anything else. Three
#: cov_age fixes were blocked that way (#1779).
#:
#: Ruled by Ben, 2026-09-03: **keep the rule, grandfather the names.** A name
#: over the cap is still an error for a table entering the corpus; for one
#: already in it under that name, it becomes a warning, because a rename is a
#: different piece of work with its own consequences for the metadata joins and
#: for anyone holding the old name.
GRANDFATHERED = "name_length"


def _grandfather_name_length(report: FileReport) -> None:
    """Demote a name-length error on a table that is already published."""
    kept, moved = [], []
    for err in report.errors:
        (moved if err.startswith(f"{GRANDFATHERED}:") else kept).append(err)
    if moved:
        report.errors[:] = kept
        report.warnings.extend(
            f"{m} -- allowed because this name is already published; "
            "the cap governs new tables, not repairs to old ones" for m in moved)


def build(reports: list[FileReport], target: Target,
          index: dict[str, list[str]]) -> list[Item]:
    """Classify every file against the target and the cross-dataset index."""
    items = []
    for report in reports:
        found = index.get(report.table, [])
        if found:
            _grandfather_name_length(report)
        reason = eligible(report.path, target)
        if reason:
            items.append(Item(report=report, status=EXCLUDED, dataset=None,
                              found_in=found, note=reason))
            continue
        if not report.ok:
            status, dataset = SKIP, None
        elif target.name in found:
            status, dataset = UPDATE, target.name
        elif found:
            status, dataset = ELSEWHERE, None   # resolved by the caller
        else:
            status, dataset = NEW, target.name
        items.append(Item(report=report, status=status, dataset=dataset,
                          found_in=found))
    return items
