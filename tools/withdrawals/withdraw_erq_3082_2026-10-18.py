"""Withdraw the item-text tables shipping the English ERQ, ruled block on #3082.

Ben ruled on irw#3082 (2026-10-18) that a grant scoped to a class of USE does
not reach redistribution of the wording. PR #3085 applies that to the ERQ,
superseding the irw#3078 ship ruling of the same morning: SWLS, PSS, BFI-2 and
IRI all block on scoped-use clauses, and Gross & John's "academic research
purposes" is the same shape. This withdraws the tables that shipped on the
reading #3085 retires.

RUN THIS ONLY AFTER #3085 IS MERGED. Until the register says `block`, this
withdraws tables the register still says may ship.

**Five tables, not four.** #3085 and the outreach batch both say "four live ERQ
tables", and the register's own `notes` names four -- moe2025_erq,
morales_2021_erq, zhao_2024_erq, garciabatista_2021_erq -- and then adds "plus
li_2024_bdyz, shipped on this reasoning in irw#2121". li_2024_bdyz is not in
itemtext/withdrawals.csv and rests on exactly the reading #3085 retires, so it
is included here. If Ben wants the count held to four, drop it from TARGETS;
nothing else changes.

Four of the five are substitution cases: moe2025_erq, morales_2021_erq,
zhao_2024_erq and li_2024_bdyz were administered in Italian, Spanish and
Chinese with no administered wording published anywhere, and ship the English
original as a stand-in. garciabatista_2021_erq is the study's own English SPSS
variable labels, independently shippable -- it is withdrawn here because the
clause it shipped under no longer reaches redistribution, not because the
wording is unavailable.

NOT withdrawn, deliberately:

  sv-maia2_randelovic_2021_erq ships the Knezevic (2021) Serbian translation
  from osf.io/fdpc2, a different translation from the one the lab hosts. The
  Gross clause never reached it; the deposit's own terms govern, and they are
  unaffected by #3082. The register's match_item_code is deliberately empty so
  that a '^erq' pattern cannot sweep it in -- do not add one.

  os_tbmwtfs_schubert_2023_cerq__items is already withdrawn (#3017 tranche 2,
  2026-10-17) on the Leiden CERQ form, and stays that way.

**Register row 165 (PANAS-ES-MORIONDO) cites this as precedent** -- it ships the
English PANAS adjectives as a stand-in on the "li_2024_bdyz/ERQ substitution
precedent". That row is NOT touched here and should not be. #3082 is about
whether a scoped grant reaches redistribution, not about which language's
wording stands in for an untranslated administration; the substitution logic
survives, it simply can no longer be applied to the ERQ. Row 165 ships English
PANAS adjectives, whose rights are a separate question already settled.

Same shape as withdraw_3017_tranche3_2026-10-18.py: confirm each table, save a
local copy to data/itemtext/ BEFORE any delete, then delete from each shard
draft only when APPLY=1. Published tables leave the warehouse at the NEXT
release, which Ben publishes. Dry-run by default.

Unlike the tranche scripts, the shard for each table is resolved at runtime
rather than hardcoded, and the run aborts if a target is in no shard or in more
than one.
"""
import csv, os, sys, time
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_erq_3082_2026_10_18")
import redivis
from ledger import record

LOCAL = Path("/home/ben/Dropbox/projects/irw/data/itemtext")
SHARDS = ("irw_text", "irw_text_2", "irw_text_3")

# table -> family, as the register's `family` column spells it.
TARGETS = {
    "moe2025_erq__items":          "ERQ",
    "morales_2021_erq__items":     "ERQ",
    "zhao_2024_erq__items":        "ERQ",
    "garciabatista_2021_erq__items": "ERQ",
    "li_2024_bdyz__items":         "ERQ",
}
assert len(TARGETS) == 5

# Named here so an accidental edit to TARGETS cannot pull them in.
NEVER = {"sv-maia2_randelovic_2021_erq__items",
         "os_tbmwtfs_schubert_2023_cerq__items"}
assert not (set(TARGETS) & NEVER)


def _retry(fn, what, tries=5):
    """Redivis throttling surfaces as AttributeError from the SDK's own error
    handler (see redivis-sdk-empty-error-attributeerror). Back off and retry."""
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            if i == tries - 1:
                raise
            wait = 5 * (2 ** i)
            print(f"  retry {i+1}/{tries-1} on {what}: {type(e).__name__}; sleeping {wait}s")
            time.sleep(wait)


