"""Permitted response values for a response table, from its item text (#2152).

`irw_validate`'s `resp_outside_permitted` is a gate error, but it needs a
documented permitted set per item and nothing supplied one. Item-text tables
are keyed on (item, resp), but their `resp` rows are often generated from the
values respondents used ("Rows emitted for every resp level each item's
respondents used"), so feeding them back would be circular: the data could
never fall outside a set built from the data.

What is documented is the LABELS. `option_text` comes from the source, so the
rule, ruled by Ben 2026-09-30, is the **anchor span**: an item's permitted set
is every integer from its lowest to its highest `resp` carrying non-blank
`option_text`. Unlabelled rows in between are not trusted, and are not needed.
Items with fewer than two labelled values, or non-integer labelled values, get
no set. Known blind spot: a scale whose legal values are not every integer
between the anchors (0/5/10) -- rare, and it blocks with a clear message rather
than passing bad data.

Where the item text comes from, in order:
1. a staged `<table>__items.csv` next to the response file -- in its own
   directory or a sibling one, which is how the upload queue stages a shard's
   files (`<queue>/item_response_warehouse_4/x.csv` beside
   `<queue>/irw_text_2/x__items.csv`) -- so a batch that changes both is
   checked against the NEW text whichever is uploaded first. Directories
   holding `provenance.csv` (batch history) are skipped;
2. the published `<table>__items` in whichever item-text shard the run's
   table index found it in;
3. otherwise nothing -- the table keeps today's warn-only behaviour.
Local batch history is deliberately not consulted: it holds superseded
extractions (conner_2017_lot's swapped anchors stayed in batch_303).
"""

from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

ITEMS_SUFFIX = "__items"


def _integer(value) -> int | None:
    if value is None:
        return None
    try:
        d = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    if not d.is_finite() or d != d.to_integral_value():
        return None
    return int(d)


def anchor_spans(rows) -> dict:
    """rows: dicts with item, resp, option_text -> {item: range of ints}.

    Keys are the item-text table's item codes as strings; an all-digit code is
    also keyed as an int, because the validator matches keys exactly and a
    response table with codes 1..10 reads them as integers."""
    labelled: dict[str, list[int]] = {}
    bad: set[str] = set()
    for row in rows:
        item = row.get("item")
        text = row.get("option_text")
        if item is None or text is None or not str(text).strip():
            continue
        item = str(item).strip()
        resp = row.get("resp")
        if resp is None or str(resp).strip() == "":
            continue
        value = _integer(resp)
        if value is None:
            bad.add(item)
            continue
        labelled.setdefault(item, []).append(value)
    spans: dict = {}
    for item, values in labelled.items():
        if item in bad or len(set(values)) < 2:
            continue
        span = range(min(values), max(values) + 1)
        spans[item] = span
        as_int = _integer(item) if item.lstrip("-").isdigit() else None
        if as_int is not None:
            spans[as_int] = span
    return spans


def _from_file(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _from_redivis(owner: str, dataset: str, table: str) -> list[dict]:
    import redivis
    t = redivis.organization(owner).dataset(dataset).table(table).get()
    ref = t.properties["qualifiedReference"]
    query = redivis.query(f"select item, resp, option_text from `{ref}`")
    return query.to_arrow_table(progress=False).to_pylist()


def staged_items(path: Path, table: str, history_marker: str = "provenance.csv") -> Path | None:
    """A `<table>__items.csv` staged beside `path`, in its directory or a sibling."""
    name = table + ITEMS_SUFFIX + ".csv"
    here = path.parent
    dirs = [here] + sorted(d for d in here.parent.iterdir() if d.is_dir() and d != here)
    for d in dirs:
        if (d / history_marker).is_file():
            continue
        cand = d / name
        if cand.is_file():
            return cand
    return None


def lookup(path: Path, table: str, index: dict[str, list[str]],
           itemtext_datasets: set[str], owner: str) -> tuple[dict | None, str]:
    """-> (permitted_values or None, where it came from / why not)."""
    name = table + ITEMS_SUFFIX
    staged = staged_items(path, table)
    if staged is not None:
        rows, source = _from_file(staged), f"staged {staged}"
    else:
        shards = [d for d in index.get(name, []) if d in itemtext_datasets]
        if not shards:
            return None, "no item text"
        try:
            rows = _from_redivis(owner, shards[-1], name)
        except Exception as exc:              # network, auth, a renamed column
            return None, f"could not read {shards[-1]}.{name}: {exc}"
        source = f"{shards[-1]}.{name}"
    spans = anchor_spans(rows)
    if not spans:
        return None, f"{source} labels fewer than two integer anchors per item"
    return spans, source
