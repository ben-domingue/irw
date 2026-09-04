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

**2. Re-running the early batches under the final ruleset.** The reliability run
showed the disagreement between runs is asymmetric: the second run committed a
value where the first left a blank on `sample` 11 times out of 60, `item format`
8, `measurement tool` 7 — against 1, 1 and 0 the other way.

That is not agent variance, it is **rule accumulation**. Batch 1 was tagged
before the `Workplace` atom, the dictionary/source contradiction rule, the
broadened `Likert Scale/selected response` definition and the multilingual
exception existed. Batch 7 had all of them. **The published corpus is therefore
not the product of one consistent ruleset**, and a re-run recovers roughly
10-15% more values on three columns.

Under the old ruling that re-run was forbidden. Under this one it is the obvious
next thing.

## Why this is the right call, recorded so it is not relitigated

The argument against is that published tags acquire a kind of authority, and
rewriting them makes the corpus a moving target for anyone who cited a version.
Redivis versioning answers that: every published version is immutable and
citable, so a fix produces a *new* version rather than editing an old one. The
reader who wants stability pins a version; the reader who wants correctness
takes the latest. Nothing is lost by improving.

The argument for is that the alternative is knowingly publishing a value we can
demonstrate is wrong, which is worse for a user than a blank.
