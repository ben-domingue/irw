# Extraction log: sun_2025_morality_study2_meaning

## Source used
- Full-text open-access PDF of the published article: Sun, J., Wu, W., & Goodwin, G. P.
  (2025). Are moral people happier? Answers from reputation-based measures of moral
  character. *Journal of Personality and Social Psychology, 128*(5), 1160-1180.
  https://jessiesun.me/publication/sun-2025/sun-2025.pdf (author's postprint; reused from
  `sun_2025_morality_study1_dependability`'s cache at
  `.cache/sun_2025_morality_study1_dependability/sun_2025_paper.txt`/`.pdf` after
  `pdftotext -layout` — no re-fetch needed).
- OSF project https://osf.io/5e9y3/overview, `data-clean/study2-maindat.csv` (fetched via
  OSF v2 files API download link `https://osf.io/download/fyz6x/`, cached at
  `.cache/sun_2025_morality_study2_meaning/study2-maindat.csv`) — plain-text CSV with the
  raw column headers, used only to confirm the `tsmlq<N>` <-> `ts.MLQ<N>` naming
  correspondence and item ordering/reverse-coding, not for item wording.
- OSF `data-clean/study2-suppdat.xlsx` (fetched via download link
  `https://osf.io/download/rw72e/`, cached at
  `.cache/sun_2025_morality_study2_meaning/study2-suppdat.xlsx`) — attempted, but this
  file is password-protected (`file` reports `CDFV2 Encrypted`; confirmed via `olefile`,
  which shows an `EncryptedPackage`/`EncryptionInfo` OLE2 structure, not a plain
  spreadsheet). No password was found anywhere in the paper, OSF page, or repo. Same
  situation previously logged for `study3-suppdat.xlsx`/`study3-itemdat.xlsx` in
  `extraction_log_sun_2025_morality_study3_loyalty.md` — this appears to be a
  project-wide pattern (all `*suppdat.xlsx` files on this OSF project are
  password-protected) rather than something specific to Study 2.
- `data-clean/normdat-labels.csv` (already cached from Study 1) was checked for MLQ
  entries and has none — it is scoped to the moral-trait norming study only (BFI-2 items),
  not the well-being measures, so it did not help here.

## Confirming what "tsmlq" means
Paper text (p. 1167, "Self-Reported Well-Being" under Study 2 Method): "Employees
reported their sense of meaning in life using the five-item Presence of Meaning subscale
from the Meaning in Life Questionnaire (Steger et al., 2006). These items (e.g., 'I
understand my life's meaning') were rated on a 7-point scale (1 = absolutely untrue, 7 =
absolutely true)."

This confirms: `tsmlq` = **T**arget **S**elf-report, **M**eaning in **L**ife
**Q**uestionnaire (Presence of Meaning subscale; Steger, Frazier, Oishi, & Kaler, 2006).
Cross-checked against `study2-maindat.csv`'s raw column names, which use the same `ts.`
prefix convention consistently across the whole file for self-report/target measures
(`ts.mt1`-`ts.mt10` = target-self morality traits, `ts.PERMA.*`, `ts.swl`, and
`ts.MLQ1`-`ts.MLQ5` = the five MLQ items), confirming `ts` = target self-report (as
opposed to `it.*`/`tm.*` columns used for informant/teammate reports of the target). This
is the well-being *outcome* measure for Study 2 (not part of the moral-character
predictor), consistent with the task brief's hypothesis.

The raw data also has a `ts.MLQ5r` column (reverse-scored version of `ts.MLQ5`, confirmed
via `study2-maindat.csv`: e.g. row `001_1` has `ts.MLQ5=5, ts.MLQ5r=3`; row `002_3` has
`ts.MLQ5=2, ts.MLQ5r=6` — consistent with `ts.MLQ5r = 8 - ts.MLQ5` on the 1-7 scale). This
confirms `tsmlq5` corresponds to the reverse-worded item of the standard 5-item MLQ
Presence subscale (item 9 of the full 10-item MLQ: "My life has no clear purpose."),
consistent with the standard Steger et al. (2006) instrument structure (Presence items =
1, 4, 5, 6, 9 of the full MLQ, the last one reverse-scored).

**Which coding does the IRW ground truth use for `tsmlq5`?** Checked empirically:
correlating `tsmlq1`-`tsmlq4` against `tsmlq5` within `.gt_sun_2025_morality_study2_meaning.rds`
gives *negative* correlations (r = -0.88 to -0.94), i.e. the ground truth uses the **raw**
(un-reversed) `ts.MLQ5` values, not the analysis-ready `ts.MLQ5r` reverse-coded values.
This matters for anyone later filling in `tsmlq5`'s `item_text`/`option_text`: the item
stem is reverse-worded ("My life has no clear purpose" or equivalent), and the same
1=absolutely untrue/7=absolutely true anchors apply directly to the raw wording — do not
apply the reverse-scoring correction.

## Structure of output
Single `section_id` (`sun_2025_morality_study2_meaning_1`) for all 5 items — the paper
describes them as one instrument-wide measure with a single response format, no
testlet/passage structure.

