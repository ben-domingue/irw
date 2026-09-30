"""Withdraw the seven moral_absolutism_goyal_2025_* tables from item_response_warehouse_2 (irw#2563).

The build appends the trial/issue column to `id`, and the survey export repeats each person's answers on every
trial row, so each respondent appears as several ids with identical responses: x6 in Study 6 (mfq, pp, dt, mr,
nfc, stance), x11 in Study 5 and x6 in Study 7 (moral), x6 in Studies 7-8 (stance). 405 real respondents are served
as 2,430 in four of the tables. _stance also maps "neither" and "support" both to 4. Verified live 2026-09-30.
Reported by batch_517 (2026-09-26). Standing wrong-now rule: withdraw now, rebuild later.

KEEP: nothing else in the deposit (all seven go). No item text exists for any of them (blocked on the NC question).

Its ledger rows are committed with this script; APPLY=1 adds them only if they are missing.

Dry run by default. Set APPLY=1 to delete.
"""
import csv, os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_goyal_2025")
import redivis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import LEDGER, record

OWNER   = "datapages"                  # metadata/redivis_config.R
DATASET = "item_response_warehouse_2"
PREFIX  = "moral_absolutism_goyal_2025_"
TARGETS = {PREFIX + s for s in ("dt", "mfq", "moral", "mr", "nfc", "pp", "stance")}
ROWS    = {PREFIX + "dt": 7290, PREFIX + "mfq": 36450, PREFIX + "moral": 44619, PREFIX + "mr": 21870,
           PREFIX + "nfc": 45280, PREFIX + "pp": 26730, PREFIX + "stance": 34860}
NOTE    = "respondents duplicated up to 11x across trial rows (id + trial); _stance codes neither = support"

apply = os.environ.get("APPLY") == "1"


def names(version):
    return {t.name for t in redivis.organization(OWNER).dataset(DATASET, version=version).list_tables(max_results=2000)}


current = names("current")
if TARGETS - current:
    sys.exit(f"ABORT: not in {DATASET} current: {sorted(TARGETS - current)}")
if {n for n in current if n.startswith(PREFIX)} != TARGETS:
    sys.exit(f"ABORT: unexpected {PREFIX}* tables in current: {sorted(n for n in current if n.startswith(PREFIX))}")

if not apply:
    try:
        before = names("next")
        print(f"DRY RUN: draft open, {len(before)} tables (current {len(current)}); "
              f"targets present: {len(TARGETS & before)}/7; "
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

for name in sorted(TARGETS):
    draft.table(name).delete()
    print("deleted:", name)

after = names("next")
removed = before - after
assert removed == TARGETS, f"MISMATCH: removed={sorted(removed)}"
with LEDGER.open(newline="") as fh:
    logged = {r["table"] for r in csv.DictReader(fh) if r["script"].endswith(os.path.basename(__file__))}
if TARGETS - logged:
    record(TARGETS - logged, dataset=DATASET, reason="wrong_data", refs="#2563", rows=ROWS, note=NOTE, script=__file__)
print(f"OK: removed exactly {len(TARGETS)} tables from {DATASET}. Draft must be RELEASED to take effect.")
