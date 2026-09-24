"""Withdraw `2024_online_addiction_*` from item_response_warehouse_2 (irw#2245).

The three tables duplicate `ma2026_bsmas/_igds/_sabas` in item_response_warehouse_3:
same figshare file (27211839, file 49748748), ingested by hand on 2026-06-10 from a
private share link before the deposit was published. The 2024 copy carries
`cov_birthdate` (children's full dates of birth) and has no licence recorded;
ma2026_* dropped the birthdates and carries the deposit's CC BY 4.0. Ben ruled
2026-09-19: withdraw the 2024 copy, keep ma2026_*.

Refuses to act unless every ma2026_* twin is in item_response_warehouse_3 `current`.
Asserts the draft lost exactly the three targets and the twins are untouched.

Dry run by default. Set APPLY=1 to delete. The draft must be RELEASED to take effect,
and prior versions of _2 still serve the tables (see the issue's open question).
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_online_addiction")
import redivis

OWNER   = "datapages"          # metadata/redivis_config.R
DATASET = "item_response_warehouse_2"
TARGETS = {"2024_online_addiction_bsmas", "2024_online_addiction_igds", "2024_online_addiction_sabas"}
TWIN_DS = "item_response_warehouse_3"
TWINS   = {"ma2026_bsmas", "ma2026_igds", "ma2026_sabas"}

apply = os.environ.get("APPLY") == "1"

def names(dataset, version):
    return {t.name for t in redivis.organization(OWNER).dataset(dataset, version=version).list_tables()}

twins = names(TWIN_DS, "current")
if TWINS - twins:
    sys.exit(f"ABORT: twins missing from {TWIN_DS} current: {sorted(TWINS - twins)}; "
             "withdrawing would take the data out of the corpus entirely")

if not apply:
    try:
        before = names(DATASET, "next")
        print(f"DRY RUN: draft open, {len(before)} tables; targets present: "
              f"{sorted(TARGETS & before)}; missing: {sorted(TARGETS - before)}")
    except Exception as exc:
        print(f"DRY RUN: no draft open ({exc}); APPLY=1 would create one.")
    print(f"twins present in {TWIN_DS} current: {sorted(TWINS)}")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

redivis.organization(OWNER).dataset(DATASET).create_next_version(if_not_exists=True)
draft = redivis.organization(OWNER).dataset(DATASET, version="next")
before = {t.name for t in draft.list_tables()}
if TARGETS - before:
    sys.exit(f"ABORT: not in the {DATASET} draft: {sorted(TARGETS - before)}")

for name in sorted(TARGETS):
    draft.table(name).delete()
    print("deleted:", name)

after = names(DATASET, "next")
removed = before - after
assert removed == TARGETS, f"MISMATCH: removed={sorted(removed)}"
assert TWINS <= names(TWIN_DS, "current"), "a ma2026_* twin went missing"
print(f"OK: exactly {len(TARGETS)} tables removed from the {DATASET} draft; ma2026_* intact. "
      "Draft must be RELEASED to take effect.")