Per the instructions/section_prompt boundary rule: the whole-instrument framing ("Employees
reported their sense of meaning in life using the five-item Presence of Meaning subscale
from the Meaning in Life Questionnaire (Steger et al., 2006), rated on a 7-point scale (1 =
absolutely untrue, 7 = absolutely true)") went in `instructions`, since it applies
identically to every item, not to a subset. No `section_prompt` text was needed (left
blank).

`option_text` populated only for resp 1 ("absolutely untrue") and resp 7 ("absolutely
true") — the paper states the scale is anchored only at these two endpoints; no verbal
labels are given anywhere for points 2-6, so those were left blank rather than invented
(same convention used in `sun_2025_morality_study1_dependability` and the
`firstborn_personality` reference example).

`correct_response` left blank throughout — this is a well-being self-report measure, no
scoring key.

## has_bare_integer_items
FALSE, as stated in the dictionary row — `item` values are the named codes `tsmlq1`-
`tsmlq5`, not bare integers. As with `sun_2025_morality_study1_dependability`, the
decoding still required a judgment call (confirming what `tsmlq` stands for and its
correspondence to the paper's Presence-of-Meaning subscale), just not the bare-integer
reconstruction-by-position procedure.

## OCR / image-based extraction
None needed. The source PDF (reused from the Study 1 cache) is text-based, extracted
cleanly with `pdftotext -layout`; no OCR was used anywhere in this extraction. The
`study2-maindat.csv` file used for variable-name cross-checking is plain text, not an
image.

## Derived vs. directly-read values
- `item_text` for `tsmlq1` ("I understand my life's meaning.") is a verbatim quote from
  the published paper's own prose (given as the explicit example item in the Measures
  section) — directly read, not derived. Its assignment specifically to `tsmlq1` (as
  opposed to another item in the subscale) is an inference from the `ts.MLQ1` variable
  name and the convention (also followed elsewhere in this paper, e.g. the PERMA and
  BFI-2 examples) of quoting the first item of a scale as the "e.g." example — reasonably
  confident, but not independently confirmed by a second source, so flagged here rather
  than treated as certain.
- `item_text` for `tsmlq2`-`tsmlq5` was **left blank** — the paper gives only one example
  item, and the source that would have the full item set (`study2-suppdat.xlsx`) is
  password-protected and inaccessible. This is a deliberate non-fabrication decision: the
  Steger et al. (2006) MLQ Presence-of-Meaning subscale is a well-known, publicly
  published instrument, and its standard item wording is broadly documented in the
  literature (e.g. item 4 typically reads "My life has a clear sense of purpose," item 6
  "I have discovered a satisfying life purpose," item 9/reverse "My life has no clear
  purpose"), but none of that wording is transcribed from *this paper or its supplementary
  materials*, so per the no-fabrication instruction it was not written into `item_text`.
  A human resolving this later could plausibly source the standard MLQ item text directly
  from Steger et al. (2006) as an independent, correctly-cited source rather than treating
  it as this paper's own disclosure — but that step was not taken here.
- `option_text` anchors ("absolutely untrue"/"absolutely true") are a direct,
  paraphrase-free read of the paper's stated scale anchors.
- `instructions` is a close paraphrase/transcription of the paper's own description of the
  measure and response format (the paper does not print the instrument in a literal
  participant-facing instructions paragraph, so this is the closest available literal
  text).
- The `ts.MLQ5` vs. `ts.MLQ5r` (raw vs. reverse) determination for `tsmlq5` was derived
  empirically from the ground-truth correlation structure and cross-checked against the
  raw CSV's own reverse-coding relationship (`ts.MLQ5r = 8 - ts.MLQ5`), not read directly
  from a codebook (none was accessible) — flagged as a derived, not directly-read, finding.

## Source type used
Published journal article (author's open-access postprint PDF, reused from the Study 1
cache) as the primary and only source for item text and response-scale anchors. The
OSF project's raw `study2-maindat.csv` was used only for variable-naming/reverse-coding
cross-checks, not item wording. The `study2-suppdat.xlsx` supplementary file, which likely
contains the full item wordings and possibly a translated (Chinese) version, was
inaccessible due to password protection.

## Ambiguities / items not extracted
- `item_text` for `tsmlq2`, `tsmlq3`, `tsmlq4`, `tsmlq5` was not recovered from the source
  materials available and was left blank rather than filled from outside knowledge of the
  standard MLQ wording. Logged in `pending_index_notes.csv`.
- The survey was administered in Chinese (per paper, p. 1167: "All surveys were
  administered in Chinese (simplified)... translated from English to Chinese and
  back-translated to English"), so even the one item_text captured here is an English
  back-translation as reported in the paper, not the literal Chinese text shown to
  participants — noted for completeness, not treated as a defect since this is the
  standard reporting convention for translated instruments and matches how the paper
  itself presents the measure.
- `item` and `resp` sets validated as an EXACT match against
  `.gt_sun_2025_morality_study2_meaning.rds` (all 5 `tsmlq<N>` items, all 7 resp values
  1-7).
