# Tags are living: fix what can be fixed

**Status: RULED by Ben, 2026-09-04.** In his words: *"the tags should be 'living'
in the sense that there is nothing magic about any one version. if we can fix,
we should."*

This **supersedes the scope half** of the 2026-09-03 ruling recorded in #1704.

---

## What changed

On 2026-09-03, correcting existing tags was ruled out of scope. The reason was
good: small corrections to already-published tags had been crowding out the
actual goal, which was tagging the 1,427 tables that had no tags at all. The
ruling carried one exception — corrections were worth doing *"only insofar as
they fall out of making the tagger better."*

That job is done. The population is cleared (1,427 → 11), so the thing the
restriction was protecting no longer needs protecting.

The new rule is simpler and wider: **a tag that can be shown to be wrong gets
fixed.** No version of the published tags is authoritative over a later,
better one.

## What it does not license

It is a licence to **fix**, not to **churn**. Three things still hold:

- **A human row in the Sheet still wins** (#1723). This changes nothing about
  precedence.
- **Evidence, not preference.** "Wrong" means demonstrable against the source —
  the language of a Brazilian study recorded as Persian. It does not mean a
  different rater would have chosen differently on an ambiguous table. The
  #1850 reliability run found five tables per twelve where a second rater
  *could* land elsewhere; those are not errors and rewriting them would be
  noise, not repair.
- **Provenance still records every write** (`metadata/tags_provenance.csv`), and
  reverting is still deleting rows from `tags/tags_auto.csv` and re-running
  `03_tags.R`.

## The first two applications

**1. `dejesus_2017_lequesne`: `per` → `por`.** The tagger recorded Persian for a
Brazilian validation study — the source says Brazil five times and Iran none.
Found only because the #1850 reliability run tagged the same table twice and the
two runs disagreed.

**2. Re-tagging the 367 language-only rows.** Not, as first proposed, the early
batches — see the correction below.

`tags/tags_auto.csv` holds 367 rows carrying `primary language(s)` **and nothing
else**: the #1837 rollout staged that one column and never gave those tables
`item format`, `measurement tool` or `sample`. They were invisible to this
whole effort, because #1704 defined its target as *"no tag row"* plus
*"derived-age row only"*, and a row with one substantive value is neither. The
classifier counted them as tagged.

So there is a third under-tagged population the target definition missed, and it
is larger than the 11 tables left in the original one. Re-tagging it would add
roughly a thousand values across three published columns.

### A correction, recorded rather than quietly fixed

This file first said the reliability asymmetry was "not agent variance, it is
rule accumulation", and that a re-run of the early batches would recover 10-15%
more values. **The corpus does not support that.** Blank rates per batch, of
the four published columns:

| batch | tables | blank lang | blank fmt | blank tool | blank sample |
|---|---|---|---|---|---|
| 1 (fewest rules) | 149 | 9 | 7 | 0 | 22 |
| 7 (all rules) | 268 | 29 | 8 | 4 | 48 |

The batches tagged under *more* rules have *more* blanks, not fewer — partly
because the multilingual rule deliberately adds blanks, and partly because later
draws took harder shards. Whatever produced the run-to-run asymmetry on those 60
tables, corpus-level blank rates are not evidence for it, and the sample was
drawn only from tables that already carried a publishable value.

The honest statement is that **the asymmetry is real in the sample and its cause
is not established.** It should be reported that way in #1850 rather than
explained away.

## Why this is the right call, recorded so it is not relitigated

The argument against is that published tags acquire a kind of authority, and
rewriting them makes the corpus a moving target for anyone who cited a version.
Redivis versioning answers that: every published version is immutable and
citable, so a fix produces a *new* version rather than editing an old one. The
reader who wants stability pins a version; the reader who wants correctness
takes the latest. Nothing is lost by improving.

The argument for is that the alternative is knowingly publishing a value we can
demonstrate is wrong, which is worse for a user than a blank.
