"""Withdraw the 26 item-text tables that ship on SILENCE for a named third-party instrument.

Counsel (Stanford library copyright, reply of 2026-10-08 to Ben's six item-text questions)
on "silence": copyright in scales is thin and a fair-use position exists, but the field has
an active licensing market and a pattern of enforcement and trolling, so redistributing a
named instrument's wording without permission or certainty about its terms is HIGH RISK
relative to other content. Ben ruled 2026-10-15: remove the live tables whose register row
rests on silence for a named third-party instrument. Study-authored and study-adapted
wording (the #2381 class ruling, the ISP/bank rows) is NOT in scope -- the depositor
originated that wording, which is counsel's easier case.

Scope was taken from `itemtext/instrument_rights_register.csv` on origin/main (305 rows):
the ship/ship_with_note rows whose clause is blank or secondhand because no originator grant
was ever located, restricted to named instruments, and the live tables those rows name.
That is a LOWER BOUND: pre-register batches shipped under the old "silence is permission"
rule with no row at all, and nothing here sweeps for them.

The register rows are flipped to `block` in the same PR (match patterns unchanged), so the
runner cannot re-ship these and the sweep reports further copies as leads.

STANDING RULE, also 2026-10-15: wording we hold but cannot upload is stored locally at
/home/ben/Dropbox/projects/irw/data/itemtext/ (Dropbox, not git). This script therefore
DOWNLOADS every target's published CSV there BEFORE deleting anything, and refuses to
delete a table whose local copy is missing or short.

Published tables, so the withdrawal takes effect at the NEXT release of irw_text /
irw_text_2; Ben publishes. Dry-run by default (downloads only); re-run with APPLY=1.
"""
import csv, os, sys
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_silence_2026_10_15")
import redivis
from ledger import record

LOCAL = Path("/home/ben/Dropbox/projects/irw/data/itemtext")

# table -> (shard, register family) ; shard from itemtext/live_tables.csv (2026-10-12)
TARGETS = {
    "mascherini_2021_meddiet__items":            ("irw_text_2", "MedDietScore"),
    "medvedev_2018_oxh__items":                  ("irw_text_2", "OHQ"),
    "kraft_todd_2017_panas__items":              ("irw_text_2", "PANAS"),
    "lee_2024_panas__items":                     ("irw_text_2", "PANAS"),
    "liu_2018_panas__items":                     ("irw_text_2", "PANAS"),
    "medvedev_2018_pan__items":                  ("irw_text_2", "PANAS"),
    "qi_2025_panas__items":                      ("irw_text_2", "PANAS-CN"),
    "ozkurt_2026_basic_psych_needs__items":      ("irw_text_2", "BNSSS"),
    "pierro_2018_assessment_s1__items":          ("irw_text_2", "RMQ"),
    "pierro_2018_assessment_s3__items":          ("irw_text_2", "RMQ"),
    "pierro_2018_locomotion_s1__items":          ("irw_text_2", "RMQ"),
    "pierro_2018_locomotion_s3__items":          ("irw_text_2", "RMQ"),
    "pierro_2018_tf_future_s4__items":           ("irw_text_2", "TFS"),
    "pierro_2018_tf_past_s4__items":             ("irw_text_2", "TFS"),
    "pierro_2018_selfforgive_s1__items":         ("irw_text_2", "SSFS"),
    "pierro_2018_selfforgive_s2__items":         ("irw_text_2", "SSFS"),
    "qi_2025_self_concept_clarity__items":       ("irw_text_2", "SCCS"),
    "amiot_2022_ucla_loneliness__items":         ("irw_text_2", "UCLA"),
    "gan_2015_ucla_loneliness__items":           ("irw_text_2", "UCLA"),
    "jutte_2024_loneliness__items":              ("irw_text_2", "UCLA"),
    "mhscdc_fried_2020_loneliness__items":       ("irw_text",   "UCLA"),
    "reinwarth_2023_loneliness3__items":         ("irw_text_2", "UCLA"),
    "ucla_BrummerHoffman_2021__items":           ("irw_text_2", "UCLA"),
    "shin2024_creactability_adaptability__items": ("irw_text_2", "Creactability"),
    "imos_1984__items":                          ("irw_text_2", "IMO"),
    "yao_2020_ius__items":                       ("irw_text",   "IUS"),
}
assert len(TARGETS) == 26

by_shard = {}
for t, (s, _) in TARGETS.items():
    by_shard.setdefault(s, set()).add(t)

# --- 1. confirm every target is published where live_tables.csv said ---
for shard, targets in by_shard.items():
    cur = redivis.user("datapages").dataset(shard, version="current")
    names = {t.name for t in cur.list_tables()}
    print(f"{shard}: {len(names)} published tables; {len(targets)} targets")
    missing = targets - names
    if missing:
        sys.exit(f"ABORT: not published in {shard}: {sorted(missing)}")

# --- 2. local copies BEFORE anything is destroyed (standing rule 2026-10-15) ---
LOCAL.mkdir(parents=True, exist_ok=True)
rows_at = {}
for shard, targets in by_shard.items():
    cur = redivis.user("datapages").dataset(shard, version="current")
    for name in sorted(targets):
        dest = LOCAL / f"{name}.csv"
        if not dest.exists() or dest.stat().st_size == 0:
            cur.table(name).download(str(dest), overwrite=True)
        with open(dest, newline="", encoding="utf-8") as fh:
            n = sum(1 for _ in csv.reader(fh)) - 1
        live_n = cur.table(name).get().properties["numRows"]
        if n != live_n or n <= 0:
            sys.exit(f"ABORT: local copy {dest} has {n} rows, live has {live_n}")
        rows_at[name] = n
        print(f"  saved {dest.name}: {n} rows")
print(f"local copies OK: {len(rows_at)} tables, {sum(rows_at.values())} rows")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- local copies written, nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

# --- 3. delete from each shard's draft; resumable (deletes TARGETS ∩ draft) ---
for shard, targets in by_shard.items():
    base = redivis.user("datapages").dataset(shard)
    base.create_next_version(if_not_exists=True)
    ds = redivis.user("datapages").dataset(shard, version="next")
    before = {t.name for t in ds.list_tables()}
    todo = targets & before
    print(f"\n{shard} draft tables before: {len(before)}; to delete: {len(todo)} "
          f"(already gone: {len(targets - before)})")
    for name in sorted(todo):
        ds.table(name).delete()
        print("deleted:", name)
    after = {t.name for t in redivis.user("datapages").dataset(shard, version="next").list_tables()}
    assert before - after == todo, f"MISMATCH in {shard}: removed={sorted(before - after)}"
    assert not (targets & after), f"targets still in {shard} draft: {sorted(targets & after)}"
    assert len(after) == len(before) - len(todo)
    print(f"OK: {shard} draft now {len(after)} tables, none of the targets remain.")
    if todo:
        for fam in sorted({TARGETS[t][1] for t in todo}):
            fam_t = sorted(t for t in todo if TARGETS[t][1] == fam)
            record(fam_t, dataset=shard, reason="rights", family=fam,
                   refs="counsel 2026-10-08; Ben 2026-10-15",
                   rows={t: rows_at[t] for t in fam_t},
                   note="silence on a named third-party instrument; local copy in data/itemtext",
                   script=__file__)
print("\nledger rows written to itemtext/withdrawals.csv")
