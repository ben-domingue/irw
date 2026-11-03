"""Withdraw four item-text tables found by reading the 2026-11-02 sweep's weak hits.

The 2026-11-02 instrument sweep (itemtext/sweep_instrument_rights.py, current
releases) flagged 20 single-line matches as leads. Read one by one: 15 were
incidental or already withdrawn; these four carry a register-governed
instrument in full and were missed because the register rows had no usable
match patterns (SD4, PMD), the wording was a translation the BFI-44 patterns
cannot see (BFI-10), or the instrument had no row (MSS-B).

  clemente_2024_sd4           irw_text_3  Short Dark Tetrad, Spanish; register SD4 block.
  clemente_2024_pmd           irw_text_3  Moore et al.'s PMD-8, Spanish; register PMD hold
                                          (a short form of a held instrument is held).
  jutte_2024_personality      irw_text_2  German BFI-10, the paper's English rendering;
                                          register BFI-10 block (2026-10-17 ruling).
  conspiracy_asd__schizotypy  irw_text    MSS-B, 37 of 38 items verbatim; new register
                                          row, silence holds (2026-10-15 rule).

Same mechanics as withdraw_3017_triage_2026-11-02.py: premise (every target is in the
current release), a verified local copy of each in data/itemtext/, then (APPLY=1 only)
delete from the drafts, assert exactly the targets left, append a ledger row per table
naming the register family that governs it. Dry-run by default.
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
    "withdraw_weak_hits_2026-11-02")
import redivis
from ledger import record

LOCAL = Path("/home/ben/Dropbox/projects/irw/data/itemtext")
SHARDS = ("irw_text", "irw_text_2", "irw_text_3", "irw_text_4")


def _retry(fn, *a, tries=5, **kw):
    """The SDK masks a throttle as AttributeError on a None response."""
    for i in range(tries):
        try:
            return fn(*a, **kw)
        except AttributeError:
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))


TARGETS = {
    "clemente_2024_sd4__items": ("block", "SD4"),
    "clemente_2024_pmd__items": ("hold", "PMD"),
    "jutte_2024_personality__items": ("block", "BFI-10"),
    "conspiracy_asd__schizotypy__items": ("hold", "MSS-B"),
}

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
               refs="2026-11-02 sweep weak-hit read; register verdict " + verdict,
               rows={name: rows_at[name]},
               note=f"{verdict} under the register row; local copy in data/itemtext",
               script=__file__)
print("\nledger rows written to itemtext/withdrawals.csv")
print("NOT released. Publish each shard by hand.")
