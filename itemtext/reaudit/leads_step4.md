# Leads from #2382 step 4 (waves 5-8), 2026-09-25

The triage agents reported these while classifying. **None has been acted on.** Table defects may be wrong-now cases
(Ben's rule: file `wrong-now`, reopen the ingestion issue, withdraw), but that call is made case by case, not as a
sweep. Personal data: IRW does not ship these columns, but the public source deposits carry them.

## Wave 5

**Table defects**
- chen2026_mpa / _sa / _sc duplicate chen_2026_mobile_phone_addiction / social_anxiety / self_control: the same
  Dataverse file was processed twice.
- ritzel_2020_farmer_burden: `cov_region` is a unique row id (CODE 1..802), not a region.
- spain_2025_tourism_importance: the script drops the valid middle answer "Regular" (resp=3).
- liu_2017_mcmq has 20 items against the paper's 19; chen_2019_csq has 27 against the paper's 20.
- lsbq_maleki_2025: the script maps `.L` codes but the .sav uses `.U`, so persian_comprehension and
  non_persian_proficiency have 3 of 4 items and non_persian_use 9 of 13.
- robison_2026_retesting_stai: the STAI-6 stems are the response table's item codes, so the register block can't reach
  them (the luu_2024_stai6 shape).
- PMT_Trzcinska_2023_*: the processing script handles a different dataset, so the script that made these tables is
  missing.
- demirbag_2025_goal_orientations has 21 items where the paper's AGQ has 12.
- West BPAQ has 10 items against 9 physical-aggression items.
- deception_professors items are bare integers built from column order.
- fullscaleiq_* cite Hampshire 2012, but the data are the Open Psychometrics FSIQ test.
- Goyal Study 6: each respondent appears as 6 pseudo-ids, because the trial number is appended to the id (mfq, dt, pp,
  mr, nfc, stance). Goyal nfc merges the 41-item and 15-item forms under nfc1..15.
- Kocar: three instruments are merged into one 38-item table.
- Jaracz TEMPS-A: TEMPS1 was dropped as a "lead-in" but is probably item 1.
- Anunciacao ASQ:SE: asqse1..39 mean different items at each of the 9 age intervals.
- Wimmer: the positional script drops FOILS1.
- Saha: the Mendeley source deposit was removed "as per author's request".
- Possible exposure: cognitive_load_klimova_2023_mlq shipped item text (irw#1930). If that MLQ is the Meaning in Life
  Questionnaire, the register blocks it.

**Personal data in source deposits**
- Sandhu PLOS S1 Data: respondent IP addresses.
- Kotsou figshare SCSdata.xls: full dates of birth.
- det_naismith_2023 (OSF zy8fb): full birthdates.
- Goyal OSF qehna: 223 IP addresses and 198 lat/long pairs.
- Anunciacao OSF n5ksw: children's dates of birth, parent initials, ZIP codes and free-text comments.

**Questions for Ben**
- pact_project: the Gates-MacGinitie items are commercial (hold). Ship the other items and leave those blank?
- The BDI editions other than BDI-II (BDI-SF, BDI-IA; kotsou, liu): does the Pearson BDI-II register row cover them?
- liu_2017_communication: the SMRC grant says "to use in your own research at no cost and without permission". Is
  that a research-only scope (block)?
- Altgassen: s01_knowledge's answer options are dictionary definitions (Duden, Oxford, DWDS), which is a third-party
  rights question. (A lone adjective under a rating stem is item text, as with PANAS, and is not treated as a
  question.)

## Wave 6

**Acted on (Ben's standing wrong-now rule)**
- MEFSIRODGAS_Nileksela_2023_freq held the severity responses (identical to _severity). Withdrawn in the draft;
  #2432, #208 reopened.
- paampsmartsud_saba_2023 ffmq/pss/ders/pacs: the "baseline" wave was built from the POST columns, so both waves are
  identical. Withdrawn in the draft; #2433, #358 reopened. Item text for ders/ffmq/pacs is left live.

**Table defects (not acted on)**
- parc_balaji_2017 and cfc_balaji_2019 were built from the same Dataverse file (same UNF).
- gerber_2022_self_esteem and gerber_2022_selfesteem are duplicates (two scripts built the same block).
- spain_2024_ideology's reference names the wrong CIS study (3480 is "Ideologia y polarizacion").
- puro_2025_prompta_writing: the script reads the EXPERIMENTAL block as "a different rubric", so only the 46 control
  students ship.
- eldor_2022 political_resilience item 49 and violent_extremism item 5 are attention checks stored as items.
- zeng_2025_megaproject_ecm has 15 items where the paper describes 8.
- LOC_fadplus_goto2021 is the locus-of-control block, not FAD-Plus.
- mbft_anunciacao_2024 keeps cov_profession and cov_institution.
- C19PRC wordsum: the IRW build-script comments spell out all 10 GSS Wordsum words and keys, which GSS keeps
  confidential.
- emotion_pcmrs: the source (FBL-R norms) is released only under a Hogrefe usage contract. That is a question about the
  response data itself.
- Register: RAND's pages now carry a non-commercial permissions block, so the RAND-36 ship row may need a re-look. The
  MBI (Mind Garden) has no register row yet.

**Personal data in source deposits**
- Dopmeijer PLOS S1 .sav: full dates of birth for 3,141 students.
- OSF wkzan (Anunciacao IFP): 272,845 test-takers with date of birth, employer, institution and city.
- Niileksela raw xlsx: free-text mental-health diagnoses.
- tasaygar PLOS S1: an initials column next to age and sex.

**Questions for Ben**
- darkfactorfrench: the French wording exists only in a CC BY-NC OSF deposit. Should 5 tables ship the English
  canonical original under the fallback rule instead?
- gao SCSQ: the block rests on Psychology Roots' site-wide boilerplate. Was the third-party-permission ruling meant to
  cover site-wide text?
- issueirt_votes_shin_2024: are Voteview roll-call descriptions item text?
- ajaykumar_2023_experience: are codebook paraphrases ("level of experience with robots") item text?
- goldberg PDA-360: a single adjective per item is item text (PANAS shape) and was not treated as a question.
