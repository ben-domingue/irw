"""Withdraw BFI-44 wording from the live item-text corpus.

Ben ruled 2026-09-11 on batch_186's escalation: withdraw the three live tables.

The rights holder is Oliver P. John (Berkeley Personality Lab). The BFI-44's own
FAQ page, https://www.ocf.berkeley.edu/~johnlab/bfi.htm (the page that describes
the BFI as "44 items total"), states "I hold the copyright to the BFI and it is not
in the public domain per se. However, it is freely available for researchers to
use for non-commercial research purposes." and "At this time, the BFI is for
non-commercial uses only." Quoted from Wayback snapshots 20150325033626 (sha256
ceba43d286792a9211a64a2f89e2e65ae944436bc45e7990168c5541435cf28d) and
20240111225603 (sha256 c7cbfffb8098498e59b2ce58144d67355c15829238213265de48ee67e50d3230);
the batch_186 orchestrator re-confirmed both sentences in both copies. The page has
since been rewritten for the BFI-2 and says nothing releasing the BFI-44. Same
structure as the BFI-2 block (tools/withdraw_bfi2.py).

WHY THESE SHIPPED. conner_2017_bfi (batch_021) and CV_OASIS_ODSIS_PPE_Novak_2020_BFI
(batch_024) shipped 2026-09-04, before the irw#1945 reserve-a-right rulings existed.
ibrahim_2015_bfi (batch_048) shipped on a round-log reading that "the BFI-44
carries no such terms", made from the current BFI-2 page only. irw#1954 re-audit shape.

All three are wholly BFI-44 (44, 44 and 8 items; the Novak table is the BFI-N
subscale shown in canonical English as a stand-in for the Czech administration), so
each is a whole-table withdrawal. Scope is these three named tables: Ben has not
ruled on a corpus-wide BFI-44 sweep, and nothing here shows the corpus is clean.

Published tables, so each withdrawal takes effect at the NEXT release; Ben publishes.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_bfi44")
import redivis

TARGETS = {
    "conner_2017_bfi__items",                    # BFI-44, 44 items, batch_021
    "CV_OASIS_ODSIS_PPE_Novak_2020_BFI__items",  # BFI-44 N subscale, 8 items, batch_024
    "ibrahim_2015_bfi__items",                   # BFI-44, 44 items, batch_048
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
