# Audit mode: Batch 14 — the four earliest-uploaded tables (issue #1645)

**Date:** 2026-08-30
**Scope:** `abouhashish_2025_chatgpt_attitudes`, `abukhalaf_2025_disaster_prep`,
`addy_2021_sdq_ghana`, `agogue_2020_self_perceived_creativity` — the four batch_001
tables that were uploaded and then removed from disk before being committed, so they
exist only on Redivis and had never been through the tooling.
**Total:** 4 tables

Recovered with `irw::irw_itemtext()` into `audit_staging/issue1645/`. Per #1645's comment,
the ask was two-sided: run `audit_batch.R` against live data, **and** confirm the
`data_labels` claim by actually opening each source file — all four carry a retroactive
`data_labels` / `NOT_NEEDED` row dated 2026-08-17 with identical boilerplate evidence,
which is an assertion made after the fact rather than a check that was run.

## Legend

- 🟢 **Green** — confirmed against source. No action.
- 🟡 **Yellow** — curation stays, but a documentable caveat is worth surfacing.
- 🔴 **Red** — genuine defect, needs review and likely replacement.
- ⚪ **Gray** — could not be confirmed either way.

## Summary

| | n |
|---|---|
| 🟢 Green | 2 |
| 🟡 Yellow | 1 |
| 🔴 Red | 1 |
| ⚪ Gray | 0 |

`audit_batch.R`: **4 PASS, no anomalies.** Set-level checks were never the risk here — the
defect below is invisible to them, because it is an `option_text`↔`resp` mapping error
within a resp set that matches live data exactly.

**Note on a false signal:** the first audit pass reported 4 WARNs for null/quoting form
plus "100% of rows have blank `option_text`" (abukhalaf) and "71.4%" (agogue). All were
artifacts of how the files were exported here (`irw_itemtext()` → `write.csv`), not
properties of the curation. `normalize_nulls.R` cleared all of them and the batch went to
4 PASS. Worth knowing that `audit_batch.R`'s blank-`option_text` check is sensitive to
whether absence is stored as `""` or the `NA` token.

---

## 🔴 Red (1)

### `addy_2021_sdq_ghana` — SDQ_7 response anchors are reversed against the source

The item text is **perfect**: all 10 `item_text` values are byte-identical to the source
`.sav`'s own variable labels, source typos preserved ("alot", "oten lose my temper",
"fidgiting", "headache,stomach-aches"). `data_labels` is correct and the codes ARE the
source column names.

The `option_text`↔`resp` mapping is not. The source assigns one value-label set to every
SDQ item — `0=not true, 1=somewhat true, 2=certainly true` — but the curation ships
**SDQ_7 reversed**:

| item | resp 0 | resp 1 | resp 2 |
|---|---|---|---|
| SDQ_1–6, 8–10 | not true | somewhat true | certainly true |
| **SDQ_7** | **certainly true** | somewhat true | **not true** |

SDQ_7 is "i usually do as i am told", one of the SDQ's five canonical reverse-scored items
(7, 11, 14, 21, 25), so the reversal looks like an assumption that the stored data is
already reverse-scored. The data says it is not:

- `r(SDQ_7, prosocial mean of SDQ_1/4/9) = +0.156` — **positive**. Compliance tracks
  prosociality, which is what raw storage predicts; pre-reverse-scored storage predicts
  negative.
- The source's own value labels for SDQ_7 state `0=not true`, same as every other item.

**Consequence:** a respondent who answered `0` on SDQ_7 is recorded in the itemtext table
as having said "certainly true", when the source says "not true". Every other item is fine.

**Recommended fix:** restore SDQ_7 to `0=not true, 1=somewhat true, 2=certainly true`, and
if reverse-scoring is thought to apply, record it in a `public_note` rather than by
silently flipping the anchors — reverse-coding is a property of the table, not the
instrument.

**Corroboration that the item↔text mapping itself is right** (independent of the labels):
the subscale block structure reproduces cleanly. Prosocial items 1/4/9 load on the
prosocial block at +0.698/+0.653/+0.557; symptom items 3/5/8 load on the symptom block at
+0.705/+0.548/+0.676. That is stronger evidence than the retroactive claim it replaces.

**Source-file quirks found along the way** (not IRW defects — IRW uses `SDQ_1..SDQ_10` only):
- The file also carries `SDQ1_CAT..SDQ25_CAT`, all 25 items labelled. That family is
  **offset by one column** relative to `SDQ_n`: `SDQ(n+1)_CAT = (SDQ_n + 2) mod 3` holds at
  100% for every pair tested, with identical NA patterns and 0.0% raw agreement. So one of
  the two label sets is shifted; content settles it in favour of `SDQ_n` (under the
  `SDQ_n` reading prosocial 1/4/9 = 1.11 sits above symptom 3/5/8 = 0.70; the shifted
  reading would put prosocial items at 0.47–0.53, i.e. the floor).
