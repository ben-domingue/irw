# NEEDS_HUMAN sample (irw#2382 step 2, 2026-09-25)

The pool is every NEEDS_HUMAN row: 206 in `triage_results.csv` (waves 1-4 plus the step 1 redo) and 25 in
`pilot_results.csv`, 231 tables in about 100 deposits. Rows were tagged by why the agent stalled, using keywords in
`evidence`, which is rough. 35 deposits were then read by hand across the tags. That is more than the planned ~20, so that every question has a concrete case.

| stall tag | tables | deposits |
|---|---:|---:|
| rights judgment (wording in hand) | 101 | 38 |
| access (page 403, bot wall, file would not open) | 44 | 27 |
| identity / mapping | 38 | 27 |
| other (mostly rights, worded differently) | 22 | 12 |
| PsycTESTS hold | 14 | 9 |
| what counts as item text | 12 | 11 |

## What the sample shows

- **Much of the rights group is already decided.** Many of these rows were written before the register had the
  rows Ben ruled on 09-19 to 09-25 (HADS, DAS/MHS, BDI/Pearson, UCLA, RES, AUDIT/SRQ). Applying those rows is
  mechanical.
- **Most access stalls are mechanical.** Web search was out of budget for part of wave 4. Also, WebFetch on
  `zenodo.org/api/records/<id>/files/<key>/content` now retrieves Zenodo binaries.
- **PsycTESTS holds stay parked** (the 09-23 rule; no PsycNET reader). They are not questions.
- **The rest needs rulings**, and they group into the 11 questions below.

## The sample

| table (deposit size) | tag | outcome |
|---|---|---|
| reinwarth_2023_psych_symptoms | access | mechanical: register HADS/GL Assessment `block` -> RIGHTS_BLOCK |
| burns_2018_das4_father (2) | access | mechanical: register MHS row names DAS-4 -> RIGHTS_BLOCK |
| kumlander_2018_bdi | access | mechanical: Pearson BDI row; adaptations inherit -> RIGHTS_BLOCK |
| uti_newlands_2023_uclals (3) | access | mechanical: register UCLA-L `ship` (Ben 09-20) -> OBTAINABLE |
| tatala_2023_religious_experience, tatala_2023_ucla_loneliness | rights | mechanical: register RES / UCLA-L `ship` -> OBTAINABLE |
| narcissism_schneider_2025_study2_audit | access | mechanical: register AUDIT `ship_with_note` -> OBTAINABLE |
| kinyanjui_2023_substance_use | rights | mechanical: same WHO clause already extended from AUDIT to SRQ -> ship_with_note (flag at ratification) |
| hannachi_2025_eco_anxiety_affect | rights | mechanical: originators' own CC BY-NC-SA; NC is a hard stop -> RIGHTS_BLOCK |
| dejesus_2017_gpm | rights | mechanical: Portuguese wording first published CC BY-NC -> RIGHTS_BLOCK |
| nonverbal_immediacy | rights | mechanical: McCroskey's "research or instructional purposes" grant is the FPS-2 shape -> block the NIS items. The TIPI items are separate. |
| trang_2023_vocabulary_beliefs (2) | rights | mechanical: first publication is CC BY; a later NC-ND repository copy doesn't govern -> OBTAINABLE |
| abdullah_2024_hbbloat_attitude (2) | access | mechanical: MDPI s1 via Europe PMC or WebFetch; note 4 PBC codes vs n_items 3 |
| goksel_2026_embarrassment_affectivetrust (2), goldberg_2018_sdv_likelihood, kay_2025_antonyms | access | mechanical: origin search died on the search budget; rerun |
| schoen_2021_bmtl_fip | identity | mechanical: map 5a..5g via the other B-MTL tables' codes |
| chile_2024_safety_aggression (42) | rights | **ruling Q1** |
| rating_speed_2025, emoji_scheffler_2024 | what counts | **ruling Q2** |
| KanjiOAHaS_Inoue_2024, mclaughlin_samuel_2025_auditory_session_2 | what counts | **ruling Q3** |
| sirventruiz_2025_pdat, erguvan_2022_questionnaire | what counts | **ruling Q4** |
| west_2022_psychnet_pclsv, dscore_battelle_weber_2019 (6) | what counts / rights | **ruling Q5** |
| pisa2003_math (4) | access / rights | **ruling Q6** |
| idemudia_2025_s101 | identity | **ruling Q7** |
| redline_2026_prosbq, duong_2025_tbl_confidence (2) | rights | **ruling Q8** |
| baquerotomas_2026_pil (2), yao_2020_epq | rights | **ruling Q9** |
| kolomiets_2026_career_match, test_taking_much_2025_ao | rights | **ruling Q10** |
| silk_2019_hyperactive (2) | rights | **ruling Q11** |

## Ruling questions for Ben

