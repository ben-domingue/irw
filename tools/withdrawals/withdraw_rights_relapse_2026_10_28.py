"""A rights-withdrawn item-text table is still live. Withdraw it a second time.

Found 2026-10-28 while closing out #3224: the release gate's `withdrawals-records`
check flagged `FomoNegativeAffect_cremer_2026_panas` as still described by
`itemtext_metadata`, and the reason it was still described is that its item text
is still SERVED.

  FomoNegativeAffect_cremer_2026_panas__items  irw_text_3  PANAS
      Ledger: withdrawn 2026-10-16, rights, register block, #3017 sweep.
      `withdraw_block_register_2026_10_16.py` writes its ledger row only AFTER a
      successful delete and an assertion that the name is gone from the draft, so
      the delete did happen. The table is nevertheless present in EVERY released
      version of irw_text_3 (v1.4 .. v7.3) and in the current draft, so that
      draft never reached a release carrying the deletion.

This is not a bookkeeping artefact: it is instrument wording that a register
verdict says IRW may not distribute, being distributed right now.

A first pass of this script also targeted `WMD_bartczuk_2023__items`, which is
likewise in the ledger as a rights withdrawal and likewise live. It was WRONG to
include: that row carries `reinstated: 2026-10-27` -- Fida, the WMDS originator,
granted the wording by email on 2026-10-26, so the table was deliberately
re-uploaded and is correctly live. The ad-hoc cross-check that found it did not
apply the `reinstated` filter that `check_release_consistency.py` applies for
exactly this reason. Read that column before calling a live withdrawal a defect.

The table already has a ledger row, and this appends another rather than editing
it. A second withdrawal IS a second event, and the ledger is append-only.

Dry-run by default; re-run with APPLY=1 to delete from each shard's draft.
Published tables leave the warehouse at the NEXT release, which Ben publishes.
Note that irw_text_3's draft currently holds 9 unrelated added tables from
another session, so releasing it ships those too -- check
`python3 -m red_up.drafts --dataset irw_text_3 --verbose` before publishing.
"""
import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token(
    "withdraw_rights_relapse_2026_10_28")
import redivis
from ledger import record

LOCAL = Path("/home/ben/Dropbox/projects/irw/data/itemtext")

#: table -> (shard, register family, why it is live again)
TARGETS = {
    "FomoNegativeAffect_cremer_2026_panas__items": (
        "irw_text_3", "PANAS",
        "delete ran on the draft 2026-10-16 but no release ever carried it; "
        "present in every version v1.4-v7.3 and in the draft"),
}
assert len(TARGETS) == 1

by_shard: dict[str, set[str]] = {}
for table, (shard, _, _) in TARGETS.items():
    by_shard.setdefault(shard, set()).add(table)

# ---------------------------------------------------------------------------
# 1. The premise: each target is in the CURRENT release of its shard.
# ---------------------------------------------------------------------------
for shard, targets in by_shard.items():
    cur = redivis.user("datapages").dataset(shard, version="current")
    names = {t.name for t in cur.list_tables()}
    if len(names) < 100:
        sys.exit(f"ABORT: {shard} listed {len(names)} tables; treating as a "
                 "failed listing rather than an empty shard")
    missing = targets - names
    if missing:
        sys.exit(f"ABORT: not in the current release of {shard}: {sorted(missing)} "
                 "-- the relapse may already have been fixed; re-read the ledger")
    print(f"{shard}: {len(names)} published tables, {len(targets)} target(s) present")

# ---------------------------------------------------------------------------
# 2. A local copy BEFORE any delete (Ben's standing rule, 2026-10-15).
#
# The file is already in the store under a name with no `.csv` suffix at all,
# so the copy is re-made under the canonical name rather than trusted.
# ---------------------------------------------------------------------------
LOCAL.mkdir(parents=True, exist_ok=True)
rows_at: dict[str, int] = {}
for shard, targets in by_shard.items():
    cur = redivis.user("datapages").dataset(shard, version="current")
    for name in sorted(targets):
        dest = LOCAL / f"{name}.csv"
        if not dest.exists() or dest.stat().st_size == 0:
            cur.table(name).download(str(dest), overwrite=True)
        with dest.open(newline="", encoding="utf-8") as fh:
            n = sum(1 for _ in csv.reader(fh)) - 1
        live_n = cur.table(name).get().properties["numRows"]
        if n <= 0 or n != live_n:
            sys.exit(f"ABORT: local copy {dest} has {n} rows, live has {live_n}")
        rows_at[name] = n
        print(f"  local copy OK {dest.name}: {n} rows")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- premise confirmed and local copies verified. "
          "Nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

# ---------------------------------------------------------------------------
# 3. Delete from the draft, assert exactly the targets went, record the event.
# ---------------------------------------------------------------------------
for shard, targets in by_shard.items():
    base = redivis.user("datapages").dataset(shard)
    base.create_next_version(if_not_exists=True)
    ds = redivis.user("datapages").dataset(shard, version="next")
    before = {t.name for t in ds.list_tables()}
    todo = targets & before
    print(f"\n{shard} draft tables before: {len(before)}; to delete: {len(todo)}")
    for name in sorted(todo):
        ds.table(name).delete()
        print("deleted:", name)
    after = {t.name for t in
             redivis.user("datapages").dataset(shard, version="next").list_tables()}
    assert before - after == todo, f"MISMATCH in {shard}: {sorted(before - after)}"
    assert not (targets & after), f"target still in {shard} draft"
    print(f"OK: {shard} draft now {len(after)} tables, no target remains.")
    for name in sorted(todo):
        _, family, why = TARGETS[name]
        record([name], dataset=shard, reason="rights", family=family,
               refs="relapse of the #3017 register block; found by the #3224 gate run",
               rows={name: rows_at[name]},
               note=f"second withdrawal -- {why}; local copy in data/itemtext",
               script=__file__)
print("\nledger rows written to itemtext/withdrawals.csv")
print("NOT released. Publish each shard by hand, then the itemtext_metadata rows "
      "drop out on the next stage-08 run.")
