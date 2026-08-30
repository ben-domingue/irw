# Audit diff: addy_2021_sdq_ghana

Classification: **red — corrected file ready, awaiting upload approval**
Raised by: issue #1645 (verify the four earliest-uploaded tables)

## Summary

- item coverage: MATCH (10 of 10)
- item_text vs source variable labels: 10 of 10 byte-identical
- resp-set alignment: MATCH (0/1/2)
- **option_text: 1 item wrong — `SDQ_7` anchors reversed**

`audit_batch.R` reports PASS. It cannot see this defect: the resp *set* matches live data
exactly, and the error is in which anchor is attached to which value within that set.

## The defect

The source `.sav` (PLOS 10.1371/journal.pone.0250424, S1 File) assigns the same value-label
set to every SDQ item: `0 = not true`, `1 = somewhat true`, `2 = certainly true`.
The published curation ships `SDQ_7` reversed.

| item | resp 0 | resp 1 | resp 2 |
|---|---|---|---|
| `SDQ_1`–`SDQ_6`, `SDQ_8`–`SDQ_10` | not true | somewhat true | certainly true |
| **`SDQ_7`** (published) | **certainly true** | somewhat true | **not true** |
| **`SDQ_7`** (corrected) | not true | somewhat true | certainly true |

`SDQ_7` is "i usually do as i am told", one of the SDQ's five canonical reverse-scored
items (7, 11, 14, 21, 25), so the reversal looks like an assumption that the stored data is
already reverse-scored.

## Why the data says it is stored raw

- `r(SDQ_7, prosocial mean of SDQ_1/4/9) = +0.156` — positive. Compliance tracking
  prosociality is what raw storage predicts; pre-reverse-scored storage predicts negative.
- The source's own value labels for `SDQ_7` read `0 = not true`, identical to every other item.
- No source states that any column was reverse-scored before distribution.

Reverse-coding is a property of the table, not of the instrument. If it is later established
that this table does hold reverse-scored values, that belongs in a `public_note`, not in a
silent anchor flip.

## Change applied

2 rows in `addy_2021_sdq_ghana__items.csv`: `SDQ_7`/`resp=0` and `SDQ_7`/`resp=2`.
Nothing else touched. After the fix all 10 items carry one identical anchor set, matching
the source. `normalize_nulls.R` clean, `audit_batch.R` PASS.

## Not defects (checked, for the record)

- Item text preserves source typos verbatim — "alot", "oten lose my temper", "fidgiting",
  "headache,stomach-aches". Correct under the literal-transcript rule; do not tidy.
- The item↔text mapping is independently corroborated by subscale block structure:
  prosocial `SDQ_1/4/9` load on the prosocial mean at +0.698/+0.653/+0.557, symptom
  `SDQ_3/5/8` on the symptom mean at +0.705/+0.548/+0.676.

## Source-file quirks — not IRW defects, recorded for whoever touches this study next

- The file carries a second family, `SDQ1_CAT`..`SDQ25_CAT` (all 25 items labelled), which is
  **offset by one column** from `SDQ_n`: `SDQ(n+1)_CAT = (SDQ_n + 2) mod 3` holds at 100% for
  every pair tested, with identical NA patterns and 0.0% raw agreement. One of the two label
  sets is therefore shifted. Content settles it in favour of `SDQ_n`, which is what IRW uses:
  under the `SDQ_n` reading prosocial (1/4/9) = 1.11 sits above symptom (3/5/8) = 0.70, while
  the shifted reading would put prosocial items at 0.47–0.53, i.e. the floor.
- `SDQ_6` and `SDQ_10` contain no zeros at all (range 1–2, means 1.81/1.91) and correlate with
  nothing (|r| < 0.18 against both blocks). Possible data-entry problem in those two columns.
  Response-data concern, not itemtext.
