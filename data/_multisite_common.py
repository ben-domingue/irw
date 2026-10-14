"""Shared helpers for the #2988 multisite-replication scripts (Many Labs 1/2/4, Many Smiles,
PSACR001, PSA001). Not a data script itself."""
import csv
import pathlib


def write_long(out_dir, table, rows, columns):
    """Write rows (dicts) to <out_dir>/<table>.csv in the given column order and print a line."""
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = [r for r in rows if r["resp"] != ""]
    with open(out / f"{table}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"{table}: {len(rows)} rows, {len({r['id'] for r in rows})} ids, "
          f"{len({r['item'] for r in rows})} items")
    return len(rows)


def int_in(v, lo, hi):
    """Return the string v if it is an integer in [lo, hi], else '' (missing)."""
    v = (v or "").strip()
    if v in ("", "NA", "N", "BLANK"):
        return ""
    try:
        f = float(v)
    except ValueError:
        return ""
    if f != int(f) or not (lo <= int(f) <= hi):
        return ""
    return str(int(f))
