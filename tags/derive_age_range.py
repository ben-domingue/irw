"""Derive `age range` and `child age` from each table's own cov_age (#1760).

Rule A of tags/decisions/1760_age_range_and_sample.md, decided 2026-09-01:
the tag describes the table as shipped, so where the table carries usable ages
the tag is computed rather than judged, and the computed value outranks a human
tag for these two columns only (03_tags.R::apply_derived_tags).

Nothing is fetched. Every figure is a Redivis-side aggregate -- one UNION ALL
query per batch of tables -- so this reads 2,363 tables without downloading one.

Outputs, all under tags/:
  age_range_derived.csv   what 03_tags.R consumes; only tables passing the guards
  age_range_audit.csv     every table considered, with its numbers and verdict
  age_range_quarantine.csv tables held back for a human look, with the reason

Usage:  python tags/derive_age_range.py [--limit N] [--batch 25]
"""
import argparse
import csv
import datetime
import os
import sys
import time

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
METADATA = os.path.join(SRC, "metadata", "metadata.csv")

MIN_RESPONDENTS = 30      # non-missing ages required before we trust the column
AGE_FLOOR, AGE_CEIL = 0, 120
BAND_MAX_DISTINCT, BAND_MAX_VALUE = 6, 10   # the cov_age_band shape
MINOR_SHARE = 0.02        # decision 2

VOCAB_ADULT = "Adult (18+)"
VOCAB_CHILD = "Child (<18y)"
VOCAB_MIXED = "Mixed"
VOCAB_ELDER = "Elderly (minimum age >50)"

DERIVED_COLS = ["table", "age range", "child age (for child-focused studies)",
                "basis", "min_age", "max_age", "n_age", "share_under_18",
                "generated"]

# Tables whose age UNIT has been confirmed against the source, releasing them
# from the months quarantine. The quarantine exists because nothing in the data
# distinguishes years from months where the two would give different tags; a
# human reading the source can, and this file is where that reading is recorded
# with its evidence rather than applied silently. Only `years` is honoured --
# a table confirmed as months needs its data fixed, not its tag derived.
UNIT_FILE = os.path.join(HERE, "age_unit_confirmed.csv")


def confirmed_years():
    if not os.path.exists(UNIT_FILE):
        return set()
    d = pd.read_csv(UNIT_FILE)
    return {str(t).strip().lower()
            for t, u in zip(d["table"], d["unit"]) if str(u).strip() == "years"}


def aggregate_sql(dataset, table):
    """One row of table-level age facts, computed Redivis-side.

    Everything is per RESPONDENT, not per response row: a table with 90 items
    would otherwise weight its ages by item count. SAFE_CAST is what makes a
    non-numeric cov_age register as missing instead of erroring the batch.
    """
    age = "SAFE_CAST(cov_age AS FLOAT64)"
    return f"""SELECT '{table}' AS tbl,
 COUNT(DISTINCT id) AS n_id,
 COUNT(DISTINCT IF({age} IS NOT NULL, id, NULL)) AS n_age,
 COUNT(DISTINCT IF({age} < 18, id, NULL)) AS n_u18,
 COUNT(DISTINCT IF({age} >= 18, id, NULL)) AS n_a18,
 MIN({age}) AS min_age,
 MAX({age}) AS max_age,
 COUNT(DISTINCT {age}) AS n_distinct,
 COUNT(DISTINCT IF({age} < 6, id, NULL)) AS n_lt6,
 COUNT(DISTINCT IF({age} >= 6 AND {age} < 12, id, NULL)) AS n_6_12,
 COUNT(DISTINCT IF({age} >= 12 AND {age} < 18, id, NULL)) AS n_12_18
FROM `datapages.{dataset}.{table}`"""


YEARS_OK = set()   # populated in main()/emit() from age_unit_confirmed.csv


