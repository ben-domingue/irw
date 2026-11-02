"""Withdraw the #3017 triage's hold and block tables from the item-text shards.

The 2026-10-16 #3017 sweep classed 372 live item-text tables as "named
third-party instrument, no grant located", from batch notes. On 2026-11-02 the
321 still live were re-read one by one (live item text, the register by
instrument name, the batch notes, the originator's own terms, PsycTESTS), with
Ben's rulings of that day applied. Two Short Dark Triad tables from the same
day's shard sweep were added. The verdicts are merged on main (#3358):

    oneoff/itemtext-rights-bank/triage_3017_verdicts_2026-11-02.csv

This script withdraws every table whose verdict there is `hold` or `block`:
238 tables, read from that file rather than retyped, so the file is the
single authority for what goes. `ship` and `ship_with_note` tables are not
touched.

A hold or block stops the WORDING, not the response data: only `__items`
tables in the irw_text* shards are deleted. Response tables stay.

Steps, each of which aborts on surprise:
  1. every target is in the CURRENT release of its shard (the premise);
  2. a local copy of every target is written to data/itemtext/ and its row
     count checked against the live table, BEFORE any delete;
  3. (APPLY=1 only) delete from each shard's draft, assert exactly the targets
     left, and append one ledger row per table.

Dry-run by default. Re-run with APPLY=1 to delete. Tables leave the warehouse
at the NEXT release of each shard, which Ben publishes. Check
`python3 -m red_up.drafts --dataset <shard> --verbose` before publishing, in
case another session has staged unrelated adds in the same draft.
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
    "withdraw_3017_triage_2026-11-02")
import redivis
from ledger import record

LOCAL = Path("/home/ben/Dropbox/projects/irw/data/itemtext")
VERDICTS = ROOT / "oneoff/itemtext-rights-bank/triage_3017_verdicts_2026-11-02.csv"
SHARDS = ("irw_text", "irw_text_2", "irw_text_3", "irw_text_4")
EXPECTED = 238


def _retry(fn, *a, tries=5, **kw):
    """The SDK masks a throttle as AttributeError on a None response."""
    for i in range(tries):
        try:
            return fn(*a, **kw)
        except AttributeError:
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))


with VERDICTS.open(newline="", encoding="utf-8") as fh:
    verdicts = [r for r in csv.DictReader(fh) if r["verdict"] in ("hold", "block")]
if len(verdicts) != EXPECTED:
    sys.exit(f"ABORT: {len(verdicts)} hold/block rows in {VERDICTS.name}, "
             f"expected {EXPECTED}; the verdicts changed, re-read before running")

#: table__items -> (verdict, family) -- family is the instrument as identified
TARGETS = {f"{r['table']}__items": (r["verdict"], r["instrument_identified"][:80])
           for r in verdicts}

# ---------------------------------------------------------------------------
# 1. The premise: every target is in the current release of some text shard.
# ---------------------------------------------------------------------------
by_shard: dict[str, set[str]] = {}
for shard in SHARDS:
    cur = redivis.user("datapages").dataset(shard, version="current")
    names = {t.name for t in _retry(cur.list_tables)}
    if len(names) < 50:
        sys.exit(f"ABORT: {shard} listed {len(names)} tables; treating as a "
                 "failed listing rather than an empty shard")
    hit = set(TARGETS) & names
    if hit:
        by_shard[shard] = hit
    print(f"{shard}: {len(names)} published tables, {len(hit)} target(s)")

found = set().union(*by_shard.values()) if by_shard else set()
missing = sorted(set(TARGETS) - found)
if missing:
    sys.exit(f"ABORT: {len(missing)} target(s) in no current text shard, e.g. "
             f"{missing[:5]} -- already withdrawn, renamed, or the listing failed")

# ---------------------------------------------------------------------------
# 2. A local copy BEFORE any delete (Ben's standing rule, 2026-10-15).
# ---------------------------------------------------------------------------
LOCAL.mkdir(parents=True, exist_ok=True)
rows_at: dict[str, int] = {}
for shard, targets in sorted(by_shard.items()):
    cur = redivis.user("datapages").dataset(shard, version="current")
    for name in sorted(targets):
        dest = LOCAL / f"{name}.csv"
        tbl = cur.table(name)
        live_n = _retry(tbl.get).properties["numRows"]
        n = -1
        if dest.exists() and dest.stat().st_size > 0:
            with dest.open(newline="", encoding="utf-8") as fh:
                n = sum(1 for _ in csv.reader(fh)) - 1
        if n != live_n:
            _retry(tbl.download, str(dest), overwrite=True)
            with dest.open(newline="", encoding="utf-8") as fh:
                n = sum(1 for _ in csv.reader(fh)) - 1
        if n <= 0 or n != live_n:
            sys.exit(f"ABORT: local copy {dest} has {n} rows, live has {live_n}")
        rows_at[name] = n
    print(f"  {shard}: {len(targets)} local copies verified")

print(f"\n{len(found)} targets, {sum(rows_at.values()):,} rows, all copied to {LOCAL}")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- premise confirmed and local copies verified. "
          "Nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

# ---------------------------------------------------------------------------
# 3. Delete from the draft, assert exactly the targets went, record the event.
# ---------------------------------------------------------------------------
for shard, targets in sorted(by_shard.items()):
    base = redivis.user("datapages").dataset(shard)
    _retry(base.create_next_version, if_not_exists=True)
    ds = redivis.user("datapages").dataset(shard, version="next")
    before = {t.name for t in _retry(ds.list_tables)}
    todo = targets & before
    print(f"\n{shard} draft tables before: {len(before)}; to delete: {len(todo)}")
    for name in sorted(todo):
        _retry(ds.table(name).delete)
    after = {t.name for t in _retry(
        redivis.user("datapages").dataset(shard, version="next").list_tables)}
    assert before - after == todo, f"MISMATCH in {shard}: {sorted(before - after)}"
    assert not (targets & after), f"target still in {shard} draft"
    print(f"OK: {shard} draft now {len(after)} tables, no target remains.")
    for name in sorted(todo):
        verdict, family = TARGETS[name]
        record([name], dataset=shard, reason="rights", family=family,
               refs="#3017 triage 2026-11-02 (#3358); register verdict " + verdict,
               rows={name: rows_at[name]},
               note=f"{verdict} under the 2026-10-15 rule; local copy in data/itemtext",
               script=__file__)
print("\nledger rows written to itemtext/withdrawals.csv")
print("NOT released. Publish each shard by hand.")
