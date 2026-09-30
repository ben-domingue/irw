"""Withdraw rights-blocked wording found by the 2026-09-29 `_translated` sweep.

Two rulings (irw#2401, audit/2401/RULES.md):

* Decision 7 -- an instrument's `block` row in itemtext/instrument_rights_register.csv
  covers the `*_translated` columns too.
* 2026-09-29, round 2 -- a `block` row covers the instrument in EVERY language, in
  `item_text` as well as `*_translated`. A translation of blocked wording is still
  the instrument.

The sweep (itemtext/sweep_instrument_rights.py, now reading `_translated`) flagged 8
tables only through those columns (audit/2401/triage/rights_translated.csv). Each was
read item by item (audit/2401/repairs/rights_translated.md); three were confirmed and
two siblings were added under the second ruling. Five were false (single-stem matches
on corti, dasilva, merlo and the two MAIA-2 tables) and are not touched.

WHOLE -- every item is the blocked instrument, in the base text and in English:
  irw_text    sun_2025_morality_study2_meaning  MLQ-Presence (tsmlq1..5), Chinese
              base; the register had it as the PERMA-Profiler, which was wrong.
  irw_text_2  jablonska_2020_swls               SWLS 5/5, Polish base.

PARTIAL -- QCAE items 1-6 are Davis's IRI (PT 1, 3, 4, 5, 6; FS 2); the other 25
QCAE items, the instructions and the anchors are the QCAE's own and stay:
  irw_text_2  queiros_2018_qcae   QCAE_1..QCAE_6, Portuguese + English
  irw_text_2  gomez_2022_qcae     QCAE1r, QCAE2r, QCAE3..QCAE6, English
  irw_text_2  powell_2018_qcae    QCAE1..QCAE6, English
Each goes 124 -> 100 rows.

This supersedes the first, `_translated`-only version of this script (jablonska and
queiros blanked, not dropped), which was committed but never run. Its two ledger rows
stay in itemtext/withdrawals.csv (the ledger is append-only); the rows citing this
version say they supersede them. Do not call ledger.record() when applying: the rows
were written by hand with `released` blank.

The partial path follows withdraw_bfi2.py: download the published CSV and filter it at
the text level, never through pandas (IRW's null is the literal "NA"), then check the
result against the staged rebuild in /home/ben/irw-stage/2401-audit/itemtext/ (built by
audit/2401/repairs/build_rights_translated.py) and refuse to go on if they differ.
Every partial is prepared before anything is deleted. push_one does a true replace
(delete, recreate, upload) and verifies with count(*) -- uploads APPEND.

Withdrawals take effect at the next release; Ben publishes. Dry-run by default;
APPLY=1 applies. NOT YET RUN.
"""
import os, sys, csv
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_translated_rights")
import redivis
from red_up.push import push_one

STAGE = Path("/home/ben/irw-stage/2401-audit/itemtext")
SCRATCH = STAGE / "withdraw_translated_rights"

WHOLE = {
    "irw_text": {"sun_2025_morality_study2_meaning__items"},
    "irw_text_2": {"jablonska_2020_swls__items"},
}
PARTIAL = {
    "irw_text_2": {
        "queiros_2018_qcae__items": {f"QCAE_{i}" for i in range(1, 7)},
        "gomez_2022_qcae__items": {"QCAE1r", "QCAE2r"} | {f"QCAE{i}" for i in range(3, 7)},
        "powell_2018_qcae__items": {f"QCAE{i}" for i in range(1, 7)},
    },
}
# Named survivors: same study families, not the blocked instruments. A name match is
# a lead, never a verdict -- these are what a careless sweep would take with it.
KEEP = {
    "irw_text": {"sun_2025_morality_study1_meaning__items"},   # re-read pending (#2401)
    "irw_text_2": {"jablonska_2020_rses__items",
                   "jablonska_2020_instagram_addiction__items"},
}
SHARDS = sorted(set(WHOLE) | set(PARTIAL))


