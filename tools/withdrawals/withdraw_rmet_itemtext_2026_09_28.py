"""Withdraw the RMET item text of rmet_higgins_2022_rmet (irw#2513, D14).

Ben ruled 2026-09-28 ("rmet: withdraw"), in the #2513 decision walk-through: the
Autism Research Centre's terms cover the Reading the Mind in the Eyes Test itself,
and the live __items table reproduces it -- 148 rows, R01..R36 plus the practice item RPrac, 4 option words each
("thoughtful", "interested", "preoccupied", ...), the test instructions, and a
description of each eye image. ARC's downloadable-tests index lists "Eyes Test
(Adult)" and says: "You may not adapt or modify any of these tests, unless
permission has been given by the Autism Research Centre" -- the clause under
which rmet_higgins_2022_aq (AQ-28) was withdrawn (withdraw_aq28.py, irw#1955).
Higgins et al.'s permission (#641) covers their response data, not ARC's test,
so the RESPONSE table rmet_higgins_2022_rmet stays.

KEEP: rmet_higgins_2022_tom__items, the same study's Imposing Memory Task-style
cafeteria story (TOM01..), which is not an ARC test.

Whole-table withdrawal of one named table. Published, so it takes effect at the
NEXT irw_text release; Ben publishes. Dry run by default; APPLY=1 deletes from
the draft and asserts exactly TARGETS were removed and KEEP survived.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_rmet_itemtext_2026_09_28")
import redivis

OWNER = "datapages"
SHARD = "irw_text"
TARGETS = {"rmet_higgins_2022_rmet__items"}
KEEP = {"rmet_higgins_2022_tom__items"}

apply = os.environ.get("APPLY") == "1"


def names(v):
    return {t.name for t in redivis.organization(OWNER).dataset(SHARD, version=v).list_tables(max_results=2000)}


current = names("current")
if TARGETS - current:
    sys.exit(f"ABORT: not in {SHARD} current: {sorted(TARGETS - current)}")
if KEEP - current:
    sys.exit(f"ABORT: KEEP missing from {SHARD} current: {sorted(KEEP - current)}")

if not apply:
    try:
        print(f"DRY RUN {SHARD}: draft open ({len(names('next'))} tables); would delete {sorted(TARGETS)}")
    except Exception:
        print(f"DRY RUN {SHARD}: no draft; APPLY=1 creates one and deletes {sorted(TARGETS)}")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

redivis.organization(OWNER).dataset(SHARD).create_next_version(if_not_exists=True)
draft = redivis.organization(OWNER).dataset(SHARD, version="next")
before = {t.name for t in draft.list_tables(max_results=2000)}
if TARGETS - before:
    sys.exit(f"ABORT: not in the {SHARD} draft: {sorted(TARGETS - before)}")
for name in sorted(TARGETS):
    draft.table(name).delete()
after = names("next")
assert before - after == TARGETS, f"removed {sorted(before - after)}"
assert KEEP <= after, f"KEEP went missing: {sorted(KEEP - after)}"
print(f"OK {SHARD}: removed exactly {len(TARGETS)} ({len(before)} -> {len(after)}); KEEP intact")
print("The draft must be RELEASED to take effect.")
