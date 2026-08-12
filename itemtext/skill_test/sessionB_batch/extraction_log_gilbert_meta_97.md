# Extraction log: gilbert_meta_97

## Ground truth
`readRDS(".gt_gilbert_meta_97.rds")`: 12 items exactly as given in the task
(`psye1`, `psye2`, `psye3`, `psyh1`, `psyh2`, `psyh3`, `psyo1`, `psyo2`, `psyo3`,
`psyr1`, `psyr2`, `psyr3`), `resp` in `{1,2,3,4,5,6}`. `has_bare_integer_items` is
**FALSE** — items already carry semantic labels (subscale prefix `e`/`h`/`o`/`r` +
within-subscale position 1-3), so the open question was purely whether the *literal
item wording* behind each label could be recovered and whether the position number
(1/2/3) reliably maps to a specific published item — not which item a bare integer
refers to.

## Repo script check
`grep -rl "WT7BYB\|gilbert_meta_97\|Adam.*psychological.capital\|storytelling video" data/`
found `data/gilbert_97through99.R` — the actual IRW processing script for this table.
It reads `97 PsyCapSASTrial.dta` from the raw Dataverse download and pivots
`psyo1:psyr3` / `fu_psyo1:fu_psyr3` to long format, confirming the item codes and
that table 97 is the T1/T2-collapsed PsyCap scale (98=gratitude GQ-6, 99=single-item
happiness, excluded). No local copy of the raw `.dta` file exists in this repo or
environment, so Stata variable *labels* (which might have disclosed literal item
wording directly) could not be inspected.

## Source type used
**Published validated instrument, identified via corroborating external metadata —
not transcribed from the Adam et al. 2025 paper's own body text.** Sequence of
evidence:

1. DataCite metadata for the Dataverse DOI (`api.datacite.org/dois/10.7910/DVN/WT7BYB`,
   not WAF-blocked, unlike `dataverse.harvard.edu` itself) states the PsyCap instrument
   used was the **CPC-12R** (Compound PsyCap Scale, Revised).