def classify(r):
    """Returns (age_range, child_age, verdict, reason).

    verdict is one of derived / unusable / quarantine. `Non-human` is never
    derived here -- it comes from the source and is left to the tagger.
    """
    n_age = int(r.n_age or 0)
    if n_age < MIN_RESPONDENTS:
        return None, None, "unusable", f"only {n_age} respondents with an age"
    lo, hi = r.min_age, r.max_age
    if pd.isna(lo) or pd.isna(hi):
        return None, None, "unusable", "no numeric ages"
    if lo < AGE_FLOOR or hi > AGE_CEIL:
        return None, None, "unusable", f"ages outside [{AGE_FLOOR}, {AGE_CEIL}]: {lo}-{hi}"
    if int(r.n_distinct) < BAND_MAX_DISTINCT and hi < BAND_MAX_VALUE:
        return None, None, "unusable", (
            f"looks like banded codes: {int(r.n_distinct)} distinct values, max {hi}")

    # A wider band signature the strict test above misses: a column that starts
    # at 1 (or 0) and covers a small contiguous range is a category code, not an
    # age. alsyouf_2024_* runs 1-7 with exactly 7 distinct values and would
    # otherwise have derived `Child (<18y)` for what is almost certainly an
    # adult sample in age brackets. Starting point matters: a real 6-12 primary
    # school study also has ~7 distinct values, but it does not start at 1.
    if lo <= 1 and hi <= 12 and int(r.n_distinct) <= hi:
        return None, None, "quarantine", (
            f"starts at {lo} and covers {int(r.n_distinct)} values up to {hi}: "
            "the shape of a band code, not an age")

    # Months, not years, would read as a plausible age in years and derive a
    # confidently wrong tag -- an infant study coded 12-36 months would come out
    # `Mixed`. Nothing in the data distinguishes the two units, so this shape is
    # held for a human rather than guessed at either way.
    #
    # Only where the unit CHANGES the tag, though. At a maximum of 18 the table
    # is `Child (<18y)` whether those are years or months, so there is nothing
    # to hold: 91 of the 104 tables this first quarantined were of that shape.
    if 18 < hi <= 36 and lo <= 6 and str(r.tbl).strip().lower() not in YEARS_OK:
        return None, None, "quarantine", (
            f"ages {lo}-{hi} are equally consistent with months, and the unit "
            "changes the tag; not stated in the data")

    u18, a18 = int(r.n_u18), int(r.n_a18)
    known = u18 + a18
    if known == 0:
        return None, None, "unusable", "no respondent on either side of 18"
    smaller = min(u18, a18)
    share = smaller / known

    if lo > 50:
        tag = VOCAB_ELDER
    elif u18 and a18 and share >= MINOR_SHARE:
        tag = VOCAB_MIXED
    elif u18 > a18:
        # Below the floor the table takes the MAJORITY side, which is the whole
        # point of a tolerance. Falling through to Adult regardless would have
        # tagged benitezsillero_2021_bullying (ages 12-20, 98% under 18)
        # `Adult (18+)` -- caught by the dry run, 2026-09-01.
        tag = VOCAB_CHILD
    else:
        tag = VOCAB_ADULT

    child = ""
    if tag in (VOCAB_CHILD, VOCAB_MIXED):
        bands = []
        for n, label in ((r.n_lt6, "Early (<6y)"), (r.n_6_12, "Child (6-12y)"),
                         (r.n_12_18, "Adolescent (12-18y)")):
            n = int(n or 0)
            if n and (u18 == 0 or n / max(u18, 1) >= MINOR_SHARE):
                bands.append(label)
        child = ", ".join(bands)

    reason = ""
    if u18 and a18 and share < MINOR_SHARE:
        reason = (f"both sides of 18 present but the smaller group is "
                  f"{share:.3%} (< {MINOR_SHARE:.0%}), so not Mixed")
    return tag, child, "derived", reason


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--batch", type=int, default=25)
    ap.add_argument("--from-audit", action="store_true",
                    help="reclassify age_range_audit.csv instead of re-querying "
                         "Redivis -- the aggregates are the expensive half and "
                         "they do not change when a classification rule does")
    args = ap.parse_args()

    global YEARS_OK
    YEARS_OK = confirmed_years()

    if args.from_audit:
        prev = pd.read_csv(os.path.join(HERE, "age_range_audit.csv"))
        prev = prev.rename(columns={"table": "tbl"})
        emit(prev)
        return

    os.environ.setdefault(
        "REDIVIS_API_TOKEN",
        open(os.path.expanduser("~/.redivis_api_token")).read().strip())
    import redivis

    meta = pd.read_csv(METADATA)
    # Exact token, never a substring: `variables` is pipe-separated, and
    # cov_age_band / cov_age_group / cov_age_range / cov_age_months are
    # DIFFERENT columns -- banded codes or another unit. A substring match pulls
    # 179 such tables in and then asks Redivis for a cov_age they do not have.
    def has_cov_age(v):
        return "cov_age" in [x.strip().lower() for x in str(v).split("|")]

    have = meta[meta["variables"].fillna("").apply(has_cov_age)]
    have = have[["table", "dataset"]].reset_index(drop=True)
    if args.limit:
        have = have.head(args.limit)
    print(f"{len(have)} live tables carry a cov_age column", flush=True)

    rows, failed = [], []
    t0 = time.time()
    for start in range(0, len(have), args.batch):
        chunk = have.iloc[start:start + args.batch]
        sql = "\nUNION ALL\n".join(
            aggregate_sql(r.dataset, r.table) for r in chunk.itertuples())
        try:
            df = redivis.query(sql).to_pandas_dataframe()
            rows.append(df)
        except Exception as exc:                      # noqa: BLE001
            # One bad table must not cost the batch: retry singly so the rest land.
            print(f"  batch {start}: {type(exc).__name__}; retrying singly", flush=True)
            for r in chunk.itertuples():
                try:
                    rows.append(redivis.query(aggregate_sql(r.dataset, r.table))
                                .to_pandas_dataframe())
                except Exception as exc2:             # noqa: BLE001
                    failed.append({"table": r.table, "dataset": r.dataset,
                                   "error": f"{type(exc2).__name__}: {exc2}"[:300]})
        done = min(start + args.batch, len(have))
        print(f"  {done}/{len(have)}  {round(time.time() - t0)}s", flush=True)

    agg = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    agg = agg.astype({c: "float64" for c in
                      ("min_age", "max_age") if c in agg.columns}, errors="ignore")

    emit(agg, failed)


