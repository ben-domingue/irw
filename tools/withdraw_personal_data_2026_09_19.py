"""Withdraw nine live tables that publish personal data (found by the #2255 triage).

Ben's call, 2026-09-19: remove them now, fix the processing scripts, re-upload later.
Each case is a column the processing script carried through from a public source deposit:

  item_response_warehouse (shard 1)
    PSR-P_Scale_Intimacy_Hakim_2018_Study2_PSR   id = the respondent's name ("Nama")
    PSR-P_Scale_Intimacy_Hakim_2018_Study2_PSI   same, same script line
      data/PSR-P_Scale_Intimacy_Hakim_2018.R: rename(id=Nama, figure=Tokoh)
      _Study3 is NOT affected: it renames id=ID, so it stays.

  item_response_warehouse_2 (shard 2)
    ipq_doglioni_2021                            cov_dob = exact dates of birth for 408
                                                 sickle-cell patients, beside cov_genotype
      data/ipq_doglioni_2021.py: 'DateNaiss': 'cov_dob'
    parenting_anunciacao_2025_{affect,goals,material_rewards,materialism,rejection,values}
                                                 cov_children_details = free text answering
                                                 "children's full names and ages", 125 filled
      data/parenting_anunciacao_2025.py keeps the column as a covariate.

Whole-table withdrawal, not partial: the fix needs a rebuild of each table anyway, and a
partial pass would leave the tables live meanwhile.

A release does not remove these rows from PRIOR versions, which still serve them at their
version tags (see the withdrawal-mechanics note). That is a separate decision for Ben.

Dry run by default. Set APPLY=1 to delete. Each shard's draft must then be RELEASED by Ben.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_personal_data_2026_09_19")
import redivis

OWNER = "datapages"

TARGETS = {
    "item_response_warehouse": {
        "PSR-P_Scale_Intimacy_Hakim_2018_Study2_PSR",
        "PSR-P_Scale_Intimacy_Hakim_2018_Study2_PSI",
    },
    "item_response_warehouse_2": {
        "ipq_doglioni_2021",
        "parenting_anunciacao_2025_affect",
        "parenting_anunciacao_2025_goals",
        "parenting_anunciacao_2025_material_rewards",
        "parenting_anunciacao_2025_materialism",
        "parenting_anunciacao_2025_rejection",
        "parenting_anunciacao_2025_values",
    },
}

# Named survivors: same family or same script, and they must NOT be touched.
KEEP = {
    "item_response_warehouse": {"PSR-P_Scale_Intimacy_Hakim_2018_Study3"},
    "item_response_warehouse_2": set(),
}

apply = os.environ.get("APPLY") == "1"


def tables(dataset, version):
    return {t.name for t in redivis.organization(OWNER).dataset(dataset, version=version).list_tables()}


for dataset, targets in TARGETS.items():
    current = tables(dataset, "current")
    missing = targets - current
    if missing:
        sys.exit(f"ABORT: not live in {dataset}, so the scope is wrong: {sorted(missing)}")
    keep_missing = KEEP[dataset] - current
    if keep_missing:
        sys.exit(f"ABORT: KEEP table not live in {dataset}: {sorted(keep_missing)}")

    if not apply:
        try:
            draft = tables(dataset, "next")
            print(f"DRY RUN {dataset}: draft ALREADY OPEN with {len(draft)} tables "
                  f"(current {len(current)}); would delete {len(targets)}: {sorted(targets)}")
        except Exception as exc:
            print(f"DRY RUN {dataset}: no draft open ({str(exc)[:60]}); APPLY=1 would create one. "
                  f"Would delete {len(targets)}: {sorted(targets)}")
        continue

    ds = redivis.organization(OWNER).dataset(dataset)
    ds.create_next_version(if_not_exists=True)
    before = tables(dataset, "next")
    if targets - before:
        sys.exit(f"ABORT: not in the {dataset} draft: {sorted(targets - before)}")

    for name in sorted(targets):
        redivis.organization(OWNER).dataset(dataset, version="next").table(name).delete()
        print(f"deleted from {dataset}: {name}")

    after = tables(dataset, "next")
    removed = before - after
    assert removed == targets, f"MISMATCH in {dataset}: removed={sorted(removed)}"
    assert KEEP[dataset] <= after, f"went missing from {dataset}: {sorted(KEEP[dataset] - after)}"
    print(f"OK {dataset}: {len(targets)} removed, {len(after)} tables left in the draft. "
          f"The draft must be RELEASED to take effect.")
