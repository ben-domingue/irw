# Item text corrections — handoff

State as of 2026-08-24. Nothing uploaded to Redivis. All work committed
(`78bc4e9`, `5e3ca13`).

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

## Ready to upload — no further judgment needed

Ten of the seventeen. Text identical to published, item and resp sets
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
| `double_marking_steele_2022` | #1616 | Only whole-content rewrite in the set (item_text similarity 0.019). Review as a rewrite. Separately: `presentation` has live resp 0/1 with no option_text row, and the boilerplate option_text problem is still unresolved. |
| `threat_isler_2024_exp4_cog_crt` | #1605 | `crt2`/`crt3` have no option_text although the scale has 4 response categories. Real gap. |
| `gilbert_meta_35` | #1615 | Knowingly incomplete (gated Dataverse). Shipping replaces an existing callout. |
| `gilbert_meta_42` | #1620 | Knowingly incomplete (gated openICPSR). Same. |
| `preschool_sel_akt` | #1611 | 47 of 48 items; `emtb4_6s_t1` prompt unrecoverable. Conditional callout depends on whether this is resolved first. |
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

1. Upload the 10 clean tables.
2. Paste their issues-page entries — including the three that **replace**
   existing live callouts (`gilbert_meta_35`, `gilbert_meta_42`,
   `sv-maia2_randelovic_2021_erq`), which only become true after upload. See
   `fixes/itemtext_issues_suggestions.md` and #1644.
3. Work the decision list above.
4. Close out #1645 (4 tables never checked by current tooling) and #1646 (13
   stale live callouts).
