# Extraction log: gilbert_meta_25

## Source used
- Dictionary URL for data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VNLWCB
  (Schreinemachers, Pepijn, 2020, "Replication Data for: Nudging children toward healthier food
  choices...", Harvard Dataverse, DOI 10.7910/DVN/VNLWCB).
- Paper: Schreinemachers, P., Baliki, G., Shrestha, R. M., Bhattarai, D. R., Gautam, I. P.,
  Ghimire, P. L., Subedi, B. P., & Brück, T. (2020). Nudging children toward healthier food
  choices: an experiment combining school and home gardens. *Global Food Security*, 26, 100454.
  Open-access full text located and read via PubMed Central: **PMC7726313**
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC7726313/).
- No existing `data/` processing script in this repo references VNLWCB / gilbert_meta_25 /
  Schreinemachers / "school...home...garden" (checked via grep before starting).

## Source type used
Journal article full text (PMC open-access mirror), Methods/Measures section. The Harvard
Dataverse dataset landing page itself (`dataset.xhtml?persistentId=...`) returned empty/
unfetchable content via the available web-fetch tool on three separate attempts (the plain
`dataset.xhtml` page, the `citation?persistentId=...` redirect target, and the Dataverse
native JSON API endpoint `api/datasets/:persistentId/`) — consistent with the task note that
this depositor's page might behave differently from the WAF-blocked ones, but in this case it
was simply unretrievable rather than confirmed present-but-blocked. No supplementary/appendix
questionnaire document was found — the PMC article text explicitly states no separate
Appendix/Supplementary Data section listing a full survey instrument is attached to the
article, and it directs readers to the Dataverse repository (which could not be inspected
directly) for the underlying data.

## OCR / image-based extraction
None performed. All text was obtained from machine-readable HTML (PMC full text), not from a
scanned image or PDF requiring OCR.

## Structure discovered
Ground-truth items are `S11_1`..`S11_15` (resp 1-4), matching the paper's stated "15 multiple
choice questions with four answer options" used to measure children's food and nutrition
knowledge (verbatim, paraphrased from PMC text: "Food and nutrition knowledge were measured
using 15 multiple choice questions with four answer options each of which exactly one was
factually correct"). This confirms: instrument identity, item count (15, matches ground truth
exactly), and response cardinality (4 options, matches ground truth resp values 1-4 exactly —
`resp` here represents the raw selected answer position, not a recoded correct/incorrect
indicator; the paper separately reports a *derived* proportion-correct score which is NOT what
is stored in the live IRW response data).

The paper gives only **three illustrative example items**, presented as examples of the three
knowledge domains probed (food-body function associations, nutrient content, healthy-diet
composition) — not as a numbered or ordered list, and not tied to any stated item position
(e.g. nothing says "item 1 is..."):
1. "Which food is good for your eyes? 1. Cucumber; 2. Beans; 3. Carrots; 4. Chicken meat"
2. "Which food has lots of Vitamin C? 1. Carrots; 2. Chicken meat; 3. Lemons; 4. Rice"
3. "Which food is not part of a healthy diet? 1. Vegetables; 2. Carbonated drinks; 3. Meat; 4. Fruit"

## Derived vs. directly-read values
- `instrument`, and the general instructions/design description, are directly transcribed
  (paraphrased where noted) from the PMC Methods text.
- `item`/`resp` values in the candidate output are the exact ground-truth values from
  `irw_fetch`/the cached ground-truth RDS — not derived or reconstructed.
- `item_text`, `option_text`, and `correct_response` are **NOT populated** (left `NA`) for
  every one of the 15 items. This is a deliberate withhold, not an omission: the paper
  discloses only 3 of 15 items' wording, with no stated order/position, no numbering scheme,
  and no visible link between those 3 examples and the `S11_1`..`S11_15` variable names. Any
  attempt to assign one of the 3 known examples to a specific `S11_N` item, or to write plausible
  item text for the other 12, would be fabrication per the explicit instruction not to guess
  item wording (per the `gilbert_meta_38` correction precedent). No supplementary questionnaire
  document was accessible to resolve the mapping.

## has_bare_integer_items
FALSE, as given in the dictionary row — items are already semantically named (`S11_1`..`S11_15`,
"Section 11, item N" of the household/child survey instrument), so the bare-integer
position-reconstruction procedure in the skill (Step 4) does not apply here. The blocker in
this case is not item-ID ambiguity but simple non-disclosure of full item wording in the
available open-access source.

## Items not extracted
All 15 items (`S11_1`..`S11_15`): `item_text`, `option_text`, `correct_response` left blank/NA.
`instrument` and a paraphrased `instructions` field (measure-level, not item-level) are
populated for every row. `item`/`resp` match the ground truth exactly (validated:
`unique(item)` and `unique(resp)` identical to the cached ground truth).

## Validation result
Exact match on `item` and `resp` sets against the cached ground truth (15 items x 4 resp
values = 60 rows). Item-level text coverage: 0/15 (partial/discrepant — logged below).
