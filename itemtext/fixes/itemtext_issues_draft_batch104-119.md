# itemtext_issues.qmd additions — batches 104–119 (2026-09-09 rounds)

Hand-selected from `draft_issues_qmd.R` output, then rewritten against each table's full
`note`, not the templated `public_note`. **29 entries**, validated: inserting the block below
before the closing `)---")` in `irw_site/itemtext_issues.qmd` takes the page from 423 to 452
entries, parses under `yaml.safe_load`, and duplicates no existing `table:` key.

**NOT YET APPLIED.** Entries go on the page only once the tables are uploaded, and these 56
tables are staged in `itemtables/clean/` awaiting Ben's `red_up` run. Committed here so the
wording is not lost in the meantime — `draft_issues_qmd.R` overwrites
`fixes/itemtext_issues_draft.md` rather than appending, which has destroyed pending entries
twice.

## DO NOT APPLY — held or blocked, these tables ship no wording

- `moe2025_scs` — held from upload pending irw#2146 (item SCS25_pre's responses look like the
  wrong column). It has a `public_note` and so will keep drafting; do not apply it until the
  data question is resolved and the table ships.
- `ngo_2025_green_pbc` — held: NO_ROUTE verification with an empty `public_note`, while its two
  sibling tables disclose the same print-order assumption. Write its note, then it can ship
  with an entry like theirs.
- `mohamed_2024_ppos`, `molino_2018_d6_scale`, `mq_supremecourt`, `muharam_2022_srq29` —
  blocked on rights at extraction. No CSV was written; an entry would tell readers IRW ships
  wording it does not.

## Considered and left off, by the bar the page actually practises

The bar is "the shipped text is not the wording respondents read". "The source never published
the options / the key / the instructions" is below it — of 423 live entries, 52 are the former
shape and 1 is an order assumption.

