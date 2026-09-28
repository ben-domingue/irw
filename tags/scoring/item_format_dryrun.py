#!/usr/bin/env python3
"""Dry run: can `item format` be DERIVED from the response data? (irw#1837 b)

    python3 tags/scoring/item_format_dryrun.py --fetch      # query Redivis, cache, report
    python3 tags/scoring/item_format_dryrun.py              # report from the cache

WRITES NOTHING outside tags/scoring/. No Sheet write (there is no write path,
#1708), nothing staged to tags_auto.csv. The derivation is not authorised by
any ruling; this measures whether it would deserve one.

#1837 proposed `item format` as class 1 (derivable from the table's own
contents) and asked for a dry run first: how many tables a derivation would
fill, and how often it disagrees with an existing tag. #1838 measured a
threshold on `n_categories` alone and found it no better than always answering
the majority class. This run gives the data a fairer chance by reading the
response values themselves, Redivis-side:

    Slider/continuous               any non-integer `resp`, or > 11 distinct values
    Likert Scale/selected response  integer `resp` with <= 11 distinct values
    (abstain)                       no numeric `resp`

`Constructed Response` and `Mixed` have no rule, because nothing in `resp`
separates them: a constructed response is usually scored 0/1, which reads
exactly like a selected-response item. That the rule cannot produce two of
the four values is itself part of the answer.

The comparison is split by WHO wrote the existing tag -- the Sheet (a human)
or tags_auto.csv (the tagger) -- because they are different yardsticks, and
the published tags.csv cannot tell them apart.

Outputs, beside this file:
    item_format_resp_stats.csv          per-table aggregates (the cache)
    results_item_format_dryrun_<date>.txt  the report
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import os
import random
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1]
METADATA = SRC / "metadata" / "metadata.csv"
AUTO = SRC / "tags" / "tags_auto.csv"
CACHE = HERE / "item_format_resp_stats.csv"
SHEET_URL = ("https://docs.google.com/spreadsheets/d/"
             "1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g/export?format=csv"
             "&gid=126134123")
COL = "Item format"
LIKERT = "Likert Scale/selected response"
SLIDER = "Slider/continuous"
MAX_SELECTED = 11      # a 0-10 scale is the widest selected-response format in use
BATCH = 25
OWNER = "datapages"


def blank(v):
    v = (v or "").strip()
    return v == "" or v == "NA"


def agg_sql(dataset, table):
    r = "SAFE_CAST(resp AS FLOAT64)"
    return (f"SELECT '{table}' AS tbl, COUNT(*) AS n_rows, COUNT({r}) AS n_num, "
            f"COUNT(DISTINCT {r}) AS n_distinct, "
            f"COUNTIF({r} IS NOT NULL AND {r} != TRUNC({r})) AS n_nonint, "
            f"MIN({r}) AS min_resp, MAX({r}) AS max_resp "
            f"FROM `{OWNER}.{dataset}.{table}`")


def fetch(tables):
    tok = Path("~/.redivis_api_token").expanduser()
    if "REDIVIS_API_TOKEN" not in os.environ and tok.exists():
        os.environ["REDIVIS_API_TOKEN"] = tok.read_text().strip()
    import redivis

    def run(sql):
        for attempt in range(6):
            try:
                return redivis.query(sql).to_pandas_dataframe()
            except Exception as exc:  # noqa: BLE001
                if "429" in str(exc) and attempt < 5:
                    time.sleep(15)
                    continue
                raise

    chunks = [tables[i:i + BATCH] for i in range(0, len(tables), BATCH)]
    rows, failed = [], []

    def one(chunk):
        try:
            return run("\nUNION ALL\n".join(agg_sql(d, t) for t, d in chunk)), []
        except Exception:  # noqa: BLE001 -- one bad table must not cost the batch
            got, bad = [], []
            for t, d in chunk:
                try:
                    got.append(run(agg_sql(d, t)))
                except Exception as exc:  # noqa: BLE001
                    bad.append((t, f"{type(exc).__name__}: {exc}"[:200]))
            import pandas as pd
            return (pd.concat(got) if got else None), bad

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=4) as pool:   # Redivis 429s above ~4
        for i, (df, bad) in enumerate(pool.map(one, chunks), 1):
            if df is not None:
                rows += df.to_dict("records")
            failed += bad
            if i % 20 == 0:
                print(f"  {i}/{len(chunks)} batches  {round(time.time() - t0)}s",
                      flush=True)
    with CACHE.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["tbl", "n_rows", "n_num", "n_distinct",
                                           "n_nonint", "min_resp", "max_resp"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return failed


def derive(s):
    if int(float(s["n_num"] or 0)) == 0:
        return None, "no numeric resp"
    nd, nonint = int(float(s["n_distinct"])), int(float(s["n_nonint"]))
    if nonint > 0:
        return SLIDER, f"{nonint} non-integer values"
    if nd > MAX_SELECTED:
        return SLIDER, f"{nd} distinct integer values"
    return LIKERT, f"{nd} distinct integer values"


def load_sheet(path):
    if path:
        text = Path(path).read_text(encoding="utf-8")
    else:
        with urllib.request.urlopen(SHEET_URL, timeout=120) as r:
            text = r.read().decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(text)))[1:]   # row 1 is instructions
    out = {}
    for r in rows:
        k = (r.get("table") or "").strip().lower()
        if k and not blank(r.get(COL)):
            out.setdefault(k, r[COL].strip())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--sheet", help="local copy of the Sheet CSV export")
    ap.add_argument("--seed", type=int, default=1837)
    args = ap.parse_args()

    meta = list(csv.DictReader(METADATA.open(encoding="utf-8")))
    live = {r["table"].lower(): (r["table"], r["dataset"]) for r in meta}
    failed = []
    if args.fetch:
        print(f"querying {len(live)} live tables", flush=True)
        failed = fetch(sorted(live.values()))
    stats = {r["tbl"].lower(): r for r in csv.DictReader(CACHE.open(encoding="utf-8"))}

    sheet = load_sheet(args.sheet)
    auto = {}
    for r in csv.DictReader(AUTO.open(encoding="utf-8")):
        if not blank(r.get(COL)):
            auto[r["table"].strip().lower()] = r[COL].strip()

    recs = []
    for k, (name, ds) in sorted(live.items()):
        if k not in stats:
            continue
        pred, why = derive(stats[k])
        human, tagger = sheet.get(k), auto.get(k)
        # Which tag is published: the Sheet wins its cell (#1723/#1863).
        current, source = (human, "sheet") if human else (
            (tagger, "auto") if tagger else (None, ""))
        recs.append(dict(table=name, dataset=ds, pred=pred, why=why,
                         current=current, source=source))

    L = []
    p = L.append
    today = dt.date.today().isoformat()
    p(f"item format derivation -- DRY RUN, {today} (irw#1837 b). Nothing written.")
    p(f"live tables {len(live)}; with resp aggregates {len(recs)}; "
      f"query failures {len(failed)}")
    p(f"rule: non-integer resp or >{MAX_SELECTED} distinct -> {SLIDER}; "
      f"else integer -> {LIKERT}; no numeric resp -> abstain")
    p("")
    derived = [r for r in recs if r["pred"]]
    p(f"derivation commits on {len(derived)} tables, abstains on "
      f"{len(recs) - len(derived)}")
    p(f"  by derived class: " + ", ".join(
        f"{v} {n}" for v, n in Counter(r['pred'] for r in derived).most_common()))
    p("")

    fills = [r for r in derived if not r["current"]]
    p(f"WOULD FILL (no item format anywhere today): {len(fills)}")
    for v, n in Counter(r["pred"] for r in fills).most_common():
        p(f"  {v:<34}{n:>5}")
    p("")

    for src, label in (("sheet", "HAND TAGS (Sheet)"), ("auto", "TAGGER (tags_auto.csv)")):
        rs = [r for r in derived if r["source"] == src]
        agree = sum(r["pred"] == r["current"] for r in rs)
        base = Counter(r["current"] for r in rs).most_common(1)
        p(f"AGAINST {label}: {len(rs)} tables, agree {agree} "
          f"({100 * agree / max(len(rs), 1):.1f}%), disagree {len(rs) - agree}")
        if base:
            p(f"  majority-class baseline (always '{base[0][0]}'): "
              f"{100 * base[0][1] / len(rs):.1f}%")
        p(f"  per existing class       n   derived=Likert  derived=Slider   agree")
        by = defaultdict(Counter)
        for r in rs:
            by[r["current"]][r["pred"]] += 1
        for cur, c in sorted(by.items(), key=lambda x: -sum(x[1].values())):
            n = sum(c.values())
            p(f"  {cur[:22]:<22}{n:>5}{c[LIKERT]:>16}{c[SLIDER]:>16}"
              f"{100 * c[cur] / n:>8.1f}%")
        p("")

    rnd = random.Random(args.seed)
    dis = [r for r in derived if r["current"] and r["pred"] != r["current"]]
    p(f"SAMPLE -- 12 disagreements of {len(dis)} (seed {args.seed}):")
    for r in sorted(rnd.sample(dis, min(12, len(dis))), key=lambda r: r["table"].lower()):
        p(f"  {r['table']:<46} {r['source']:<5} tag={r['current']!r:<34} "
          f"derived={r['pred']!r} ({r['why']})")
    p("")
    p(f"SAMPLE -- 12 would-fill tables of {len(fills)}:")
    for r in sorted(rnd.sample(fills, min(12, len(fills))), key=lambda r: r["table"].lower()):
        p(f"  {r['table']:<46} derived={r['pred']!r} ({r['why']})")
    if failed:
        p("")
        p("query failures:")
        for t, e in failed:
            p(f"  {t}: {e}")

    out = HERE / f"results_item_format_dryrun_{today}.txt"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
