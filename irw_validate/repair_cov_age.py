"""Rebuild a table with its out-of-range `cov_age` nulled, ready for `red_up`.

    python3 -m irw_validate.repair_cov_age --from-file tables.txt -o /some/dir
    python3 -m irw_validate.repair_cov_age acunamora_2018_gypes -o /some/dir

The repair half of `live_cov_range.py`, for the tables that measurement showed
have nothing to recover -- a value the respondent could not have meant, with the
true age recorded nowhere. Setting it to NULL is the whole fix, and for 52 of
the 81 tables in #1779 it touches one or two respondents.

**The repair happens in the SELECT, not here.** What comes back over the wire is
already the fixed table, so there is no download-then-edit step in which a
column could pick up a different type or a float could be reformatted.
`SELECT * REPLACE` leaves every other column exactly as it was, and `IF()`
preserves `cov_age`'s own type -- an integer column stays an integer.

Every table is checked against `results/cov_age_repair_<date>.csv` before it is
written: the row count must be unchanged and the null count must have risen by
exactly the number of bad rows that were measured. A table that fails is not
written at all. Nothing here uploads: hand the directory to Ben.

Two things this needs that the plain client does not give you:

* `redivis_shim`, without which no full-table read completes at all.
* patience -- this is a real export, unlike the aggregate measuring, so run it
  under `nice` and only over tables that need it.
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys
import time

LO, HI = 0, 120

SQL = """
SELECT * REPLACE(
  IF(SAFE_CAST(`cov_age` AS FLOAT64) BETWEEN {lo} AND {hi}, `cov_age`, NULL) AS `cov_age`
) FROM `{ref}`
"""


def _fetch(redivis, ref: str):
    """to_arrow_table with a retry: the stream truncates occasionally."""
    for attempt in range(5):
        try:
            return redivis.query(SQL.format(ref=ref, lo=LO, hi=HI)).to_arrow_table(
                progress=False), attempt + 1
        except OSError as exc:
            if attempt == 4 or "message body" not in str(exc):
                raise
            time.sleep(2 * (attempt + 1))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("tables", nargs="*")
    p.add_argument("--from-file", help="file of table names, one per line")
    p.add_argument("-o", "--out-dir", required=True)
    p.add_argument("--measurements",
                   default="irw_validate/results/cov_age_repair_2026-09-03.csv",
                   help="live_cov_range output the result is checked against")
    a = p.parse_args(argv)

    tables = list(a.tables)
    if a.from_file:
        tables += [ln.strip() for ln in open(a.from_file) if ln.strip()]
    if not tables:
        p.error("give table names, or --from-file")

    import pyarrow.csv as pacsv

    src_root = pathlib.Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(src_root))
    import redivis_shim
    redivis_shim.install()
    from irw_validate.live_dup import _authenticate, shard_index

    out_dir = pathlib.Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "repair_log.jsonl"
    expected = {r["table"]: r for r in csv.DictReader(
        open(src_root / a.measurements))}

    redivis = _authenticate(src_root)
    idx = shard_index(redivis, src_root / "irw_validate/results/.shard_index.json")
    done = ({json.loads(ln)["table"] for ln in log_path.open()}
            if log_path.exists() else set())

    failures = 0
    with log_path.open("a") as log:
        for i, t in enumerate(tables, 1):
            if t in done:
                print(f"[{i}/{len(tables)}] {t} (done)")
                continue
            rec = {"table": t}
            try:
                ref = idx[t][0]
                tb, rec["attempts"] = _fetch(redivis, ref)
                e = expected[t]
                rec["ref"] = ref
                rec["n_rows"] = tb.num_rows
                rec["expected_rows"] = int(e["n_rows"])
                rec["cov_age_nulls"] = tb.column("cov_age").null_count
                rec["expected_nulls"] = int(e["n_null"]) + int(e["n_bad_rows"])
                rec["ok"] = (rec["n_rows"] == rec["expected_rows"]
                             and rec["cov_age_nulls"] == rec["expected_nulls"])
                if rec["ok"]:
                    pacsv.write_csv(tb, out_dir / f"{t}.csv")
            except Exception as exc:
                rec["error"] = str(exc)[:300]
            failures += not rec.get("ok")
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(f"[{i}/{len(tables)}] {t} "
                  f"rows={rec.get('n_rows')}/{rec.get('expected_rows')} "
                  f"nulls={rec.get('cov_age_nulls')}/{rec.get('expected_nulls')} "
                  f"ok={rec.get('ok')} {rec.get('error', '')[:70]}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
