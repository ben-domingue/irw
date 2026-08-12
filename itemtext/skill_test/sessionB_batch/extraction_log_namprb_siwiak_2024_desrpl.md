# Extraction log: namprb_siwiak_2024_desrpl

## has_bare_integer_items
Dictionary row marks this FALSE ("items already have semantic labels") — confirmed. Ground-truth
`item` values are `DES-R-PL_1`..`DES-R-PL_28` (literal hyphens preserved in the `item` column,
exactly as required), not bare integers requiring positional reconstruction.

## Source type used
Multiple sources, none of them the dictionary's own cited paper's full text directly:

1. **Dictionary reference** (Siwiak, Buczel, Rabińska, & Szpitalak, 2024, PsyArXiv preprint,
   doi:10.31234/osf.io/7u98d, "New Age of measuring paranormal and related beliefs: Psychometric
   properties and correlates of the Polish version of the Survey of Scientifically Unaccepted
   Beliefs (SSUB)") — this paper's own focal instrument is the SSUB, not DES-R-PL; DES-R-PL is
   evidently a correlate/validity measure administered in the same battery, per the task framing.
   No open full-text PDF of the preprint itself was fetched in this session (WebSearch budget was
   exhausted mid-session; the preprint's own text was not directly consulted for a description of
   DES-R-PL's role as a correlate).
2. **OSF project `osf.io/k2453`** (dictionary's "URL for data") — file listing fetched via the OSF
   v2 API (cached at `.cache/namprb_siwiak_2024_desrpl/osf_files.json`): 4 files
   (`data_SSUB-PL_adaptation.xlsx`, `irt_TRB.pdf`, `irt_NAB.pdf`,
   `Online_Supplement_translation_of_items_polish_SSUB_version.pdf`). No dedicated DES-R-PL
   materials/questionnaire file exists in this OSF project — the online supplement PDF covers only
   the SSUB's own item translations, not DES-R-PL.
3. **`data_SSUB-PL_adaptation.xlsx`** (downloaded, cached at
   `.cache/namprb_siwiak_2024_desrpl/data_SSUB-PL_adaptation.xlsx`) — raw data export. Its column
   headers confirm the exact item set: `DES-R-PL_1` .. `DES-R-PL_28` plus a `DES-R-PL_sum` column,
   matching ground truth exactly. No item-level text is present in the file (headers/values only).
4. **ESTD (European Society for Trauma and Dissociation) hosted PDF**
   (`https://estd.org/wp-content/uploads/2023/08/DissociativeExperiencesScale-Revised.pdf`,
   downloaded and cached at `.cache/namprb_siwiak_2024_desrpl/des_r_estd.pdf`, text extracted to
   `des_r_estd.txt`) — the open, freely-hosted **English-language "DES-R" (Dissociative
   Experiences Scale - Revised)** instrument itself: 28 items (Bernstein & Putnam, 1986 original
   item content), explicitly headed "The scoring system adapted by Pietkiewicz, Hełka, and
   Tomalski, 2018" — i.e. this is the direct English basis for the DES-R-PL Polish adaptation
   named in this table. It gives the literal instructions ("Choose the answer that shows how often
   this happens to you."), all 28 item stems in order, and the 8-point lettered response scale
   (a-h = Never / It has happened once or twice / No more than once a year / Once every few months
   / At least once a month / On average once a week / More than once a week / Once a day or more).
   The PDF itself cites: Pietkiewicz, I. J., Hełka, A. M., & Tomalski, R. (2019). Validity and
   reliability of the revised Polish online and pen-and-paper versions of the Dissociative
   Experiences Scale (DESR-PL). *European Journal of Trauma & Dissociation, 3*(4), 235-243.
   https://doi.org/10.1016/j.ejtd.2019.02.003 — the actual Polish-adaptation paper.
5. **Attempted but blocked**: the Polish-language DES-R-PL instrument document itself
   (ResearchGate `publication/327011780_Skala_doswiadczen_dysocjacyjnych_-_wersja_poprawiona_DESR_PL`,
   uploaded by Igor Pietkiewicz) — direct PDF link returned ResearchGate's login-wall HTML both via
   WebFetch and via `curl` with browser User-Agent/Referer headers (not a real PDF, "Temporarily
   Unavailable" / auth-gated). A Scribd mirror of the same document
   (`scribd.com/document/765916961/...`) returned a JS bot-challenge page ("Client Challenge") to
   both WebFetch and `curl`. A StudoCu mirror likewise did not expose document text to WebFetch.
   The Jagiellonian University institutional repository (RUJ) entry found in search results was an
   unrelated 2022 master's thesis with no downloadable PDF. WebSearch budget was exhausted before
   further mirrors/proxies could be tried.

## What "DES-R" turned out to mean
**DES-R = Dissociative Experiences Scale - Revised** (Bernstein & Putnam, 1986, for the original
item content; re-scored/re-anchored as an 8-point frequency scale by Pietkiewicz, Hełka, & Tomalski,
2018). **PL = the Polish adaptation (DES-R-PL)**, validated in Pietkiewicz, Hełka, & Tomalski (2019),
*European Journal of Trauma & Dissociation*. This is a general dissociation self-report measure, not
a bespoke instrument of the Siwiak et al. (2024) paper itself — it was evidently included as a
correlate/validity measure in the same survey battery as the paper's focal SSUB scale, consistent
with the task's "closely related sibling scale" framing. Confirmed NOT "Death Anxiety Scale" or any
paranormal-belief-specific instrument, despite the paper's paranormal-beliefs subject matter — DES-R
measures dissociative experiences (memory gaps, depersonalization, absorption, etc.), a construct
commonly studied alongside paranormal/anomalous belief as a correlate.

## Structure confirmed
- 28 items, ground-truth item codes `DES-R-PL_1`..`DES-R-PL_28` (literal hyphens), matching the
  `data_SSUB-PL_adaptation.xlsx` column headers exactly.
- 8-point response scale, ground-truth resp = {0,1,2,3,4,5,6,7} — matches the ESTD source's 8
  lettered options (a-h) exactly when mapped a=0 ... h=7 (standard additive DES-R scoring: sum of
  0-7 codes across 28 items, consistent with the cited scoring-system paper).
- No testlet/passage grouping — single `section_id` (`namprb_siwiak_2024_desrpl_1`) used for all
  28 items per the skill's "no grouping" convention.

## IMPORTANT language caveat (discrepancy)
**The study population and instrument administration were Polish** (DES-R-**PL**), but the only
literal, fully-recoverable item/option/instruction text found in this session is the **English**
DES-R source (ESTD PDF) that the Polish version is a direct, faithful translation of (per the
Pietkiewicz et al. 2018/2019 scoring-and-validation papers, which describe DES-R-PL as a translated
adaptation of this same 28-item, 8-point instrument, not a modified/re-authored one). The actual
literal Polish wording administered to Siwiak et al.'s (2024) participants was **not** recovered —
every source found hosting the Polish-language document (ResearchGate, Scribd, StudoCu) was
access-blocked in this environment. `item_text`, `instructions`, and `option_text` in the candidate
output are therefore populated with the **English DES-R source text**, not verified literal Polish
text as administered. This is flagged, not silently substituted — see `pending_index_notes.csv`.

## Ambiguities / not independently confirmed
- The item-order correspondence (`DES-R-PL_1` = ESTD item 1 "driving a car...", etc.) assumes the
  Polish adaptation preserved the original DES-R's 1-28 item order and numbering — a standard,
  low-risk assumption for a direct translation/adaptation paper (no evidence found of item
  reordering or omission; 28 items in both sources, exact count match), but not independently
  verified against the Polish paper's own item table (paywalled/blocked, see above).
- `correct_response` is blank for all items — DES-R-PL is a self-report frequency scale with no
  correct/incorrect answer key.

## Items not extracted
None dropped — all 28 ground-truth items extracted with full 8-option resp structure.
Validated: `unique(item)` and `unique(resp)` match `readRDS(".gt_namprb_siwiak_2024_desrpl.rds")`
exactly (28 items, resp {0..7}). The open discrepancy is the item/option/instruction **text's
language** (English source text standing in for unrecovered literal Polish), not item/resp
coverage.
