"""Withdraw the 13 anunciacao_2025_personality_* tables from item_response_warehouse_2: they publish exact dates of
birth (irw#2835).

`data/anunciacao_2025_personality.do` renames the deposit's `nascimento` column to `cov_dob`; live, 18,659 distinct
birth dates sit beside cov_age, cov_institution and cov_profession (checked 2026-10-05 on _order). Same pattern as
ipq_doglioni_2021 in #2282, which was withdrawn and rebuilt with age only. The responses themselves are fine.
Found scope-checking the Anunciacao deposits for #2506.

NEEDS BEN: withdraw all 13 now (doglioni precedent), or strip cov_dob in place instead. Not applied.

KEEP: the other Anunciacao tables carry no date of birth (anunciacao_2025_emotional_*, anunciacao_2024_intelligence_gmi,
parenting_anunciacao_2025_*, and mbft_anunciacao_2024 on shard 1). development_delay_anunciacao_* go in
withdraw_wrongnow_2026_10_05.py (#2834). No item text exists for any target.

Its ledger rows are committed with this script; APPLY=1 adds them only if they are missing.

Dry run by default. Set APPLY=1 to delete. Resumable: a rerun deletes whatever targets remain in the draft.
"""
import csv, os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_anunciacao_personality_dob")
import redivis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import LEDGER, record

OWNER   = "datapages"                  # metadata/redivis_config.R
DATASET = "item_response_warehouse_2"
PREFIX  = "anunciacao_2025_personality_"
ROWS = {PREFIX + k: v for k, v in {
    "achievement": 2455605, "affiliation": 2455605, "aggression": 1364225, "autonomy": 2455605,
    "change": 1909915, "deference": 2455605, "dominance": 1909915, "exhibition": 2455605,
    "intraception": 1909915, "nurturance": 2182760, "order": 1637070, "persistence": 2182760,
    "succorance": 1909915}.items()}
TARGETS = set(ROWS)
KEEP = {"anunciacao_2025_emotional_management", "anunciacao_2024_intelligence_gmi",
        "parenting_anunciacao_2025_values"}
NOTE = "cov_dob: exact dates of birth beside age, institution and profession (the #2282 pattern)"

apply = os.environ.get("APPLY") == "1"


def names(version):
    return {t.name for t in redivis.organization(OWNER).dataset(DATASET, version=version).list_tables(max_results=2000)}


current = names("current")
if KEEP - current:
    sys.exit(f"ABORT: KEEP not in {DATASET} current: {sorted(KEEP - current)}")
if {n for n in current if n.startswith(PREFIX)} - TARGETS:
    sys.exit(f"ABORT: unexpected {PREFIX}* tables in current: {sorted({n for n in current if n.startswith(PREFIX)} - TARGETS)}")

if not apply:
    print(f"targets in current: {len(TARGETS & current)}/{len(TARGETS)}")
    try:
        before = names("next")
        print(f"DRY RUN: draft open, {len(before)} tables (current {len(current)}); "
              f"targets in draft: {len(TARGETS & before)}/{len(TARGETS)}; keep missing: {sorted(KEEP - before)}; "
              f"draft vs current names: +{sorted(before - current)} -{sorted(current - before)}")
    except Exception as exc:
        print(f"DRY RUN: no draft open ({type(exc).__name__}); APPLY=1 would create one.")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

ds = redivis.organization(OWNER).dataset(DATASET)
ds.create_next_version(if_not_exists=True)
draft = redivis.organization(OWNER).dataset(DATASET, version="next")
before = {t.name for t in draft.list_tables(max_results=2000)}
if KEEP - before:
    sys.exit(f"ABORT: keep set missing from draft: {sorted(KEEP - before)}")
todo = TARGETS & before
if not todo:
    sys.exit(f"Nothing to do: no {PREFIX}* target left in the {DATASET} draft.")
for name in sorted(todo):
    draft.table(name).delete()
    print("deleted:", name)

after = names("next")
assert before - after == todo, f"MISMATCH: removed={sorted(before - after)}, expected {sorted(todo)}"
assert not (TARGETS & after), f"still in draft: {sorted(TARGETS & after)}"
assert KEEP <= after, f"went missing: {sorted(KEEP - after)}"
with LEDGER.open(newline="") as fh:
    logged = {r["table"] for r in csv.DictReader(fh) if r["script"].endswith(os.path.basename(__file__))}
if TARGETS - logged:
    record(TARGETS - logged, dataset=DATASET, reason="personal_data", refs="#2835 #2282", rows=ROWS, note=NOTE,
           script=__file__)
print(f"OK: removed {len(TARGETS)} {PREFIX}* tables from {DATASET}. Draft must be RELEASED to take effect.")
