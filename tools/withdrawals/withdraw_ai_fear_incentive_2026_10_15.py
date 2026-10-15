"""Withdraw ai_fear_dong_2026_incentive (#2906, PR #3011; 2026-10-15).

Its "responses" were the experimental condition, not answers: in South Korea and the UK, 500 respondents
were offered a bonus for accurate estimates of others' fear and 500 were not, and the long source file
carries that flag on every one of a person's 48 rows. The table held 1,000 ids x 48 items, each person all
0 or all 1. PR #3011 (merged 2026-10-15) stops data/ai_fear_dong_2026.py writing it and puts the condition
on ai_fear_dong_2026_other_fear as `treat`; the three siblings (_ai, _own_fear, _other_fear) were
re-uploaded to the item_response_warehouse_2 draft the same day with one row per real answer.

item_response_warehouse_2
  ai_fear_dong_2026_incentive   #2906   out_of_scope (a condition stored as resp)
  KEEP ai_fear_dong_2026_requirement, _ai, _own_fear, _other_fear

No item text exists for it. Its ledger row is committed with this script; APPLY=1 adds it only if missing.

Dry run by default. Set APPLY=1 to delete. Resumable: a rerun deletes whatever targets remain in the draft.
"""
import csv, os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_ai_fear_incentive_2026_10_15")
import redivis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import LEDGER, record

OWNER = "datapages"                    # metadata/redivis_config.R

T = {
    "ai_fear_dong_2026_incentive": ("item_response_warehouse_2", "out_of_scope", "#2906 #3011", 48000,
        "the between-person incentive condition stored as resp (each person all 0 or all 1); now `treat` on ai_fear_dong_2026_other_fear"),
}
KEEP = {
    "item_response_warehouse_2": {"ai_fear_dong_2026_requirement", "ai_fear_dong_2026_ai",
                                  "ai_fear_dong_2026_own_fear", "ai_fear_dong_2026_other_fear"},
}
TARGETS = {}
for name, (ds, *_rest) in T.items():
    TARGETS.setdefault(ds, set()).add(name)

apply = os.environ.get("APPLY") == "1"


def names(ds, version):
    return {t.name for t in redivis.organization(OWNER).dataset(ds, version=version).list_tables(max_results=2000)}


current = {ds: names(ds, "current") for ds in sorted(set(TARGETS) | set(KEEP))}
for ds, keep in KEEP.items():
    if keep - current[ds]:
        sys.exit(f"ABORT: KEEP not in {ds} current: {sorted(keep - current[ds])}")

if not apply:
    for ds, targets in sorted(TARGETS.items()):
        print(f"{ds}: targets in current {len(targets & current[ds])}/{len(targets)}"
              + (f"; already gone from current: {sorted(targets - current[ds])}" if targets - current[ds] else ""))
        try:
            nxt = names(ds, "next")
            print(f"  DRY RUN: draft open ({len(nxt)} tables, current {len(current[ds])}); "
                  f"targets in draft: {sorted(targets & nxt)}; keep missing from draft: "
                  f"{sorted(KEEP.get(ds, set()) - nxt)}; draft vs current: +{sorted(nxt - current[ds])} "
                  f"-{sorted(current[ds] - nxt)}")
        except Exception as exc:
            print(f"  DRY RUN: no draft open ({type(exc).__name__}); APPLY=1 would create one.")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

for ds, targets in sorted(TARGETS.items()):
    redivis.organization(OWNER).dataset(ds).create_next_version(if_not_exists=True)
    draft = redivis.organization(OWNER).dataset(ds, version="next")
    before = {t.name for t in draft.list_tables(max_results=2000)}
    if KEEP.get(ds, set()) - before:
        sys.exit(f"ABORT: keep set missing from the {ds} draft: {sorted(KEEP[ds] - before)}")
    todo = targets & before
    if not todo:
        print(f"{ds}: nothing to do, no target left in the draft.")
        continue
    for name in sorted(todo):
        draft.table(name).delete()
        print(f"{ds}: deleted {name}")
    after = names(ds, "next")
    assert before - after == todo, f"{ds}: MISMATCH removed={sorted(before - after)}, expected {sorted(todo)}"
    assert not (targets & after), f"{ds}: still in draft: {sorted(targets & after)}"
    assert KEEP.get(ds, set()) <= after, f"{ds}: keep went missing: {sorted(KEEP[ds] - after)}"

with LEDGER.open(newline="") as fh:
    logged = {r["table"] for r in csv.DictReader(fh) if r["script"].endswith(os.path.basename(__file__))}
for name in sorted(set(T) - logged):
    ds, reason, refs, rows, note = T[name]
    record({name}, dataset=ds, reason=reason, refs=refs, rows={name: rows}, note=note, script=__file__)
print(f"OK: {len(T)} target(s) withdrawn. The draft must be RELEASED to take effect.")
