# Extraction log: sun_2025_morality_study3_loyalty

## Source used
- Full-text open-access PDF of the published article: Sun, J., Wu, W., & Goodwin, G. P.
  (2025). Are moral people happier? Answers from reputation-based measures of moral
  character. *Journal of Personality and Social Psychology, 128*(5), 1160-1180.
  https://jessiesun.me/publication/sun-2025/sun-2025.pdf (author's own postprint copy).
  Reused from the cached copy at
  `.cache/sun_2025_morality_study1_dependability/sun_2025_paper.pdf` /
  `sun_2025_paper.txt` (no refetch needed; this is the same paper for all three studies).
  The DOI (10.1037/pspp0000539) is paywalled at the APA site, so this author copy was
  used instead.
- OSF project https://osf.io/5e9y3/overview, file `data-clean/normdat-labels.csv`
  (reused from the same cache directory). This is the codebook for a related MTurk
  moral-relevance norming study that used the same MCQ item pool, keyed to standard MCQ
  item codes (`mv.MCQ.<facet><n>`). It gives verbatim text for all four MCQ Loyalty items
  (L1-L4).
- `data/sun_2025_morality.do` in this repo (existing IRW processing script) was inspected
  fresh for this table (not reused, since it covers Study 3 in a separate code block from
  Study 1). Confirms `itmcql1 itmcql2 itmcql3 itmcql4` are read directly, unmodified, from
  the raw `study3-maindat.csv` (via intermediate `sun_2025_morality_3.csv`) with no
  reordering or relabeling — the melt into long format at line ~1994-2026 uses the literal
  column names.
- Two additional Study-3-specific OSF supplementary files were located and attempted:
  `data-clean/study3-itemdat.xlsx` and `data-clean/study3-suppdat.xlsx` (downloaded via
  the OSF v2 files API, cached at `.cache/sun_2025_morality_study1_dependability/
  study3-itemdat.xlsx` / `study3-suppdat.xlsx`). Both are password-protected
  (`CDFV2 Encrypted` per `file`) and could not be opened — no password was found in the
  paper, OSF project description, or wiki. These were not needed for the final mapping
  (see below) but are logged here in case a password surfaces later and someone wants a
  third independent source.

## What "itmcql" turned out to mean
`itmcql<n>` = **i**tem, **M**oral **C**haracter **Q**uestionnaire (MCQ; Furr et al., 2022),
**L**oyalty facet, item `<n>`. This is a *different* instrument from
`sun_2025_morality_study1_dependability`'s `itbfi2<NN>` prefix (BFI-2), confirming the
task's hint that Study 3 draws on a different item bank for this facet. Specifically:

- The paper (p. 1165-1166) states the original 32-item Study 1 measure combined items from
  three source scales: BFI-2, HEXACO-PI-R Honesty-Humility, and the MCQ. It explicitly
  says: "we included additional measures of moral character from the MCQ (Furr et al.,
  2022): general morality ... honesty ... fairness ... and loyalty (four items; e.g.,
  'Believes it is important not to betray people')." So the loyalty facet's *source
  instrument* is the MCQ, not BFI-2/HEXACO — this explains the different prefix pattern.
- The paper (p. 1168, Study 3 Method) states: "For the moral character index, we used the
  same item stems and most of the same items as in Study 1... The resulting 36-item
  measure included the facets of benevolence (six items), respectfulness (six items),
  general morality (four items), dependability (four items), and the same four-item
  measures of loyalty, honesty, interpersonal fairness, and fraud avoidance as in Study 1.
  Targets and informants responded to all items using a 5-point scale anchored by strongly
  disagree and strongly agree." So Study 3's loyalty facet is identical in content to
  Study 1's (same four MCQ items), just re-collected on a new (Study 3) sample —
  consistent with `cov_moralgroup` values ("average"/most-moral/least-moral) and the
  `T_*` target-ID pattern in `cov_tid`, which only exist in the Study 3 nomination design.

## Item-to-code mapping (itmcql1-4)
`normdat-labels.csv` gives the four MCQ Loyalty items under their own standard numbering:
```
mv.MCQ.L1, Loyalty, is a loyal person
mv.MCQ.L2, Loyalty, shifts their loyalties easily
mv.MCQ.L3, Loyalty, believes it is important not to betray people
mv.MCQ.L4, Loyalty, wants to be loyal even when its hard
```
Two of these (L3, L4) are independently confirmed verbatim in the published paper's own
prose, in two separate places, as the loyalty facet's example items ("Wants to be loyal
even when it's hard"; "Believes it is important not to betray people") — a two-source
match for those two.

The `itmcql<n>` -> MCQ `L<n>` numeric correspondence (rather than assuming presentation
order) is additionally supported by the `.do` file's reverse-scoring convention: line 1576
drops a set of `*r`-suffixed recoded variables, including `itmcql2r`, alongside
`itmcqh1r` (Honesty item 1) and `itmcqf3r` (Fairness item 3). Cross-checking
`normdat-labels.csv`, MCQ.H1 = "doesn't believe that honesty is that important" and MCQ.F3
= "doesn't believe it is important to treat others fairly" — both are the one
negatively-worded item in their four-item facet, and both carry the `r`-suffix reverse
code at exactly that item number. MCQ.L2 = "shifts their loyalties easily" is likewise the
one negatively-worded loyalty item, and it is the one carrying `itmcql2r`. This pattern
across three separate facets (H, F, L) each independently confirms that `itmcql<n>`'s
numeric suffix is the MCQ's own official item number, not just sequential presentation
order — so:
- `itmcql1` -> "is a loyal person"
- `itmcql2` -> "shifts their loyalties easily" (the reverse-scored item)
- `itmcql3` -> "believes it is important not to betray people"
- `itmcql4` -> "wants to be loyal even when it's hard"

