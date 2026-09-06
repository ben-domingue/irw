# Administered-language backfill (irw#1777)

Measured 2026-09-01. The `_translated` / `language` columns entered the item text
schema on 2026-09-01 (#1774, #1777). Every table published before that predates
them. This directory measures how many published tables are affected and what
each one actually needs — it does not change anything.

## How the audit was built

1. `fetch_published_itemtext.R` pulls `irw_itemtext(<table>)` for every published
   item text table whose tags-sheet language is not English-only (291 of 560).
2. `classify_administered_language.py` judges **each text field separately**
   (`item_text`, `option_text`, `instructions`, `section_prompt`). Only two
   things can prove a field is not English:
   - a non-Latin script (CJK, Kana, Hangul, Cyrillic, Arabic, …);
   - Latin script carrying more than three non-ASCII letters (diacritics).

   Everything else is `NEEDS_REVIEW`. **Nothing is called non-English on the
   absence of English.**

   That rule is deliberately weak, because two stronger ones were tried and both
   produced confident wrong answers:

   - *"few English function words ⇒ non-English"* fires on word-list
     instruments. `amarilla_2020_barthel` ("Bathing", "Bladder", "Grooming"),
     `geography` ("Lusaka (city)"), `gilbert_meta_40` ("Add: 4 + 1") are all
     English and all score zero. It invented **21** non-English tables, caught
     only by reading samples by eye.
   - the same rule applied to short option labels ("Never", "A little")
     invented **45** false mixed-language tables before that.

   Both failures share one cause: English prose is only one of the shapes
   English item text takes, so a test tuned to prose reads every other shape as
   foreign. A backfill driven by either version would have machine-translated
   English word lists into English.

3. `audit_2026-09-01.csv` is the result, one row per table.

## Do not trust the tags sheet for this

`primary language(s)` in the tags sheet is a freeform column. It contains
`no access to the osf page`, `in ghana`, `i can't find the description of this
dataset`, and country codes (`afg`, `ken`, `bra`) where language codes belong.
It is usable to decide *which tables to look at* and never as the source for what
`language` should say. The shipped text and the paper are the evidence.

## What the audit found

| tier | tables | state | what it needs |
|---|---|---|---|
| **A** | 79 | at least one field is **provably** in the administered language | add `language`; generate `_translated` for the ADMIN fields only |
| **B** | 181 | ships English text | confirm the administered language, then either add `language` + `text_source=translated_substitute`, or close as a genuinely English study |
| **C** | 31 | pure ASCII and not provably either way, or empty | inspect by hand |

**The tier A count was published three times before it settled.** #1799 and commit
`16a8720` say **104**; `69f28f9` corrected that to **83** ("the classifier was
over-claiming"); this table and `audit_2026-09-01.csv` now say **79**. The CSV is
the measurement and the other two numbers are superseded. The last four moves were
`geography`, `gilbert_meta_84` and `preschool_sel_pl` (A -> B, confirmed English by
eye) and `brederecke_2020_sis` (A -> C, see below). Quote the CSV, never this
paragraph's history.

The tier A/C boundary is *proof*, not likelihood: a table lands in C when no
field carries a non-Latin script or a diacritic, which happens for word-list
instruments in any language.

**The per-field verdict is what drives the work, not the table verdict.** A
table can have Chinese stems and English anchors (`aslec_insomnia_wang2025`,
`isi_insomnia_wang2025`) or the reverse. Only fields marked `ADMIN` get a
translated twin; a field already in English is its own translation and must
never be round-tripped through a translator.

Tier B is 181 tables, but 75 of them have no usable language tag at all, so an
unknown share are simply English studies needing no action. 180 of the 291
candidates have neither a provenance row nor an issues-page entry, so confirming
their administered language is a per-paper lookup.

## Two defects found on the way, unrelated to the backfill

- `metadata/itemtext_metadata.csv` carries `fcv19s_hossain_2022__fear`, a
  double-underscore duplicate of the real `fcv19s_hossain_2022_fear` — almost
  certainly a `__items` suffix-strip bug. `irw_itemtext()` returns nothing for it.
- The same file carries `eammi_grahe_2018_marriage_timing`, which names no table
  in `metadata.csv`.

## Backfill mechanics

Cheaper than it looks. **Each item text table is its own Redivis table**, so a
backfill is a per-table CSV re-upload (`red_up <dir>`), not row surgery on a
shared table. All the cost is in producing the corrected CSVs.


## Where the English comes from (decided 2026-09-01, ben-domingue)

**If the instrument's official documentation publishes an English version, ship
that.** No further adjudication needed. Many tier A tables are well-known
instruments administered in translation — WHOQOL-BREF, UWES, IES-R, BFI, HEXACO,
ERQ, MAAS, MAIA, SHS, OLBI, RSES — and the publisher's own English is better
wording than any rendering written here.

Otherwise translate the administered text faithfully.

Either way `backfill_provenance.csv` records which, per table, in
`translation_source`:

The allowed values live in [`itemtext/provenance_vocab.csv`](../provenance_vocab.csv)
and are deliberately not restated here — `itemtext/check_provenance.R` validates
every provenance file against that one list and exits non-zero on anything else.
Two sessions added this column on the same day with two different vocabularies
(#1815 and #1820); one file, checked by something that fails, is what stops that
recurring.

The distinction is recorded rather than adjudicated because it is a real
difference: official English is a *parallel version*, not a translation of the
administered string, so if a local adaptation diverges from the original the
`_translated` column stops corresponding word-for-word to the base field. That
is an acceptable trade for better wording, but it should be legible to anyone
who later compares the two columns.

`instrument`, `instructions` and `section_prompt` usually have no official
parallel even when the items do — study-specific framing is written by the
authors — so a table is commonly `mixed`: official English for the items and
options, translated framing around them.


## File naming: the `__items` suffix is required

Staged files are `<table>__items.csv`, and the suffix is **not cosmetic**.

The Redivis table is named after the file's basename, minus the extension.
Every live table in `irw_text` is named `<table>__items`, so a file named
`<table>.csv` would upload as a **new table beside the existing one** rather
than replacing it — and `red_up` would refuse it outright, since a file without
the `__items` suffix is not eligible for `irw_text`.

This is easy to get wrong because `irw_list_itemtext_tables()` hides it:
`Rpkg/R/itemtext.R` does `sub("__items$", "", names)` before returning, so the
R package reports `burkert_2019_whoqol_bref` for a table actually called
`burkert_2019_whoqol_bref__items`. The first 78 files of this backfill were
written without the suffix on the strength of that listing, which would have
created 78 duplicate tables. Caught by ben-domingue before upload.

**Check before any upload**, against the raw Redivis names rather than the R
package's:

Item text is a shard list, so check every shard rather than naming one -- a
table that lives in an older shard is still an existing table.

```r
source("../../metadata/redivis_config.R")   # IRW_OWNER, IRW_TEXT_DATASETS
nm <- unlist(lapply(IRW_TEXT_DATASETS, function(ds)
  vapply(redivis::user(IRW_OWNER)$dataset(ds)$list_tables(),
         function(t) t$name, character(1))))
fs <- sub("\\.csv$", "", list.files("staged", pattern = "__items\\.csv$"))
sum(!fs %in% nm)   # must be 0 - anything else creates new tables
```

The `table` *column* inside the CSV stays the bare table name, with no suffix,
matching what the published tables carry.

## What has actually shipped, and by which of two parallel efforts

On 2026-09-01 two sessions worked this backfill at the same time without knowing
about each other. The work turned out to be **complementary rather than duplicated**
— verified: zero table overlap — but the record of it was split across a merged PR
and a branch that was never pushed, so this section is the single place that says
what is live.

| effort | tables | tier | state |
|---|---|---|---|
| tier A bulk (#1806/#1808/#1813) | 78 | A | built, verified, **uploaded**; `backfill_provenance.csv` |
| `spanishmegastudy` | 1 | A | deferred by size, #1809 |
| wording recovered from the paper (`8f35d6e`) | 3 | B, B, C | built, uploaded, doubled, **and since repaired**; `provenance.csv`, `published/` |
| round 2, the disclosure pass (`6bd1171`) | 17 | B (16) + 1 outside the audit | gated; **16 uploaded 2026-09-02**, 1 held — see below; `round2/` |

The three recovered-wording tables are the interesting ones: `baaziz_2023_sms2` and
`arzamoncunill_2023_epq_clinical` are **tier B** and `brederecke_2020_sis` is **tier
C**, which is to say the audit could not see their administered wording and going to
the paper found it anyway. That is the tier B/C remedy demonstrated on three cases,
not a shortcut around the tier A bulk.

### The three recovered-wording tables were doubled on Redivis — repaired 2026-09-02

Verified against live data 2026-09-02:

| table | rows staged | rows live | distinct rows | rows with no `language` |
|---|---|---|---|---|
| `baaziz_2023_sms2` | 126 | **252** | 126 | 126 |
| `brederecke_2020_sis` | 55 | **110** | 55 | 55 |
| `arzamoncunill_2023_epq_clinical` | 151 | **302** | 151 | 151 |

This is exactly the #1810 append signature — every table at 2x, half the rows
carrying `language` and half not, because the pre-backfill version survived beside
the new upload. `irw_itemtext("baaziz_2023_sms2")` returns 252 rows for an 18-item
instrument, and each item appears twice with different text.

**These three were missed by the repair.** #1813 re-uploaded the 78 tier A tables
with the delete-then-recreate guard and they are now correct (COUNT(\*) = 7,984,
`language` on every row, verified 2026-09-02). These three were uploaded from a
branch that was never pushed, so nothing in the repair's scope knew they existed.
That is the concrete cost of the unpushed branch, and it is the strongest argument
in the corpus for #1810.

**Fixed 2026-09-02.** All three were re-uploaded with the delete-then-recreate guard.
Re-verified against live data by `COUNT(*)` on the same day: `baaziz_2023_sms2` 126,
`brederecke_2020_sis` 55, `arzamoncunill_2023_epq_clinical` 151 — each back to its
staged row count, each carrying `language` on every row. The table above records the
defect as it was measured; this paragraph is the outcome. `staging/` is kept because
it is the source the repair was made from.

**`brederecke_2020_sis` contradicts its own audit row and the audit row is the stale
one.** `audit_2026-09-01.csv` marks it `CANNOT BACKFILL` because `item_text` held
both languages in one field, which would need a base field split rather than an
added column. The split was made, deliberately and with the reasoning recorded in
`provenance.csv`; the table is live and `irw_site/itemtext_issues.qmd` already
describes the shipped German. The audit row is annotated rather than deleted, so the
disagreement stays visible.

## Round 2 — the disclosure pass (2026-09-01; 16 of 17 uploaded 2026-09-02)

The other half of the tier B bucket: 17 published tables that ship English for a
non-English administration where the wording genuinely could not be recovered from
the deposit or the paper's own supplements. No text changes. What changes is that
each table now *says so* — `language` names the administered language and the four
`_translated` columns are present and empty, which is the schema's signal that the
base text fields are not what respondents read. Every language is taken from the
table's own provenance note, not inferred here. `add_language.py` asserts, per row,
that no text field moved.

**Partly gated now.** `normalize_nulls.R` has run (0 of 17 needed fixing), and as of
2026-09-02 all 17 also pass `verify_backfill.py` against their cached live copies in
`round2/published/` — no text field moved, `language` is on every row, and every
`_translated` column is uniformly empty:

```
ITBF_SRC=itemtext/language_backfill/round2/published \
  python3 itemtext/language_backfill/verify_backfill.py itemtext/language_backfill/round2/staging
# 17 passed, 0 failed
```

**Fully gated 2026-09-02, and the gate caught one table.** `audit_batch.R` ran
against live *response* data — the check that the `item`/`resp` keys still join —
and returned **16 PASS, 1 FAIL**. The report is `round2/staging/audit_report.csv`
(committed in `95ce958`, swept in by a concurrent session rather than by this
workstream, which is why this section read as ungated for a day after it wasn't).

**`ALSECYPIAMH_WU_2022_SDQ` FAILED and was held.** Its staged file carried six items
where the live response table has five; the extra one is `SDQ_Pro`, the prosocial
subscale *total*, with 3 of the file's 18 rows. That defect was not introduced by
round 2 — the published table already carried it, at 18 rows — so the gate surfaced
a pre-existing error rather than a new one. See "The SDQ hold" below.

The other 16 were uploaded 2026-09-02 and verified live the same day: row counts
identical to `round2/published/`, `language` non-empty on every row, all four
`_translated` columns present, no doubling. `round2/staging/` was cleared by
ben-domingue on upload, as `itemtables/clean/` is; the files remain in git.

**Still owed:** provenance rows correcting `text_source` to `translated_substitute`.
The count in the earlier draft of this section was nine; measured against the batch
`provenance.csv` files it is **eleven** of the 16 uploaded — five `canonical_instrument`
(`ALSECYPIAMH_WU_2022_PHQ`, `abdullah_2024_bsq_sev24`, `bukurov_2022_sf36`,
`buzgova_2023_gai`, `buzgova_2023_lsita`) and six `study_materials`
(`almuqbil_2022_epds`, `altahla_2024_swls`, `altahla_2024_whoqol`,
`avilesgonzalez2019_ces`, `brederecke_2020_phq4`, `chen_2022_sasc`), plus
`ALSECYPIAMH_WU_2022_SDQ` if it ships. The remaining five already say
`translated_substitute`. Quote the measurement, not the nine.
Also owed: `abdullah_2024_bsq_sev24` has no issues-page entry.

Note that these rows do not live here — each of the 17 is an already-published table,
so its provenance row sits in the `itemtables/batch_NNN/provenance.csv` of the batch
that first extracted it (004 and 012 both carry an `ALSECYPIAMH_WU_2022_PHQ` row; that
duplicate is worth resolving while editing). There is no `round2/provenance.csv`.

### The SDQ hold

`ALSECYPIAMH_WU_2022_SDQ__items` was **removed from `irw_text` entirely** rather than
re-uploaded, and `irw_text` is now at v15.0 with 578 tables (v14.0 had 579). So the
table currently has *no* published item text, where before it had item text with three
bad rows.

**A corrected file is rebuilt and staged** at
`round2/staging/ALSECYPIAMH_WU_2022_SDQ__items.csv`, awaiting upload. It is the round-2
file with the three `SDQ_Pro` rows dropped — 15 rows over `SDQ_Pro1`..`SDQ_Pro5`, which
is exactly the item set `audit_batch.R` reports as live and the same set
`itemtables/batch_012/ALSECYPIAMH_WU_2022_SDQ__items.csv` ships. The round-2 file was
the right base rather than the batch_012 one: batch_012 predates the schema and would
drop the `language` and `_translated` columns, losing the disclosure this whole pass
exists to add.

Gates run 2026-09-02 on the rebuilt file: `normalize_nulls.R` normalized it (the
committed round-2 copy still carried literal `NA` strings — the pass's normalize run
was never committed back), `audit_batch.R` returns **PASS** — 5 live items, 5 candidate
items, item and resp sets both matching, canonical nulls, 0% missing item or option text
— recorded in `round2/staging/audit_report_sdq_recheck.csv` rather than in
`audit_report.csv`, which stays the round's own 17-table record. `irw-validate` returns
only the pre-existing `name_charset` WARN about the table's capitalised name, which is a
property of the response table, not of this file.

Worth noting what the bad rows actually were, because the extractor had already worked it
out and shipped them anyway: `SDQ_Pro`'s `item_text` reads "Not an item: this code is the
respondent's Prosocial Behaviour subscale score, the mean of SDQ_Pro1-SDQ_Pro5 rounded to
the nearest integer (reproduces exactly for all 7,841 respondents)". It is a column in the
study's deposit that the IRW processing script correctly does not ship, so it has no place
in an item text table — see the join-key rule in `.claude/skills/irw-auto-itemtext/SKILL.md`.

Two of the 17 turn on one unanswered question: **`altahla_2024` — Arabic or
Chinese?** #1777 calls it an Arabic administration while all three `altahla_2024_*`
provenance rows describe Chinese adults completing a Chinese-language version. The
staged files take the provenance's side — both say `Chinese` — so #1777's claim is
the outlier, and the likeliest explanation is that it was confused with
`almuqbil_2022_epds`, which is genuinely Arabic and sits three rows away in the same
batch. **Uploaded 2026-09-02 saying `Chinese`**, i.e. on the provenance's side; the
deposit confirmation was never made, so this remains an unconfirmed disagreement that
is now published.

Three tables that belong to this set could not be pulled, because they are not
published item text at all: `algner2022_oss` and `APFCompact_Ptacek_2024_DASS-21`
(never uploaded, provenance `uploaded` correctly blank) and
`altahla_2024_whoqol_bref`, whose provenance claims `uploaded=2026-08-17` but which
appears in neither `irw_itemtext()` nor `metadata/itemtext_metadata.csv` — it went
missing between staging and Redivis.

**The audit's candidate gate leaks.** `ALSECYPIAMH_WU_2022_PHQ` is in round 2 and is
not one of the 291 candidates, because the gate selected on the tags sheet that this
README's own caution calls unusable. `altahla_2024_whoqol_bref`, `algner2022_oss` and
`APFCompact_Ptacek_2024_DASS-21` are outside it too. 291 is a floor, not a
measurement.
