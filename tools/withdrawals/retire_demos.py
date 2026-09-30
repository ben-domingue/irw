"""Retire DEMOS: its four "items" are per-stimulus means across raters, not responses (irw#2401).

Source: Zhang et al. (2023), Behavior Research Methods 55(5), 2353-2366,
10.3758/s13428-022-01887-4; OSF 83fst, DEMOS_data.xlsx (sha256 6a23fb5a...cf34e1,
downloaded 2026-09-29). Built by data/DEMOS.R.

The workbook has one row per VIDEO, not per person: 2,664 rows, one per `filename`
(F01H0V1_0.mp4, ...), with the actor, emotion, view and scenario of each clip and four
columns that are each already averaged over the raters who judged it: `accuracy_mean`
(share of raters who named the intended emotion, 0-1), `intensity_mean` and
`subj_move_mean` (mean 1-9 ratings) and `obj_move_mean` (a motion-energy measure,
120-1122, a different unit altogether). data/DEMOS.R keeps those four columns and sets
`id = filename`, so the live table (10,656 rows = 2,664 clips x 4) has stimuli as persons
and rater means as responses. Under datastandard.md's composite rule (a mean across raters
or trials is a composite, not a `resp`) nothing in it is an item response, and the
workbook holds no rater-level data to rebuild from. Re-checked 2026-09-29 against the
fresh download: 2,664 rows, 2,664 distinct filenames, the four *_mean columns as above.

Ben ruled 2026-09-29 (audit/2401/BATCH_1.md, B; RULES.md "Decisions, round 2"):
withdraw. Triage: audit/2401/triage/judgement.csv (resp_mixed_scale, DEMOS).

Target: item_response_warehouse, DEMOS (10,656 rows, v65_0). It has no item text in
irw_text or irw_text_2/_3 (checked 2026-09-29), so nothing else leaves with it.
KEEP: every other table in the shard; the script asserts the draft lost exactly DEMOS.

The itemtext/withdrawals.csv row was written BY HAND when this script was written
(released blank, note "staged, not yet applied"), as withdraw_iesr_translated.py did, so
do NOT call ledger.record() again when applying.

Published table: the deletion takes effect at the NEXT release; Ben publishes. Dry run
by default; APPLY=1 deletes from the draft.
"""
import os
import sys

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("retire_demos")
import redivis

OWNER = "datapages"  # metadata/redivis_config.R
DATASET = "item_response_warehouse"
TARGET = "DEMOS"
EXPECTED_ROWS = 10656  # measured 2026-09-29, v65_0
OTHER = ("item_response_warehouse_2", "item_response_warehouse_3", "item_response_warehouse_4",
         "item_response_warehouse_5", "item_response_warehouse_6")

apply = os.environ.get("APPLY") == "1"


def names(dataset, version):
    return {t.name for t in redivis.organization(OWNER).dataset(dataset, version=version)
            .list_tables(max_results=5000)}


def n_rows(version):
    q = f"SELECT COUNT(*) AS n FROM `{OWNER}.{DATASET}:{version}.{TARGET}`"
    return int(redivis.query(q).to_pandas_dataframe()["n"].iloc[0])


def open_draft():
    # The SDK indexes properties["nextVersion"] unconditionally, and the API omits the key
    # when no draft is open (the state right after a release).
    d = redivis.organization(OWNER).dataset(DATASET)
    d.get()
    d.properties.setdefault("nextVersion", None)
    d.create_next_version(if_not_exists=True)
    return redivis.organization(OWNER).dataset(DATASET, version="next")


# ---- scope checks, against `current`, before anything is touched -----------------------
current = names(DATASET, "current")
if TARGET not in current:
    sys.exit(f"ABORT: {TARGET} is not published in {DATASET}")
n = n_rows("current")
if n != EXPECTED_ROWS:
    sys.exit(f"ABORT: {TARGET} has {n:,} rows, expected {EXPECTED_ROWS:,}; re-measure first")
for other in OTHER:
    try:
        if TARGET in names(other, "current"):
            sys.exit(f"ABORT: {TARGET} also lives in {other}; scope is wrong")
    except Exception as exc:  # a shard that does not exist is not a clash
        print(f"  (skipped {other}: {type(exc).__name__})")
print(f"{DATASET}: {len(current)} published; {TARGET} live with {n:,} rows")

if not apply:
    try:
        draft = names(DATASET, "next")
        print(f"DRY RUN: draft open, {len(draft)} tables (current {len(current)}); "
              f"target in draft: {TARGET in draft}")
    except Exception as exc:
        print(f"DRY RUN: no draft open ({type(exc).__name__}); APPLY=1 creates one")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

# ---- apply ------------------------------------------------------------------------------
keep = current - {TARGET}
draft = open_draft()
before = {t.name for t in draft.list_tables(max_results=5000)}
if TARGET not in before:
    sys.exit(f"ABORT: {TARGET} not in the {DATASET} draft")
if keep - before:
    sys.exit(f"ABORT: draft is missing published tables: {sorted(keep - before)[:5]}")
draft.table(TARGET).delete()
print(f"deleted from {DATASET} draft: {TARGET}")
after = names(DATASET, "next")
assert before - after == {TARGET}, f"MISMATCH: removed={sorted(before - after)}"
assert keep <= after, f"went missing: {sorted(keep - after)}"
print(f"OK: exactly {TARGET} removed; {len(after)} left in the draft. The draft must be "
      "RELEASED to take effect. Ledger row already exists; do not call ledger.record().")
