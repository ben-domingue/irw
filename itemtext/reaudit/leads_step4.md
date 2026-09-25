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
