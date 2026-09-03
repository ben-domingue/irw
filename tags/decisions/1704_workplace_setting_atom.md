# Proposed: a `Workplace` atom for `sample`'s SETTING facet

**Status: PROPOSED, not ruled. Nothing in `vocab.md` or `TAG_VOCAB` has been
changed.** Put to Ben 2026-09-03. Written in the form #1760 established — the
case as it was put, so the answer's basis stays legible later.

Raised by the two-path comparison (#1704). It is P6's first clause, split out
because a vocabulary change is a different kind of decision from a
documentation fix, and every previous one — #1760, #1837 — was ruled
separately.

---

## The gap

#1760 split `sample` into two facets. SETTING answers *how were these people
reached*; FRAME answers *how broad was the sampling*. Under #1704 only SETTING
publishes.

SETTING has five atoms: `Educational`, `Clinical`, `Program-based`,
`Internet-based`, `Non-human`. **There is no atom for a workplace.** A study
that recruits hotel frontline staff through their employer, or nurses through a
hospital's nursing service, or teachers through a school district, has a real
and nameable recruitment channel, and the vocabulary cannot express it.

The rater then has three options and all of them are bad:

1. **Leave SETTING blank.** A false abstention on a *published* column — the
   tagger knew the answer and had nowhere to put it. This is what happened on
   `song_2025_sb` in the comparison run.
2. **Reach for `Targeted/specific`.** This is the common failure and it is
   worse, because that is a FRAME value answering a different question. A study
   can recruit through a workplace *and* impose no restriction beyond it, which
   under the #1796 amendment makes it `General/non-specific`.
3. **Reach for `Educational` or `Clinical`** because the workplace happens to be
   a school or a hospital. That silently reclassifies the study as being about
   students or patients when its respondents are staff.

## What the corpus already does about it

Measured 2026-09-03 against the Data Dictionary, matching descriptions and
references on occupational keywords (`employee`, `worker`, `nurse`, `teacher`,
`staff`, `burnout`, `job satisfaction`, `occupational`, …). **This is a keyword
proxy and an upper bound** — "teachers" recruited *as learners* in a training
study is legitimately `Educational`, and the regex cannot tell.

| | tables |
|---|---|
| occupational-looking, in the 1,427 untagged | **249** (17%) |
| occupational-looking, already tagged | 169 |

And what the 169 already-tagged ones say for `sample` today:

| value | tables |
|---|---|
| blank / `NA` | **97** |
| `Targeted/specific` | **48** |
| `Educational` | 23 |
| `Educational, Internet-based` | 10 |
| everything else | ≤4 each |

**That distribution is the argument.** Ninety-seven blanks and forty-eight
frame-values-standing-in-for-a-setting is not a distribution of opinions; it is
the shape of raters working around a missing category, and they worked around it
in two different directions. The 23 `Educational` rows are the ambiguous middle
the keyword proxy cannot resolve and a rule would have to.

## The proposal

Add `Workplace` to the SETTING facet, with this boundary:

> `Workplace` — respondents were reached **through their employer, their
> occupation, or a professional body**: an organisation's staff, a licensed
> profession, a union or professional register, a company panel.
>
> It describes the *channel*, not a restriction. Recruiting a hospital's nurses
> is `Workplace`; recruiting *nurses who have worked night shifts for five
> years* is `Workplace` plus a FRAME of `Targeted/specific`. The #1796
> amendment governs the frame half unchanged.
>
> Where the respondents are the institution's **clients** rather than its
> staff — students at a school, patients at a clinic — the existing atom
> applies and `Workplace` does not. A study of teachers is `Workplace`; a study
> of their pupils is `Educational`. A study that samples both takes both.

## Why this is lower-risk than it looks

**Adding an enum value is additive.** It invalidates nothing: all 2,257 rows
carrying a `sample` value keep exactly the value they have, and `tag_normalize.R`
enforces membership, not completeness. Only new tagging can use it.

The corollary is that adding it **does not by itself fix the 97 blanks and 48
frame-substitutions above** — those are existing tags, and correcting existing
tags is out of scope under the 2026-09-03 ruling. The value of the atom is
forward: 249 untagged tables, 17% of the remaining work, get a setting they can
express instead of a blank or a wrong-facet answer.

## The case against, put fairly

- **Six atoms is a bigger vocabulary to hold a boundary against.** `Workplace`
  and `Program-based` touch where the employer *is* the intervention, and
  `Workplace` and `Educational` touch on school staff. The rule above draws
  both lines, but it is one more line to get wrong.
- **It creates a visible inconsistency.** New tagging says `Workplace` where 48
  published rows say `Targeted/specific` for the same situation, and nothing is
  authorised to reconcile them. The column gets more correct and less uniform at
  the same time.
- **The 249 is a keyword proxy.** The true count is lower, and nobody has read
  a sample of them to find out how much lower.
- **It was measured on one confirmed sighting.** `song_2025_sb`, in a
  forty-table run. The corpus-level numbers above are inference from how other
  raters behaved, not from raters saying they were stuck.

## The question

1. Add `Workplace` to the SETTING facet with the boundary above?
2. If yes — does anything happen to the 48 `Targeted/specific` and 97 blank
   rows, or do they stay as they are under the "do not correct existing tags"
   ruling?

A "no" is a perfectly good answer, and the cost of it is known: roughly 249
tables keep producing a blank on a published column, and it stays legible in
`Status`/`Reason` as of #1859.
