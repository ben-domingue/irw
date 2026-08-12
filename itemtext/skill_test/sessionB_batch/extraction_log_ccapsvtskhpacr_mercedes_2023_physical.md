# Extraction log: ccapsvtskhpacr_mercedes_2023_physical

## Source used
Dictionary URL `https://osf.io/8t4fp/` is the OSF project for Coello-Cremades et al.
(2024), "The Spanish adaptation of the Tampa Scale for Kinesiophobia Heart: psychometric
evidence in cardiac rehabilitation patients" (Eur J Phys Rehabil Med 60(4):691), DOI
10.23736/S1973-9087.24.08268-6. The paper is open access on PMC:
https://pmc.ncbi.nlm.nih.gov/articles/PMC11403632/ (fetched for Table I text). The OSF
project's `Data/` folder contains the actual raw SPSS file `TSK_ES_231202.sav`
(N=194 rows, 119 variables), which was downloaded and read with R `haven::read_sav()` —
cached at `.cache/ccapsvtskhpacr_mercedes_2023_physical/TSK_ES_231202.sav` (also
`var_labels.csv`, a dump of each variable's SPSS variable label + value labels + N
counts for the 30 target variables, generated for this extraction).

## Source type used
Raw SPSS data file (`.sav`) with embedded variable labels and value labels — not a
published codebook/appendix and not the paper's prose. This is the most literal
available source: SPSS variable labels (e.g. `af` -> "Atrial Fibrillation") and value
labels (e.g. `0` -> "No", `1` -> "Ablation") are transcribed directly from the file's
metadata via `haven::read_sav()`, cross-checked against the frequencies printed in the
paper's Table I ("Baseline characteristics") for the ~24 of 30 variables whose row also
appears in that published table.

## Critical finding: naming mismatch (table name vs. actual items)
This table's name (`...tskhpacr...`, "TSK" = Tampa Scale for Kinesiophobia) and the
dictionary's Reference field both point to a psychometric fear-of-movement instrument
(the TSK-SPA, 17 self-report Likert items). **The 30 items actually present in the live
IRW data are NOT TSK items.** They are binary (0/1) presence/absence flags for cardiac
diagnoses, procedures, and comorbidities — i.e., a "Table 1"-style baseline patient
characteristics / medical history checklist from the same study's participant sample,
not the kinesiophobia scale itself.

This was confirmed conclusively, not just inferred:
- The paper's own Table I ("Baseline characteristics") lists diagnosis/procedure/
  comorbidity rows (STEMI, Non-STEMI, unstable/stable angina, atrial fibrillation,
  valvular disease, ventricular aneurysm, PCI, CABG, pacemaker, valve procedure,
  ablation, CAD non-revascularized, hypertension, diabetes, ex-smoker, sedentarism,
  hypercholesterolemia, alcoholism, obesity, family history, musculoskeletal disorder,
  oncological disease, rheumatic disease, COPD, OSAS, COVID, stroke, LVEF preserved/
  non-preserved) whose category counts (N=194 total) match the ground-truth `item`/`resp`
  cross-tab exactly for every one of the 30 items (e.g. `disli` 95/99, `hta` 88/106,
  `pci` 23/171, `lvef` 40/154 — verified against `table(gt$item, gt$resp)`).
- The raw `.sav` file's own variable labels for these 30 variables (`af`="Atrial
  Fibrillation", `cabg`="Coronary Artery Bypass Grafting", `pci`="Percutaneous Coronary
  Intervention", `lvef`="Preserved or not prevserved [sic]", etc.) are unambiguous
  clinical/demographic flags, not kinesiophobia-scale item stems.
- The same `.sav` file separately contains the actual TSK-17 instrument as variables
  `tsk1`-`tsk17` (with literal Spanish item text, e.g. `tsk1` = "Me da miedo dañarme si
  hago actividad física/ejercicio físico.") plus a 7-day retest block (`tsk1d7`-
  `tsk17d7`). These are a completely separate set of variables from the 30 in this
  table, confirming the TSK items exist in the source but were not what got loaded into
  `ccapsvtskhpacr_mercedes_2023_physical` — some other IRW table (not this one) likely
  corresponds to the real TSK-17 scale, or that scale hasn't been separately ingested.

Recorded this in the `instrument` field of every output row rather than force-fitting a
kinesiophobia narrative onto these items.

## Structure discovered
30 binary variables, each coded 0="No <condition>" / 1=condition present, matching the
ground truth's `resp` values {0,1} exactly. No shared testlet/passage grouping applies
(these are independent chart-review/intake variables, not a scale with item ordering or
subscales), so a single trivial `section_id` (`ccapsvtskhpacr_mercedes_2023_physical_1`)
is used for all 30 items with blank `section_prompt`, per the skill's rule for
instruments with no real grouping.

`has_bare_integer_items` is FALSE for this table — confirmed: `item` values are semantic
codes (`af`, `pci`, `stroke`, etc.) taken directly from the ground truth and cross-walked
1:1 onto the raw data's own SPSS variable names (same strings), not reconstructed from
position/order the way bare-integer items would require.

