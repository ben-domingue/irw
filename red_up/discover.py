"""Turn a path argument into the list of CSVs to upload."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Discovery:
    csvs: list[Path] = field(default_factory=list)
    #: Non-CSV files found and skipped. Shown, because a file the uploader
    #: silently ignores is as surprising as one it silently uploads.
    skipped: list[Path] = field(default_factory=list)


def table_name(path: Path) -> str:
    """The Redivis table name a file becomes.

    `foo.csv` -> `foo`, `foo__items.csv` -> `foo__items`. Only the final
    extension is stripped: the old uploaders used `split('.')[0]`, which
    truncates any name containing a dot.
    """
    return path.name[: -len(path.suffix)] if path.suffix else path.name


def discover(path: Path) -> Discovery:
    """Collect CSVs from a file or (recursively) a directory.

    The caller resolves `path` to an absolute path first. The old uploaders
    chdir'd into the script's own directory before reading their argument, so
    `upload.py .` never meant the caller's cwd; red_up never chdirs.
    """
    found = Discovery()
    if path.is_file():
        if path.suffix.lower() == ".csv":
            found.csvs.append(path)
        else:
            found.skipped.append(path)
        return found

    for entry in sorted(path.rglob("*")):
        if not entry.is_file():
            continue
        if entry.suffix.lower() == ".csv":
            found.csvs.append(entry)
        else:
            found.skipped.append(entry)
    return found
