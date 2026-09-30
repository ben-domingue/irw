"""Withdraw rights-blocked English from two tables' `*_translated` columns.

Ben ruled 2026-09-29 (irw#2401, audit/2401/RULES.md Decision 7) that an
instrument's `block` row in itemtext/instrument_rights_register.csv covers the
`*_translated` columns too, and that a `_translated` flag confirmed as a block
instrument's wording is removed with no new ruling. The 2026-09-29 rights sweep
(itemtext/sweep_instrument_rights.py, now reading `_translated`) flagged 8 tables
only through those columns (audit/2401/triage/rights_translated.csv). Each was read
item by item (audit/2401/repairs/rights_translated.md); two are confirmed:

jablonska_2020_swls__items (irw_text_2) -- the whole table is the SWLS (block,
    2026-09-09), administered in Polish. item_text_translated is Diener's canonical
    English SWLS, 5/5 verbatim ("In most ways my life is close to my ideal.").
    item_text_translated and option_text_translated (the appendix's English anchors,
    a rendering of the Polish SWLS's) go to NA on all 35 rows, as for beck_2021_iesr.
queiros_2018_qcae__items (irw_text_2) -- the Portuguese QCAE. QCAE items 1-6 are
    Davis's IRI (block, 2026-09-06): PT items 1, 3, 4, 5, 6 and FS item 2.
    item_text_translated goes to NA for QCAE_1..QCAE_6 only (24 rows); the other 25
    items, the instructions and the anchors are the QCAE's own and stay.

PARTIAL, not whole: both tables keep their rows, keys and administered-language
base fields. Whether the translated base wording (Polish SWLS; Portuguese IRI items)
stays is a separate question for Ben, as it is for beck's German IES-R.

NOT HERE: sun_2025_morality_study2_meaning__items. It is the MLQ-Presence subscale
(tsmlq1..5, 5/5 MLQ in item_text_translated), and the MLQ row says translations are
covered, so its Chinese base is itself blocked: a whole withdrawal, held for Ben.

The expected outputs are staged at /home/ben/irw-stage/2401-audit/itemtext/
<table>__items.csv (built by audit/2401/repairs/build_rights_translated.py from the
live copies). This script re-derives each from the published table at the text
level and refuses to push if the two differ. The filter works on csv rows as strings,
not through pandas: IRW's null is the literal "NA". push_one does a true replace
(delete, recreate, upload) and verifies with count(*) -- uploads APPEND.

Takes effect at the next release; Ben publishes. Dry-run by default; APPLY=1
applies. NOT YET RUN as of 2026-09-29: its itemtext/withdrawals.csv rows were written
by hand with `released` blank, so do not call ledger.record() again when applying.
"""
import os, sys, csv
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_translated_rights")
import redivis
from red_up.push import push_one

SHARD = "irw_text_2"
STAGE = Path("/home/ben/irw-stage/2401-audit/itemtext")
SCRATCH = STAGE / "withdraw_translated_rights"

# table -> (columns to blank, items to blank them on (None = every row),
#           wording that must still be present, as a check of what is withdrawn)
TARGETS = {
    "jablonska_2020_swls__items": (
        ["item_text_translated", "option_text_translated"], None,
        {"In most ways my life is close to my ideal.", "I am satisfied with my life."}),
    "queiros_2018_qcae__items": (
        ["item_text_translated"], {f"QCAE_{i}" for i in range(1, 7)},
        {"I try to look at everybody’s side of a disagreement before I make a decision."}),
}

cur = {t.name for t in redivis.user("datapages").dataset(SHARD, version="current").list_tables()}
missing = sorted(set(TARGETS) - cur)
if missing:
    sys.exit(f"ABORT: not published in {SHARD}: {missing}")
print(f"{SHARD}: all {len(TARGETS)} targets present")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, nothing uploaded, no draft opened.")
    print("Re-run with APPLY=1.")
    sys.exit(0)

# --- prepare every table before anything is destroyed ---
SCRATCH.mkdir(parents=True, exist_ok=True)
prepared = {}
for target, (cols, items, expect) in TARGETS.items():
    src, out = SCRATCH / f"{target}.orig.csv", SCRATCH / f"{target}.csv"
    redivis.user("datapages").dataset(SHARD, version="current").table(target).download(
        str(src), overwrite=True)
    with open(src, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    header, body = rows[0], rows[1:]
    if not set(cols) <= set(header):
        sys.exit(f"ABORT: {target} lacks {sorted(set(cols) - set(header))}")
    idx = {header.index(c) for c in cols}
    it, itx = header.index("item"), header.index("item_text_translated")
    if not expect <= {r[itx] for r in body}:
        sys.exit(f"ABORT: {target}: item_text_translated no longer holds the blocked wording")
    kept = [[("NA" if (i in idx and (items is None or r[it] in items)) else v)
             for i, v in enumerate(r)] for r in body]
    with open(STAGE / f"{target}.csv", newline="", encoding="utf-8") as fh:
        staged = list(csv.DictReader(fh))
    got = [dict(zip(header, r)) for r in kept]
    key = lambda d: tuple(d.get(c, "") for c in sorted(set(header) | set(staged[0])))
    if sorted(map(key, got)) != sorted(map(key, staged)):
        sys.exit(f"ABORT: {target}: text-level filter differs from the staged rebuild")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        w.writerow(header)
        w.writerows(kept)
    prepared[target] = (out, len(kept))
    print(f"prepared {target}: {len(kept)} rows")

# --- open the draft and replace ---
base = redivis.user("datapages").dataset(SHARD)
base.create_next_version(if_not_exists=True)
ds = redivis.user("datapages").dataset(SHARD, version="next")
before = {t.name for t in ds.list_tables()}
if not set(prepared) <= before:
    sys.exit(f"ABORT: not in the draft: {sorted(set(prepared) - before)}")
for target, (out, n) in prepared.items():
    res = push_one(ds, out, target, n)
    if res.error:
        sys.exit(f"ABORT: replace failed for {target}: {res.error}")
    print(f"replaced: {target} -- {res.actual:,} rows confirmed by count(*)")
after = {t.name for t in redivis.user("datapages").dataset(SHARD, version="next").list_tables()}
assert after == before, "unexpected table-set change in the draft"
print("\nThe withdrawals sit in the draft. They reach users at the next release, which Ben cuts.")
