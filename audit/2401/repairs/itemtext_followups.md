# Item-text follow-ups from the #2401 rebuild batch

Both fixes approved by Ben and applied 2026-09-30 in the worktree. Nothing was uploaded,
committed or pushed. Status is in "What's staged" at the end.

## tuason_2021_covid_coping_enjoy (`public_note` claim_edit)

The live `public_note` (batch_197 `provenance.csv`, uploaded 2026-09-11) describes the
response-data defect that the rebuild fixes:

> In the source data file the 0/1 selection columns were filled in only for the low and high
> well-being groups the paper analysed, so 321 of the 322 respondents in the middle well-being
> group are coded 0 on every item even though each selected five options; treat their zeros as
> missing, not as non-selection.

Once the rebuilt table is live, replace it with:

> Each respondent selected exactly five options. The source file's own 0/1 selection columns
> were filled in only for the low and high well-being groups the paper analysed, so IRW builds
> the items from the source's list of each respondent's picks: every respondent has their five
> selections coded 1 and the rest 0.

Do not ship this before the rebuilt response table: until then the old sentence is the true one.

## amatus_cipora_2024_fsmas_se (option_text, SE1-SE4)

The live `amatus_cipora_2024_fsmas_se__items` (irw_text, 45 rows) maps resp 1-5 to
yes / rather yes / partly partly / rather no / no for all nine items. The AMATUS codebook marks
SE1-SE4 as Reversed = yes, and the stored data are reverse-keyed on those four (e.g. SE2
"Studying mathematics is just as appropriate for women as for men": 223 of 258 at resp 5; all
inter-item correlations positive; the stored items sum to `score_FSMAS_SE`). Corrected
`option_text` for `FSMAS_SE1`, `FSMAS_SE2`, `FSMAS_SE3`, `FSMAS_SE4`:

| resp | option_text (corrected) | live (wrong) |
|---|---|---|
| 1 | no | yes |
| 2 | rather no | rather yes |
| 3 | partly partly | partly partly |
| 4 | rather yes | rather no |
| 5 | yes | no |

`FSMAS_SE5`-`FSMAS_SE9` stay as they are (1 = yes ... 5 = no). Suggested `public_note`
addition: "Items SE1-SE4 are stored reverse-keyed in the source, so on every item a higher
resp is the less stereotyped answer. The codebook's note that a higher sum means more
stereotype endorsement does not hold for the stored values."

## What's staged (2026-09-30)

Staging folder: `/home/ben/irw-stage/2401-audit/itemtext_round3/`. The live copies the
build read (`irw::irw_itemtext()`, current version) are in `live/` beside it.

**tuason_2021_covid_coping_enjoy: provenance only, nothing to upload.** The live
`__items` table (46 rows) has no `public_note` column, so it was not rebuilt. The
batch_197 `provenance.csv` row now carries the replacement `public_note` above, and its
`note` records the change (#2401).
- *Still owed, site repo (not touched):* the `tuason_2021_covid_coping_enjoy` entry in
  `irw_site/itemtext_issues.qmd` (around L2793) still has the old sentence. Replace its
  `issue:` block with the new text (drop the final period, per the page's convention).

**amatus_cipora_2024_fsmas_se: staged.** `amatus_cipora_2024_fsmas_se__items.csv` has 45
rows. `option_text` on FSMAS_SE1-SE4 is reversed (16 cells; the midpoint is unchanged).
SE5-SE9 and every other field are byte-identical to live, and literal "NA" is kept.
- Built by `audit/2401/repairs/build_itemtext_round3.py`.
- The table had no provenance row anywhere: it is pre-pipeline curated. A backfilled row
  is now in `itemtext/itemtables/pilot/provenance.csv`, with `mapping_basis=unknown`,
  `uploaded=unrecorded`, the fix in `note`, and the suggested sentence as `public_note`.
- Gates:
  - `irw-validate --profile upload`: ok.
  - `validate_items.R --table-sets`: PASS, with 9/9 items and the resp sets matching.
    It notes that `correct_response` is absent, as it is live; a Likert scale has none.
  - `check_provenance.R`: exit 0.
- Upload with `red_up`'s delete-then-recreate (`irw_text`). Then stamp `uploaded` in the
  pilot row.
- *Still owed, site repo:* `check_issues_page.R` now reports amatus as **DUE**, because
  it is live and has a `public_note` but no page entry. Add it after the upload:

  ```yaml
  - table: amatus_cipora_2024_fsmas_se
    issue: |-
      Items SE1-SE4 are stored reverse-keyed in the source, so on every item a higher
      resp is the less stereotyped answer. The codebook's note that a higher sum means
      more stereotype endorsement does not hold for the stored values
  ```
