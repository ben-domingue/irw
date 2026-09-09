"""Withdraw the eight remaining live tables carrying canonical Cohen PSS wording.

Ben ruled 2026-09-08: withdraw all eight. This is the same Cohen/CMU restriction
("Use of the PSS in profit making ventures including corporate clinical trials
requires special permission and a nominal fee") that already withdrew
bakker/beck/duboz (2026-09-06) and gillman_2023_pss/cormier_2024_pss4
(2026-09-07, 5004d7e). The ruling existed; the corpus was never swept.

Each target was verified item-by-item against the ten canonical PSS-10 items --
not matched on table name. Six reproduce the instrument near-completely:

  mhscdc_fried_2020_ps          10 items, all 10 canonical
  eammi_grahe_2018_stress       10 items, all 10 canonical
  ecps_sahm_2024_stress         27 items, all 10 canonical
  lhsbrasil_couto_2023_pss      10 items,  9 canonical
  paampsmartsud_saba_2023_pss   10 items,  9 canonical
  gilbert_meta_59               10 items,  9 canonical
  oxfordcovid_xue_2024_pss       4 items,  4 of 4 canonical
  kfcovid_pss_li2020             4 items,  1 canonical

NOT a target, and must survive: alkouri_2025_icu_stressors. Its `instrument`
field says "Perceived Stress Scale (PSS)" but the items are Sheu et al. (1997),
a nursing-student clinical-placement stressor scale -- zero canonical matches
across 29 distinct items. An instrument-name match is a lead, never a verdict.

All eight are published, so each withdrawal takes effect at the next release.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_pss_sweep")
import redivis

TARGETS = {
    "lhsbrasil_couto_2023_pss__items",
    "oxfordcovid_xue_2024_pss__items",
    "kfcovid_pss_li2020__items",
    "paampsmartsud_saba_2023_pss__items",
    "mhscdc_fried_2020_ps__items",
    "gilbert_meta_59__items",
}
# Already handled before this script ran, verified in the draft -- do NOT re-delete:
#   eammi_grahe_2018_stress__items  -- withdrawn whole (8975953), absent from draft
#   ecps_sahm_2024_stress__items    -- PARTIAL withdrawal, draft numRows 87 against 137
#                                      published; the 18 COVID-stressor items are unrestricted
#                                      and must survive, so it must NOT be deleted whole.
ALREADY = {"eammi_grahe_2018_stress__items", "ecps_sahm_2024_stress__items"}
# Verified NOT the PSS; a name-based sweep would have taken it.
KEEP = {"alkouri_2025_icu_stressors__items", "ecps_sahm_2024_stress__items"}

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
    assert KEEP & after == keep_before, "ABORT: alkouri_2025_icu_stressors went missing"
    assert len(after) == len(before) - len(targets), f"unexpected count change in {shard}"
    print(f"OK: exactly the {len(targets)} targets removed from {shard}; keep-set intact.")
