Decision came back from Ben, and it changes what you should do next. Good work — the
sweep found the real problem and the attribution errors are already fixed off the back
of it. But **the renames are declined**, so don't queue them.

## What was decided

The 12 attribution errors are **fixed and verified** in the dictionary — 10 corrected
`Reference` strings plus 2 that were empty, each resolved from its DOI. That was the
critical half: `metadata/02_biblio.R` reads `Reference` into `biblio.csv`, so the site
had been publishing false citations. Two corrupted titles were fixed at the same time
(`burgess_2025_soas` said "children and adolescents" where the source says "children
and adults"; `gizaw_2023_phq9` was truncated).

**The remaining 15 tables will not be renamed.** Ben's reasoning, which I think is
right: a table name is an opaque identifier carried across the dictionary, biblio, tags
sheet, Redivis, `__items`, processing scripts and issue history, with no transaction
across those surfaces. A rename is guaranteed to be non-atomic, and a consistent
non-compliant name is better than an inconsistent compliant one. The convention is a
guideline, not a rule, and the factual claim about authorship lives in `Reference`,
which is now correct.

One rename did happen — `alomari_2025_student_questionnaire` -> `xie_2026_student_questionnaire`
— because it was already agreed on #1651 and unusually cheap. It is complete across
IRW3, `irw_text`, and the dictionary. Nothing else moves.

## Your three questions

**1. Commit the CSV — yes, but relabel it first.** It's the evidence behind the
decision and belongs in the repo. The hazard is the `proposed_name` column: as written
it reads as a work queue, and someone will pick it up in three months not knowing the
renames were declined. Before committing, add a header note to the file (a leading
comment row, or a short companion `naming_audit_README.md`) stating plainly that
renaming was **considered and declined** for the 15 remaining tables, with the reason,
and that `proposed_name` is documentation of what the correct name *would* be — not a
task list.

**2. TODO.md entries — not "rename 15 tables."** That would recreate exactly the
problem the decision closes. The right entries are:

- Add the naming gate: at the point the pipeline picks a table name, resolve the DOI
  and require the chosen surname to appear in the resolved author list. Include both
  carve-outs you documented (compound/particled surnames with the Turkish dotless-i
  mapping; Dataverse's depositor-only creator list needing the linked publication).
- Make script headers record the resolved author list alongside `DOI:`. This is the
  cheap half and probably the highest value per line — the fabrications happened in
  scripts whose headers had no author field at all.
- DOI column hygiene as its own item: 465 rows hold a dataset DOI in `DOI (for paper)`,
  which drives ~55 spurious year mismatches, plus 33 URLs, 22 `data doi: ` prefixes,
  10 PLOS `.sNNN` suffixes, 4 `not yet published`. This is a separate defect from
  naming and deserves its own issue rather than a line in this one.
- Optionally: the 6 tables you could not verify at all.

**3. Your count is off by one.** You reported 15 fabricated surnames; the CSV has **16**
rows carrying a `proposed_name`. `divia_2025_tiktok_fomo_shopping` is tabled under
`given_name_used` (the figshare creator is "Arifin, Divia Indira" — "Divia" is the given
name) but was dropped from the headline count. Worth correcting in the CSV note so the
numbers reconcile.

## Do not

- Do not rename anything, in the sheets or on Redivis.
- Do not implement the gate yet — propose it in TODO.md and let Ben schedule it.

## Context you may not have

#1686 has been retitled "Automated pipeline can invent first-author surnames: add a
naming gate" and its body rewritten to reflect all of the above. Read it before writing
the TODO entries so they match. Your report comment stands as-is and is still the
detailed evidence — nothing in it needs editing.

One correction now recorded there that came from your work: the claim in the original
handoff that the errors localize to the 6/23/2026 batch was wrong, and your finding that
8/12/2026 carries the same fabrication *with the invented surname written into the
`Reference` too* is the reason. That was the most valuable thing the sweep turned up.
