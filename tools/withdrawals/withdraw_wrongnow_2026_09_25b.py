"""Withdraw tables serving wrong data, found in #2382 item-text triage (wave 6), 2026-09-25.
Ben's standing rule (2026-09-24/25): a table found serving wrong data is withdrawn at once, then rebuilt.

item_response_warehouse
  MEFSIRODGAS_Nileksela_2023_freq    data/MEFSIRODGAS_Nileksela_2023.R writes severity_df to BOTH _freq.csv and
                                     _severity.csv. The live _freq and _severity tables are identical (45,409 rows,
                                     499 ids, 91 items, same id/item/resp). The 499 ids are the Severity group (the
                                     Frequency group has 501), so _severity is right and _freq holds severity data.
  paampsmartsud_saba_2023_{ffmq,pss,ders,pacs}
                                     data/paampsmartsud_saba_2023.r builds every *_BASELINE_df from the *_POST columns,
                                     so wave 0 and wave 1 are the same post-treatment responses (verified live: the
                                     id/item/resp rows of the two waves are identical in all four tables). _amps (4
                                     distinct waves) and _attendance (no waves) are unaffected and stay.

Item text for ders/ffmq/pacs is NOT withdrawn: the wording is correct and the rebuilt tables reuse it.
Dry run by default. Set APPLY=1 to delete. Asserts exactly TARGETS were removed from the draft.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_wrongnow_2026_09_25b")
import redivis

OWNER = "datapages"
TARGETS = {
    "item_response_warehouse": {"MEFSIRODGAS_Nileksela_2023_freq"}
        | {f"paampsmartsud_saba_2023_{s}" for s in ("ffmq", "pss", "ders", "pacs")},
}
MUST_STAY = {("item_response_warehouse", "MEFSIRODGAS_Nileksela_2023_severity"),
             ("item_response_warehouse", "paampsmartsud_saba_2023_amps"),
             ("item_response_warehouse", "paampsmartsud_saba_2023_attendance")}

apply = os.environ.get("APPLY") == "1"


def names(ds, v):
    return {t.name for t in redivis.organization(OWNER).dataset(ds, version=v).list_tables(max_results=2000)}


for ds, targets in TARGETS.items():
    cur = names(ds, "current")
    missing = targets - cur
    if missing:
        sys.exit(f"ABORT: not in {ds} current: {sorted(missing)}")
for ds, t in MUST_STAY:
    if t not in names(ds, "current"):
        sys.exit(f"ABORT: {t} missing from {ds} current")

if not apply:
    for ds, targets in TARGETS.items():
        try:
            nxt = names(ds, "next")
            print(f"DRY RUN {ds}: draft open ({len(nxt)} tables); would delete {len(targets)}")
        except Exception:
            print(f"DRY RUN {ds}: no draft; APPLY=1 creates one and deletes {len(targets)}")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

for ds, targets in TARGETS.items():
    redivis.organization(OWNER).dataset(ds).create_next_version(if_not_exists=True)
    draft = redivis.organization(OWNER).dataset(ds, version="next")
    before = {t.name for t in draft.list_tables(max_results=2000)}
    if targets - before:
        sys.exit(f"ABORT: not in the {ds} draft: {sorted(targets - before)}")
    for name in sorted(targets):
        draft.table(name).delete()
    after = names(ds, "next")
    assert before - after == targets, f"{ds}: removed {sorted(before - after)}"
    print(f"OK {ds}: removed exactly {len(targets)}")
for ds, t in MUST_STAY:
    assert t in names(ds, "next"), f"{t} went missing from {ds}"
print("Drafts must be RELEASED to take effect.")
