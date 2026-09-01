# Proposed decision rules: `age range` and `sample`

**Status: proposed, awaiting Ben's approval. Nothing here is in force.**
If approved, these fold into
`tags/.claude/skills/irw-auto-tag/references/vocab.md` and this file goes away.

Context: #1760 asked @SamuelEnrique and @saviranadela which referent they had
in mind when tagging. No reply as of 2026-09-01. The question they were asked
was about **intent** — what the existing ~700 `Mixed` labels mean. Setting the
**convention** was always the PI's call; their answer would have informed it,
not authorised it. These rules are written so the convention can be set now,
and so a later "we meant something else" is a correction to a written rule
rather than an answer to an unanswered question.

Every count below was measured 2026-09-01 from `metadata/tags.csv` (2,480 rows)
and `metadata/metadata.csv` (4,134 live tables).

---

## The evidence this rests on

Restated here so this file stands alone; the source is #1760.

Many IRW tables carry `cov_age`, so for those the `age range` tag can be
compared against the ages actually present. On a random sample of **70 tagged
tables that have `cov_age`**:

- `Adult (18+)` agreed with the data **28 of 30** times.
- `Mixed` disagreed **26 of 29** times — and in **25 of those the table contains
  no respondent under 18 at all**, with a minimum age of exactly 18.

Six of the contested tables, with the ages actually in them:

| table | ages present | respondents under 18 |
|---|---|---|
| `colombia_2023_politics_voting` | 18 – 114 (n=46,392) | 0 |
| `mexico_2023_quality_wellbeingservice` | 18 – 98 (n=78,896) | 0 |
| `spain_2025_democracy_parties` | 18 – 97 (n=4,010) | 0 |
| `spain_2024_politics_beliefs` | 18 – 94 (n=2,562) | 0 |
| `margaretto_2025_translation_study_2_lextale` | 18 – 68 (n=220) | 0 |
| `silvia_2024_funny` | 18 – 88 (n=1,842) | 0 |

Mostly national survey programmes (CIS, ENSU and similar), plus a few lab
studies. **This is not the signature of careless tagging** — careless tagging
scatters. It is the signature of a consistent rule that differs from the one the
filters assume, which is why the fix is a stated convention rather than a QC
pass.

Current distribution of the column, across the 2,480 tagged rows:

| `age range` | rows |
|---|---|
| `Adult (18+)` | 1,260 |
| `Mixed` | 700 |
| `Child (<18y)` | 416 |
| blank | 45 |
| `Elderly (minimum age >50)` | 43 |
| `Non-human` | 16 |

---

## Rule A — `age range`

### A0. Referent

**The tag describes the shipped IRW table, not the source study or its target
population.** This is option 1 in #1760.

Three reasons, in the order they carry weight:

1. Every other column in the sheet describes the shipped table. One column
   silently describing something else is the ambiguity, whatever value it takes.
2. It is the only reading a filter can honour. `irw_filter(age_range = "Mixed")`
   returning a table whose minimum age is exactly 18 is a defect on any account
   of intent.
3. **It is the only reading that is checkable.** 2,363 of 4,134 live tables
   carry a `cov_age` column, so under this referent the tag is derived,
   auditable and self-updating. Under the source-study referent it stays a hand
   label that decays as the corpus grows — the exact failure item 2 exists to
   fix. This third reason holds even if the RAs reply "we meant the study."

### A1. Derivation, when the table's own ages are usable

Guard first. `cov_age` is **usable** only when all of these hold; otherwise
treat the table as having no age data and fall through to A2:

- the column parses as numeric;
- at least 30 non-missing values;
- all values fall in `[0, 120]`;
- the values are not obviously banded codes — reject if there are fewer than 6
  distinct values **and** the maximum is under 10 (that is the `cov_age_band`
  shape: 1–6 category codes, e.g. `chen_2024_*`);
- if the source states the unit is months, convert before applying anything
  below.

Then, in this order, first match wins:

