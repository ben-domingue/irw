"""Withdraw 47 live item-text tables whose register rows say block (#3017, 2026-10-17).

Second tranche against the 2026-10-15 silence ruling. Every target was verified on
2026-10-17 by reading the shipped item text on Redivis (irw v584): the wording is a
sentence-level reproduction of the blocked instrument, not an acronym match.

NOT included, and why:
  13 tables ship only a word or name list: the 11 PANAS adjective sets, the
     Matosas-Lopez BARS dimension labels and the Vermeiren ART author/foil list.
     Ben ruled 2026-10-17 that a word list is not wording -- see the R-wordlist
     clause on register rows 32, 55 and 169. They ship.
   6 tables were misidentified in the 2026-10-16 sweep and are not the blocked
     instrument at all (BSQ acronym collision, a lone self-esteem item, bare Big Five
     adjectives, an RSES row that ships, BFI-10 paraphrases, a study is own items).
     See oneoff/itemtext-rights-bank/withdraw_3017_blocked_2026-10-17.csv.

psychtools_sai IS included although it is the same shape as the PANAS tables -- the
STAI-S twenty-adjective checklist. Ben pulled it 2026-10-17 on enforcement risk
(Mind Garden), not on the copyright analysis, which would have kept it. Recorded so
the inconsistency with rows 32/55 reads as a decision rather than an oversight.

Related: FomoNegativeAffect_cremer_2026_panas__items was withdrawn 2026-10-16 as
PANAS/rights, released blank. Under R-wordlist that withdrawal is wrong and is
reversed by tools/repairs/restore_cremer_panas_2026_10_17.py.

Same steps as withdraw_silence_2026_10_15.py: confirm published, save local copies to
data/itemtext/ BEFORE any delete, then delete from each shard draft only when APPLY=1.
Published tables leave the warehouse at the NEXT release, which Ben publishes.
Dry-run by default.
"""
import csv, os, sys
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_block_register_2026_10_16")
import redivis
from ledger import record

LOCAL = Path("/home/ben/Dropbox/projects/irw/data/itemtext")

TARGETS = {
    "IJLS_Eersel_2024_IUS__items": ("irw_text_2", "IUS"),
    "IJLS_Eersel_2024_Work__items": ("irw_text_2", "UWES"),
    "alsecypiamh_wu_2022_swemwbs__items": ("irw_text", "SWEMWBS"),
    "amatus_cipora_2024_bfi_n__items": ("irw_text", "BFI"),
    "amatus_cipora_2024_stai__items": ("irw_text", "STAI"),
    "assessment_time_fournier_2025_upps__items": ("irw_text", "UPPS-P"),
    "ccapsvtskhpacr_mercedes_2023_beck__items": ("irw_text", "BDI-II"),
    "ccapsvtskhpacr_mercedes_2023_hada__items": ("irw_text", "HADS"),
    "ccapsvtskhpacr_mercedes_2023_sf__items": ("irw_text", "SF-12"),
    "cdm_mentalhealth_tan_2023_bsi__items": ("irw_text", "BSI"),
    "ding_2025_iu__items": ("irw_text_3", "IUS"),
    "facit_yount_2021_hadsx__items": ("irw_text", "HADS"),
    "florida_twins_grit__items": ("irw_text", "Grit"),
    "gao2025_attachment_anxiety__items": ("irw_text_2", "ECR-RS anxiety items"),
    "gilbert_meta_44__items": ("irw_text", "Short Warwick-Edinburgh Mental Well-bein"),
    "heard_roch_2022_whodas__items": ("irw_text", "WHODAS"),
    "heekerens2025_bfi_neuroticism__items": ("irw_text", "BFI"),
    "heekerens2025_bfi_openness__items": ("irw_text", "BFI"),
    "isi_insomnia_wang2025__items": ("irw_text", "ISI"),
    "kim_2025_isi__items": ("irw_text_2", "ISI"),
    "li_2026_imi_teq__items": ("irw_text_2", "IMI"),
    "mhscdc_fried_2020_motivation__items": ("irw_text", "SIMS"),
    "os_tbmwtfs_schubert_2023_cerq__items": ("irw_text", "ERQ/RRS"),
    "oxfordcovid_xue_2024_iusc__items": ("irw_text", "IUS"),
    "oxfordcovid_xue_2024_swemws__items": ("irw_text", "SWEMWBS"),
    "pezzuti_2025_coolpeople_adventurous__items": ("irw_text", "Schwartz PVQ"),
    "pezzuti_2025_coolpeople_benevolent__items": ("irw_text", "Schwartz PVQ"),
    "pezzuti_2025_coolpeople_conforming__items": ("irw_text", "Schwartz PVQ"),
    "pezzuti_2025_coolpeople_hedonistic__items": ("irw_text", "Schwartz PVQ"),
    "pezzuti_2025_coolpeople_main_big5_southkorea__items": ("irw_text", "Schwartz PVQ"),
    "pezzuti_2025_coolpeople_secure__items": ("irw_text", "Schwartz PVQ"),
    "pezzuti_2025_coolpeople_traditional__items": ("irw_text", "Schwartz PVQ"),
    "pierro_2018_assessment_s4__items": ("irw_text_2", "Regulatory Mode Questionnaire"),
    "pierro_2018_locomotion_s4__items": ("irw_text_2", "Regulatory Mode Questionnaire"),
    "pierro_2018_selfforgive_s3__items": ("irw_text_2", "SSFS"),
    "pierro_2018_tf_present_s4__items": ("irw_text_2", "TFS"),
    "psychtools_sai__items": ("irw_text", "STAI"),
    "qi_2025_self_construal__items": ("irw_text_2", "SCS"),
    "ren_2024_loneliness__items": ("irw_text", "UCLA-3"),
    "shin2024_creactability_creativity__items": ("irw_text_2", "Creactability"),
    "shin2024_creactability_quickness__items": ("irw_text_2", "Creactability"),
    "singh_2025_identity_grit__items": ("irw_text", "Grit"),
    "socialstereotype_hughes_2025_personality_other__items": ("irw_text", "BFI-2-XS"),
    "socialstereotype_hughes_2025_personality_self__items": ("irw_text", "BFI-2-XS"),
    "song_2025_wwb__items": ("irw_text_2", "EWBS"),
    "teq_novak_2021_spirit__items": ("irw_text_2", "DSES"),
    "yang_2023_emotional_eating_uppsp__items": ("irw_text_2", "UPPS-P"),
}

assert len(TARGETS) == 47

by_shard = {}
for t, (s, _) in TARGETS.items():
    by_shard.setdefault(s, set()).add(t)

for shard, targets in by_shard.items():
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
for shard, targets in by_shard.items():
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
        print(f"  saved {dest.name}: {n} rows")
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
               refs="register block; #3017 tranche 2 2026-10-17; item text verified",
               rows={t: rows_at[t] for t in fam_t},
               note="register verdict block; sentence-level reproduction verified against item text 2026-10-17; local copy in data/itemtext",
               script=__file__)
print("\nledger rows written to itemtext/withdrawals.csv")
