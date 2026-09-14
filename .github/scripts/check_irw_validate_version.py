"""Fail the release if the tag and irw_validate/pyproject.toml disagree.

PyPI never allows a version to be re-uploaded, even after deletion, so a
mismatch caught after the upload cannot be fixed -- only worked around with a
version number nobody asked for. This runs before the build.

Called with the tag name, or with "" for a workflow_dispatch run, where there
is no tag to compare and the check is a no-op.
"""
from __future__ import annotations

import pathlib
import re
import sys

PREFIX = "irw-validate-v"
PYPROJECT = pathlib.Path(__file__).resolve().parents[2] / "irw_validate" / "pyproject.toml"


def declared_version() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    # Deliberately not tomllib: this must run on the oldest Python the workflow
    # might pin, and the field is unambiguous.
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if match is None:
        sys.exit(f"no version field found in {PYPROJECT}")
    return match.group(1)


def main(argv: list[str]) -> int:
    version = declared_version()
    tag = argv[1] if len(argv) > 1 else ""
    if not tag:
        print(f"no tag (workflow_dispatch); pyproject declares {version}")
        return 0
    if not tag.startswith(PREFIX):
        sys.exit(
            f"tag {tag!r} does not start with {PREFIX!r}. Only irw_validate is "
            f"released from this repository, so its tags say so."
        )
    tagged = tag[len(PREFIX):]
    if tagged != version:
        sys.exit(
            f"tag {tag!r} means version {tagged!r}, but "
            f"irw_validate/pyproject.toml declares {version!r}. Bump the "
            f"pyproject in a PR, merge it, then tag the merge commit."
        )
    print(f"tag {tag} matches pyproject version {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