## `instructions` field
Left blank (`NA`). This is not a self-report instrument administered to participants
with standard instructions text — it is a clinician/chart-derived set of baseline
characteristics — so there is no literal "instructions" text in the source to transcribe.
Inventing generic framing language (e.g. "Indicate whether the patient has...") would
violate the no-fabrication rule, so the field is left blank rather than guessed.

## `item_text` source per item
For 22 of 30 items, `item_text` is the literal SPSS variable label from the `.sav` file
(e.g. `pci` -> "Percutaneous Coronary Intervention", `apnea` -> "Obstructive Sleep Apnea
Syndrome"). For 8 items whose SPSS variable label was unset/uninformative (`ablation`,
`alcohol`, `covid`, `diabetes`, `hta`, `obesity`, `stroke`, `valve`), `item_text` instead
uses the corresponding row label from the paper's published Table I (e.g. `hta` ->
"Hypertension", `alcohol` -> "Alcoholism") — still a literal transcription from a source
document, just the paper rather than the raw file's metadata for those 8.

## `option_text` source
Literal SPSS value labels: resp=0 always labeled "No" (or "no" for `hta`) in the source
file; resp=1 labeled with the source's own value-label text (e.g. `af` resp=1 ->
"Atrial Fibrilation" [sic, source's spelling retained], `disli` resp=1 ->
"Hyperlipidemia"). Not rewritten or corrected for spelling/typos — transcribed as-is,
including the source's own inconsistencies noted below.

## OCR / image-based extraction
None. All text was extracted programmatically from machine-readable sources: the PMC
open-access HTML article (Table I) and the SPSS `.sav` file's embedded metadata via
`haven::read_sav()`. No OCR, image transcription, or PDF text-layer extraction was
required or used.

## Derived vs. directly-read values
All `item_text` and `option_text` values are directly read from source metadata/text —
none are derived/computed (e.g. no arithmetic, no reverse-scoring, no recoding). The
`resp` values (0/1) are the raw values already in the live IRW data, used as-is; no
transformation applied. One minor exception worth flagging as "derived by
cross-reference" rather than directly read: for the 8 items lacking an SPSS variable
label, `item_text` was derived by matching that variable's N=194 case counts against the
paper's Table I row with the identical N split, then using that row's stated label —
i.e., inferred via a unique-count match, not read directly off the variable itself. This
match was unambiguous in all 8 cases (exact N tie to a single Table I row each).

## Ambiguities / discrepancies noted (not silently resolved)
- **`disli` vs. `hychol` naming inconsistency in the source itself**: the `.sav` file has
  two separate variables that both relate to cholesterol/lipids — `disli` (SPSS label
  "dislipemia", N=95/99) and `hychol` (SPSS label "Hypercholesterolaemia", N=190/4). The
  paper's Table I lists only one row, "Hypercholesterolemia 99 (51%)", which numerically
  matches `disli`, not `hychol`. This means the paper's published label
  ("Hypercholesterolemia") was applied to what the raw data calls `disli`
  (dyslipidemia/hyperlipidemia), while the data's own variable literally labeled
  "Hypercholesterolaemia" (`hychol`) is a much rarer, seemingly distinct condition (4/194,
  not reported in the paper's table at all). Retained each variable's own SPSS label
  rather than reconciling them, since collapsing them would misrepresent two genuinely
  different columns in the source data as one.
- **`vent` naming**: SPSS label is "Aortic Aneurism"; the paper's Table I row with the
  matching N (8/194) is labeled "Ventricular aneurism." Used the SPSS label as primary
  (`item_text` = "Aortic Aneurism") since it's the more literal/direct source, and note
  the paper's wording differs.
- **`lvef` SPSS label has a typo** ("Preserved or not prevserved") — transcribed
  verbatim rather than silently correcting it.
- **`option_text` spelling inconsistencies** in the source's own value labels (e.g.
  "Atrial Fibrilation", "AAortic Aneurism", "Tabaquism" for ex-smoker=1, "Peacemaker" for
  pacemaker=1) were kept as-is rather than corrected, per literal-transcription practice.

## Items not extracted
None — all 30 ground-truth items were matched and extracted; validated exact `item`/
`resp` set match against the cached ground truth
(`.gt_ccapsvtskhpacr_mercedes_2023_physical.rds`): `setequal(unique(gt$item),
unique(cand$item))` and `setequal(unique(gt$resp), unique(cand$resp))` both TRUE, and
every item's per-`resp` N in the ground truth matches the raw `.sav` file's frequency
table exactly (spot-checked all 30 items, not just a sample).

## Naming-mismatch discrepancy to log
Logged to `pending_index_notes.csv`: this table is misleadingly named/referenced as if
it were the TSK-17 kinesiophobia scale but actually contains a baseline comorbidity
checklist; flagging for whoever maintains the index sheet in case a companion table
(the real TSK-17 items) exists elsewhere in IRW and should be cross-linked, or in case
the table's origin/description metadata needs a correction note.
