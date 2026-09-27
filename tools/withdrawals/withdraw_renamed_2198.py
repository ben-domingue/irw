"""Remove two misnamed tables from the item_response_warehouse_3 draft after their rename (irw#2198).

    wang_2026_teaching_presence    -> wang_2026_technology_perception
        The S1 Appendix heads the TP block "Technology Perception (TP)"; "teaching presence"
        appears nowhere in the article or appendix.
    weida_2020_financial_security  -> weida_2020_cesd10
        rowSums(secf_1m..secf_10m) equals the study's own dpsscore for all 371 respondents; the
        items are the CES-D-10.

Both renames were proposed in Ben's 2026-09-16 comment on #2198 ("independent, no cycle -- can
be done now"). The new names were uploaded to the _3 draft on 2026-09-27 from
data/wang_2026_efl_tam.py and data/weida_2020_financial_security.py, and each matches its live
table cell for cell (4,000 and 3,710 rows). Redivis cannot rename in place, so this deletes the
old names from the draft only, as withdraw_zhou_2025_peer_relationship_w5.py did for #2149.

Refuses to act unless each new name is already in the draft, and asserts the siblings survive.
Neither old name has item text (it was held out pending this rename), so irw_text is untouched.

Dry run by default. Set APPLY=1 to delete. The draft must be RELEASED to take effect.
"""
import os
import sys

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_renamed_2198")
import redivis

OWNER = "datapages"
SHARD = "item_response_warehouse_3"
RENAMES = {"wang_2026_teaching_presence": "wang_2026_technology_perception",
           "weida_2020_financial_security": "weida_2020_cesd10"}
TARGETS = set(RENAMES)
KEEP = set(RENAMES.values()) | {"wang_2026_perceived_usefulness", "wang_2026_technology_anxiety",
                                "wang_2026_attitude", "wang_2026_behavioral_intention"}


def names(v):
    return {t.name for t in redivis.organization(OWNER).dataset(SHARD, version=v).list_tables(max_results=2000)}


cur = names("current")
if TARGETS - cur:
    sys.exit(f"ABORT: not published in {SHARD}: {sorted(TARGETS - cur)}")
nxt = names("next")
if set(RENAMES.values()) - nxt:
    sys.exit(f"ABORT: new names not in the draft yet: {sorted(set(RENAMES.values()) - nxt)}")
print(f"{SHARD}: draft has {len(nxt)} tables; would delete {sorted(TARGETS)}")

if os.environ.get("APPLY") != "1":
    print("DRY RUN -- nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

draft = redivis.organization(OWNER).dataset(SHARD, version="next")
for name in sorted(TARGETS):
    draft.table(name).delete()
    print("deleted", name)
after = names("next")
assert nxt - after == TARGETS, f"removed {sorted(nxt - after)}"
assert KEEP <= after, f"keeper gone: {sorted(KEEP - after)}"
print(f"OK: draft {len(nxt)} -> {len(after)}; exactly the two old names removed.")
