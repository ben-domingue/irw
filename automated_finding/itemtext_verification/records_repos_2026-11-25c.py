#!/usr/bin/env python3
"""Write the provenance and mapping-verification records for the 2026-11-25c item text batch.

    python3 records_repos_2026-11-25c.py            # dry run: print what would change
    python3 records_repos_2026-11-25c.py --apply

automated_finding/itemtext_provenance.csv already holds one "NOT SHIPPED ..." row per table from the
leads batch; a table built here has that row REPLACED in place (raw bytes, QUOTE_ALL, CRLF, as the
file's rows are), never duplicated, and the rest of the file is left byte-identical. A held table's
row is replaced the same way with a HELD note. itemtext/mapping_verification.csv gets one appended
row per SHIPPED table (LF, QUOTE_ALL, as that file is); a table already present there is an error.
"""
import csv
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
PROV = HERE / "itemtext_provenance.csv"
MV = HERE.parent / "itemtext" / "mapping_verification.csv"
BATCH = "repos_leads_2026-11-25c"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from records_spec_2026_11_25c import RECORDS  # noqa: E402  {table: dict}


def line(fields, end):
    s = io.StringIO()
    csv.writer(s, quoting=csv.QUOTE_ALL, lineterminator=end).writerow(fields)
    return s.getvalue().encode("utf-8")


def main(apply):
    b = PROV.read_bytes()
    mv = MV.read_bytes()
    mv_tables = {r["table"] for r in csv.DictReader(io.StringIO(mv.decode("utf-8")))}
    n_rep = n_app = n_mv = 0
    for table, r in RECORDS.items():
        new = line([table, r["mapping_basis"], r["text_source"], r["source_ref"], r["note"],
                    r.get("public_note", ""), ""], "\r\n")
        key = b'\n"' + table.encode() + b'",'
        if (b"\n" + new) in b and (table in mv_tables or not r.get("shipped", True)):
            continue                       # already written by an earlier run
        i = b.find(key)
        if i >= 0:
            assert b.find(key, i + 1) < 0, ("two provenance rows", table)
            j = b.find(b"\r\n", i + 1)
            assert j > 0 and b[j - 1:j] == b'"', table
            old = b[i + 1:j + 2]
            # the old row must be a leads-batch placeholder, not something already shipped
            assert b'NOT SHIPPED' in old or b'HELD' in old, table
            b = b[:i + 1] + new + b[j + 2:]
            n_rep += 1
        else:
            b = b + new
            n_app += 1
        if r.get("shipped", True):
            assert table not in mv_tables, ("already in mapping_verification", table)
            mv = mv + line([table, BATCH, r["mapping_basis"], "", r["route"], r["status"],
                            r["evidence"]], "\n")
            n_mv += 1
    print(f"provenance: {n_rep} replaced, {n_app} appended; mapping_verification: {n_mv} appended")
    if apply:
        PROV.write_bytes(b)
        MV.write_bytes(mv)
        print("written")


if __name__ == "__main__":
    main("--apply" in sys.argv)
