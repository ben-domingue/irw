# Suggested `itemtext_issues.qmd` additions/updates — audit fix pass (2026-08-15)

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
