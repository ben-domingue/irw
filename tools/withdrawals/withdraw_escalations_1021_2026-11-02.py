"""Withdraw the four 2026-10-21 escalations, ruled hold by Ben on 2026-11-02.

  dasilva_2019_hexaco24        irw_text    Brief HEXACO Inventory: named instrument, no grant;
                                            the originators' reprint is paywalled (SIMS rule).
  reinwarth_2023_domain_importance irw_text_2  FLZM: the labels are a word list, but the table
                                            carries the instrument's instruction paragraph and stem;
                                            held whole, redaction not adopted.
  yuebo_2024_netbenefit        irw_text_2  the one shipped table of six from Yuebo et al. 2024;
                                            items adapted from cited IS-success literature, held
                                            with its five siblings (adapted-battery ruling).
  moon_2023_pregnancy_stress   irw_text    Prenatal Psychosocial Profile: stressor categories
                                            wrapped in the PPP stress scale's own stem; FLZM shape.

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
    "withdraw_escalations_1021_2026-11-02")
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
    "dasilva_2019_hexaco24__items": ("hold", "BHI"),
    "reinwarth_2023_domain_importance__items": ("hold", "FLZM"),
    "yuebo_2024_netbenefit__items": ("hold", "ISS-TPACK-Yuebo"),
    "moon_2023_pregnancy_stress__items": ("hold", "PPP-Curry"),
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
               refs="2026-10-21 escalation, ruled by Ben 2026-11-02; register verdict " + verdict,
               rows={name: rows_at[name]},
               note=f"{verdict}, ruled 2026-11-02; local copy in data/itemtext",
               script=__file__)
print("\nledger rows written to itemtext/withdrawals.csv")
print("NOT released. Publish each shard by hand.")
