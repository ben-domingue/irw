# itemtext_issues.qmd entry — the four karajko2025_* tables

Decided on #1774: the English in these tables' `*_translated` columns was produced by the
extraction pipeline, not by the study, so it is disclosed on the public issues page.

Applies to `karajko2025_ai_benefit`, `karajko2025_ai_risk`, `karajko2025_ai_governance`,
`karajko2025_ai_trust` — all four from doi:10.7910/DVN/IREEJJ.

Why it meets the issues-page bar (a concrete text-vs-table caveat, not a gap the source
never published): the administered wording IS published and IS shipped, in Bosnian/Croatian.
What is not published is any English version — `ESM_4.pdf` is entirely Croatian and the
spreadsheet's parenthetical English glosses cover only the unrelated P4 block. So the English
a reader sees is ours, and that is exactly the kind of thing a user cannot tell from the data.

Paste the block below into `itemtext_issues.qmd`, before the final `:::` that closes the
`.grid` div. Four separate callouts rather than one, so a reader landing on any single table
sees it.

```qmd
::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## karajko2025_ai_benefit
Item text, response options and the block prompt are the administered Bosnian/Croatian, transcribed from the study's own questionnaire. The English in the `*_translated` columns is a **machine translation produced by the IRW extraction pipeline** — it is not the study's own wording and has not been reviewed or back-translated by a Bosnian/Croatian speaker. No English version of this block is published in the source record. Treat the translation as a reading aid, not as a validated English instrument
:::
:::

::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## karajko2025_ai_risk
Item text, response options and the block prompt are the administered Bosnian/Croatian, transcribed from the study's own questionnaire. The English in the `*_translated` columns is a **machine translation produced by the IRW extraction pipeline** — it is not the study's own wording and has not been reviewed or back-translated by a Bosnian/Croatian speaker. No English version of this block is published in the source record. Treat the translation as a reading aid, not as a validated English instrument
:::
:::

::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## karajko2025_ai_governance
Item text, response options and the block prompt are the administered Bosnian/Croatian, transcribed from the study's own questionnaire. The English in the `*_translated` columns is a **machine translation produced by the IRW extraction pipeline** — it is not the study's own wording and has not been reviewed or back-translated by a Bosnian/Croatian speaker. No English version of this block is published in the source record. Treat the translation as a reading aid, not as a validated English instrument
:::
:::

::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## karajko2025_ai_trust
Item text, response options and the block prompt are the administered Bosnian/Croatian, transcribed from the study's own questionnaire. The English in the `*_translated` columns is a **machine translation produced by the IRW extraction pipeline** — it is not the study's own wording and has not been reviewed or back-translated by a Bosnian/Croatian speaker. No English version of this block is published in the source record. Treat the translation as a reading aid, not as a validated English instrument
:::
:::
```

## Held, not applied

`itemtext_issues.qmd` lives in `datapages/irw`, where this account has pull but not push
(#1777). Land it by forking per the recipe Ben gave on #1696, or hand it to him.

## Two things to settle first

The `*_translated` and `language` columns are **not yet in the public schema** (#1777). Until
that is agreed there is no point publishing a callout that refers to columns the page does not
document — so this entry should land *after* the schema question, not before.

Separately, both `ai_benefit` and `ai_risk` carry a **construct** mismatch with their dictionary
descriptions, which is a different problem from the translation and is not covered by these
callouts. `ai_benefit`'s P7 asks how widely AI *is used*, not whether it is beneficial;
`ai_risk`'s P8 asks approval on a disapprove–approve scale, so a high `resp` means the
respondent approves. The questionnaire contains no benefit block and no risk block at all. That
needs its own dictionary correction and probably its own callout.
