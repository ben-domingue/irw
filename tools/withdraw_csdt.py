"""Withdraw the three live tables carrying Center for Self-Determination Theory instruments.

Ben ruled 2026-09-09, FULL SCOPE: the CSDT Limited Use License reaches every
instrument in the library, not only wording downloaded from
selfdeterminationtheory.org. Deci and Ryan are the originators, and the
2026-09-08 originator ruling reaches translations and adaptations, so where a
given study took its items from does not change the answer.

The licence (https://selfdeterminationtheory.org/terms-and-conditions/,
sha256 fe92eda1273f0dbd9b5af37f677f8412baf9c663dc0886309dfa41cfda5ab10d) grants
"a non-exclusive, non-transferable, limited use license to use the Materials
solely for non-for-profit research purposes" and bars the user from
"(ii) make available or distribute all or any portion of the Materials to any
third party" and "(v) publish the Materials online in any form, without the
prior written consent of the Organization." Three reserved rights at once.

What forced the ruling was a real inconsistency, not a suspected one:
makransky_2016_motivation was BLOCKED on the IMI Interest/Enjoyment subscale
while fivpei_perrig_2023_imi served the same canonical stems LIVE, with the
target activity substituted ("The game was fun to play" for "This activity was
fun to do"). Verified item by item before this script was written.

All three are published, so each withdrawal takes effect at the next release.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_csdt")
import redivis

TARGETS = {
    "fivpei_perrig_2023_imi__items",     # Intrinsic Motivation Inventory, English, 49 rows
    "baka2023_bpnsf__items",             # BPNSFS at Work, Polish as administered, 168 rows
    "aspirations_sonmez_2022__items",    # Aspiration Index, Turkish as administered, 245 rows
}

shards = {}
for shard in ("irw_text", "irw_text_2"):
    names = {t.name for t in redivis.user("datapages").dataset(shard, version="current").list_tables()}
    print(f"{shard}: {len(names)} published tables")
    if TARGETS & names:
        shards[shard] = TARGETS & names

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
    print(f"OK: exactly the {len(targets)} targets removed from {shard}.")
