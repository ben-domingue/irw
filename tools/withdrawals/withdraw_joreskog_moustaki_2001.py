"""Withdraw `joreskog_moustaki_2001` (irw#2266).

The table is response patterns hand-typed from Table 3 of Joreskog & Moustaki (2001),
"Factor Analysis of Ordinal Variables: A Comparison of Three Approaches", Multivariate
Behavioral Research (data/joreskog_moustaki_2001.R). There is no data deposit and no
licence anywhere: the dictionary records `Original License = Missing (NA)`, the source
is a ResearchGate copy of a paywalled article, and unlicensed data is a hard stop.
The #2255 pilot also flagged that the table may hold only the most frequent patterns,
not the full sample. Ben ruled 2026-09-23 on #2266: withdraw (option c).

The shard is found, not assumed: exactly one of the six must hold the table in
`current`, or the script aborts. Asserts the draft lost exactly this one table.

Dry run by default. Set APPLY=1 to delete. The draft must be RELEASED by Ben to take
effect, and prior versions still serve the table at their version tags.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_joreskog_moustaki_2001")
import redivis

OWNER  = "datapages"          # metadata/redivis_config.R
SHARDS = ["item_response_warehouse"] + [f"item_response_warehouse_{i}" for i in range(2, 7)]
TARGET = "joreskog_moustaki_2001"

apply = os.environ.get("APPLY") == "1"


def names(dataset, version):
    return {t.name for t in redivis.organization(OWNER).dataset(dataset, version=version).list_tables()}


hits = [ds for ds in SHARDS if TARGET in names(ds, "current")]
if len(hits) != 1:
    sys.exit(f"ABORT: expected {TARGET} in exactly one shard's current, found {hits}")
dataset = hits[0]
current = names(dataset, "current")

if not apply:
    try:
        draft = names(dataset, "next")
        print(f"DRY RUN {dataset}: draft ALREADY OPEN with {len(draft)} tables "
              f"(current {len(current)}); would delete {TARGET}")
    except Exception as exc:
        print(f"DRY RUN {dataset}: no draft open ({str(exc)[:60]}); APPLY=1 would create one. "
              f"Would delete {TARGET}")
    sys.exit(0)

ds = redivis.organization(OWNER).dataset(dataset)
ds.create_next_version(if_not_exists=True)
before = names(dataset, "next")
if TARGET not in before:
    sys.exit(f"ABORT: {TARGET} not in the {dataset} draft")

redivis.organization(OWNER).dataset(dataset, version="next").table(TARGET).delete()
after = names(dataset, "next")
removed = before - after
assert removed == {TARGET}, f"MISMATCH in {dataset}: removed={sorted(removed)}"
print(f"OK {dataset}: removed {TARGET}, {len(after)} tables left in the draft. "
      f"The draft must be RELEASED to take effect.")
