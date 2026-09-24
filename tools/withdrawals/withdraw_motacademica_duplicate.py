"""Withdraw `MotAcademica_Ribeiro_2019` and its item text (irw#2313 item 14).

It duplicates `ribeiro_2019_academic_motivation` (item_response_warehouse_5): the same
33,553 rows, identical on (id, item, resp) after sorting, from two deposits of the same
study (Harvard Dataverse doi:10.7910/DVN/KWTMWT and Mendeley doi:10.17632/6n78w5pz74).
The survivor is strictly richer -- it carries `cov_study`, the Amostra A/B split -- and its
item text is keyed identically (`Item1`..`Item29`). Ben ruled 2026-09-23: withdraw.

  item_response_warehouse   MotAcademica_Ribeiro_2019
  irw_text_2                MotAcademica_Ribeiro_2019__items

Refuses to act unless both twins are in their datasets' `current` with the same row count.
Asserts each draft lost exactly its target and the twins are untouched.

Dry run by default. Set APPLY=1 to delete. Both drafts must be RELEASED to take effect,
and prior versions still serve the tables at their version tags.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_motacademica_duplicate")
import redivis

OWNER = "datapages"          # metadata/redivis_config.R

TARGETS = {
    "item_response_warehouse": "MotAcademica_Ribeiro_2019",
    "irw_text_2":              "MotAcademica_Ribeiro_2019__items",
}
# target dataset -> (twin dataset, twin table)
TWINS = {
    "item_response_warehouse": ("item_response_warehouse_5", "ribeiro_2019_academic_motivation"),
    "irw_text_2":              ("irw_text_2",                "ribeiro_2019_academic_motivation__items"),
}

apply = os.environ.get("APPLY") == "1"


def ds(dataset, version=None):
    if version is None:
        return redivis.organization(OWNER).dataset(dataset)
    return redivis.organization(OWNER).dataset(dataset, version=version)


def names(dataset, version):
    return {t.name for t in ds(dataset, version).list_tables()}


def n_rows(dataset, version, table):
    q = f"SELECT COUNT(*) AS n FROM `{OWNER}.{dataset}:{version}.{table}`"
    return int(redivis.query(q).to_pandas_dataframe()["n"].iloc[0])


def open_draft(dataset):
    # The SDK indexes properties["nextVersion"] unconditionally, and the API omits the key
    # when no draft is open -- the state right after a release (red_up's KeyError, same bug).
    d = ds(dataset)
    d.get()
    d.properties.setdefault("nextVersion", None)
    d.create_next_version(if_not_exists=True)
    return ds(dataset, "next")


for dataset, target in TARGETS.items():
    twin_ds, twin = TWINS[dataset]
    if target not in names(dataset, "current"):
        sys.exit(f"ABORT: {target} is not live in {dataset}; the scope is wrong")
    if twin not in names(twin_ds, "current"):
        sys.exit(f"ABORT: twin {twin} missing from {twin_ds} current; "
                 "withdrawing would take the data out of the corpus entirely")
    nt, nw = n_rows(dataset, "current", target), n_rows(twin_ds, "current", twin)
    if nt != nw:
        sys.exit(f"ABORT: {target} has {nt:,} rows, {twin} has {nw:,}; not the duplicate recorded")
    print(f"{dataset}: {target} and twin {twin_ds}.{twin} both {nt:,} rows")

if not apply:
    for dataset, target in TARGETS.items():
        try:
            draft = names(dataset, "next")
            print(f"DRY RUN {dataset}: draft ALREADY OPEN, {len(draft)} tables "
                  f"(current {len(names(dataset, 'current'))}); target in draft: {target in draft}")
        except Exception as exc:
            print(f"DRY RUN {dataset}: no draft open ({str(exc)[:60]}); APPLY=1 would create one")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

for dataset, target in TARGETS.items():
    twin_ds, twin = TWINS[dataset]
    draft = open_draft(dataset)
    before = {t.name for t in draft.list_tables()}
    if target not in before:
        sys.exit(f"ABORT: {target} not in the {dataset} draft")
    draft.table(target).delete()
    print(f"deleted from {dataset}: {target}")

    after = names(dataset, "next")
    assert before - after == {target}, f"MISMATCH in {dataset}: removed={sorted(before - after)}"
    assert twin in names(twin_ds, "current"), f"{twin} went missing from {twin_ds}"
    if twin_ds == dataset:
        assert twin in after, f"{twin} went missing from the {dataset} draft"
    print(f"OK {dataset}: exactly 1 table removed, {len(after)} left in the draft; "
          f"{twin} intact. The draft must be RELEASED to take effect.")
