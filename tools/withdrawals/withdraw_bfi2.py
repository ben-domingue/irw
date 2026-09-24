"""Withdraw BFI-2 wording from the live item-text corpus.

Ben ruled 2026-09-10 on batch_163's escalation. The rights holder is the Berkeley
Personality Lab (Oliver P. John, Christopher J. Soto), whose own BFI page states
"it is freely available for researchers to use for non-commercial research
purposes" and "At this time, the BFI-2 is for non-commercial uses only", and gates
the wording behind a registration step. Under the 2026-09-05 HEXACO rule -- any
stated use restriction attached by the rights holder to the published source of the
wording -- that blocks, and IRW's own non-commercial research use is not a defence
because IRW redistributes to users whose use it cannot condition.

WHY THIS IS AN irw#1954 CASE. cormier_2024_personality shipped 2026-09-04 explicitly
on the grounds that the Colby page was Cloudflare-blocked and "no clause could be
quoted". The clause IS quotable, from ocf.berkeley.edu, and the batch_163
orchestrator re-confirmed it directly (page sha256
281322e0046d6db980b6fb1b27e2d7cdc398c541bed10f8085edda5a189d9499, 13,537 bytes,
both sentences present). A table cleared on an access failure rather than on a
reading is exactly the shape #1954 exists to re-audit.

SCOPE WAS WIDER THAN THE ESCALATION SAID. batch_163 named four tables. Reading the
published wording of every sun_2025/cormier item-text table found SEVEN wholly-BFI-2
tables -- three of them (study1_dependability, study1_respectfulness,
study3_compassion) were never in that list -- plus two MIXED tables and cormier.
Ben ruled: withdraw all eight whole, partial the two mixed.

A CODE SWEEP WOULD HAVE MISSED cormier ENTIRELY. Its item codes are Q20_1..Q20_16,
nothing resembling "bfi"; only reading the wording found it. Recorded because the
next person to scope an instrument block will reach for a code prefix first. Ben
ruled against a full-corpus wording sweep for now (2026-09-10): wider BFI-2 exposure
outside these two study families stays an irw#1954 re-audit item, NOT something this
run establishes. Nothing here should be read as proving the corpus is clean.

WHOLE-TABLE withdrawals -- every item is BFI-2, so there is no unblocked block to
preserve:
  sun_2025_morality_study1_compassion       4 items
  sun_2025_morality_study1_dependability    2 items
  sun_2025_morality_study1_respectfulness   4 items
  sun_2025_morality_study3_compassion       3 items
  sun_2025_morality_study3_extraversion     6 items
  sun_2025_morality_study3_neuroticism      6 items
  sun_2025_morality_study3_openness         6 items
  cormier_2024_personality                 16 items -- 15 BFI-2-XS plus one
      attention check ("For this question... please select Agree Strongly"),
      which is the only wording lost that is not BFI-2.

PARTIAL withdrawals -- mixed tables, a delete would destroy unrestricted wording:
  sun_2025_morality_study3_benevolence   drop itbfi227 ("Has a forgiving nature."),
      keeping two Big Five Aspect Scales items.
  sun_2025_morality_study3_dependability drop itbfi213, itbfi243, keeping two IPIP
      items.
The partial path downloads the published CSV and filters it at the text level rather
than round-tripping through pandas: IRW's null is the literal string "NA", which a
pandas read/write silently turns into an empty cell. push_one then does a true
replace (delete, recreate, upload) and verifies with count(*) -- uploads APPEND, so
replacing is the only safe way to shrink a table.

All ten are in irw_text. Withdrawals take effect at the next release; Ben publishes.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys, csv
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_bfi2")
import redivis
from red_up.push import push_one

SHARD = "irw_text"
WHOLE = {
    "sun_2025_morality_study1_compassion__items",
    "sun_2025_morality_study1_dependability__items",
    "sun_2025_morality_study1_respectfulness__items",
    "sun_2025_morality_study3_compassion__items",
    "sun_2025_morality_study3_extraversion__items",
    "sun_2025_morality_study3_neuroticism__items",
    "sun_2025_morality_study3_openness__items",
    "cormier_2024_personality__items",
}
PARTIAL = {
    "sun_2025_morality_study3_benevolence__items": {"itbfi227"},
    "sun_2025_morality_study3_dependability__items": {"itbfi213", "itbfi243"},
}
# Named survivors: same study families, confirmed NOT BFI-2 by reading their items.
# A name match is a lead, never a verdict -- these are the tables a careless sweep
# would have taken with it.
KEEP = {
    "sun_2025_morality_study3_honesty__items",      # itmcqh*, moral-character items
    "sun_2025_morality_study3_loyalty__items",      # itmcql*
    "sun_2025_morality_study1_honesty__items",
    "sun_2025_morality_study1_loyalty__items",
    "cormier_2024_phq4__items",
    "cormier_2024_cognitive_decline__items",
}
SCRATCH = Path("/tmp/claude-1000/-home-ben-Dropbox-projects-irw/"
               "cdee94fe-2904-4e40-996c-eb8e91fe34da/scratchpad/bfi2")

targets = WHOLE | set(PARTIAL)
cur = {t.name for t in redivis.user("datapages").dataset(SHARD, version="current").list_tables()}
missing = targets - cur
if missing:
    sys.exit(f"ABORT: not published in {SHARD}: {sorted(missing)}")
print(f"{SHARD}: {len(cur)} published tables")
print(f"  {len(WHOLE)} whole-table targets, {len(PARTIAL)} partial, all present")
absent_keep = KEEP - cur
if absent_keep:
    print(f"  NOTE: keep-set members not published: {sorted(absent_keep)}")
print(f"  keep-set present and must survive: {len(KEEP & cur)}")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, nothing uploaded, no draft opened.")
    print("Re-run with APPLY=1.")
    sys.exit(0)

# --- partials first: download and filter BEFORE anything is destroyed ---
SCRATCH.mkdir(parents=True, exist_ok=True)
prepared = {}
for name, drop in PARTIAL.items():
    src = SCRATCH / f"{name}.orig.csv"
    out = SCRATCH / f"{name}.csv"
    redivis.user("datapages").dataset(SHARD, version="current").table(name).download(
        str(src), overwrite=True)
    with open(src, newline="") as fh:
        rows = list(csv.reader(fh))
    header, body = rows[0], rows[1:]
    icol = header.index("item")
    kept = [r for r in body if r[icol] not in drop]
    dropped = len(body) - len(kept)
    seen_drop = {r[icol] for r in body} & drop
    if seen_drop != drop:
        sys.exit(f"ABORT: {name} does not contain {sorted(drop - seen_drop)}")
    if not kept:
        sys.exit(f"ABORT: {name} would be left empty -- that is a whole withdrawal")
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        w.writerow(header)
        w.writerows(kept)
    prepared[name] = (out, len(kept))
    left = sorted({r[icol] for r in kept})
    print(f"prepared {name}: {len(body)} -> {len(kept)} rows "
          f"(dropped {dropped}); items kept: {left}")

# --- open the draft and apply ---
base = redivis.user("datapages").dataset(SHARD)
base.create_next_version(if_not_exists=True)
ds = redivis.user("datapages").dataset(SHARD, version="next")
before = {t.name for t in ds.list_tables()}
keep_before = KEEP & before
print(f"\n{SHARD} draft tables before: {len(before)}")
if WHOLE - before:
    sys.exit(f"ABORT: whole-target not in draft: {sorted(WHOLE - before)}")
if set(PARTIAL) - before:
    sys.exit(f"ABORT: partial-target not in draft: {sorted(set(PARTIAL) - before)}")

for name in sorted(WHOLE):
    ds.table(name).delete()
    print("deleted:", name)

for name, (path, expected) in sorted(prepared.items()):
    res = push_one(ds, path, name, expected)
    if res.error:
        sys.exit(f"ABORT: partial replace failed for {name}: {res.error}")
    print(f"replaced: {name} -- {res.actual:,} rows confirmed by count(*)")

after = {t.name for t in redivis.user("datapages").dataset(SHARD, version="next").list_tables()}
removed = before - after
print(f"\n{SHARD} draft tables after: {len(after)}")
assert removed == WHOLE, f"MISMATCH: removed={sorted(removed)} expected={sorted(WHOLE)}"
assert set(PARTIAL) <= after, "ABORT: a partial target went missing entirely"
assert KEEP & after == keep_before, f"ABORT: keep-set changed: {sorted(keep_before - after)}"
assert len(after) == len(before) - len(WHOLE), "unexpected table-count change"
print(f"OK: exactly the {len(WHOLE)} whole targets removed; "
      f"{len(PARTIAL)} partials replaced; keep-set intact ({len(keep_before)} tables).")
print("\nWithdrawals sit in the draft. They reach users at the next release, which Ben cuts.")
