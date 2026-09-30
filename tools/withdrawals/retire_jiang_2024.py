"""Retire the 21 jiang_2024_* tables, and their 6 item-text tables (irw#2401).

Source: Jiang et al. (2024), PLOS ONE 10.1371/journal.pone.0312338, S1 Data
(journal.pone.0312338.s001.sav), built by data/jiang_2024_student_thriving.py.

The S1 file has 1,792 rows but only 707 distinct response vectors: rows k, k+707 and
k+1414 carry identical item responses and identical `totalseconds`, while Gender and Age
differ between the copies (in 252-357 of the 707 `index` values, per scale). The paper
reports N=1,792. Re-checked 2026-09-29 against a fresh download of the .sav: 1,792 x 128,
707 distinct vectors once `index`/Gender/Age are set aside, and the three blocks equal at
offsets 0, 707 and 1414. Live, every table has 707 ids and 1,792 x n_items rows
(metadata/metadata.csv), so each respondent is in IRW about 2.5 times.

A dedupe would leave 707 people with conflicting demographics and a sample the paper
does not describe. Ben ruled 2026-09-29 (audit/2401/RULES.md, "Decisions, round 2"):
withdraw the family. triage: audit/2401/triage/dup_exact.csv.

Targets
  item_response_warehouse_3  the 21 jiang_2024_* response tables (TARGETS below)
  irw_text                   jiang_2024_{ptsexp,ptsinv,ptspr}__items
  irw_text_2                 jiang_2024_{growthm,instituinteg,ptsacc}__items
(item-text shards from itemtext/live_tables.csv, refreshed 2026-09-29, #2549). Item text
for a withdrawn table has nothing to join to, so it leaves in the same pass.

KEEP: jiang_2025_* and every other table in each shard. The script asserts the jiang_2024_
prefix in each shard's `current` is exactly its target set, so a sibling added since the
ruling stops it rather than riding along.

The itemtext/withdrawals.csv rows were written BY HAND when this script was committed
(released blank, note "staged, not yet applied"), as withdraw_iesr_translated.py did, so
do NOT call ledger.record() again when applying.

Published tables: the deletions take effect at the NEXT release of each dataset; Ben
publishes. Dry run by default; APPLY=1 deletes from the drafts.
"""
import os
import sys

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("retire_jiang_2024")
import redivis

OWNER = "datapages"  # metadata/redivis_config.R
PREFIX = "jiang_2024_"

SCALES = ("ciacadec", "ciactivel", "cienrichex", "cistudsi", "cisuppenv", "commitsw",
          "growthm", "instituinteg", "institutionr", "psychosc", "ptsacc", "ptsexp",
          "ptsinv", "ptspr", "sensewb", "spiritua", "thracademd", "thrdiversc",
          "threngagel", "thrpositivep", "thrsocialc")
assert len(SCALES) == 21

TARGETS = {
    "item_response_warehouse_3": {PREFIX + s for s in SCALES},
    "irw_text": {f"{PREFIX}{s}__items" for s in ("ptsexp", "ptsinv", "ptspr")},
    "irw_text_2": {f"{PREFIX}{s}__items" for s in ("growthm", "instituinteg", "ptsacc")},
}
#: Other shards checked so a copy elsewhere is caught rather than left behind.
OTHER = ("item_response_warehouse", "item_response_warehouse_2", "item_response_warehouse_4",
         "item_response_warehouse_5", "item_response_warehouse_6", "irw_text_3")

apply = os.environ.get("APPLY") == "1"


def names(dataset, version):
    return {t.name for t in redivis.organization(OWNER).dataset(dataset, version=version)
            .list_tables(max_results=5000)}


def open_draft(dataset):
    # The SDK indexes properties["nextVersion"] unconditionally, and the API omits the key
    # when no draft is open (the state right after a release).
    d = redivis.organization(OWNER).dataset(dataset)
    d.get()
    d.properties.setdefault("nextVersion", None)
    d.create_next_version(if_not_exists=True)
    return redivis.organization(OWNER).dataset(dataset, version="next")


# ---- scope checks, all against `current`, before anything is touched -------------------
current = {}
for dataset, targets in TARGETS.items():
    cur = names(dataset, "current")
    found = {n for n in cur if n.startswith(PREFIX)}
    if found != targets:
        sys.exit(f"ABORT: {PREFIX}* in {dataset} current differs from TARGETS: "
                 f"missing {sorted(targets - found)}, extra {sorted(found - targets)}")
    current[dataset] = cur
    print(f"{dataset}: {len(cur)} published; {len(targets)} targets present")

for other in OTHER:
    try:
        clash = {n for n in names(other, "current") if n.startswith(PREFIX)}
    except Exception as exc:  # a shard that does not exist is not a clash
        print(f"  (skipped {other}: {type(exc).__name__})")
        continue
    if clash:
        sys.exit(f"ABORT: {sorted(clash)} also in {other}; scope is wrong")

if not apply:
    for dataset, targets in TARGETS.items():
        try:
            draft = names(dataset, "next")
            print(f"DRY RUN {dataset}: draft open, {len(draft)} tables (current "
                  f"{len(current[dataset])}); targets in draft {len(targets & draft)}/{len(targets)}")
        except Exception as exc:
            print(f"DRY RUN {dataset}: no draft open ({type(exc).__name__}); APPLY=1 creates one")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

# ---- apply ------------------------------------------------------------------------------
for dataset, targets in TARGETS.items():
    keep = current[dataset] - targets
    draft = open_draft(dataset)
    before = {t.name for t in draft.list_tables(max_results=5000)}
    if targets - before:
        sys.exit(f"ABORT: not in the {dataset} draft: {sorted(targets - before)}")
    if keep - before:
        sys.exit(f"ABORT: {dataset} draft is missing published tables: {sorted(keep - before)[:5]}")
    for name in sorted(targets):
        draft.table(name).delete()
        print(f"deleted from {dataset} draft: {name}")
    after = names(dataset, "next")
    assert before - after == targets, f"{dataset} MISMATCH: removed={sorted(before - after)}"
    assert keep <= after, f"{dataset} went missing: {sorted(keep - after)}"
    print(f"OK {dataset}: exactly {len(targets)} removed; {len(after)} left in the draft.")

print("Done. Each draft must be RELEASED to take effect. Ledger rows already exist; "
      "do not call ledger.record().")
