"""Withdraw the 13 mexico_2023_mobility_* tables (ESRU-EMOVI 2023) from item_response_warehouse_5 (irw#1528).

No licence: CEEY's EMOVI page and its aviso de privacidad state no terms for reuse or redistribution; the data are
free to download, which is not a grant to re-share. The dictionary carried Derived License "Custom" with no terms
behind it. Ben 2026-09-29: pull them while Samuel asks CEEY for permission; re-upload from data/mexico_2023_mobility.do
if it is granted.

KEEP: nothing else in the shard shares the prefix. No item text exists for these tables, so no irw_text shard is
touched.

Dry run by default. Set APPLY=1 to delete.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_mexico_2023_mobility_1528")
import redivis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import record

OWNER   = "datapages"                  # metadata/redivis_config.R
DATASET = "item_response_warehouse_5"
PREFIX  = "mexico_2023_mobility_"
TARGETS = {PREFIX + s for s in ("anxiety", "appliances", "articles", "assets", "community", "finances", "mood",
                                "necessities", "neighborhood", "rooms", "services", "spaces", "utilities")}

apply = os.environ.get("APPLY") == "1"


def names(ds_name, version):
    return {t.name for t in redivis.organization(OWNER).dataset(ds_name, version=version).list_tables(max_results=2000)}


current = names(DATASET, "current")
found = {n for n in current if n.startswith(PREFIX)}
if found != TARGETS:
    sys.exit(f"ABORT: {PREFIX}* in {DATASET} current differs from TARGETS: "
             f"missing {sorted(TARGETS - found)}, extra {sorted(found - TARGETS)}")
KEEP = current - TARGETS

if not apply:
    try:
        before = names(DATASET, "next")
        print(f"DRY RUN: draft open, {len(before)} tables (current {len(current)}); "
              f"targets present: {len(TARGETS & before)}/13; keep missing: {sorted(KEEP - before)}; "
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

after = names(DATASET, "next")
removed = before - after
assert removed == TARGETS, f"MISMATCH: removed={sorted(removed)}"
assert KEEP <= after, f"went missing: {sorted(KEEP - after)}"
record(TARGETS, dataset=DATASET, reason="unlicensed", refs="#1528",
       note="ESRU-EMOVI 2023: CEEY states no reuse/redistribution terms; permission requested", script=__file__)
print(f"OK: removed exactly the 13 {PREFIX}* tables from {DATASET}; {len(KEEP)} other tables intact. "
      "Draft must be RELEASED to take effect.")
