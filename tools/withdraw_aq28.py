"""Withdraw AQ-28 wording from the live item-text corpus.

Ben ruled 2026-09-11, on batch_191's for-the-human item 2: withdraw
rmet_higgins_2022_aq and widen the register's AQ row to the whole ARC AQ family.

The table serves the 28-item short Autism Spectrum Quotient (AQ-Short; Hoekstra et al.
2011) verbatim -- AQ01..AQ28, all 28 statements read back from the live table
2026-09-11 ("I prefer to do things with others rather than on my own." ...
"I find it easy to play games with children that involve pretending."), matching
itemtables/pilot/audit_confirmed.csv ("the standard Autism Spectrum Quotient (AQ-28)
verbatim"). The Autism Research Centre's test-download terms, re-checked by the
batch_191 trevisan_2018_aq round: "used for research purposes and not for commercial
use ... You may not adapt or modify any of these tests, unless permission has been
given" -- a reserved right, the same clause under which trevisan_2018_aq (AQ-50) was
blocked and conspiracy_asd__asd_aq10 withdrawn (irw#1955).

WHY IT SHIPPED. A pilot table (2026-08-21), before the reserve-a-right rulings; the
register row named only the AQ-10 and matched `^aq` on codes, which AQ01..AQ28 would
hit, but nothing sweeps the published corpus. Its sibling rmet_higgins_2022_tas was
withdrawn under the TAS ruling. irw#1954 re-audit shape.

Whole-table withdrawal. Scope is this one named table: no corpus-wide AQ sweep has
been run, and nothing here shows the corpus is clean.

Published table, so the withdrawal takes effect at the NEXT release; Ben publishes.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_aq28")
import redivis

TARGETS = {
    "rmet_higgins_2022_aq__items",  # AQ-28 (AQ-Short), 28 items, pilot 2026-08-21
}

shards = {}
for shard in ("irw_text", "irw_text_2"):
    cur = redivis.user("datapages").dataset(shard, version="current")
    names = {t.name for t in cur.list_tables()}
    print(f"{shard}: {len(names)} published tables")
    for t in TARGETS & names:
        shards.setdefault(shard, set()).add(t)

found = {t for s in shards.values() for t in s}
if found != TARGETS:
    sys.exit(f"ABORT: not published anywhere: {sorted(TARGETS - found)}")
for s, ts in shards.items():
    print(f"  {s}: {sorted(ts)}")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

for shard, targets in shards.items():
    base = redivis.user("datapages").dataset(shard)
    base.create_next_version(if_not_exists=True)
    ds = redivis.user("datapages").dataset(shard, version="next")
    before = {t.name for t in ds.list_tables()}
    print(f"\n{shard} draft tables before: {len(before)}")
    if targets - before:
        sys.exit(f"ABORT: target not in {shard} draft: {sorted(targets - before)}")
    for name in sorted(targets):
        ds.table(name).delete()
        print("deleted:", name)
    after = {t.name for t in redivis.user("datapages").dataset(shard, version="next").list_tables()}
    removed = before - after
    print(f"{shard} draft tables after: {len(after)}")
    assert removed == targets, f"MISMATCH in {shard}: removed={sorted(removed)}"
    assert len(after) == len(before) - len(targets), f"unexpected count change in {shard}"
    print(f"OK: exactly the {len(targets)} target(s) removed from {shard}.")
