# `_translated` rights follow-up, #2401, 2026-09-30

Loose ends from `repairs/rights_translated.md` ("Still open"). Read-only: nothing withdrawn, staged, uploaded or committed. Rows are in `rights_translations_followup.csv`.

**Method.** The live item text (`current` version, all 2,450 tables in `irw_text`, `irw_text_2` and `irw_text_3`, with `item_text` and `item_text_translated`) was dumped to the session scratchpad, not the repo. The dump was compared in scripts against:
- the register's `match_item_text` stems for MLQ, IRI, SWLS and EWBS-LWB;
- short key fragments for every item of the 28-item IRI, the 10-item MLQ and the 5-item SWLS;
- multilingual phrase patterns in Spanish, Portuguese, German, Polish, French, Italian, Czech, Dutch, Turkish, Swedish, Chinese and Russian.

A separate scan looked for instrument patterns in the item codes. Candidates also came from `metadata/itemtext_metadata.csv`, `biblio.csv` and `tags.csv`, and from every `provenance.csv` in `itemtext/itemtables/`, including the queue-rounds checkout. Tables already in `itemtext/withdrawals.csv` were set aside.

## 1. `sun_2025_morality_study1_meaning`: PERMA-Profiler, not MLQ

- Its codes are `tspermam1`-`tspermam3`, three items. These are the Meaning items of the PERMA-Profiler, the same family as study 1's `tspermap`, `tsperman` and `tspermar` tables. The MLQ-Presence subscale has five items.
- The script `data/sun_2025_morality.do` builds this table from `ts.PERMA.m*`. It builds study 2's table from `tsmlq1`-`tsmlq5`.
- In the comparison scripts:
  - it matched 0 of 6 register MLQ stems and 0 of 10 MLQ item fragments;
  - it matched all 3 PERMA-M fragments.
- The register's original PERMA note was right for study 1. The MLQ block does not reach this table.
- The PERMA-Profiler has no register row. Its terms are unreviewed; that question was not asked here.

## 2. QCAE: no other tables

Three tables carry QCAE items: `gomez_2022_qcae`, `powell_2018_qcae` and `queiros_2018_qcae`. All three are already handled. The searches that found no others:
- item codes;
- metadata instrument names;
- provenance;
- a check of 8 QCAE-distinctive fragments across the corpus. Only these three tables matched 8/8; two IPIP tables matched 1 each.

## 3. IRI, SWLS and MLQ not yet withdrawn

**One new finding:** `alsecypiamh_wu_2022_empathy` is the IRI Empathic Concern subscale, whole and verbatim in English `item_text`.
- `Empathy1`-`Empathy7` match the 7 EC items (IRI 2, 4, 9, 14, 18, 20 and 22) at similarity ratio 1.00.
- The metadata, tags and dictionary all name it.
- The pilot audit (2026-08-17) had already recorded it as verbatim IRI EC.
- Why the earlier checks missed it:
  - the register's code regex `^iri|^pts?..` does not match `Empathy*`;
  - only 1 of the 10 register IRI stems is an EC item.
- Its sibling `alsecypiamh_wu_2022_swls` was withdrawn on 2026-09-09.
- Under the IRI `block` row this is a whole withdrawal. That needs Ben's go-ahead.

**No other English hits.** Leads from the register stems and the per-item fragments were read in-script and cleared (listed in the CSV):
- `fredrickson_2015_mhcsf`;
- `goldberg_2018_ipip`;
- `heard_roch_2022_swlpwi`;
- `wang_2025_green_space_wellbeing`;
- `liu_2025_learning_motivation`;
- `corti_2023_academic_adaptation`, already FALSE.

**No other-language hits beyond tables already withdrawn** (medium confidence).
- In the multilingual phrase sweep, every hit was a single incidental item: ENEM, the Chilean and Argentine surveys, the CIS surveys and `spanishmegastudy`.
- The provenance-named IRI, MLQ and SWLS tables that are not in the ledger are not live, because they were held at extraction:
  - `herrera_2018_iri`, `zautra_2015_iri` and `ruiz_parra_2023_iri_pt`;
  - `liu_2025_mlq` and `ALSECYPIAMH_WU_2022_MIL`;
  - `park_2021_swls`, `ptacek2023_swls`, `rahm_2017_swls`, `rzeszutek_2020_swls`, `wu2021_swls` and `song_2025_lwb`.
- The phrase lists cannot catch every rewording. A translated SWLS, MLQ or IRI under a neutral table name, with wording outside those patterns, would be missed.

## Records that need a follow-up (not edited here)

- The IRI register row could name `alsecypiamh_wu_2022_empathy` and widen `match_item_code`, or add EC stems.
- The docstring of `itemtext/sweep_instrument_rights.py` still says `sun_2025_morality_study{1,2}_meaning` are both PERMA. Study 2 is the MLQ.
