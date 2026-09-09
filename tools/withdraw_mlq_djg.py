"""Withdraw item text for cognitive_load_klimova_2023_mlq and dopmeijer_2022_loneliness.

Both are LIVE in irw_version 358. Ruled by Ben 2026-09-08:

  cognitive_load_klimova_2023_mlq -- ships nine canonical English MLQ items
  verbatim (Steger et al. 2006). michaelfsteger.com states "Commercial use
  requires prior written permission" and names the University of Minnesota as
  copyright holder: a stated use restriction, which blocks under irw#1945
  (2026-09-05). Same shape as sv-maia2_randelovic_2021_hexaco60.

  dopmeijer_2022_loneliness -- ships the De Jong Gierveld 11-item scale as the
  deposit's OWN English variable labels; none of the eleven match the canonical
  English wording in the DJG manual (osf.io/u6gck), so it is a back-rendering of
  the Dutch administration rather than a transcription. The DJG terms carry
  "No derivatives -- if you remix, transform or build upon the material, you may
  not distribute the modified material", and Ben ruled that ND reaches exactly
  this case. loneliness_mudfold (batch_087) stays blocked.

Both were published, so each withdrawal takes effect at the NEXT release.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_mlq_djg")
import redivis

TARGETS = {
    "cognitive_load_klimova_2023_mlq__items",  # MLQ, Steger: commercial use by permission
    "dopmeijer_2022_loneliness__items",        # DJG-11, de Jong Gierveld: NC + ND
}

# Locate the shard each target is published in.
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
