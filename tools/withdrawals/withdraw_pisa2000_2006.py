"""Withdraw the six pisa2000_* and pisa2006_* tables from item_response_warehouse (irw#2558).

The student identifier in these six tables is not unique across countries (the #2558
id-collision defect), so rows from different students are merged under one id. The fix
needs the original OECD files, which since 2025 are only obtainable through the PISA PUF
Users Data Collection form, whose terms bar making the data available to third parties;
counsel (2026-10-08) agreed that accepting those terms while republishing would be a
breach. Ben ruled 2026-10-15: withdraw the six as wrong data, and ask OECD for permission
separately (oneoff/emails_2026-10-15/oecd_pisa_permission_draft.md). If OECD agrees, the
tables are rebuilt from the form files (id = CNT_SCHOOLID_STIDSTD) and re-uploaded.

The other 20 pisa* tables are NOT touched: a KEEP set asserts they survive. No item-text
table exists for any pisa* table (checked irw_text, _2, _3 current on 2026-10-15).

The source files for 2000/2006 downloaded in January 2024 stay on disk (data/pisa) and are
not part of this withdrawal.

Published tables, so the withdrawal takes effect at the NEXT release; Ben publishes.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
from pathlib import Path
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_pisa2000_2006")
import redivis
from ledger import record

DATASET = "item_response_warehouse"
TARGETS = {"pisa2000_math", "pisa2000_read", "pisa2000_science",
           "pisa2006_math", "pisa2006_read", "pisa2006_science"}
KEEP = {f"pisa{y}_{s}" for y in (2003, 2009, 2012, 2015, 2022) for s in ("math", "read", "science")} \
     | {"pisa2003_problem_solving", "pisa2018_gc", "pisa2018_math", "pisa2018_read", "pisa2018_science"}
assert len(KEEP) == 20 and not (KEEP & TARGETS)

cur = redivis.user("datapages").dataset(DATASET, version="current")
names = {t.name for t in cur.list_tables()}
print(f"{DATASET} current: {len(names)} tables")
if TARGETS - names:
    sys.exit(f"ABORT: not published in {DATASET}: {sorted(TARGETS - names)}")
if KEEP - names:
    sys.exit(f"ABORT: KEEP table missing from current (scope wrong?): {sorted(KEEP - names)}")
rows_at = {n: cur.table(n).get().properties["numRows"] for n in sorted(TARGETS)}
for n, r in rows_at.items():
    print(f"  {n}: {r:,} rows")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

base = redivis.user("datapages").dataset(DATASET)
base.create_next_version(if_not_exists=True)
ds = redivis.user("datapages").dataset(DATASET, version="next")
before = {t.name for t in ds.list_tables()}
todo = TARGETS & before
print(f"\ndraft tables before: {len(before)}; to delete: {len(todo)} (already gone: {len(TARGETS - before)})")
for name in sorted(todo):
    ds.table(name).delete()
    print("deleted:", name)
after = {t.name for t in redivis.user("datapages").dataset(DATASET, version="next").list_tables()}
assert before - after == todo, f"MISMATCH: removed={sorted(before - after)}"
assert not (TARGETS & after)
assert KEEP <= after, f"KEEP table lost: {sorted(KEEP - after)}"
print(f"OK: draft now {len(after)} tables; all 20 other pisa* tables intact.")
if todo:
    record(sorted(todo), dataset=DATASET, reason="wrong_data", refs="#2558; counsel 2026-10-08; Ben 2026-10-15",
           rows={t: rows_at[t] for t in todo},
           note="student id not unique across countries; source files only via OECD form whose terms bar redistribution; rebuild pending OECD permission",
           script=__file__)
    print("ledger rows written")
