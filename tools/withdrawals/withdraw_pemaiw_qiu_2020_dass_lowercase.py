"""Withdraw the lowercase duplicate of the PEMAIW_Qiu_2020_DASS item text.

Two item-text tables were published for one response table:

  pemaiw_qiu_2020_dass__items  irw_text    pilot-era extraction, mapping_basis=unknown,
                                           canonical paper DASS-21 wording ("circle a
                                           number 0, 1, 2 or 3" against resp 1-4)
  PEMAIW_Qiu_2020_DASS__items  irw_text_2  batch_131, transcribed from the study's own
                                           Qualtrics question-text row (OSF ph6ks)

batch_131 was meant to REPLACE the pilot table (itemtext/itemtables/batch_131/notes.csv
says so and warns that the capitalised name would create a second table, which is what
happened). Ben chose the batch_131 copy on 2026-11-25; the capitalised name also matches
the IRW table name, per the 2026-09-10 case ruling. Found through the duplicate-key warning
in the 2026-11-25 metadata pipeline run (#3731).

Premise: the target is in irw_text current and the keeper is in irw_text_2 current. A local
copy of the target is verified before any delete. With APPLY=1: delete from the irw_text
draft, assert exactly the target left, assert the keeper is untouched, append a ledger row.
Dry-run by default. Nothing is released.
"""
import csv
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token(
    "withdraw_pemaiw_qiu_2020_dass_lowercase")
import redivis
from ledger import record

LOCAL = Path("/home/ben/Dropbox/projects/irw/data/itemtext")
TARGET, TARGET_DS = "pemaiw_qiu_2020_dass__items", "irw_text"
KEEP, KEEP_DS = "PEMAIW_Qiu_2020_DASS__items", "irw_text_2"


def _retry(fn, *a, tries=5, **kw):
    """The SDK masks a throttle as AttributeError on a None response."""
    for i in range(tries):
        try:
            return fn(*a, **kw)
        except AttributeError:
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))


def names(ds):
    out = {t.name for t in _retry(ds.list_tables)}
    if len(out) < 50:
        sys.exit(f"ABORT: listing returned {len(out)} tables; treating as a failed listing")
    return out


# 1. Premise.
cur = redivis.user("datapages").dataset(TARGET_DS, version="current")
if TARGET not in names(cur):
    sys.exit(f"ABORT: {TARGET} not in {TARGET_DS} current -- already withdrawn?")
keep_cur = redivis.user("datapages").dataset(KEEP_DS, version="current")
if KEEP not in names(keep_cur):
    sys.exit(f"ABORT: keeper {KEEP} not in {KEEP_DS} current; withdrawing would leave no DASS text")
keep_rows = _retry(keep_cur.table(KEEP).get).properties["numRows"]
print(f"premise ok: {TARGET} in {TARGET_DS}; keeper {KEEP} in {KEEP_DS} ({keep_rows} rows)")

# 2. Local copy before any delete.
LOCAL.mkdir(parents=True, exist_ok=True)
dest = LOCAL / f"{TARGET}.csv"
tbl = cur.table(TARGET)
live_n = _retry(tbl.get).properties["numRows"]
_retry(tbl.download, str(dest), overwrite=True)
with dest.open(newline="", encoding="utf-8") as fh:
    n = sum(1 for _ in csv.reader(fh)) - 1
if n <= 0 or n != live_n:
    sys.exit(f"ABORT: local copy {dest} has {n} rows, live has {live_n}")
print(f"local copy verified: {dest} ({n} rows)")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

# 3. Delete from the draft and verify.
base = redivis.user("datapages").dataset(TARGET_DS)
_retry(base.create_next_version, if_not_exists=True)
ds = redivis.user("datapages").dataset(TARGET_DS, version="next")
before = names(ds)
if TARGET not in before:
    sys.exit(f"ABORT: {TARGET} not in the {TARGET_DS} draft")
_retry(ds.table(TARGET).delete)
after = names(redivis.user("datapages").dataset(TARGET_DS, version="next"))
assert before - after == {TARGET}, f"MISMATCH: {sorted(before - after)}"
assert "dumas_Organisciak_2022__items" in after, "dumas_Organisciak_2022__items went missing"
assert KEEP in names(redivis.user("datapages").dataset(KEEP_DS, version="current"))
print(f"OK: {TARGET_DS} draft now {len(after)} tables; {TARGET} removed, keeper intact.")

record([TARGET], dataset=TARGET_DS, reason="duplicate",
       refs="#3731 duplicate-key warning; batch_131 notes.csv; Ben 2026-11-25",
       rows={TARGET: n},
       note=f"case-variant duplicate of {KEEP} ({KEEP_DS}), which is the study's administered "
            "wording; local copy in data/itemtext",
       script=__file__)
print("ledger row written to itemtext/withdrawals.csv")
print(f"NOT released. Publish {TARGET_DS} by hand.")
