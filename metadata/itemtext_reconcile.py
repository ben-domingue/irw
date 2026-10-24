#!/usr/bin/env python3
"""Reconcile `itemtext_metadata.csv` against what exists (review R-27, #3224).

WHY
---
`itemtext_metadata` is append-only: it gains a row when a table's item text is
ingested and loses one never. The review found 200 of 2,921 rows (6.8%)
describing item text that cannot be retrieved, and 83 item-text tables with no
joinable base table -- but its two independent reviews decomposed the 200
differently (191 withdrawn / 182 rights, versus 154 live-response / 14
withdrawn / 8 renamed), and the disagreement is itself the finding: nothing
reconciles this table against what exists.

This is that reconciliation, in one place, against the live catalog. Every row
lands in exactly one bucket, so the buckets sum to 2,921 and a later count can
be compared with this one.

WHAT EACH BUCKET MEANS

  ok                  item text live, base response table live -- the row
                      describes something a user can fetch and join
  text_withdrawn      the `__items` table is in `itemtext/withdrawals.csv`;
                      the row describes text that was deliberately retired,
                      which is the half `check_release_consistency.py`'s
                      `withdrawals-records` check already reports
  text_missing        no live `__items` table and no ledger row -- the row
                      describes text nothing serves and nothing retired
  base_case_only      item text live, base response table live under a
                      DIFFERENT CASE -- `itemtext_metadata` says
                      `alsecypiamh_wu_2022_cps` and the table is
                      `ALSECYPIAMH_WU_2022_CPS`. R-27 counted these as orphans;
                      they are R-31 (295 mixed-case names against lowercase
                      records) seen from a third surface, and a
                      case-insensitive join fixes all of them at once
  base_renamed        item text live under the old name, base table renamed in
                      `table_changes.csv`; the join needs the new name
  base_missing        item text live, base response table gone under any
                      spelling -- R-27's "no joinable base table", once the
                      case and rename cases are taken out

USAGE (from src/metadata, read-only Redivis token)

  python3 itemtext_reconcile.py                  # the decomposition
  python3 itemtext_reconcile.py --list text_missing
  python3 itemtext_reconcile.py --csv out.csv    # one row per non-ok row
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "redivis_config.R"
SUFFIX = "__items"


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def r_vector(name: str) -> list[str]:
    m = re.search(name + r"\s*<-\s*c\((.*?)\)", CONFIG.read_text(), re.S)
    return re.findall(r'"([^"]+)"', m.group(1)) if m else []


def owner() -> str:
    m = re.search(r'IRW_OWNER\s*<-\s*"([^"]+)"', CONFIG.read_text())
    return m.group(1) if m else "datapages"


def live(datasets: list[str], account: str) -> set[str]:
    import redivis
    names: set[str] = set()
    for dataset in datasets:
        names |= {t.name for t in
                  redivis.organization(account).dataset(dataset).list_tables()}
    return names


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", dest="bucket", help="print the tables in one bucket")
    ap.add_argument("--csv", help="write one row per non-ok row")
    args = ap.parse_args(argv)

    account = owner()
    text_live = live(r_vector("IRW_TEXT_DATASETS"), account)
    #: Every family a base table can live in. Conjoint and rankings tables have
    #: no item text, but naming them costs one listing each and makes a
    #: `base_missing` verdict mean "nowhere", not "not in core".
    base_datasets = (r_vector("IRW_CORE_DATASETS")
                     + [d for d in re.findall(r'"([^"]+)"',
                        re.search(r"IRW_AUX_DATASETS\s*<-\s*c\((.*?)\)",
                                  CONFIG.read_text(), re.S).group(1))
                        if d != "irw_meta"]
                     + r_vector("IRW_CONJ_DATASETS") + r_vector("IRW_RANK_DATASETS"))
    base_live = live(base_datasets, account)
    #: Case-folded, because `itemtext_metadata.table` is lowercase while 295
    #: live names are mixed case: an exact join calls those tables orphans.
    base_fold = {n.lower(): n for n in base_live}

    ledger = {(r.get("table") or "").strip() for r in
              read_csv(HERE.parent / "itemtext" / "withdrawals.csv")}
    renamed = {(r.get("table") or "").strip(): (r.get("replaced_by") or "").strip()
               for r in read_csv(HERE / "table_changes.csv")
               if (r.get("replaced_by") or "").strip()}

    rows = read_csv(HERE / "itemtext_metadata.csv")
    buckets: dict[str, list[tuple[str, str]]] = {}
    for row in rows:
        table = row["table"]
        items = table + SUFFIX
        if items in text_live:
            if table in base_live:
                bucket, note = "ok", ""
            elif table.lower() in base_fold:
                bucket, note = "base_case_only", f"-> {base_fold[table.lower()]}"
            elif renamed.get(table) and renamed[table] in base_live:
                bucket, note = "base_renamed", f"-> {renamed[table]}"
            else:
                bucket, note = "base_missing", ""
        elif items in ledger:
            bucket, note = "text_withdrawn", "in itemtext/withdrawals.csv"
        else:
            bucket, note = "text_missing", ("base table live"
                                            if table.lower() in base_fold
                                            else "base table gone too")
        buckets.setdefault(bucket, []).append((table, note))

    total = len(rows)
    print(f"{total} rows in itemtext_metadata.csv, {len(text_live)} live item-text "
          f"tables, {len(base_live)} live base tables")
    for bucket in ("ok", "text_withdrawn", "text_missing", "base_case_only",
                   "base_renamed", "base_missing"):
        got = buckets.get(bucket, [])
        print(f"  {bucket:<16}{len(got):>6}  {100 * len(got) / total:5.1f}%")
        if bucket == "text_missing" and got:
            for note, n in Counter(n for _t, n in got).most_common():
                print(f"      {note:<24}{n:>6}")
    assert sum(len(v) for v in buckets.values()) == total

    if args.bucket:
        for table, note in sorted(buckets.get(args.bucket, [])):
            print(f"{table}\t{note}")
    if args.csv:
        with open(args.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["table", "bucket", "note"])
            for bucket, got in buckets.items():
                if bucket == "ok":
                    continue
                for table, note in sorted(got):
                    w.writerow([table, bucket, note])
        print(f"wrote {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