def published(shard):
    return {t.name for t in
            redivis.user("datapages").dataset(shard, version="current").list_tables()}


# --- every target must be published; report the keep-set ---
for shard in SHARDS:
    cur = published(shard)
    targets = WHOLE.get(shard, set()) | set(PARTIAL.get(shard, {}))
    missing = targets - cur
    if missing:
        sys.exit(f"ABORT: not published in {shard}: {sorted(missing)}")
    print(f"{shard}: {len(WHOLE.get(shard, ()))} whole, {len(PARTIAL.get(shard, {}))} "
          f"partial, all present; keep-set present: {len(KEEP.get(shard, set()) & cur)}")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, nothing uploaded, no draft opened.")
    print("Re-run with APPLY=1.")
    sys.exit(0)

# --- prepare every partial BEFORE anything is destroyed ---
SCRATCH.mkdir(parents=True, exist_ok=True)
prepared = {}
for shard, tables in PARTIAL.items():
    for name, drop in tables.items():
        src, out = SCRATCH / f"{name}.orig.csv", SCRATCH / f"{name}.csv"
        redivis.user("datapages").dataset(shard, version="current").table(name).download(
            str(src), overwrite=True)
        with open(src, newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        header, body = rows[0], rows[1:]
        icol = header.index("item")
        seen = {r[icol] for r in body} & drop
        if seen != drop:
            sys.exit(f"ABORT: {name} does not contain {sorted(drop - seen)}")
        kept = [r for r in body if r[icol] not in drop]
        if not kept:
            sys.exit(f"ABORT: {name} would be left empty -- that is a whole withdrawal")
        with open(STAGE / f"{name}.csv", newline="", encoding="utf-8") as fh:
            staged = list(csv.DictReader(fh))
        got = [dict(zip(header, r)) for r in kept]
        cols = sorted(set(header) | set(staged[0]))
        key = lambda d: tuple(d.get(c, "") for c in cols)  # noqa: E731
        if sorted(map(key, got)) != sorted(map(key, staged)):
            sys.exit(f"ABORT: {name}: text-level filter differs from the staged rebuild")
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
            w.writerow(header)
            w.writerows(kept)
        prepared[(shard, name)] = (out, len(kept))
        print(f"prepared {shard}/{name}: {len(body)} -> {len(kept)} rows")

# --- per shard: open the draft, delete the wholes, replace the partials ---
for shard in SHARDS:
    base = redivis.user("datapages").dataset(shard)
    base.create_next_version(if_not_exists=True)
    ds = redivis.user("datapages").dataset(shard, version="next")
    before = {t.name for t in ds.list_tables()}
    whole = WHOLE.get(shard, set())
    parts = set(PARTIAL.get(shard, {}))
    keep_before = KEEP.get(shard, set()) & before
    if (whole | parts) - before:
        sys.exit(f"ABORT: not in the {shard} draft: {sorted((whole | parts) - before)}")

    for name in sorted(whole):
        ds.table(name).delete()
        print(f"deleted: {shard}/{name}")
    for name in sorted(parts):
        out, n = prepared[(shard, name)]
        res = push_one(ds, out, name, n)
        if res.error:
            sys.exit(f"ABORT: replace failed for {shard}/{name}: {res.error}")
        print(f"replaced: {shard}/{name} -- {res.actual:,} rows confirmed by count(*)")

    after = {t.name for t in redivis.user("datapages").dataset(shard, version="next").list_tables()}
    assert before - after == whole, f"MISMATCH in {shard}: removed={sorted(before - after)}"
    assert parts <= after, f"ABORT: a partial target went missing in {shard}"
    assert KEEP.get(shard, set()) & after == keep_before, f"ABORT: {shard} keep-set changed"
    assert len(after) == len(before) - len(whole), f"unexpected table-count change in {shard}"
    print(f"OK {shard}: {len(whole)} removed, {len(parts)} replaced, keep-set intact.")

print("\nThe withdrawals sit in the drafts. They reach users at the next release, which Ben cuts.")
