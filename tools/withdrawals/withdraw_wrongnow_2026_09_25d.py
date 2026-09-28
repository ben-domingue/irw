"""Withdraw two tables whose item codes mean different questions in different studies, found in #2382 triage
(wave 7), 2026-09-25. Ben's standing rule (2026-09-24/25): withdraw at once, then rebuild.

item_response_warehouse_3
  alsuhibani_2022_gcbs   data/alsuhibani_2022_conspiracy_paranoia.py maps Study 2 GCBS1-15 and Study 3 GCBS01-15 onto
                         GCBS_01-15 by position, but Study 2's GCBS7 is a Princess Diana item and its GCBS8-15/17 are
                         canonical items 7-14/15. So GCBS_07-15 are shifted for Study 2. Live: items 1-6 agree across
                         studies (|dmean| <= .05); GCBS_07 1.76 vs 2.83; items 7-15 mean gap 0.34, 0.09 when shifted.
                         Item text (irw_text) is left live: it follows the canonical order the rebuild will use.
item_response_warehouse
  fcupanas_cffsdas_reyna_2018
                         data/fcupanas_cffsdas_reyna_2018.r stacks four studies on raw column names. Study 4 (athletes)
                         numbers items differently (11 = Temeroso, 12-20 = canonical 11-19), and shares the PANAS#
                         code family with Study 1, so PANAS11-20 mean different adjectives by study (e.g. PANAS20
                         4.33 vs 2.30; +.49 with positive affect vs +.64 with negative). Study 3's 7-point responses
                         are also cut by a 1-5 filter (1,138 values of 6-7 set to NA).

Dry run by default. Set APPLY=1 to delete. Asserts exactly TARGETS were removed from each draft.
"""


import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_wrongnow_2026_09_25d")
import redivis

OWNER = "datapages"
TARGETS = {"item_response_warehouse_3": {"alsuhibani_2022_gcbs"},
           "item_response_warehouse": {"fcupanas_cffsdas_reyna_2018"}}
MUST_STAY = {("item_response_warehouse_3", "alsuhibani_2022_loc"), ("item_response_warehouse_3", "alsuhibani_2022_gcbs_extra_s2")}

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
