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
| **A** | 83 | at least one field is **provably** in the administered language | add `language`; generate `_translated` for the ADMIN fields only |
| **B** | 178 | ships English text | confirm the administered language, then either add `language` + `text_source=translated_substitute`, or close as a genuinely English study |
| **C** | 30 | pure ASCII and not provably either way, or empty | inspect by hand |

The tier A/C boundary is *proof*, not likelihood: a table lands in C when no
field carries a non-Latin script or a diacritic, which happens for word-list
instruments in any language.

**The per-field verdict is what drives the work, not the table verdict.** A
table can have Chinese stems and English anchors (`aslec_insomnia_wang2025`,
`isi_insomnia_wang2025`) or the reverse. Only fields marked `ADMIN` get a
translated twin; a field already in English is its own translation and must
never be round-tripped through a translator.

Tier B is 178 tables, but 75 of them have no usable language tag at all, so an
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

| value | meaning |
|---|---|
| `official_instrument_english` | the instrument publisher's own English for the same numbered items |
| `study_supplied` | this study's deposit or paper carried its own English rendering |
| `machine_translation` | translated here from the administered text |
| `mixed` | different fields from different sources — say which in the note |

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

```r
nm <- vapply(redivis::user("datapages")$dataset("irw_text:07b6")$list_tables(),
             function(t) t$name, character(1))
fs <- sub("\\.csv$", "", list.files("staged", pattern = "__items\\.csv$"))
sum(!fs %in% nm)   # must be 0 - anything else creates new tables
```

The `table` *column* inside the CSV stays the bare table name, with no suffix,
matching what the published tables carry.
