"""Withdraw the eight item-text tables carrying `wording_rights` (irw#1955).

Each took its wording from an openly licensed deposit, but each instrument's
rights holder states a use restriction on their own page. Under the 2026-09-05
ruling (any stated use restriction blocks -- irw#1945) they do not ship. Ben
ruled on 2026-09-06 that all eight are withdrawn.

Deletes them from the `irw_text` DRAFT, so they leave at the next release.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_wording_rights")
import redivis

TARGETS = {
    "alsuhibani_2022_ecrs_s3__items",              # ECR-12, Fraley: no commercial use w/o permission
    "conspiracy_asd__asd_aq10__items",             # AQ-10, ARC Cambridge: research, not commercial
    "dominguez_2018_jcs__items",                   # UWES, Bakker: commercial use by permission
    "dpt_noncog__interpersonal_reactivity__items", # IRI, Davis: all non-commercial uses only
    "duboz_2021_pss10__items",                     # PSS-10, Cohen: profit-making needs permission + fee
    "esiason_2024_aaqii__items",                   # AAQ-II, ACBS/Bond: commercial users seek permission
    "EWAS_Sanford_2024_Flourish__items",           # Flourishing Scale, Diener: non-commercial only
    "extremera_2016_shs__items",                   # SHS, Lyubomirsky: permission for non-commercial use
}
# Sibling tables from the same studies that carry no restriction and MUST survive.
KEEP = {
    "conspiracy_asd__thinking_styles__items",
    "dpt_noncog__emotional_intelligence__items",
    "duboz_2021_swls__items",
    "esiason_2024_ace__items",
    "esiason_2024_cfq__items",
    "extremera_2016_swls__items",
    "extremera_2016_ei__items",
    "extremera_2016_sbq__items",
    "conner_2017_flourishing__items",
}

# Verify against what is PUBLISHED -- that is what has to leave. There is no
# `next` draft until this script (or an upload) makes one.
cur = redivis.user("datapages").dataset("irw_text", version="current")
published = {t.name for t in cur.list_tables()}
print("published tables (current):", len(published))
missing = TARGETS - published
if missing:
    sys.exit(f"ABORT: target not published: {sorted(missing)}")
print("targets present: all", len(TARGETS))
keep_pub = KEEP & published
print("keep-set present:", len(keep_pub), "of", len(KEEP))

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

# Creating the draft opens the release window (see the draft-release-window rule).
base = redivis.user("datapages").dataset("irw_text")
base.create_next_version(if_not_exists=True)
ds = redivis.user("datapages").dataset("irw_text", version="next")
before = {t.name for t in ds.list_tables()}
print("draft tables before:", len(before))
if TARGETS - before:
    sys.exit(f"ABORT: target not in draft: {sorted(TARGETS - before)}")
keep_before = KEEP & before

for name in sorted(TARGETS):
    ds.table(name).delete()
    print("deleted:", name)

after = {t.name for t in redivis.user("datapages").dataset("irw_text", version="next").list_tables()}
removed = before - after
print("\ndraft tables after:", len(after))
assert removed == TARGETS, f"MISMATCH: removed={sorted(removed)}"
assert KEEP & after == keep_before, "a keep-set table went missing"
assert len(after) == len(before) - len(TARGETS), "unexpected count change"
print(f"OK: exactly the {len(TARGETS)} targets removed; keep-set intact.")
