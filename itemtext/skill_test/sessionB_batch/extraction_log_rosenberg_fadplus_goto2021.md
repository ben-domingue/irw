# Extraction log: rosenberg_fadplus_goto2021

## Naming-mismatch investigation (primary finding)

The table name `rosenberg_fadplus_goto2021` and the dictionary Reference both point to
Goto (2021), "Comparing the Psychometric Properties of Two Japanese-Translated Scales of
the Free Will and Determinism-Plus Scale" (Frontiers in Psychology, 12, 720601) — a paper
primarily about the **FAD-Plus** (Free Will and Determinism Plus Scale, 27 items, 5-point
Likert, 4 subscales). But the live ground-truth data for this table has:
- 10 items, literally named `Rosenberg_1`..`Rosenberg_10`
- `resp` values 1-4 (4-point scale)

Neither the item count (10 vs. 27) nor the response range (1-4 vs. 1-5) matches the
FAD-Plus. Confirmed directly from the paper's own Methods text (fetched full PDF,
`https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2021.720601/pdf`,
cached at `.cache/rosenberg_fadplus_goto2021/paper.pdf` / `paper.txt`):

> "The Rosenberg self-esteem scale (Rosenberg, 1965) is widely used to assess trait
> self-esteem. In this study, we used the Japanese-translated scale developed by Mimura
> and Griffiths (2007)... This scale consisted of 10 items in a four-point Likert format
> with anchors of 1 = 強くそう思わない ("Strongly disagree") to 4 = 強くそう思う
> ("Strongly agree")."

This matches the live data's 10 items / 1-4 resp range exactly, while the FAD-Plus (27
items / 1-5) does not.

**Conclusion: this IRW table is actually the Rosenberg Self-Esteem Scale (RSES,
Japanese-translated per Mimura & Griffiths, 2007), administered alongside the two
FAD-Plus translations (and other scales: locus of control, brief self-control, global
belief in a just world) as a convergent-validity measure in the same study — not the
FAD-Plus that the table name suggests.** Same pattern as `ccapsvtskhpacr_mercedes_2023_physical`
and `phq_insomnia_wang2025` earlier in this batch. Set `instrument` = "Rosenberg
Self-Esteem Scale (RSES; Japanese translation by Mimura & Griffiths, 2007)" accordingly,
not FAD-Plus.

This should be flagged in the dictionary/index — the table name and Reference describe a
study centered on the FAD-Plus, but the actual response data in this table is the RSES.

## Item order / mapping confirmation

`item` values (`Rosenberg_1`..`Rosenberg_10`) are already named codes, not bare integers
(`has_bare_integer_items` = FALSE, confirmed — no positional reconstruction of the `item`
column itself was needed). However, mapping each `Rosenberg_k` code to specific RSES item
*wording* did require confirming presentation order, since the paper doesn't print the
item text. This was cross-checked against the OSF-hosted analysis script rather than
assumed from range-matching alone:

- OSF project https://osf.io/2xbe5/ (folder "Comparing the psychometric properties of two
  Japanese-translated scales of the FAD-Plus") contains `FAD_compare_rawdata.csv` (has
  literal columns `Rosenberg_1`..`Rosenberg_10`, confirming these are the actual raw
  survey item columns) and `FAD_compare_analysis.Rmd`, which computes the self-esteem
  total score as:
  ```
  dat_cl$Self_esteem <- (dat_cl$Rosenberg_1 + (5-dat_cl$Rosenberg_2) + dat_cl$Rosenberg_3 +
    dat_cl$Rosenberg_4 + (5-dat_cl$Rosenberg_5) + (5-dat_cl$Rosenberg_6) +
    dat_cl$Rosenberg_7 + (5-dat_cl$Rosenberg_8) + (5-dat_cl$Rosenberg_9) +
    dat_cl$Rosenberg_10)/10
  ```
  i.e. items 2, 5, 6, 8, and 9 are reverse-scored (`5 - x` on a 1-4 scale), items
  1, 3, 4, 7, 10 are scored as-is. This exactly matches the standard, fixed RSES
  reverse-keyed item set and order (Rosenberg, 1965's conventional 10-item presentation:
  items 2, 5, 6, 8, 9 are the negatively-worded/reverse-scored items). Since this
  reverse-scoring pattern is a distinguishing structural fingerprint of the specific,
  universally fixed RSES item order (not something that would coincidentally match by
  chance), it corroborates that `Rosenberg_1`..`Rosenberg_10` follow the standard RSES
  presentation order, beyond just "a 1-4 Likert item exists" range-matching.
- Cached: `.cache/rosenberg_fadplus_goto2021/FAD_compare_rawdata.csv`,
  `.cache/rosenberg_fadplus_goto2021/FAD_compare_analysis.Rmd`,
  `.cache/rosenberg_fadplus_goto2021/osf_folder_listing.json`.

## Source type used

- Primary source: Frontiers in Psychology full-text PDF (open access), fetched directly
  and converted with `pdftotext -layout` (cached as `paper.pdf` / `paper.txt`). Used for
  the Methods-section description of the RSES (item count, response format, verbal
  anchors, translation citation).
