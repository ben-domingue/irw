"""Retire wellbeing_kocar_2025 from item_response_warehouse_2: split into three tables (irw#2848).

The table held three instruments for the same 669 students under one well-being-scale
name: swb1-19 (1-7, the Student Well-Being Scale in Higher Education), ls1-5 (1-5,
life satisfaction) and wb1-14 (1-5, well-being). data/wellbeing_kocar_2025.R now builds
wellbeing_kocar_2025_swb, _ls and _wb, uploaded to the same draft first (2026-10-05,
row-count verified); every response is unchanged. 25,422 rows. No item text exists.

KEEP: the three replacements must already be in the draft.

Dry run by default. Set APPLY=1 to delete from the draft; the deletion takes effect at
the next release, which is Ben's.
"""
import csv, os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("retire_wellbeing_kocar_2025")
import redivis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import LEDGER, record

OWNER   = "datapages"                  # metadata/redivis_config.R
DATASET = "item_response_warehouse_2"
TARGETS = {"wellbeing_kocar_2025"}
KEEP    = {"wellbeing_kocar_2025_swb", "wellbeing_kocar_2025_ls", "wellbeing_kocar_2025_wb"}

apply = os.environ.get("APPLY") == "1"


def names(version):
    return {t.name for t in redivis.organization(OWNER).dataset(DATASET, version=version).list_tables(max_results=2000)}


current = names("current")
if TARGETS - current:
    sys.exit(f"ABORT: not in {DATASET} current: {sorted(TARGETS - current)}")

before = names("next")
if KEEP - before:
    sys.exit(f"ABORT: replacements not yet in the draft: {sorted(KEEP - before)}")

if not apply:
    print(f"DRY RUN: draft {len(before)} tables (current {len(current)}); "
          f"targets present: {sorted(TARGETS & before)}; replacements present: {sorted(KEEP & before)}")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

draft = redivis.organization(OWNER).dataset(DATASET, version="next")
if TARGETS - before:
    sys.exit(f"Nothing to do: already gone from the {DATASET} draft: {sorted(TARGETS - before)}")
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
    record(TARGETS - logged, dataset=DATASET, reason="misnamed", refs="#2848", rows={"wellbeing_kocar_2025": 25422},
           note="three instruments under one name; split into wellbeing_kocar_2025_swb/_ls/_wb", script=__file__)
print(f"OK: removed exactly {sorted(TARGETS)} from {DATASET}; replacements intact. Draft must be RELEASED to take effect.")
