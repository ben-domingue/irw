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

## Child Age (for child-focused studies) — exact column name (multi-select, comma-separated)

Only fill when the sample includes children (`Age Range` is `Child (<18y)`
or `Mixed`) and the source specifies a sub-range. Leave blank otherwise,
including whenever `Age Range` is `Adult (18+)`, `Elderly (minimum age
>50)`, or `Non-human`.

- `Early (<6y)`
- `Child (6-12y)`
- `Adolescent (12-18y)`

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

## Construct type (multi-select, comma-separated)

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
