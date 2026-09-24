"""Withdraw two response tables serving wrong data from item_response_warehouse (irw#2408, irw#2409).

Found by item-text round batch_379 (irw#2381 slice 5), which blocked both rather than write item text.
Ben 2026-09-24: withdraw now, rebuild and re-upload later.

  DMCT_Addis_2020_MCT   resp is the task's answer key, not participant accuracy: every item is constant
                        across all 92 participants and equals the stimulus's Korrekt column (irw#2408).
  PBS_Surrain_2019_PoB  pools two studies whose PoB item codes denote different questions (PoB4, 6-10),
                        and all 319 Study 2 respondents duplicate Study 1 respondents (irw#2409).

KEEP: the two DMCT siblings stay in the shard, and DMCT_Addis_2020_PSIQ's item text stays in irw_text.

Dry run by default. Set APPLY=1 to delete.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_wrongnow_2026_09_24")
import redivis

OWNER   = "datapages"                  # metadata/redivis_config.R
DATASET = "item_response_warehouse"
TARGETS = {"DMCT_Addis_2020_MCT", "PBS_Surrain_2019_PoB"}
KEEP    = {"DMCT_Addis_2020_PSIQ", "DMCT_Addis_2020_SUIS"}
TEXT    = ("irw_text", "DMCT_Addis_2020_PSIQ__items")   # must survive

apply = os.environ.get("APPLY") == "1"


def names(ds_name, version):
    return {t.name for t in redivis.organization(OWNER).dataset(ds_name, version=version).list_tables(max_results=2000)}


current = names(DATASET, "current")
if TARGETS - current:
    sys.exit(f"ABORT: not in {DATASET} current: {sorted(TARGETS - current)}")

if not apply:
    try:
        before = names(DATASET, "next")
        print(f"DRY RUN: draft open, {len(before)} tables (current {len(current)}); "
              f"targets present: {sorted(TARGETS & before)}; keep missing: {sorted(KEEP - before)}; "
              f"draft vs current names: +{sorted(before - current)} -{sorted(current - before)}")
    except Exception as exc:
        print(f"DRY RUN: no draft open ({type(exc).__name__}); APPLY=1 would create one.")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

ds = redivis.organization(OWNER).dataset(DATASET)
ds.create_next_version(if_not_exists=True)
draft = redivis.organization(OWNER).dataset(DATASET, version="next")
before = {t.name for t in draft.list_tables(max_results=2000)}
if TARGETS - before:
    sys.exit(f"ABORT: not in the {DATASET} draft: {sorted(TARGETS - before)}")
if KEEP - before:
    sys.exit(f"ABORT: keep set missing from draft: {sorted(KEEP - before)}")

for name in sorted(TARGETS):
    draft.table(name).delete()
    print("deleted:", name)

after = names(DATASET, "next")
removed = before - after
assert removed == TARGETS, f"MISMATCH: removed={sorted(removed)}"
assert KEEP <= after, f"went missing: {sorted(KEEP - after)}"
assert TEXT[1] in names(TEXT[0], "current"), f"{TEXT[1]} went missing from {TEXT[0]}"
print(f"OK: removed exactly {sorted(TARGETS)} from {DATASET}; siblings and item text intact. "
      "Draft must be RELEASED to take effect.")