1. **ShareAlike.** Does CC BY-SA on the wording (INE Chile's question dictionary, 42 tables) ship with attribution,
   or count as a reserved right?
2. **Rating prompts.** When the stimulus is on `id` and the items are rating dimensions ("How familiar is the emoji..."),
   is the rating prompt the item text?
3. **Per-item stimuli.** Is a performance item's target (the kanji to write, the sentence to transcribe) item text?
4. **Partial coverage.** What share of a table's items must be worded to ship? For example, 13 of 26, or 23 of 25 with
   2 left blank.
5. **Short titles.** Do short item titles or descriptors count as item text? For example, the PCL:SV's "Grandiose",
   or D-score's one-line labels for a commercial test (Battelle).
6. **OECD released items.** Which governs the PISA released items: the 2009 book's reserved public/commercial-use
   clause, or the current OECD site terms? Only the released subset is public in any case.
7. **Inferred instrument.** Is an instrument inferred from composite columns and item count, never named by the
   source (MSPSS from S/F/SO composites), enough to attach canonical wording?
8. **Third-party permission lines.** Does a third party's statement that permission is needed block? Examples: a
   summary site's "permission must be attained", or a study's "authorized for use by the original authors". Or only
   the originator's own terms?
9. **Commercial, no stated terms.** A test sold by a publisher whose page states no terms (Psychometric Affiliates PIL,
   EdITS EPQ-R, Polish PTP manuals): silence, or hold?
10. **Deliberate withholding.** When the originator says the wording is not distributed (kolomiets: "Item wording is
    not distributed"; Much 2025: "cannot be republished due to copyright"), is that a reserved right, even with no
    licence clause?
11. **DSM criterion text.** DSM-IV ADHD criteria printed verbatim in a CC BY paper: does APA's DSM reservation block?

## Leads seen (not acted on)

- yu_2015_family_environment holds BDI items. It is a pilot lead in #2255, and possibly `wrong-now`, because the codes
  mean different questions than the name says.
- kokoszka_2022_soc is the Body Esteem Scale, but the script calls it Sense of Coherence.
- najari_2024 s1-s21 are the DASS-21.
- robison_2026_retesting_* has no biblio row and no processing script.
- From step 1:
  - fadhliah_2022 reads only 1 of 3 sheets (75 of 200 respondents);
  - zhu_2024_pyd dropped B1-B3 as "theta scores";
  - tims_2017 has 4 items where the paper has 3;
  - mbps_vangsness_2019 drops item 11 (a misspelled column);
  - rvobgvmaas has 27 codes for the 19-item MAAS;
  - li_2026 has 223 rows where the deposit's table reports N=323;
  - Hakim Study 2's public .sav carries `Nama`/`Email` columns (IRW drops them).
- The register's MEQ30 `block` row is a name-match trap for the Morningness-Eveningness Questionnaire (MEQ).

## Rulings (Ben, 2026-09-25)

Where the rules page ("IRW item-text licensing rules", 12 rules) already answers a question, that answer is used. Ben:
"rely on that for the moment to the extent we can". Questions still open go to counsel.

| Q | Ruling | What it does to the verdicts |
|---|---|---|
| 1 ShareAlike | **open, being researched**; may go to counsel. Rule 8 (restrictions travel downstream via `Derived_License`) is the candidate route. | chile_2024_safety (42) stays NEEDS_HUMAN |
| 2 rating prompts | The stimulus (word, emoji) probably has to be part of the item text too. That is a format change, not a rights call. | stays NEEDS_HUMAN, tagged `design:stimulus-on-id`; not queued |
| 3 per-item targets | A target the respondent produces, scored against a rubric (kanji to write, sentence to transcribe), is the answer key, not item text. It may belong in the nominal branch. | NOT_ITEM_TEXT, unless the prompt itself is published |
| 4 partial coverage | Ship if **more than half** of the items are worded, with the rest blank. | 13/26 = exactly half: no; 23/25: yes; cbq 50/64: yes if rights clear |
| 5 short titles | **No.** | NOT_PUBLISHED |
| 6 PISA | **Skip.** Be careful with PISA. | `excluded` (reason: PISA skipped by ruling) |
| 7 inferred instrument | **Yes, but verify** (e.g. p-values match what the canonical items predict) and file an issue for each one. | OBTAINABLE after the check passes, plus an issue |
| 8 third-party permission lines | Ben wants examples. Rules page **rule 10** (secondhand evidence of a refusal blocks) and **rule 12** (when in doubt, don't host) cover it for now. | RIGHTS_BLOCK |
| 9 commercial, no terms | **Hold.** | NEEDS_HUMAN, tagged `hold:commercial` |
| 10 deliberate withholding | **Block.** | RIGHTS_BLOCK |
| 11 DSM criteria | Investigate. Rules **1 and 4** cover it now: APA reserves reproduction, and a CC BY reprint doesn't launder it. | RIGHTS_BLOCK unless research says otherwise |
