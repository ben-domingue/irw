"""Withdraw two c19prc response tables serving wrong data from item_response_warehouse_4 (irw#2542).

Found by item-text rounds batch_718 and batch_728 (irw#2382 slice 18), which blocked both rather than write
item text. Ben 2026-09-29: withdraw now, rebuild and re-upload later.

  c19prc_uk_mcbride_2021_socialdistance               W5 inserts a new item at position 8 but the build maps W5 by
                                                     number, so SocialDistance8-14 and 18 mix two statements.
  c19prc_uk_mcbride_2021_lockdown_contact_behaviours  W6 dropped two of W5's nine items and renumbered; pooled by
                                                     number, so Risk_Behaviours_5-7 mix different behaviours.

KEEP: the deposit's other 70 c19prc tables stay in the shard. No item text exists for the targets (both were
blocked), so nothing in the irw_text shards is touched.

Dry run by default. Set APPLY=1 to delete.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_wrongnow_2026_09_29")
import redivis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import record

OWNER   = "datapages"                  # metadata/redivis_config.R
DATASET = "item_response_warehouse_4"
TARGETS = {"c19prc_uk_mcbride_2021_socialdistance", "c19prc_uk_mcbride_2021_lockdown_contact_behaviours"}
PREFIX  = "c19prc_uk_mcbride_2021_"
N_KEEP  = 70                           # the deposit's other tables, all of which must survive

apply = os.environ.get("APPLY") == "1"


def names(ds_name, version):
    return {t.name for t in redivis.organization(OWNER).dataset(ds_name, version=version).list_tables(max_results=2000)}


current = names(DATASET, "current")
if TARGETS - current:
    sys.exit(f"ABORT: not in {DATASET} current: {sorted(TARGETS - current)}")
KEEP = {n for n in current if n.startswith(PREFIX)} - TARGETS
if len(KEEP) != N_KEEP:
    sys.exit(f"ABORT: expected {N_KEEP} sibling c19prc tables in current, found {len(KEEP)}")

if not apply:
    try:
        before = names(DATASET, "next")
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

after = names(DATASET, "next")
removed = before - after
assert removed == TARGETS, f"MISMATCH: removed={sorted(removed)}"
assert KEEP <= after, f"went missing: {sorted(KEEP - after)}"
record(TARGETS, dataset=DATASET, reason="wrong_data", refs="#2382 #2542",
       note="W5/W6 items pooled by number; codes mix different questions across waves", script=__file__)
print(f"OK: removed exactly {sorted(TARGETS)} from {DATASET}; {len(KEEP)} c19prc siblings intact. "
      "Draft must be RELEASED to take effect.")
