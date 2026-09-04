"""Measure an out-of-range `cov_age` against the LIVE corpus, one table at a time.

    python3 -m irw_validate.live_cov_range TABLE [TABLE ...] -o results/cov_age.csv
    python3 -m irw_validate.live_cov_range --from-file tables.txt -o out.csv --resume

Written for #1779, which enumerated 81 tables whose `cov_age` holds a sentinel,
a birth year or a date offset but could not say *how much* of each table was
affected -- and that is the number the repair decision turns on. A table where
one respondent typed 999 and a table whose whole column is a date of birth are
the same row in `tags/age_range_audit.csv` and need opposite fixes.

**Queries, never irw_fetch.** Same reason as `live_dup`: the export allowance is
200GB/30 days against a 181.8GB corpus, and every measure here is an aggregate
or a value histogram of the offending values only, so this reads nothing but
counts.

Per table it returns the in-range extent, how many rows and how many *distinct
respondents* hold a value outside [0, 120], and the histogram of those values
with an id count each. The respondent count is the one that matters: 52 of the
81 turned out to be one or two people.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import sys

LO, HI = 0.0, 120.0
FIELDS = ["table", "ref", "n_rows", "n_ids", "n_null", "n_bad_rows", "n_bad_ids",
          "share_bad_ids", "ok_min", "ok_max", "bad_values", "error"]


def _summary_sql(ref: str) -> str:
    return f"""
WITH v AS (SELECT SAFE_CAST(`cov_age` AS FLOAT64) a, `id` FROM `{ref}`)
SELECT COUNT(*) n_rows, COUNT(DISTINCT id) n_ids,
 COUNTIF(a IS NULL) n_null,
 COUNTIF(a IS NOT NULL AND (a < {LO} OR a > {HI})) n_bad_rows,
 (SELECT COUNT(DISTINCT id) FROM v WHERE a < {LO} OR a > {HI}) n_bad_ids,
 MIN(IF(a BETWEEN {LO} AND {HI}, a, NULL)) ok_min,
 MAX(IF(a BETWEEN {LO} AND {HI}, a, NULL)) ok_max
FROM v
"""


def _values_sql(ref: str) -> str:
    return f"""
WITH v AS (SELECT SAFE_CAST(`cov_age` AS FLOAT64) a, `id` FROM `{ref}`)
SELECT a AS value, COUNT(*) n_rows, COUNT(DISTINCT id) n_ids
FROM v WHERE a IS NOT NULL AND (a < {LO} OR a > {HI})
GROUP BY a ORDER BY a
"""


def measure(redivis, idx: dict, table: str) -> dict:
    rec = {"table": table, "error": ""}
    try:
        refs = idx.get(table)
        if not refs:
            rec["error"] = "not found in any core shard (renamed, or not published)"
            return rec
        ref = refs[0]
        rec["ref"] = ref
        s = redivis.query(_summary_sql(ref)).to_arrow_table(progress=False).to_pylist()[0]
        rec.update(s)
        rec["share_bad_ids"] = (round(s["n_bad_ids"] / s["n_ids"], 5)
                                if s["n_ids"] else "")
        vals = redivis.query(_values_sql(ref)).to_arrow_table(progress=False).to_pylist()
        # value:n_ids pairs, so a reader can tell a lone 999 from a whole column
        # of birth years without going back to the server.
        rec["bad_values"] = "|".join(f"{v['value']:g}:{v['n_ids']}" for v in vals)
    except Exception as exc:
        rec["error"] = str(exc)[:300]
    return rec


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("tables", nargs="*")
    p.add_argument("--from-file", help="file of table names, one per line")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--resume", action="store_true",
                   help="skip tables already present in the output CSV")
    a = p.parse_args(argv)

    tables = list(a.tables)
    if a.from_file:
        tables += [ln.strip() for ln in open(a.from_file) if ln.strip()]
    if not tables:
        p.error("give table names, or --from-file")

    if hasattr(os, "nice") and os.nice(0) < 10:
        print("note: this machine runs other people's work -- consider nice -n 19",
              file=sys.stderr)

    src_root = pathlib.Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(src_root))
    from irw_validate.live_dup import _authenticate, shard_index
    redivis = _authenticate(src_root)
    idx = shard_index(redivis, pathlib.Path(a.out).parent / ".shard_index.json")

    done = set()
    if a.resume and os.path.exists(a.out):
        done = {r["table"] for r in csv.DictReader(open(a.out))}
    fresh = not os.path.exists(a.out) or not a.resume
    with open(a.out, "w" if fresh else "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if fresh:
            w.writeheader()
        for i, t in enumerate(tables, 1):
            if t in done:
                print(f"[{i}/{len(tables)}] {t} (done)")
                continue
            rec = measure(redivis, idx, t)
            w.writerow({k: rec.get(k, "") for k in FIELDS})
            f.flush()
            print(f"[{i}/{len(tables)}] {t} bad_ids={rec.get('n_bad_ids')}"
                  f"/{rec.get('n_ids')} ok=[{rec.get('ok_min')},{rec.get('ok_max')}]"
                  f" {rec['error'][:60]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