## has_bare_integer_items
FALSE, as stated in the dictionary row — `item` values are the named codes
`itmcql1`-`itmcql4`, not bare integers. As with the sibling `study1_dependability` table,
the same category of reconstruction judgment was still required (decoding what the prefix
means and confirming the numeric suffix maps to a specific item, not just its facet), and
was resolved via the paper's own quoted examples plus the OSF norming codebook plus the
`.do` file's reverse-coding pattern (three converging sources), not by range-matching.

## Structure of output
One `section_id` (`sun_2025_morality_study3_loyalty_1`) for all four items, since they
share the same instrument-wide response format and the same construction (target's name
prepended directly, no additional shared stem phrase). Per the instructions/section_prompt
boundary rule:
- `instructions` (whole-instrument framing, response-format specific): "Informants rated
  the extent to which each of these statements described their target using a 5-point
  scale anchored by strongly disagree and strongly agree." — mirrors the Study 1
  dependability table's instructions text, since Study 3 uses the identical response
  format per the paper's Study 3 Method section quoted above.
- `section_prompt`: `[Target's name]`. The paper states that, unlike the compassion/
  respectfulness/dependability facets (which get the stem "[Target's name] is someone
  who…"), loyalty items (along with honesty, interpersonal fairness, fraud avoidance) are
  "simply preceded by the target's name" with no added stem phrase — so `section_prompt`
  here is just the bare name placeholder, and the full items already read naturally as
  "[Target's name] is a loyal person," etc.
- `item_text` holds only the item-specific statement (e.g., "is a loyal person"), matching
  the terseness of the source (`normdat-labels.csv` gives these as short unpunctuated
  phrases; the paper quotes them the same way), consistent with how the sibling
  dependability table split stem vs. item text.

`option_text` populated only for resp 1 ("strongly disagree") and resp 5 ("strongly
agree") — the paper states the scale is "anchored by" these two endpoints only; no verbal
labels for intermediate points 2-4 are given anywhere in the paper or OSF materials, so
those were left blank rather than invented (same convention as `study1_dependability` and
the `firstborn_personality` reference example).

`correct_response` left blank throughout — this is a personality/character rating measure,
no scoring key. (Note: item 2 being reverse-scored in the analysis pipeline is a scoring/
recoding decision, not a "correct answer" key, so it is not recorded in
`correct_response`.)

## OCR / image-based extraction
None needed. The source PDF was text-based (not scanned/image), previously extracted with
`pdftotext -layout` for the sibling table; reused directly. `normdat-labels.csv` is a plain
CSV. No OCR used anywhere in this extraction.

## Derived vs. directly-read values
- `item_text` for all four items is a verbatim/near-verbatim transcription from
  `normdat-labels.csv`'s MCQ Loyalty rows; two of the four (L3, L4) are independently
  cross-confirmed as verbatim quotes in the published paper's own prose. The other two
  (L1, L2) are read directly from `normdat-labels.csv` only — not independently quoted in
  the paper itself, so they carry one-source (not two-source) confirmation for the exact
  wording, though the `itmcql1`/`itmcql2` -> L1/L2 *numbering* is corroborated by the
  reverse-coding pattern described above.
- `option_text` anchors ("strongly disagree"/"strongly agree") are a direct,
  paraphrase-free read of the paper's stated Study 3 scale anchors.
- `instructions` and `section_prompt` are close transcriptions/paraphrases of the paper's
  own description of the informant rating task and item-stem convention (the paper does
  not print the instrument in a literal instructions-paragraph form a participant would
  see, so this is the closest available literal text, not an invented summary) — same
  approach as the sibling `study1_dependability` table.
- The `itmcql<n>` -> MCQ `L<n>` decoding is an inference, but one confirmed by three
  converging sources (paper prose for 2 of 4 items, OSF norming codebook for all 4, and
  the `.do` file's reverse-scoring pattern for the numbering itself) rather than assumed
  from the naming pattern alone.

## Source type used
Published journal article (author's open-access postprint PDF) as primary source for the
Study 3 measure description and two of the four items' verbatim wording, cross-checked
against the dataset's own OSF repository (`data-clean/normdat-labels.csv`, a related
norming-study codebook using the MCQ's own item numbering) for all four items' wording,
and against this repo's existing `data/sun_2025_morality.do` processing script (for the
`itmcql<n>` variable-naming and reverse-scoring convention, not for item text itself,
since the `.do` file contains no item text or labels). Two OSF supplementary Excel files
(`study3-itemdat.xlsx`, `study3-suppdat.xlsx`) that might have offered a fully
Study-3-specific codebook were located but are password-protected and could not be
opened.

## Ambiguities / items not extracted
None left unextracted — all four ground-truth items were mapped and validated exact
against `.gt_sun_2025_morality_study3_loyalty.rds` (`unique(item)` and `unique(resp)`,
NA excluded, match exactly). The only residual uncertainty is that L1/L2's exact wording
is confirmed by one source (`normdat-labels.csv`) rather than two, since the paper only
quotes L3 and L4 verbatim — noted above, not logged to `pending_index_notes.csv` since the
mapping itself (which code = which item) has multi-source corroboration and validation
passed exactly; this is a wording-provenance nuance, not a structural discrepancy.
