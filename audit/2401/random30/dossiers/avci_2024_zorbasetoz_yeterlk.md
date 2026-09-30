# avci_2024_zorbasetoz_yeterlk (slot 30, agent e)

**State.** Live in `item_response_warehouse_5` (1,296 rows = metadata.csv). No item text, so no rights check. Not in withdrawals, table_changes, data_notes or validator results.

**Data (full live read; upload profile: conforms, passes).** 216 ids x 6 items, 1-7; item 8 has no 1s (`resp_scale_nested_support` warn, category non-use). No dups. cov_age 18-73, founding year 2003-2021, n_partners 0-6, n_employees 0-73.

**Finding - free-text covariates are truncated in the source (data_note, medium).** `cov_expertise` and `cov_sector` are cut to 8 bytes: `Mühendi`, `Yazılı`, `MÜHEND`, `Pazarlam`, `Biyotekn`. Checked against the deposit (Mendeley 826gmw6ypw, `öLÇEK Murat_UYARLAMA_HALİ SON.sav`, sha256 1eb9f472...7b75, downloaded 2026-09-29): both are `A8` string variables in a UTF-8 file, so the truncation is in the source, not IRW. They are also unstandardised free text (`Mühendi`/`mühendi`/`MÜHEND` are one category), so grouping on them splits categories. The unlabelled codes are also worth a line: `cov_gender` 1=Kadın (female), 2=Erkek (male) (181 male, 35 female); `cov_education` 1=primary ... 5=doctorate. This applies to all 27 `avci_2024_*` tables (group `avci_2024_covs`). The table itself is still usable.

**Source caveat.** `data/avci_2024_entrepreneurial_orientation.py`: `*ORT` subscale means are dropped and typo'd block names repaired; nothing that affects this block.
