# `phq_insomnia_wang2025__items` — the last doubled table (#1816)

`phq_insomnia_wang2025__items` was live at **72 rows for 36 distinct** — an exact
2x, every row present twice. Same class as #1810/#1816, but from an earlier
upload: it has no provenance row in any batch file, and its two siblings
(`aslec_insomnia_wang2025`, `isi_insomnia_wang2025`) were both in the tier A 78
and are clean, so the backfill did not cause it.

`phq_insomnia_wang2025__items.csv` here is **the published content, deduplicated,
and nothing else** — the 36 distinct rows exactly as `irw_text` v14.0 serves
them. No text was edited, no column added. A fix should change one thing.

Cross-checked against `itemtext/skill_test/sessionB_batch/`, whose
`candidate_phq_insomnia_wang2025.rds` holds an independently extracted 36-row
version: the item set (`PHQ_1`..`PHQ_9`) and response set (0-3) match the live
response data exactly, so the join is sound in both.

## Two things this does NOT fix, deliberately

**The item text has lost an em-dash.** Live `PHQ_6` reads "Feeling bad about
yourself or that you are a failure...", where the canonical PHQ-9 wording — and
the independent extraction — has "Feeling bad about yourself **—** or that you
are a failure...". That is an encoding fault of the same class as
`namprb_siwiak_2024_kop20`'s stripped Polish diacritics, recorded in #1806 and
likewise not silently repaired. Meaning is unchanged, so it is not urgent; it is
a separate edit to published text and wants its own decision.

**The table's name and citation describe a different instrument.** The name
`phq_insomnia_wang2025` and the dictionary `Reference` both point at a paper
about the *Insomnia Severity Index*, but the data is nine `PHQ_*` items on a 0-3
scale — the PHQ-9. The study administered both instruments; this table is the
PHQ-9 and is named for the other one. `itemtext/skill_test/sessionB_batch/
extraction_log_phq_insomnia_wang2025.md` has the full investigation, including
the paper text confirming the battery. Renaming a live table and correcting a
dictionary row is a decision, not a repair.

Both are recorded on #1816.
