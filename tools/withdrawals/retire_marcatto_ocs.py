"""Retire dvivdtws_ppmial_marcatto_2023_ocs -- a third copy of _dtw (irw#2287).

Ben ruled 2026-09-19, the same way irw#1967 retired _cwb. The two tables hold the same
12,166 rows, 553 participants, 22 items and identical covariates, and _ocs CONTAINS DTW
ITEM CODES: the first rows read back from the live table 2026-09-19 (irw_version 393)
are dtw4, dtw13, dtw15, dtw15, dtw5. Sorted on (id, item) the frames are identical --
all.equal returns TRUE (@xingyi-zhang, irw#2268).

So the name promises the Organizational Commitment scale and the table holds the Dark
Tetrad at Work scale, which is exactly why _cwb was retired rather than _dtw.

NOTE FOR THE #1967 RECORD: that round log says keeping _cwb would have left the sibling
family "(_ocb, _ocs, _snaq, each named for what it holds)" with one member that is not.
That was wrong about _ocs. _ocb and _snaq have NOT been tested here and are worth the
same check before this is closed.

The deposit's real Organizational Commitment responses appear to be absent from IRW
entirely -- _ocs occupies the name without holding the data, the same shape as the CWB
block #1967 found missing. A lead for a future import, not something this fixes.

Located 2026-09-19: shard 1, item_response_warehouse (991 published tables), and in no
other shard. No open draft on that dataset, so nothing else rides along.

KEEP is asserted explicitly: _dtw must survive untouched.

Published table, so the deletion takes effect at the NEXT release; Ben publishes.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("retire_marcatto_ocs")
import redivis

SHARD = "item_response_warehouse"
TARGET = "dvivdtws_ppmial_marcatto_2023_ocs"
KEEP = "dvivdtws_ppmial_marcatto_2023_dtw"

cur = redivis.user("datapages").dataset(SHARD, version="current")
names = {t.name for t in cur.list_tables()}
print(f"{SHARD}: {len(names)} published tables")
if TARGET not in names:
    sys.exit(f"ABORT: {TARGET} is not published in {SHARD}")
if KEEP not in names:
    sys.exit(f"ABORT: keeper {KEEP} is not in {SHARD} -- scope is wrong")

for other in ("item_response_warehouse_2", "item_response_warehouse_3"):
    if TARGET in {t.name for t in redivis.user("datapages").dataset(other, version="current").list_tables()}:
        sys.exit(f"ABORT: {TARGET} also lives in {other}; this tool deletes from one shard only")

print(f"  target: {TARGET}\n  keeper: {KEEP} (must survive)")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

base = redivis.user("datapages").dataset(SHARD)
base.create_next_version(if_not_exists=True)
ds = redivis.user("datapages").dataset(SHARD, version="next")
before = {t.name for t in ds.list_tables()}
print(f"\ndraft tables before: {len(before)}")
if TARGET not in before:
    sys.exit(f"ABORT: {TARGET} not in the draft")
ds.table(TARGET).delete()
print("deleted:", TARGET)

after = {t.name for t in redivis.user("datapages").dataset(SHARD, version="next").list_tables()}
removed = before - after
print(f"draft tables after: {len(after)}")
assert removed == {TARGET}, f"MISMATCH: removed={sorted(removed)}"
assert KEEP in after, f"KEEPER GONE: {KEEP}"
assert len(after) == len(before) - 1, "unexpected count change"
print(f"OK: exactly {TARGET} removed; {KEEP} survives.")
