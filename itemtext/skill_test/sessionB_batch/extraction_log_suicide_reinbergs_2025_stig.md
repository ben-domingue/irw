# Extraction log: suicide_reinbergs_2025_stig

## has_bare_integer_items
FALSE, confirmed. Ground-truth `item` values are already semantic codes (`stig01`..`stig09`),
not bare integers — no positional reconstruction from item numbering was needed to identify
*which* item is which. (What turned out to be genuinely hard here was confirming what those
codes actually *contain*, not which position they occupy — see below.)

## Source used
Reused the cached preprint PDF from `suicide_reinbergs_2025_phq`'s extraction
(`.cache/suicide_reinbergs_2025_phq/preprint.pdf` / `.txt`, `pdftotext -layout`, real text
layer, no OCR). This is the same paper — Reinbergs et al.'s Suicide Stigma Scale
development/validation preprint — and the "stig" table is the paper's own focal instrument
(not a convergent-validity measure), so the expectation going in was that full item text
would be in the body or an appendix table.

In addition, the dictionary's "URL (for data)" (`https://osf.io/f5qgm/files/4dwr5`) was
re-resolved via the OSF API (`https://api.osf.io/v2/nodes/f5qgm/files/osfstorage/`), which
listed three files on that OSF node: `mdss-data-public.Rds` (the raw analysis data,
downloaded to `.cache/suicide_reinbergs_2025_stig/raw_data.rds`) and
`analysis-mdss-2025-05-12.qmd` (the authors' own Quarto analysis script, downloaded to
`.cache/suicide_reinbergs_2025_stig/analysis-mdss.qmd`). The `.qmd` was fetched specifically
to disambiguate a discrepancy described below — it is the actual code that produced the
paper's tables, so it settles which raw variables map to which reported results.

## Source type used
- Preprint PDF (text layer, machine-readable) — Table 2 ("Factor loadings for the one
  factor model of 8 retained items") gives literal, numbered item text for what the paper
  calls the Suicide Stigma Scale.
- Raw OSF data file (`mdss-data-public.Rds`, `haven_labelled` columns) — used to identify
  which raw variables the live IRW `item` codes (`stig01`..`stig09`) actually draw from, and
  to read the `resp` value-label mapping.
- Authors' own analysis script (`analysis-mdss-2025-05-12.qmd`) — used to confirm which raw
  variable prefix (`dssm*` vs `stig*`) the paper's reported Suicide Stigma Scale results
  (Table 1/Table 2, Cronbach's alpha) are actually computed from.

## OCR / image-based extraction
None needed. `preprint.pdf`/`.txt` is a normal text-layer PDF (already confirmed clean in
the `_phq` extraction). No images/scans involved for this table's sources either.

## Central finding: `stig01`-`stig09` in the live data do NOT match the paper's disclosed Suicide Stigma Scale item text
This required real investigation and the result is a genuine, load-bearing discrepancy, not
a minor caveat:

1. The preprint states the (personal-stigma) Suicide Stigma Scale is "9 items ... rated on a
   5-point scale ranging from 0 (Strongly disagree) to 4 (Strongly agree)" and Table 1 (item
   descriptives) reports Min=0/Max=4 for every item — a 5-point, 0-4 scale.
2. But ground truth `resp` for this table is strictly `{1,2,3,4}` — a 4-point scale, no 0.
   This is a real mismatch with the paper's stated scale, not a display/typing issue (checked
   `table(gt$resp)`, confirmed only 4 levels, N=1258 unique id, 9 items/id).
