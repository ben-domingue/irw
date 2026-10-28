#!/usr/bin/env python3
"""Respondent uniqueness on published quasi-identifiers -- k=1, #3273.

    python3 metadata/20_k1.py                  # the whole corpus
    python3 metadata/20_k1.py --per-run 400    # a rotation slice, stalest first
    python3 metadata/20_k1.py --tables a,b     # named tables only
    python3 metadata/20_k1.py --dry-run        # print the plan, query nothing

What this writes
----------------
    k1_by_table.csv   one row per core table: which quasi-identifiers it
                      publishes, how many cells they cut it into, and the share
                      of respondents alone in their cell
    metadata.csv      two columns joined on from the above: k1_prop,
                      n_quasi_identifiers

What k=1 is, and is not (#3232)
-------------------------------
Group a table's respondents by the `cov_*` quasi-identifiers it publishes and
count distinct `id` per cell. k=1 is the share of respondents alone in their
cell -- nobody else in the table shares their exact combination of age, sex,
region, education and the rest.

It is a necessary condition for re-identification, not re-identification, and
in a small sample it is mostly arithmetic: the corpus median is 41.2% under 100
respondents and 0.3% above 10,000. #3232 ruled on what IRW does about it --
nothing, beyond never publishing a covariate at finer granularity than its
source -- because every at-risk table comes from a public deposit publishing
the same demographics, so coarsening IRW's copy diverges from the source and
protects nobody. This stage exists because that position was asserted rather
than checkable: a user selecting a table could not see that eight demographics
on 3,000 people leaves nearly all of them unique.

The quasi-identifier set is NOT to be rewritten
-----------------------------------------------
QI below is copied verbatim from `oneoff/k-anonymity-3232/run_k1.py`, the
2026-10-28 measurement #3232 was decided on. A new regex makes the numbers
incomparable with that baseline, which is the only thing a reimplementation can
be checked against. The baseline, for exactly that purpose: p25 3.1%, median
18.9%, p75 54.5%, p90 86.8%; `friedman_2018_risks_discrimination` 100.0% on 12
quasi-identifiers, and 41.0% (1,276 of 3,110) on the five columns #3232's own
table names, which is the cheapest single-table check.

This stage reproduces all 2,942 of that run's rows exactly, and both friedman
figures. Two of the four percentiles #3273 quotes are stale, though: p25 3.1%
and median 18.9% hold, but the real p75 is 54.9% and p90 88.1%. The quoted
54.5% and 86.8% were computed before the date/timestamp arm was added and were
not recomputed when `k1_by_table.csv` was regenerated with it -- the CSV in that
directory is post-widening (friedman sits at 12 quasi-identifiers and 100% in
it), which is why the upper tail moved and the median did not.

It selects attributes a person is identifiable by in combination -- age/birth,
gender, race, income, education, geography at every grain, nationality,
religion, household, occupation, politics, language, health, orientation, body
measures, and date/timestamp columns, a survey start time being close to a
unique key. Not condition, study, group, sample, or anything experimental.
The date and timestamp arm was added on 2026-10-28, after the run: it is why
friedman was first reported at 99.2% and is really 100%, and 12 core tables
carry such a column. So this stage does not reproduce `k1_by_table.csv` in that
directory row for row on those 12. That is the regex being right.

Every table, every run
----------------------
A published table's quasi-identifier values do not change except when the table
is corrected, so a rotation would spend most of its time recomputing numbers
that cannot have moved. The argument for computing once and recomputing on a
`metadata/table_changes.csv` row is real, and it was considered (#3273); what
decided against it is that its own audit clause costs most of what it saves.
Catching a table whose data moved without a `table_changes.csv` row needs 400
tables of queries a run plus the code to compare them against what is stored --
versus 4,921 tables and no comparison code at all, because under unconditional
recompute a k=1 value that changed IS the finding, and the pipeline already
snapshots every stage's CSVs and diffs them. Corpus-wide every run, rather than
400 at a time, which is twelve runs for a sweep. Same conclusion stage 19
reached on its own costs, and for the same reason: a rotation defends a budget
that does not need defending, at the price of a five-week staleness front.
`--per-run` is kept as the escape hatch if a future corpus makes that false.

Which is also why `k1_by_table.csv` is committed, unlike stage 19's store, and
why it carries no per-row timestamp. 6,720 rows of mostly-unchanging values is
a review surface: the diff is empty unless a table's data moved. A
`computed_at` column would rewrite every row on every run and drown exactly the
signal the file is kept for. When it ran is the pipeline log's business, and
git's.

Cost
----
One server-side `GROUP BY` per table, batched with `UNION ALL`, four batches at
a time; nothing is downloaded but five integers per table, so this costs
nothing against the 200 GB export cap. The 2026-10-28 full pass did 2,942
tables in ~15 minutes (~0.3 s/table). 1,799 of the 6,720 core tables publish no
quasi-identifier at all and are not queried -- with no columns to group by every
respondent sits in one cell, so k=1 is 0 by arithmetic (1 only if the table has
a single respondent). That leaves 4,921 queried, measured at 466 s for the full
corpus on 2026-10-28 (~0.09 s/table, a third of what the oneoff run cost per
table, which batched 30 serially rather than four batches at a time).

Caveats that ship with the numbers
----------------------------------
* `people` is respondents summed over cells, so it exceeds `n_participants`
  where one `id` appears with two different covariate values -- a person whose
  `cov_age` moves between waves is counted in both cells. That gap is itself
  worth looking at; it is not an error in the count.
* A table with one quasi-identifier can still show a high rate if that column
  is near-unique on its own, which is what the date/timestamp arm catches.
* k=1 describes the table as published, not the deposit. A source that
  published finer demographics than IRW carries is the more identifying object,
  and #3232's rule is that IRW may never be the finer of the two.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
METADATA = HERE / "metadata.csv"
CONFIG = HERE / "redivis_config.R"
K1_CSV = HERE / "k1_by_table.csv"

K1_FIELDS = ["table", "n_qi", "qi", "n_participants", "cells", "people",
             "k1_n", "k1_prop", "klt5_prop", "status"]
SUMMARY_FIELDS = ["k1_prop", "n_quasi_identifiers"]

PER_RUN = 0          # 0 means every table; --per-run N caps it, --per-run -1 skips
MAX_TABLES_PER_BATCH = 30
MAX_RESP_PER_BATCH = 60_000_000
WORKERS = 4
MAX_SECONDS = 2400
RETRIES = 6

# Copied verbatim from oneoff/k-anonymity-3232/run_k1.py. Do not rewrite it --
# see the module docstring. The date/timestamp arm is the 2026-10-28 widening.
QI = re.compile(r'^cov_('
  r'age|age_.*|.*_age|birth.*|dob|'
  r'gender|sex|male|female|'
  r'race|ethnic.*|hispanic|'
  r'income|salary|wage|ses|'
  r'educ.*|degree|school|university|grade|major|gpa|'
  r'country|state|region|residence|location|city|zip.*|postal.*|province|county|municipal.*|urban.*|'
  r'nationality|immigra.*|born.*|'
  r'religio.*|'
  r'marital.*|relationship_status|children|household.*|family_size|'
  r'occupation|employ.*|job|profession|work.*|'
  r'party|ideolog.*|politic.*|vote.*|'
  r'language|'
  r'disab.*|health.*|diagnos.*|'
  r'orientation|sexual.*|lgbt.*|'
  r'date|datetime|timestamp|startdate|enddate|starttime|endtime|'
  r'assess_date|recordeddate|time|sduration|'
  r'height|weight|bmi'
  r')$')


def owner() -> str:
    """IRW_OWNER out of redivis_config.R -- the one place the account is named."""
    m = re.search(r'IRW_OWNER\s*<-\s*"([^"]+)"', CONFIG.read_text())
    if not m:
        sys.exit(f"error: no IRW_OWNER in {CONFIG}")
    return m.group(1)


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    """CRLF and minimal quoting, as canonicalize_csv.py leaves a file, so a
    standalone run produces the same bytes the pipeline would."""
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\r\n",
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def num(s, default=None):
    try:
        v = float(s)
    except (TypeError, ValueError):
        return default
    return default if math.isnan(v) else v


def fmt(v, digits=6):
    """Fixed notation, trailing zeros trimmed, blank for missing. Never
    scientific: metadata.csv published enem row counts at two significant
    digits for months because R's write.csv chose whichever form was shorter."""
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return ""
    if isinstance(v, int) or (isinstance(v, float) and v.is_integer() and abs(v) < 1e15):
        return str(int(v))
    return f"{v:.{digits}f}".rstrip("0").rstrip(".")


