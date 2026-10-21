#!/usr/bin/env python3
"""Per-item classical statistics for every core table -- roadmap item 8, tier 0.

    python3 metadata/19_item_classical.py                 # one rotation slice
    python3 metadata/19_item_classical.py --per-run 40    # a smaller slice
    python3 metadata/19_item_classical.py --tables a,b    # named tables only
    python3 metadata/19_item_classical.py --dry-run       # print the plan, query nothing

What this writes
----------------
    item_classical.csv         one row per (table, item): n, mean, sd, n_levels,
                               item_rest_r, min_resp, max_resp
    item_classical_stamps.csv  one row per table: when it was computed, under
                               what n_responses, and with what outcome
    metadata.csv               three summary columns joined on from the above:
                               difficulty_spread, mean_item_rest_r, prop_items_extreme

Why it exists (#1710)
---------------------
metadata.csv carries structural columns only -- n_responses, n_categories,
n_items, density -- so the catalogue cannot be filtered by any psychometric
property. "Tables with a usable difficulty spread and no floor effects" is not
an askable question today. These columns make it askable.

Tier 0 is deliberately model-free. Ben's objection to the original item 8 was
that IRT is a choice: a network or factor-analytic perspective derives
different item quantities from the same data, and publishing only 2PL
parameters takes a side in a live dispute. Nothing here is estimated, nothing
converges, and nothing assumes a latent variable -- which is also why it is
defined for all 6,651 tables rather than the 710 dichotomous ones. Tier 1 (the
polychoric matrix) and tier 2 (fits, plural) stay specified and unbuilt; the
first-eigenvalue ratio was moved out of tier 0 on measurement, because it is
the one column that forces a long->wide pivot -- infeasible above ~2,000 items,
and needing an item cap and a Pearson/polychoric ruling it does not have.

One query per table, server-side, no export
-------------------------------------------
Redivis caps *data export* at 200 GB per rolling 30 days account-wide, and one
pass over the corpus comes close to that on its own. Queries are not subject to
that cap, so every statistic here is computed by Redivis and only the per-item
result set comes back -- a few hundred rows for a typical table. Nothing is
downloaded and nothing counts against the quota, exactly as the row-count
fallback in 01_metadata.R does.

The rest score needs no self-join and no wide matrix: one window partition over
`id` gives each response its person total, rest = total - resp, and a single
grouped pass gives all seven statistics. That is O(np), which is why the sparse
item banks nothing fit-based can reach (neurips_2020 at 27,613 items) cost the
same here as a dense 10-item scale.

Batching is where the budget comes from
---------------------------------------
Most of a per-table query's 4-11 s is fixed startup, not work on the data, so
400 tables run one at a time would cost ~55 minutes -- and the 2026-10-19 run
left only 71 minutes of headroom under the 240-minute job timeout. Tables are
therefore stacked into one query with UNION ALL, the way the item-distribution
sweep did 897 tables in ~36 queries, and the batches run four at a time
(Redivis starts 429ing above that). A batch that errors is retried table by
table, so one bad table costs its own row and not the other 24.

Three caps keep a batch from being the thing that breaks: table count, summed
n_responses, and summed n_items (which bounds the result set). MAX_SECONDS is
the backstop -- no new wave starts past it, and the remaining tables simply
wait for the next run, because the rotation is designed to be interrupted.

Every table, every run -- which was not the plan
------------------------------------------------
This was designed to fill over a rotation, 400 tables a run on the Mon/Wed/Fri
cadence, ~5 weeks for a sweep. That was sized on the rolling refresh in
01_metadata.R, which costs ~10.3 s/table. Measured, this costs ~0.14 s/table:
the whole corpus is 6,651 tables and 1,125,820 items in 947 s, no failures.
A rotation defends a budget that does not need defending, at the price of
columns that disagree with each other across a five-week front, so the default
is to recompute everything. --per-run is kept as the escape hatch if a future
corpus makes that false, and it still orders by staleness when used: tables
whose n_responses has moved since their stamp first, then never-computed, then
oldest first.

The cost that does bind is a 78 MB per-item file, which is why what the repo
keeps is item_classical_stamps.csv (one row per table, 380 KB) and the four
metadata.csv columns, not the store itself. See the .gitignore block.

Caveats that ship with the numbers
----------------------------------
* `item_rest_r` is defined everywhere but is not the same quantity everywhere.
  Where a respondent sees 20 of 160,786 items the rest score is nearly disjoint
  across respondents; 59 tables sit under 0.1 density.
* Response direction is not harmonised in IRW. ffm_AGR item_1 comes back at
  item_rest_r = -0.20 because it is reverse-keyed. These columns describe the
  data as stored, not a scored scale. That is why metadata.csv carries BOTH
  `mean_item_rest_r` and `mean_abs_item_rest_r`: ffm_AGR's five positive and
  five reverse-keyed items average to 0.0075, which reads as a scale whose
  items are unrelated, while the absolute mean is 0.208. The signed column is
  the honest description of the stored data; the absolute one is the column a
  "do these items hang together" filter wants. A wide gap between the two is
  itself a reverse-keying detector.
* On a table with `wave` or `rater`, `id` repeats across waves, so the person
  total pools them. The statistic is still well defined; it is just not a
  within-wave quantity.
* Non-numeric responses are dropped by SAFE_CAST, so a table whose `resp` is
  categorical text yields no rows and is stamped `no_numeric_resp`.
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
ITEM_CSV = HERE / "item_classical.csv"
STAMPS_CSV = HERE / "item_classical_stamps.csv"

ITEM_FIELDS = ["table", "item", "n", "mean", "sd", "n_levels", "item_rest_r",
               "min_resp", "max_resp"]
STAMP_FIELDS = ["table", "computed_at", "n_items", "n_responses", "status"]
SUMMARY_FIELDS = ["difficulty_spread", "mean_item_rest_r", "mean_abs_item_rest_r",
                  "prop_items_extreme"]

PER_RUN = 0          # 0 means every table; --per-run N caps it, --per-run -1 skips
MAX_TABLES_PER_BATCH = 25
MAX_RESP_PER_BATCH = 60_000_000
MAX_ITEMS_PER_BATCH = 40_000
WORKERS = 4
MAX_SECONDS = 2400
RETRIES = 6

# An item mean within 5% of either end of the table's observed response range
# counts as floor or ceiling. For a dichotomous table that is p < .05 or p > .95.
EXTREME = 0.05


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
    """Write in the canonical form: CRLF, minimal quoting, as canonicalize_csv.py
    leaves a file. Writing it that way here means a standalone run produces the
    same bytes the pipeline would, instead of a whole-file line-ending diff."""
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
    scientific: metadata.csv published enem row counts at two significant digits
    for months because R's write.csv chose whichever form was shorter."""
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return ""
    if isinstance(v, int) or (isinstance(v, float) and v.is_integer() and abs(v) < 1e15):
        return str(int(v))
    return f"{v:.{digits}f}".rstrip("0").rstrip(".")


