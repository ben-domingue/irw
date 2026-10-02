# #2401 batch 1: what's staged, and what comes back to Ben

Everything under `~/irw-stage/2401-audit/` passed its own verification. **Nothing is uploaded.** Repo changes are on branch `ben-domingue/2401-audit` (worktree `~/irw-wt/2401-audit`), uncommitted.

## Staged, ready to upload (fixes Ben already ruled)

| what | tables | where | changes rows |
|---|---|---|---|
| Mechanical covariate / rt / resp-sentinel fixes (Decision 3) | 124 | `mechanical/` | `audit/2401/repairs/mechanical_table_changes.csv` |
| tuason, mclaughlin, amatus rebuilds (Decision 8) | 3 | `rebuilds/` | `audit/2401/repairs/rebuilds_table_changes.csv` |
| Item text: bitew ×4 language, beck/ali IES-R `_translated` removed (Decisions 7, 8) | see `audit/2401/repairs/itemtext.md` | `itemtext/` | withdrawals.csv rows |

**Held, not staged:** the 5 `narcissism_schneider_2025_study1_jauk_*` tables and `gcbs_brotherton_2013`. They have fixes in the unreleased draft, and repairing the live copies would upload over those fixes. They get re-run after the draft is released.

## Needs a yes/no from Ben

### A. Waivers (the upload gate blocks on conditions the live tables already have)
1. ~~`name_length`~~ **Ruled 2026-09-29: leave long-named published tables as they are.** Waivers recorded for the 7 tables.
2. `selm_2019_climate_knowledge`: 9 duplicate id+item rows already live. The dedupe is below (C1). Waive for this upload, or wait for C1.

### B. Confirmed judgement-class fixes (Decision 5: agents confirmed these; one yes covers all)
| family | tables | fix |
|---|---|---|
| guatemala_2024_homes (incl. 7 unflagged siblings) | 8+ | resp=3 ("No sabe") → NA on the Sí/No/NS grids |
| chile_2023_social-welfare `_h` | 1 | h3_d/h3_e resp=3 ("no children in household", "N/A") → NA |
| chile_2023_children-adolescents `cp9_*` | 1 | resp ≥ 88 → NA (the 88:88 "no sabe" time code parsed as 89.47 h) |
| chile_2023_social-welfare `yy3` | 1 | move the peso income out of `resp` to `cov_income_clp` |
| EEN_Lacey_2024 `mh_treatable` | 1 | recode to No=0/Maybe=1/Yes=2 (Maybe was coded 2, above Yes); `covid_jobloss` 2="not employed" → NA |
| spain_2013_services `p27c` | 1 | resp=3 ("still processing") → NA. **Another session has uncommitted edits to `data/spain_2013_services.do`, so coordinate first.** |
| DEMOS | 1 | all 4 "items" are per-stimulus composite means → withdraw the table (composite rule) |
| rt in milliseconds: emoji_scheffler, megart_tonkovic, spalex_aguasvivas, vollbracht | 4 | rt / 1000 |

Unsure, left as-is: sel_marca Q13/Q25 code 3 (needs a private codebook), western_reserve (opaque items), chile `u` (minutes as items).

### C. Identical-rows class (Decision 4). The triage split it four ways:
1. **Dedupe, 5 families.** `mhscdc_fried_2020_ema` (the same beep written up to 30×), `foundationalassist_worden_2026`, `smoking_perseverance_mcneish_2025`, `selm_2019`, **and `jiang_2024` (21 tables): see C4.**
2. **Rebuild, keeping a column the script dropped, 14 families.** 2.96M rows, 2.64M of them in PISA 2000/2006, whose scripts drop SCHOOLID so student ids collide. This is real rebuild work from raw files; in 9 families the dropped column is a trial or time column, not an id. Proposed: file one issue for this rebuild queue. Don't try it inside the audit.
3. **Known issue, 8 families.** emobank, petley, VCISM, robison_2026 ×2, cud_stone2024, nas_rogoza, debacker, megart. Proposed: a known-issues flag on each landing page.
4. **Eyeball:**
   - **`jiang_2024_*` (21 tables).** The source file is 707 real respondents stacked about 2.5× with *differing* demographics, which the paper reports as N=1,792. A dedupe leaves 707 people with conflicting demographics. **Dedupe with the demographics dropped, or withdraw the family?**
   - **`petley_2025_flanker_*`.** Its rows are synthetic Bernoulli trials expanded from correct/total counts. Does that belong in IRW at all?
   - **`emobank`.** Its duplicates are anonymous annotators who agreed. Keep as a known issue.

### D. Two follow-ons
- **The amatus siblings.** The 9 `amatus_cipora_2024_*` tables are also missing age for teachers. Rebuilds are staged in `rebuilds/amatus_siblings_pending_ruling/`. Proposed: include them (same ruling as the main table).
- **The detector tuning suggested by triage.** Change `resp_binary_plus` to a `{1,2}`-core rule, with precision rising from about 20% to about 73%. Worth doing before any re-run.
