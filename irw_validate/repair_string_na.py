"""Rebuild a table with the literal "NA" in `resp` (and `rt`) made a true null (#2029).

    python3 -m irw_validate.repair_string_na --from-file tables.txt -o /some/dir
    python3 -m irw_validate.repair_string_na identity_fusion_gomez_2025 -o /some/dir
    python3 -m irw_validate.repair_string_na --verify-draft -o /some/dir

`write.csv(na = "NA")` wrote the two-character token into published tables, and
one token types the whole column `string` on Redivis. Ruled 2026-09-09: repair
only the low-share worklist (`results/resp_na_lowshare_worklist_2026-09-09.csv`),
leave missing rows as rows. Ruled 2026-09-19 (#2141): clear `rt` in the same
write, casting it only if every surviving value parses. No other column changes.

Modelled on `repair_cov_age`: **the repair happens in the SELECT**, so what comes
back is already the fixed table and `SELECT * REPLACE` leaves every other column
as it was. Per table, in order:

1. **Probe** (aggregate, no export). Counts `"NA"`, blanks and nulls, and the
   values that will not parse as a number. A table with even one unparseable
   `resp` value is not written -- that is a different defect, not this one.
   Values with no fractional part are cast to INT64, anything else to FLOAT64
   (some `resp` columns are continuous scores).
2. **Fetch** the repaired table.
3. **Check** it against the probe: same row count, `resp` nulls risen by
   exactly the `"NA"` and blank count, and the sum of the numeric values
   unchanged. A table that fails is not written.

Output lands in `<out>/<shard>/<table>.csv`, one directory per shard, so each can
be handed to `python3 -m red_up <dir> --dataset <shard> --yes` as it stands.

`--verify-draft` runs after the upload. `red_up` has already proved the row
count, so this checks what it cannot: that every column other than `resp`/`rt`
kept its Redivis type through the CSV round trip (an `id` of `"001"` re-inferred
as an integer would lose its zeros), and that `resp` is now numeric.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
import sys
import time

WORKLIST = "irw_validate/results/resp_na_lowshare_worklist_2026-09-09.csv"
STRINGY = {"string"}
NUMERIC_TYPES = {"integer", "float"}


def _probe_sql(ref: str, col: str) -> str:
    v = f"TRIM(`{col}`)"
    f = f"SAFE_CAST({v} AS FLOAT64)"
    return f"""
SELECT
  COUNT(*) AS n,
  COUNTIF(`{col}` IS NULL) AS n_null,
  COUNTIF({v} = 'NA') AS n_na,
  COUNTIF({v} = '') AS n_blank,
  COUNTIF(`{col}` IS NOT NULL AND {v} NOT IN ('NA', '') AND {f} IS NULL) AS n_bad,
  COUNTIF(IS_NAN({f}) OR IS_INF({f})) AS n_nonfinite,
  COUNTIF({f} IS NOT NULL AND {f} != TRUNC({f})) AS n_frac,
  SUM({f}) AS total
