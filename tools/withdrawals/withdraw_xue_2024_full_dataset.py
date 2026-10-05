"""Withdraw xue_2024_full_dataset from item_response_warehouse_2 (irw#2506; Ben 2026-10-05: "drop").

Its 19 "items" are not administered items: each is a count (0-7) of how often a coded category appeared in a
respondent's free-text answers -- a content-analysis output, not item responses. 2,603 rows.

KEEP: xue_2024_study2_efa. (xue_2024_study3_cfa was withdrawn by withdraw_wrongnow_2026_10_05.py, #2837, and is
being rebuilt; it is not checked here.) No item text exists for the target.

Its ledger rows are committed with this script; APPLY=1 adds them only if they are missing.

Dry run by default. Set APPLY=1 to delete.
"""
import csv, os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_xue_2024_full_dataset")
import redivis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import LEDGER, record

OWNER   = "datapages"                  # metadata/redivis_config.R
DATASET = "item_response_warehouse_2"
TARGETS = {"xue_2024_full_dataset"}
KEEP    = {"xue_2024_study2_efa"}

apply = os.environ.get("APPLY") == "1"


def names(version):
    return {t.name for t in redivis.organization(OWNER).dataset(DATASET, version=version).list_tables(max_results=2000)}


current = names("current")
if TARGETS - current:
    sys.exit(f"ABORT: not in {DATASET} current: {sorted(TARGETS - current)}")
if KEEP - current:
    sys.exit(f"ABORT: sibling not in {DATASET} current: {sorted(KEEP - current)}")

if not apply:
    try:
        before = names("next")
        print(f"DRY RUN: draft open, {len(before)} tables (current {len(current)}); "
              f"targets present: {sorted(TARGETS & before)}; keep missing: {sorted(KEEP - before)}; "
              f"draft vs current names: +{sorted(before - current)} -{sorted(current - before)}")
    except Exception as exc:
        print(f"DRY RUN: no draft open ({type(exc).__name__}); APPLY=1 would create one.")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

ds = redivis.organization(OWNER).dataset(DATASET)
ds.create_next_version(if_not_exists=True)
draft = redivis.organization(OWNER).dataset(DATASET, version="next")
before = {t.name for t in draft.list_tables(max_results=2000)}
if TARGETS - before:
    sys.exit(f"ABORT: not in the {DATASET} draft: {sorted(TARGETS - before)}")
if KEEP - before:
    sys.exit(f"ABORT: keep set missing from draft: {sorted(KEEP - before)}")

for name in sorted(TARGETS):
    draft.table(name).delete()
    print("deleted:", name)

after = names("next")
removed = before - after
assert removed == TARGETS, f"MISMATCH: removed={sorted(removed)}"
assert KEEP <= after, f"went missing: {sorted(KEEP - after)}"
with LEDGER.open(newline="") as fh:
    logged = {r["table"] for r in csv.DictReader(fh) if r["script"].endswith(os.path.basename(__file__))}
if TARGETS - logged:
    record(TARGETS - logged, dataset=DATASET, reason="out_of_scope", refs="#2506", rows={"xue_2024_full_dataset": 2603},
           note="items are counts of coded free-text categories, not administered items", script=__file__)
print(f"OK: removed exactly {sorted(TARGETS)} from {DATASET}; sibling intact. Draft must be RELEASED to take effect.")
