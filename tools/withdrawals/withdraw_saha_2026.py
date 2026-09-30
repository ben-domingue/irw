"""Withdraw saha_2026_cesd (item_response_warehouse_5) and its item text (irw_text_3) (irw#2565).

The source deposit, Mendeley Data 10.17632/c5gpdtj8jv (CC BY 4.0), was removed "as per author's request" (API 451,
then 404 by 2026-09-30). CC BY is irrevocable, so keeping is lawful, but the reason is unknown and this is student
mental-health data. Ben 2026-09-30: withdraw both, ask the author, restore on a clear yes.

KEEP: nothing else is touched; each dataset loses exactly its one target.

Its ledger rows are committed with this script; APPLY=1 adds them only if they are missing.

Dry run by default. Set APPLY=1 to delete.
"""
import csv, os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_saha_2026")
import redivis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import LEDGER, record

OWNER   = "datapages"                  # metadata/redivis_config.R
TARGETS = {"item_response_warehouse_5": "saha_2026_cesd",
           "irw_text_3": "saha_2026_cesd__items"}
ROWS    = {"saha_2026_cesd": 17840, "saha_2026_cesd__items": 80}
NOTE    = "source deposit removed at the author's request (Mendeley 10.17632/c5gpdtj8jv); author to be asked"

apply = os.environ.get("APPLY") == "1"


def names(ds, version):
    return {t.name for t in redivis.organization(OWNER).dataset(ds, version=version).list_tables(max_results=2000)}


for ds, t in TARGETS.items():
    if t not in names(ds, "current"):
        sys.exit(f"ABORT: {t} not in {ds} current")

if not apply:
    for ds, t in TARGETS.items():
        try:
            nxt, cur = names(ds, "next"), names(ds, "current")
            print(f"DRY RUN {ds}: draft open, {len(nxt)} tables (current {len(cur)}); target present: {t in nxt}; "
                  f"draft vs current names: +{sorted(nxt - cur)} -{sorted(cur - nxt)}")
        except Exception as exc:
            print(f"DRY RUN {ds}: no draft open ({type(exc).__name__}); APPLY=1 would create one.")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

with LEDGER.open(newline="") as fh:
    logged = {r["table"] for r in csv.DictReader(fh) if r["script"].endswith(os.path.basename(__file__))}

for ds, t in TARGETS.items():
    redivis.organization(OWNER).dataset(ds).create_next_version(if_not_exists=True)
    draft = redivis.organization(OWNER).dataset(ds, version="next")
    before = {x.name for x in draft.list_tables(max_results=2000)}
    if t not in before:
        sys.exit(f"ABORT: {t} not in the {ds} draft")
    draft.table(t).delete()
    removed = before - names(ds, "next")
    assert removed == {t}, f"MISMATCH in {ds}: removed={sorted(removed)}"
    print(f"deleted: {ds}.{t}")
    if t not in logged:
        record([t], dataset=ds, reason="source_withdrawn", refs="#2565", rows=ROWS, note=NOTE, script=__file__)
print("OK: both removed. Release item_response_warehouse_5 and irw_text_3 to take effect.")
