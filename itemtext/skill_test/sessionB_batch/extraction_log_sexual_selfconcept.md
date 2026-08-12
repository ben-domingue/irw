# Extraction log: sexual_selfconcept

## Source used
Same pattern as `firstborn_personality`/`fisher_temperment`: the dictionary's URL (for
data) + Reference gave `http://openpsychometrics.org/_rawdata/MSSCQ.zip`, which
downloaded cleanly (HTTP 200, ~771KB) and contained `MSSCQ/data.csv` (raw response file,
columns `Q1`...`Q100`, `age`, `gender`) and `MSSCQ/codebook.txt` (windows-1252 encoded;
converted to UTF-8 with `iconv` — this fixed mangled `’` apostrophes rendered as `�` in
the raw bytes). Cached at
`.cache/sexual_selfconcept/MSSCQ/MSSCQ/{data.csv,codebook.txt,codebook_utf8.txt}`.

The codebook gives full literal text for all 100 items (`Q1` through `Q100`), each
numbered `N. <text>`, plus the shared 1-5 response-scale definition and two ancillary
survey questions (`base`, `gender`, `age`) that are not part of the psychometric item
set and are not in the IRW ground truth.

Also attempted `http://www4.semo.edu/snell/scales/MSSCQ.HTM` (Snell's own scale-listing
page) — DNS resolution failed (`ENOTFOUND www4.semo.edu`, page appears dead/decommissioned)
and `web.archive.org` fetches are blocked in this environment (tool-level restriction), so
could not retrieve an archived copy directly. Used a web search instead (see below) to
independently corroborate the MSSCQ's known 20-subscale structure (Snell's published
subscale-to-item mapping), which was not needed for item-text recovery (the codebook
already gives full literal text for every item) but was used as a secondary check on
plausibility of the item ordering/reverse-scoring pattern.

## Structure discovered
Ground truth items are `"1"`-`"100"` (bare integers), resp 1-5 — matches the codebook's
`Q1`...`Q100` exactly, 100 items, no discrepancy.

The raw `data.csv` header row is `Q1, Q2, ..., Q100, age, gender` — i.e. the raw data
file's own column order is the same ascending 1-100 numbering as the codebook's item
list. This is a stronger check than range-plausibility alone: the raw file that (almost
certainly) fed the IRW long-format pivot has its columns in the identical order as the
codebook's numbered item text, so bare-integer `item` "N" maps unambiguously to codebook
item N by direct positional correspondence in the source data file itself, not just by
inferred presentation order in a separate document.

As a secondary corroboration, a web search (not the primary evidence — see caveat above
on the dead semo.edu page) surfaced the MSSCQ's published 20-subscale structure (5 items
each), e.g. Sexual-anxiety = items {1,21,41,61,81}, Sexual self-efficacy = {2,22,42,62,82},
etc., interleaved across the 1-100 range rather than in contiguous 5-item blocks. This
matches the codebook's own `(R)` reverse-scored markers, which appear at items 27, 47,
68, 77, 88, 97 — consistent with the search result's claimed reverse-keyed items for the
Sexual-assertiveness (27R,47R), Sexual-optimism (68R), Fear-of-sex (77R,97R) subscales.
This cross-check was corroborating only; it did not change the extraction, since the
codebook already supplies literal item text keyed to the exact same 1-100 numbering used
in the raw data file.

## Structure of output
One `section_id` (`sexual_selfconcept_1`) for the whole instrument, blank
`section_prompt`. The codebook presents all 100 items as a single flat numbered list
under one shared instruction/scale-description line — it does not group them into named
subscale blocks with distinct framing text (the subscale structure exists in the
published scoring key, per the web search above, but is not how the source
data-collection instrument itself was administered/presented per the codebook). Per
SKILL.md's rule ("use a single trivial section_id ... when the instrument has no real
testlet/passage grouping"), a single section was used rather than one section per
subscale or one per item.