- Secondary source: OSF project https://osf.io/2xbe5/ (raw data CSV + analysis Rmd), used
  to confirm the `Rosenberg_1`..`Rosenberg_10` column identity and reverse-scoring/item
  order (see above).
- The paper's own Supplementary Table 1 covers the FAD-Plus/FAD+/FAD-J items only (per
  paper text: "All items in the original scale (FAD-Plus) and translated scales (FAD+ and
  FAD-J) are listed in the Supplementary Table 1") — it does **not** cover the RSES.
- Literal item-by-item text was **not found** for either the Japanese translation
  actually administered (Mimura & Griffiths, 2007, published in *Journal of Psychosomatic
  Research* — paywalled at ScienceDirect, not accessible) or reproduced anywhere in the
  Goto (2021) paper or its OSF materials.
- Because the specific administered Japanese wording could not be recovered, `item_text`
  was populated with the **canonical published English-original RSES** (Rosenberg, 1965)
  — a fixed, public-domain, universally standard 10-item wording and order — as
  corroborating/documentary text, explicitly not claimed to be the literal Japanese text
  respondents saw. This mirrors the `phq_insomnia_wang2025` precedent in this batch (using
  the canonical published English instrument the paper cites as its translation source,
  when the paper doesn't reproduce the administered-language item text itself).

## OCR / image-based extraction

Not applicable — all source text was machine-readable (Frontiers PDF text layer via
`pdftotext -layout`; OSF CSV/Rmd plain text). No OCR was performed.

## Derived vs. directly-read values

- `item` and `resp` values (`Rosenberg_1`..`Rosenberg_10`, 1-4): directly read from the
  ground-truth cached data — not derived/guessed.
- Instrument identity (RSES, not FAD-Plus), item count (10), response format (4-point),
  and verbal anchor text for resp=1 and resp=4 (強くそう思わない "Strongly disagree" /
  強くそう思う "Strongly agree"): directly read/quoted from the paper's own Methods text.
- `option_text` for resp=2 and resp=3: left **blank** — the paper only discloses the two
  endpoint anchors verbatim, not labels for the interior scale points, so no label was
  invented for 2/3 (same convention as `firstborn_personality`'s unlabeled midpoints in
  this batch's model example).
- `item_text` (English RSES wording per item): **derived** from the canonical published
  Rosenberg (1965) English original in its fixed conventional order, cross-checked
  against this study's own reverse-scoring pattern (see "Item order / mapping
  confirmation" above) rather than assumed from response-range matching alone. Not
  directly read from this paper (which doesn't print item text) or from the specific
  Mimura & Griffiths (2007) Japanese translation actually administered (inaccessible,
  paywalled).
- `instructions` field: no literal participant-facing instruction stem is quoted anywhere
  in the paper for the RSES specifically (it's introduced as one of a battery of six
  scales administered in sequence). The paper's own Methods-section sentence describing
  the scale's format ("This scale consisted of 10 items in a four-point Likert format
  with anchors of 1 = ... to 4 = ...") was used verbatim in `instructions` instead, since
  it's the only literal descriptive text available and is analogous to how
  `firstborn_personality`'s `instructions` field used a codebook's descriptive sentence
  rather than a separately-quoted participant instruction.
- `instrument` field: set to "Rosenberg Self-Esteem Scale (RSES; Japanese translation by
  Mimura & Griffiths, 2007)" per the naming-mismatch investigation above, overriding what
  the table name and dictionary Reference would naively suggest (FAD-Plus).

## has_bare_integer_items

FALSE, as stated in the dictionary row — ground-truth items are already the named codes
`Rosenberg_1`..`Rosenberg_10`, not bare integers, so no position-based bare-integer
reconstruction was needed for the `item` values themselves (only the item *text* mapping,
per above, relied on cross-checked positional/reverse-scoring order since neither the
paper nor its supplementary materials print the RSES item-by-item wording).

## Ambiguities / discrepancies

1. **Naming mismatch** (see above, main finding): table name/Reference describe a study
   centered on the FAD-Plus; live data and correct `instrument` are the RSES.
2. **Item text not verbatim from the administered Japanese translation**: used the
   canonical English-original Rosenberg (1965) RSES wording (the source the actually-used
   Mimura & Griffiths 2007 Japanese translation is itself translated from) rather than the
   literal Japanese wording respondents saw, because neither the paper, its OSF materials,
   nor an accessible copy of Mimura & Griffiths (2007) reproduce it. Logged to
   `pending_index_notes.csv`.
3. **Interior Likert-scale labels (resp=2, resp=3) not disclosed**: only the 1 and 4
   endpoint anchors are quoted in the paper; `option_text` left blank for 2 and 3 rather
   than invented.

## Validation result

Exact match: `unique(candidate$item)` == `unique(irw_fetch-equivalent ground truth$item)`
(10 items, `Rosenberg_1`..`Rosenberg_10`) and `unique(candidate$resp)` ==
`unique(ground truth$resp)` (1, 2, 3, 4). Confirmed via direct R comparison
(`setequal()` both TRUE) against `.gt_rosenberg_fadplus_goto2021.rds`.
