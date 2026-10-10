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


#: Redivis caps a dataset at 1000 tables (ARCHITECTURE.md section 2). An upload
#: that would add the 1001st is refused before anything is written; one that
#: leaves a dataset above TABLE_WARN is allowed but says the next shard is due.
TABLE_CAP = 1000
TABLE_WARN = 990


def table_counts(owner: str, dataset_names: list[str]) -> dict[str, int]:
    """Tables per dataset as the next upload will find them.

    The open draft if there is one, since that is where new tables land and it
    can already hold more than the release; else the latest version.
    index_tables cannot answer this: `dataset(name)` lists the release only.
    """
    import redivis

    def fetch(name: str) -> tuple[str, int]:
        try:
            return name, len(redivis.organization(owner).dataset(name, version="next").list_tables())
        except Exception:  # no draft open (NotFoundError), see push.open_draft
            return name, len(redivis.organization(owner).dataset(name).list_tables())

    with ThreadPoolExecutor(max_workers=min(8, len(dataset_names) or 1)) as pool:
        return dict(pool.map(fetch, dataset_names))


def over_cap(items: list[Item], counts: dict[str, int],
             cap: int = TABLE_CAP) -> dict[str, tuple[int, int]]:
    """Datasets this upload would take past `cap`: name -> (now, new tables).

    Only NEW items add a table; an UPDATE replaces one in place.
    """
    adding: dict[str, int] = {}
    for item in items:
        if item.status == NEW and item.dataset:
            adding[item.dataset] = adding.get(item.dataset, 0) + 1
    return {name: (counts[name], n) for name, n in adding.items() if counts[name] + n > cap}


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

#: An item-text table's name is not its own: it must equal its response
#: table's name or the join breaks. `irw_validate` knows this and measures the
#: RESPONSE name -- `_validate_item_text` strips this suffix before calling
#: `check_name` -- so a `name_length` error on item text is a report about a
#: name the upload cannot choose.
#:
#: Ruled by Ben, 2026-09-16 (#2199): exempt a name that matches a live table.
#: Two weatherspoon_2015 tables were skipped by the 2026-09-16 item-text upload
#: for a cap their own response tables have exceeded since they were published,
#: and shortening only the item-text side would ship text that joins to nothing.
ITEMS_SUFFIX = "__items"


def _grandfather_name_length(report: FileReport, inherited: bool = False) -> None:
    """Demote a name-length error on a table that is already published.

    `inherited` says the published name is the RESPONSE table's, not this
    file's own -- the item-text case, where the length was never a choice.
    """
    why = ("allowed because this name is inherited from the response table, "
           "which is already published under it; an item-text table must "
           "carry that exact name or the join breaks"
           if inherited else
           "allowed because this name is already published; "
           "the cap governs new tables, not repairs to old ones")
    kept, moved = [], []
    for err in report.errors:
        (moved if err.startswith(f"{GRANDFATHERED}:") else kept).append(err)
    if moved:
        report.errors[:] = kept
        report.warnings.extend(f"{m} -- {why}" for m in moved)


def build(reports: list[FileReport], target: Target,
          index: dict[str, list[str]]) -> list[Item]:
    """Classify every file against the target and the cross-dataset index."""
    items = []
    for report in reports:
        found = index.get(report.table, [])
        if found:
            _grandfather_name_length(report)
        elif report.table.endswith(ITEMS_SUFFIX) and index.get(
                report.table[: -len(ITEMS_SUFFIX)]):
            # The response table is live under this over-length name, so the
            # length is inherited. Looked up SEPARATELY and deliberately not
            # folded into `found`: `found` decides the destination, and an
            # item-text file must never be routed onto its response table.
            _grandfather_name_length(report, inherited=True)
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


def _family(target: Target) -> str:
    """Core shards are one source; every aux dataset is its own."""
    return "core" if target.kind == "core" else (target.source or target.name)


def cross_source_conflicts(items: list[Item], target: Target,
                           targets: list[Target],
                           index: dict[str, list[str]]) -> None:
    """Refuse a response table whose name another IRW source already uses.

    Table names must be unique across sources, ignoring case (#2454): the site
    builds one flat /tables/<name>/ page per table, and a bare-name lookup --
    item text, the dictionary joins -- cannot tell `enem_2013_1mil_ch` in the
    warehouse from `enem_2013_1mil_ch` in irw_nominal. 59 of the 66 nominal
    tables had exactly that clash before they were renamed to *_nom.

    Item text is exempt in both directions: an `__items` table carries its
    response table's name by design. Within one source a clash is the ordinary
    UPDATE/ELSEWHERE case and is left to `build`.
    """
    if target.is_itemtext or target.is_meta:
        return
    family = {t.name: _family(t) for t in targets}
    mine = _family(target)
    lowered: dict[str, list[str]] = {}
    for name, datasets in index.items():
        for dataset in datasets:
            if family.get(dataset, mine) in (mine, "text"):
                continue
            lowered.setdefault(name.lower(), []).append(f"{dataset}.{name}")
    for item in items:
        if item.status == EXCLUDED:
            continue
        clash = lowered.get(item.table.lower())
        if not clash:
            continue
        error = (f"name_collision: {', '.join(sorted(clash))} already uses this "
                 f"name in another source; table names must be unique across "
                 f"IRW sources, ignoring case (#2454) -- rename this table")
        item.report.errors.append(error)
        item.status, item.dataset = SKIP, None
        item.note = error


def within_source_duplicates(items: list[Item], target: Target,
                             targets: list[Target],
                             index: dict[str, list[str]]) -> None:
    """Warn when an upload touches a name that is, or would become, ambiguous
    inside its own source (#2151).

    Clients resolve a bare name newest-shard-first and case-insensitively, so
    two copies inside one source mean one silently shadows the other. Two cases
    reach an upload:

    - the name is ALREADY in more than one shard of the source -- this upload
      updates one copy and leaves the other (zhou_2025_peer_relationship,
      #2149, was in `_3` and `_5`);
    - a NEW table differs only by case from one already in the source, so it
      would become a second copy under the case-insensitive lookup.

    A warning, not a refusal: `cross_source_conflicts` already refuses the
    cross-source clash (#2457), the within-source case-only question is left
    to the table-name case ruling, and refusing the first case would block the
    very repair that resolves it. `--strict` makes it blocking. The published
    state is reported daily by metadata/drift_report.py.
    """
    if target.is_itemtext or target.is_meta:
        return
    family = {t.name: _family(t) for t in targets}
    mine = _family(target)
    by_lower: dict[str, list[str]] = {}
    for name, datasets in index.items():
        for dataset in datasets:
            if family.get(dataset, mine) == mine:
                by_lower.setdefault(name.lower(), []).append(f"{dataset}.{name}")
    for item in items:
        if item.status in (EXCLUDED, SKIP):
            continue
        held = sorted(by_lower.get(item.table.lower(), []))
        exact = [h for h in held if h.split(".", 1)[1] == item.table]
        if len(held) > 1:
            item.report.warnings.append(
                f"duplicate_name: {', '.join(held)} -- this name is already "
                f"published more than once in this source, and clients read only "
                f"the newest copy; this upload changes one of them (#2151)")
        elif held and not exact:
            item.report.warnings.append(
                f"duplicate_name: {held[0]} differs from this name only by case; "
                f"clients match names case-insensitively, so this would be a second "
                f"copy that shadows or is shadowed by it (#2151)")