def agg_sql(owner_name: str, dataset: str, table: str) -> str:
    """All seven per-item statistics in one grouped pass.

    The window gives each response its person total without a self-join. `rest`
    is NULL when a person answered a single item, because total - resp is then
    a constant 0 and would distort the correlation -- CORR drops NULL pairs, so
    n/mean/sd/n_levels still see every response while item_rest_r does not."""
    ref = f"`{owner_name}.{dataset}.{table}`"
    return (
        f"SELECT '{table}' AS tbl, item, COUNT(*) AS n, AVG(resp) AS mean, "
        f"STDDEV_SAMP(resp) AS sd, COUNT(DISTINCT resp) AS n_levels, "
        f"CORR(resp, rest) AS item_rest_r, MIN(resp) AS min_resp, MAX(resp) AS max_resp "
        f"FROM (SELECT item, resp, "
        f"IF(COUNT(*) OVER (PARTITION BY id) > 1, "
        f"SUM(resp) OVER (PARTITION BY id) - resp, NULL) AS rest "
        f"FROM (SELECT CAST(id AS STRING) AS id, CAST(item AS STRING) AS item, "
        f"SAFE_CAST(resp AS FLOAT64) AS resp FROM {ref}) "
        f"WHERE resp IS NOT NULL AND id IS NOT NULL) "
        f"GROUP BY item"
    )


