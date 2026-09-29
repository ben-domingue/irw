"""Retire test_taking_much_2025_*: a second ingestion of OSF 9j6hm (irw#2513).

The same deposit (same 1,244 people) is also ingested as much_tte_2025_*, which Ben ruled canonical on
2026-09-28 (decision D3 in oneoff/2513-course-data-problems/README.md). Its cov_ac and cov_disruptions were
ported to much_tte_2025_* in PR #2535. Ben approved the retirement 2026-09-28.

Removes five response tables from item_response_warehouse and two item-text tables from irw_text.
KEEP: the five much_tte_2025_* tables, and their item text (irw_text_2).

Dry run by default. Set APPLY=1 to delete.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_much_duplicates_2026_09_28")
import redivis

OWNER = "datapages"                    # metadata/redivis_config.R
PLAN = {
    "item_response_warehouse": (
        {f"test_taking_much_2025_{s}" for s in ("ao", "cm", "ct", "ef", "mr")},
        {f"much_tte_2025_{s}" for s in ("actionorientation", "concentrationtask", "currentmotivation",
                                        "effort", "matrixreasoning")},
    ),
    "irw_text": (
        {"test_taking_much_2025_cm__items", "test_taking_much_2025_ef__items"},
        set(),
    ),
}
TEXT_KEEP = ("irw_text_2", {"much_tte_2025_currentmotivation__items", "much_tte_2025_effort__items"})

apply = os.environ.get("APPLY") == "1"


def names(ds_name, version):
    return {t.name for t in redivis.organization(OWNER).dataset(ds_name, version=version).list_tables(max_results=2000)}


for ds_name, (targets, keep) in PLAN.items():
    current = names(ds_name, "current")
    if targets - current:
        sys.exit(f"ABORT: not in {ds_name} current: {sorted(targets - current)}")
    if keep - current:
        sys.exit(f"ABORT: keep set missing from {ds_name} current: {sorted(keep - current)}")
if TEXT_KEEP[1] - names(TEXT_KEEP[0], "current"):
    sys.exit(f"ABORT: much_tte item text missing from {TEXT_KEEP[0]}: {sorted(TEXT_KEEP[1] - names(TEXT_KEEP[0], 'current'))}")

if not apply:
    for ds_name, (targets, _) in PLAN.items():
        print(f"DRY RUN {ds_name}: would delete {sorted(targets)}")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

for ds_name, (targets, keep) in PLAN.items():
    ds = redivis.organization(OWNER).dataset(ds_name)
    ds.create_next_version(if_not_exists=True)
    draft = redivis.organization(OWNER).dataset(ds_name, version="next")
    before = {t.name for t in draft.list_tables(max_results=2000)}
    if targets - before:
        sys.exit(f"ABORT: not in the {ds_name} draft: {sorted(targets - before)}")
    for name in sorted(targets):
        draft.table(name).delete()
        print("deleted:", ds_name, name)
    after = names(ds_name, "next")
    assert before - after == targets, f"MISMATCH in {ds_name}: removed={sorted(before - after)}"
    assert keep <= after, f"went missing from {ds_name}: {sorted(keep - after)}"
print("OK: removed exactly the targets; much_tte_2025_* and their item text intact. Drafts must be RELEASED.")