`instructions` = the codebook's scale-anchor description, trimmed of the "Q1 through
Q100" item-range framing (which is data-file bookkeeping language, not participant-facing
instruction text): "The items were rated on a scale where 1=Not at all characteristic of
me, 2=Slightly characteristic of me, 3=Somewhat characteristic of me, 4=Moderately
characteristic of me, 5=Very characteristic of me." All five scale points have literal
verbal anchors in the source (unlike `firstborn_personality`'s IPIP-50 block, which only
labeled 1/3/5) — all five were used as `option_text`.

`item_text` kept exactly as transcribed from the codebook, including inline `(R)`
reverse-scoring annotations on the ~6 items that carry them (e.g. item 27: "I'm not very
direct about voicing my sexual needs and preferences. (R)") — this is literal source text
in the codebook itself, not an added interpretation.

## Ambiguities
- The MSSCQ has a well-documented 20-subscale factor structure (Snell et al.), but the
  *administered instrument* (per the codebook) presents items as one continuous
  undifferentiated list, so no subscale-level `section_id`/`section_prompt` grouping was
  applied — this is a judgment call favoring what was actually shown to respondents over
  the published scoring taxonomy. If a future pass wants subscale-level `section_id`s for
  downstream tagging/analysis purposes, note that the subscale-to-item mapping is
  interleaved (e.g. items 1,21,41,61,81 all belong to Sexual-anxiety), not contiguous, so
  it can't be reconstructed from the raw item order alone.
- `correct_response` left blank throughout — this is a self-report personality/attitude
  measure with no scoring key beyond raw Likert value.
- Two ancillary variables in the raw data (`base` — relationship-type framing question —
  and `gender`) are not part of the 100-item ground truth `item` set and were correctly
  excluded from the candidate table.

## Items not extracted
None — all 100 ground-truth items matched and were extracted with full literal item text
and all 5 response-scale anchors; validated exact `item`/`resp` set match against the
cached ground truth (`.gt_sexual_selfconcept.rds`).

## OCR / image-based extraction
Not needed. The codebook is a plain-text file (`codebook.txt`, windows-1252 encoded,
converted to UTF-8 via `iconv`) with fully machine-readable literal item text — no PDF,
scanned image, or OCR step was involved anywhere in this extraction.

## Derived vs. directly-read values
No item text, option text, or instructions were derived/computed — all were read
directly, verbatim, from the codebook (aside from trivial whitespace/numbering-prefix
stripping, e.g. removing the leading "27. " before the item text). The only "derived"
fact used was the item-number-to-item-text mapping itself, and that mapping was
established by direct positional correspondence (raw `data.csv` column order `Q1...Q100`
== codebook numbering `1...100`), not by inference, range-matching, or guesswork.

## Source type used
Raw-data-file column headers (`data.csv`: `Q1`...`Q100`) cross-checked against a website
codebook (`codebook.txt`, a plain-text companion file bundled in the same zip on
openpsychometrics.org) — both are companion files of the dataset's own hosting page, not
a PDF manual or paper appendix. A secondary web search was used only to corroborate the
published subscale structure (not needed for item-text recovery itself); the dead
`www4.semo.edu` scale-listing page and Wayback Machine (blocked in this environment) could
not be reached directly.

## Bare-integer validation check
Since `has_bare_integer_items=TRUE`, item-order was NOT confirmed by resp-range
plausibility alone (all 100 items share the same 1-5 Likert range, so that check would be
uninformative). Instead: (1) confirmed the codebook discloses exactly 100 items,
numbered 1-100, matching the ground truth `item` count/range exactly; (2) confirmed the
raw `data.csv` header row's column order (`Q1, Q2, ..., Q100`) is the identical ascending
sequence as the codebook's item numbering, i.e. the source data file itself (not just a
separate prose document) encodes item-number-to-item-text correspondence positionally;
(3) corroborated via a web search that the MSSCQ's independently-published subscale
structure and reverse-scored item list (interleaved subscales, reverse-keyed items at
27/47/68/77/88/97) is consistent with the codebook's own inline `(R)` markers at those
same item numbers. Result: PASS — no discrepancy found. `unique(candidate$item)` == `1:100`
and `unique(candidate$resp)` == `1:5`, exactly matching the cached ground truth.