def summarise(rs: list[dict]) -> dict:
    """The metadata.csv columns, from one table's per-item rows.

    `difficulty_spread` is normalised by the table's observed response range so
    it means the same thing on a 0/1 test and a 1-5 Likert scale: the share of
    the range the item means cover. On a dichotomous table it is exactly the
    p-range. Without that normalisation the column could not be filtered on
    across a corpus that is five-sixths polytomous.

    `prop_items_extreme` uses the same range: an item whose mean sits within 5%
    of either end is at floor or ceiling.

    Every column is blank rather than 0 when it is undefined -- no rows yet
    (the rotation has not reached this table), or a table whose responses are
    all one value, where a "spread" of 0 would read as a measured finding
    instead of an absent one."""
    means = [v for v in (num(x["mean"]) for x in rs) if v is not None]
    los = [v for v in (num(x["min_resp"]) for x in rs) if v is not None]
    his = [v for v in (num(x["max_resp"]) for x in rs) if v is not None]
    rr = [v for v in (num(x["item_rest_r"]) for x in rs) if v is not None]
    spread = extreme = rbar = rabs = None
    if means and los and his and max(his) > min(los):
        lo, hi = min(los), max(his)
        spread = (max(means) - min(means)) / (hi - lo)
        cut = EXTREME * (hi - lo)
        extreme = sum(1 for m in means if m - lo < cut or hi - m < cut) / len(means)
    if rr:
        rbar = sum(rr) / len(rr)
        rabs = sum(abs(v) for v in rr) / len(rr)
    return {"difficulty_spread": fmt(spread, 4),
            "mean_item_rest_r": fmt(rbar, 4),
            "mean_abs_item_rest_r": fmt(rabs, 4),
            "prop_items_extreme": fmt(extreme, 4)}


