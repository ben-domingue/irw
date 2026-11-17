#!/usr/bin/env python3
"""Say, for each table named, how the irw MCP server would find its build script.

17_coverage.R used to count a table as having a script only when it had a row
in table_scripts.csv. That index deliberately leaves out every table whose
script has the table's own name (stage 13: "the MCP already handles those"),
so the coverage audit reported ~2,150 tables as script-less that the MCP finds
without trouble (2026-11-16: 4,717 "missing", 1,089 of them exact-name matches).

This runs the one matcher the repository already keeps in step with the MCP --
14_column_docs.py's `match_scripts` (exact stem, then table_scripts.csv, then
a separator-bounded name prefix) -- and writes `table,match` where match is
exact / index / prefix / ambiguous / none. No credentials, no network.

    python3 metadata/script_match.py --tables live.txt --out match.csv
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("column_docs", HERE / "14_column_docs.py")
column_docs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(column_docs)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=HERE.parent)
    parser.add_argument("--tables", type=Path, required=True, help="one table name per line")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    tables = [t.strip() for t in args.tables.read_text(encoding="utf-8").splitlines() if t.strip()]
    paths = column_docs.script_index.data_scripts(args.repo)
    index = column_docs.read_index(args.repo / "metadata" / "table_scripts.csv")
    with args.out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["table", "match"])
        for t in tables:
            w.writerow([t, column_docs.match_scripts(t, paths, index)[1]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
