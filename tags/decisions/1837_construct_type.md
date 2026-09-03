# Decision rules: `construct type`

**Status: proposed 2026-09-02, not yet ruled on.** Written in the form #1760
established — the case as it was put, so each answer's basis stays legible
later. Once ruled, the rules fold into
`tags/.claude/skills/irw-auto-tag/references/vocab.md`, which is what the tagger
reads; this file stays as the record of *why*.

Context: #1837 classified the tag columns by what kind of problem each is, and
Ben ruled on 2026-09-02 that **`construct type` takes the next definitional
effort** rather than `sample`. The argument was that it is the only column with
an *enforced* vocabulary and *no written rules* — eight values, and no guidance
anywhere on where the boundaries fall.

The precedent is `sample`. Writing its rules (#1760) and then amending them
(#1796) took its frame facet from 26.9% → 45.5% → 54.5% exact match **with no
change to the tagger at all**. If even part of that transfers, `construct type`'s
64.9% is a definitional problem rather than a model problem.

Every count below was measured 2026-09-02 from `metadata/tags.csv` (2,254 tables
carrying a `construct type`).

---

## Where the column stands

| value | tables | share of tagged |
|---|---|---|
| `Opinion/attitude` | 889 | 39.4% |
| `Affective/mental health` | 614 | 27.2% |
| `Cognitive/educational` | 523 | 23.2% |
| `Personality` | 209 | 9.3% |
| `Behavioral` | 209 | 9.3% |
| `Physical health/functioning` | 79 | 3.5% |
| `Developmental` | 74 | 3.3% |
| `Other` | 34 | 1.5% |

45 distinct combinations. **Only 343 of 2,254 rows (15%) carry more than one
value**, and the tagger's measured failure is under-tagging: 80% precision
against 70% recall (#1782). It names fewer facets than the gold set holds.

---

## Question 1 — Does the tag describe the table, or the study?

**This is the same question #1760 asked about `age range`, and it has the same
answer available.**

**36 of the 96 study families with six or more tagged tables give every table
the identical `construct type`** — 738 tables in total, a third of everything
tagged. For some families that is correct: `enem` (52 tables) and `imos` (34)
really are all `Cognitive/educational`, because every table in them is an exam.

For others it is a blanket. All **72** `c19prc_*` tables carry
`Affective/mental health, Opinion/attitude`, including:

| table | what it measures |
|---|---|
| `c19prc_uk_mcbride_2021_wordsum` | **verbal ability** |
| `c19prc_uk_mcbride_2021_phq15` | somatic symptoms |
| `c19prc_uk_mcbride_2021_conservatism` | political conservatism |
| `c19prc_uk_mcbride_2021_neighbourcohesion` | neighbourhood social cohesion |

`wordsum` is a vocabulary test. It is `Cognitive/educational` by any reading, and
it is tagged as neither. The pair describes the *study* — a COVID-era psychology
survey — and was applied to all 72 of its tables regardless of what each one
holds.

**Proposed rule.** The tag describes **what this table measures**, never what the
study was about. A family may end up uniform because its tables are alike; it
must not be uniform because they share a paper.

*Why this one first: it is the only rule here that can be checked mechanically
after the fact. A uniform family whose members measure visibly different things
is a flag, and 738 tables can be swept for it.*

## Question 2 — Is a second value the exception, or expected when two apply?

The tagger under-tags. 15% of rows are multi-valued; recall (70%) trails
precision (80%) by ten points, which is the signature of naming one facet where
the key holds two.

Nothing in `vocab.md` says whether multi-tagging is encouraged or grudging, so
"how many values" is currently a matter of individual temperament. That is
exactly the kind of undefined question that made `sample`'s whole-cell match a
dead number.

**Proposed rule.** Name **every** facet the instrument genuinely measures, not
the single best one. A depression scale that asks about sleep and appetite is
still `Affective/mental health` alone — those are symptoms of the construct, not
a second construct. But a well-being battery that measures mood *and* physical
functioning is both, and should say so.

The test: would a researcher searching for the second value want this table in
their results? If yes, tag it.

## Question 3 — Where does `Behavioral` stop and `Personality` begin?

All three of these are currently `Behavioral` alone:

- `west_2021_retaliatory_aggression_*` — Trait Aggression (Physical)
- `mpsycho_bsss` — Brief Sensation Seeking Scale
- `afps_vangsness_2019` — Academic Functional Procrastination

Each names a **disposition**: trait aggression, sensation seeking and
procrastination are stable individual differences, which is what `Personality`
is for. But each is also *about* behaviour, which is presumably why they landed
where they did. With no rule, both readings are defensible and the column
becomes a coin flip.

**Proposed rule.** `Behavioral` is for instruments that ask what someone **did**
— frequency, occurrence, a count of acts. `Personality` is for instruments that
ask what someone is **like**, including dispositions toward a class of
behaviour. "How often did you skip class last term" is `Behavioral`; "I tend to
put things off" is `Personality`.

Under this rule all three examples above move to `Personality`, and the ~209
`Behavioral` tables want a sweep.

## Question 4 — When is `Other` legitimate?

34 tables. Two of them are `margaretto_2025_translation_study_*`, whose construct
name is **"General Knowledge 1"** and **"General Knowledge 2"** — a general
knowledge test, which is `Cognitive/educational` without much argument. Another
is `ajaykumar_2023_experience`, a prior-experience rating.

**Proposed rule.** `Other` means the construct genuinely falls outside all seven
named values — not that the tagger was unsure between two of them. If two values
are competing, pick both (question 2) rather than escaping to `Other`. An
instrument measuring a stimulus property rather than a person (`sned_bendall_2024`,
a database of nature-scene images) is the legitimate case.

## Question 5 — Is `Physical health/functioning` about the body or about illness?

`c19prc_uk_mcbride_2021_phq15` measures somatic symptoms and is tagged
`Affective/mental health`. The PHQ-15 is a somatic symptom scale used to screen
for somatoform distress — genuinely both. At 79 tables, `Physical
health/functioning` is the second-rarest value, and it is plausible that
symptom-report instruments are being absorbed into `Affective/mental health` by
default.

**Proposed rule.** `Physical health/functioning` covers bodily symptoms,
functional capacity and disability, *whether or not* the instrument is used in a
mental-health context. A somatic symptom scale is both values, per question 2.

---

## What is not proposed

Nothing here changes the eight values. `TAG_VOCAB` in `metadata/tag_normalize.R`
stays the authoritative list and the pipeline still halts on anything outside it
(#1720). These are boundary rules for values that already exist.

No re-tagging is proposed either. If the rules are accepted, the sweepable
consequence is question 1's uniform families (738 tables) and question 3's
`Behavioral` set (209) — both worth measuring before deciding whether to touch.

## What ruling this needs

Five yes/no answers, or amendments. The one that matters most is question 1:
it is the only rule that can be checked mechanically afterwards, and the
`c19prc` family is 72 tables of evidence that it is not currently being
followed.