# Resolve where each target lives. A table must appear in exactly one shard: the
# same item-text table in two shards would mean a delete in one leaves the
# wording published from the other.
listing = {}
for shard in SHARDS:
    cur = _retry(lambda s=shard: {t.name for t in redivis.user("datapages")
                                  .dataset(s, version="current").list_tables()},
                 f"current {shard}")
    try:
        nxt = _retry(lambda s=shard: {t.name for t in redivis.user("datapages")
                                      .dataset(s, version="next").list_tables()},
                     f"next {shard}")
    except Exception as exc:
        nxt = set()
        print(f"{shard}: no open draft ({type(exc).__name__})")
    listing[shard] = (cur, nxt)
    print(f"{shard}: {len(cur)} published, {len(nxt)} draft")

for name in sorted(NEVER):
    where = [s for s, (c, n) in listing.items() if name in (c | n)]
    if where:
        print(f"  leaving in place (not a #3082 target): {name} in {where[0]}")

home = {}
for name in sorted(TARGETS):
    where = [s for s, (c, n) in listing.items() if name in (c | n)]
    if not where:
        sys.exit(f"ABORT: {name} is in none of {SHARDS}")
    if len(where) > 1:
        sys.exit(f"ABORT: {name} is in more than one shard: {where}")
    home[name] = where[0]

by_shard = {}
for t, s in home.items():
    by_shard.setdefault(s, set()).add(t)

published, draft_only = {}, {}
for name, shard in home.items():
    cur, _ = listing[shard]
    (published if name in cur else draft_only)[name] = shard
print(f"\nresolved: {len(published)} published, {len(draft_only)} draft-only")
for name in sorted(home):
    print(f"   {name:42s} {home[name]:11s} "
          f"{'published' if name in published else 'DRAFT-ONLY'}")
if draft_only:
    print(f"DRAFT-ONLY (deleting removes these outright): {sorted(draft_only)}")

LOCAL.mkdir(parents=True, exist_ok=True)
rows_at = {}
for name, shard in sorted(home.items()):
    ver = "current" if name in published else "next"
    ds = redivis.user("datapages").dataset(shard, version=ver)
    dest = LOCAL / f"{name}.csv"
    if not dest.exists() or dest.stat().st_size == 0:
        _retry(lambda n=name, d=ds: d.table(n).download(str(dest), overwrite=True),
               f"download {name}")
    with open(dest, newline="", encoding="utf-8") as fh:
        n = sum(1 for _ in csv.reader(fh)) - 1
    live_n = _retry(lambda nm=name, d=ds: d.table(nm).get().properties["numRows"],
                    f"numRows {name}")
    if n != live_n or n <= 0:
        sys.exit(f"ABORT: local copy {dest} has {n} rows, live ({ver}) has {live_n}")
    rows_at[name] = n
    print(f"  saved {dest.name}: {n} rows (from {ver})")
print(f"local copies OK: {len(rows_at)} tables, {sum(rows_at.values())} rows")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- local copies written, nothing deleted, no draft created. "
          "Re-run with APPLY=1.")
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
    after = {t.name for t in redivis.user("datapages")
             .dataset(shard, version="next").list_tables()}
    assert before - after == todo, f"MISMATCH in {shard}"
    assert not (targets & after)
    assert not (NEVER & after) or (NEVER & before), f"NEVER-list table vanished in {shard}"
    print(f"OK: {shard} draft now {len(after)} tables, none of the targets remain.")
    record(sorted(todo), dataset=shard, reason="rights", family="ERQ",
           refs="register block; irw#3082 scoped-use ruling 2026-10-18; PR #3085",
           rows={t: rows_at[t] for t in sorted(todo)},
           note=("shipped on the irw#3078 reading that Gross & John's academic-research "
                 "grant reaches redistribution; superseded the same day by the irw#3082 "
                 "ruling that a scoped use-grant does not. Includes li_2024_bdyz, which "
                 "rests on the same reading via irw#2121 and which #3085's count of four "
                 "omits. local copy in data/itemtext"),
           script=__file__)
print("\nledger rows written to itemtext/withdrawals.csv")
