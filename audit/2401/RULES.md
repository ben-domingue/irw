# irw#2401 audit rules (DRAFT, pilot version, 2026-09-29)

One set of rules for the whole retroactive audit. The pilot tests this draft. A rule the pilot had to bend is recorded in `pilot/REPORT.md`, not patched here quietly.

**Freeze date: 2026-09-29.** The rulings and register rows in force on that date govern the whole pass. A ruling made mid-audit applies only to tables not yet reviewed.

## 1. What is checked, and against what

| Strand | Standard applied |
|---|---|
| **rights** (item text) | `itemtext/instrument_rights_register.csv` as of the freeze date. The 2026-09-04 rulings: an enforced licence fee disqualifies the wording (TAS-20), and a quotable no-redistribution clause overrides the deposit's licence (DSES). The #1891 rule: a *stated* non-commercial restriction on the wording blocks it. Silence is not a restriction (#1897). The response table itself is not at issue: the rulings are about wording. |
| **data** (response table) | `datastandard.md`, plus `irw_validate`'s **upload** profile run on live data (the `legacy` profile only for tables that predate a rule). A finding counts only if it would change an analysis: wrong values, rows that shouldn't exist, or missing rows. |
| **claim** (issues page, language) | The public text must match live data today. A claim that no longer holds is removed. A vague claim is made more precise. |
| **note** (source caveat) | #2529's test: something a user of the table should know that the table can't express, and that is true of the *source*, not an IRW defect. |
| **format** (validator warnings) | Out of scope unless the warning changes an analysis. A warning that is a false alarm is recorded as such, so the checker can be tuned. |

## 2. Allowed outcomes (exactly one per finding)

| code | outcome | lands in |
|---|---|---|
| `fix` | rebuild the response table or item text | `data/` or itemtext script, then `metadata/table_changes.csv` |
| `withdraw` | take the item text (or table) down | `tools/withdrawals/<script>` + `itemtext/withdrawals.csv` |
| `known_issue` | an open IRW defect not fixed in this pass | `landing/known_issues.tsv` (datapages/irw) |
| `data_note` | a source caveat | `metadata/data_notes.csv` |
| `claim_edit` | rewrite or remove an issues-page entry | `itemtext_issues.qmd` (datapages/irw) |
| `register` | a register row or pattern change, and no table-level action | `itemtext/instrument_rights_register.csv` |
| `waive` | a real validator finding, accepted | `processing_notes/validator_overrides.csv` |
| `no_action` | checked, nothing wrong (including false alarms) | the worklist row only |
| `needs_ruling` | the evidence is clear but the policy isn't | escalated to Ben, grouped with others that need the same decision |

## 3. Evidence bar

- **Live data, never `data/pub` alone.** The local archive is stale (see `irw_validate/results/README.md`). Use aggregate queries (`irw_validate.live_*`, SQL) and not whole-table `irw_fetch`, because of the export cap. Call `redivis_shim.install()` before any row read.
- **A lead is not a verdict.** A round-log line, an agent report or a name match is where the check starts. The dossier states what was re-checked independently.
- **Rights:** quote the clause and give its URL (Wayback if the live page has changed). "Couldn't find terms" means *no stated restriction*, not "unknown".
- **Confidence**, one of `high` / `medium` / `low`. Anything below `high` on a `withdraw` or `fix` becomes `needs_ruling`.

## 4. Grouping

Findings that need the same decision are grouped (e.g. "all live BFI-2 wording") and ruled once. The worklist's `group` column carries that key.

## 5. Worklist schema (`worklist.csv`)

`table, strand, source, claim, checks_run, evidence, proposed_outcome, confidence, group, minutes, redivis_reads`

- `source`: where the lead came from (`round_log:L<line>`, `issue:#NNNN`, `legacy_sweep`, `provenance`, `control`).
- `claim`: the lead as stated, in one line.
- `evidence`: the short result, plus a pointer to the dossier.
- `redivis_reads`: `none`, `aggregate`, or `rows:<n>`.

## Decisions (Ben, 2026-09-29)

These supersede the per-table workflow above. The audit fixes **classes**, not tables (see `detectors/RESULTS.md`).

1. **Class-based audit.** Rule once per class, fix family by family, report batch totals.
2. **Out of scope:**
   - legacy-sweep format warnings;
   - script-reproducibility (`script_drift`), which becomes its own later project;
   - hunting for data notes, which are written only when a table is touched anyway.
3. **Mechanical classes, fixed without per-table review** (`irw_validate/repair_classes.py`):

   | class | fix |
   |---|---|
   | `cov_all_null` | drop the column |
   | `cov_sentinel` | values to NULL |
   | `cov_range` | values to NULL; age bound 0–120 as in #1779, birth year 1900–2026 |
   | `rt_constant` | rename to `cov_completion_time_s` |
   | `resp_sentinel` | drop those rows |

   `rt_units` goes to triage first.
