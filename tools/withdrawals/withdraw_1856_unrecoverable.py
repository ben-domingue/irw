"""Withdraw two #1856 tables whose defect cannot be repaired (irw#1856, #1842).

  item_response_warehouse   non_parametric_mixture_modeling_exp1_Cleaned
  item_response_warehouse   realpic_souza2021

`non_parametric_mixture_modeling_exp1_Cleaned`: 44,957 rows over only 57 distinct
(id, item) pairs. `data/Non_parametric_mixture_modeling_exp1.R` rebuilds `id` as
`rep(names(table(id)), times = table(id))` onto rows it has just sorted by `item`, so a
row's `id` has no connection to the subject who produced it. No source URL is recorded,
so the true ids cannot be recovered.

`realpic_souza2021`: `id` is a picture filename and `resp` a mean rating across raters.
Not person-by-item response data; the 28 repeated (id, item) pairs are the smaller problem.

Ben ruled 2026-09-24: withdraw both. The four `PROMISPME_Forrest_2021_*_Proxy` tables
from the same ruling are accepted as-is with a note in their script header, not withdrawn.

Refuses to act unless both targets are live in `current` with the row counts measured on
2026-09-24 (v414). Asserts the draft lost exactly the two targets.

Dry run by default. Set APPLY=1 to delete. The draft must be RELEASED to take effect,
and prior versions still serve the tables at their version tags.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_1856_unrecoverable")
import redivis

OWNER = "datapages"          # metadata/redivis_config.R
DATASET = "item_response_warehouse"

# table -> row count measured by irw_validate.live_dup against v414, 2026-09-24
TARGETS = {
    "non_parametric_mixture_modeling_exp1_Cleaned": 44957,
    "realpic_souza2021": 4172,
}

apply = os.environ.get("APPLY") == "1"


def ds(version=None):
    if version is None:
        return redivis.organization(OWNER).dataset(DATASET)
    return redivis.organization(OWNER).dataset(DATASET, version=version)


def names(version):
    return {t.name for t in ds(version).list_tables()}


def n_rows(version, table):
    q = f"SELECT COUNT(*) AS n FROM `{OWNER}.{DATASET}:{version}.{table}`"
    return int(redivis.query(q).to_pandas_dataframe()["n"].iloc[0])


def open_draft():
    # The SDK indexes properties["nextVersion"] unconditionally, and the API omits the key
    # when no draft is open -- the state right after a release (red_up's KeyError, same bug).
    d = ds()
    d.get()
    d.properties.setdefault("nextVersion", None)
    d.create_next_version(if_not_exists=True)
    return ds("next")


live = names("current")
for target, expected in TARGETS.items():
    if target not in live:
        sys.exit(f"ABORT: {target} is not live in {DATASET}; the scope is wrong")
    n = n_rows("current", target)
    if n != expected:
        sys.exit(f"ABORT: {target} has {n:,} rows, expected {expected:,}; "
                 "it changed since the ruling -- re-measure before withdrawing")
    print(f"{DATASET}: {target} live, {n:,} rows")

if not apply:
    try:
        draft = names("next")
        print(f"DRY RUN: draft ALREADY OPEN, {len(draft)} tables (current {len(live)}); "
              f"extra in draft: {sorted(draft - live)[:5]}, missing from draft: {sorted(live - draft)[:5]}")
    except Exception as exc:
        print(f"DRY RUN: no draft open ({str(exc)[:60]}); APPLY=1 would create one")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

draft = open_draft()
before = {t.name for t in draft.list_tables()}
missing = set(TARGETS) - before
if missing:
    sys.exit(f"ABORT: not in the draft: {sorted(missing)}")
for target in TARGETS:
    draft.table(target).delete()
    print(f"deleted from {DATASET} draft: {target}")

after = names("next")
assert before - after == set(TARGETS), f"MISMATCH: removed={sorted(before - after)}"
print(f"OK: exactly {len(TARGETS)} tables removed, {len(after)} left in the draft. "
      "The draft must be RELEASED to take effect.")
