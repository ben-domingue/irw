"""Withdraw the two live HEXACO-PI-R item-text tables (irw#1945).

Ben's ruling 2026-09-05: IRW ships no HEXACO-PI-R wording. These two were
uploaded in the pilot era, before irw#1891 existed.

Deletes from the irw_text DRAFT, so the tables leave at the next release. If the
last version has been released and no draft is open -- the state right after
someone clicks publish, which reads as "Not found: datapages.irw_text:next" --
a draft is opened first, exactly as red_up.push.open_draft does.

Dry run by default. Set APPLY=1 to delete.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_hexaco")
import redivis

OWNER   = "datapages"          # metadata/redivis_config.R
DATASET = "irw_text"
TARGETS = {"sv-maia2_randelovic_2021_hexaco60__items",
           "sv-maia2_randelovic_2021_hexaco100__items"}
KEEP    = "dasilva_2019_hexaco24__items"   # Brief HEXACO Inventory, CC BY -- must survive

apply = os.environ.get("APPLY") == "1"

cur = redivis.organization(OWNER).dataset(DATASET, version="current")
live = {t.name for t in cur.list_tables()}
print(f"released version: {len(live)} tables; targets live: {sorted(TARGETS & live)}")

def open_draft():
    ds = redivis.organization(OWNER).dataset(DATASET)
    ds.create_next_version(if_not_exists=True)
    return redivis.organization(OWNER).dataset(DATASET, version="next")

if not apply:
    try:
        draft = redivis.organization(OWNER).dataset(DATASET, version="next")
        before = {t.name for t in draft.list_tables()}
        print(f"DRY RUN: draft open, {len(before)} tables; targets present: {sorted(TARGETS & before)}")
    except Exception as exc:
        print(f"DRY RUN: no draft open ({exc}); APPLY=1 would create one.")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

draft = open_draft()
before = {t.name for t in draft.list_tables()}
print(f"draft tables before: {len(before)}")
missing = TARGETS - before
if missing:
    sys.exit(f"ABORT: target not in draft: {missing}")
if KEEP not in before:
    sys.exit(f"ABORT: {KEEP} not in draft; refusing to act on an unexpected dataset")

for name in sorted(TARGETS):
    draft.table(name).delete()
    print("deleted:", name)

after = {t.name for t in redivis.organization(OWNER).dataset(DATASET, version="next").list_tables()}
removed = before - after
print(f"draft tables after: {len(after)}")
print("removed set:", sorted(removed))
assert removed == TARGETS, f"MISMATCH: removed={removed} targets={TARGETS}"
assert KEEP in after, f"{KEEP} went missing"
assert len(after) == len(before) - 2, "unexpected count change"
print("OK: exactly the two targets removed. Draft must be RELEASED for this to take effect.")
