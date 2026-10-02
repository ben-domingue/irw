# conner_2017_lot: inverted anchors on items 2, 4 and 5 (#2230)

Ben ruled 2026-09-30 to replace the live copy.

**The defect.** The live `conner_2017_lot__items` (`irw_text`, pilot-era) labels every item 1 = "Strongly disagree", 7 = "Strongly agree". But the deposit stores the three pessimism-worded items (item2, item4, item5) **already reverse-scored**. The S1 `.sav` labels say "(already reverse scored)", but its value labels were never flipped. So on those three items a 7 means strong *dis*agreement, and the live item text said the opposite.

**Evidence** (`verify_conner_2017_lot.R`, VERDICT: PASS; first written by batch_303, which built this fix and then withdrew it in #2268 because the table was already published):
- The item wording matches the `.sav` variable labels for all six items.
- All six items intercorrelate positively (min 0.29). That can't happen if items 2, 4 and 5 are stored raw.
- All six correlate negatively with the trial's CES-D (-0.32 to -0.41). "If something can go wrong for me, it will", stored raw, would correlate positively.

**The file.** `conner_2017_lot__items.csv` is the live table (read from `irw_text` current on 2026-09-30) with exactly six cells changed: `option_text` for item2/item4/item5 at resp 1 ("Strongly agree") and resp 7 ("Strongly disagree"). Every other cell is byte-for-byte the live value, and nulls stay null (not literal "NA"). 42 rows. `irw-validate` passes.

**Rights.** LOT-R is `ship_with_note` in `instrument_rights_register.csv`. The Carver page's "Please note that this is a research instrument, not intended for clinical applications" disclaims fitness and reserves no right, so it does not block (2026-09-08 rule).

**Staged** for Ben's batch in `oneoff/upload_queue_2026-09-30/irw_text/`. red_up replaces the table itself.
