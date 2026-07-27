# IRW Item Text Schema

Verbatim field definitions, copied from https://itemresponsewarehouse.org/itemtext.html
(2026-07-27) so this skill doesn't need to re-fetch the page every run. This is the
schema of the **merged** `{table}__items.csv` — the output of joining the four
per-table tabs (instrument, sections, items, responses) on `table` / `section_id` / `item`.

| Field | Definition |
|---|---|
| `table` | Identifier used to link to the IRW response data. |
| `section_id` | Identifier for a group of items that share a common context; functions like `item_family`, annotating testlets and grouped items. |
| `item` | Persistent identifier for the probe being used to measure — matches the core IRW dataset's `item` field exactly. |
| `instrument` | Full, human-readable name or title for the instrument identified by `table`. |
| `instructions` | Literal text of the instructions provided to the participant for the overall instrument. |
| `section_prompt` | Literal text of a shared prompt (e.g. a reading passage) that applies to all items within a given `section_id`. |
| `item_text` | Literal text of the specific prompt or question associated with an `item`. |
| `correct_response` | Scoring key for a given `item`. Blank when there is no correct answer; multiple correct answers are semicolon-separated (e.g. `A;C`). |
| `option_text` | Literal text for a specific response option available for an item. May legitimately be missing for behavior-scored items. |
| `resp` | Response value assigned to a specific `option_text` — must match the numeric/ordinal values already present in the live response-level IRW dataset (`irw::irw_fetch(table)$resp`). |

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
