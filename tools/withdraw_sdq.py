"""Withdraw the two live tables carrying Goodman SDQ wording.

Ben ruled 2026-09-10 in the batch_156 triage. The clause is sdqinfo.org's, and it
reserves three separate rights: it bars distributing electronic versions without
prior authorization, adds a no-derivatives term, and restricts use to non-profit
purposes. Under the 2026-09-06 rule that any stated restriction on the instrument
blocks outright, that outranks either deposit's CC BY 4.0 -- the deposit licence is
not the instrument licence -- and it reaches translations explicitly.

The same clause blocked ren_2019_sdq and ren2019_sdq in batch_156 the same day, so
the corpus was refusing to ship wording it was already publishing elsewhere.

  addy_2021_sdq_ghana        10 items, the SDQ
  ALSECYPIAMH_WU_2022_SDQ     5 items, the SDQ prosocial subscale

Both are WHOLE-table withdrawals: every item in each is SDQ, so there is no
unblocked block to preserve and no partial withdrawal to get wrong.

Neither has a provenance.csv row -- both predate the batch pipeline -- so per
itemtext_standard.md the record lives in instrument_rights_register.csv and the
round log only, and no provenance row is manufactured to hold it.

NOT a target, and must survive: heekerens2025_sdq. Its name matches but it is the
Somatoform Dissociation Questionnaire (SDQ-20), a different instrument entirely --
an instrument-name match is a lead, never a verdict.

Both are published, so each withdrawal takes effect at the next release.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_sdq")
import redivis

TARGETS = {"addy_2021_sdq_ghana__items", "ALSECYPIAMH_WU_2022_SDQ__items"}
KEEP = {"heekerens2025_sdq__items"}

shards = {}
for shard in ("irw_text", "irw_text_2"):
    names = {t.name for t in redivis.user("datapages").dataset(shard, version="current").list_tables()}
    print(f"{shard}: {len(names)} published tables")
    if TARGETS & names:
        shards[shard] = TARGETS & names
    if KEEP & names:
        print(f"  keep-set present in {shard}: {sorted(KEEP & names)}")

found = {t for s in shards.values() for t in s}
if found != TARGETS:
    sys.exit(f"ABORT: not published anywhere: {sorted(TARGETS - found)}")
for s, ts in shards.items():
    print(f"  {s}: {len(ts)} targets")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

for shard, targets in shards.items():
    base = redivis.user("datapages").dataset(shard)
    base.create_next_version(if_not_exists=True)
    ds = redivis.user("datapages").dataset(shard, version="next")
    before = {t.name for t in ds.list_tables()}
    keep_before = KEEP & before
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
    assert KEEP & after == keep_before, "ABORT: heekerens2025_sdq went missing"
    assert len(after) == len(before) - len(targets), f"unexpected count change in {shard}"
    print(f"OK: exactly the {len(targets)} targets removed from {shard}; keep-set intact.")
