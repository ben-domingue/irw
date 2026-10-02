"""Withdraw English IES-R wording: beck_2021_iesr's `*_translated` columns (partial)
and ali_2021_iesr's whole item-text table.

Ben ruled 2026-09-29 (irw#2401, audit/2401/RULES.md Decision 7) that an
instrument's `block` row in itemtext/instrument_rights_register.csv covers the
`*_translated` columns too. The IES-R row (family `IES-R`, Weiss & Marmar 1997,
"incl. translations/derivatives") is a block, kept by Ben on 2026-09-11.

beck_2021_iesr ships the German IES-R (Maercker & Schuetzwohl 1998) in its base
fields. The 2026-09-01 language backfill (itemtext/language_backfill/
backfill_provenance.csv, translation_source=official_instrument_english) added
English beside it: item_text_translated is Weiss & Marmar's English IES-R, 22 of 22
items verbatim apart from expanded contractions ("Any reminder brought back
feelings about it.", "I felt watchful and on guard."), and the instructions and
four anchors are English renderings of the German form. All four `_translated`
columns are blanked -- the holder's English is exactly what the block reserves,
and a rendering of the German is a derivative of the same instrument. The German
base fields are NOT touched here; whether they stay is a separate open question
(audit/2401/pilot/dossiers/beck_2021_iesr.md, proposed_outcome needs_ruling).

PARTIAL, not whole: the table stays, 88 rows, same item/resp keys, `language`
still German; only the four `_translated` columns go to NA. The expected output
is staged at /home/ben/irw-stage/2401-audit/itemtext/beck_2021_iesr__items.csv
(built by audit/2401/repairs/build_itemtext.py from the live copy); this script
re-derives it from the published table at the text level and refuses to push if
the two differ.

WHOLE: ali_2021_iesr (added 2026-09-29, Ben approved the full withdrawal). Its
item_text is itself the English Weiss & Marmar IES-R (22/22, read off the study's
S1 workbook headers) and its instructions are the Weiss preamble; it has no
`_translated` columns, so there is no unblocked wording to keep. The whole
`ali_2021_iesr__items` table is deleted from the draft. The RESPONSE table
ali_2021_iesr (a different dataset) is not touched.

The filter works on csv rows as strings, not through pandas: IRW's null is the
literal "NA", which a pandas round trip turns into an empty cell. push_one does a
true replace (delete, recreate, upload) and verifies with count(*) -- uploads
APPEND, so replacing is the only safe way to change a table.

Takes effect at the next release; Ben publishes. Dry-run by default; APPLY=1
applies. NOT YET RUN as of 2026-09-29: its itemtext/withdrawals.csv rows were written
by hand with `released` blank, so do not call ledger.record() again when applying.
"""
import os, sys, csv
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_iesr_translated")
import redivis
from red_up.push import push_one

SHARD = "irw_text"
TARGET = "beck_2021_iesr__items"                     # partial: _translated blanked
WHOLE = {"ali_2021_iesr__items"}                      # whole item-text table deleted
TRANSLATED = ["instructions_translated", "section_prompt_translated",
              "item_text_translated", "option_text_translated"]
STAGED = Path("/home/ben/irw-stage/2401-audit/itemtext/beck_2021_iesr__items.csv")
SCRATCH = Path("/home/ben/irw-stage/2401-audit/itemtext/withdraw_iesr_translated")
# Two Weiss & Marmar items, as a check that the column still holds what is being withdrawn.
WEISS = {"Any reminder brought back feelings about it.", "I stayed away from reminders of it."}

cur = {t.name for t in redivis.user("datapages").dataset(SHARD, version="current").list_tables()}
missing = ({TARGET} | WHOLE) - cur
if missing:
    sys.exit(f"ABORT: not published in {SHARD}: {sorted(missing)}")
print(f"{SHARD}: {TARGET} (partial) and {sorted(WHOLE)} (whole) present")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, nothing uploaded, no draft opened.")
    print("Re-run with APPLY=1.")
    sys.exit(0)

# --- prepare before anything is destroyed ---
SCRATCH.mkdir(parents=True, exist_ok=True)
src, out = SCRATCH / f"{TARGET}.orig.csv", SCRATCH / f"{TARGET}.csv"
redivis.user("datapages").dataset(SHARD, version="current").table(TARGET).download(
    str(src), overwrite=True)
with open(src, newline="", encoding="utf-8") as fh:
    rows = list(csv.reader(fh))
header, body = rows[0], rows[1:]
missing = [c for c in TRANSLATED if c not in header]
if missing:
    sys.exit(f"ABORT: published table lacks {missing} -- already withdrawn?")
idx = [header.index(c) for c in TRANSLATED]
itx = header.index("item_text_translated")
if not WEISS <= {r[itx] for r in body}:
    sys.exit("ABORT: item_text_translated no longer holds the Weiss & Marmar items")
kept = [[("NA" if i in idx else v) for i, v in enumerate(r)] for r in body]

# Must equal the staged rebuild, as rows (quoting may differ).
with open(STAGED, newline="", encoding="utf-8") as fh:
    staged = list(csv.DictReader(fh))
got = [dict(zip(header, r)) for r in kept]
key = lambda d: tuple(d.get(c, "") for c in sorted(set(header) | set(staged[0])))
if sorted(map(key, got)) != sorted(map(key, staged)):
    sys.exit("ABORT: text-level filter differs from the staged rebuild")
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
    w.writerow(header)
    w.writerows(kept)
print(f"prepared {TARGET}: {len(kept)} rows, {len(TRANSLATED)} columns blanked")

# --- open the draft and replace ---
base = redivis.user("datapages").dataset(SHARD)
base.create_next_version(if_not_exists=True)
ds = redivis.user("datapages").dataset(SHARD, version="next")
before = {t.name for t in ds.list_tables()}
if ({TARGET} | WHOLE) - before:
    sys.exit(f"ABORT: not in the draft: {sorted(({TARGET} | WHOLE) - before)}")
res = push_one(ds, out, TARGET, len(kept))
if res.error:
    sys.exit(f"ABORT: replace failed for {TARGET}: {res.error}")
print(f"replaced: {TARGET} -- {res.actual:,} rows confirmed by count(*)")
for name in sorted(WHOLE):
    ds.table(name).delete()
    print("deleted:", name)
after = {t.name for t in redivis.user("datapages").dataset(SHARD, version="next").list_tables()}
assert before - after == WHOLE, f"MISMATCH: removed={sorted(before - after)} expected={sorted(WHOLE)}"
assert TARGET in after and len(after) == len(before) - len(WHOLE), "unexpected table-set change"
print("\nThe withdrawal sits in the draft. It reaches users at the next release, which Ben cuts.")
