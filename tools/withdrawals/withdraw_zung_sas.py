"""Withdraw Zung SAS item text: `zhou_2016_anxiety__items` from irw_text.

Ben ruled Zung SAS `block` on 2026-09-23 (instrument_rights_register.csv,
commit 3f9a55eb). The distributor, Mapi ePROVIDE, gates the scale behind a
login. zhou_2016_anxiety is the only live Zung item-text table. It carries all
20 canonical English items. The other Zung table, shen_2020_sas20, was never
uploaded. The response table is untouched: only the item text is withdrawn.

Scope was set by reading the wording, not by name or code: the live rows'
instrument is "Zung Self-Rating Anxiety Scale (SAS)" and item_text is Zung's
own English ("I feel more nervous and anxious than usual." ...).

Asserts the draft loses exactly this one table. Dry run by default. Set
APPLY=1 to delete.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_zung_sas")
import redivis

OWNER   = "datapages"          # metadata/redivis_config.R
DATASET = "irw_text"
TARGET  = "zhou_2016_anxiety__items"

apply = os.environ.get("APPLY") == "1"

def names(ds):
    return {t.name for t in ds.list_tables()}

current = names(redivis.organization(OWNER).dataset(DATASET, version="current"))
if TARGET not in current:
    sys.exit(f"ABORT: {TARGET} is not in {DATASET}:current -- nothing to withdraw, or the name is wrong")

if not apply:
    try:
        draft = redivis.organization(OWNER).dataset(DATASET, version="next")
        before = names(draft)
        print(f"DRY RUN: draft open, {len(before)} tables; target present: {TARGET in before}")
    except Exception as exc:
        print(f"DRY RUN: no draft open ({exc}); APPLY=1 would create one from current "
              f"({len(current)} tables).")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

ds = redivis.organization(OWNER).dataset(DATASET)
ds.create_next_version(if_not_exists=True)
draft = redivis.organization(OWNER).dataset(DATASET, version="next")
before = names(draft)
if TARGET not in before:
    sys.exit(f"ABORT: {TARGET} not in the {DATASET} draft")

draft.table(TARGET).delete()
print("deleted:", TARGET)

after = names(redivis.organization(OWNER).dataset(DATASET, version="next"))
removed = before - after
assert removed == {TARGET}, f"MISMATCH: removed={removed}"
assert after - before == set(), f"unexpected additions: {after - before}"
print(f"OK: only {TARGET} removed from the {DATASET} draft ({len(before)} -> {len(after)}). "
      "Draft must be RELEASED to take effect.")
