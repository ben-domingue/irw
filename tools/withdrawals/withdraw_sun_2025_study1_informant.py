"""Withdraw the eight sun_2025_morality study-1 informant tables (#2423): same defect as study 3.

study1-maindat.csv (OSF 5e9y3, data-clean/) carries one row per TARGET, with `numinformants`
(1 for 212 targets, 2 for 167, 3 for 102, 4 for 26), and its it.* columns are the MEAN of that
target's informants. data/sun_2025_morality.do then applies `replace resp = round(resp)`. Checked
2026-09-27 against the live tables (irw_version 439): every non-null live resp equals round-half-up
of the matching it.* cell, and 4,962 of the 16,185 informant cells (30.7%) were non-integer before
rounding. So these tables ship rounded per-target means as item responses, exactly what #2423
found for study 3, whose 17 tables were withdrawn on 2026-09-25 (withdraw_wrongnow_2026_09_25.py).

The deposit has no informant-level file to rebuild from: study1-suppdat.xlsx and study3-itemdat.xlsx
are password-encrypted (CDFV2 Encrypted), and study1-demographics.csv holds informant demographics
only. So this is a withdrawal, not a rebuild.

Kept on purpose: the four study-1 self-report tables (pemotion, nemotion, meaning, prelationships,
from ts.PERMA.* -- all integer), and every study-2 table (study2-maindat.csv's it.* columns are one
per rater, it.mtK_j, all integer).

Their item text is NOT touched here: sun_2025_morality_study1_{honesty,loyalty,morality}__items
(irw_text) and sun_2025_morality_study1_fairnessMCQ__items (irw_text_2) are owed the same withdrawal
the study-3 item text got.

Dry run by default. APPLY=1 deletes from the item_response_warehouse_2 draft and asserts exactly
TARGETS were removed and the KEEP siblings survive. The draft must be RELEASED to take effect.
"""
import os
import sys

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_sun_2025_study1_informant")
import redivis

OWNER = "datapages"
SHARD = "item_response_warehouse_2"
P = "sun_2025_morality_study1_"
TARGETS = {P + s for s in ("morality", "compassion", "respectfulness", "honesty", "loyalty",
                           "fairnessMCQ", "fairnessHEXACO", "dependability")}
KEEP = {P + s for s in ("pemotion", "nemotion", "meaning", "prelationships")}


def names(v):
    return {t.name for t in redivis.organization(OWNER).dataset(SHARD, version=v).list_tables(max_results=2000)}


cur = names("current")
if TARGETS - cur:
    sys.exit(f"ABORT: not in {SHARD} current: {sorted(TARGETS - cur)}")
if KEEP - cur:
    sys.exit(f"ABORT: keepers missing from {SHARD} current: {sorted(KEEP - cur)}")
for other in ("item_response_warehouse", "item_response_warehouse_3", "item_response_warehouse_4",
              "item_response_warehouse_5", "item_response_warehouse_6"):
    clash = TARGETS & {t.name for t in redivis.organization(OWNER).dataset(other, version="current").list_tables(max_results=2000)}
    if clash:
        sys.exit(f"ABORT: {sorted(clash)} also in {other}")
print(f"{SHARD}: {len(cur)} published; {len(TARGETS)} targets, {len(KEEP)} keepers present")

if os.environ.get("APPLY") != "1":
    try:
        print(f"DRY RUN: draft open ({len(names('next'))} tables); would delete {len(TARGETS)}")
    except Exception:
        print(f"DRY RUN: no draft; APPLY=1 creates one and deletes {len(TARGETS)}")
    sys.exit(0)

redivis.organization(OWNER).dataset(SHARD).create_next_version(if_not_exists=True)
draft = redivis.organization(OWNER).dataset(SHARD, version="next")
before = {t.name for t in draft.list_tables(max_results=2000)}
if TARGETS - before:
    sys.exit(f"ABORT: not in the draft: {sorted(TARGETS - before)}")
for name in sorted(TARGETS):
    draft.table(name).delete()
    print("deleted", name)
after = names("next")
assert before - after == TARGETS, f"removed {sorted(before - after)}"
assert KEEP <= after, f"keeper gone: {sorted(KEEP - after)}"
print(f"OK: draft {len(before)} -> {len(after)}; exactly the {len(TARGETS)} targets removed. Release to take effect.")
