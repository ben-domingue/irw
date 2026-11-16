#!/usr/bin/env python3
"""Sort a pipeline output CSV into a stable, case-insensitive key order.

Why this exists
---------------
The pipeline's outputs are committed (see the block in .gitignore), and the
weekly diff -- both diff_csv.py's report and the pull request the workflow
opens -- is the product. That only works if a run which changes nothing
produces a byte-identical file.

It did not. The first full GitHub Actions run produced a 30,668-line diff on
biblio.csv in which **0 of 4,184 existing rows had any field changed**: 86
tables were added and the rest was pure reordering, because the stages write
rows in whatever order Redivis and the Google Sheets happened to return them.
A diff like that is unreviewable, and stored weekly it defeats git's delta
compression as well.

metadata.csv looked fine in that same run (+91/-3), but that is luck rather
than design: it is not sorted either, merely stable so far. Sorting makes the
property something we control.

Case-insensitive, deliberately
------------------------------
308 of the table names are not lowercase. A plain sort hoists every one of them
into a block at the top, away from the neighbours a reader expects them beside
-- and this is the same population behind the case-sensitive join bugs that
have bitten this project before. `str.lower` keeps ALSECYPIAMH_WU_2022_CPS
next to its lowercase siblings.

The sort is stable, so rows sharing a key keep their relative order.

Usage:
    canonicalize_csv.py FILE --key table
    canonicalize_csv.py FILE --key table,collection
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

# Some biblio rows carry embedded BibTeX with very long single fields.
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=Path)
    ap.add_argument("--key", default="table",
                    help="comma-separated key column(s) to sort by")
    args = ap.parse_args()

    if not args.path.is_file():
        print(f"canonicalize: {args.path} does not exist, skipping")
        return 0

    keys = [k.strip() for k in args.key.split(",") if k.strip()]

    with args.path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if not fieldnames:
        print(f"canonicalize: {args.path.name} is empty, skipping")
        return 0

    missing = [k for k in keys if k not in fieldnames]
    if missing:
        # Not fatal: a stage that changes its columns should not break the run
        # before the diff has had a chance to report the change.
        print(f"canonicalize: {args.path.name} has no column(s) "
              f"{', '.join(missing)}; leaving order untouched")
        return 0

    before = [tuple(r.get(k) or "" for k in keys) for r in rows]
    rows.sort(key=lambda r: tuple((r.get(k) or "").lower() for k in keys))
    after = [tuple(r.get(k) or "" for k in keys) for r in rows]

    # The canonical form is the ORDER and the BYTES: CRLF and minimal quoting
    # (the csv module's defaults, which 19_item_classical.py and 20_k1.py also
    # write). Deciding on order alone let a file flip format from run to run:
    # 08_itemtext.R writes quoted LF with new rows on top, so a run that added
    # rows got re-sorted to CRLF and a run that added none kept R's LF -- every
    # line of itemtext_metadata.csv rewritten each time it flipped (2,655 lines
    # in the 2026-11-10 run, #3460, with no field changed).
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    out = buf.getvalue().encode("utf-8")

    if out == args.path.read_bytes():
        print(f"canonicalize: {args.path.name} already canonical ({len(rows)} rows)")
        return 0

    tmp = args.path.with_suffix(args.path.suffix + ".tmp")
    tmp.write_bytes(out)
    tmp.replace(args.path)
    what = f"sorted by {args.key}" if before != after else "rewritten in canonical form"
    print(f"canonicalize: {args.path.name} {what} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
