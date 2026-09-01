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