- Order-assumption only (`mapping_basis=paper_order`, study's own materials): the five
  `ngo_2025_green_*`, the four `nas_rogoza_2024_study2/5_*`, `metacogmonitoring_double2025`.
- Blank by design, source published nothing to ship: `mturkddm_y25`,
  `mindfulness_assessment`, `neurodegenerative_huizinga_2019_svc`.
- Table composition rather than wording: `MGSISGCLQ_Hollyhead_2018`, `molino_2018_d5_scale`,
  `muller_2016_dog_inhibition` (the last two also contradict their IRW dictionary
  Description — that is a dictionary fix, not an item-text entry).
- Verification ties and data missingness: `nakano_2020_osce_contact_precautions`,
  `muir_2025_resilience_behaviours`, `mpsycho_avlancheprep`, `mturkddm_recognition`.

Two entries below are hand-written because the table carries no `public_note` at all — the
drafter is blind to those (`niazi_2020_mfq`, `narcissistic_personality_inventory`).

## The block

```yaml
- table: meloni_2015_parent_divers_ed
  issue: |-
    The questionnaire was administered in Italian and neither the article nor its supplements
    publish any Italian wording, so the item text shown here is the English given in the study's
    own S2 File codebook. Each of the five sections corresponds to a photograph shown to the
    parent -- a person with a physical disability, a person with Down's syndrome, a boatload of
    migrants, two gay men kissing, a pelican covered in oil -- and section_prompt holds the
    study's own description of that image, not a caption respondents read; the twelve statements
    were repeated in randomised order under every image.
- table: meloni_2015_parent_interests
  issue: |-
    The questionnaire was administered in Italian to Italian parents, but neither the PLOS ONE
    article nor its two supporting files publish any Italian wording, so the item text shown here
    is the authors' own English from the S2 File codebook rather than what the parents read; the
    codebook lists the 25 statements as one unnumbered roman-numbered run tied to no variable
    code, so the order of the items within each conceptual block (music, religious, sport,
    cultural, social) is inferred from that list order. The response labels are also partly IRW's:
    the codebook says only 'Scale: Important/Not Important from 1 to 5' and never labels a scale
    point, so 'Not Important' is shown at 1 and 'Important' at 5 - a placement supported by the
    data (reading books averages 4.46 and watching sport on television 1.96) - and points 2 to 4
    are deliberately left blank.
- table: menaldi_2023_brief_cope
  issue: |-
    The English in option_text_translated was written by IRW: the study administered its own
    Indonesian frequency anchors (Tidak pernah / Kadang-kadang / Cukup sering / Sangat sering)
    rather than the Brief COPE's published anchors, so no authors' English exists for them.
    item_text_translated is Carver's original English for the correspondingly numbered item, a
    parallel version rather than a translation of the Indonesian wording.
- table: mendes_2019_snycq
  issue: |-
    The Short-NYC-Q was administered at MPI-CBS Leipzig to native German speakers, but no German
    wording is published in the deposit or the paper, so the item text shown here is the English
    wording from the deposit's own SNYCQ.json data dictionary; responses are a continuous 0-100
    visual-analogue scale, so only the two endpoints carry option text
- table: meng_2017_referent_assignment
  issue: |-
    Item codes EQ and EQ2 each cover two literal wordings under the study's counterbalanced design
    -- the name question in name-first (NC) trials and the color question in color-first (CN)
    trials (the trial's order is in cov_pattern) -- so both are given in item_text with the
    condition named in brackets; AQ, AQ2 and AQ3 share one identical question ("What about this?")
    and are distinguished only by their position in the fixed EQ/AQ/EQ2/AQ2/AQ3 sequence, not by
    wording.
- table: merlo2025_eet
  issue: |-
    The questionnaire was administered in Italian; item_text and instructions are the administered
    Italian verbatim from the deposit's own data dictionary, and the English in the *_translated
    columns was produced by IRW rather than by the authors. The Italian response anchors were
    never published, so option_text instead carries the authors' English
    (never/rarely/sometimes/often/almost always/always, coded 1-6) taken from the paper; the
    direction is confirmed by the questionnaire's own attention-check item EET_17, whose wording
    is "Seleziona la risposta Mai" and which 1034 of 1065 respondents answered with resp = 1. Note
    that EET_17 is that attention check and not a food, so it should be dropped from any diet
    score pooling the other 28 items.
- table: merlo2025_eng_cognitive
  issue: |-
    The questionnaire was administered in Italian; item_text and instructions are the administered
    Italian verbatim from the deposit's own data dictionary, and the English in the *_translated
    columns was produced by IRW rather than by the authors. The Italian response anchors were
    never published, so option_text instead carries the authors' English for the two ends of the
    scale only - Never at resp = 1 and Always at resp = 7, per Merlo et al. sec. 3.2.6 and Mameli
    & Passini (2017) - and the five interior scale points are left blank because no source labels
    them. The direction is confirmed numerically: rebuilding the paper's own ENG_C composite from
    the live data gives mean 4.229 and skew -0.318 against a published 4.229 and -0.317, where the
    reversed coding would give 3.771 and +0.318. Note also that the deposit's data dictionary has
    had its commas and colons flattened to spaces by its exporter, and the shipped Italian
    reproduces it as-is without restoring punctuation.
- table: merlo2025_eng_emotional
  issue: |-
    The questionnaire was administered in Italian; item_text and instructions are the administered
    Italian verbatim from the deposit's own data dictionary, and the English in the *_translated
    columns was produced by IRW rather than by the authors. The Italian response anchors were
    never published, so option_text instead carries the English coding stated in the paper (1 =
    completely disagree to 7 = totally agree) with the five interior points left blank because the
    source labels only the two ends. One item is stored reverse-scored: ENG_EMO_09 ("Penso che
    studiare sia noioso" / "I think studying is boring") correlates +0.21 to +0.39 with all eight
    positively worded items and Cronbach alpha is 0.890 as stored against 0.820 with it flipped,
    so for that item alone resp 7 means "completely disagree" and resp 1 means "totally agree"; do
    not reverse it again before scoring.
- table: mhscdc_fried_2020_ema
  issue: |-
    This EMA table carries TWO different 1-5 response ladders and nothing in the resp values
    distinguishes them: Q1-Q10 are momentary affect items scored 1 'Not at all' to 5 'Extremely',
    while Q11-Q18 are duration items scored 1 '0 min', 2 '1 - 15 min', 3 '15 - 60 min', 4 '1 - 2
    hours', 5 '> 2 hours'. Do not read one common scale across the table. Item wording is
    transcribed from the deposit's administered survey form (Measures_EMA.pdf), which differs in
    several places from the paraphrased Item column of Codebook_EMA.xlsx.
- table: mistry_2022_hardship
  issue: |-
    For mistry_2022_hardship the option_text values are the labels of the collapsed binary recode
    the deposit ships ('No difficulty'/'Some difficulty'), not the response options respondents
    were offered, which for the food, medicine and routine-care items were None/some/much/unable
    or very difficult; and the item_text for memory and difficulty_earning is cut off mid-phrase
    because the source Stata variable labels hit Stata's 80-character cap
- table: mobility
  issue: |-
    The item wording for this table is the English text documented in the ltm R package, not the
    Bengali in which the Bangladesh Fertility Survey 1989 was administered to rural Bangladeshi
    women; no Bengali original is published in the source, and the instructions field is the
    documentation's description of what respondents were asked rather than a verbatim administered
    instruction.
- table: moe2025_erq
  issue: |-
    The ERQ was administered to Italian teachers, but the figshare deposit is a single SPSS file
    with no item wording in any language and no accompanying article or supplement could be
    located, so the item text shown here is Gross & John's (2003) canonical English ERQ rather
    than the Italian sentences the teachers read. Item codes ERQ1_pre-ERQ10_pre are matched to the
    instrument's own printed item numbers; the assignment of reappraisal versus suppression
    wording is confirmed by the deposit's own Reappraisal composite, which is the mean of exactly
    ERQ1/3/5/7/8/10 (the unique such six-item subset of 210, next-best deviation 0.83), but
    nothing in the data distinguishes the near-parallel reappraisal items 1, 3, 7 and 10 from one
    another. Scale points 2, 3, 5 and 6 carry no option text because the ERQ form labels only 1, 4
    and 7.
- table: mohammed_2021_patient_safety_culture
  issue: |-
    The only item wording this study ever published is the variable labels inside its SPSS data
    file, and those labels are truncated: they stop at 70 characters (so some items lose their
    final words) and they are also cut at the start, so many begin with a word fragment such as
    'fied.' or '. '. They are shipped exactly as the file stores them rather than repaired,
    because this administration is not the canonical AHRQ HSOPSC: 18 items are negated rewrites of
    AHRQ's reverse-worded items, and the responses run in the labels' direction (all 18 correlate
    +0.13 to +0.55 with the other items rather than negatively), so substituting the standard
    wording would have inverted them.
- table: monier_2026_pot
  issue: |-
    Item text for this table is the study authors' English rendering; the questions were
    administered in French, and no French original is published in the paper or its S1 Table, so
    the administered wording could not be shipped.
- table: monier_2026_sti
  issue: |-
    Item text for this table is the English wording printed in the study's own Table 6; the
    inventory was administered in French, and no full French original is published in the paper or
    its S1 Table, so the administered wording could not be shipped. The paper never states the
    7-point response anchors, so option text is blank.
- table: morales_2021_erq
  issue: |-
    The ERQ was administered in Spanish (the Cabello et al., 2013 adaptation) to a mostly Chilean
    sample, but neither the PeerJ deposit nor the paper's supplement contains any Spanish item
    wording -- the deposit's ERQ columns are bare codes ERQ_1..ERQ_10 -- so the item text shown
    here is Gross and John's (2003) canonical English ERQ rather than the sentences participants
    read. Item codes erq1-erq10 follow the instrument's printed item numbers; the split into
    reappraisal (erq1, 3, 5, 7, 8, 10) and suppression (erq2, 4, 6, 9) wording is confirmed by the
    paper's Table S.5, whose twelve published subscale statistics reproduce exactly under that key
    and under no other of the 210 possible six-item splits, but nothing in the data distinguishes
    the near-parallel reappraisal items 1, 3, 7 and 10 from one another. Scale points 2, 3, 5 and
    6 carry no option text because the ERQ form labels only 1, 4 and 7.
- table: motion
  issue: |-
    The items of `motion` are stimulus conditions in a random-dot motion task, not questions: each
    item code is block number and motion coherence (e.g. '1 6' = block 1, 6% coherence), and the
    item_text IRW ships is a description of that stimulus rather than wording the child read. The
    only verbatim on-screen text is in the instructions field. resp is scored accuracy (1 =
    correct direction judgement), not the left/right key the child pressed.
- table: much_tte_2025_matrixreasoning
  issue: |-
    The speed/accuracy block instruction was counterbalanced across participants (Group 1 saw the
    non-speeded framing first, Group 2 the speeded), so the instructions field reproduces both
    verbatim rather than the one wording any single respondent read; item_text is blank because
    the OMIB matrix stimuli are figures, not text.
- table: muslih_2024_rses
  issue: |-
    The item text shipped for this table is the English wording the paper prints in its Table 2;
    the scale was administered to participants in Indonesian, and no Indonesian wording is
    published in the paper or its S1 Dataset.
- table: najari_2024_bpqsf_awareness
  issue: |-
    This table is named for the BPQ-SF's Body Awareness subscale but actually contains the whole
    46-item BPQ-SF: q1-q26 are Body Awareness, q27-q40 Supradiaphragmatic Reactivity and q41-q46
    Subdiaphragmatic Reactivity, per Table 2 of the source paper.
- table: nam_2024_function
  issue: |-
    The survey was administered online in Korean and neither the article nor its S1 Data
    supplement publishes any Korean wording, so the item text shown here is the Washington Group's
    own canonical English WG-SS wording; the assignment of FL1-FL6 to the six domains follows the
    canonical WG-SS order that the paper's Methods reproduces, and the data confirm the mobility
    and self-care items (FL3, FL5) and the seeing/hearing pair (FL1, FL2) but cannot tell seeing
    from hearing.
- table: narcissistic_personality_inventory
  issue: |-
    This is the forced-choice NPI-40, so `item_text` is blank for all 40 items by design and both
    statements of each pair are carried as `option_text` at resp 1 and 2. The 80 statements are
    the 2014 deposit's own codebook wording. The `instructions` line, however, was transcribed
    from the live openpsychometrics NPI form as it stood in 2026, because the deposit's codebook
    only describes how the test was administered rather than quoting the instruction respondents
    read; the 80 item statements on that live form are byte-identical to the 2014 codebook, so it
    is the same instrument, but the instruction wording itself is current-page evidence for a 2014
    administration.
- table: neurodegenerative_huizinga_2019_dass
  issue: |-
    The study does not say which Dutch DASS-21 translation it administered, and two are
    distributed that differ in items 1-3; IRW ships the 2010 revised de Beurs version, chosen
    because DASS.1 behaves as a stress item (corrected r .618 stress vs .448 anxiety, where the
    2001 form's item 1 loads equally on both) and DASS.2 behaves as the dry-mouth item (weakest
    item in the scale, r .329, yet the most endorsed anxiety item at mean .502) rather than the
    2001 form's sweating item; the instructions are the paper form's and mention circling a
    number, though this battery was administered online
- table: neurodegenerative_huizinga_2019_vfq
  issue: |-
    Item text is the NEI VFQ-25's official ENGLISH wording; the study administered the
    questionnaire in Dutch and neither the paper's appendices nor the DataverseNL deposit publish
    the Dutch form, so this is a same-instrument substitute rather than what respondents read.
    Note also that resp is the RAND-converted 0-100 item score rescaled (higher = better vision-
    related functioning), not the response number printed on the questionnaire, so for items 1-14,
    15c, 16 and 16a the option order is the reverse of the printed one.
- table: ni_2025_open_innovation
  issue: |-
    The item text shipped for this table is the English wording the source paper prints in its
    Methods; the questionnaire was administered to participants in Chinese, and no Chinese wording
    is published in the paper or its S1 Data. The order of items within each of the two blocks
    (OI1-1..OI1-4 and OI2-1..OI2-4) is inferred from the paper's presentation order rather than
    from an explicit item-code label.
- table: ni_2025_strategic_orientation
  issue: |-
    The questionnaire was administered in Chinese to managers of Chinese SMEs, but neither the
    article nor its S1 Data supplement publishes any Chinese wording, so the item text shown here
    is the English the authors print in section 3.2 of the paper; the assignment of items to the
    codes SO3-1..SO3-3 follows the paper's own listing order, which the published factor loadings
    (0.914/0.920/0.919, reproduced from the live data as 0.9144/0.9199/0.9189) pin to the column
    order but not to the wording order, and the paper publishes no labels for the five Likert
    points, so option_text is blank
- table: niazi_2020_mfq
  issue: |-
    The item text here is the canonical MFQ30 wording (moralfoundations.org, MFQ30.doc, July
    2008), not the study's own variable labels: those labels are an abridgement, dropping the stem
    "Whether or not " throughout Part 1 and carrying the depositor's scoring notes on two items.
    The labels are what tie code to text and they reconcile 32/32 to the sentences shipped here.
    Note also that MATH and GOOD are the MFQ30's two catch items and belong to no foundation
    subscale, so a five-foundation score computed over all 32 items in this table would be wrong.
- table: niazi_2020_mfq_stereotype
  issue: |-
    The item wording here is the standard self-report MFQ30 form, but this table is the study's
    stereotype condition: respondents rated each statement as they predicted a typical member of
    the opposite gender would answer it. The authors' reworded stereotype instructions are not
    published in the paper or its supporting information, so the instruction and section-prompt
    fields are blank rather than carrying the self-referential canonical prompts.
- table: nomt_hooper_2024_study1
  issue: |-
    Study 1 randomly assigned participants to an English- or Spanish-language version of the same
    task (63 English, 56 Spanish); the item text shipped here is the English wording, and the IRW
    response table does not record which language a given participant received.
```
