#!/usr/bin/env python3
"""Stage 15 of the weekly pipeline: link new tables' source codebooks (#2770).

Runs `find_codebook_links.py --new-only`: every committed row of
codebook_links.csv / codebook_links_checked.csv for a table already checked
stands, and only tables not in the checked file are swept -- a week's new
tables, minutes not hours, and no local cache needed. It also refreshes the
`recorded_at_ingest` rows from automated_finding/codebook_at_ingest.csv, which
stage_dict_row.py writes when a table is built.

Reads public APIs only (OSF, Dataverse, figshare, Zenodo, Mendeley). The README
check also reads item names from Redivis; without the `redivis` package or a
token those READMEs are left "not checked" rather than failing the run.

`--deep` (#2787 follow-up) also opens a new table's repository deposit past the
file names: workbook sheet names, the member list of each zip (read by HTTP
Range, never downloaded whole), and the text of its documents, judged against
the table's item names like a README. A week's new tables are few, so this
costs seconds to minutes; without Redivis those documents stay unlinked.

A full re-sweep stays manual: `python3 metadata/find_codebook_links.py`.
"""
import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.argv = [str(Path(__file__).with_name("find_codebook_links.py")), "--new-only", "--deep"]
    runpy.run_path(sys.argv[0], run_name="__main__")
