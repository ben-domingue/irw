# Extraction log: polca_cheating

## Source used
Dictionary URL points to the CRAN page for the R package `poLCA` (Polytomous Variable
Latent Class Analysis), with Reference/DOI citing Dayton, C. Mitchell. 1998. *Latent
Class Scaling Analysis*. Thousand Oaks, CA: SAGE Publications. `poLCA`'s built-in
`cheating` dataset (`data(cheating)`) is the source for this IRW table: 319
undergraduates' dichotomous responses to four academic-cheating behavior items
(LIEEXAM, LIEPAPER, FRAUD, COPYEXAM), reproduced from Dayton (1998, pp. 33, 85, Tables
3.4 and 7.1). Installed `poLCA` 1.6.0.2 from CRAN and extracted the `cheating.Rd` help
page via `tools::Rd_db("poLCA")` — cached at
`itemtext/.cache/polca_cheating/cheating_Rd.txt`.

## Source type used
**Package documentation (R help/man page), not the original instrument.** The `poLCA`
help page for `cheating` gives a narrative description of what each item measures, not
literal reproduced survey-question text:

> Students responded either (1) no or (2) yes as to whether they had ever lied to avoid
> taking an exam ('LIEEXAM'), lied to avoid handing a term paper in on time
> ('LIEPAPER'), purchased a term paper to hand in as their own or had obtained a copy of
> an exam prior to taking the exam ('FRAUD'), or copied answers during an exam from
> someone sitting near to them ('COPYEXAM').

Dayton's 1998 SAGE monograph — the actual original source of the item wording — was not
accessible (no free/open PDF found; checked ResearchGate, Google Books, SAGE Research
Methods, Amazon/Goodreads listings, none offer full text). Targeted web searches for the
literal survey-question wording (e.g. exact phrase "lied to avoid taking an exam" as a
questionnaire item) returned no hits beyond the `poLCA` help page itself and generic,
unrelated academic-dishonesty-survey literature.

## Derived vs. directly-read values
- `item_text` for all 4 items is **transcribed directly from the `poLCA` help page's
  descriptive phrasing** (near-verbatim, just detached from the "whether they had ever
  ..." framing sentence), not converted into an invented first-person question format
  (e.g. did NOT write "Have you ever lied to avoid taking an exam?"), since that
  reformatting would be reconstructing plausible-sounding wording rather than
  transcribing what the source actually says. Treat `item_text` here as the closest
  available paraphrase of item content, not confirmed literal instrument wording.
- `resp`/`option_text` mapping (0=No, 1=Yes) was **derived, not directly read**: the
  help page states the original package coding is 1=no, 2=yes. Confirmed via
  `data(cheating)` in the installed package that raw counts are 285 "1" / 34 "2" for
  LIEEXAM. Ground-truth IRW `resp` values are 0/1, with 0 the majority level (285) and 1
  the minority (34) for LIEEXAM — same skew, one-off shifted coding — so mapped
  0=No, 1=Yes (i.e. IRW recoded the package's 1/2 down to 0/1, preserving order).
  Verified this pattern holds for all four items (No count > Yes count in both the
  ground truth and the installed package's raw data for every item).
- `instructions` and `section_prompt` left blank: the help page documents response
  *coding* (no/yes) but not the literal instructions/framing text given to
  participants, and no other accessible source discloses it.
- `correct_response` left blank: behavior self-report items, no scoring key.
- Single trivial `section_id` (`polca_cheating_1`), no real testlet/passage grouping —
  the four items are an unordered checklist of cheating behaviors, not a
  shared-passage/testlet structure.

## OCR / image-based extraction
None. The `poLCA` package help page was read as R documentation text
(`tools::Rd_db()` + `Rd2txt()`), not an image or scanned PDF — no OCR involved.

## has_bare_integer_items
FALSE, as stated in the dictionary row — items already carry semantic codes
(`COPYEXAM`, `FRAUD`, `LIEEXAM`, `LIEPAPER`), so no item-to-position reconstruction was
needed; the 4 ground-truth item codes map 1:1 to the 4 named variables in `poLCA`'s
`cheating` data frame.

## Items not extracted
None — all 4 ground-truth items and both resp values (0, 1) matched and were extracted;
validated exact item/resp set match against the cached ground truth
(`.gt_polca_cheating.rds`).

## Discrepancy logged
Logged to `pending_index_notes.csv`: `item_text` is the `poLCA` package documentation's
paraphrase of item content (confirmed accurate as to what each item measures, per
cross-check against the installed package's data), not verified literal wording from
Dayton (1998)'s original instrument, which was not accessible. `instructions` left
blank for the same reason. This is a full item/resp match (exact validation), with the
open discrepancy being text *fidelity* (paraphrase vs. literal), not coverage.
