"""Retire foundationalassist_worden_2026: the source is licensed CC BY-NC 4.0 (irw#2401).

Source: Worden, Heffernan, Heffernan & Sonkar (2026), FoundationalASSIST, arXiv:2602.00070;
data at https://huggingface.co/datasets/ASSISTments/FoundationalASSIST (gated). Built by
data/foundationalassist_worden_2026.R.

IRW's dictionary recorded the licence as Custom / CC BY 4.0. The dataset card declares
`cc-by-nc-4.0`. Ben confirmed the card on 2026-09-30, and a non-commercial licence is not
open under IRW's rules (CLAUDE.md, "License must be explicitly and verifiably open").
Ruled: withdraw (audit/2401/RULES.md, "Decisions, round 3"). The audit had found the table
while triaging exact-duplicate rows (audit/2401/triage/dup_exact.csv); that question is moot
once it is withdrawn.

Target: item_response_warehouse_4, foundationalassist_worden_2026 (1,712,991 rows, v10_0).
It has no item text in irw_text, irw_text_2 or irw_text_3 (checked 2026-09-30), so nothing
else leaves with it.

The itemtext/withdrawals.csv row was written by hand with `released` blank, so do NOT
call ledger.record() when applying. Other pending withdrawals in the same draft (ledger
rows with `released` blank) are allowed to be missing from it; see retire_jiang_2024.py,
whose first run aborted without that allowance.

Published table: the deletion takes effect at the NEXT release; Ben publishes. Dry run
by default; APPLY=1 deletes from the draft.
"""
import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("retire_foundationalassist")
import redivis

OWNER = "datapages"  # metadata/redivis_config.R
DATASET = "item_response_warehouse_4"
TARGET = "foundationalassist_worden_2026"
EXPECTED_ROWS = 1712991  # measured 2026-09-30, v10_0
OTHER = ("item_response_warehouse", "item_response_warehouse_2", "item_response_warehouse_3",
         "item_response_warehouse_5", "item_response_warehouse_6")

apply = os.environ.get("APPLY") == "1"

_ledger = Path(__file__).resolve().parents[2] / "itemtext" / "withdrawals.csv"
with open(_ledger, newline="", encoding="utf-8") as fh:
    PENDING = {r["table"] for r in csv.DictReader(fh)
               if r["dataset"] == DATASET and not r["released"].strip()}


def names(dataset, version):
    return {t.name for t in redivis.organization(OWNER).dataset(dataset, version=version)
            .list_tables(max_results=5000)}


def n_rows(version):
    q = f"SELECT COUNT(*) AS n FROM `{OWNER}.{DATASET}:{version}.{TARGET}`"
    return int(redivis.query(q).to_pandas_dataframe()["n"].iloc[0])


def open_draft():
    d = redivis.organization(OWNER).dataset(DATASET)
    d.get()
    d.properties.setdefault("nextVersion", None)
    d.create_next_version(if_not_exists=True)
    return redivis.organization(OWNER).dataset(DATASET, version="next")


# ---- scope checks, against `current`, before anything is touched -----------------------
current = names(DATASET, "current")
if TARGET not in current:
    sys.exit(f"ABORT: {TARGET} is not published in {DATASET}")
n = n_rows("current")
if n != EXPECTED_ROWS:
    sys.exit(f"ABORT: {TARGET} has {n:,} rows, expected {EXPECTED_ROWS:,}; re-measure first")
for other in OTHER:
    try:
        if TARGET in names(other, "current"):
            sys.exit(f"ABORT: {TARGET} also lives in {other}; scope is wrong")
    except Exception as exc:  # a shard that does not exist is not a clash
        print(f"  (skipped {other}: {type(exc).__name__})")
print(f"{DATASET}: {len(current)} published; {TARGET} live with {n:,} rows")

if not apply:
    try:
        draft = names(DATASET, "next")
        print(f"DRY RUN: draft open, {len(draft)} tables (current {len(current)}); "
              f"target in draft: {TARGET in draft}")
    except Exception as exc:
        print(f"DRY RUN: no draft open ({type(exc).__name__}); APPLY=1 creates one")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

# ---- apply ------------------------------------------------------------------------------
keep = current - {TARGET}
draft = open_draft()
before = {t.name for t in draft.list_tables(max_results=5000)}
if TARGET not in before:
    sys.exit(f"Nothing to do: {TARGET} is already gone from the {DATASET} draft")
missing = keep - before - PENDING
if missing:
    sys.exit(f"ABORT: draft is missing published tables: {sorted(missing)[:5]}")
draft.table(TARGET).delete()
print(f"deleted from {DATASET} draft: {TARGET}")
after = names(DATASET, "next")
assert before - after == {TARGET}, f"MISMATCH: removed={sorted(before - after)}"
assert keep - PENDING <= after, f"went missing: {sorted(keep - after)}"
print(f"OK: exactly {TARGET} removed; {len(after)} left in the draft. The draft must be "
      "RELEASED to take effect. Ledger row already exists; do not call ledger.record().")
