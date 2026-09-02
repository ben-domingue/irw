"""Prove the uploaded table has the rows we sent it.

This exists because the old uploaders' "verification" was a print() telling a
human to run count(*) by hand, and because `numRows` cannot be trusted: it
reported "no change" for tables that had just doubled (#1677/#1683). So the
assertion is an actual count(*) against the draft.
"""

from __future__ import annotations

import redivis


def count_rows(qualified_table: str) -> int:
    """count(*) against a fully qualified Redivis table reference.

    Arrow rather than list_rows(), which the SDK deprecated, and rather than a
    dataframe: the result is a single integer and pulling pandas/pyarrow
    dataframes out of Redivis has its own failure mode here (Python-pkg#5).
    `progress=False` keeps a tqdm bar per table out of the log.
    """
    query = redivis.query(f"select count(*) as n from `{qualified_table}`")
    rows = query.to_arrow_table(progress=False).to_pylist()
    if not rows:
        raise RuntimeError(f"count(*) returned no rows for {qualified_table}")
    return int(rows[0]["n"])


def verify(table, expected: int) -> tuple[bool, int]:
    """Compare the live count against the local data-row count.

    Returns (ok, actual). The caller reports; this raises only if the query
    itself fails, which is a different failure from a count mismatch.
    """
    reference = table.get().properties["qualifiedReference"]
    actual = count_rows(reference)
    return actual == expected, actual
