# Topic tags for the conjoint family

**Status: ACCEPTED by Ben, 2026-10-11** ("i think this is fine so long as we
can allow for multi-select"; storage: "let's go with your preferred option").
Tracked on #2919, where "Tags for conj: not yet (Ben, 10-07)" was the open item.

## The question

Conjoint tables have no construct, instrument or item format, so the eight core
tag columns mostly do not apply, and the design records (`conj_metadata`,
`conj_outcomes`) already give language, country and outcome type mechanically.
Ben's driver was neither parity with core nor sample/age (deferred): it was
**topic**, "find the immigration conjoints", which nothing captured except the
free-text description.

## What was decided

1. **Two axes, not one.** `domain` = the setting of the study; `choice_object`
   = what a profile represents. The two are nearly independent (candidate
   tables are almost all `person`, climate tables mostly `policy`), and the
   second disambiguates the first at the seams (immigrant applicants versus
   immigration policy versus migrants choosing destinations).
2. **18 domains plus `other`, multi-select.** Derived bottom-up from all 921
   descriptions by one blind pass; the two values under a 2% floor
   (`corruption_accountability`, `housing_neighbourhoods`) were kept because
   multi-select lets scandal-attribute candidate tables carry both. The list is
   heavily political (11 of 18), which is the corpus, not the vocabulary.
3. **Domain is the setting, not the manipulated attribute.** "The gender
   conjoints" is a different question, partly answered by the attribute
   crosswalk; a third axis was considered and deferred.
4. **Storage: columns of `conj_metadata`, not a `conj_tags` table and not
   `03_tags.R`.** The core tags path is built around the eight-column Sheet
   schema and the per-source Sheet union; conj has no Sheet by ruling and
   different columns. Joining `data/conjoint/tags.csv` in stage 16 is the least
   machinery, the packages already filter on `conj_metadata` fields, and nothing
   stops a later promotion to its own table.
5. **Tags are living**, as for core (`1850_tags_are_living.md`): corrections go
   by PR against the source.

## How the first 921 rows were made

Pilot of ten tables confirmed by Ben against the draft vocabulary, then two
blind passes over every description (pass 2 saw the vocabulary and rules, not
pass 1's answers). Agreement: primary domain 98.2%, any shared domain 99.0%,
choice object 97.7%, identical on both axes 93.2%. The 30 conflicts were
adjudicated by hand and produced the rules now in `data/conjoint/README.md`
("Topic tags"): the vehicle rule, office versus job, groups are persons, cyber
by actor, food and farming, hypothetical countries. Where the passes agreed on
the primary and one added a secondary, the secondary was kept (recall over
precision for a search facet). Source: the table descriptions in
`dictionary_auto_conj.csv`, which were written from the deposits and were
adequate throughout; no deposit was re-read.

## Alternatives rejected

- **Eight to ten coarse domains, split later.** Easier to tag, but a user
  searching wants the finer grain, and the agreement numbers showed the finer
  grain was already reliable from descriptions alone.
- **A `conj_tags` irw_meta table through the `.irw_tag_sources` mechanism.**
  Keeps "tags" meaning one thing across sources and leaves room for sample and
  age range, but needs a per-source schema in both packages for two columns.
- **Folding `housing_neighbourhoods` and `corruption_accountability` into
  `other`.** Rejected once multi-select was accepted.

## Still open

- Package filters (`domain`, `choice_object`) in R and Python, and the MCP
  server, once the columns are live in `irw_meta`.
- Sample and age-range tags for conj, with the core rules: deferred.
- A manipulated-attribute axis: deferred; the crosswalk covers gender.
