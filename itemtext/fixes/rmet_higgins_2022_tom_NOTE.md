# rmet_higgins_2022_tom — dictionary Description fix (not an itemtext change)

Issue: [ben-domingue/irw#1617](https://github.com/ben-domingue/irw/issues/1617)

**Scope note:** this is a fix to the IRW data dictionary's `Description`
field (produced by the `metadata/` pipeline / `irw-site-update` skill), not
to the itemtext content.

The table is named for the Reading the Mind in the Eyes Test, but its live
items are the **Imposing Memory Task** — a distinct secondary
Theory-of-Mind measure from the same paper. `rmet_higgins_2022_rmet` is the
actual RMET table.

@xingyi-zhang confirmed this on the issue (2026-08-26) and ruled out a
rename: renaming the Redivis table is disruptive, so the agreed fix is to
correct the Description so the table is not read as an RMET
administration.

**Corrected Description:**
> Imposing Memory Task (IMT), a story-vignette measure of theory of mind
> administered alongside the Reading the Mind in the Eyes Test in the same
> study; see `rmet_higgins_2022_rmet` for the RMET itself

Whoever next runs the metadata/dictionary pipeline should apply this text
for `rmet_higgins_2022_tom` in the IRW Data Dictionary sheet
(https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s).

The item text itself is correct — 16 story-vignette statements
(`TOM01`..`TOM16`, e.g. "Emma thought that her boyfriend Matt realized that
Hannah liked him.") that are unmistakably IMT recursive-mental-state items
and not eye-photo trials. One small itemtext follow-up: the `instrument`
field currently reads the generic "Theory of Mind" and would be better as
"Imposing Memory Task (IMT)". That is a one-field edit, worth folding into
whichever batch next touches this table rather than a re-upload on its
own.