def plan_batches(todo: list[dict]) -> list[list[dict]]:
    """Greedy packing under all three caps. Tables arrive in rotation order and
    stay in it: a batch is a contiguous run, so an interrupted run resumes where
    the rotation left off rather than somewhere in the middle of it."""
    batches, cur, resp, items = [], [], 0.0, 0.0
    for t in todo:
        r, i = t["_n_responses"] or 0, t["_n_items"] or 0
        if cur and (len(cur) >= MAX_TABLES_PER_BATCH
                    or resp + r > MAX_RESP_PER_BATCH
                    or items + i > MAX_ITEMS_PER_BATCH):
            batches.append(cur)
            cur, resp, items = [], 0.0, 0.0
        cur.append(t)
        resp += r
        items += i
    if cur:
        batches.append(cur)
    return batches


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--per-run", type=int, default=PER_RUN,
                    help="tables to compute this run (default 0 = all of them; "
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
    stamps = {r["table"]: r for r in read_csv(STAMPS_CSV)}
    items_by_table: dict[str, list[dict]] = {}
    for r in read_csv(ITEM_CSV):
        items_by_table.setdefault(r["table"], []).append(r)
    print(f"base: {len(meta)} tables in metadata.csv; "
          f"{len(items_by_table)} with per-item rows ({sum(len(v) for v in items_by_table.values())} items); "
          f"{len(stamps)} stamped")

    for r in meta:
        r["_n_responses"] = num(r.get("n_responses"), 0.0)
        r["_n_items"] = num(r.get("n_items"), 0.0)

    if args.tables:
        wanted = [t.strip() for t in args.tables.split(",") if t.strip()]
        by_name = {r["table"]: r for r in meta}
        missing = [t for t in wanted if t not in by_name]
        if missing:
            sys.exit(f"error: not in metadata.csv: {', '.join(missing)}")
        todo = [by_name[t] for t in wanted]
    elif args.per_run < 0:
        print("per-run is negative; skipping the compute pass, rewriting outputs only")
        todo = []
    else:
        # Rotation: stale first (n_responses moved since the stamp, so the rows
        # on disk are wrong), then never computed, then oldest computed.
        def key(r):
            st = stamps.get(r["table"])
            if st is None:
                return (1, "")                      # never computed
            if num(st.get("n_responses")) != r["_n_responses"]:
                return (0, st.get("computed_at", ""))   # stale: data moved
            return (2, st.get("computed_at", ""))
        todo = sorted(meta, key=lambda r: key(r) + (r["table"].lower(),))
        if args.per_run:
            todo = todo[:args.per_run]
        kinds = [key(r)[0] for r in todo]
        print(f"rotation: {len(todo)} of {len(meta)} table(s) this run "
              f"({kinds.count(0)} stale, {kinds.count(1)} never computed, "
              f"{kinds.count(2)} oldest-first)")

    batches = plan_batches(todo)
    if batches:
        print(f"plan: {len(batches)} batch(es), "
              f"{min(len(b) for b in batches)}-{max(len(b) for b in batches)} tables each, "
              f"{args.workers} at a time")
    if args.dry_run:
        for i, b in enumerate(batches[:5], 1):
            print(f"  batch {i}: {len(b)} tables, "
                  f"{int(sum(t['_n_responses'] for t in b)):,} responses, "
                  f"{int(sum(t['_n_items'] for t in b)):,} items -- "
                  f"{', '.join(t['table'] for t in b[:4])}"
                  f"{' ...' if len(b) > 4 else ''}")
        if len(batches) > 5:
            print(f"  ... and {len(batches) - 5} more")
        return 0

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
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
                agg_sql(own, t["dataset"], t["table"]) for t in batch)
            try:
                return run(sql).to_dict("records"), []
            except Exception:  # noqa: BLE001 -- one bad table must not cost the batch
                rows, bad = [], []
                for t in batch:
                    try:
                        rows += run(agg_sql(own, t["dataset"], t["table"])).to_dict("records")
                    except Exception as exc:  # noqa: BLE001
                        bad.append((t["table"], f"{type(exc).__name__}: {exc}"[:200]))
                return rows, bad

        t0 = time.time()
        done_tables: set[str] = set()
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
                    got: dict[str, list[dict]] = {}
                    for r in rows:
                        got.setdefault(r["tbl"], []).append(r)
                    for t in batch:
                        name = t["table"]
                        if name in dict(bad):
                            continue
                        done_tables.add(name)
                        rs = got.get(name, [])
                        items_by_table[name] = [{
                            "table": name,
                            "item": str(r["item"]),
                            "n": fmt(num(r["n"])),
                            "mean": fmt(num(r["mean"])),
                            "sd": fmt(num(r["sd"])),
                            "n_levels": fmt(num(r["n_levels"])),
                            "item_rest_r": fmt(num(r["item_rest_r"])),
                            "min_resp": fmt(num(r["min_resp"])),
                            "max_resp": fmt(num(r["max_resp"])),
                        } for r in rs]
                        stamps[name] = {
                            "table": name,
                            "computed_at": now,
                            "n_items": str(len(rs)),
                            "n_responses": fmt(t["_n_responses"]),
                            "status": "ok" if rs else "no_numeric_resp",
                        }
                print(f"  {min(w + args.workers, len(batches))}/{len(batches)} batches  "
                      f"{int(time.time() - t0)}s  {len(done_tables)} tables", flush=True)
        print(f"computed {len(done_tables)} table(s) in {int(time.time() - t0)}s")
        if failures:
            print(f"  ! {len(failures)} table(s) failed and keep their previous rows:")
            for t, err in failures[:20]:
                print(f"    {t}: {err}")

    # Tables that have left the corpus keep neither rows nor a stamp -- the
    # rotation reads metadata.csv, so an orphan would never be revisited and
    # would sit in item_classical.csv forever.
    live = {r["table"] for r in meta}
    gone = sorted((set(items_by_table) | set(stamps)) - live)
    if gone:
        print(f"dropping {len(gone)} table(s) no longer in metadata.csv: "
              f"{', '.join(gone[:20])}{' ...' if len(gone) > 20 else ''}")
        for t in gone:
            items_by_table.pop(t, None)
            stamps.pop(t, None)

    rows = [r for t in sorted(items_by_table, key=str.lower) for r in
            sorted(items_by_table[t], key=lambda r: r["item"].lower())]
    write_csv(ITEM_CSV, ITEM_FIELDS, rows)
    write_csv(STAMPS_CSV, STAMP_FIELDS,
              [stamps[t] for t in sorted(stamps, key=str.lower)])
    print(f"wrote {ITEM_CSV.name}: {len(rows)} item row(s) over {len(items_by_table)} table(s)")

    # The three summary columns, recomputed from the whole per-item store on
    # every run. 01_metadata.R rebuilds metadata.csv from base.cols and drops
    # anything else, so these have to be re-joined each time rather than carried
    # -- which also means the store, not metadata.csv, is the single source.
    n_filled = 0
    for r in meta:
        rs = items_by_table.get(r["table"], [])
        r.update(summarise(rs))
        if rs:
            n_filled += 1
    fields = [f for f in meta[0] if not f.startswith("_") and f not in SUMMARY_FIELDS]
    write_csv(METADATA, fields + SUMMARY_FIELDS, meta)
    print(f"metadata.csv: {n_filled} of {len(meta)} row(s) carry tier-0 columns "
          f"({100 * n_filled / len(meta):.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