def qi_columns(row: dict) -> list[str]:
    """The quasi-identifiers a table publishes, from metadata.csv's `variables`.

    `variables` is pipe-separated with spaces ("id| item| cov_age"), so split on
    either separator and strip -- the same parse run_k1.py used to arrive at
    2,942 tables with three or more, which this reproduces exactly."""
    raw = row.get("variables") or ""
    cols = [c.strip() for c in re.split(r'[|,]', raw) if c.strip()]
    return sorted({c for c in cols if QI.match(c)})


def k1_sql(owner_name: str, dataset: str, table: str, qi: list[str]) -> str:
    """Cells, respondents, and respondents alone or near-alone, in one pass.

    `id` is deliberately NOT cast to STRING here, unlike stage 19: that cast is
    needed for PARTITION BY on a FLOAT64 id, there is no window function here,
    and the 2026-10-28 baseline was measured without it on 2,942 tables with no
    failures. Casting would be a silent change to a published number.

    SUM(IF(c=1,c,0)) over cell sizes is the count of respondents in cells of
    one, since such a cell contributes exactly its single occupant."""
    ref = f"`{owner_name}.{dataset}.{table}`"
    group = ", ".join(f"`{c}`" for c in qi)
    return (
        f"SELECT '{table}' AS tbl, COUNT(*) AS cells, SUM(c) AS people, "
        f"SUM(IF(c=1,c,0)) AS k1, SUM(IF(c<5,c,0)) AS klt5 FROM "
        f"(SELECT COUNT(DISTINCT id) AS c FROM {ref} GROUP BY {group})"
    )


