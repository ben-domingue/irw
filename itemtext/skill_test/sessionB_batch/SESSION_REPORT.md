# irw-auto-itemtext Skill Test — Session B Batch Report (100/100 — COMPLETE)

## Executive summary

- **100/100 tables processed, 100/100 independently re-validated** — exact `item`/`resp`
  match against live ground truth on every table, confirmed in a fresh check that did not
  rely on agents' self-reports.
- **Coverage:** 78 tables with full item-text recovery, 3 partial, 19 with the join
  structure validated but item text honestly withheld (secure/copyrighted/paywalled
  sources, or genuinely unresolvable numbering) rather than guessed.
- **Needs your attention:** `pending_index_notes.csv` — 52 rows, one per table with a
  logged discrepancy or caveat, ready to paste into the real index sheet's NOTES column.
- **One quality issue found and fixed:** `gilbert_meta_38` initially shipped with guessed
  item text; caught on cross-batch review and corrected — see "Quality control catch"
  below.
- **No open blockers.** Everything below this point is supporting detail: per-table
  coverage reasoning, cross-cutting patterns worth feeding back into the skill, and the
  operational issues hit along the way.

---

## Scope

Run the `irw-auto-itemtext` skill (repo commit `fe22bc7`, past PR #1589) against a
100-table benchmark batch, processed in 10 waves of 10 parallel extraction agents. Ground
truth (`item`/`resp` sets) came from live `irw::irw_fetch()`, not from the withheld
`sessionA_batch/groundtruth_*.rds` answer key, which was not accessed at any point.

## Result: 100/100 tables complete, 100/100 independently re-validated

Every table has a `candidate_<table>.rds` + `extraction_log_<table>.md`. A final,
independent validation pass (re-reading every candidate and every cached ground-truth
object fresh, not trusting agents' self-reports) confirmed **exact `item`/`resp` match on
all 100 tables, zero failures**. No table was skipped, and no table hit the skill's
stop-and-ask gate for any reason other than the expected, pre-approved "already linked"
override.

### Coverage breakdown

| Coverage | Count | What it means |
|---|---|---|
| **Full** (0% of rows have blank `item_text`) | 78 | Literal item text recovered for every item |
| **Partial** (some blank) | 3 | Mixed — some items recovered, some genuinely unrecoverable |
| **None** (100% blank `item_text`) | 19 | Item/resp structure validated exactly; item-level text withheld rather than guessed |

**52 tables** have at least one row in `pending_index_notes.csv` — a discrepancy, caveat,
or provenance note for you to review before pasting into the index sheet's NOTES column.
This is expected at this scale, not a red flag: many are minor (e.g. "response anchor
wording sourced from the general published scale, not this study's specific materials")
rather than missing content.

### Two examples, to make "coverage" concrete

**Good recovery — `gilbert_meta_59` (Perceived Stress Scale, 10/10 items, exact match):**

| item | item_text | option_text (resp) |
|---|---|---|
| `pss1` | "Have you been upset because of something that happened unexpectedly?" | Never (0) … Very often (4) |
| `pss4rev` | "Have you felt confident about your ability to handle your personal problems?" | Never (0) … Very often (4) |
| `pss10` | "Have you felt difficulties were piling up so high you could not overcome them?" | Never (0) … Very often (4) |

The dictionary's cited paper doesn't even mention PSS-10 — the agent identified the
instrument from a *companion* paper on the same study cohort, then confirmed the mapping
by checking that the live data's `pss4rev`/`pss5rev`/`pss7rev`/`pss8rev` reverse-scored
suffixes land exactly on PSS-10's known reverse-keyed item positions (4, 5, 7, 8) before
trusting the standard published wording.

**Marginal recovery — `paampsmartsud_saba_2023_pacs` (Penn Alcohol Craving Scale, 2/5 items):**

| item | item_text |
|---|---|
| `PACS_1_POST` | *(blank)* |
| `PACS_2_POST` | "At its most severe point how strong was your craving?" |
| `PACS_3_POST` | "How much time have you spent thinking about doing drugs or drinking?" |
| `PACS_4_POST` | *(blank)* |
| `PACS_5_POST` | *(blank)* |

The paper quotes only 2 of the 5 items verbatim as illustrative examples; those two were
matched to `_2`/`_3` using the instrument's standard fixed item order (frequency →
intensity → duration → resistance → overall), which is a reasonable inference but wasn't
independently provable the way the AMPS sibling table's subscale-sum check was — so it's
flagged as medium-confidence in the log. The other 3 items were left blank rather than
filled with the *original* (unrevised) published PACS wording, since the paper explicitly
states the study revised the scale's alcohol-only language to also cover drug craving —
using the unrevised text would have been a plausible-looking but wrong answer. `item`/`resp`
still match ground truth exactly in both tables; the difference is entirely in how much of
the literal text a real, checkable source would support.

### The 19 fully-blank tables — why, grouped by cause

- **Secure/non-public researcher-designed assessments** (10): `gilbert_meta_1`, `_2`, `_8`,
  `_25`, `_74`, `_80`(picture stimuli only, see below), `_78`, `_100`, `_104`, `_108` — all
  from research programs (Kim/Gilbert content-literacy RCTs, IFPRI Kenya credit study) whose
  reading/vocabulary/knowledge assessments are test-secured or whose exact item wording
  simply isn't published anywhere reachable. Instrument identity, structure, and scoring
  were confirmed in most of these; only the literal item stems are missing.
- **Commercial/copyrighted standardized tests** (2, deliberate copyright-hygiene holds):
  `mpsycho_youthdep` (CDI — item stems were actually found in the R package's own CRAN
  docs, but deliberately withheld anyway as more cautious than the WJ-IV precedent) and
  `gilbert_meta_80`'s WJ-IV Picture Vocabulary stimuli (target words were extracted,
  stimulus images/prompts were not).
- **Naming-mismatch tables where the disclosed text belongs to a different variable set**
  (1): `suicide_reinbergs_2025_stig` — the paper's own Table 2 item text was verified to
  belong to a *different* raw variable (`dssm01-09`), not the live table's `stig01-09`;
  correctly left blank rather than misattributed.
- **Paywalled source paper, no accessible alternative** (3): `faces_spanish_vegas_2022_fss`
  (FACES IV/FSS, also copyright-cautioned), `fedsp_trzcinska_2023_smsd`, and
  `alsecypiamh_wu_2022_nei` (instrument identity confirmed via raw variable labels, wording
  paywalled/unavailable).
- **Genuinely ambiguous item-numbering with no empirical way to resolve it** (2):
  `paampsmartsud_saba_2023_ffmq` (two secondary sources gave contradicting FFMQ-24
  numbering schemes) and `wang_onlineriskexp_2025` (English precursor scale's item order
  vs. this study's Chinese-translated order and response format didn't line up safely).

None of these 19 are extraction failures — every one still has an exact `item`/`resp`
match, correctly-identified instrument (in nearly all cases), and an honest, logged reason
item text isn't there. This is the skill working as designed: "don't force a match" per
`SKILL.md`.

## Quality control catch worth flagging

**`gilbert_meta_38`** originally shipped with `item_text` filled from *inferred* DHS-survey-
style wording (guessed from variable names) rather than left blank when the real source was
blocked — inconsistent with every other blocked-source table in this run. Caught on a
cross-table review after batch 2, corrected in place (text blanked, log annotated with a
visible correction note). This is the one place in 100 tables where an agent's output
needed post-hoc intervention rather than being trustworthy as delivered — worth watching
for in any future unattended run of this skill, since a single agent working one table in
isolation has no way to notice it's drifting from the pattern every other agent in the
batch is independently converging on.

## Notable patterns across the full run

1. **Existing repo `data/*.R` / `.r` processing scripts were the single highest-value
   source** for opaque item-naming mappings — resolved `fad_dataset1/2`, `gilbert_meta_2`,
   `political_psychology`, `florida_twins_hwk`, `mhscdc_fried_2020_*` (5 tables sharing one
   script with a different column-offset per measure), and more. When items are bare
   integers or raw column names, check `data/` before anything else.
2. **Dataverse's AWS WAF bot-challenge is a systematic, cross-depositor blocker**, not
   specific to one research group — hit `gilbert_meta_*` repeatedly but also
   `faces_spanish_vegas_2022_fss` (a completely different depositor). DataCite's metadata
   API (a separate host) reliably worked as a non-blocked fallback for basic dataset
   identification, just not file contents.
3. **R package help documentation** (`?Dataset` after `library()`) was a repeatedly
   high-yield, low-effort source for CRAN-hosted psychometric datasets — MPsychoR
   (`_rmotivation`, `_ceaq`, `_lakes`, `_youthdep`), psychotools (`_gratitude_gart/gac`,
   `_conspiracist`), psychTools (`_athenstaedt`) all resolved this way, sometimes catching
   real bugs in the process (a duplicated item across subscales from a hallucinated
   WebFetch summary; a doc/data mismatch in `psychTools`'s own help file).
4. **Raw SPSS/.sav variable and value labels** (via `pyreadstat`/`haven`) recovered exact,
   verbatim item text straight from the source data file in several cases where the paper
   itself only paraphrased or partially quoted items — `pezzuti_2025_coolpeople_*`,
   `ips_vangsness_2019`/`afps_`/`aip_` (all three via one shared combined-survey PDF),
   `os_tbmwtfs_schubert_2023_bmw3`.
5. **Naming mismatches between table name and actual live content were common and always
   worth verifying rather than trusting**: `ccapsvtskhpacr_mercedes_2023_physical` (named
   for a kinesiophobia scale, actually a comorbidity checklist), `phq_insomnia_wang2025`
   (named for an insomnia index, actually PHQ-9), `rosenberg_fadplus_goto2021` (named for
   FAD-Plus, actually RSES), `fedsp_trzcinska_2023_smsd` (assumed self-esteem, actually an
   EU-SILC poverty indicator). In every case the live item names/count/resp range were the
   tell — worth checking against the dictionary Reference before trusting either blindly.
6. **Real empirical detective work, not just document-reading, resolved several genuinely
   hard cases**: reconstructing published subscale sums from raw items to confirm item
   order (`paampsmartsud_saba_2023_amps`), using correlation structure to determine a
   reverse-scored item stores its raw not analysis-ready value
   (`sun_2025_morality_study2_meaning`), matching response-frequency tables cell-by-cell
   against a codebook (`chile_2023_social-welfare-survey_h`), and per-category count
   matching against raw data to prove a paper's disclosed item text belonged to a
   different variable (`suicide_reinbergs_2025_stig`).

## Operational issues hit and resolved across the whole run

1. `tables_batch.csv` didn't exist at the start — derived from `manifest_batch.csv` (100
   confirmed unique rows after a naive line-count check was shown to be misleading).
2. `irw::irw_fetch()` was blocked by the auto-mode permission classifier on every attempt
   until the user granted Bash permission.
3. Several IRW table names required exact-case matching that differed from
   `tables_batch.csv`'s lowercase listing (`mpsycho_Rmotivation`, `ALSECYPIAMH_WU_2022_NEI`,
   `NAMPRB_Siwiak_2024_DESRPL`, `FEDSP_Trzcinska_2023_SMSD`, `Rosenberg_fadplus_goto2021`) —
   resolved via `irw_list_tables()` lookups when `irw_fetch()` errored "table does not
   exist" on the lowercase form.
