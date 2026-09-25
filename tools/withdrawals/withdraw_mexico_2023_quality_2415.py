"""Withdraw two mexico_2023_quality tables from item_response_warehouse_2 (irw#2415).

Found by item-text round batch_422 (irw#2381 slice 7). data/mexico_2023_quality.do appends ENCIG 2021 under
ENCIG 2023 with no wave column, and INEGI renumbered section V between the waves, so these two tables pool a
different service's answers under the same codes:

  mexico_2023_quality_cablecars  2023 q5.11 = Cablebus/Mexicable, 2021 q5.11 = toll highways; 95.4% of the
                                 non-missing rows on p5_11_1..5 / p5_11a are 2021 toll-highway answers.
  mexico_2023_quality_buses      2023 q5.9 = urban bus, 2021 q5.9 = articulated BRT; 17-18% of each item's
                                 responses are 2021 BRT answers.

Ben 2026-09-25: withdraw these two now (the confirmed ones); audit the rest of the family before touching it.
KEEP: the other 26 mexico_2023_quality_* tables, and gilbert_meta_112/113 (irw-eb's #2313 re-upload in this draft).

Dry run by default. Set APPLY=1 to delete.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_mexico_2023_quality_2415")
import redivis

OWNER   = "datapages"                  # metadata/redivis_config.R
DATASET = "item_response_warehouse_2"
TARGETS = {"mexico_2023_quality_cablecars", "mexico_2023_quality_buses"}
OTHERS  = {"gilbert_meta_112", "gilbert_meta_113"}

apply = os.environ.get("APPLY") == "1"


def names(version):
    return {t.name for t in redivis.organization(OWNER).dataset(DATASET, version=version).list_tables(max_results=2000)}


current = names("current")
if TARGETS - current:
    sys.exit(f"ABORT: not in {DATASET} current: {sorted(TARGETS - current)}")
keep = {n for n in current if n.startswith("mexico_2023_quality")} - TARGETS
keep |= OTHERS & current
print(f"{DATASET} current: {len(current)} tables; keeping {len(keep)} named siblings/others")

if not apply:
    try:
        before = names("next")
        print(f"DRY RUN: draft open, {len(before)} tables; draft vs current: "
              f"+{sorted(before - current)} -{sorted(current - before)}")
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
if keep - before:
    sys.exit(f"ABORT: keep set missing from draft: {sorted(keep - before)}")

for name in sorted(TARGETS):
    draft.table(name).delete()
    print("deleted:", name)

after = names("next")
removed = before - after
assert removed == TARGETS, f"MISMATCH: removed={sorted(removed)}"
assert keep <= after, f"went missing: {sorted(keep - after)}"
print(f"OK: removed exactly {sorted(TARGETS)} from {DATASET}; {len(keep)} kept tables intact. "
      "Draft must be RELEASED to take effect.")
