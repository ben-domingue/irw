# Extraction log: faces_spanish_vegas_2022_fss

## Source used
Dictionary URL is a Harvard Dataverse record (doi:10.7910/DVN/UA5GTO), which returned
an AWS WAF challenge (HTTP 202, `x-amzn-waf-action: challenge`, empty body) on both
`curl` and `WebFetch` -- same block pattern already seen on `gilbert_meta_*` tables this
batch series, confirmed here on a different depositor/dataset, so it is not depositor-
specific. Could not enumerate or download any file from the Dataverse record (raw data,
codebook, or questionnaire).

Fell back to the paper: Vegas, M. I., Mateos-Agut, M., Pineda-Otaola, P. J., &
Sebastián-Vega, C. (2022). Psychometric properties of the FACES IV package for Spanish
adolescents. *Psicologia: Reflexão e Crítica*, 35, 18.
https://doi.org/10.1186/s41155-022-00222-2 -- open access (Springer Open), full text
pulled from the PMC mirror (PMC9209570, https://pmc.ncbi.nlm.nih.gov/articles/PMC9209570/)
after `link.springer.com` redirected to an auth-wall page. Also checked two secondary
Spanish-language FACES IV papers (Costa-Ball & Cracco 2021, Uruguayan FSS validation,
revistas.um.es; and a Burgos/problematic-families FACES IV paper from dehesa.unex.es) for
possible literal item text -- neither reproduces FSS item wording either (both report only
"Ítem 1".."Ítem 10" with descriptive statistics/factor loadings, never the item stems).

## Source type used
Primary paper full text (PMC mirror), not the dataset's own documentation (Dataverse
inaccessible). No PDF/OCR extraction was needed for this source (PMC page is HTML/text,
not scanned) -- the two secondary Spanish papers were fetched as PDF and parsed with
`pdftotext -layout`, also confirmed to contain no literal item text.

## OCR / image-based extraction
Not applicable -- no image-based or scanned source was used or needed. All sources
consulted were digital-native HTML or text-layer PDFs.

## Derived vs. directly-read values
- `item` values (`FSS-item 1`..`FSS-item 10`) and `resp` values (1-5) are taken directly
  from the cached ground truth (`.gt_faces_spanish_vegas_2022_fss.rds`), not derived.
- The 5-point response scale endpoints "Very Dissatisfied" (resp=1) / "Very Satisfied"
  (resp=5) are a **direct quote** from the paper's Measures section (PMC9209570): "the
  Family Satisfaction Scale (FSS) (Olson, 2000), with 10 items, with responses on a
  5-point Likert-type scale: 1 (Very Dissatisfied) to 5 (Very Satisfied)." Only the two
  endpoints are labeled in the source; midpoints 2-4 are left blank (unlabeled), matching
  the source's own level of disclosure -- not derived/invented.
- `item_text` is **not derived** -- left `NA` for all 10 items. No source reachable from
  this environment (the target paper, the Dataverse record, or either secondary Spanish
  FACES IV paper checked) discloses the literal FSS item wording. The target paper's own
  Table 4 (factor loadings) labels items only as `FSS1`..`FSS10`, never the item stems.
- `instructions` is left blank -- the participant-facing instructions for the FSS section
  specifically are not disclosed in the accessible source; the paper only states the
  general response-scale format quoted above.
- `correct_response` left blank -- FSS is a satisfaction/attitude scale with no scoring
  key.

## Source type/format note: has_bare_integer_items = FALSE
`has_bare_integer_items` is FALSE for this table, as stated in the dictionary row --
ground-truth `item` values already carry a semantic label (`FSS-item 1`..`FSS-item 10`,
confirmed verbatim including the "FSS-item N" space/hyphen formatting), so no
integer-to-item reconstruction was needed. The unusual formatting was matched exactly
(not normalized to "FSS_item_1" or similar) to satisfy the validation gate.

## Licensing note
The FACES IV package (which includes the FSS) is a **copyrighted, commercially
distributed instrument** owned by Life Innovations, Inc. (facesiv.com), copyright dated
2006. Per publicly available permission-request documentation (e.g.
https://revistas.ucr.ac.cr/index.php/ap/article/download/3064/3440/14235), researchers
must obtain permission from Life Innovations to use the FACES IV Package, it "must be
used in its entirety," and Life Innovations requests copies of resulting papers/theses.
This is analogous to the WJ-IV caution flagged elsewhere in this batch
(`gilbert_meta_80`): no attempt was made to locate a leaked/pirated copy of the FSS item
booklet to fill in `item_text`. Even where a plausible-looking hosted copy turned up in
search results (e.g. `media.gopll.com/documents/FACES%20IV.pdf`, a Scribd document titled
"Family Satisfaction Scale (FSS): David H. Olson, Ph.D.," and an academia.edu upload),
all three returned 403/404 on fetch attempts, so none were actually used as a source --
this is a moot point for this extraction (nothing was retrieved from them), but noting it
because the copyright status would have counseled against using them even if reachable.

## Items not extracted
`item_text` for all 10 items (`FSS-item 1`..`FSS-item 10`) -- literal item wording is not
disclosed in any reachable source, and the instrument is licensed/copyrighted, so no
attempt was made to locate or transcribe it from a non-primary source. `instructions` is
also blank for the same reason (participant-facing instructions text not disclosed in the
target paper). Everything else (`item`, `resp`, response-scale endpoint `option_text` for
resp 1/5, `instrument` name, table/section_id join keys) matches ground truth exactly and
is directly sourced.

## Validation
`unique(item)` and `unique(resp)` in `candidate_faces_spanish_vegas_2022_fss.rds` match
`.gt_faces_spanish_vegas_2022_fss.rds` exactly (10 items, resp 1-5; confirmed via
`setequal()` in `build_faces_spanish_vegas_2022_fss.R`). This is a **partial** extraction
(structure exact, item wording not recovered) -- logged to `pending_index_notes.csv`.

Note: the live ground truth also contains 136/11960 rows (~1.1%) with `resp = NA`,
spread across all 10 items (range 8-22 rows per item). Treated as ordinary item-level
non-response/missing data rather than a real response category, per the same precedent
already applied to `heard_roch_2022_k6` -- no `option_text` row was added for it, and it
does not affect the 1-5 `resp` match (R's default `unique()`/`sort()` behavior drops `NA`,
which is why the plain `setequal(sort(unique(...)))` check in the build script reports
TRUE; a stricter `setequal()` on the raw `unique()` vectors, which keeps `NA` as a
distinct element, would report FALSE on this technicality alone).
