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

## Wave 7

**Acted on (standing wrong-now rule; each checked against the live table first)**
- ds14_mokken: Si3. is a reversed copy of Si1., and the real Si3 is lost. #2434.
- alsuhibani_2022_gcbs: GCBS_07-15 are shifted by one item for Study 2. #2435.
- fcupanas_cffsdas_reyna_2018: Study 4's PANAS11-20 are in a different order under the same codes. #2436, #308
  reopened.

All three are withdrawn in drafts (item_response_warehouse, _3). The alsuhibani item text is left live.

**Checked and NOT a wrong-now case**
- matosaslopez_2024_teacher_assessment: its two forms are recorded in `cov_questionnaire_type`, and the per-item means
  match. Separate lead: responses are near-uniform on 1-5 and the mean inter-item r is about 0.01, which may mean the
  data are simulated (the okeke pattern). **For Ben.**

**Table defects (not acted on)**
- ds14 aside, the other *_mokken tables were not checked.
- alsuhibani_2022_gcbs_extra_s2 pairs a Diana item with canonical GCBS item 15; retire it at the rebuild.
- eammi_grahe_2018: the live mindful/stress tables still carry computed biascheck columns, and range filters drop every
  stress "5" and every physsx "3".
- rfq8_wozniakprus_2022 reads the same Dataverse file as rfq_wozniakprus_2021 (probable duplicate).
- GART_Grolig_2020 holds study 2 only.
- chen_2022_cesd: CESD02 ("feel like dying or hurting myself") is not a CES-D item.
- nature_relatedness merges three instruments.
- political_psychology items are column-order ids.
- gahps_korner_2021: the ids may collide across studies.
- bialowolski_2024_financial_literacy has three gendered wordings per item, and FL codes skip 18.
- pks_probability p110 is worded differently for lab and online respondents.
- chakraborty2026_IRI has 21 items vs two 7-item subscales.
- vermeiren_2022_bfi pools 150 differently named columns from three studies.
- villarrealzegarra2026_trif has 85 items vs the preprint's 53.
- dong_2024_engagement EE5_A differs from EE5 in 69% of rows.
- anunciacao GMI keeps option numbers on a matrix test.
- yuebo_2024_pck reads as TPK items.

**Personal data in source deposits**
- Doherty BICDIS.sav (Irish consultant doctors): specialty, mental-health diagnosis, antidepressant use, disciplinary
  actions and lawsuits.
- Celik TEZ_412VERI.xlsx: a name-initials plus phone-digits code.
- OSF fecgz: 100 Prolific IDs in free text.

**Questions for Ben**
- avci_2024 entrepreneurial motivation (12 tables): are stemless reason phrases ("Kariyer yapmak") item text?
- The canonical-English fallback when the translation is published NC-ND (zhou_2025 exercise self-efficacy, now
  RIGHTS_BLOCK) or CC BY-NC-SA (reyna's Spanish PANAS): does the English original ship?
- haehner CCB2I: first published in a CC0 preprint, but the JPSP version is CC BY-NC-ND. Which governs?
- ART / author-recognition lists (GART, Wimmer): are they item text?

## Wave 8

**Table defects (not acted on)**
- arbinaga_2025_sport_anxiety is misnamed: its 45 items are the SA-45 symptom checklist.
- arbinaga_2025_perfectionism: the paper says Frost MPS, but the deposit's labels are coping-in-sport. Identity conflict.
- lev_ari_2021_des has 14 unlabelled items where the paper used the 28-item DES-II.
- spain_2014_volunteering_activity: P10A asks whether the association is "especificamente juvenil", not about "active
  participation". The name and description are wrong.
- argentina_2013_* biblio says ENSSyR 2023; the survey is 2013.
- spain_2015_immigration_proximity: P27a/b reverse P26a/b (check at extraction).
- wallace_2026: about 10 tables carry one code with study-specific referents (MCM Consulting / XYZ Organization /
  professor), so item text needs per-study variants. The S2a label vs script disagree on which organisation.
- adamczyk_2022_workbat has 20 columns vs 15 statements.
- enders_2022_conflict: conflict_1/2 are unexplained, and there is a second PSS-4 block in the raw export.
- data/robison_2026_retesting.py has no source header.
- data/nguyen_2026_factcheck.py puts a personal email in its User-Agent.
- OSF amiot (56sbh) and adamczyk (7hv32) now return 401 without view-only links.
- zhou_2016_anxiety's withdrawal is still in the irw_text draft (release owed).

**Personal data in source deposits**
- Enders OSF 6a7et (CC0 raw export): ZIP code, birth year, gender and state per respondent.
- fan_2026 PeerJ deposit: caregiver and patient birth year-month with diagnosis and record id.

**Questions for Ben**
- spain_2014_citizenship (13): CIS fielded the ISSP 2014 module. Does the CIS grant cover the ISSP wording (GESIS
  terms unread)?
- spain_2011_immigrant (10): Immigrant Citizens Survey (King Baudouin / MPG), "for your own use ... excerpts". Is that
  a restriction?
- IFEval prompts (Apache-2.0): the import was scoped scores-only.
- aziz_2020_bmq: the register row says `escalate`.
