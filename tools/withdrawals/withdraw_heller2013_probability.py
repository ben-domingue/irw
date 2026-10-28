"""Remove `heller2013_probability` from irw_simsyn (irw#3229).

The table is the second half of `pks::probability` -- 345 respondents x 12 items,
the b201..b212 problems, for the "completer" subset the package's own example
takes (`probability[!is.na(probability$b201), ]`). Three things are wrong with it
and one fix settles all three.

1. It is real data in a family ARCHITECTURE.md defines as "responses not produced
   by real people". 345 people answered these problems.
2. Core already publishes the same responses. `pks_probability` in
   item_response_warehouse is 504 x 24, both problem sets, with a `wave` column;
   this table's 4,140 responses are a subset of those 12,096.
3. Its one addition over that table, the Q-matrix, ships as `Q_matrix_A1..A4`
   where datastandard.md says `qmatrix1`..`qmatrixN`.

So rather than move it to core, `data/pks.R` now writes that Q-matrix onto
`pks_probability` as `qmatrix1..qmatrix4` (the package's own `sf1`, which its
examples apply to both problem sets), and this withdraws the duplicate. Ben ruled
the fold on 2026-10-28.

Refuses to act unless the rebuilt `pks_probability` is already in the core draft
or release CARRYING the qmatrix columns -- the data must be in the corpus before
the duplicate leaves it.

Dry run by default. Set APPLY=1 to delete.
"""
import os
import sys

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token(
    "withdraw_heller2013_probability")
import redivis

OWNER = "datapages"                     # metadata/redivis_config.R
DATASET = "irw_simsyn"
TARGET = "heller2013_probability"
CORE = "item_response_warehouse"        # where pks_probability lives
KEEPER = "pks_probability"
NEEDED = {"qmatrix1", "qmatrix2", "qmatrix3", "qmatrix4"}

apply = os.environ.get("APPLY") == "1"


def keeper_table():
    """The rebuilt keeper, from the core draft if one is open, else the release."""
    for version in ("next", "current"):
        try:
            ds = redivis.organization(OWNER).dataset(CORE, version=version)
            t = ds.table(KEEPER)
            cols = {v["name"] for v in t.list_variables()}
            if NEEDED <= cols:
                return version, cols
        except Exception:
            continue
    return None, set()


version, cols = keeper_table()
if version is None:
    sys.exit(f"ABORT: {CORE}.{KEEPER} does not carry {sorted(NEEDED)} in either the "
             f"draft or the release; upload the rebuild first, or the Q-matrix "
             f"leaves the corpus with this table")
print(f"{KEEPER} in {CORE}:{version} carries the Q-matrix ({len(cols)} columns)")


def open_draft():
    ds = redivis.organization(OWNER).dataset(DATASET)
    ds.create_next_version(if_not_exists=True)
    return redivis.organization(OWNER).dataset(DATASET, version="next")


if not apply:
    try:
        draft = redivis.organization(OWNER).dataset(DATASET, version="next")
        before = {t.name for t in draft.list_tables()}
        print(f"DRY RUN: draft open, {len(before)} tables; target present: "
              f"{TARGET in before}")
    except Exception as exc:
        print(f"DRY RUN: no draft open ({exc}); APPLY=1 would create one.")
    print("Nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

draft = open_draft()
before = {t.name for t in draft.list_tables()}
if TARGET not in before:
    sys.exit(f"ABORT: {TARGET} not in the {DATASET} draft")

draft.table(TARGET).delete()
print("deleted:", TARGET)

after = {t.name for t in redivis.organization(OWNER).dataset(
    DATASET, version="next").list_tables()}
removed = before - after
assert removed == {TARGET}, f"MISMATCH: removed={removed}"
assert len(after) == len(before) - 1, f"MISMATCH: {len(before)} -> {len(after)}"
print(f"OK: only {TARGET} removed from {DATASET} ({len(before)} -> {len(after)} "
      f"tables). Draft must be RELEASED to take effect.")
