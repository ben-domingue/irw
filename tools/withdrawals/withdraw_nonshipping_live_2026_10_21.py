"""Withdraw 21 live item-text tables whose register rows say block or hold (2026-10-21).

The 2026-10-21 sweep ran `itemtext/sweep_instrument_rights.py --version current` over
all 303 `block` + `hold` rows against the three released text shards (irw_text v37.0,
irw_text_2 v17.0, irw_text_3 v5.3), then read the item text of every strong and weak
lead on Redivis. Only tables where the shipped wording is a sentence-level reproduction
of the non-shipping instrument are here. Evidence per table:
oneoff/itemtext-rights-bank/decisions_nonshipping_2026-10-21.csv (action == withdraw),
which this script reads rather than restating, so the committed evidence stays the
single source of truth for the target list.

Two findings the list records:

  The ERQ withdrawal of 2026-10-18 was incomplete. `sv-maia2_randelovic_2021_erq__items`
  (10 of 10, in item_text_translated) and `ecps_sahm_2024_emotion__items` (8) were still
  live three days after the instrument was ruled block and five other tables were pulled
  for it -- see irw-scoped-use-grant-ruling, #3082. A ruling does not reach the corpus
  on its own.

  The two Christensen WSSSF tables were ruled hold on 2026-10-18 (#3075) and the
  withdrawal never ran. Holds are not swept behind.

NOT included, and why:
   5 tables are the wrong instrument or an incidental overlap:
     conspiracy_asd__schizotypy__items is the Multidimensional Schizotypy Scale, not the
       Wisconsin short forms its hold row names -- it needs its own register row;
     gps_vangsness_2019__items is Lay's 1986 General Procrastination Scale, not Tuckman,
       and has no register row at all;
     c19prc_uk_mcbride_2021_vaccineattitudes__items overlaps the VCBS by one item inside
       an otherwise different battery;
     moon_2023_selfesteem__items is the Rosenberg, which ships on an express grant;
     gerou_2023_dass21__items is the English DASS-21 (public domain); its hold row covers
       the Greek translation only.
  12 further single-item block leads on generic stems were each read and each incidental
     (SWLS inside a wellbeing battery, PSS inside a burnout scale, and so on).
   4 tables need a ruling, not a withdrawal: dasilva_2019_hexaco24__items carries 24
     verbatim Brief HEXACO items and the register blocks only the HEXACO-PI-R, whose row
     has an empty match_item_text (the text sweep is blind to HEXACO entirely);
     cavalini_mokken__items and reinwarth_2023_domain_importance__items look like word
     lists under the 2026-10-17 rule and probably ship; yuebo_2024_netbenefit__items
     turns on the PsycTESTS question that needs PsycNET.

Same steps as withdraw_3017_tranche2_2026-10-17.py: confirm published, save local copies
to data/itemtext/ and row-count-check them against live BEFORE any delete, then delete
from each shard draft only when APPLY=1. The archive step already ran clean on
2026-10-21 via oneoff/itemtext-rights-bank/preflight_nonshipping_live_2026_10_21.py
(21 of 21, 1,781 rows), so it is re-checked here and skipped where the file is on disk.
Published tables leave the warehouse at the NEXT release, which Ben publishes.
Dry-run by default.
"""
import csv, os, sys
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_nonshipping_live_2026_10_21")
import redivis
from ledger import record

LOCAL = Path("/home/ben/Dropbox/projects/irw/data/itemtext")

# Resolved against this repo, not the main checkout: the decisions CSV lands with
# PR #3134 and may not be on main yet.
DECISIONS = (Path(__file__).resolve().parents[2]
             / "oneoff/itemtext-rights-bank/decisions_nonshipping_2026-10-21.csv")

with DECISIONS.open(newline="", encoding="utf-8") as fh:
    TARGETS = {r["table"]: (r["shard"], r["family"])
               for r in csv.DictReader(fh) if r["action"] == "withdraw"}
assert len(TARGETS) == 21, f"expected 21 withdraw rows, read {len(TARGETS)}"
print(f"read {len(TARGETS)} targets from {DECISIONS.name}")

by_shard = {}
for t, (s, _) in TARGETS.items():
    by_shard.setdefault(s, set()).add(t)

for shard, targets in sorted(by_shard.items()):
    cur = redivis.user("datapages").dataset(shard, version="current")
    names = {t.name for t in cur.list_tables()}
    print(f"{shard}: {len(names)} published tables; {len(targets)} targets")
    missing = targets - names
    if missing:
        sys.exit(f"ABORT: not published in {shard}: {sorted(missing)}")


def _retry(fn, what, tries=5):
    """Redivis throttling surfaces as AttributeError from the SDK's own error
    handler (see redivis-sdk-empty-error-attributeerror). Back off and retry."""
    import time
    for i in range(tries):
        try:
            return fn()
        except (AttributeError, Exception) as e:  # noqa: B014 - SDK masks the status
            if i == tries - 1:
                raise
            wait = 5 * (2 ** i)
            print(f"  retry {i+1}/{tries-1} on {what}: {type(e).__name__}; sleeping {wait}s")
            time.sleep(wait)


LOCAL.mkdir(parents=True, exist_ok=True)
rows_at = {}
for shard, targets in sorted(by_shard.items()):
    cur = redivis.user("datapages").dataset(shard, version="current")
    for name in sorted(targets):
        dest = LOCAL / f"{name}.csv"
        if not dest.exists() or dest.stat().st_size == 0:
            _retry(lambda n=name: cur.table(n).download(str(dest), overwrite=True),
                   f"download {name}")
        with open(dest, newline="", encoding="utf-8") as fh:
            n = sum(1 for _ in csv.reader(fh)) - 1
        live_n = _retry(lambda n=name: cur.table(n).get().properties["numRows"],
                        f"numRows {name}")
        if n != live_n or n <= 0:
            sys.exit(f"ABORT: local copy {dest} has {n} rows, live has {live_n}")
        rows_at[name] = n
        print(f"  archived {dest.name}: {n} rows ({TARGETS[name][1]})")
print(f"local copies OK: {len(rows_at)} tables, {sum(rows_at.values())} rows")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- local copies written, nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

for shard, targets in sorted(by_shard.items()):
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
               refs="register block/hold; non-shipping live sweep 2026-10-21; item text verified",
               rows={t: rows_at[t] for t in fam_t},
               note="register verdict block or hold; sentence-level reproduction verified against item text 2026-10-21; local copy in data/itemtext",
               script=__file__)
print("\nledger rows written to itemtext/withdrawals.csv")
