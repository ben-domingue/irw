"""Withdraw matosaslopez_2024_teacher_assessment from item_response_warehouse_4 (irw#2559).

Its ten teacher-rating items look randomly generated, not answered: across 2,223 students the mean inter-item
r is 0.003 (max |r| 0.045, alpha 0.03), and responses are flat on 1-5 (4,397 / 4,547 / 4,497 / 4,402 / 4,387;
chi-square vs uniform p = 0.33), in both the Likert and BARS arms. Same author's 2022 BARS teacher items run
r = 0.58-0.73. The okeke2025 pattern (#2422). Ben 2026-09-29: withdraw it, keep the sibling.

KEEP: matosaslopez_2024_questionnaire_quality (same students; skewed, items correlate 0.24-0.55, so it looks
real). No item text exists for the target.

Its ledger rows are committed with this script; APPLY=1 adds them only if they are missing.

Dry run by default. Set APPLY=1 to delete.
"""
import csv, os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_matosaslopez_2024_teacher")
import redivis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import LEDGER, record

OWNER   = "datapages"                  # metadata/redivis_config.R
DATASET = "item_response_warehouse_4"
TARGETS = {"matosaslopez_2024_teacher_assessment"}
KEEP    = {"matosaslopez_2024_questionnaire_quality"}

apply = os.environ.get("APPLY") == "1"


def names(version):
    return {t.name for t in redivis.organization(OWNER).dataset(DATASET, version=version).list_tables(max_results=2000)}


current = names("current")
if TARGETS - current:
    sys.exit(f"ABORT: not in {DATASET} current: {sorted(TARGETS - current)}")
if KEEP - current:
    sys.exit(f"ABORT: sibling not in {DATASET} current: {sorted(KEEP - current)}")

if not apply:
    try:
        before = names("next")
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

after = names("next")
removed = before - after
assert removed == TARGETS, f"MISMATCH: removed={sorted(removed)}"
assert KEEP <= after, f"went missing: {sorted(KEEP - after)}"
with LEDGER.open(newline="") as fh:
    logged = {r["table"] for r in csv.DictReader(fh) if r["script"].endswith(os.path.basename(__file__))}
if TARGETS - logged:
    record(TARGETS - logged, dataset=DATASET, reason="wrong_data", refs="#2559", rows={"matosaslopez_2024_teacher_assessment": 22230},
           note="teacher items look simulated: uniform 1-5, mean inter-item r 0.003", script=__file__)
print(f"OK: removed exactly {sorted(TARGETS)} from {DATASET}; sibling intact. Draft must be RELEASED to take effect.")
