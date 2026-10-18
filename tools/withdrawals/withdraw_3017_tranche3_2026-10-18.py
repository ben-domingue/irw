"""Withdraw 13 item-text tables whose register rows shipped on retired reasoning (#3017).

Tranche 3. The first two tranches worked the register's `block` rows. These come
from the opposite direction: rows still reading `ship` or `ship_with_note` whose
own notes say the verdict rests on SILENCE -- the reasoning Ben retired on
2026-10-15 after counsel. Thirteen such rows survived that flip; this withdraws
the tables behind them. Ben authorised 2026-10-18.

Every target was verified on 2026-10-18 by reading all 183 items, not by trusting
the sweep. That mattered twice:

  The sweep's match counts are LOWER BOUNDS and were badly low. It scored
  goldberg_2018_hpq_h at "6 of 39" when all 39 items are the Health Behavior
  Checklist, and WMD_bartczuk_2023 at 5 when the table is WMDS01-WMDS24 entire.
  There are no partial tables here; every one is a whole instrument.

  Two tables are NOT withdrawn, on Ben's R-wordlist ruling (2026-10-17) that a
  word list is not wording. cavalini_mokken carries 17 bare coping labels ("Keep
  windows closed", "Seek diversion") and moon_2023_pregnancy_stress 11 stressor
  categories ("Finantial worries", "Family problems") -- labels, no stems, no
  instructions. Their sibling moon_2023_spousal_support IS withdrawn: it carries
  authored sentences ("He tolerates my ups and downs and unusual behaviors").

Known not fixed by this: chen2022b_psychabuse uses full sentences as item CODES,
so the wording survives in the response table, which no item-text withdrawal
reaches. Withdrawn anyway; the response-side defect is recorded separately.

Same steps as withdraw_3017_tranche2_2026-10-17.py: confirm each table, save a
local copy to data/itemtext/ BEFORE any delete, then delete from each shard draft
only when APPLY=1. Published tables leave the warehouse at the NEXT release, which
Ben publishes. Dry-run by default.
"""
import csv, os, sys
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_3017_tranche3_2026_10_18")
import redivis
from ledger import record

LOCAL = Path("/home/ben/Dropbox/projects/irw/data/itemtext")

TARGETS = {
    "goldberg_2018_hpq_h__items":                ("irw_text",   "HBC-Vickers"),
    "WMD_bartczuk_2023__items":                  ("irw_text",   "WMDS"),
    "wu_2024_video_addiction__items":            ("irw_text",   "SVAS-Qin"),
    "chen2022b_psychabuse__items":               ("irw_text",   "CPANS-Deng"),
    "SABFI2_Gallardo_Pujol_2018_Constru__items": ("irw_text",   "SC-Vignoles"),
    "SABFI2_Gallardo_Pujol_2018_Trust__items":   ("irw_text",   "GTS-Yamagishi"),
    "SABFI2_Gallardo_Pujol_2018_Tight__items":   ("irw_text",   "TL-Gelfand"),
    "abdullah_2024_blqol__items":                ("irw_text",   "BLQoL"),
    "moon_2023_spousal_support__items":          ("irw_text",   "PPP-Curry"),
    "islam_2022_bsmas__items":                   ("irw_text_2", "BSMAS"),
    "ma2026_bsmas__items":                       ("irw_text_2", "BSMAS"),
    "dassean_2025_bsmas__items":                 ("irw_text_3", "BSMAS"),
    "shen_2025_bsmas__items":                    ("irw_text_3", "BSMAS"),
}
assert len(TARGETS) == 13

by_shard = {}
for t, (s, _) in TARGETS.items():
    by_shard.setdefault(s, set()).add(t)


def _retry(fn, what, tries=5):
    """Redivis throttling surfaces as AttributeError from the SDK's own error
    handler (see redivis-sdk-empty-error-attributeerror). Back off and retry."""
    import time
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            if i == tries - 1:
                raise
            wait = 5 * (2 ** i)
            print(f"  retry {i+1}/{tries-1} on {what}: {type(e).__name__}; sleeping {wait}s")
            time.sleep(wait)


# A target may be published (in `current`) or draft-only. Both are withdrawn, but
# they are not the same act: deleting a published table takes effect at the next
# release, deleting a draft-only one removes it outright and the extraction is
# gone unless the local copy exists. So read each table from the version that
# actually has it, and say which is which.
published, draft_only = {}, {}
for shard, targets in by_shard.items():
    cur = {t.name for t in redivis.user("datapages").dataset(shard, version="current").list_tables()}
    nxt = {t.name for t in redivis.user("datapages").dataset(shard, version="next").list_tables()}
    missing = targets - (cur | nxt)
    if missing:
        sys.exit(f"ABORT: not in {shard} at all: {sorted(missing)}")
    for t in sorted(targets):
        (published if t in cur else draft_only)[t] = shard
    print(f"{shard}: {len(cur)} published, {len(nxt)} draft; "
          f"{len(targets & cur)} target(s) published, {len(targets - cur)} draft-only")
if draft_only:
    print(f"DRAFT-ONLY (deleting removes these outright): {sorted(draft_only)}")

LOCAL.mkdir(parents=True, exist_ok=True)
rows_at = {}
for name, shard in sorted({**published, **draft_only}.items()):
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
               refs="register silence survivor; #3017 tranche 3 2026-10-18; item text verified",
               rows={t: rows_at[t] for t in fam_t},
               note=("shipped on the pre-2026-10-15 silence reasoning; ruled hold by Ben "
                     "2026-10-18; all items read and confirmed the whole instrument; "
                     "local copy in data/itemtext"),
               script=__file__)
print("\nledger rows written to itemtext/withdrawals.csv")
