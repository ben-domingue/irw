# Suggested `itemtext_issues.qmd` additions/updates — audit fix pass (2026-08-15)

## STATUS 2026-08-17 — HELD, PENDING UPLOAD OF THE `fixes/` CSVs

Confirmed with Ben 2026-08-17: **the corrected tables in `itemtext/fixes/*.csv` have NOT
been uploaded** — they are still in his todo pile. That is why most of this file is still
unpasted, and it is deliberate, not an oversight.

Three of the entries below (`gilbert_meta_35`, `gilbert_meta_42`,
`sv-maia2_randelovic_2021_erq`) would **replace existing callouts** on the live page with
more precise wording, and that wording describes the coverage of the *fixed* table — e.g.
"4 of 12 democratic-values items have no item text" is only true once
`fixes/gilbert_meta_35__items.csv` is live. **Paste these when the corresponding fix
uploads, not before**, or the page will describe a table that doesn't exist yet.

Current live wording, for comparison when the time comes:
- `gilbert_meta_35` — "codebook contain only 8 items, response data contains 12"
- `gilbert_meta_42` — "only item text for `phq` and `pss`"
- `sv-maia2_randelovic_2021_erq` — "Paper references a 1-7 scale, IRW table is on 1-5"

Already resolved, do not re-paste:
- `dumas_organisciak_2022` — **added to the live page 2026-08-17**. It was safe to add ahead
  of the fixes because it describes a paper-vs-live-data scale discrepancy, not the fixed
  table's coverage; verified directly against live data (resp values 1,2,3,4,5 over 10
  items, against the paper's stated 0-4).

Still conditional on Ben's judgment regardless of upload state:
- `political_psychology` — do not add without his confirmation that item numbering drifts.
- `preschool_sel_akt` — only if the `emtb4_6s_t1` prompt gap wasn't resolved before upload.

---

Draft only — nothing has been pasted into the live file
(`/home/ben/Dropbox/projects/irw/irw_site/itemtext_issues.qmd`, datapages/irw repo).
These are candidates for tables where a real gap remains even after the
drafted itemtext fix in `./fixes/`, or where a drafted fix rests on an
unverified assumption worth a public caveat. Format matches the site's
existing grid/callout convention.

---

## Update existing entry: `sv-maia2_randelovic_2021_erq`

The page already has an entry for this table ("Paper references a 1-7
scale, IRW table is on 1-5"). Even after the drafted fix in
`fixes/sv-maia2_randelovic_2021_erq__items.csv` (which compresses the
itemtext to a 1-5 scale to match live data), the specific 1-5 anchor
wording is inferred from the existing 1-7 labels, not source-verified
against the study's own 5-point instrument. Suggest **updating** the
existing callout rather than adding a new one:

```
::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## sv-maia2_randelovic_2021_erq
IRW table uses a 1-5 scale (paper's ERQ is normally 1-7); itemtext anchor labels for the 1-5 version are inferred, not sourced from the study's own materials
:::
:::
```

## New entry (only if item-ID drift is confirmed — do not add on speculation): `political_psychology`

The #1594 fix pass (group B) surfaced something bigger than the original
7-item finding: item numbers in this table may not be stable identifiers
— item 27's curated item_text ("friends with Republicans") doesn't match
its own live resp domain, which instead fits a different variable
(`votereport`) predicted by the build script's recode logic. This needs
Ben's confirmation before being treated as fact; only add if confirmed:

```
::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## political_psychology
Item numbering may drift between builds (items are assigned by column position, not variable name) — some item text/response-scale pairings may not be reliable; under investigation
:::
:::
```

## New entry: `gilbert_meta_35`

```
::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## gilbert_meta_35
4 of 12 democratic-values items (values_i/j/k/l) have no item text -- source (Harvard Dataverse) blocks automated access and the paper's full item wording lives in a supplementary appendix not otherwise available online
:::
:::
```

## New entry: `gilbert_meta_42`

```
::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## gilbert_meta_42
8 of 20 items (life_satisfaction_*, locus_of_control_*) have no item text -- instrument identity confirmed (Diener SWLS subset; locus-of-control battery) via the paper's own appendix, but exact per-item wording is gated behind openICPSR access
:::
:::
```

## New entry: `dumas_organisciak_2022`

```
::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## dumas_organisciak_2022
Paper describes originality coded on a 0-4 scale; live IRW data is 1-5. Whether this is an intentional +1 shift during processing or an unverified discrepancy is unresolved -- raw data file not available to check directly
:::
:::
```

## New entry (conditional — only if the gap isn't resolved before upload): `preschool_sel_akt`

Only needed if Ben doesn't independently resolve the one remaining gap
noted in the #1611 GitHub comment before uploading
`fixes/preschool_sel_akt__items.csv`.

```
::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## preschool_sel_akt
Emotion Matching Task item `emtb4_6s_t1` has no recoverable prompt text in the source LDbase codebook
:::
:::
```

## New entries (conditional — only when item text actually ships): `galindo_2023_beliefs`, `galindo_2023_emotional_intelligence`, `galindo_2023_loneliness`

Added 2026-09-01 at Ben's request, under #1751. These three tables were
reclassified `BLOCKED` → `AVAILABLE` in the Dataverse API sweep on the
**liberal bar** — Ben approved that call on condition it is noted here.

Why they are the unusual case: the Harvard Dataverse record
(`doi:10.7910/DVN/EDEVGY`) does **not** reproduce any item wording. Its
`Dataset_Documentation.docx` identifies each instrument exactly and pins every
code to its subscale (SS01-SS08 = MSPSS, Family SS01-02/05/07 and Friends
SS03-04/06/08; EI01-EI16 = WLEIS, SEA/OEA/UOE/ROE in blocks of four;
LN01-LN03 = Hughes et al. 2004 Short Loneliness Scale; all 1-5 Likert), and
`AVAILABLE` rests on those three instruments being freely published elsewhere —
the same bar already applied to GAD-7 and RSES in this audit.

That makes the eventual `item_text` **sourced from the instrument literature,
not from the study's own materials**, which is a genuine text-vs-table gap and
therefore in scope for this page. The concrete risk is language: the
documentation states the scales were "administered in each participant's
language" (Spanish, Basque and Greek), so English canonical wording would not
be what any respondent actually read.

Do not paste until `irw-auto-itemtext` has actually shipped these tables — the
callouts describe item text that does not exist yet. If the extraction instead
locates the administered translations, drop these entries rather than pasting.

```
::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## galindo_2023_beliefs
Item text is the canonical published wording of the Multidimensional Scale of Perceived Social Support, not wording taken from this study's materials -- the source deposit documents only the code-to-subscale mapping. Items were administered in Spanish, Basque or Greek depending on the respondent, so the English wording shown here is not what any respondent read.
:::
:::
```

```
::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## galindo_2023_emotional_intelligence
Item text is the canonical published wording of the Wong and Law Emotional Intelligence Scale, not wording taken from this study's materials -- the source deposit documents only the code-to-subscale mapping (SEA EI01-04, OEA EI05-08, UOE EI09-12, ROE EI13-16). Items were administered in Spanish, Basque or Greek, so the English wording shown here is not what any respondent read.
:::
:::
```

```
::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## galindo_2023_loneliness
Item text is the canonical published wording of the Hughes et al. (2004) Three-Item Loneliness Scale, not wording taken from this study's materials -- the source deposit documents only the code-to-subscale mapping. Items were administered in Spanish, Basque or Greek, so the English wording shown here is not what any respondent read.
:::
:::
```