4. **`dup_exact`:**
   - if a country, sample or study column separates the colliding ids, prefix the id;
   - otherwise dedupe;
   - if neither can be settled from the source, flag as a known issue.
5. **Judgement classes** (`resp_binary_plus`, `resp_mixed_scale`): agents triage each family against its source. Only confirmed cases come back, as one batch with fixes proposed.
6. **`dup_id_item` with conflicts:** stays with #1856.
7. **Rights:** an instrument's `block` register row covers the `*_translated` columns too. `beck_2021_iesr` and `ali_2021_iesr` lose their English IES-R `_translated` text. The rights sweep must read `_translated`.
8. **One small rebuild batch now:**
   - `tuason_2021_covid_coping_enjoy`;
   - `bitew_2020_*` language metadata (4 tables);
   - `mclaughlin_samuel_2025_auditory_session_2`;
   - `amatus_cipora_2024_fsmas_se`;
   - the false "already reversed" header in `lee_2020_empathy`'s script.

   Covariate and `rt` cases go through the class batches instead.
9. **Sample floor:** applies to incoming tables only. Published tables under 100 stay.

**Held:** tables with a `table_changes` row dated 2026-09-22 or later have a fix in an unreleased draft. Repairing the live copy would upload over it, so they wait for the draft's release.

## Decisions, round 2 (Ben, 2026-09-29, on BATCH_1.md)

- **Long table names:** already-published tables stay as they are. The 40-character cap is for intake only. Waivers are recorded.
- **B, the 8 confirmed value fixes:** approved. Spain `p27c` waits for the other session's `spain_2013_services.do` edits.
- **C, identical rows:**
  - dedupe `mhscdc_fried_2020_ema`, `foundationalassist_worden_2026`, `smoking_perseverance_mcneish_2025` and `selm_2019`;
  - known-issue flags on the 8 families;
  - one new issue for the 14 rebuild-from-raw families.
- **`jiang_2024_*`:** withdraw. The source's 707 respondents are stacked about 2.5× with conflicting demographics.
- **`petley_2025_flanker_*`:** keep. Expanding the per-condition correct/total counts is lossless for models that treat trials as exchangeable. Drop study 1's invented `trial` index, add a data note (trial order not observed), and record a `dup_id_item` waiver because the repeats are by design. Don't look for trial-level source data.
- **amatus siblings:** included under the same ruling.
- **`ali_2021_iesr`:** withdraw its item text entirely (Ben, 2026-09-29). Its base `item_text` is the English IES-R, a `block` row. The response table stays.
- **`_translated` rights flags:** where the flagged wording is confirmed as a `block` instrument's, it is removed under Decision 7 with no new ruling. If a table's base `item_text` also carries it, that comes back to Ben.
- **A block covers translations (Ben, 2026-09-29).** A `block` row covers the instrument in every language, not only English, in `item_text` as well as `*_translated`. Applied here:
  - withdraw `sun_2025_morality_study2_meaning`'s item text (the MLQ-Presence subscale, in Chinese);
  - `jablonska_2020_swls` (Polish SWLS) and `queiros_2018_qcae` (Portuguese QCAE_1–6, which are the IRI) lose the blocked items in their base text as well;
  - `gomez_2022_qcae` and `powell_2018_qcae` lose QCAE_1–6 (English IRI) from `item_text`, and the rest of the QCAE stays.
- **`jablonska_2020_swls` response table (Ben, 2026-09-30):** its item codes are the SWLS's own English wording (e.g. "52. I am satisfied with my life."), which counts as shipped wording under the rights rules. The codes are recoded to neutral `swls_1`–`swls_5`, following the SWLS's published item order. No response changes.

## Decisions, round 3 (Ben, 2026-09-30)

- **`alsecypiamh_wu_2022_empathy`:** withdraw its item text. It is the whole English IRI Empathic Concern subscale (items 2, 4, 9, 14, 18, 20, 22), and the IRI is a `block` row. The response table stays.
- **`foundationalassist_worden_2026`:** withdraw it. Ben confirmed the source's dataset card (huggingface.co/datasets/ASSISTments/FoundationalASSIST) declares CC BY-NC 4.0, which is not an open license under IRW's rules.
- **`jablonska_2020_hads`:** check its 14 item codes against the published HADS. If they are the licensed wording, recode them to `hads_1`–`hads_14` (no response changes); if they are a paraphrase, leave them.
- Open the website PR (the tuason issues-page fix, the amatus entry, the 11 known-issue rows) and the `2401-audit-3` PR.