def summarise(row: dict | None) -> dict:
    """The two metadata.csv columns, from one table's k1_by_table.csv row.

    Blank rather than 0 when undefined -- no row yet, or a table whose query
    returned no respondents. A 0 there would read as a measured finding
    (nobody is unique) instead of an absent one."""
    if not row or not row.get("status"):
        return {"k1_prop": "", "n_quasi_identifiers": ""}
    return {"k1_prop": row.get("k1_prop", ""),
            "n_quasi_identifiers": row.get("n_qi", "")}


def no_qi_row(t: dict) -> dict:
    """A table publishing no quasi-identifier, by arithmetic rather than query.

    With nothing to group by every respondent is in one cell, so none of them is
    alone in it -- unless the table has a single respondent, who then is. These
    are the 1,799 tables #3273 asked be carried anyway: they sit at zero, and
    that is informative."""
    n = t["_n_participants"]
    alone = 1 if n == 1 else 0
    return {"table": t["table"], "n_qi": "0", "qi": "",
            "n_participants": fmt(n), "cells": "1" if n else "0",
            "people": fmt(n), "k1_n": fmt(alone),
            "k1_prop": fmt(alone / n, 4) if n else "",
            "klt5_prop": fmt(1.0 if n and n < 5 else 0.0, 4) if n else "",
            "status": "no_qi"}


