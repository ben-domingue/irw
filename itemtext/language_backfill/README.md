# Administered-language backfill (irw#1777)

Measured 2026-09-01. The `_translated` / `language` columns entered the item text
schema on 2026-09-01 (#1774, #1777). Every table published before that predates
them. This directory measures how many published tables are affected and what
each one actually needs — it does not change anything.

## How the audit was built

1. `fetch_published_itemtext.R` pulls `irw_itemtext(<table>)` for every published
   item text table whose tags-sheet language is not English-only (291 of 560).
2. `classify_administered_language.py` judges **each text field separately**
   (`item_text`, `option_text`, `instructions`, `section_prompt`) on positive
   evidence only:
   - a non-Latin script (CJK, Cyrillic, Arabic, …) → administered wording;
   - Latin script with >3 non-ASCII letters → administered wording;
   - ≥25 words and a high English function-word ratio → English;
   - too little text to judge → `ASCII_SHORT`, which is *not* counted either way.

   The short-text guard matters: option labels like "Never" or "A little" carry
   almost no English function words, and an earlier version of this classifier
   read them as non-English and invented 45 false "mixed-language" tables.

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
| **A** | 104 | already ships the administered wording | add `language`; generate `_translated` |
| **B** | 178 | ships English text | confirm the administered language, then either add `language` + `text_source=translated_substitute`, or close as a genuinely English study |
| **C** | 9 | indeterminate or empty | inspect by hand |

Tier A splits three ways, and the split is per field, not per table:

- `ADMIN` (62) — every populated field is in the administered language.
- `ADMIN_ITEMS_ENG_PARTS` (30) — administered `item_text`, English options or
  instructions (e.g. `aslec_insomnia_wang2025`: Chinese stems, English anchors).
- `ENG_ITEMS_ADMIN_PARTS` (12) — the reverse.

Tier A volume: 4,721 distinct item stems and 4,779 distinct option labels,
~254k characters. Scripts: 84 Latin, 18 CJK/Kana, 1 Cyrillic, 1 Arabic.

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
