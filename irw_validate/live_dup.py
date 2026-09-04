"""Measure `dup_id_item` against the LIVE corpus, one table at a time.

    python3 -m irw_validate.live_dup TABLE [TABLE ...] -o results/recheck.csv
    python3 -m irw_validate.live_dup --from-file tables.txt -o out.csv

Written for the #1835 follow-up and kept so a fix can be *proved*: re-run it on
a table after regenerating it and `excess_pair` should be 0 (or, where the
repeat is the design, `excess_occ` should be).

**Queries, never irw_fetch.** irw_fetch() exports the whole table, and the
account's Redivis export allowance is 200GB/30 days against a 181.8GB corpus --
one pass over everything spends ~91% of a month (#1736, and the note at the top
of itemtext/.claude/skills/irw-auto-itemtext/scripts/table_sets.R). Aggregate
queries are not capped, and every measure below is an aggregate. So this reads
nothing: it asks the server to count.

What one query per table returns:

    n_rows                    rows in the table
    excess_pair               rows beyond the first in each id+item group
    n_dup_pairs               id+item groups holding more than one row
    n_conflict_pairs          ... of those, how many hold >1 distinct resp
    excess_exact              excess rows byte-identical to a row already there
    excess_allbutresp         what survives grouping by EVERY column but resp
    excess_occ                what survives once the occasion columns are used

Reading them: `excess_occ == 0` means an occasion column explains the repeat and
there is nothing to fix. `excess_exact == excess_pair` means every excess row is
a duplicate and deduping is safe. `excess_allbutresp == 0` with only a
person-level column (group/study/treat) doing the separating means the opposite
of a repeated measure -- the same id denotes different people, and deduping
would destroy real responses. See results/README.md.

Same machine etiquette as sweep_legacy: one table at a time, `--resume` picks up
where a stopped run left off, and it is worth running under `nice -n 19`.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import sys
import warnings

# The gate profiles' occasion columns as of #1835. A column here describes WHEN
# or UNDER WHAT the measurement was taken. group/study/treatment are absent on
# purpose: they describe the person or the arm, and a person appearing twice
# under one is a question, not an answer.
OCCASION = ("wave", "timepoint", "date", "rater", "trialnum", "trial", "order",
            "session", "occasion", "period", "block", "subtest")

SHARDS = ["item_response_warehouse"] + [
    f"item_response_warehouse_{i}" for i in (2, 3, 4, 5, 6)]

FIELDS = ["table", "ref", "cols", "occ_cols", "n_rows", "n_pairs", "excess_pair",
          "n_dup_pairs", "n_conflict_pairs", "excess_allbutresp", "n_conflict_full",
          "excess_exact", "excess_occ", "error"]


def _authenticate(src_root: pathlib.Path):
    sys.path.insert(0, str(src_root))
    from irw_secrets import load_write_token
    load_write_token()
    import redivis
    warnings.filterwarnings("ignore", message="No reference id was provided.*")
    redivis.authenticate()
    return redivis


def shard_index(redivis, cache: pathlib.Path) -> dict:
    """table name -> qualified Redivis reference, over all six core shards.

    Six list_tables() calls for ~4,100 tables, cached to disk because the answer
    changes only when a table is added -- or when a version is released.

    **`version="current"` is not optional.** `dataset(name).list_tables()` with
    no version returned the *previous* release: after four shards were released
    on 2026-09-03 it still handed back `v46_0` refs, so a run meant to prove a
    fix measured the data from before the fix and reported every table
    unchanged. A verification tool that silently reads stale data is worse than
    none.

    The cache records the version tag it was built from and is discarded when
    the live tags move, so the same trap cannot be sprung by the cache either.
    """
    tags = {}
    for ds in SHARDS:
        try:
            props = redivis.organization("datapages").dataset(
                ds, version="current").get().properties
            tags[ds] = props.get("version", {}).get("tag")
        except Exception:
            tags[ds] = None
    if cache.exists():
        cached = json.loads(cache.read_text())
        if isinstance(cached, dict) and cached.get("_versions") == tags:
            return cached["index"]
    idx: dict[str, list[str]] = {}
    for ds in SHARDS:
        for t in redivis.organization("datapages").dataset(
                ds, version="current").list_tables():
            idx.setdefault(t.name, []).append(t.properties["qualifiedReference"])
    cache.write_text(json.dumps({"_versions": tags, "index": idx}))
    return idx


def _sql(ref: str, cols: list[str]) -> str:
    q = lambda c: f"`{c}`"                                    # noqa: E731
    key = "`id`,`item`"
    all_but_resp = ",".join(q(c) for c in cols if c != "resp")
    all_cols = ",".join(q(c) for c in cols)
    occ = [c for c in cols if c.lower() in OCCASION]
    occ_key = key + ("," + ",".join(q(c) for c in occ) if occ else "")
    # resp is compared as a string with an explicit NULL token: COUNT(DISTINCT)
    # skips NULLs, so without this a pair of {5, NULL} would look unanimous.
    r = "IFNULL(CAST(`resp` AS STRING),'<<NULL>>')"
    # CTEs are ga/gb/gc/go, not a/b/c/o: a CTE named `c` shadows the `c` column
    # in `WHERE c>1`, which BigQuery reports as a type error on `>`.
    return f"""