| # | Condition | Tag |
|---|---|---|
| 1 | respondents are not human | `Non-human` |
| 2 | `min(cov_age) > 50` | `Elderly (minimum age >50)` |
| 3 | under-18s and 18+ both present, **and** the smaller of the two groups is ≥ `MINOR_SHARE` of respondents | `Mixed` |
| 4 | `max(cov_age) < 18` | `Child (<18y)` |
| 5 | otherwise | `Adult (18+)` |

`Non-human` is never derived from ages; it comes from the source and short-
circuits everything.

**`MINOR_SHARE = 0.02`.** This is the one free parameter and it is worth being
explicit about. A literal reading (any respondent on the other side of 18 makes
a table `Mixed`) reproduces the original complaint in reverse: a national survey
of adults with three 17-year-olds in it would be served to someone filtering for
children. 2% is small enough that any genuinely mixed-age table clears it and
large enough to absorb edge cases. It changes nothing about the cases in #1760:
25 of the 26 contested tables have **zero** respondents under 18, so they resolve
to `Adult (18+)` under any tolerance. When the tolerance is what decided a tag,
that fact is recorded in the basis (A4) rather than left implicit.

**This also answers #1743**, which observes that `vocab.md` never says a range
crossing 18 is `Mixed`. Row 3 says it, with a stated tolerance.

### A2. When there is no usable `cov_age`

Tag only from **explicit** age information in the source:

- a stated numeric inclusion criterion ("participants aged 18–65");
- a reported minimum/maximum, or a mean with a range;
- a school-grade level that cannot include 18-year-olds (grade ≤ 10 → `Child
  (<18y)`; grades 11–12 are **not** decidable this way and get no tag from
  grade alone).

Otherwise **leave it blank**. Specifically, do not infer from: the country or
name of a survey programme, "undergraduates" or "college students" (which
routinely include 17-year-olds), "adults" used loosely in an abstract, or the
construct being measured.

Blank is the correct answer far more often than the current sheet suggests, and
it is cheaper to fix than a wrong tag, because nothing downstream trusts a blank.

### A3. `child age`, as a consequence

Same referent, derived from the same column when A1 applied, half-open bands so
the boundaries do not overlap: `Early (<6y)` = `[0, 6)`, `Child (6-12y)` =
`[6, 12)`, `Adolescent (12-18y)` = `[12, 18)`. Multi-select: include every band
with at least one respondent in it, subject to the same `MINOR_SHARE` floor.
Blank whenever `age range` is `Adult (18+)`, `Elderly`, `Non-human`, or blank —
unchanged from the current vocabulary.

### A4. Record the basis, always

Each tag carries one of `derived_cov_age`, `source_stated`, or blank, plus —
for derived rows — the `min`, `max`, and under-18 share it was derived from.
This is what makes the column auditable instead of re-litigable, and it is the
natural thing for #1767's `status.json` to publish.

### What A does to the corpus, measured

| | count |
|---|---|
| Live tables carrying `cov_age` | 2,363 of 4,134 |
| …already tagged, so the tag becomes checkable | 1,243 |
| …of which currently `Mixed` — the disputed population | **472 of 700** |
| …**not currently tagged at all**, so a tag appears with no human effort | **1,120** |
| Currently `Mixed` with no `cov_age`, needing A2 or a blank | 228 |

The 1,120 is the part worth noticing. Tag coverage fell 6.4 points between
2026-08-29 and 2026-08-31 because the denominator grows faster than hand
tagging; A1 is the first rule here that adds tagged tables **as fast as the
corpus grows**, because it reads the corpus rather than a person.

---

## Rule B — `sample`

### B0. The actual problem

`sample` is multi-select with eight values, and they are **two different facets
jammed into one column**:

- **Setting / recruitment channel:** `Educational`, `Clinical`,
  `Program-based`, `Internet-based (Mturkers, etc)`, `Non-human`
- **Sampling frame / breadth:** `Representative`, `Targeted/specific`,
  `General/non-specific`

Nothing says so, which is why the column reads as though seven values all
overlap. They do not; two groups of values answer two different questions, and
only the second group has a genuine conflict inside it.

### B1. Setting atoms — independent, any number

Assign each that the source supports. Definitions, which the vocabulary has
never carried:

