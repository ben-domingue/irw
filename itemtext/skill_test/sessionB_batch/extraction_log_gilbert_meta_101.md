# Extraction log: gilbert_meta_101

## Source used
- Main paper: Schumacher L, Klein JP, Elsaesser M, Härter M, Hautzinger M, Schramm E, Kriston L.
  "Implications of the Network Theory for the Treatment of Mental Disorders: A Secondary Analysis
  of a Randomized Clinical Trial." *JAMA Psychiatry*. 2023;80(11):1160-1168.
  doi:10.1001/jamapsychiatry.2023.2823. Fetched as the open-access PMC HTML full text
  (PMC10448377), cached at `.cache/gilbert_meta_101/article.html`.
- OSF record for the *data* URL in the dictionary (osf.io/fhqmk) contains only the analysis
  scripts (`preparatory_analysis.R`, `main_analysis_final.R`) and the already-derived binary
  `data.csv` (columns are already the 9 symptom names, 0/1) plus a 2-page
  "Model specification" PDF (statistical model only, no item content) — no raw IDS item-level
  data or codebook. All cached at `.cache/gilbert_meta_101/`.
- Companion paper (same trial data, same 9 derived symptoms) used only to try to recover the
  item-to-symptom mapping: Schumacher et al., "Predicting the outcome of psychotherapy for
  chronic depression by person-specific symptom networks," *World Psychiatry* 2024;23:411-420
  (PMC11403179, open access) — its own supplementary PDF (OSF osf.io/eqbzt, view-only link found
  via the paper's Acknowledgements) was also fetched and checked; it contains model-specification
  detail only, no mention of "IDS" or item-level content at all.

## Source type used
Open-access journal HTML (PMC full text) for the primary paper's Methods/Measures section and
Figure 1 legend (both quoted verbatim below). No PDF/OCR was used for the primary source — PMC
serves this article as clean HTML text. The one genuinely useful non-HTML source was the OSF
"Model specifications.pdf" (native-text PDF, read directly, no OCR needed) — it was mostly a
dead end (formula-level detail only).

**JAMA Psychiatry Supplement 1 (contains eTable 4, the actual IDS-item-to-symptom mapping) could
not be retrieved.** Two independent access attempts were made:
1. PMC's own supplement binary endpoint
   (`pmc.ncbi.nlm.nih.gov/articles/instance/10448377/bin/jamapsychiatry-e232823-s001.pdf`) —
   returns an interactive "Preparing to download..." page gated by a JavaScript proof-of-work
   challenge (`window.ncbi.pmc.pow.init(...)`), not fetchable via a plain HTTP client.
2. The JAMA Network CDN link surfaced from the publisher's own article page
   (`cdn.jamanetwork.com/ama/content_public/journal/psych/939255/yoi230061supp1_prod_...pdf`) —
   returns HTTP 403/`MissingKey` (a time-signed URL that had already expired/required an
   authenticated session by the time it was reached).

## OCR / image-based extraction
None used. All text extracted here came from machine-readable HTML (PMC article) or native-text
PDF (OSF "Model specifications.pdf", checked but not ultimately load-bearing for the output).
No image/figure OCR was performed — Figure 1's *caption text* (not the image itself) was used,
and that caption is plain HTML text in the PMC page, not an image.

## Structure discovered
Ground-truth `item` values (`appetite, concentration, mood, pleasure, psychomotor, self_worth,
sleep, suicidal_ideation, tiredness`) are **not bare integers** — `has_bare_integer_items` is
correctly `FALSE` for this table, and each item name is already a literal, semantically
meaningful symptom-domain code, so no position/order reconstruction against the paper was
needed to identify *which* item is which.

From the Methods/Measures section (quoted verbatim):
> "Depression symptoms were assessed with the Inventory of Depressive Symptomatology, a 28-item
> self-reported measure. Participants were asked before every treatment session how they
> experienced a specific symptom on a 4-point Likert scale. Due to limitations of analyses for
> ordinal data, we dichotomized all items with a score of 0 and 1 (none to mild intensity) into
> "symptom not present" and a score of 2 and 3 (moderate to strong intensity) into "symptom
> present." All analyses were conducted on the item level. As there was considerable topological
> overlap between individual items, we selected only items that correspond to the 9 symptoms of
> major depressive disorder as defined in the DSM-5, similar to other studies (eTable 4 in
> Supplement 1). When several items assessed the same symptom, these were qualified as present
> if one of them was present."

From Figure 1's legend (quoted verbatim, gives the paper's own literal label for each of the 9
numbered symptom nodes — used directly as `item_text`):
> "Numbered circles represent symptoms (1, sleeping problems; 2, reduced pleasure and/or
> interest; 3, psychomotor problems; 4, change in appetite and/or weight; 5, depressive mood;
> 6, reduced self-worth; 7, suicidal ideation; 8, tiredness; and 9, concentration problems)"

