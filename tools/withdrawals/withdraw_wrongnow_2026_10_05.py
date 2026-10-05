"""Withdraw eleven response tables serving wrong data, found checking the #2506 table-defect leads (2026-10-05).

Standing wrong-now rule (Ben 2026-09-24/25): a table found serving wrong data is withdrawn now and rebuilt later.
Each group has its own issue with the evidence; the ingestion issue is reopened where one exists.

item_response_warehouse
  PeSCBCSCe_Novak_2020_SPIRIT              #2836  a byte-for-byte copy of _SCBCS: the script writes SCBCS_df to the
                                                  SPIRIT file. KEEP PeSCBCSCe_Novak_2020_SCBCS (correct).
item_response_warehouse_2
  development_delay_anunciacao_asqse       #2834  asqseK / conK mean a different ASQ:SE-2 item at each of 9 age
  development_delay_anunciacao_concerns           intervals; non-administered items are filled with 0 (228,106 of
                                                  1,003,587 asqse rows); also child DOB, initials, ZIP, free text.
  xue_2024_study3_cfa                      #2837  empty SPSS value labels read as missing: every 2-6 answer dropped
                                                  (69.6% of valid answers), only 1 and 7 survive.
                                                  KEEP xue_2024_study2_efa, xue_2024_full_dataset.
  chen2026_mpa, chen2026_sa, chen2026_sc   #2838  duplicates of chen_2026_mobile_phone_addiction / _social_anxiety /
                                                  _self_control (item_response_warehouse_4), same Dataverse file.
  lsbq_maleki_2025_dominant_language_home_community, lsbq_maleki_2025_non_persian_use
                                           #2839  every "all Persian" answer dropped (scale_map key typo).
                                                  KEEP _persian_comprehension, _non_persian_proficiency, _persian_switching.
  chen2022_sasc                            #2841  10 SASC items plus 4 non-SASC items (A45-A48) under one name.
                                                  KEEP chen2022_cls, chen2022_ses.
item_response_warehouse_3
  yu_2015_family_environment               #2840  misnamed: its 21 items are the BDI, not the Family Environment Scale.

No item text exists for any target (checked in irw_text, irw_text_2, irw_text_3).

Its ledger rows are committed with this script; APPLY=1 adds them only if they are missing.

Dry run by default. Set APPLY=1 to delete. Resumable: a rerun deletes whatever targets remain in each draft (a
concurrent upload can re-create a withdrawn table; rerun after other sessions' uploads, before the release).
"""
import csv, os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_wrongnow_2026_10_05")
import redivis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import LEDGER, record

OWNER = "datapages"                    # metadata/redivis_config.R

# table -> (dataset, reason, refs, rows at withdrawal, note)
T = {
    "PeSCBCSCe_Novak_2020_SPIRIT": ("item_response_warehouse", "wrong_data", "#2836 #245", 2860,
        "copy of PeSCBCSCe_Novak_2020_SCBCS: script writes SCBCS_df to the SPIRIT file"),
    "development_delay_anunciacao_asqse": ("item_response_warehouse_2", "wrong_data", "#2834 #1386", 1003587,
        "item codes mean different ASQ:SE-2 items per age interval; non-administered items filled with 0; also personal data"),
    "development_delay_anunciacao_concerns": ("item_response_warehouse_2", "wrong_data", "#2834 #1386", 1003587,
        "item codes mean different ASQ:SE-2 items per age interval; non-administered items filled with 0; also personal data"),
    "xue_2024_study3_cfa": ("item_response_warehouse_2", "wrong_data", "#2837 #306", 53641,
        "empty SPSS value labels read as missing: every 2-6 answer dropped, only 1 and 7 survive"),
    "chen2026_mpa": ("item_response_warehouse_2", "duplicate", "#2838", 3900,
        "duplicate of chen_2026_mobile_phone_addiction (item_response_warehouse_4), same Dataverse file"),
    "chen2026_sa": ("item_response_warehouse_2", "duplicate", "#2838", 2145,
        "duplicate of chen_2026_social_anxiety (item_response_warehouse_4), same Dataverse file"),
    "chen2026_sc": ("item_response_warehouse_2", "duplicate", "#2838", 3705,
        "duplicate of chen_2026_self_control (item_response_warehouse_4), same Dataverse file"),
    "lsbq_maleki_2025_dominant_language_home_community": ("item_response_warehouse_2", "wrong_data", "#2839 #1297", 3031,
        "every 'all Persian' answer dropped (scale_map key typo)"),
    "lsbq_maleki_2025_non_persian_use": ("item_response_warehouse_2", "wrong_data", "#2839 #1297", 1764,
        "every 'all Persian' answer dropped (scale_map key typo); 17.2.* items missing"),
    "chen2022_sasc": ("item_response_warehouse_2", "wrong_data", "#2841", 4242,
        "10 SASC items plus 4 non-SASC items (A45-A48) under one name"),
    "yu_2015_family_environment": ("item_response_warehouse_3", "misnamed", "#2840", 96222,
        "items are the 21 BDI items, not the Family Environment Scale"),
}
KEEP = {
    "item_response_warehouse": {"PeSCBCSCe_Novak_2020_SCBCS"},
    "item_response_warehouse_2": {"xue_2024_study2_efa", "xue_2024_full_dataset",
                                  "lsbq_maleki_2025_persian_comprehension", "lsbq_maleki_2025_non_persian_proficiency",
                                  "lsbq_maleki_2025_persian_switching", "chen2022_cls", "chen2022_ses"},
    "item_response_warehouse_4": {"chen_2026_mobile_phone_addiction", "chen_2026_social_anxiety",
                                  "chen_2026_self_control"},
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
for ds, keep in KEEP.items():
    if ds not in TARGETS:
        assert keep <= names(ds, "current"), f"{ds}: keep went missing from current"

with LEDGER.open(newline="") as fh:
    logged = {r["table"] for r in csv.DictReader(fh) if r["script"].endswith(os.path.basename(__file__))}
for name in sorted(set(T) - logged):
    ds, reason, refs, rows, note = T[name]
    record({name}, dataset=ds, reason=reason, refs=refs, rows={name: rows}, note=note, script=__file__)
print(f"OK: {len(T)} targets withdrawn across {len(TARGETS)} drafts. Drafts must be RELEASED to take effect.")