2. Web search independently corroborates: the underlying study is Adam, Rohr, Greuel
   et al., "Measuring the effect of short, animated storytelling videos to boost
   psychological capital in US adults: a randomized controlled trial," *Scientific
   Reports* 15:40326 (2025), doi:10.1038/s41598-025-26894-1 — multiple secondary
   sources describing this trial explicitly name the CPC-12R as the PsyCap outcome
   measure (T1 and T2, matching this table's `wave` column). I could not get past
   Nature's authentication redirect to read the paper's own Methods text directly, so
   this identification rests on DataCite + secondary-source corroboration, not a
   first-party read of the Adam et al. paper.
3. The `psye`/`psyh`/`psyo`/`psyr` item-code prefixes (Efficacy/Hope/Optimism/
   Resilience) and the 3-items-per-subscale, 12-items-total, 6-point-response
   structure match the CPC-12R's published structure exactly (confirmed against the
   instrument's own validation paper — see below), which is strong independent
   confirmation of the instrument identification, not just the DataCite label.
4. Literal item wording was pulled from the CPC-12R's own open-access validation
   paper: Baron, Rigotti & Jimmieson (or similar; verify byline on read) 2022,
   "Validation of the revised Compound PsyCap Scale (CPC-12R) and its measurement
   invariance across the US and Germany," *Frontiers in Psychology*,
   doi:10.3389/fpsyg.2022.1075031, open PMC copy at PMC9815509. Table 1 of that paper
   gives the English-language wording for all 12 items with explicit H1-H3/E1-E3/
   R1-R3/O1-O3 subscale-and-position labels, and the Methods section states the
   response format: "a 6-point rating scale ranging from 1 = 'strongly disagree' to
   6 = 'strongly agree.'" This matches ground truth's `resp` range (1-6) exactly.

`item_text` in the candidate output is therefore the CPC-12R's own canonical
published item wording (from its validation paper), mapped onto Adam et al.'s
`psy{e,h,o,r}{1,2,3}` variable-name scheme by subscale-letter and position-number.
This is **not** literal transcription from the Adam et al. 2025 paper or its
Dataverse codebook — I was not able to open either (Nature paywall/auth-redirect for
the paper; standard Dataverse AWS WAF block for the raw file/codebook, consistent
with other `gilbert_meta_*` tables in this batch).

## Residual uncertainty (not resolved, flagged rather than guessed past)
- **Position-number mapping is assumed, not confirmed against Adam et al.'s own
  codebook.** I'm relying on the CPC-12R validation paper's own H1/H2/H3 (etc.)
  ordering matching Adam et al.'s `psyh1`/`psyh2`/`psyh3` (etc.) ordering. This is a
  reasonable default (researchers using a published scale typically number items in
  the scale's own published order) but is not independently verified from Adam et
  al.'s Dataverse `.dta` variable labels or supplementary materials, which I could
  not access (Dataverse WAF block; Nature auth-wall).
- **Instructions**: no participant-facing framing/instructions text (e.g. "please
  indicate how much you agree with each statement") was located in either the CPC-12R
  validation paper or any accessible portion of Adam et al. 2025 — only the response-
  scale definition itself. `instructions` in the output is limited to the response-
  scale text, which is literally quoted from the CPC-12R paper, rather than inventing
  framing language.
- **Option labels for scale points 2-5**: only the endpoints (1="strongly disagree",
  6="strongly agree") are labeled in the CPC-12R source; points 2-5 are unlabeled
  numeric scale positions in the original instrument, so `option_text` is left blank
  for those `resp` values (mirrors the `firstborn_personality` model example's
  treatment of unlabeled midpoints).

## OCR / image-based extraction
None. All source text (CPC-12R Table 1 item wording, response-scale description) was
retrieved as machine-readable text via `WebFetch` against the PMC HTML page
(PMC9815509), not from a scanned image or PDF requiring OCR.

## Derived vs. directly-read values
- **Directly read** (from the CPC-12R validation paper, PMC9815509, Table 1 and
  Methods text): all 12 `item_text` values, the response-scale wording used for
  `instructions`, and the 1="strongly disagree"/6="strongly agree" `option_text`
  endpoint labels.
- **Derived/inferred**: the mapping from CPC-12R's own H/E/R/O + position-number
  labeling to Adam et al.'s `psy{e,h,o,r}{1,2,3}` variable names (by matching
  subscale-letter prefix and position number 1-3) — see "Residual uncertainty" above.
  `instrument` name ("Revised Compound Psychological Capital Scale (CPC-12R)") and
  `section_id` (`gilbert_meta_97_1`, single section — no testlet/passage grouping
  exists in a straightforward Likert battery) are labels I constructed, not literal
  source text.
- Nothing was fabricated from variable-name semantics alone (contrast with the
  corrected `gilbert_meta_38` case) — every `item_text` string is a verbatim quote
  from the CPC-12R's own published validation paper.

## Licensing / copyright note
The CPC-12R validation paper (Frontiers in Psychology, 2022) is published under
Frontiers' standard open-access model, which defaults to CC BY 4.0; I was not able to
confirm the exact license banner text in the fetched excerpt, so this should be
spot-checked before wide reuse, but Frontiers articles are essentially always CC BY.
Unlike WJ-IV or PPVT-4 (proprietary, commercially-sold picture-based tests handled
with explicit caution elsewhere in this batch, e.g. `gilbert_meta_80`/`gilbert_meta_78`),
the CPC-12R and its predecessor CPC-12 (Lorenz et al. 2016, PLOS ONE, doi:10.1371/
journal.pone.0152892, also open-access CC BY) are freely published research
instruments intended for academic reuse with citation — there is no Mind-Garden-style
commercial gate on this scale (that applies to the *original* Luthans PCQ-12, which
this is **not** — confirmed CPC-12R is a distinct, independently-constructed compound
scale drawing items from other public-domain-style instruments, not a repackaging of
the copyrighted PCQ-12). No licensing block on quoting/reusing the item text here,
beyond normal academic citation practice.

## Validation result
Exact match: `unique(candidate$item)` and `unique(candidate$resp)` both match
`unique(gt$item)` / `unique(gt$resp)` exactly (12 items x 6 resp values = 72 rows).
Confirmed programmatically via `setequal()` against
`.gt_gilbert_meta_97.rds` before writing the candidate file.
