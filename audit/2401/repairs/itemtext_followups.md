# Item-text follow-ups from the #2401 rebuild batch

Drafts only. No item text has been edited or uploaded.

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
