# Extraction log: gilbert_meta_107

## Source type used
CEGA Working Paper WPS-230 (2023-08-16), Cohen, Isabelle; Abubakar, Maryam; Perlman,
Daniel (2023), "Pathways to Choice: A Bundled Intervention against Child Marriage,"
Center for Effective Global Action, UC Berkeley. Hosted open-access on eScholarship
(https://escholarship.org/uc/item/33j1k1k4, DOI 10.26085/C31C71 — the paper DOI itself,
distinct from the dataset DOI 10.26085/C31C71 given in the dictionary row, which pointed
at the same working paper). This is a working paper, not a peer-reviewed journal article
— matches the task brief's expectation of a report-style source rather than a traditional
journal article.

The `dataverse.harvard.edu` dataset landing page
(doi:10.7910/DVN/899DIN) was NOT used and was not even attempted directly, per the task's
warning that this host has AWS-WAF-blocked every prior `gilbert_meta` table in this batch.
Pivoted straight to the paper itself instead, which turned out to contain everything
needed.

Cached at `itemtext/.cache/gilbert_meta_107/`:
- `escholarship_page.html` — the escholarship.org landing page (JS-rendered SPA shell,
  19 lines, not useful on its own)
- `paper_raw.pdf` / `paper_raw.txt` — the actual working-paper PDF, fetched successfully
  via WebFetch at `https://escholarship.org/content/qt33j1k1k4/qt33j1k1k4.pdf` (a direct
  `curl` to the same URL was blocked by CloudFront with a 403, but the WebFetch tool's
  fetch succeeded and the binary was recovered from its cached tool-result and converted
  with `pdftotext`)

## Structure discovered
The repo's own existing processing script, `data/gilbert_meta_105through107.R` (found via
grep for `899DIN` in `data/`), shows `gilbert_meta_107` is the "norm" half of Cohen et
al.'s raw survey data (`105 survey_data.dta`, columns prefixed `norm_...`), pivoted long
across baseline (`wave=0`) and endline (`wave=1`) waves. This matches the ground truth's
10 items exactly, both by name and by count.

Appendix B of the working paper ("Details on Index Construction," `paper_raw.txt` lines
1748-1768) lists an "Empowerment beliefs index" built from exactly 10 statements, each
prefixed "Disagree with statement:" (Anderson 2008 index-construction convention — each
component is coded as a (d) dummy oriented so higher = more empowered). The 10 statements
map 1:1 onto the 10 ground-truth item codes by content:

| item | statement (paper, quotation marks removed for item_text) |
|---|---|
| soneduc | "It is important that sons have more education than daughters." |
| dghthome | "Daughters should be sent to school only if they are not needed to help at home." |
| sonparent | "The most important reason that sons should be more educated than daughters is so that they can better look after their parents when they are older." |
| sonfirst | "If there is a limited amount of money to pay for tutoring, it should be spent on sons first." |
| womanfcshome | "A woman should take good care of her own children and not worry about other people's affairs." |
| manpltcs | "Woman should leave politics to the men." |
| needhus | "A woman has to have a husband or sons or some other male kinsman to protect her." |
| relyson | "The only thing a woman can really rely on in her old age is her sons." |
| agreehus | "A good woman never questions her husband's opinions, even if she is not sure she agrees with them." |
| fatherchoose | "When it is a question of children's health, it is best to do whatever the father wants." |

Confidence in this mapping is high: it is a clean, unambiguous bijection between the 10
paper statements and the 10 variable-name codes (each code contains a clearly matching
substring of its statement — "sonparent"/"look after their parents", "manpltcs"/"leave
politics to the men", "fatherchoose"/"whatever the father wants", etc.) — not a
range-matching or positional guess.

## Derived vs. directly-read values
The paper's Appendix B text is describing the **Anderson (2008) index-construction
recoding**, not necessarily the raw item-level response coding used in the underlying
`.dta` file that `data/gilbert_meta_105through107.R` reads directly (`norm_*_base` /
`norm_*` columns, unpivoted with no recoding applied in that script). The paper states
each index component is a "(d)" dummy = 1 if the respondent **disagrees** with the
(traditionally-restrictive) statement — i.e., oriented so 1 = more empowered — but this
orientation is documented for the *index*, not confirmed as the coding of the raw
`norm_*` survey variables that feed `gilbert_meta_107`'s `resp` column. Without the
Dataverse codebook (blocked, per the task brief) there is no way to confirm whether
`resp=1` in the live IRW data means "disagreed with the statement" (matching the index's
orientation) or is a raw "agreed" response with the opposite coding, or whether some
items were reverse-coded relative to others by the survey instrument itself.

Because of this, **`option_text` and `correct_response` were left blank/NA for all rows**
rather than guessing that `resp=1` → "Disagree" / `resp=0` → "Agree" (or the reverse).
`item_text` was populated with high confidence since it depends only on the item-to-
statement mapping (confirmed above), not on the resp-direction question.

## OCR / image-based extraction
None needed — the source PDF has embedded, machine-readable text (`pdftotext` extracted
cleanly, no OCR pass required).

## Items not extracted
None missing at the item level — all 10 ground-truth items were matched to literal
statement text. What's missing is the `resp`-to-`option_text` (Agree/Disagree) direction
mapping only, as detailed above.

## has_bare_integer_items
FALSE, as stated in the dictionary row — ground-truth `item` values are already
semantic/named codes (`agreehus`, `dghthome`, `fatherchoose`, `manpltcs`, `needhus`,
`relyson`, `soneduc`, `sonfirst`, `sonparent`, `womanfcshome`), not bare integers, so no
positional/reconstruction inference was needed for the item-to-code mapping — only the
item-to-statement-text mapping (via variable-name semantics, confirmed against the
paper's own appendix wording as detailed above).