3. The raw OSF data file (`mdss-data-public.Rds`) has **two distinct sets of 9 stigma-style
   items**: `dssm01`..`dssm09` and `stig01`..`stig09`.
   - `dssm01`..`dssm09` carry full, correct `haven_labelled` labels that are verbatim matches
     to Table 2's literal item text (e.g. `dssm01` label = "People who are suicidal could
     snap out of it if they wanted."), are coded 0-4 (5-point), and `dssm01`'s mean (1.10)
     matches Table 1's reported Item-1 mean (1.13) closely (some rounding drift expected
     since Table 1 is computed on a full/analysis sample, not identical to a raw re-mean).
     The authors' own `.qmd` script explicitly runs `psych::alpha()` on `dssm01:dssm09` in the
     block computing the Suicide Stigma Scale's Cronbach's alpha reported in the paper — this
     is the variable set that actually produced the paper's Suicide Stigma Scale results.
   - `stig01`..`stig09` carry an identical, truncated (80-char), boilerplate
     `haven_labelled` label on *every* item — `"What do you think: How do most people act
     towards someone who has been treated f"` — cut off mid-word, giving no usable per-item
     content, and is coded 1-4 with value labels 1=Disagree, 2=Somewhat disagree, 3=Somewhat
     agree, 4=Agree. This phrasing ("How do most people act towards someone who has been
     treated for...") reads like a *perceived*-stigma stem (Griffiths et al.'s original DSS
     has separate personal- and perceived-stigma subscales), not the personal-stigma wording
     ("People who are suicidal...") that the paper's own Table 2 discloses.
4. Decisively: `table(unclass(raw$stig01))` etc. for all 9 `stig0N` variables reproduce the
   ground-truth `resp` distribution for `suicide_reinbergs_2025_stig` **exactly**, item by
   item (e.g. `stig01`: 193/311/554/196 for resp 1/2/3/4 in both raw data and ground truth).
   `dssm01`..`dssm09` do not (different scale, different distribution). So the live IRW table
   is built from the raw `stig*` variables, not the `dssm*` variables the paper's Table 2
   text/Table 1 stats/Cronbach's-alpha computation actually describes.

**Conclusion:** the `item` codes `stig01`-`stig09` in this IRW table are very likely a
mislabeled/boilerplate variable set in the source researchers' own raw export — not the
9-item Suicide Stigma Scale the paper reports on. I could not find literal, verified item
text for what `stig01`-`stig09` actually ask. Per the task instruction not to
guess/fabricate item text, **`item_text` is left `NA` for all 9 items** rather than
assigning them the Table 2 wording (which belongs to a different, non-matching variable
set) or the truncated boilerplate label (which is not real content — identical and
incomplete across all 9 items).

## Derived vs. directly-read values
- `option_text`/`resp` mapping (1=Disagree, 2=Somewhat disagree, 3=Somewhat agree,
  4=Agree) — **directly read** from the raw OSF data file's `haven_labelled` value labels on
  `stig01`..`stig09`, and cross-validated by exact per-category count match against the
  ground-truth `resp` distribution for every one of the 9 items. High confidence despite not
  coming from the paper's prose (which describes a different, non-matching 0-4/5-point
  scale for the `dssm*` variables instead).
- `item_text` — left blank/NA throughout; not directly read (no reliable literal source) and
  not derived (would require assuming `stig0N` == `dssm0N`, which the evidence above
  contradicts).
- `instructions` — left blank/NA. The preprint's stated instructions passage belongs to the
  `dssm` variable set (a different question battery from what's actually in this table), so
  it would misrepresent the `stig` items if reused. The raw label associated with `stig0N`
  is truncated mid-sentence and not usable as a literal instructions string.
- `instrument` — set to "Suicide Stigma Scale" per the dictionary/task framing (this is the
  table this row is nominally cataloged under), with the identification caveat recorded here
  rather than silently assumed.
- `correct_response` — left blank; no scoring key, personal-belief/attitude items.
- `section_id` — no testlet/passage grouping confirmed; used a single trivial
  `suicide_reinbergs_2025_stig_1` for all 9 items with blank `section_prompt`, per
  `itemtext_standard.md`.

## Validation
`unique(item)`: exact match (`stig01`..`stig09`, both ground truth and candidate, N=9).
`unique(resp)`: candidate `{1,2,3,4}` vs. ground truth `{1,2,3,4,NA}` — the extra `NA` in
ground truth is item-level missingness in the live response data (26 rows), not a resp
*level* the candidate needs to enumerate; all 4 real response levels are covered. Same
non-issue pattern as `_phq`'s int/double type note — not treated as a real discrepancy.

## Items not extracted
`item_text` and `instructions` not extracted for any of the 9 items/the instrument as a
whole — see "Central finding" above. `option_text`/`resp` were fully recovered and verified
for all 9 items x 4 response levels (36/36 rows). This is a genuine partial extraction,
logged to `pending_index_notes.csv`.
