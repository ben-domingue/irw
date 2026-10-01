"""Append withdrawn tables to `itemtext/withdrawals.csv`, the table-keyed record (#2155).

A withdrawal writes its reason into a per-table `provenance.csv` only when the
table was built by the batch pipeline, and the rights register is organised by
instrument. So a table that predates the pipeline had nothing anywhere keyed by
its own name: `git grep aspirations_sonmez_2022` found no reason it was gone,
and #2132 was filed asserting there was none. This file is that reverse index --
one row per withdrawn table, whatever the reason, grep-able by name.

Append-only. Rows are never rewritten or removed; a table withdrawn twice gets
two rows. The one column filled after the fact is `released`, the version at
which the withdrawal left `current` -- a draft deletion is not a withdrawal
anyone can see until Ben publishes it, and the row is written at deletion time.

Usage, from a withdrawal script, AFTER the draft assertions pass:

    from ledger import record
    record(TARGETS, dataset="irw_text", reason="rights", family="PSS",
           refs="#1955", note="canonical PSS-10 wording", script=__file__)
"""
from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "itemtext" / "withdrawals.csv"

COLUMNS = ["table", "dataset", "kind", "withdrawn", "reason", "family", "refs",
           "rows", "released", "script", "note"]
#: Why a table left. `rights` rows name the register `family` they rest on.
#: `source_withdrawn`: the author took the source deposit down (#2565).
#: `out_of_scope`: not item responses, e.g. a table whose only "response" is a
#: physical measure such as amount consumed (#1700).
REASONS = {"rights", "wrong_data", "duplicate", "personal_data", "misnamed",
           "unlicensed", "source_withdrawn", "out_of_scope"}
KINDS = {"whole", "partial"}


def record(tables, *, dataset: str, reason: str, kind: str = "whole",
           family: str = "", refs: str = "", rows: dict | None = None,
           note: str = "", script: str = "", when: str | None = None,
           path: Path = LEDGER) -> int:
    """Append one row per table. Returns the number of rows written.

    `rows` maps table -> row count at withdrawal, when the script measured it.
    Refuses an unknown reason or kind rather than inventing a category.
    """
    if reason not in REASONS:
        raise ValueError(f"reason {reason!r} not in {sorted(REASONS)}")
    if kind not in KINDS:
        raise ValueError(f"kind {kind!r} not in {sorted(KINDS)}")
    if reason == "rights" and not family:
        raise ValueError("a rights withdrawal names its register `family`")
    if script:
        p = Path(script).resolve()
        script = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else script
    when = when or dt.date.today().isoformat()
    rows = rows or {}
    new = not path.exists()
    with path.open("a", newline="") as fh:
        w = csv.DictWriter(fh, COLUMNS, quoting=csv.QUOTE_MINIMAL)
        if new:
            w.writeheader()
        n = 0
        for t in sorted(tables):
            w.writerow({"table": t, "dataset": dataset, "kind": kind,
                        "withdrawn": when, "reason": reason, "family": family,
                        "refs": refs, "rows": rows.get(t, ""), "released": "",
                        "script": script, "note": note})
            n += 1
    return n
