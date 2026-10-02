"""Withdraw the 16 uruguay_2022_technology_* tables (INE Uruguay EUTIC 2022) from item_response_warehouse_2.

Not redistributable: INE's "Términos y condiciones" for the survey (ANDA catalog 736, read 2026-09-29) say "Los datos
y otros materiales proporcionados por el Instituto Nacional de Estadística (INE) no serán redistribuidos o vendidos a
otras personas, instituciones u organizaciones sin el consentimiento escrito del Instituto Nacional de Estadística."
No written consent was sought (#1390 said "they are open data"). The dictionary's Derived License "Custom: Public
Domain ... under Ley 16.616" misreads Ley 16.616, which is the statistical-secrecy law, not a licence. Ben
2026-09-29: pull; re-upload from data/uruguay_2022_technology.do if INE grants written consent.

KEEP: nothing else in the shard shares the prefix. No item text exists for these tables, so no irw_text shard is
touched.

Dry run by default. Set APPLY=1 to delete.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_uruguay_2022_technology")
import redivis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import record

OWNER   = "datapages"                  # metadata/redivis_config.R
DATASET = "item_response_warehouse_2"
PREFIX  = "uruguay_2022_technology_"
TARGETS = {PREFIX + s for s in ("access", "barriers", "communication", "devices", "entertainment", "govperception",
                                "govservices", "information", "ownership", "places", "safety", "skills",
                                "socialmedia", "streaming", "transactions", "work")}

apply = os.environ.get("APPLY") == "1"


def names(ds_name, version):
    return {t.name for t in redivis.organization(OWNER).dataset(ds_name, version=version).list_tables(max_results=2000)}


current = names(DATASET, "current")
found = {n for n in current if n.startswith(PREFIX)}
if found != TARGETS:
    sys.exit(f"ABORT: {PREFIX}* in {DATASET} current differs from TARGETS: "
             f"missing {sorted(TARGETS - found)}, extra {sorted(found - TARGETS)}")
KEEP = current - TARGETS

if not apply:
    try:
        before = names(DATASET, "next")
        print(f"DRY RUN: draft open, {len(before)} tables (current {len(current)}); "
              f"targets present: {len(TARGETS & before)}/16; keep missing: {sorted(KEEP - before)}; "
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

after = names(DATASET, "next")
removed = before - after
assert removed == TARGETS, f"MISMATCH: removed={sorted(removed)}"
assert KEEP <= after, f"went missing: {sorted(KEEP - after)}"
record(TARGETS, dataset=DATASET, reason="unlicensed", refs="#1390 #2064",
       note="INE Uruguay EUTIC 2022: terms bar redistribution without INE's written consent", script=__file__)
print(f"OK: removed exactly the 16 {PREFIX}* tables from {DATASET}; {len(KEEP)} other tables intact. "
      "Draft must be RELEASED to take effect.")
