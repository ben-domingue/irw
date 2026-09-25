"""Withdraw ds14_mokken, found serving wrong data in #2382 item-text triage (wave 7), 2026-09-25.
Ben's standing rule (2026-09-24/25): a table found serving wrong data is withdrawn at once, then rebuilt.

item_response_warehouse
  ds14_mokken    data/mokken.R lines 81-82: `x[,3]<-abs(5-x[,3])` then `x[,5]<-abs(5-x[,3])`. Column 3 is Si1.,
                 column 5 is Si3. Si1. is recoded 0-4 -> 5-1 (against the don't-recode rule, and off by one), and
                 Si3. is then overwritten with |5-(5-Si1)| = the ORIGINAL Si1; the real Si3 responses are lost.
                 Verified live: Si1.+Si3. = 5 for all 540 persons (r = -1.00); Si1. ranges 1-5, all other items 0-4.

Dry run by default. Set APPLY=1 to delete. Asserts exactly TARGETS were removed from the draft.
"""

import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_wrongnow_2026_09_25c")
import redivis

OWNER = "datapages"
TARGETS = {"item_response_warehouse": {"ds14_mokken"}}
MUST_STAY = {("item_response_warehouse", "cavalini_mokken"), ("item_response_warehouse", "transreas_mokken")}

apply = os.environ.get("APPLY") == "1"


def names(ds, v):
    return {t.name for t in redivis.organization(OWNER).dataset(ds, version=v).list_tables(max_results=2000)}


for ds, targets in TARGETS.items():
    cur = names(ds, "current")
    missing = targets - cur
    if missing:
        sys.exit(f"ABORT: not in {ds} current: {sorted(missing)}")
for ds, t in MUST_STAY:
    if t not in names(ds, "current"):
        sys.exit(f"ABORT: {t} missing from {ds} current")

if not apply:
    for ds, targets in TARGETS.items():
        try:
            nxt = names(ds, "next")
            print(f"DRY RUN {ds}: draft open ({len(nxt)} tables); would delete {len(targets)}")
        except Exception:
            print(f"DRY RUN {ds}: no draft; APPLY=1 creates one and deletes {len(targets)}")
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
    print(f"OK {ds}: removed exactly {len(targets)}")
for ds, t in MUST_STAY:
    assert t in names(ds, "next"), f"{t} went missing from {ds}"
print("Drafts must be RELEASED to take effect.")