WITH ga AS (SELECT {key}, COUNT(*) c, COUNT(DISTINCT {r}) dr FROM `{ref}` GROUP BY {key}),
     gb AS (SELECT {all_but_resp}, COUNT(*) c, COUNT(DISTINCT {r}) dr FROM `{ref}` GROUP BY {all_but_resp}),
     gc AS (SELECT {all_cols}, COUNT(*) c FROM `{ref}` GROUP BY {all_cols}),
     go AS (SELECT {occ_key}, COUNT(*) c FROM `{ref}` GROUP BY {occ_key})
SELECT
 (SELECT COUNT(*) FROM `{ref}`) AS n_rows,
 (SELECT COUNT(*) FROM ga) AS n_pairs,
 (SELECT IFNULL(SUM(c-1),0) FROM ga WHERE c>1) AS excess_pair,
 (SELECT COUNT(*) FROM ga WHERE c>1) AS n_dup_pairs,
 (SELECT COUNT(*) FROM ga WHERE dr>1) AS n_conflict_pairs,
 (SELECT IFNULL(SUM(c-1),0) FROM gb WHERE c>1) AS excess_allbutresp,
 (SELECT COUNT(*) FROM gb WHERE dr>1) AS n_conflict_full,
 (SELECT IFNULL(SUM(c-1),0) FROM gc WHERE c>1) AS excess_exact,
 (SELECT IFNULL(SUM(c-1),0) FROM go WHERE c>1) AS excess_occ
"""


def measure(redivis, idx: dict, table: str) -> dict:
    rec = {"table": table, "error": ""}
    try:
        refs = idx.get(table)
        if not refs:
            rec["error"] = "not found in any core shard (renamed, or not published)"
            return rec
        ref = refs[0]
        tb = redivis.table(ref)
        cols = [v.properties["name"] for v in tb.list_variables()]
        rec["ref"] = ref
        rec["cols"] = "|".join(cols)
        rec["occ_cols"] = "|".join(c for c in cols if c.lower() in OCCASION)
        rec.update(redivis.query(_sql(ref, cols))
                   .to_arrow_table(progress=False).to_pylist()[0])
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
    redivis = _authenticate(src_root)
    idx = shard_index(redivis, pathlib.Path(a.out).parent / ".shard_index.json")

    done = set()
    if a.resume and os.path.exists(a.out):
        done = {r["table"] for r in csv.DictReader(open(a.out))}
    fresh = not os.path.exists(a.out) or not a.resume
    # Appended as each table finishes, not held to the end: a run that is
    # interrupted must still leave --resume something to resume from.
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
            print(f"[{i}/{len(tables)}] {t} rows={rec.get('n_rows')} "
                  f"excess_pair={rec.get('excess_pair')} exact={rec.get('excess_exact')} "
                  f"occ={rec.get('excess_occ')} {rec['error'][:60]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