def plan_batches(todo: list[dict]) -> list[list[dict]]:
    """Greedy packing under the table-count and response caps. Tables arrive in
    rotation order and stay in it, so an interrupted run resumes where the
    rotation left off rather than in the middle of it."""
    batches, cur, resp = [], [], 0.0
    for t in todo:
        r = t["_n_responses"] or 0
        if cur and (len(cur) >= MAX_TABLES_PER_BATCH or resp + r > MAX_RESP_PER_BATCH):
            batches.append(cur)
            cur, resp = [], 0.0
        cur.append(t)
        resp += r
    if cur:
        batches.append(cur)
    return batches


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--per-run", type=int, default=PER_RUN,
                    help="tables to query this run (default 0 = all of them; "
                         "a positive N takes the N most-stale, -1 skips the pass "
                         "and only rewrites the derived files)")
    ap.add_argument("--tables", default="",
                    help="comma-separated table names; ignores the rotation")
    ap.add_argument("--max-seconds", type=int, default=MAX_SECONDS,
                    help=f"stop starting new work after this many seconds (default {MAX_SECONDS})")
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--dry-run", action="store_true",
                    help="print the rotation slice and the batch plan, query nothing")
    args = ap.parse_args()

    meta = read_csv(METADATA)
    if not meta:
        sys.exit(f"error: no usable {METADATA}")
    stored = {r["table"]: r for r in read_csv(K1_CSV)}

    for r in meta:
        r["_n_responses"] = num(r.get("n_responses"), 0.0)
        r["_n_participants"] = num(r.get("n_participants"), 0.0)
        r["_qi"] = qi_columns(r)

    with_qi = [r for r in meta if r["_qi"]]
    print(f"base: {len(meta)} tables in metadata.csv; {len(with_qi)} publish a "
          f"quasi-identifier ({len(meta) - len(with_qi)} do not and are not queried); "
          f"{len(stored)} stored")

    if args.tables:
        wanted = [t.strip() for t in args.tables.split(",") if t.strip()]
        by_name = {r["table"]: r for r in meta}
        missing = [t for t in wanted if t not in by_name]
        if missing:
            sys.exit(f"error: not in metadata.csv: {', '.join(missing)}")
        todo = [by_name[t] for t in wanted if by_name[t]["_qi"]]
        skipped = [t for t in wanted if not by_name[t]["_qi"]]
        if skipped:
            print(f"  {len(skipped)} named table(s) publish no quasi-identifier: "
                  f"{', '.join(skipped[:10])}")
    elif args.per_run < 0:
        print("per-run is negative; skipping the query pass, rewriting outputs only")
        todo = []
    else:
        # Rotation, used only under --per-run: stale first (n_participants moved
        # since the stored row, so that row describes data that has changed),
        # then never computed, then the rest.
        def key(r):
            st = stored.get(r["table"])
            if st is None:
                return (1, "")
            if num(st.get("n_participants")) != r["_n_participants"]:
                return (0, "")
            return (2, "")
        todo = sorted(with_qi, key=lambda r: (key(r), r["table"].lower()))
        if args.per_run:
            todo = todo[:args.per_run]
        kinds = [key(r)[0] for r in todo]
        print(f"queueing {len(todo)} of {len(with_qi)} queryable table(s) "
              f"({kinds.count(0)} stale, {kinds.count(1)} never computed, "
              f"{kinds.count(2)} already current)")

    batches = plan_batches(todo)
    if batches:
        print(f"plan: {len(batches)} batch(es), "
              f"{min(len(b) for b in batches)}-{max(len(b) for b in batches)} tables each, "
              f"{args.workers} at a time")
    if args.dry_run:
        for i, b in enumerate(batches[:5], 1):
            print(f"  batch {i}: {len(b)} tables, "
                  f"{int(sum(t['_n_responses'] for t in b)):,} responses -- "
                  f"{', '.join(t['table'] for t in b[:4])}"
                  f"{' ...' if len(b) > 4 else ''}")
        if len(batches) > 5:
            print(f"  ... and {len(batches) - 5} more")
        return 0

    failures: list[tuple[str, str]] = []

    if batches:
        tok = Path("~/.redivis_api_token").expanduser()
        if "REDIVIS_API_TOKEN" not in os.environ and tok.exists():
            os.environ["REDIVIS_API_TOKEN"] = tok.read_text().strip()
        import redivis
        own = owner()

        def run(sql):
            for attempt in range(RETRIES):
                try:
                    return redivis.query(sql).to_pandas_dataframe()
                except Exception as exc:  # noqa: BLE001
                    if "429" in str(exc) and attempt < RETRIES - 1:
                        time.sleep(15)
                        continue
                    raise

        def one(batch):
            sql = "\nUNION ALL\n".join(
                k1_sql(own, t["dataset"], t["table"], t["_qi"]) for t in batch)
            try:
                return run(sql).to_dict("records"), []
            except Exception:  # noqa: BLE001 -- one bad table must not cost the batch
                rows, bad = [], []
                for t in batch:
                    try:
                        rows += run(k1_sql(own, t["dataset"], t["table"],
                                           t["_qi"])).to_dict("records")
                    except Exception as exc:  # noqa: BLE001
                        bad.append((t["table"], f"{type(exc).__name__}: {exc}"[:200]))
                return rows, bad

        t0 = time.time()
        done: set[str] = set()
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for w in range(0, len(batches), args.workers):
                elapsed = time.time() - t0
                if elapsed > args.max_seconds:
                    left = sum(len(b) for b in batches[w:])
                    print(f"  budget: {int(elapsed)}s spent, "
                          f"{left} table(s) left for the next run")
                    break
                wave = batches[w:w + args.workers]
                for batch, (rows, bad) in zip(wave, pool.map(one, wave)):
                    failures += bad
                    got = {r["tbl"]: r for r in rows}
                    for t in batch:
                        rec = got.get(t["table"])
                        if rec is None:
                            continue
                        people = num(rec["people"], 0.0) or 0.0
                        k1 = num(rec["k1"], 0.0) or 0.0
                        klt5 = num(rec["klt5"], 0.0) or 0.0
                        stored[t["table"]] = {
                            "table": t["table"],
                            "n_qi": str(len(t["_qi"])),
                            "qi": "|".join(t["_qi"]),
                            "n_participants": fmt(t["_n_participants"]),
                            "cells": fmt(num(rec["cells"])),
                            "people": fmt(people),
                            "k1_n": fmt(k1),
                            "k1_prop": fmt(k1 / people, 4) if people else "",
                            "klt5_prop": fmt(klt5 / people, 4) if people else "",
                            "status": "ok" if people else "no_respondents",
                        }
                        done.add(t["table"])
                print(f"  {min(w + args.workers, len(batches))}/{len(batches)} batches  "
                      f"{int(time.time() - t0)}s  {len(done)} tables", flush=True)
        print(f"queried {len(done)} table(s) in {int(time.time() - t0)}s")
        if failures:
            print(f"  ! {len(failures)} table(s) failed and keep their previous row:")
            for t, err in failures[:20]:
                print(f"    {t}: {err}")

    # The no-QI tables, every run: they cost nothing and #3273 asked for them.
    for t in meta:
        if not t["_qi"]:
            stored[t["table"]] = no_qi_row(t)

    # A table that has left the corpus keeps no row. The queue reads
    # metadata.csv, so an orphan would never be revisited and would sit here
    # forever, with a k=1 for data that is no longer published.
    live = {r["table"] for r in meta}
    gone = sorted(set(stored) - live)
    if gone:
        print(f"dropping {len(gone)} table(s) no longer in metadata.csv: "
              f"{', '.join(gone[:20])}{' ...' if len(gone) > 20 else ''}")
        for t in gone:
            stored.pop(t, None)

    write_csv(K1_CSV, K1_FIELDS, [stored[t] for t in sorted(stored, key=str.lower)])
    rates = sorted(v for v in (num(r.get("k1_prop")) for r in stored.values())
                   if v is not None)
    print(f"wrote {K1_CSV.name}: {len(stored)} row(s)")
    if rates:
        def pct(p):
            return rates[min(len(rates) - 1, int(p * len(rates)))]
        print(f"  k=1 across the corpus: p25 {100 * pct(.25):.1f}%  "
              f"median {100 * pct(.50):.1f}%  p75 {100 * pct(.75):.1f}%  "
              f"p90 {100 * pct(.90):.1f}%")

    # The two summary columns, re-joined from the store on every run.
    # 01_metadata.R rebuilds metadata.csv from base.cols and drops anything
    # else, so they have to be re-joined rather than carried -- which also keeps
    # the store, not metadata.csv, as the single source.
    n_filled = 0
    for r in meta:
        r.update(summarise(stored.get(r["table"])))
        if r["k1_prop"] != "":
            n_filled += 1
    fields = [f for f in meta[0] if not f.startswith("_") and f not in SUMMARY_FIELDS]
    write_csv(METADATA, fields + SUMMARY_FIELDS, meta)
    print(f"metadata.csv: {n_filled} of {len(meta)} row(s) carry k1_prop "
          f"({100 * n_filled / len(meta):.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
