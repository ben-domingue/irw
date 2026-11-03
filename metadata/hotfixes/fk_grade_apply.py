"""Patch itemtext_metadata.csv's FK_grade cells from a fk_grade_per_item.R log.

Only rows logged with status "ok" are touched; a non-English row becomes "NA"
(the file's null). Every other cell keeps its original text, and the file keeps
its CRLF line endings (ben-domingue/irw#3229).

    python3 hotfixes/fk_grade_apply.py logs/fk_grade_backfill_<date>.csv
"""
import csv, sys

log_path = sys.argv[1]
path = "itemtext_metadata.csv"
with open(log_path, newline="") as fh:
    new = {r["table"]: r["new"] for r in csv.DictReader(fh) if r["status"] == "ok"}
with open(path, newline="") as fh:
    raw = fh.read()
eol = "\r\n" if "\r\n" in raw else "\n"
rows = list(csv.reader(raw.splitlines()))
head = rows[0]; ti, fi = head.index("table"), head.index("FK_grade")
changed = 0
for r in rows[1:]:
    if r[ti] in new:
        v = new[r[ti]]
        v = "NA" if v in ("", "NA") else repr(float(v)) if "e" not in v else v
        if r[fi] != v:
            r[fi] = v; changed += 1
with open(path, "w", newline="") as fh:
    csv.writer(fh, lineterminator=eol).writerows(rows)
print(f"{changed} FK_grade cells changed of {len(rows) - 1} rows")
