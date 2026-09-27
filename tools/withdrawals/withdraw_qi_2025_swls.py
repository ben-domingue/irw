"""Withdraw qi_2025_swls__items: SWLS wording shipped after the SWLS block (irw#2479).

The register row (itemtext/instrument_rights_register.csv, family SWLS, verdict
block, Ben 2026-09-09) blocks Diener's Satisfaction With Life Scale wording. It names
qi_2025_swls as one of six QUEUED tables the block covers. The table was extracted
anyway, in batch_205 (#1945 rights line), uploaded 2026-09-18 to irw_text_2, and so
was missed by withdraw_swls.py, which had already run on 2026-09-09.

Item text only. The response table qi_2025_swls (item_response_warehouse_3) stays
live, and its item codes SWLS_1..SWLS_5 carry no wording. The same deposit's other
item-text tables (qi_2025_self_construal etc.) are not SWLS and are asserted to survive.

Whole-table withdrawal: all five items are SWLS items, read one by one
(itemtext/itemtables/batch_205/qi_2025_swls__items.csv).

Dry run by default. APPLY=1 deletes from the irw_text_2 draft and asserts exactly
the target was removed. The draft must be RELEASED to take effect.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_qi_2025_swls")
import redivis

OWNER = "datapages"
SHARD = "irw_text_2"
TARGETS = {"qi_2025_swls__items"}
# Must survive: same-deposit item text that is not the SWLS, and the response table.
MUST_STAY = {(SHARD, "qi_2025_self_construal__items"),
             ("item_response_warehouse_3", "qi_2025_swls")}

apply = os.environ.get("APPLY") == "1"


def names(ds, v):
    return {t.name for t in redivis.organization(OWNER).dataset(ds, version=v).list_tables(max_results=2000)}


cur = names(SHARD, "current")
if TARGETS - cur:
    sys.exit(f"ABORT: not published in {SHARD}: {sorted(TARGETS - cur)}")
for ds, t in MUST_STAY:
    if t not in names(ds, "current"):
        sys.exit(f"ABORT: {t} missing from {ds} current")
print(f"{SHARD}: {len(cur)} published; target present; must-stay set present")

if not apply:
    try:
        print(f"DRY RUN: {SHARD} draft open ({len(names(SHARD, 'next'))} tables); would delete {sorted(TARGETS)}")
    except Exception:
        print(f"DRY RUN: no {SHARD} draft; APPLY=1 creates one and deletes {sorted(TARGETS)}")
    sys.exit(0)

redivis.organization(OWNER).dataset(SHARD).create_next_version(if_not_exists=True)
draft = redivis.organization(OWNER).dataset(SHARD, version="next")
before = {t.name for t in draft.list_tables(max_results=2000)}
if TARGETS - before:
    sys.exit(f"ABORT: not in the {SHARD} draft: {sorted(TARGETS - before)}")
for name in sorted(TARGETS):
    draft.table(name).delete()
    print("deleted:", name)
after = names(SHARD, "next")
assert before - after == TARGETS, f"{SHARD}: removed {sorted(before - after)}"
assert len(after) == len(before) - len(TARGETS)
for ds, t in MUST_STAY:
    if ds == SHARD:
        assert t in after, f"{t} went missing from {ds} draft"
print(f"OK {SHARD}: removed exactly {sorted(TARGETS)} ({len(before)} -> {len(after)}). Release owed.")
