# Extraction log: mpsycho_lakes

## Source used
The dictionary URL (for data) is the CRAN landing page for the `MPsychoR` R package
(https://cran.r-project.org/web/packages/MPsychoR/index.html), which contains the `Lakes`
dataset used by the source paper (Lakes & Hoyt, 2009, Journal of Clinical Child &
Adolescent Psychology). MPsychoR was already installed locally (`library(MPsychoR)`
succeeds). Following the same pattern as `mpsycho_rmotivation`/`mpsycho_ceaq`, the
`?Lakes` help page was fetched via `tools::Rd_db("MPsychoR")` / `Rd2txt()` and cached at
`.cache/mpsycho_lakes/Lakes_Rd.txt`.

Unlike `Rmotivation`/`CEAQ`, the `?Lakes` help page does **not** give literal item
wording — it only describes the instrument at the construct level ("The response to
challenge scale (RCS) is a theory-derived, observer-rated measure of children's
self-regulation... 3 domains: cognitive (6 items), affective/motivational (7 items), and
physical (3 items)") and cites three source papers: Lakes (2012, IJEPA), Lakes & Hoyt
(2004, JADP), and Lakes & Hoyt (2009, JCCAP — the dictionary's own Reference/DOI).

The dictionary's own reference paper, Lakes & Hoyt (2009), was fetched via PMC
(https://pmc.ncbi.nlm.nih.gov/articles/PMC3650138/) but its WebFetch summary explicitly
stated the full 16-item list/anchors are not in that paper and are given instead in
Lakes & Hoyt (2004) or Lakes (2012). Lakes (2012),
"The Response to Challenge Scale (RCS): The Development and Construct Validity of an
Observer-Rated Measure of Children's Self-Regulation" (open access via PMC,
https://pmc.ncbi.nlm.nih.gov/articles/PMC4349369/), was fetched and cached as raw HTML
(`.cache/mpsycho_lakes/lakes2012_pmc.html`) and parsed directly (tags stripped, not
relying on the WebFetch summarizer model) to guard against fabricated table content —
this located **Appendix A** (the literal RCS rating form, all 16 bipolar-adjective items
with their 1–7 scale, e.g. "Attentive 1 2 3 4 5 6 7 Inattentive") and **Appendix B**
("RCS Items by Subscale (Based on Factor Analysis; Lakes & Hoyt, 2004)"), which lists all
16 items grouped under Cognitive/Affective/Physical-Motor headers. The two appendices'
item counts (6/7/3 = 16) cross-check exactly against both the `?Lakes` help page and the
live ground-truth item set (`aff1`..`aff7`, `cog1`..`cog6`, `phy1`..`phy3` = 16 items).

## Structure discovered
- Appendix A gives the literal rater instructions ("After the child's performance on the
  task has concluded, please rate the child on each of the following characteristics:")
  and the literal bipolar-adjective pair + 7-point scale for every item, in rating-form
  presentation order, e.g. "Vulnerable 1 2 3 4 5 6 7 Invincible".
- Appendix B groups the same 16 pairs by subscale (Cognitive/Affective/Physical-Motor),
  in a fixed within-subscale order, but without numbering them "cog1"/"aff1"/etc. — the
  MPsychoR package's own `item` factor levels (`cog1`..`cog6`, `aff1`..`aff7`,
  `phy1`..`phy3`) are not tied to specific adjective pairs anywhere in the package
  documentation or the two source papers reachable here.
- **Item-to-code mapping is therefore a derived/positional assumption, not a directly
  confirmed one**: `cog1`..`cog6` were assigned to Appendix B's Cognitive-subscale list in
  its stated order (1st listed = cog1, ..., 6th = cog6), and likewise `aff1`..`aff7` and
  `phy1`..`phy3` to Appendix B's Affective and Physical/Motor lists in their stated order.
  This mirrors the `firstborn_personality` precedent for reconstructing item order from
  the paper's own stated presentation order when the live data's item codes don't encode
  the specific wording. This is flagged as a real discrepancy/uncertainty below — the
  *set* of 16 items and their subscale membership is fully confirmed exactly, but the
  specific number (e.g. "cog1" vs "cog2") assigned to each adjective pair within a
  subscale is not independently verifiable from any source reached.
- `item_text` for each item is written as the bipolar pair in Appendix A's literal
  low-anchor/high-anchor order (e.g. "Attentive — Inattentive"), and `option_text` is
  populated only at `resp==1` (the low-anchor word) and `resp==7` (the high-anchor word),
  left blank for `resp` 2–6 — consistent with Appendix A's literal form, which only labels
  the two endpoints of each 7-point scale, not the intermediate points.

## Source type used
- Item text, rater instructions, and response-scale anchors: open-access journal article
  (Lakes, 2012, PMC4349369), Appendix A and Appendix B, fetched as raw HTML and parsed by
  stripping tags directly (not via the WebFetch summarizer) specifically to avoid
  hallucinated/duplicated table content — an initial WebFetch summary of the same page had
  incorrectly listed "Unfit—Athletic" under both the Affective and Physical subscales,
  which was caught and discarded by cross-checking against the raw parsed text.
- `instrument` name ("Response to Challenge Scale (RCS)"): from the `?Lakes` help page
  title and Lakes (2012) Appendix A header.
- No OCR was involved — Lakes (2012) was retrieved as machine-readable PMC HTML, not a
  scanned PDF.

## OCR / image-based extraction
Not applicable. No scanned images, PDFs requiring OCR, or screenshots were used. Lakes
(2012) was fetched as PMC HTML and parsed as plain text (regex tag-stripping), and the
`?Lakes` help page was rendered R documentation text (`Rd2txt()`), not an image.

## Derived vs. directly-read values
- `item_text` (bipolar pair wording, all 16 items): directly read, verbatim, from Lakes
  (2012) Appendix A.
- `instructions`: directly quoted, verbatim, from Lakes (2012) Appendix A's header text
  above the rating items ("After the child's performance on the task has concluded,
  please rate the child on each of the following characteristics:"). Applies to the whole
  16-item instrument, so recorded once in `instructions`, not `section_prompt`.
- `option_text` (endpoint labels only, resp 1 and 7): directly read from Appendix A's
  literal low/high anchor words for each pair; resp 2–6 intentionally left blank since no
  verbal anchors are given for the interior scale points in the source.
- `section_id` (`mpsycho_lakes_cognitive` / `_affective` / `_physical`): derived, not
  source text — grouping label built from the subtest names disclosed in the `?Lakes`
  help page's `subtest` variable documentation ("Subtests (cognitive, affective,
  physical)"). `section_prompt` left blank for all rows — no literal shared passage text
  exists per section beyond the whole-instrument instructions already captured.
- **`item` code assignment within each subscale (e.g. which specific pair is "cog1" vs
  "cog2") is a derived positional mapping**, not a directly confirmed one — see
  "Structure discovered" above and the discrepancy note below.
- `correct_response`: left blank for all items — this is an observer-rated
  self-regulation scale with no scoring key.

## has_bare_integer_items
FALSE, per the dictionary row, and confirmed: all 16 ground-truth `item` values are
subscale-prefixed semantic codes (`aff1`..`aff7`, `cog1`..`cog6`, `phy1`..`phy3`), not
bare integers. However, similar to a bare-integer case, the specific *within-subscale
sequence number* (the "1" in "cog1", "2" in "cog2", etc.) is not disclosed anywhere in
the MPsychoR package or either source paper reached — only each item's *subscale
membership* is confirmed with certainty. The within-subscale ordering used here follows
Appendix B's stated list order for each subscale, the only source-provided ordering
available, and is logged as a derived assumption rather than a confirmed one.

## Items not extracted
None — all 16 ground-truth items were extracted (subscale membership and item_text
wording) and validated for item-set and resp-set match. The only open uncertainty is the
within-subscale numbering (which specific pair is "cog1" vs "cog2", etc.), not item
content or coverage.

## Discrepancy / lower-confidence flag (logged per Step 6b)
Within-subscale item numbering (`cog1`..`cog6`, `aff1`..`aff7`, `phy1`..`phy3` assigned to
specific bipolar-adjective pairs) is a derived positional mapping based on Lakes (2012)
Appendix B's list order, not independently confirmed against the MPsychoR package or
either source paper — no source discloses which specific pair the package authors coded
as "1" vs "2" within a subscale. Item *set* and *subscale membership* are fully confirmed.
Logged in `pending_index_notes.csv`.

## Validation result
Exact match: `unique(candidate$item)` == `unique(ground truth$item)` (16 items:
`aff1`..`aff7`, `cog1`..`cog6`, `phy1`..`phy3`) and `unique(candidate$resp)` ==
`unique(ground truth$resp)` after dropping `NA` (`1`..`7`) — ground truth has an 8th value
(`NA`, 62 missing observations out of 15,520) which `sort()`/the validation script's
`setdiff` logic drops automatically, so this counts as an exact resp-set match per the
skill's own validation method. Output written as `candidate_mpsycho_lakes.rds`, one row
per (item, resp) — 16 items x 7 resp values = 112 rows.
