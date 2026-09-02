"""The one real upload implementation.

Every previous copy of this logic (thirteen of them) reimplemented the same
two paragraphs. The two that matter:

1. Redivis uploads APPEND. `replace_on_conflict` only replaces an *upload* of
   the same name; rows inherited from the previously released version survive
   alongside it, silently doubling the table (#1677/#1683, a batch came back
   at exactly 2x). Deleting the draft table and recreating it is the only true
   replace.
2. Deleting the table drops its description too, so it has to be read back
   first and re-applied -- upload_meta.py already did this, the shard
   uploaders did not, and descriptions were being lost on every update.

Nothing here ever publishes. Redivis keeps an unpublished draft nobody outside
the project can see; that click is always a human action taken after reviewing
a diff (ARCHITECTURE.md section 4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .verify import verify


@dataclass
class UploadResult:
    table: str
    dataset: str
    expected: int
    actual: int | None = None
    error: str | None = None
    #: Uploads found on the table under some other name, cleared by the delete.
    stray_uploads: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.error is None and self.actual == self.expected


def push_one(dataset, path: Path, table_name: str, expected_rows: int) -> UploadResult:
    """Upload one CSV as one table, replacing any existing table of that name."""
    result = UploadResult(
        table=table_name, dataset=dataset.name, expected=expected_rows
    )
    try:
        table = dataset.table(table_name)
        description = None
        if table.exists():
            description = table.get().properties.get("description")
            # An upload on this table with some other name is a leftover from a
            # hand-run or an older script. Deleting the table removes it too,
            # so this is only ever a note -- but it explains a row count that
            # looked wrong before this run. (Ported from upload_meta.py, where
            # it was added after comps_metadata went 23 -> 90 -> 180 rows.)
            try:
                stray = [u.name for u in table.list_uploads() if u.name != table_name]
            except Exception:
                stray = []
            if stray:
                result.stray_uploads = stray
            # The only true replace; see the module docstring.
            table.delete()
            table = dataset.table(table_name)

        table = table.create(description=description) if description else table.create()
        upload = table.upload(path.name)
        with path.open("rb") as handle:
            upload.create(
                handle,
                type="delimited",
                remove_on_fail=True,    # do not leave a half-finished upload behind
                wait_for_finish=True,
                raise_on_fail=True,
            )

        ok, actual = verify(table, expected_rows)
        result.actual = actual
        if not ok:
            result.error = (
                f"row count mismatch: uploaded {expected_rows:,} from the CSV, "
                f"count(*) reports {actual:,}"
            )
    except Exception as exc:  # surfaced per table; the run continues
        result.error = f"{type(exc).__name__}: {exc}"
    return result


def open_draft(owner: str, name: str):
    """Return the dataset's unreleased draft, creating one if there is none.

    `dataset(name, version="next")` raises NotFoundError when the last version
    has been released and no new draft has been opened -- exactly the state a
    dataset is in immediately after someone clicks publish. Every uploader
    this replaces would fail there and say only "Not found: <name>:next".

    `if_not_exists=True` makes this idempotent, so concurrent runs do not race
    to create the same draft.
    """
    import redivis

    dataset = redivis.organization(owner).dataset(name)
    dataset.create_next_version(if_not_exists=True)
    return redivis.organization(owner).dataset(name, version="next")