These 9 labels map 1:1 and unambiguously onto the 9 ground-truth `item` codes by name
(sleep->1, pleasure->2, psychomotor->3, appetite->4, mood->5, self_worth->6,
suicidal_ideation->7, tiredness->8, concentration->9), so `item_text` for each row is the
paper's own literal phrase for that symptom.

`resp` mapping is exact and explicit in the Methods text: 0 = "symptom not present"
(underlying IDS score 0-1), 1 = "symptom present" (underlying IDS score 2-3). Used verbatim
as `option_text`.

`instructions` (table-wide, applies regardless of `section_id`) uses the paper's own framing
sentence for how the instrument was administered ("Participants were asked before every
treatment session how they experienced a specific symptom on a 4-point Likert scale.") — this
is deliberately NOT the original IDS-SR's actual participant-facing instructions text (that
text is part of the IDS instrument itself and is not reproduced in this secondary-analysis
paper); it's the paper's description of the administration procedure, which is the most
specific instructions-level text this source discloses.

Single `section_id` (`gilbert_meta_101_1`) used for all 9 items with blank `section_prompt` —
no testlet/passage grouping exists; the 9 symptom domains are presented as a flat list, not a
shared-passage structure.

## Derived vs. directly-read values (important — this is a collapsed/derived measure)
**This table is NOT the raw IDS item-response data.** Per the Methods text quoted above, each of
the 9 published `item` values is a **derived composite** of one or more original 28 IDS-SR items,
constructed by the paper's authors in two steps that happened upstream of anything recoverable
from the sources available to this extraction:
1. Each of the 28 original IDS-SR items (each itself a 4-point 0-3 Likert item) was dichotomized
   individually (0-1 -> not present, 2-3 -> present).
2. Items belonging to the same DSM-5 symptom domain were then OR-combined ("qualified as present
   if one of them was present") into a single binary domain flag — i.e., `appetite` (etc.) in the
   live IRW data is not any single original questionnaire item, it is `max()` over however many
   original IDS items loaded onto that domain.

The paper explicitly says this original-item-to-domain assignment is documented in **eTable 4 of
Supplement 1**, which — despite two independent access attempts (PMC binary endpoint blocked by a
JS proof-of-work gate; JAMA CDN link expired/403) — could not be retrieved. As a result:
- `item_text` in this output is the paper's own **domain-level** label (from the Figure 1
  legend), not the literal wording of the underlying original IDS-SR item(s) that were OR'd
  together for a given domain (e.g., which specific IDS items besides "appetite decrease" and
  "appetite increase" were merged into `appetite` is not disclosed by any source reached).
- `option_text` ("symptom not present" / "symptom present") reflects the *domain-level*
  post-collapse presence/absence semantics quoted directly from the Methods text, not the
  original item's own 4-point response-option wording (which is standard IDS-SR anchor text,
  e.g. "I feel sad" 0-3, and is itself not reproduced in this secondary paper either).
- Despite this, `item` and `resp` values written here match the live IRW data **exactly** — the
  9 domain-level codes and the 0/1 coding are precisely what the paper (and the OSF-hosted
  `data.csv`) already uses, so no invented items/values were needed; the derivation gap only
  affects how literal/granular `item_text` and `option_text` can be (domain-level, not
  original-item-level).

## Ambiguities
- The exact count and identity of which of the 28 IDS-SR items feed into each of the 9 domains
  (e.g., is `sleep` an OR of all 4 IDS sleep items 1-4, or fewer?) is unrecoverable without
  Supplement 1's eTable 4. Flagged in `pending_index_notes.csv` in case a future pass can access
  the supplement (e.g., via institutional access) and enrich `item_text`/`option_text` with the
  true original-item wording.
- `correct_response` left blank throughout — this is self-reported symptom presence, no scoring
  key/correct answer.

## Items not extracted
None — all 9 ground-truth items were assigned domain-level `item_text`, and both live `resp`
values (0, 1) were assigned `option_text`; validated exact `item`/`resp` set match against the
cached ground truth (`.gt_gilbert_meta_101.rds`).