FROM `{ref}`
"""


def _expr(col: str, target: str | None) -> str:
    """NA and blank -> NULL; then cast, or leave as string when target is None."""
    cleaned = f"NULLIF(NULLIF(TRIM(`{col}`), 'NA'), '')"
    if target is None:
        # rt that does not parse: clear the token, keep the column a string
        return f"IF(TRIM(`{col}`) = 'NA', NULL, `{col}`)"
    if target == "INT64":
        # via FLOAT64 so that "1.0" becomes 1 rather than NULL
        return f"CAST(SAFE_CAST({cleaned} AS FLOAT64) AS INT64)"
    return f"SAFE_CAST({cleaned} AS FLOAT64)"


def _one_row(redivis, sql: str) -> dict:
    df = redivis.query(sql).to_pandas_dataframe()
    return {k: (None if (isinstance(v, float) and math.isnan(v)) else v)
            for k, v in df.iloc[0].to_dict().items()}


def _fetch(redivis, sql: str):
    """to_arrow_table with a retry: the stream truncates occasionally."""
    for attempt in range(5):
        try:
            return redivis.query(sql).to_arrow_table(progress=False), attempt + 1
        except OSError as exc:
            if attempt == 4 or "message body" not in str(exc):
                raise
            time.sleep(2 * (attempt + 1))


def _retry(fn, what: str):
    """Redivis sometimes answers with an error and an empty body (throttling or a
    5xx); SDK 0.20.14 then dies in raise_api_error with AttributeError instead of
    reporting it. Both are transient: back off and try again."""
    for attempt in range(6):
        try:
            return fn()
        except AttributeError as exc:
            if "'get'" not in str(exc) or attempt == 5:
                raise
        except Exception as exc:
            if attempt == 5 or not any(k in str(exc) for k in ("429", "500", "502", "503", "internal")):
                raise
        time.sleep(5 * 2 ** attempt)
    raise RuntimeError(f"unreachable: {what}")


def _types(table) -> dict[str, str]:
    return _retry(lambda: {v.name: v.properties.get("type") for v in table.list_variables()},
                  "list_variables")


def _close(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-6)


def repair(redivis, idx, shards, name: str, out_dir: pathlib.Path) -> dict:
    import pyarrow.csv as pacsv

    rec = {"table": name, "shard": shards[name]}
    ref = next(r for r in idx[name] if f".{shards[name]}:" in r)
    rec["ref"] = ref
    tbl = redivis.organization("datapages").dataset(
        shards[name], version="current").table(name)
    types = _types(tbl)
    rec["types_before"] = types
    if types.get("resp") not in STRINGY:
        rec["skip"] = f"resp is already {types.get('resp')}"
        return rec

    cols = ["resp"] + (["rt"] if types.get("rt") in STRINGY else [])
    replace, probes = [], {}
    for col in cols:
        p = _one_row(redivis, _probe_sql(ref, col))
        probes[col] = p
        if p["n_nonfinite"]:
            rec["skip"] = f"{col}: {p['n_nonfinite']} NaN/Inf values"
            rec["probes"] = probes
            return rec
        if p["n_bad"]:
            if col == "resp":
                rec["skip"] = f"resp: {p['n_bad']} values that are not numbers"
                rec["probes"] = probes
                return rec
            target = None                       # rt: clear the token only
        else:
            target = "INT64" if p["n_frac"] == 0 else "FLOAT64"
        p["target"] = target
        replace.append(f"{_expr(col, target)} AS `{col}`")
    rec["probes"] = probes

    sql = f"SELECT * REPLACE({', '.join(replace)}) FROM `{ref}`"
    tb, rec["attempts"] = _fetch(redivis, sql)
    problems = []
    n = probes["resp"]["n"]
    if tb.num_rows != n:
        problems.append(f"rows {tb.num_rows} != {n}")
    for col, p in probes.items():
        c = tb.column(col)
        if p["target"] is None:
            want = p["n_null"] + p["n_na"]
        else:
            want = p["n_null"] + p["n_na"] + p["n_blank"]
        if c.null_count != want:
            problems.append(f"{col} nulls {c.null_count} != {want}")
        if p["target"] is not None:
            import pyarrow.compute as pc
            got = pc.sum(c).as_py()
            if not _close(got, p["total"]):
                problems.append(f"{col} sum {got} != {p['total']}")
    if list(tb.column_names) != list(types):
        problems.append("column order changed")
    rec["problems"] = problems
    rec["ok"] = not problems
    if rec["ok"]:
        d = out_dir / shards[name]
        d.mkdir(parents=True, exist_ok=True)
        pacsv.write_csv(tb, d / f"{name}.csv")
        rec["n_rows"] = tb.num_rows
    return rec


def verify_draft(redivis, log_path: pathlib.Path) -> int:
    recs = [json.loads(ln) for ln in log_path.open()]
    recs = [r for r in recs if r.get("ok")]
    bad = unchanged = 0
    # A failed replace in red_up deletes the table before the upload fails, so a
    # release would delete it from the corpus. Any current table absent from the
    # draft is fatal, whether or not this run touched it.
    for shard in sorted({r["shard"] for r in recs}):
        cur = _retry(lambda: {t.name for t in redivis.organization("datapages").dataset(
            shard, version="current").list_tables()}, "list_tables")
        nxt = _retry(lambda: {t.name for t in redivis.organization("datapages").dataset(
            shard, version="next").list_tables()}, "list_tables")
        if cur - nxt:
            bad += 1
            print(f"MISSING from the {shard} draft: {sorted(cur - nxt)}")
    for r in recs:
        t = redivis.organization("datapages").dataset(
            r["shard"], version="next").table(r["table"])
        if not _retry(t.exists, "exists"):
            continue                          # reported above
        after = _types(t)
        before = r["types_before"]
        if after == before:
            # red_up refused it (e.g. unexplained id+item repeats): the draft still
            # holds the published table, untouched. Not a failure; not repaired.
            unchanged += 1
            print(f"{r['shard']}.{r['table']}: NOT UPLOADED (draft unchanged)")
            continue
        issues = []
        for col, typ in before.items():
            if col in r["probes"]:
                want = {"INT64": "integer", "FLOAT64": "float", None: typ}[
                    r["probes"][col]["target"]]
                if after.get(col) != want:
                    issues.append(f"{col}: {after.get(col)}, wanted {want}")
            elif after.get(col) != typ:
                issues.append(f"{col}: {typ} -> {after.get(col)}")
        extra = set(after) - set(before)
        if extra:
            issues.append(f"new columns {sorted(extra)}")
        bad += bool(issues)
        print(f"{r['shard']}.{r['table']}: {'OK' if not issues else '; '.join(issues)}")
    print(f"{len(recs) - bad - unchanged}/{len(recs)} repaired in the draft with every "
          f"column type kept; {unchanged} not uploaded; {bad} problems")
    return 1 if bad else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("tables", nargs="*")
    p.add_argument("--from-file", help="file of table names, one per line")
    p.add_argument("-o", "--out-dir", required=True)
    p.add_argument("--verify-draft", action="store_true",
                   help="after upload: check the draft tables' column types")
    a = p.parse_args(argv)

    src_root = pathlib.Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(src_root))
    import redivis_shim
    redivis_shim.install()
    from irw_validate.live_dup import _authenticate, shard_index

    out_dir = pathlib.Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "repair_log.jsonl"
    redivis = _authenticate(src_root)

    if a.verify_draft:
        return verify_draft(redivis, log_path)

    tables = list(a.tables)
    if a.from_file:
        tables += [ln.strip() for ln in open(a.from_file) if ln.strip()]
    if not tables:
        p.error("give table names, or --from-file")

    shards = {r["table"]: r["shard"] for r in csv.DictReader(open(src_root / WORKLIST))}
    off = [t for t in tables if t not in shards]
    if off:
        p.error(f"not on the #2029 worklist: {off}")

    idx = shard_index(redivis, src_root / "irw_validate/results/.shard_index.json")
    done = ({json.loads(ln)["table"] for ln in log_path.open()}
            if log_path.exists() else set())

    failures = 0
    with log_path.open("a") as log:
        for i, t in enumerate(tables, 1):
            if t in done:
                print(f"[{i}/{len(tables)}] {t} (done)")
                continue
            try:
                rec = repair(redivis, idx, shards, t, out_dir)
            except Exception as exc:
                rec = {"table": t, "shard": shards[t], "error": str(exc)[:300]}
            failures += not (rec.get("ok") or rec.get("skip"))
            log.write(json.dumps(rec, default=str) + "\n")
            log.flush()
            pr = rec.get("probes", {})
            summary = " ".join(
                f"{c}:{v.get('n_na')}NA->{v.get('target')}" for c, v in pr.items())
            print(f"[{i}/{len(tables)}] {t} {summary} ok={rec.get('ok')} "
                  f"{rec.get('skip', '')}{'; '.join(rec.get('problems', []))}"
                  f"{rec.get('error', '')[:90]}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
