"""Withdraw the item text of the withdrawn sun_2025_morality study-1 informant tables (irw#2423).

PR #2466 (tools/withdrawals/withdraw_sun_2025_study1_informant.py) deleted the eight
study-1 informant tables from the item_response_warehouse_2 draft: study1-maindat.csv's
it.* columns are per-target informant MEANS, rounded by data/sun_2025_morality.do.
Four of those eight have published item text, which this removes, as the study-3
withdrawal (withdraw_wrongnow_2026_09_25.py, PR #2427) did for study 3:

  irw_text    sun_2025_morality_study1_{honesty,loyalty,morality}__items
  irw_text_2  sun_2025_morality_study1_fairnessMCQ__items

Pairing checked 2026-09-27 against the published tables: each __items table's item set
equals its response table's item set exactly, and all are it.* informant codes
(itmcqh1-4, itmcql1-4, itmcqgm1-6, itmcqf1-4). The study-1 SELF-REPORT tables
(meaning, pemotion, nemotion, prelationships; ts.PERMA.* codes, all integer) stay live
with their item text, and are asserted to survive.

Dry run by default. APPLY=1 deletes from each draft and asserts exactly TARGETS were
removed. The drafts must be RELEASED to take effect, together with the
item_response_warehouse_2 draft that holds the response-table deletions.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_sun_2025_study1_itemtext")
import redivis

OWNER = "datapages"
P = "sun_2025_morality_study1_"
TARGETS = {
    "irw_text": {f"{P}{s}__items" for s in ("honesty", "loyalty", "morality")},
    "irw_text_2": {f"{P}fairnessMCQ__items"},
}
MUST_STAY = {("irw_text", f"{P}{s}__items") for s in ("meaning", "pemotion", "nemotion", "prelationships")}

apply = os.environ.get("APPLY") == "1"


def names(ds, v):
    return {t.name for t in redivis.organization(OWNER).dataset(ds, version=v).list_tables(max_results=2000)}


for ds, targets in TARGETS.items():
    missing = targets - names(ds, "current")
    if missing:
        sys.exit(f"ABORT: not in {ds} current: {sorted(missing)}")
for ds, t in MUST_STAY:
    if t not in names(ds, "current"):
        sys.exit(f"ABORT: {t} missing from {ds} current")

if not apply:
    for ds, targets in TARGETS.items():
        try:
            print(f"DRY RUN {ds}: draft open ({len(names(ds, 'next'))} tables); would delete {sorted(targets)}")
        except Exception:
            print(f"DRY RUN {ds}: no draft; APPLY=1 creates one and deletes {sorted(targets)}")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

for ds, targets in TARGETS.items():
    redivis.organization(OWNER).dataset(ds).create_next_version(if_not_exists=True)
    draft = redivis.organization(OWNER).dataset(ds, version="next")
    before = {t.name for t in draft.list_tables(max_results=2000)}
    if targets - before:
        sys.exit(f"ABORT: not in the {ds} draft: {sorted(targets - before)}")
    for name in sorted(targets):
        draft.table(name).delete()
    after = names(ds, "next")
    assert before - after == targets, f"{ds}: removed {sorted(before - after)}"
    print(f"OK {ds}: removed exactly {len(targets)} ({len(before)} -> {len(after)})")
for ds, t in MUST_STAY:
    assert t in names(ds, "next"), f"{t} went missing from {ds}"
print("Drafts must be RELEASED to take effect.")
