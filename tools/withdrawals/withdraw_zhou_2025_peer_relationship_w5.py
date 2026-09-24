"""Remove the misnamed `zhou_2025_peer_relationship` from item_response_warehouse_5 (irw#2149).

Two papers published a table under that name. The 14,892-student table in
item_response_warehouse_3 (Zhou N et al., pone.0330637) had it first and keeps
it. The 514-student table in item_response_warehouse_5 (Zhou X et al.,
pone.0320845) is re-uploaded as `zhou_2025_peer_relationship_inventory`, byte-for-
byte the same rows, and this deletes the old name from the _5 draft only.

Refuses to act unless the renamed table is already in the _5 draft, and asserts
the three sibling tables and the _3 copy are untouched.

Dry run by default. Set APPLY=1 to delete.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_zhou_2025_peer_relationship_w5")
import redivis

OWNER   = "datapages"          # metadata/redivis_config.R
DATASET = "item_response_warehouse_5"
TARGET  = "zhou_2025_peer_relationship"
KEEP    = {"zhou_2025_peer_relationship_inventory", "zhou_2025_social_support",
           "zhou_2025_exercise_self_efficacy", "zhou_2025_pa_intention"}
OTHER   = "item_response_warehouse_3"   # holds the pone.0330637 table under TARGET; must keep it

apply = os.environ.get("APPLY") == "1"

other = {t.name for t in redivis.organization(OWNER).dataset(OTHER, version="current").list_tables()}
if TARGET not in other:
    sys.exit(f"ABORT: {TARGET} is not in {OTHER}; the name would leave the corpus entirely")

def open_draft():
    ds = redivis.organization(OWNER).dataset(DATASET)
    ds.create_next_version(if_not_exists=True)
    return redivis.organization(OWNER).dataset(DATASET, version="next")

if not apply:
    try:
        draft = redivis.organization(OWNER).dataset(DATASET, version="next")
        before = {t.name for t in draft.list_tables()}
        print(f"DRY RUN: draft open, {len(before)} tables; target present: {TARGET in before}; "
              f"keep missing: {sorted(KEEP - before)}")
    except Exception as exc:
        print(f"DRY RUN: no draft open ({exc}); APPLY=1 would create one.")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

draft = open_draft()
before = {t.name for t in draft.list_tables()}
if TARGET not in before:
    sys.exit(f"ABORT: {TARGET} not in the {DATASET} draft")
if KEEP - before:
    sys.exit(f"ABORT: not in draft, upload first: {sorted(KEEP - before)}")

draft.table(TARGET).delete()
print("deleted:", TARGET)

after = {t.name for t in redivis.organization(OWNER).dataset(DATASET, version="next").list_tables()}
removed = before - after
assert removed == {TARGET}, f"MISMATCH: removed={removed}"
assert KEEP <= after, f"went missing: {KEEP - after}"
other_after = {t.name for t in redivis.organization(OWNER).dataset(OTHER, version="current").list_tables()}
assert TARGET in other_after, f"{TARGET} went missing from {OTHER}"
print(f"OK: only {TARGET} removed from {DATASET}; {OTHER} copy intact. Draft must be RELEASED to take effect.")
