"""Withdraw three live tables whose register rows already say block (#3017 sweep, 2026-10-16).

Targets (register verdict block, table live in the published shard):
  FomoNegativeAffect_cremer_2026_panas  irw_text_3  PANAS  (block, counsel 2026-10-15)
  ali_2021_isi                          irw_text    ISI    (block, row 238)
  beck_2021_iesr                        irw_text    IES-R  (block, row 72)

Same steps as withdraw_silence_2026_10_15.py: confirm published, save local copies to
data/itemtext/ BEFORE any delete, then delete from each shard's draft only when APPLY=1.
Published tables leave the warehouse at the NEXT release, which Ben publishes.
Dry-run by default.
"""
import csv, os, sys
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_block_register_2026_10_16")
import redivis
from ledger import record

LOCAL = Path("/home/ben/Dropbox/projects/irw/data/itemtext")

TARGETS = {
    "FomoNegativeAffect_cremer_2026_panas__items": ("irw_text_3", "PANAS"),
    "ali_2021_isi__items":                         ("irw_text",   "ISI"),
    "beck_2021_iesr__items":                       ("irw_text",   "IES-R"),
}
assert len(TARGETS) == 3

by_shard = {}
for t, (s, _) in TARGETS.items():
    by_shard.setdefault(s, set()).add(t)

for shard, targets in by_shard.items():
    cur = redivis.user("datapages").dataset(shard, version="current")
    names = {t.name for t in cur.list_tables()}
    print(f"{shard}: {len(names)} published tables; {len(targets)} targets")
    missing = targets - names
    if missing:
        sys.exit(f"ABORT: not published in {shard}: {sorted(missing)}")

LOCAL.mkdir(parents=True, exist_ok=True)
rows_at = {}
for shard, targets in by_shard.items():
    cur = redivis.user("datapages").dataset(shard, version="current")
    for name in sorted(targets):
        dest = LOCAL / f"{name}.csv"
        if not dest.exists() or dest.stat().st_size == 0:
            cur.table(name).download(str(dest), overwrite=True)
        with open(dest, newline="", encoding="utf-8") as fh:
            n = sum(1 for _ in csv.reader(fh)) - 1
        live_n = cur.table(name).get().properties["numRows"]
        if n != live_n or n <= 0:
            sys.exit(f"ABORT: local copy {dest} has {n} rows, live has {live_n}")
        rows_at[name] = n
        print(f"  saved {dest.name}: {n} rows")
print(f"local copies OK: {len(rows_at)} tables, {sum(rows_at.values())} rows")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- local copies written, nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

for shard, targets in by_shard.items():
    base = redivis.user("datapages").dataset(shard)
    base.create_next_version(if_not_exists=True)
    ds = redivis.user("datapages").dataset(shard, version="next")
    before = {t.name for t in ds.list_tables()}
    todo = targets & before
    print(f"\n{shard} draft tables before: {len(before)}; to delete: {len(todo)}")
    for name in sorted(todo):
        ds.table(name).delete()
        print("deleted:", name)
    after = {t.name for t in redivis.user("datapages").dataset(shard, version="next").list_tables()}
    assert before - after == todo, f"MISMATCH in {shard}"
    assert not (targets & after)
    print(f"OK: {shard} draft now {len(after)} tables, none of the targets remain.")
    for fam in sorted({TARGETS[t][1] for t in todo}):
        fam_t = sorted(t for t in todo if TARGETS[t][1] == fam)
        record(fam_t, dataset=shard, reason="rights", family=fam,
               refs="register block; #3017 sweep 2026-10-16",
               rows={t: rows_at[t] for t in fam_t},
               note="register verdict block; local copy in data/itemtext",
               script=__file__)
print("\nledger rows written to itemtext/withdrawals.csv")