- `SDQ_6` and `SDQ_10` have no zeros at all (range 1–2, means 1.81/1.91) and correlate with
  nothing (|r| < 0.18 against both blocks). Possible data-entry problem in those two
  columns. Response-data concern, not itemtext.

---

## 🟡 Yellow (1)

### `abukhalaf_2025_disaster_prep` — 0–100% likelihood scale is undocumented

Item text matches the source `.xlsx` headers, and the schema use is right: the shared
matrix stem ("During this hurricane season, how likely is it that you will have the
following?") sits in `section_prompt`, with the sub-labels ("a) An emergency supply kit")
in `item_text`.

`option_text` is blank for all 33 rows. That is defensible — the 11 `resp` levels are a
0–1 slider with no per-point labels in the source — but the paper explains what the
numbers mean and none of it is recorded:

> Each behavioral construct was measured through a set of questions in a Likert or Rising
> scales format. The answers were translated into percentages, for example, Strongly
> Disagree (0.0%), Disagree (25%), Neutral (50%), Agree (75%), and Strongly Agree (100%).

So `resp` is a proportion, not an ordinal level, and `0`/`1` are 0% and 100% likelihood.

**Suggested website caveat:** *Responses for this table are proportions on a 0–1 scale
(0% to 100% likelihood), not ordinal Likert levels — the source study converted its
rising-scale answers to percentages. The source provides no text labels for individual
points, so `option_text` is empty by design.*

Also noted: the codes (`prep_kit`, `prep_evac_plan`, `prep_comm_plan`) are mnemonics
assigned by the processing script, not source column names — so `data_labels` describes the
text correctly but not how the code was tied to it. And the source's `prep_evac` column
contains a stray `0.5397` among otherwise 0.1-grid values, an averaged value leaking into
item-level data; the IRW script drops it.

---

## 🟢 Green (2)

### `agogue_2020_self_perceived_creativity` — fully confirmed

`study1.sav` (N=200, matching the dictionary) labels `SPCpre_1..SPCpre_6` with wording
**identical** to the shipped `item_text`. Codes ARE the source column names. Note the
curation picked the right file of three: `study2.sav` has the same six columns with **no**
labels.

`option_text` is populated only at `resp` 1 ("strongly disagree") and 7 ("strongly agree"),
blank for 2–6. That is correct, not a gap: the `.sav` carries no value labels for these
items, and the paper states only the endpoints — *"6-items ranging from 1 'strongly
disagree' to 7 'strongly agree'"*.

### `abouhashish_2025_chatgpt_attitudes` — content confirmed; provenance basis is mischaracterized

All 40 items check out against the source `.xlsx` headers (columns 6–45, four blocks of 10
matching the dictionary's Knowledge/Perceptions/Attitudes/Concerns). `option_text` is fully
populated 1–5 Strongly Disagree..Strongly agree.

Two things to record rather than fix:

1. **The code derivation is positional, not `data_labels`.** The codes are
   `item_01..item_40` — indices assigned by the processing script, not source column
   names. The existing row claims `data_labels` / `NOT_NEEDED` on the grounds that
   "numeric verification would add nothing", but positional assignment is the pattern the
   skill flags as highest-risk. It happens to be correct here — I diffed all 40 shipped
   texts against the header at each position and the alignment holds — but that check had
   never been run. The row should read as positional-and-verified, not exempt.
2. **The source headers are bilingual English/Arabic; only the English was shipped.** A
   reasonable choice, undisclosed. Two items also had whitespace normalized (a
   non-breaking space in item_22, a triple space in item_39). Minor, and notably the stray
   `" ."` in item_22 was preserved, so this was not aggressive rewriting.

---

## Follow-ups

1. Fix `addy_2021_sdq_ghana`'s SDQ_7 anchors (red, above). Needs an explicit decision on
   whether the table is meant to hold raw or reverse-scored responses.
2. Replace the four retroactive `mapping_verification.csv` rows with the real evidence
   above. Two become genuinely `data_labels`/verified; `abouhashish` should be recorded as
   positional-verified; `abukhalaf` as codes-assigned-by-script.
3. Add the abukhalaf caveat to `itemtext_issues.qmd`.
4. Response-data items for elsewhere: addy's `SDQ_6`/`SDQ_10` zero-free columns, and the
   `SDQ*_CAT` one-column offset in the source file.