4. The account's monthly spend limit was hit mid-batch during wave 2, killing 8 of 10
   subagents; the limit reset within the session and all 8 were successfully retried,
   reusing each one's partial `.cache/` where left behind.
5. The `gilbert_meta_38` quality-control catch described above.

## Files produced (in `itemtext/skill_test/sessionB_batch/`)

- `tables_batch.csv` — the 100-row input file, derived from `manifest_batch.csv`
- 100× `candidate_<table>.rds`, 100× `extraction_log_<table>.md`
- `pending_index_notes.csv` — 52 rows, one per table with a logged discrepancy/caveat
- `.gt_<table>.rds` (100 files) — cached ground-truth pulls, for reproducibility
- `.cache/<table>/` — cached source material (PDFs, codebooks, raw data files) per table
- `final_validation_summary.csv` — the independent re-validation pass's full per-table
  results (item_match/resp_match/blank_item_text_pct for all 100)

## Recommended next steps for you

1. Review `pending_index_notes.csv` (52 rows) and paste the relevant NOTES text into the
   real index workbook for each table — this skill has no tool that can write there
   directly.
2. Spot-check a sample of the "full coverage" tables against their cited sources — this
   report is honest about what's logged as uncertain, but a benchmark run like this is
   exactly the setting where an independent human read of a few outputs is worth the time.
3. Consider the patterns in section "Notable patterns" above as candidate additions to
   `SKILL.md` itself (the `data/*.R` first-check, the R-package-help-page source, the
   "verify the table name against actual content" habit) — several of these were
   independently rediscovered by many different agents across this run, suggesting they'd
   be genuinely useful codified guidance rather than one-off cleverness.
