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

Cheaper than it looks. `itemtext/upload.py` does `dataset.table(<name>)` with
`replace_on_conflict`, so **each item text table is its own Redivis table** and a
backfill is a per-table CSV re-upload, not row surgery on a shared table. All the
cost is in producing the corrected CSVs.

## Round 1 — the three tables whose administered wording was in the source (2026-09-01)

Bucket B of the provenance-side scan: tables that shipped English while the administered
wording sat in the study's own paper or supplements, which is the recoverability test
SKILL.md sets. Ten other tables looked like this until that test was applied — their
originals are published, but off-source (WHO's Chinese WHOQOL-BREF, the canonical German
PHQ-4, a cited validation paper's Chinese PHQ-2-C), which makes them correct-as-shipped
fallbacks rather than misses.

| table | language | what changed |
|---|---|---|
| `baaziz_2023_sms2` | Arabic | All 18 items now carry the Arabic from the paper's Table 7; the authors' English moves to `item_text_translated`. |
| `brederecke_2020_sis` | German | Table 3's composite `English (German)` string is split — German to `item_text`, English to `item_text_translated`. |
| `arzamoncunill_2023_epq_clinical` | Spanish | 12 of 22 items get the administered Spanish from Appendix S3, plus the Spanish `instructions` stem; the other 10 have no published wording in any language and keep their English descriptor. |

`build_backfill.py` rebuilds all three from `published/` (pulled with `irw_itemtext()`) into
`staging/`. The diff against the live tables is deliberately narrow: only `item_text`
changes, plus `instructions` for the EPQ, plus the five new columns. `item`, `resp` and
`option_text` are untouched in all three.

**Anchors stay English in all three.** None of the three studies publishes its response
anchors in the administered language — the SIS paper states them in English and its `.sav`
labels values `1`..`5` with no text, the SMS-II paper gives `Not at all true` / `Very true`
only, the EPQ paper gives `very much disagree` / `very much agree` only. So `option_text`
keeps the English with an empty `option_text_translated`, which is the schema's documented
signal that those particular words are not what respondents read.

Gates: `validate_items.R` passes on all three against live data (item and resp sets exact),
`normalize_nulls.R` applied, `audit_batch.R` reports 3/3 PASS with no anomalies.
`lint_verification.R` emits two WARNs — `baaziz` and `brederecke` are recorded `NOT_NEEDED`
on a `paper_explicit` basis, which the linter flags because only `data_labels` is exempt.
That is expected here rather than a gap: both tables already hold a `VERIFIED` row from
batches 007 and 009, and this round adds no mapping inference to either. In the SMS-II the
Arabic and English share one numbered table row; in the SIS the German was already inside
the string being split. Only the EPQ carries new inference, and it is recorded `PARTIAL`
with the limits stated.

Not uploaded. `itemtext_issues.qmd` still describes the published tables correctly and
should be updated in the same pass as the upload — three entries go stale at that moment:
`baaziz_2023_sms2` ("the Arabic wording printed alongside it is not reproduced here"),
`brederecke_2020_sis` ("English wording followed by the German actually administered"),
and `arzamoncunill_2023_epq_clinical` ("None of the item text here is the wording
respondents read", which becomes true of 10 items rather than all 22).