| Value | Applies when the respondents were reached through… |
|---|---|
| `Educational` | a school, university, or course, as part of that setting |
| `Clinical` | a health-care setting, or recruitment by diagnosis or treatment status |
| `Program-based` | a specific intervention, programme, or cohort the study is about |
| `Internet-based (Mturkers, etc)` | an online panel or crowdwork platform (MTurk, Prolific, Qualtrics panels, Wenjuanxing) |
| `Non-human` | the respondents are not people — mutually exclusive with everything else |

These are about *how people were reached*, so more than one can be true
(`Clinical, Educational, Internet-based` — 15 rows today — is coherent).

### B2. Frame atoms — the fix

Two independent booleans, and one residual:

- **`Representative`** — the source claims probability sampling, or claims the
  sample is representative of a defined population. The claim must be the
  source's, not our inference from a large *n* or a national name.
- **`Targeted/specific`** — the sampling frame is restricted to a defined
  subpopulation: a diagnosis, an occupation, an age band, a single institution,
  a language community.
- **`General/non-specific`** — **defined as neither of the above**: recruitment
  is described, and no restriction on the frame and no representativeness claim
  is made.

The one rule the vocabulary needs and has never had:

> `General/non-specific` is the residual. It **never** co-occurs with
> `Representative` or `Targeted/specific`.

`Representative` and `Targeted/specific` **may** co-occur, and often should: a
nationally representative sample *of teachers* is both, and collapsing it to one
value loses the fact that made it worth collecting.

If recruitment is not described at all, leave the frame facet **blank**. Silence
is not the same as "general", and 970 rows already carry no frame value, so a
blank frame is an established state rather than a novelty.

### What B does to the corpus, measured

Frame-atom combinations across the 2,480 tagged rows:

| combination | rows | under B |
|---|---|---|
| no frame value | 970 | unchanged — blank stays a valid state |
| `General/non-specific` alone | 650 | unchanged |
| `Targeted/specific` alone | 525 | unchanged |
| `General/non-specific` + `Representative` | 112 | **contradiction — resolve to `Representative`** |
| `Representative` alone | 105 | unchanged |
| `General/non-specific` + `Targeted/specific` | 69 | **contradiction — resolve to `Targeted/specific`** |
| `Representative` + `Targeted/specific` | 49 | **unchanged — legitimately both** |

So B leaves 2,299 of 2,480 rows exactly as they are and repairs 181. It is a
definition, not a re-tagging campaign — which is the argument for making this
call without the RAs: their labels are mostly right, and what is missing is the
sentence nobody ever wrote down.

The 49 `Representative, Targeted/specific` rows are the evidence that the
precedence-list version of this rule (pick one frame value, highest wins) would
be wrong. An earlier draft of mine had exactly that; the data says otherwise.

---

## Worked examples

The six tables from #1760, plus the `sample` example, run through both rules.
Current tags are from `metadata/tags.csv` as of 2026-09-01; ages are from #1760.

| table | ages | `age range` now → under A | `sample` now → under B |
|---|---|---|---|
| `colombia_2023_politics_voting` | 18–114, 0 under 18 | `Mixed` → **`Adult (18+)`** (A1 row 5) | `General/non-specific, Representative` → **`Representative`** (B2 contradiction) |
| `mexico_2023_quality_wellbeingservice` | 18–98, 0 under 18 | `Mixed` → **`Adult (18+)`** | `General/non-specific` → unchanged |
| `spain_2025_democracy_parties` | 18–97, 0 under 18 | `Mixed` → **`Adult (18+)`** | `General/non-specific` → unchanged |
| `spain_2024_politics_beliefs` | 18–94, 0 under 18 | `Mixed` → **`Adult (18+)`** | `General/non-specific` → unchanged |
| `margaretto_2025_translation_study_2_lextale` | 18–68, 0 under 18 | `Mixed` → **`Adult (18+)`** | `Educational, Targeted/specific` → unchanged |
| `silvia_2024_funny` | 18–88, 0 under 18 | `Mixed` → **`Adult (18+)`** | `Targeted/specific` → unchanged |
| `mexico_2023_quality_low` | — | `Mixed` → **`Adult (18+)`** | `General/non-specific` → unchanged |

Three things this shows, which matter more than the individual rows:

