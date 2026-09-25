"""Withdraw tables serving wrong data, found in #2381 item-text triage (Ben 2026-09-25: "withdraw the existing tables
and open these with issues ... at least not serve bad data now").

item_response_warehouse_2
  dass21_depression_anxiety_stress   duplicate of falih_2026_dass21 (_3): same author, same 262 respondents, 5,500/5,502
                                     responses equal; the 2 that differ are out-of-range 4s here (3 in falih).
                                     NOTE: it carries covariates falih lacks (caffeine, education, income, weekly hours).
  okeke2025_* (10)                   near-zero inter-item correlations across all 32 deposit items (mean |r| 0.06,
                                     n=200): no scale has internal consistency; reads as simulated responses.
  sun_2025_morality_study3_* (17)    every it.* value in study3-maindat.csv is a per-target MEAN across informants,
                                     rounded by data/sun_2025_morality.do (`replace resp = round(resp)`; 35.8% of
                                     adjective cells were non-integer); itkindness/itintegrity are composites. All 17
                                     study-3 tables contain it.* items (meaning, pemotion, nemotion, costofmorality mix
                                     them with self-report items).
  ren2019_scpv, ren_2019_scpv        a duplicate pair whose dictionary description names a different instrument.
item_response_warehouse_3
  qiang_2025_surface_acting          table name / description misname the instrument (Step 3b instrument mismatch).
irw_text
  sun_2025_morality_study3_{benevolence,dependability,honesty,loyalty}__items   item text for withdrawn tables.

Dry run by default. Set APPLY=1 to delete. Each dataset: asserts exactly TARGETS were removed from its draft.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_wrongnow_2026_09_25")
import redivis

OWNER = "datapages"
SUN3 = ["benevolence", "compassion", "costofmorality", "dependability", "extraversion", "fairnessHEXACO",
        "fairnessMCQ", "generalmorality", "honesty", "loyalty", "meaning", "moralratings", "nemotion",
        "neuroticism", "openness", "pemotion", "respectfulness"]
OKEKE = ["adaptability", "ai_usefulness_post", "ai_usefulness_pre", "cognitive_agility_post", "cognitive_agility_pre",
         "decision_accuracy", "decision_confidence_post", "decision_confidence_pre", "response_time", "risk_mitigation"]
TARGETS = {
    "item_response_warehouse_2": {"dass21_depression_anxiety_stress", "ren2019_scpv", "ren_2019_scpv"}
        | {f"okeke2025_{s}" for s in OKEKE} | {f"sun_2025_morality_study3_{s}" for s in SUN3},
    "item_response_warehouse_3": {"qiang_2025_surface_acting"},
    "irw_text": {f"sun_2025_morality_study3_{s}__items" for s in ("benevolence", "dependability", "honesty", "loyalty")},
}
MUST_STAY = {("item_response_warehouse_3", "falih_2026_dass21"), ("irw_text", "falih_2026_dass21__items")}

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
