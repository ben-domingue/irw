"""Retire dvivdtws_ppmial_marcatto_2023_ocb and _snaq -- the last two copies of _dtw (irw#2364).

Same call as irw#1967 (_cwb) and irw#2287 (_ocs, tools/withdrawals/retire_marcatto_ocs.py).
Checked 2026-09-27 against the released tables (item_response_warehouse v62.0): _ocb, _snaq
and _dtw each hold 12,166 rows, 553 ids and items dtw1..dtw22, with the same columns
(id, cov_gender, cov_age, cov_language, item, resp), and sorted on every column the _ocb and
_snaq frames are IDENTICAL to _dtw's. So the names promise Organizational Citizenship
Behavior and the Short Negative Acts Questionnaire, and both tables hold the Dark Tetrad at
Work items. Only _dtw is named for what it holds, so it is the one kept.

With this, all four siblings (_cwb, _ocs, _ocb, _snaq) are gone. The deposit's real OCS,
OCB, CWB and SNAQ blocks (osf.io/8mj73 data.csv) are not in IRW at all -- a lead for a
future import, not something this fixes.

Located 2026-09-27: shard 1, item_response_warehouse, and in no other shard. KEEP is
asserted explicitly: _dtw must survive untouched. The item text for these rows is live
under dvivdtws_ppmial_marcatto_2023_dtw__items; neither retired table has an __items table.

Published tables, so the deletion takes effect at the NEXT release; Ben publishes.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("retire_marcatto_ocb_snaq")
import redivis

OWNER = "datapages"                     # metadata/redivis_config.R
SHARD = "item_response_warehouse"
TARGETS = {"dvivdtws_ppmial_marcatto_2023_ocb", "dvivdtws_ppmial_marcatto_2023_snaq"}
KEEP = "dvivdtws_ppmial_marcatto_2023_dtw"
OTHER_SHARDS = ("item_response_warehouse_2", "item_response_warehouse_3",
                "item_response_warehouse_4", "item_response_warehouse_5",
                "item_response_warehouse_6")


def names(ds, version):
    return {t.name for t in redivis.user(OWNER).dataset(ds, version=version)
            .list_tables(max_results=5000)}


cur = names(SHARD, "current")
print(f"{SHARD}: {len(cur)} published tables")
if TARGETS - cur:
    sys.exit(f"ABORT: not published in {SHARD}: {sorted(TARGETS - cur)}")
if KEEP not in cur:
    sys.exit(f"ABORT: keeper {KEEP} is not in {SHARD} -- scope is wrong")
for other in OTHER_SHARDS:
    hit = TARGETS & names(other, "current")
    if hit:
        sys.exit(f"ABORT: {sorted(hit)} also live in {other}; this tool deletes from one shard only")

print(f"  targets: {sorted(TARGETS)}\n  keeper:  {KEEP} (must survive)")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

base = redivis.user(OWNER).dataset(SHARD)
base.create_next_version(if_not_exists=True)
ds = redivis.user(OWNER).dataset(SHARD, version="next")
before = names(SHARD, "next")
print(f"\ndraft tables before: {len(before)}")
if TARGETS - before:
    sys.exit(f"ABORT: not in the draft: {sorted(TARGETS - before)}")
for name in sorted(TARGETS):
    ds.table(name).delete()
    print("deleted:", name)

after = names(SHARD, "next")
removed = before - after
print(f"draft tables after: {len(after)}")
assert removed == TARGETS, f"MISMATCH: removed={sorted(removed)}"
assert KEEP in after, f"KEEPER GONE: {KEEP}"
assert len(after) == len(before) - len(TARGETS), "unexpected count change"
print(f"OK: exactly {sorted(TARGETS)} removed; {KEEP} survives. Release owed.")
