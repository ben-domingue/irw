# Controlled vocabularies — "IRW Tags" sheet

These are strict enums for the fields below. **Never write a value outside
a list here.** If the source doesn't clearly support a confident choice,
leave the field blank rather than guessing — this matches how human raters
already treat these columns (many existing rows have several of these
fields empty).

## Provenance and how to keep this current

There is no Sheets API / OAuth credential available to this skill (Google
Drive tools 404 on both the tags sheet and dictionary sheet IDs — they
aren't shared with the connected account — and only each sheet's public
CSV export is reachable). So the sheet's actual data-validation dropdown
rules can't be read directly.

Every list below was instead derived by **enumerating every non-empty
value actually entered** in the live sheet (`python scripts/derive_vocab.py`,
last run 2026-08-29 over ~2450 rows), which is a strong proxy: these columns
show zero stray/off-list values, consistent with enforced dropdown validation.
If you suspect the sheet's dropdowns have since changed (a new option added),
re-run `derive_vocab.py` and diff its output against this file — don't assume
this file is exhaustive forever.

**`Age Range`, `Child Age` and `Sample` now carry decision rules, not just
enums.** #1760 asked which referent `age range` describes and where the three
overlapping `sample` values divide; both were settled on 2026-09-01. The rules
are stated inline below. The reasoning, the measured impact, the alternatives
rejected and the seven decisions as they were put are in
`tags/decisions/1760_age_range_and_sample.md` — read that before changing any of
them, and record a change there too.