1. **A is decisive where it applies.** Every one of these resolves on the data,
   with no judgment call and no tolerance needed — all six have zero respondents
   under 18.
2. **B fires only on contradictions.** One row of seven changes. B is not a
   re-tagging campaign; it is a definition that happens to invalidate 181 rows
   out of 2,480.
3. **B does not re-open settled rows.** `mexico_2023_quality_low` is the `sample`
   example in #1760 — human said `General/non-specific`, the auto-tagger said
   `Representative`. B does not adjudicate that: it says only that the two can
   never *both* stand. Whether ENSU counts as `Representative` turns on whether
   INEGI claims representativeness, which is B2's "the claim must be the
   source's" test, and it is a per-table read, not something this rule decides
   in advance.

---

## Alternatives I considered and rejected

**The source-study referent (option 2 in #1760).** Defensible on its own terms —
a survey with a broad frame that releases 18+ microdata *is* describing that
study. Rejected because it makes the column unverifiable in principle: there is
no artifact in the IRW against which "the study's target population" can be
checked, so the column could never be audited, only re-litigated. The
tie-breaker is #1709/#1702's lesson about hand-maintained counts: anything not
derivable drifts.

**A frame precedence list** (`Representative` beats `Targeted/specific` beats
`General/non-specific`; pick one). This was my first draft, and the data killed
it: 49 rows carry `Representative, Targeted/specific` together, and a
nationally-representative sample *of teachers* is genuinely both. A precedence
list would have quietly deleted the restriction that made those samples worth
collecting.

**Splitting `sample` into two columns**, one per facet — which is what the
column actually is. Rejected for now as out of scope: it breaks
`irw_filter(sample=)` for every existing user and needs a Sheets write path
(#1732, blocked behind #1723). B2 gets the same correctness inside the existing
column. Worth revisiting if the column is ever versioned.

**Waiting for the RAs.** Two working days with no reply, against an item-2 track
that is fully blocked and a coverage figure moving the wrong way — 61.7% to
55.3% between 2026-08-29 and 2026-08-31, as 484 new tables arrived against 35
newly tagged ones (#1702). The asymmetry is that a written rule is cheap to
correct and a blocked track is not.

---

## Confidence, honestly

- **A1** — high. Fully mechanical, and the guard makes its own failure visible;
  when `cov_age` is unusable the rule declines rather than guesses.
- **A2** — high, because it is mostly a rule about **when to leave the field
  blank**. The risk is that it produces more blanks than the sheet has today;
  that is intended.
- **A3** — high, same mechanism as A1.
- **B1** — medium-high. Reading "how were these people reached" off a methods
  section is judgment, but it is the ordinary kind, and the definitions bound it.
- **B2** — high for the contradiction rule (mechanical), medium-high for
  applying `Representative`, which turns on whether the source *claims*
  representativeness. Written as "the claim must be the source's" precisely so
  it does not become a judgment about whether the claim is true.

The weakest point in the whole proposal is `MINOR_SHARE`. It is a threshold
chosen to sit between two failure modes rather than derived from anything, which
is why it is named, isolated, and recorded per row instead of buried.

## What I need from you

Six decisions. Defaults are what the document currently says, so "approve" with
no comment means all six as written.

1. **`age range` referent = the shipped table.** (§A0) — the load-bearing one.
2. **`MINOR_SHARE = 0.02`.** Set it to `0` for a purely literal rule; nothing in
   #1760's cases changes either way. This is the parameter I am least able to
   defend from first principles.
3. **`Representative` and `Targeted/specific` may co-occur** (§B2), and
   `General/non-specific` is the residual that never co-occurs with either.
4. **`child age` gets derived too** (§A3), from the same `cov_age` column.
   Say no and I leave that column entirely to human raters.
5. **Blank beats a guess** (§A2). This will *reduce* filled cells on tables
   whose source states nothing explicit about age. If you would rather keep a
   best-guess tag with the basis recorded as `source_inferred`, say so — it is a
   one-line change, and it is a real trade-off, not an oversight.
6. **Whether to tell the RAs**, and in what terms — draft below.
7. **How a derived tag interacts with an existing human row** — see immediately
   below. This one is not optional: without an answer, most of Rule A cannot
   publish.

### 7, in full — the merge policy is in the way

`03_tags.R` unions the sheet with `tags/*_auto.csv` and **drops any automated
row for a table a human has already tagged** (#1723). The precedence is
whole-row, not per-column, and the sheet is read-only from code — there is no
service account and, per that file's own header comment, there is not going to
be one until #1708 / #1732.

That splits Rule A's payoff cleanly in two:

| | tables | publishes today? |
|---|---|---|
| Tables with `cov_age` and **no** tag row — a derived tag is new information | **1,120** | **yes**, nothing is in the way |
| Tables with `cov_age` and an existing human tag, including the 472 disputed `Mixed` rows | 1,243 | **no** — the automated row is dropped before it reaches the export |

So as things stand, adopting Rule A would tag 1,120 new tables and change **none**
of the rows that prompted #1760. Three ways out:

- **(a) A per-column exception.** For `age range` only, a tag with basis
  `derived_cov_age` outranks a human value; every other column keeps human
  precedence. Recommended: it is ~10 lines in `03_tags.R`, it is the only option
  that fixes the defect this issue is about, and it is defensible on exactly the
  ground that made A0 the right referent — a value computed from the table's own
  data is not an opinion competing with a rater's, it is a measurement. The
  human value stays in the sheet and stays recoverable.
- **(b) Publish the 1,120, leave human rows alone.** Deliverable immediately,
  no policy change, and dishonest by omission: `irw_filter(age_range = "Mixed")`
  keeps returning adults-only tables indefinitely.
- **(c) Wait for a Sheets write path** and fix the rows at source. Correct in
  principle, blocked behind #1708 / #1732 / 6.1, which is a Ben-decision item
  with no date.

My recommendation is **(a)**, with the derived rows carrying their `min`/`max`/
under-18 share so any disagreement is inspectable rather than mysterious. Note
that (a) is a change to a rule you set deliberately in #1723, which is why it is
a decision and not an implementation detail.

## Draft note to the RAs, for your edit

> On the tagging conventions question in #1760: we have gone ahead and written
> the rules down rather than leave the tag work blocked, so nothing here is a
> judgment about your tagging — the rule you were being asked about had never
> been stated, which is the actual defect.
>
> For `age range`, the tag now describes the **table as shipped in the IRW**, not
> the source study's target population. Where a table has a `cov_age` column we
> derive the tag from the ages actually present, so most of these stop being a
> judgment call. Tables tagged `Mixed` whose data contain no respondents under 18
> will be re-derived to `Adult (18+)` — that is a change of convention, not a
> correction of your work.
>
> For `sample`, the three overlapping values now have a stated boundary:
> `General/non-specific` means "no representativeness claim and no restricted
> frame", so it never appears alongside `Representative` or `Targeted/specific`.
> Those two *can* appear together — a representative sample of a specific
> population is both.
>
> If either rule is not what you intended, say so on #1760 and we will change the
> rule; it is written down now, so disagreeing with it is a concrete edit rather
> than an open question.

## If approved

1. Fold A and B into `vocab.md`; delete this file.
2. Close #1743 — A1 row 3 is the sentence it asks for.
3. Unblock **2.3** (#1722): `age range` and `sample` gain per-column rules, so
   they stop holding the other columns.
4. Implement A1/A3 as a derivation step in the auto-tagger (it currently reads
   only sources, never `cov_age`), with the basis field from A4.
5. Regenerate, and report the diff **before** anything publishes: how many tags
   changed, in which direction, and how many tables gained a first tag.
6. Tell @SamuelEnrique and @saviranadela what was decided and why — framed as a
   re-derivation under a stated rule, not a correction of their work. Their
   labels being consistently at odds with `cov_age` in one specific direction is
   evidence they applied a rule; it was just a different one from the one the
   filters assume.

---

## If it goes wrong

Tags are regenerated, not hand-maintained: `03_tags.R` rebuilds the published
table from the sheet plus the automated CSV on every run, and a human row always
wins over an automated one (#1723). So reversing any of this is changing the
rule and re-running — not a migration. That is the main reason deciding now is
the low-risk option rather than the bold one.
