# IRW Item Text Schema

Verbatim field definitions, copied from https://itemresponsewarehouse.org/itemtext.html
(2026-09-01, updated for the administered-language columns agreed in irw#1777) so this
skill doesn't need to re-fetch the page every run. This is the
schema of the **merged** `{table}__items.csv` — the output of joining the four
per-table tabs (instrument, sections, items, responses) on `table` / `section_id` / `item`.

| Field | Definition |
|---|---|
| `table` | Identifier used to link to the IRW response data. |
| `section_id` | Identifier for a group of items that share a common context; functions like `item_family`, annotating testlets and grouped items. |
| `item` | Persistent identifier for the probe being used to measure — matches the core IRW dataset's `item` field exactly. |
| `instrument` | Full, human-readable name or title for the instrument identified by `table`. |
| `language` | Language the instrument was administered in, named plainly (`German`, `Spanish`) rather than as a code. Present when that language is not English. |
| `instructions` | Literal text of the instructions provided to the participant for the overall instrument. |
| `section_prompt` | Literal text of a shared prompt (e.g. a reading passage) that applies to all items within a given `section_id`. |
| `item_text` | Literal text of the specific prompt or question associated with an `item`. |
| `correct_response` | Scoring key for a given `item`. Blank when there is no correct answer; multiple correct answers are semicolon-separated (e.g. `A;C`). |
| `option_text` | Literal text for a specific response option available for an item. May legitimately be missing for behavior-scored items. |
| `resp` | Response value assigned to a specific `option_text` — must match the numeric/ordinal values already present in the live response-level IRW dataset (`irw::irw_fetch(table)$resp`). |
| `instructions_translated`, `section_prompt_translated`, `item_text_translated`, `option_text_translated` | English translation of the correspondingly named field. Present only for instruments administered in a language other than English. |

`instructions` and `section_prompt` are scoped differently: `instructions` applies to
the entire table regardless of `section_id`; `section_prompt` applies only to the items
sharing one or more specific `section_id` values. The same span of source text should
never be recorded in both fields. If framing or task-level text applies across the whole
table, record it once in `instructions`. If it is specific to a subset of items sharing
a `section_id` (e.g. a passage or context given before a testlet), record it in
`section_prompt` only, even if it superficially resembles instructional language.

**Administered language.** For a study administered in a language other than English,
the four text fields hold the wording respondents actually read, verbatim, `language`
names that language, and the English goes in the parallel `_translated` fields. `item`
and `resp` are join keys and are never translated. For an English administration,
`language` and the `_translated` columns are left out entirely rather than emitted
empty.

**The fallback, and what `language` holds in it.** When the administered original
cannot be recovered and only an English version exists, the English goes in the base
fields, the `_translated` fields stay empty, and `text_source=translated_substitute`
records the fallback.

`language` is populated **whenever the administration was non-English, regardless of
what the base fields contain** — it is defined as a fact about the study, not a claim
about `item_text`. So in the fallback a table reads `language=Chinese` while
`item_text` is English, and that combination is deliberate:

> **Populated `language` + empty `_translated` is the signal that the base fields are
> NOT the administered wording.** It is also the query that finds tables needing a
> later backfill (`language != '' AND item_text_translated == ''`). Leaving `language`
> empty here would make a fallback table indistinguishable from an English
> administration and destroy that query.

**Recoverability is scoped, so the test is decidable at extraction time.** Look in the
data deposit and the paper's own supplements. If the administered wording is there,
ship it; if it is not, take the fallback and say in provenance which files you checked
and that they contained no text in that script. Do not go hunting off-source for a
published original — that is a later pass, not a blocker.

Whether the shipped English is the authors' own rendering or a canonical instrument
does **not** change any of this. `text_source` distinguishes those (`study_materials`
vs `canonical_instrument` vs `translated_substitute`); the base/`_translated`/`language`
layout is the same either way.

See SKILL.md's core model section 4 for the full rule.

**`resp_raw`** (per the public schema page): when the scoring key can't be recovered —
i.e. the item is on some categorical/lettered coding in the source material that doesn't
map cleanly onto the numeric `resp` already in the live data — the raw categorical option
goes here instead of being forced into `resp`. **Caveat observed in the actual Sheets**:
the real per-table `responses` tab spells this column `raw_resp`, not `resp_raw` (seen in
`gilbert_meta_11`). Treat both spellings as the same field; `scripts/validate_items.R`
checks for either.

## Per-tab schema (the 4 source tabs, before merging)

Confirmed against two populated examples (`coach_chen_2022_phq9`, `gilbert_meta_11`) —
inspect a live example yourself before assuming this is exhaustive, sheets can vary.

- **instrument** (gid=0): `table, instrument, instructions`
- **sections** (gid=971697782): `table, section_id, section_prompt` — one row per section;
  use a single trivial `section_id` (e.g. `<table>_1`) with blank `section_prompt` when the
  instrument has no real testlet/passage grouping, rather than omitting the tab.
- **items** (gid=653192405): `table, section_id, item, item_text, correct_response`
- **responses** (gid=1308795295): `table, section_id, item, option_text, resp` (or
  `raw_resp` in place of `resp` — see above)

For a non-English administration each tab additionally carries the translated twin of
its own text field — `instructions_translated` on instrument (alongside `language`),
`section_prompt_translated` on sections, `item_text_translated` on items,
`option_text_translated` on responses — so the merge carries them through unchanged.

Merge logic (what `join.R` and `validate_items.R` do): start from `items`, then
successively `merge(..., all.x=TRUE)` with `sections`, `instrument`, `responses` on their
shared key columns (`table`, `section_id`, `item` as applicable).

## Non-negotiable validation gate

Before anything is written as final output, the merged data must satisfy — exactly, not
approximately:

- `unique(items_csv$item)` == `unique(irw::irw_fetch(table)$item)`
- `unique(items_csv$resp)` == `unique(irw::irw_fetch(table)$resp)` (only when a real
  `resp` column, not `raw_resp`, is populated — see `validate_items.R`)

`item` must always be drawn from the existing response data's item values — never
invented. Same for `resp`. If the source paper discloses a different item count than the
live data (this has happened, e.g. `fivpei_perrig_2023_attdiff`: 28 items in the paper vs.
21 in the data), or the item/response text can't be fully recovered, do not force a match.
Emit whatever partial structure is defensible and record the discrepancy — see SKILL.md's
"Can't fully automate" handling.