**Two of these lists are no longer a proxy.** `Sample` and `Construct type` are
now enforced in code: `TAG_VOCAB` in `metadata/tag_normalize.R` is the
authoritative list, and `03_tags.R` **stops the pipeline** on any atom outside
it rather than publishing it (issue #1720). If you need to add a value to
either column, add it there too or the next export fails. The remaining
columns are still enumerated proxies with nothing enforcing them.

## Age Range (single-select)

- `Child (<18y)`
- `Adult (18+)`
- `Mixed`
- `Elderly (minimum age >50)`
- `Non-human`

**Referent and definition (decided 2026-09-01, #1760).** The tag describes the
**table as shipped in the IRW**, not the source study or its target population.

> `Mixed` means more than one of the age ranges we otherwise use is present in
> the table — operationally, **at least one person under 18 and at least one
> person aged 18 or over**. One boundary, at 18.

Two neighbouring distinctions do **not** create a second boundary:

- `Elderly (minimum age >50)` is a property of the whole sample, not of a
  person: everyone in the table is over 50. A 30–80 sample is `Adult (18+)`.
- The `Early/Child/Adolescent` bands belong to `Child Age`, not here. A 4–15
  sample is `Child (<18y)`.

**Derive it when you can.** Where the table has a usable `cov_age`, this column
is computed rather than judged, and the derived value **outranks a human tag**
(the one exception to human precedence, #1723 / decision 7). `cov_age` is usable
only when it parses as numeric, has ≥30 non-missing values, lies in `[0, 120]`,
and is not a banded code (fewer than 6 distinct values *and* a maximum under 10
is the `cov_age_band` shape); convert first if the source states months.

Then, first match wins: not human → `Non-human`; `min > 50` → `Elderly`; both
sides of 18 present **and** the smaller group ≥ **2%** of respondents → `Mixed`;
`max < 18` → `Child (<18y)`; otherwise `Adult (18+)`. The 2% floor stops three
17-year-olds in a 46,000-person adult survey from making it `Mixed`.

**With no usable `cov_age`, tag only from explicit age information** in the
source — a stated numeric inclusion criterion, a reported minimum/maximum, or a
school grade that cannot include 18-year-olds (grade ≤ 10 → `Child (<18y)`;
grades 11–12 decide nothing). **Otherwise leave it blank** (decided 2026-09-01):
do not infer from a country or survey-programme name, from "undergraduates" or
"college students" (which routinely include 17-year-olds), from a loose "adults"
in an abstract, or from the construct. Blank is cheaper to fix than a wrong tag.

## Child Age (for child-focused studies) — exact column name (multi-select, comma-separated)

Only fill when the sample includes children (`Age Range` is `Child (<18y)`
or `Mixed`) and the source specifies a sub-range. Leave blank otherwise,
including whenever `Age Range` is `Adult (18+)`, `Elderly (minimum age
>50)`, or `Non-human`.

- `Early (<6y)`
- `Child (6-12y)`
- `Adolescent (12-18y)`

Derived from `cov_age` alongside `Age Range` when that column is usable (decided
2026-09-01, #1760), on **half-open** bands so the shared boundaries are not
ambiguous: `Early (<6y)` = `[0, 6)`, `Child (6-12y)` = `[6, 12)`,
`Adolescent (12-18y)` = `[12, 18)`. Include every band holding at least one
respondent, subject to the same 2% floor.

## Sample (multi-select, comma-separated)

**This column has two forms — write the sheet's, not the published one.**
Write `Internet-based (Mturkers, etc)` exactly as listed, matching what human
raters have always entered; `03_tags.R` renames it to `Internet-based` on
export. Do not write `Internet-based` into the sheet: it would leave the sheet
internally inconsistent for no gain, since the export normalizes either way.

Background: that literal comma is why the value has to be quoted, and the
inconsistent quoting that resulted spawned three separate workarounds — a
34-line parser in `Rpkg`, a tilde-swap in `irw_site`, and nothing at all in
`Python-pkg`, where filtering on it silently matched no tables. All three are
gone; the rename on export is what replaced them. The sheet itself keeps the
old form until there is a service account to change it (#1708).

- `Program-based`
- `General/non-specific`
- `Internet-based (Mturkers, etc)` — exported as `Internet-based`
- `Educational`
- `Clinical`
- `Targeted/specific`
- `Representative`
- `Non-human`

**These eight values are two facets, not one (decided 2026-09-01, #1760).**

*Setting — how were these people reached?* `Educational` (through a school,
university or course), `Clinical` (through a health-care setting, or by
diagnosis or treatment status), `Program-based` (through the specific
intervention or cohort the study is about), `Internet-based` (an online panel or
crowdwork platform), `Non-human` (mutually exclusive with everything). **These
combine freely** — `Clinical, Educational, Internet-based` is coherent.

*Frame — how broad was the sampling?*

- `Representative` — the source claims probability sampling, or claims the
  sample represents a defined population. **The claim must be the source's**,
  never inferred from a large *n* or a national-sounding name. Where a source
  describes its sampling procedure *and* labels it, **the description of the
  procedure wins**: a claim of representativeness contradicted by the stated
  method is not a claim. (Amended 2026-09-01 — `shan_2020` says "convenient
  sampling" in its Methods while the authors' rebuttal letter in the same PMC
  record says "simple random sampling"; `silva_2018` says "regionally
  representative samples" alongside "non-probabilistic sampling designed by
  convenience".)
- `Targeted/specific` — the frame is restricted by something the study
  **imposed on top of its setting**, not by what the setting already implies.
  Recruiting in a school is not a restriction; recruiting *teacher-education
  majors* in a school is. **"Undergraduates" is not an age band.** A real
  restriction looks like: a diagnosis, a screening criterion, a named occupation
  within a workplace, a residency or language requirement, a single named cohort.
  (Amended 2026-09-01. The first wording listed "an age band, one institution"
  as markers, which fires on almost every study — one blind rater measured it
  applying to 9 of 10 tables — and contradicted the `Educational,
  General/non-specific` combination blessed below, which 133 rows carry.)
- `General/non-specific` — **the catch-all**: recruitment is described, and
  there is no representativeness claim and no restricted frame.

Two rules follow, and `metadata/tag_normalize.R` enforces the first on export:

> `General/non-specific` is not used when one of the other two frame values
> applies, so it **never co-occurs** with `Representative` or
> `Targeted/specific`. A *setting* atom does not displace it —
> `Educational, General/non-specific` is a real statement.

> `Representative` and `Targeted/specific` **may co-occur**: a nationally
> representative sample *of teachers* is both. Never collapse them to one.

If recruitment is not described at all, leave the frame facet blank. Silence is
not the same as `General/non-specific`.

## Primary Language(s) — what evidence licenses a value (decided 2026-09-01, #1803)

**Inference is allowed here, and that is deliberate — the opposite of the
`Age Range` rule.** Where a source does not state the language of
administration, infer it from what you do know: the country, the population, a
forward-backward translation, the language of the instrument's cited version.

The asymmetry is Ben's call and has a reason. A wrong guess is cheap and
visible; a blank is neither. The corpus is majority non-English and every
missing value makes it read as more English than it is, so **erring toward
naming a non-English language is the intended failure direction.** That is not
true of `age range`, where a wrong tag silently mis-filters a sample.

Two things are still not licensed, because neither is an inference about the
respondents:

- **A repository record's own language field is not the instrument's language.**
  Zenodo stamps "Languages: English" on the *record*; Dataverse and figshare do
  the same. After #1789 the tagger reads mostly repository metadata, so this
  will come up constantly — and it biases toward English, the one direction this
  rule exists to avoid. `soderberg_2024_*` is the worked example: the Zenodo
  record says English, the study is at Åbo Akademi, and the instrument could be
  Swedish or Finnish. Left blank, correctly.
- **The language of the paper is not the language of the instrument.** A study
  published in English having administered a Turkish questionnaire is `tur`.

Record what the respondents read. If an instrument went out in more than one
language, list them all (`eng, vie`).

## Construct type (multi-select, comma-separated)

**This column carries decision rules, not just an enum** (decided 2026-09-02,
#1837). The reasoning, the evidence and the five questions as they were put are
in `tags/decisions/1837_construct_type.md` — read that before changing any of
them, and record a change there too.

**1. The tag describes what THIS TABLE measures, never what the study was
about.** A family of tables from one paper may end up uniform because its tables
are alike; it must not be uniform because they share a source. `enem` and `imos`
are legitimately all `Cognitive/educational` — every table is an exam. All 72
`c19prc_*` tables carrying `Affective/mental health, Opinion/attitude` is not:
one of them is `wordsum`, a vocabulary test.

**2. Name every facet the instrument genuinely measures**, not the single best
one. The test: would a researcher searching for the second value want this table
in their results? Symptoms of one construct do not make a second — a depression
scale that asks about sleep and appetite is `Affective/mental health` alone. A
battery measuring mood *and* physical functioning is both.

**3. `Behavioral` is what someone DID; `Personality` is what they are LIKE.**
Frequency, occurrence and counts of acts are `Behavioral`. Stable dispositions
are `Personality`, *including* dispositions toward a class of behaviour. "How
often did you skip class last term" is `Behavioral`; "I tend to put things off"
is `Personality`. Trait aggression, sensation seeking and procrastination are
`Personality`.

**4. `Other` means outside all seven values, not undecided between two.** If two
compete, tag both (rule 2). The legitimate case is an instrument that measures a
stimulus rather than a person — `sned_bendall_2024`, a database of nature-scene
images. A general-knowledge test is `Cognitive/educational`.

**5. `Physical health/functioning` covers bodily symptoms, functional capacity
and disability, whether or not the instrument is used in a mental-health
context.** A somatic symptom scale such as the PHQ-15 is `Physical
health/functioning` *and* `Affective/mental health`, per rule 2.

Order doesn't matter. `03_tags.R` sorts atoms into canonical order on export,
so `Behavioral, Opinion/attitude` and `Opinion/attitude, Behavioral` become the
same published string — don't spend effort hand-sorting, and don't treat a
differently-ordered existing row as a discrepancy.

- `Developmental`
- `Affective/mental health`
- `Cognitive/educational`
- `Opinion/attitude`
- `Personality`
- `Behavioral`
- `Physical health/functioning`
- `Other`

## Measurement tool (multi-select, comma-separated — most rows have exactly one value, but a handful have two)

- `Observational rating`
- `Survey/questionnaire`
- `Test`

## Item format (single-select)

- `Likert Scale/selected response`
- `Constructed Response`
- `Mixed`
- `Slider/continuous`

## Item text available? (single-select)

- `Yes`
- `No`

Leave blank if you can't tell from the source whether item text was
published anywhere (a "Notes" caveat is more honest than guessing Yes/No).

## Primary Language(s) — NOT a strict dropdown

Unlike the fields above, this column is genuinely free text in the live
sheet: it mixes ISO 639-2 bibliographic and terminology codes (`fre` and
`fra` both appear for French; `ger`/`deu`, `chi`/`zho`, `dut`/`nld`,
`jap`/`jpn`, `cze`/`ces`, `per`/`fas` similarly split), and a fair number of
rows have stray notes typed into this field instead of a code (`"need
help"`, `"missing description"`, `"no access to the osf page"`,
`"non-verbal task"`). Don't repeat that pattern.

- Use lowercase **ISO 639-2 bibliographic codes** (`eng`, `spa`, `fre`,
  `ger`, `chi`, `por`, `rus`, `jpn`, `kor`, `ara`, `dut`, ...) —
  bibliographic is the more common convention in the existing data.
- Comma-separated, no spaces after the comma (matches the majority
  pattern, e.g. `eng,spa`), lowercase.
- Never put uncertainty or access notes in this field — put those in
  `Notes` instead, using the exact conventions below.

## Notes — exact strings already used in the sheet, reuse them verbatim

- `no working link` — when the Data Dictionary has no match for the table,
  or every one of Description/URL/Reference/DOI is empty.
- `cannot fully access due to paywall` — when the source was found but
  couldn't be fetched/read (paywalled, login-gated, or otherwise
  unreachable) after an actual fetch attempt.

Leave `Notes` blank otherwise — most existing rows do.
