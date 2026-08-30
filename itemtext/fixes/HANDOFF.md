# Item text corrections — handoff

> **Working directories archived 2026-08-29.** The audit diffs and the pilot
> extractions that fed this workstream now live in
> `itemtext/archive_v9_correction_workstream/`. They were being read as a live
> review queue. See `itemtext/audit_queue_status_20260829/README.md`.

State as of 2026-08-25. **The correction workstream is complete and released
as `irw_text` v9.0** (531 tables). All 17 corrections are resolved:

- **14 shipped**: the nine live since v8.0, plus `gilbert_meta_42` (12 of 20
  items), `double_marking_steele_2022`, `preschool_sel_akt` (65/65),
  `threat_isler_2024_exp4_cog_crt` and `gilbert_meta_35` (corrected mapping,
  8 items) released in v9.0.
- **3 resolved by removing the itemtext table**: `gilbert_meta_78`/`_80`
  (#1607/#1606, PPVT-4 / WJ-III licensing) and `political_psychology` (#1594,
  item-to-text mapping unverifiable). `dumas_organisciak_2022` (#1598) was
  uploaded but its table is being removed from IRW, so #1598 stays open on
  that separate decision.

v9.0 also released the 11 `batch_011` extraction tables.

### The failure mode worth carrying forward

`gilbert_meta_35` (#1615) is the one to remember. Its 8 published statements
had been laid onto items `values_a`..`values_h` in the order a paper listed
them, but the study's replication do-file builds the scale from
`values_a, c, d, e, f, g, i, j` — four non-scale items sit inside that range,
so every item after the first carried the next one's text. **7 of 8 wrong,
and live for months.**

Both gates passed it: the item *set* matched live data exactly, and each text
was individually plausible. `audit_batch.R` and `diff_itemtext.R` cannot see
this. What caught it was the source's own variable labels plus its replication
code naming the scale items.

**Rule:** anchor an item-to-text mapping in something that names items —
variable labels, a codebook keyed by variable name, replication code. Never in
the order statements appear in a paper. Where the anchor covers only some
items, ship those and omit the rest.

### Uploading replaces nothing — read this before shipping the rest

`upload_text.py` / `upload.py` **append** to an existing table. They do not
replace its contents, despite what #1644 and upload.py's own comments say.
`replace_on_conflict` replaces an *upload of the same name*; data inherited
from the prior version survives alongside it. A first attempt on 2026-08-24
produced 10 tables holding old rows **plus** new ones (e.g.
`singh_2025_identity_pit` at 45 rows, still carrying the orphaned `pit5`).

This never surfaced before because the extraction batches only ever created
*new* tables. Correction is the first workstream to overwrite existing ones.

**The working procedure:** delete the target tables from the draft version
first, then upload — they are recreated with only the new content. Verify with
an actual `count(*) / count(distinct item)` query, never `numRows`, which
reported stale values throughout the incident.

## What is now verified

The 17 corrected tables in `fixes/*__items.csv` have been through two checks
they had never been through before:

1. **`audit_batch.R`** — against live response data. `item_set_match` and
   `resp_set_match` are TRUE for all 17. 8 PASS, 9 WARN, 0 failures.
   Report: `fixes/audit_report.csv`.
2. **`diff_itemtext.R`** — against the currently published item text, i.e.
   what each upload would overwrite. Reports in `fixes/diffs_vs_published/`,
   `summary.csv` alongside.

16 of 17 have `mean_item_text_similarity = 1.000`: the corrected text is
identical to published wherever both carry text, and every structural change
maps to the filed issue. These are patches, not rewrites.

## Uploaded 2026-08-24 — pending release

Ten of the seventeen. Verified in the draft by query: rows and distinct-item
counts match the local files exactly for all ten. Text identical to published, item and resp sets
match live data, differences are exactly the filed defect:

| table | issue | change vs published |
|---|---|---|
| `ccapsvtskhpacr_mercedes_2023_tsk` | #1599 | option labels added |
| `chile_2023_social-welfare-survey_h` | #1602 | resp category restored |
| `dumas_organisciak_2022` | #1598 | `instructions` added |
| `shu_2025_translation_eib` | #1603 | resp category restored |
| `sv-maia2_randelovic_2021_hexaco60` | #1601 | 24 NA resp populated |
| `singh_2025_identity_pit` | #1619 | −1 orphaned item (`pit5`) |
| `singh_2025_identity_cse` | #1609 | option_text 0.82 — scale direction reversed, the intended repair |
| `sv-maia2_randelovic_2021_erq` | #1600 | option_text 0.81 — 1–7→1–5 rescale, the intended repair |
| `eammi_grahe_2018_npi` | #1613 | statements moved into `option_text`; gate's "100% blank item_text" is correct for a forced-choice instrument |
| `eammi_grahe_2018_socmedia` | #1604 | `SocMedia_bias_dummy` resp populated; row-count anomaly resolved below |

Caveat carried, not blocking: `erq`'s 1–5 anchor wording is **inferred** from
the 1–7 labels, not source-verified. Its replacement issues-page callout says
so and must be pasted with the upload.

## Needs a human before upload

Seven of the seventeen.

| table | issue | what needs deciding |
|---|---|---|
| `gilbert_meta_78` | #1607 | Reproduces actual **PPVT-4** target words (`ankle`, `appliance`…). Commercial instrument — **licensing call, not a data call.** |
| `gilbert_meta_80` | #1606 | Same, **WJ-III Picture Vocabulary** (`fork`, `fish`…). |
| `double_marking_steele_2022` | #1616 | **Done 2026-08-25.** Rubric item_text uploaded (108 rows). option_text deliberately left as the generic band descriptors per @xingyi-zhang. Fixed en route: duplicate `abstract` N/S rows, and `presentation`'s missing N/S rows. audit_batch.R now PASSes. |
| `threat_isler_2024_exp4_cog_crt` | #1605 | **Done 2026-08-25.** option_text for all 3 items and correct_response verified against the study's own Qualtrics .qsf (OSF grafm, Experiment 4): code 1 is the correct answer in all three items. Also fixed a wrong `table` value in the file (`..._cognitive_crt` -> `..._cog_crt`). audit_batch.R PASS. |
| `gilbert_meta_35` | #1615 | **Done 2026-08-25.** @joshgilbert1994 confirmed `values1k`/`_l` are real and that the `values1/2/3` prefix is the wave, so IRW's letters are the source's letters. The Dataverse **API** is not WAF-blocked (the web page is): the `.dta` variable labels name 6 items outright and `Replication_do_file.do` line 49 gives the 8-item scale as a,c,d,e,f,g,i,j. **The published text was wrong on 7 of 8 items** — laid onto a-h in order, shifted by the 4 non-scale items. Rewritten to 8 items x 4 options, b/h/k/l omitted, and the reversed option labels fixed on e/j. Uploaded and verified at 32 rows / 8 items; issues-page entry added for the 4 omitted items. |
| `gilbert_meta_42` | #1620 | **Done 2026-08-25.** Ships 12 of 20 items; the 4 `life_satisfaction_*` and 4 `locus_of_control_*` items omitted (no text available). Draft verified at 60 rows. Open follow-up on the issue: the `stress` section prompt does not fit `stress_b`/`stress_c`. |
| `preschool_sel_akt` | #1611 | **Done 2026-08-25.** Complete: all 65 items now carry text. @xingyi-zhang found `emtb4_6s_t1`'s prompt (it sits under the raw-score twin on the next page); verified against the codebook. Also confirmed the `emtb1_4`/`_5` reconstruction, and stripped a trailing "Scored" variable-label artifact from all 17 `akt*` items. Issues-page callout removed. |
| `political_psychology` | #1594 | **Not fixed.** Item numbers may be assigned by column position, not variable name. Needs confirmation before anything touches this table. |

### Not a defect — do not "fix"

`eammi_grahe_2018_npi` (#1613) shows *100% blank item_text* in the gate. That
is correct: NPI-13 is forced-choice, there is no item stem, and the two
statements live in `option_text` at resp 1 and 2. The gate cannot know this.

`eammi_grahe_2018_socmedia`'s row-count anomaly is resolved: `SocMedia_bias_dummy`
has n=140 against ~3,179 for its siblings, and every response is the value 1
(`lo=1 hi=1 n_lev=1`). Fewer rows, not more, so it is not item-code conflation.
It is a degenerate flag variable with zero variance — arguably not an item at
all, which is a **data-side** observation worth filing separately (same class as
#1618/#1622). It does not block the item text upload.

`gilbert_meta_78`/`_80` show *100% blank option_text*: PPVT and WJ are ability
items scored 0/1 with no labeled options. Their row-count anomalies are
basal/ceiling adaptive administration. Both expected.

## Out of scope for item text entirely

`#1614`, `#1617`, `#1618`, `#1622` need changes to response data, table names,
or the dictionary — no corrected `__items.csv` fixes them. They need a
data-side owner. `#1621` (`heekerens2025_bfi_neuroticism`) is a dictionary
Description edit belonging to the metadata pipeline; text is in
`fixes/heekerens2025_bfi_neuroticism_NOTE.md`.

## Shipping order

1. ~~Upload the 10 clean tables.~~ Done 2026-08-24, released in v8.0.
2. ~~Release the draft version.~~ Done 2026-08-25 as **v9.0**.
3. ~~After release, update the issues-page callouts.~~ Done 2026-08-25
   (datapages/irw `5295beb`): `gilbert_meta_35` added (8 of 12 items, and
   `values_e`/`_j` run in the opposite direction), `gilbert_meta_42` rewritten
   to match what shipped, `preschool_sel_akt` removed (gap closed). Original
   note follows: update **one** issues-page callout:
   `sv-maia2_randelovic_2021_erq` (its 1–5 anchors are inferred).
   `gilbert_meta_42`'s callout was already updated 2026-08-25 to match what
   actually shipped (12 of 20 items). `gilbert_meta_35`'s callout was **removed**
   2026-08-25 — its itemtext table is being pulled, so there is no text-vs-table
   mismatch left to describe. `dumas_organisciak_2022` was already added
   2026-08-17. See `fixes/itemtext_issues_suggestions.md` and #1644.
4. ~~Close the resolved issues.~~ Done: #1594, #1599, #1600, #1601, #1602,
   #1603, #1604, #1605, #1606, #1607, #1609, #1611, #1613, #1615, #1616,
   #1619, #1620, #1644. **#1598 stays open** on the separate
   `dumas_organisciak_2022` removal decision.
5. ~~Work the decision list above.~~ Done.
4. Close out #1645 (4 tables never checked by current tooling) and #1646 (13
   stale live callouts).
