"""Withdraw matosaslopez_2022_bars_teaching from item_response_warehouse_4 (irw#2412).

Found by item-text round batch_397 (irw#2381 slice 6), which blocked it rather than write item text. The
table pools two different BARS instruments (blended: LMS-centred anchors; face-to-face: classroom anchors)
under the same codes BARS_1..BARS_10, so each code denotes two different items (per-item means 2.5-3.3
blended vs 3.8-4.3 face-to-face). Ben 2026-09-24: wrong-now tables are withdrawn at once, then rebuilt
(here: split by teaching mode).

KEEP: the two matosaslopez_2024_* tables, if they share the shard.

Dry run by default. Set APPLY=1 to delete.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_matosaslopez_2022_bars")
import redivis

OWNER   = "datapages"                  # metadata/redivis_config.R
DATASET = "item_response_warehouse_4"
TARGETS = {"matosaslopez_2022_bars_teaching"}
KEEP    = {"matosaslopez_2024_questionnaire_quality", "matosaslopez_2024_teacher_assessment"}

apply = os.environ.get("APPLY") == "1"


def names(version):
    return {t.name for t in redivis.organization(OWNER).dataset(DATASET, version=version).list_tables(max_results=2000)}


current = names("current")
if TARGETS - current:
    sys.exit(f"ABORT: not in {DATASET} current: {sorted(TARGETS - current)}")
keep_here = KEEP & current
print(f"{DATASET} current: {len(current)} tables; siblings in this shard: {sorted(keep_here)}")

if not apply:
    try:
        before = names("next")
        print(f"DRY RUN: draft open, {len(before)} tables; draft vs current: "
              f"+{sorted(before - current)} -{sorted(current - before)}")
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

for name in sorted(TARGETS):
    draft.table(name).delete()
    print("deleted:", name)

after = names("next")
removed = before - after
assert removed == TARGETS, f"MISMATCH: removed={sorted(removed)}"
assert keep_here <= after, f"went missing: {sorted(keep_here - after)}"
print(f"OK: removed exactly {sorted(TARGETS)} from {DATASET}; siblings intact. Draft must be RELEASED to take effect.")