def emit(agg, failed=()):
    stamp = datetime.date.today().isoformat()
    audit, derived, quarantine = [], [], []
    for r in agg.itertuples():
        tag, child, verdict, reason = classify(r)
        share = (min(int(r.n_u18), int(r.n_a18)) / (int(r.n_u18) + int(r.n_a18))
                 if (int(r.n_u18) + int(r.n_a18)) else float("nan"))
        rec = {"table": r.tbl, "n_id": int(r.n_id), "n_age": int(r.n_age),
               "min_age": r.min_age, "max_age": r.max_age,
               "n_distinct": int(r.n_distinct), "n_u18": int(r.n_u18),
               "n_a18": int(r.n_a18), "share_under_18": round(share, 6) if share == share else "",
               "n_lt6": int(r.n_lt6), "n_6_12": int(r.n_6_12), "n_12_18": int(r.n_12_18),
               "verdict": verdict, "age range": tag or "", "child age": child or "",
               "reason": reason}
        audit.append(rec)
        if verdict == "derived":
            derived.append({"table": r.tbl, "age range": tag,
                            "child age (for child-focused studies)": child,
                            "basis": "derived_cov_age",
                            "min_age": r.min_age, "max_age": r.max_age,
                            "n_age": int(r.n_age),
                            "share_under_18": round(share, 6) if share == share else "",
                            "generated": stamp})
        elif verdict == "quarantine":
            quarantine.append(rec)

    def write(path, records, cols=None):
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols or list(records[0]))
            w.writeheader()
            w.writerows(records)
        print(f"wrote {len(records):>5} rows -> {path}")

    if audit:
        write(os.path.join(HERE, "age_range_audit.csv"), audit)
    if derived:
        write(os.path.join(HERE, "age_range_derived.csv"), derived, DERIVED_COLS)
    if quarantine:
        write(os.path.join(HERE, "age_range_quarantine.csv"), quarantine)
    if failed:
        write(os.path.join(HERE, "age_range_failed.csv"), failed)
        print(f"{len(failed)} table(s) could not be queried", file=sys.stderr)


if __name__ == "__main__":
    main()
