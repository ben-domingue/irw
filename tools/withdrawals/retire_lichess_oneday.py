"""Retire the one-day `lichess` comp table, superseded by lichess_2013_* (irw#2634, PR #2635).

`lichess` (189,964 games, built by data/competitions/lichess.py from ayaan-gupta's
harvest script) holds a single day of Lichess play, 2017-01-31, so repeated pairings are
rematches and there is no network of players meeting each other -- useless for the
pairwise models the competition tables exist for. Its `homefield` is "N/A" although
agent_a is always White. The 2013 tables (bullet / blitz / classical, 3.38M games, CC0,
same source) replace it. Ben ruled 2026-10-01: retire it.

The ledger has no `superseded` reason, so the row uses `duplicate`, with a note saying it
is a supersession, not row-for-row duplicates.

Target: irw_competitions, `lichess`. KEEP: the three lichess_2013_* tables, which must
already be in the draft; the script asserts the draft lost exactly `lichess`.

Takes effect at the NEXT release; Ben publishes. Dry run by default; APPLY=1 deletes.
"""
import os, sys
from pathlib import Path
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("retire_lichess_oneday")
import redivis

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger import record

OWNER   = "datapages"          # metadata/redivis_config.R
DATASET = "irw_competitions"
TARGET  = "lichess"
KEEP    = {"lichess_2013_bullet", "lichess_2013_blitz", "lichess_2013_classical"}

apply = os.environ.get("APPLY") == "1"

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

ds = redivis.organization(OWNER).dataset(DATASET)
ds.create_next_version(if_not_exists=True)
draft = redivis.organization(OWNER).dataset(DATASET, version="next")
before = {t.name for t in draft.list_tables()}
if TARGET not in before:
    sys.exit(f"ABORT: {TARGET} not in the {DATASET} draft")
if KEEP - before:
    sys.exit(f"ABORT: successors not in draft, upload first: {sorted(KEEP - before)}")
n_rows = draft.table(TARGET).get().properties.get("numRows")

draft.table(TARGET).delete()
print("deleted:", TARGET)

after = {t.name for t in redivis.organization(OWNER).dataset(DATASET, version="next").list_tables()}
removed = before - after
assert removed == {TARGET}, f"MISMATCH: removed={removed}"
assert KEEP <= after, f"went missing: {KEEP - after}"

record([TARGET], dataset=DATASET, reason="duplicate", refs="#2634 #2635",
       rows={TARGET: n_rows} if n_rows else None,
       note="superseded, not row duplicates: one day (2017-01-31) of Lichess replaced by lichess_2013_bullet/_blitz/_classical (Ben 2026-10-01)",
       script=__file__)
print(f"OK: only {TARGET} removed from {DATASET}; ledger row written. Draft must be RELEASED to take effect.")
