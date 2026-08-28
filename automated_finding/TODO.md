# IRW Automated Finding — TODO

Currently open action items only. For the full batch-by-batch history and
context behind these (and everything already resolved), see `BATCH_LOG.md`.

## From the 2026-08-28 Zenodo re-run

- [x] **Zenodo connector fix validated end to end** (2026-08-28). The fix in
  `9d481e6` was necessary but not sufficient -- it had also poisoned
  `repo_triage_seen_keys.csv`, where 92 Zenodo keys sat as `no_usable_file`
  verdicts against deposits no resolver had ever opened. Released (backup at
  `repo_triage_seen_keys.csv.bak`, list at
  `runs/zenodo_released_keys_2026-08-28.csv`) and re-triaged: 4 leads
  recovered, the other 88 now carry real verdicts.

- [x] **15 tables / 85,307 responses uploaded and in biblio** (confirmed
  2026-08-28, ben-domingue) from 6 Zenodo deposits, all CC BY 4.0, all new to
  IRW (creates, not replaces). The 15 `irw_output/` CSVs are off disk as
  expected, and the `biblio_zenodo_2026-08-28.csv` rows are in the dictionary.

- [ ] **THE BIG ONE: ~2,458 prior repo-mode terms have never had working
  Zenodo coverage.** A 140-term sample returned 1,342 candidates of which
  **801 were new** -- absent from both the ledger and the 6,048-candidate
  2026-08-27 sweep -- yielding 276 open-licensed keeps and 15 shippable leads.
  Zenodo was dark, not thin. The full sweep is ~9 hours unattended and
  one-time; future runs inherit the fix automatically. Agreed with
  ben-domingue on 2026-08-28 to fire this "later in the afternoon".
  Command shape:
  `python3 irw_discover_updated.py <terms> --sources zenodo --out runs/<name>.csv`
  then prefilter -> rank -> triage as in `BATCH_LOG.md`'s 2026-08-28 entry.

- [ ] **10 of the 18 Zenodo leads still unworked** (~52k responses). The tail:
  item text used as column headers, several header-offset files, one allergy
  survey that is mostly clinical binaries rather than an instrument. Two are
  blocked on deposits whose author field is literally "Anonymous"
  (`zenodo.20475015`, and `10.7910/DVN/YCXDBI` from tier B) -- clean data, no
  name for `authorname_year_construct`.

- [ ] **PISA re-publication held.** `zenodo` PISA 2018/2022 deposit, 35,943 x 7
  = 251,601 nominal responses, was the largest lead of the Zenodo batch. It is
  a re-publication of PISA variables rather than an original instrument; IRW
  already carries PISA tables and #1342 is open on PISA per-country exclusion.
  Check against the dictionary and #1342 before writing a script -- do not
  assume those responses are additive.

## From the 2026-08-27 tier-B batch -- CLOSED

- [x] **Tier B closed 2026-08-28 (ben-domingue's call).** 432 of the 463
  tier-B leads triaged, Step 2b run, and the highest-value deposits worked:
  **22 tables / 4,749,229 responses** staged to `irw_output/` with
  `biblio_tierB_2026-08-27.csv` (22 rows) prepared for the dictionary. See
  `BATCH_LOG.md` for the per-deposit coding decisions.

  Tier B is closed as a *worklist*, not exhausted. Deliberately left unworked,
  and still recoverable from `runs/triage_tierB_2026-08-27.csv` and
  `runs/retriage_tierB_2026-08-27.csv` if anyone wants them:

  - **~65 `worth_retrying` rows, ~950k responses.** The tail after the top
    dozen; mostly 200-600 respondent single-instrument deposits.
  - **19 of the 31 `good` rows, ~120k responses.** The small tail -- largely
    100-300 respondent Indonesian marketing surveys at 3-10k responses each,
    several needing header-offset repair. Low yield per unit of work.
  - **129 `human_review` rows** in
    `human_review/human_review_repo_tierB_2026-08-27.csv`.
  - **68 `download_failed`** rows, deliberately left out of
    `repo_triage_seen_keys.csv` so a later run retries them.

- [ ] **The lead ranker cannot see dataset size, and tier B proved it costs
  us.** Tier B scored *lower* than tier A on every signal the scorer reads
  (title wording, filename, file count, license) yet carried ~7.8M candidate
  responses to tier A's 1.3M -- because the 3.7M-response
  `tu_2022_achievement_motivation` deposit looks, from its title and filename,
  exactly like a 300-respondent survey. `resolve_data_files()` already returns
  file sizes for most sources, so adding a size term to
  `runs/rank_2026-08-27.py` is cheap and would put deposits like that at the
  top of tier A instead of the middle of tier B.

- [ ] **Two named leads deferred for identity reasons, both otherwise clean.**
  `10.7910/DVN/YCXDBI` (Teacher Work Ability Scale, 36 items x 4 samples,
  2,539 respondents, CC0) has the literal string "Anonymized" in its Dataverse
  author field, so there is no name for `authorname_year_construct`;
  recoverable if the paper behind it is identified. And Mendeley `8bphntrc65`
  (spiteful/strategic punishment, 315 x 205) was skipped under the blanket PII
  rule for an `initials` column alongside race/gender/age -- the weakest PII
  case seen in this batch and a reasonable overrule candidate.

## From the 2026-08-27 tier-A batch

- [x] **`biblio_tierA_2026-08-27.csv` (24 rows) imported into the dictionary**
  (confirmed 2026-08-27, ben-domingue) -- 889,761 responses across 24 tables
  from 16 deposits, all licenses verified CC BY 4.0 or CC0 1.0. The 24
  `irw_output/` CSVs were uploaded the same day and are off disk as expected.
  `livacicrojas_2023_lvq` was renamed from `..._2021_...` before upload; the
  deposit is dated 2023-12-27.

- [ ] **`10.5281/zenodo.1295642` (Gonzalez-Robles 2018) is deferred on its
  identifier.** Six instruments (OASIS, ODSIS, BAI, BDI, PANAS, QLI) and a real
  pre/post `wave` on OASIS, but `User` gives 428 distinct values over 583 rows
  and `(Study, User)` only 430 -- 153 rows share a person key with nothing in
  the file to say whether they are repeated administrations or a non-person
  identifier. Needs a human call or an email to the authors. Two isolated
  data-entry errors already located for whoever takes it: `BAI21pre` has one
  value of 13 on a 0-3 scale, `PANASR1pre` one value of 10 on a 1-5 scale.

- [ ] **`emiral_2025_aips`: ~110 more items available if four blocks can be
  named.** `PYAYT` (18), `TBO` (35), `TKO` (45) and `IBO` (12) are the study's
  convergent-validity measures; the Zenodo record has an empty description, no
  codebook, and the paper is paywalled. Hypothesis worth one check: `TKO` is
  the Basic Personality Traits Inventory -- 45 items, six factors, and its
  composite columns read as extraversion / conscientiousness / agreeableness /
  emotional instability / openness / negative valence. Not acted on.

- [ ] **`kumlander_2018_*` wave 2 is recoverable with a linking id.** The
  deposit's second file is a follow-up wave of the same cohort (n=1,497) with
  no respondent identifier in either file, so it could not be joined and was
  left out rather than shipped as ~1,497 fictitious extra people. An email to
  the authors asking for a linking id would add ~38k responses across the SCS
  and BDI tables.

## From the 2026-08-27 repo-mode discovery sweep (155 new terms, 6,048 candidates)

- [x] **Zenodo connector was returning an empty `url` for every hit** --
  fixed 2026-08-27 in `irw_discover_updated.py` (`from_zenodo`). Zenodo's
  InvenioRDM migration dropped `links["html"]`; the record page is now
  `links["self_html"]`. Reading the retired key gave every Zenodo Hit an
  empty url, so `resolve_data_files()` found no files and the candidate was
  retired as `no_tabular_file` without any resolver being called. **1,508
  rows -- 25% of the 2026-08-27 pool -- were zeroed this way**, and the
  same applies to every repo-mode run since the migration. The fix falls
  back to `links["html"]` and then to `https://zenodo.org/records/{id}`.

  **Still open: past runs under-reported Zenodo.** Any repo-mode batch in
  `BATCH_LOG.md` whose Zenodo rows all came back `no_usable_file` was
  measuring this bug, not the deposits. Worth re-running the Zenodo half of
  the recent term pools before concluding Zenodo is a low-yield surface.

- [x] **Dataverse resolver only ever reached Harvard** -- fixed 2026-08-27
  in `irw_batch_updated.py`. `_dataverse_files()` hardcoded
  `dataverse.harvard.edu`, so a SURF/DANS or Scholars Portal/Borealis
  persistentId was queried against Harvard (403), and `surf` /
  `scholars_portal` additionally matched no branch in `resolve_data_files()`
  at all -- falling through to `return [], "", []`, which is exactly the
  silent-empty-list failure the datacite comment above that dispatch warns
  about. 503 rows in this run. The resolver now derives the installation
  from the landing-page host, following the doi.org redirect when the URL is
  a bare DOI, and file-access URLs are built against the same instance.

- [x] **`.sav` encoding failures were being recorded as `download_failed`** --
  fixed 2026-08-27 in `irw_triage_updated.py` (`load_table`). `pyreadstat`
  trusts the header's declared encoding, and files written by localised SPSS
  builds routinely declare one they do not honour, dying with "Unable to
  convert string to the requested encoding (invalid byte sequence)". The file
  is fully downloaded and fine, but the exception reaches `process_one()`,
  which records `download_failed` -- a verdict indistinguishable from a dead
  URL. **19 of the 28 `download_failed` rows in the 2026-08-27 tier-A run were
  this**, all Spanish- or Turkish-language deposits, every one a real
  instrument. `load_table` now falls back to `pyreadstat.read_sav` with
  latin1/cp1252/utf-8; 19/19 parse after the fix.

  Third defect of the same class found this session, after the Zenodo and
  Dataverse connectors above: a real failure wearing a "nothing here" label.
  Worth a standing habit -- when a verdict means "no data", check that a
  resolver/reader actually ran.

- [ ] **Figshare 403s under concurrency.** A metadata-only pass at 8 threads
  drew 1,858 `403 Forbidden` responses from `api.figshare.com`; the same
  article ids return `200` when retried serially. These are throttle
  artifacts, not dead records -- but note `polite_get()`'s per-domain delay
  does not apply to the resolver helpers, which call `requests.get` directly.
  Any parallel driver over `resolve_data_files()` needs its own backoff, or
  the rate limiting should move into the resolvers.

## From the 2026-08-27 table-name audit (issue #1686)

Evidence: `naming_audit_suspects.csv` + `naming_audit_README.md`. The audit is
complete and the attribution errors are fixed. **Renaming the 15 remaining
mis-named tables was considered and declined** (see #1686) -- do not queue it, and
do not treat the CSV's `proposed_name` column as a work list.

- [ ] **Add a naming gate to the pipeline.** At the point the pipeline picks a
  table name, resolve the DOI and require the chosen surname to appear in the
  resolved author list; refuse to name the table otherwise. This would have caught
  all 16 bad names, and it costs nothing at creation time, when nothing else
  references the name yet -- which is why enforcing the convention forward is cheap
  and enforcing it backward is not. **Proposed only; Ben to schedule -- do not
  implement unprompted.** Two carve-outs are mandatory, both of which produced real
  false positives during the audit:
  - Compound and particled surnames. Matching only the Crossref `family` field
    falsely flags `van Teffelen`, `Lopes de Jesus`, `Makowska-Tlomak`, `von Hippel`
    and ~35 others. Match every contiguous run of surname words joined without
    separators, absorb trailing nobiliary particles from `given`, and map Turkish
    dotless `i` explicitly -- it has no NFKD decomposition.
  - Dataverse lists only the depositor. `cavojova_2017_cfc` and `cosenza_2015_cfc`
    look fabricated against the creator list but are correct per the record's
    linked publication. A gate reading only creators will produce confident false
    accusations.

- [ ] **Make script headers record the resolved author list alongside `DOI:`.**
  The cheap half of the fix and probably the highest value per line: every
  fabrication traced to commit `b830262`, whose scripts record `Source:`, `DOI:`
  and `License:` but **no author field at all**, so the naming step had nothing to
  read and supplied a surname from nothing. Worth doing regardless of whether the
  gate above is scheduled.

- [ ] **Open a separate issue for `DOI (for paper)` column hygiene.** This is a
  distinct defect from naming and does not belong on #1686. Across the 1,945
  automated rows: **465 hold a dataset DOI** (figshare, Mendeley, Dataverse, OSF,
  Zenodo, Dryad) in a column meant for the paper DOI, which is what drives roughly
  55 spurious year mismatches -- the deposit year is not the paper year. Alongside:
  33 full URLs, 22 cells prefixed `data doi: `, 10 PLOS `.sNNN` supplement
  suffixes, 4 reading `not yet published`, and 2 cramming several DOIs plus
  free-text notes into one cell.

- [ ] **Six tables could not be name-checked at all** -- no DOI in the sheet and
  the DOI implied by their URL is not registered with Crossref or DataCite, so
  these are unverified rather than clean: `marquezpalacios_2026_bdi2`,
  `opladen2025_edeq`, `opladen2025_wi`, `opladen2025_fkg`, `opladen2025_fks`,
  `schoepp2022_test_anxiety`. Low priority.

## From the 2026-08-26 weekly PMC sweep review (BATCH_LOG.md, same date)

- [x] **`biblio_tang_2024_2026-08-26.tsv` (13 rows) pasted into the dictionary
  sheet** (confirmed 2026-08-26, ben-domingue) -- 147,535 responses across 13
  tables from one CC BY *Scientific Reports* deposit
  (`10.1038/s41598-024-63589-5`), rescued from a false `below_min_n` skip.
  The 13 `irw_output/` CSVs written by `data/tang_2024_migrant_children.py`
  were uploaded the same day (confirmed 2026-08-26, ben-domingue); the staged
  TSV and CSVs are gone from disk accordingly.

- [ ] **Triage fix: `density >> 1` falsifies a `below_min_n` verdict.**
  The Tang 2024 row was skipped as "only 7 distinct respondents" while
  carrying density 238.3 in the same row -- which can only mean the id column
  was misidentified (that deposit has no id column at all, so the heuristic
  fell back on a 7-category demographic). Density is already computed for
  every candidate, so this is a one-line guard in the `below_min_n` branch of
  `irw_triage_updated.py`: when density is far above 1, the verdict is
  "misidentified id", not "too small", and the row belongs in
  `human_review/` rather than being dropped with "no human review needed".

- [ ] **Name `CCCLIT` in the Tang 2024 deposit, or confirm dropping it.**
  A 4-item 1-5 block (~6,700 responses) alongside the caregiver-child
  attachment/conflict/communication/regulation blocks. By elimination it
  should be the paper's caregiver-child *co-activity* variable -- that is the
  only named family-relationship construct left unaccounted for -- but the
  abbreviation does not support that reading and the paper publishes no item
  table for it, so it was held rather than named on a guess. Everything else
  in the deposit is shipped.

- [x] **`10.7717/peerj.21420` resolved as a SKIP** (2026-08-27). The
  header-offset diagnosis recorded here was wrong: all five sheets of
  `peerj-14-21420-s001.xlsx` are aggregate contingency tables (counts,
  percentages, Yates chi-square), with no per-respondent row anywhere, so no
  `id` column can exist. Not recoverable -- the data was never published at
  the respondent level.

## From the 2026-08-25 system audit (see BATCH_LOG.md for evidence)

- [x] **`biblio_mendeley_2026-08-26.tsv` (17 rows) uploaded/pasted**
  (confirmed 2026-08-26, ben-domingue) — 56,383 responses across 17 tables
  from 5 Mendeley deposits, all CC BY 4.0. Verified against the live sheet:
  all 17 present exactly once at 14 fields, alignment spot-checked. The TSV
  and the `irw_output/` CSVs are off disk as expected. See the Mendeley entry
  in `BATCH_LOG.md` for the per-deposit coding decisions.

- [x] **`mendeley_leads_2026-08-26.csv` (31 leads) worked** (2026-08-27):
  23 deposits -> 121 tables / 758,832 responses, 5 skipped, 3 deferred (below).
  See the 2026-08-27 entry in `BATCH_LOG.md`. Note `zktjjx93sv`, listed here
  as the largest lead, turned out to be PII-blocked (real mobile numbers and
  respondent names) and was skipped entirely.

- [x] **The 121 `irw_output/` CSVs are uploaded** (confirmed 2026-08-27,
  ben-domingue). 758,832 responses across 23 Mendeley deposits, all CC BY 4.0.
  The CSVs are off disk as expected.

- [x] **`biblio_mendeley_batch_2026-08-27.csv` (121 rows) uploaded/pasted**
  (confirmed 2026-08-27, ben-domingue). Verified against the live dictionary
  tab: all 121 rows present, contiguous at sheet rows 4022-4142, 14 columns
  each, no duplicates, and zero field mismatches across 1,694 cells. Landed
  via **File > Import > Append to current sheet**, comma-separated -- the
  `.tsv` paste path misaligned because the three mandated blank columns become
  consecutive tabs that Sheets collapses. See `BATCH_LOG.md` and the corrected
  lesson in the skill's SKILL.md. The file itself is deleted -- biblio files
  are not kept once their rows are on the sheet (ben-domingue, 2026-08-27),
  which matches the history: every past `biblio_*` file was added and later
  removed, and none are tracked today.

  If this ever needs regenerating: `irw_output/` is emptied on upload, and the
  row counts in the Description column are computed from those CSVs -- re-run
  the 23 `data/*.py` scripts first (all verified reproducible 2026-08-27) and
  assert the file count before writing.

- [ ] **Three Mendeley deposits deferred, each for a specific reason**
  (2026-08-27, all CC BY 4.0, all downloadable):
  - `10.17632/4n5x4ffzn5` (Javanese marital quality, 840x111) -- the workbook
    has four sections (Bagian I-IV) with subtotal ("T") columns and unnamed
    blocks interspersed between the item columns, plus a stray section-label
    row 0 and `?` as a missing code. Shipping it needs the instrument or the
    paper to tell items from subtotals; guessing risks shipping subtotals as
    items.
  - `10.17632/mrrc83rt3b` (Indian healthcare-worker wellbeing, 240x60) --
    three coherent text-Likert blocks (a 9-item UWES-shaped engagement scale,
    an 8-item COVID-stress scale, a numeric job-affect block). Blocked on
    category ORDER: one block offers both "Rare" and "Less than a day or two"
    as distinct options in the same column (39 vs 4 responses), and whether
    those are the same rank or adjacent ranks is not inferable from the data.
    Needs the paper's Methods. Checked for PII -- clean.
  - `10.17632/ry2dvfydjd` (Integrated Palliative care Outcome Scale Rasch
    analysis, 300 rows / 260 distinct patients) -- repeated measures whose
    wave structure needs the paper, and it carries a `DOA` admission-date
    column alongside age and 29-category diagnosis. Not PII by the letter of
    the rule (no name/email/DOB/GPS/ID), but worth a human look before
    shipping a palliative-care cohort.

- [ ] **`10.17632/h3yhs5gy3w` is a nominal-standard candidate, not core**
  (Myszkowski & Storme 2018, "A snapshot of g?", 499x12, CC BY). The SPM
  items are option-coded 1..8 -- which distractor the respondent chose, not
  an ordinal rating -- so they belong in the nominal standard, or in core
  once scored against an answer key. The key is not in the deposit. Deliberately
  NOT shipped to core in the 2026-08-27 batch.

- [ ] **Lead CSVs have no "worked" marker, so shipped datasets keep getting
  recommended.** On 2026-08-27 the daily nudge routine recommended
  `10.7910/dvn/terjak` as the day's best lead; it had already shipped on
  2026-08-26 as mailing #13 of `data/goldberg_2018_escs.py`. The dedup
  practice exists (`grep -rli <key> ../data/*.py`) but nothing writes the
  result back, so every consumer of the lead CSVs re-derives it or, like the
  nudge, skips it. Options: a `worked` column written back after each batch,
  or have the nudge run the grep itself before recommending.

- [x] **`10.17632/hwp4wsb549` empty-file-listing problem is gone**
  (2026-08-27). The Mendeley public API now returns both files
  (`TEZ_412VERI.xlsx`, `TEZ_VERI_UNI.csv`) without trouble. Shipped as
  `data/celik_2026_motivation_distance_ed.py` -- 6 tables / 81,220 responses
  across two samples (AMS-28, distance-ed-26, TIPI-10 on 412 respondents;
  BFI-44, distance-ed-16, BPNS-24 on 653). The CSV is semicolon-delimited,
  which is why a default read produced a 653x12 mess.

- [x] **A biblio paste can fail for reasons not visible in the file.**
  On 2026-08-26 the 55-row combined biblio failed to paste repeatedly while
  being verifiably well-formed; it went in after two speculative content
  changes and the mechanism was never established. — **closed 2026-08-26
  (ben-domingue): "don't worry about the paste issue, it is working ok now."**
  Both subsequent pastes (55 rows, then 17) went in clean first time. Not
  investigated further. The per-field discipline the files are now written to
  is recorded in `SKILL.md` and costs nothing to keep: ASCII, no tab, CR,
  newline or double quote in any field, no leading `=`/`+`/`-`/`@`/`'`.

- [ ] **Decide whether Qualtrics geo-IP coordinates count as PII**
  (`10.7910/DVN/JC6F9O`, Hemesath & Tepe 2025, CC0). The export carries
  `LocationLatitude`/`LocationLongitude` at 4 decimal places for every row.
  It was skipped whole under `feedback_pii_skip_entirely`, which was written
  about names and emails; if coarse geo-IP coordinates are acceptable to drop
  rather than disqualifying, the deposit is worth about 132,000 responses
  (the 20-item GAAIS x 6,620 rows, though only 4,156 `ResponseId`s are
  distinct so the duplication needs sorting out first). Not decided
  unilaterally.

- [ ] **The education profile's `thin`/`not_instrument` tail is unworked.**
  All 36 `instrument` rows of `runs/edu_work_profile_2026-08-26.csv` have now
  been adjudicated (30 shipped or skipped this pass, 6 previously). The other
  38 rows were never opened.

- [ ] **Dryad downloads are blocked; decide what to do about it** (found
  2026-08-26). `_dryad_files()` lists versions and files fine, but
  `/api/v2/files/{id}/download` returns 401 and `/downloads/file_stream/{id}`
  returns a JS bot-challenge page. Dryad is one of the eight default sources,
  so every Dryad candidate ever downloaded has failed this way and been
  retried forever as a transient `download_failed`. Options: drop dryad from
  `DEFAULT_SOURCES`, get an API token, or route it through DataCite's
  backfill the way blocked publishers already are. Related: the same retry
  batch showed 13 figshare S3 404s (files genuinely gone) and 13
  Dataverse 401/403/400s -- neither is retryable either, so
  `download_failed` needs a terminal sibling for "access denied / file gone"
  rather than sending them round the retry loop. That is the same gap as the
  older Dataverse-restrictions item below.

- [x] **`biblio_nominal_2026-08-26.tsv` (2 rows) pasted into the nominal sheet**
  (confirmed 2026-08-26, ben-domingue): `goldberg_2018_spa_computer_use`
  (709 x 2, categories A-L) and `mthimkhulu_2023_pirls_reading_mc`
  (1,680 x 4, categories A-D). Pasted from **TSV** after the CSV would not
  split — see the BATCH_LOG correction; hand over TSV for every biblio from
  now on. Biblio file and both `output_noncore/`
  CSVs removed by ben-domingue on upload — `output_noncore/` follows the same
  clear-on-upload pattern as `irw_output/`, so nothing further is pending.

- [ ] **`germann_2026_*` tables have colliding `id`s** — tracked in
  [#1683](https://github.com/ben-domingue/irw/issues/1683) (`data fix`).
  Found 2026-08-26 by `irw_lint_covariates.py`, the first thing it caught on
  real output. 30,072 of 228,070 rows in `germann_2026_immigration.csv` are
  duplicate `(id, wave, item)` keys. Root cause: the raw file carries both
  `newid` (unique across all 76,466 rows) and `id`, and
  `data/germann_2026_terrorism.py` uses `id`, which restarts from 1 in each
  of the three country samples — `newid = region * 100000 + id`, region
  1/2/3 = England/Scotland/Wales. Melting on `newid` gives 0 duplicate keys
  and 0 covariates varying within a person. Same issue also establishes that
  `wave` is wrong here: every respondent appears exactly once, so pre/during/
  post separates different people (a natural experiment), not timepoints —
  it belongs in `cov_*` or `treat`. Corrected N is 76,466, not the ≈53k
  recorded in `BATCH_LOG.md`.

- [x] **`biblio_batch_2026-08-26.csv` (3 rows) uploaded/pasted** (confirmed
  2026-08-26, ben-domingue): 67,592 responses —
  `trang_2023_vocabulary_beliefs` / `_strategies` (Gu's Vocabulary Learning
  Questionnaire, 722 Vietnamese EFL learners, the first thing the
  educational-measurement term gap produced) and `sirventruiz_2025_pdat` (the
  26-item PDAT, repeated measures with a `wave` column). Staged CSV and
  `irw_output/` files off disk as expected.

- [x] **`biblio_batch_2026-08-25c.csv` (40 rows) uploaded/pasted** (confirmed
  2026-08-25, ben-domingue): 187,097 responses across 40 tables from 13
  deposits — `wang_2025_*` (4), `senyurt_2023_burnout`,
  `sokolovskii_2021_tfeq`, `doherty_2023_*` (3), `daderman_2023_naqr`,
  `chen_2026_*` (3), `eldor_2022_*` (9), `milson_2026_*` (3),
  `kermen_2022_*` (4), `gan_2024_*` (2), `peng_2024_*` (3),
  `rosyid_2025_*` (3), `dalichaouche_2026_*` (3). All CC BY 4.0 or CC0 1.0,
  none previously seen by any discovery run. The staged CSV and the
  `irw_output/` files are off disk as expected. See the five "worklist pass"
  entries in `BATCH_LOG.md` for the per-deposit coding decisions.

- [x] **Decide what to do about the scheduled cloud runs.** Throughput fell
  from ~26 new `data/*.py` scripts/day (2026-07-26..08-13, manual batches) to
  ~1.4/day (08-14..08-25, scheduled runs) — an 18x drop. The bugs behind each
  individual run are now fixed, but two design problems are not: a scheduled
  run surfaces candidates into a PR and stops, with nobody reviewing the
  `good`+`worth_retrying` pool (which is where all the manual-batch yield
  came from); and the weekly runs re-search the same 15 high-yield terms
  behind a seen-DOI ledger, so they are mined out by construction. Options:
  fold a "review the pool" step into the routine prompt, rotate the weekly
  term list, or drop the weekly cadence and run monthly full sweeps only.
  This is a ben-domingue call, not a code fix. — **decided 2026-08-25 (ben-domingue): keep the routines as discovery+triage and work the pools locally.** The processing step stays with a person, because that is what produced ~26 scripts/day. Done as part of the decision: a daily nudge routine `IRW daily search nudge` (`trig_014YcLgR2Sa2D8P2yAkvQFTx`, cron `0 15 * * *` = 8am PT, read-only) now reads `TODO.md` and the two leads CSVs each morning and names one concrete thing to work; and the two runaway PR-watcher one-offs on #1676 / #1681 (`trig_01UfLcQ11WAtgNEgyR6Yp5WF`, `trig_0184pheJDQbsY8tBE1uPkY7S`) were disabled — they had been re-arming hourly since 2026-08-24 against PRs an agent is told never to merge.
- [ ] **Thin the standing weekly discovery routines** — follow-on from the decision
  above. The weekly repos/PLOS/PMC routines re-search the same 15 `HIGH_YIELD_TERMS`
  behind a seen-DOI ledger, so they are mined out by construction; and the monthly
  sweeps want a higher `--limit` (or explicit `--per-term-cap 3-5`) now that
  `TERM_LIST` is 125 terms. **Blocked on routine IDs**: the `RemoteTrigger` `list`
  action returns only the newest page and this tool exposes no cursor for it, so the
  standing routines (created ~2026-08-13/14) are unreachable from here. Get their IDs
  from https://claude.ai/code/routines and hand them over, or edit them there.
- [ ] **The monthly routines' `--limit 150` is now spread across 125 terms.**
  `per_term_cap = max(1, limit // len(terms))`, so each term gets exactly 1
  candidate — it was already 1 at 100 terms, so this is not a regression, but
  a 125-term sweep at `--limit 150` is very broad and very shallow. If the
  education terms are to get a fair test, the monthly PLOS/PMC/repos routines
  want a higher `--limit` (or `--per-term-cap 3-5` explicitly). That is a
  change to the cloud routine prompts, not to the code, so it needs
  ben-domingue. Folds into the scheduled-runs decision above.
- [ ] **Re-run the ~1,215 non-Latin-script repo terms under the fixed
  relevance filter.** They were all run under an English-only title gate that
  discarded essentially every non-English-titled hit before triage (fixed
  2026-08-25). Same shape as the 2026-07-15 English alt-format re-discovery.
  A 45-term pilot is running as
  `runs/candidates_nonlatin_pilot_2026-08-25.csv` — size the payoff from that
  before committing to all 1,215. The Spanish/German/French/Dutch terms were
  affected too and are not in that 1,215 count. **Decided 2026-08-25 (ben-domingue): size it with the pilot first, then decide** — same justification path as the 2026-07-15 English alt-format re-discovery (575 terms re-run, 186 previously-invisible candidates, 21 new tables). The 45-term pilot is queued behind the education sweep and writes to `runs/candidates_nonlatin_pilot_2026-08-25.csv`; compare its per-term candidate rate against those same terms' original rows in `search_terms_log.csv` to get the recovery rate, then judge the remaining ~1,170. Note the ~1,215 figure counts only non-Latin-script terms — the Spanish/German/French/Dutch ones hit the same bug and are a further pool on top.
- [ ] **Work the 1,983 candidates just un-blocked from
  `googlesheet_humaneye.csv`.** Of its 4,833 rows only 31 were ever
  adjudicated; the rest were being excluded from every discovery run as
  though they had been. A first cut — cleanly-parsing, explicit open
  license, N>=100, >=3 items — is 173 unique candidates, triaged as
  `runs/triage_backlog_recovered_2026-08-25.csv`. That filter is
  conservative (it drops every row whose columns are shifted by the Sheets
  export, and every row with no N recorded), so there is more in there.

- [x] **43 actionable leads from the recovered backlog** —
  `backlog_recovered_leads_2026-08-25.csv` (3 good + 40 worth_retrying from
  the 173 candidates un-blocked from `googlesheet_humaneye.csv`). Largest:
  `dvn/rwpomi` (12,622 x 11, CC0), `dvn/me8oji` (1,646 x 42, CC0),
  `dvn/xpuru1` (1,201 x 39, CC BY), `dvn/l6g8ul` (1,067 x 46, CC0),
  `dvn/7cyiqg` (199 x 256, CC0). All three `good` rows were already checked
  by hand and none shipped — see the BATCH_LOG entry. — **worked 2026-08-25**: re-ranked by instrument shape into `lead_worklist_2026-08-25.csv` (69 leads: 25 instrument, 35 thin, 8 PII, 1 no_usable_file), then processed top-down. **40 tables / 187,097 responses shipped from 13 deposits**, all CC BY/CC0, none previously seen by any run. See the five worklist passes in `BATCH_LOG.md`. What remains of the 69 is the `thin` tail plus the four items below.
- [ ] **Three deposits that need the paper before they can ship** (all
  2026-08-25, all CC BY, all structurally strong — see `BATCH_LOG.md` for the
  full reasoning):
  - `10.17632/nr9388gbzf` — 700 respondents x ~241 columns of clean ordinal
    blocks (AQ×28, GQ×27, IQ×19, FQ×18, HQ×15, OQ×15, BQ×14, CQ×14, KQ×13) with
    a real `id` and full demographics. No variable labels, no codebook, and the
    reconstruct-the-derived-score trick does not apply (no composites shipped),
    so the letter prefixes decode to nothing. The paper would unlock ~9 tables.
  - `10.17632/fkyw9v8yj2` (= `nfzwfhw4k4`, byte-identical) — Rosenberg items
    on a labelled 5-point scale whose midpoint ("fair") occurs **zero times in
    2,870 responses**. Unexplained recode; the derived `selfesteem` column is
    neither the sum nor the rounded mean, so it gives no way in.
  - `10.3389/fendo.2024.1390564`'s `社` social-support block — 32 columns
    mixing 1-4 Likert items with 0/1 multi-select checkbox options (three of
    them constant 0). Needs the instrument to split correctly. The other two
    blocks from this deposit shipped.

- [ ] **`10.17632/kh5zvysyph` (visual-spatial ability, 128 x 239, CC BY) is
  probably trials data, not item responses** — its blocks are `MR*_ACC`,
  `OUT_MR*_ACC`, `Out_MC_ACC`, i.e. per-trial accuracy on mental-rotation
  tasks. `datastandard.md` handles trials-based data differently from an item
  battery; decide which shape applies before writing anything. Relevant to the
  educational-measurement gap (spatial ability), so worth the look.

- [ ] **The `thin` tail of `lead_worklist_2026-08-25.csv`** — 35 leads scored
  as having no item block of 5+ columns. Some are genuinely not item-response
  data; some are small real scales the scorer's threshold missed. Worth one
  sweep at a lower threshold before the file is considered worked.
- [ ] **Decide: is `10.7910/dvn/1ufrud` (trolley problem, CC0) IRW-eligible?**
  1,597 respondents x ~4 vignettes, `flip` 0/1, already long. The catch is
  that the vignette is a *crossing* of one-track victim type x five-track
  victim type (exactly two of nine dummies are 1 per row), so an "item"
  would be a cell of a factorial experimental manipulation — ~21 cells,
  density ~0.2 — rather than an item of a validated battery. Same judgment
  class as the rejected `carus_2021_snowboard_speed`. If it counts, the
  script is easy; if it does not, this is a `treat`-column study, not an
  IRW table. Not guessed at.

- [x] **Raw Google Forms exports are a recurring PII risk the `good` flag
  cannot see.** Both doomscrolling deposits
  (`figshare.29857874`, `figshare.28979105`) triaged `good` and both carry a
  `Respondent's Name (Real Name/Initial)` column of actual given names plus
  second-precision timestamps. Skipped per
  `feedback_pii_skip_entirely`. Worth considering a triage-time warning when
  a column name matches `name|email|phone|address|birth` so these surface as
  something other than `good`. — **fixed 2026-08-25**: `screen_for_pii()` plus the terminal `pii_suspected` flag now run ahead of every other verdict in `triage_dataset()`. See the BATCH_LOG entry for the two-tier design and the 24/27 verification.

- [x] **Build a Mendeley Data discovery connector.** — **done 2026-08-26**:
  `from_mendeley()` is in `SOURCES`, reaching Mendeley through DataCite's
  index of prefix `10.17632`. It dedupes Mendeley's versioned DOIs
  (`<base>.1`) to the base, is in `_DATACITE_SKIP` so the generic sweep stops
  duplicating it, and is in `_DATACITE_FALLBACK_FOR` so the skip lifts if it
  blocks. Measured on 7 terms: 123 unique candidates, 114 triaged, **31
  actionable (27%)** — higher than the 22% that justified building it. The
  26 standing leads were worked first, as this item required: 17 tables /
  56,383 responses shipped from 5 deposits.

- [x] **Add educational-measurement terms to
  `irw_discover_monthly.py`'s `TERM_LIST`.** It is ~100 terms of self-report
  psychology with six executive-function tasks and nothing else on ability
  or achievement. Zero queries have ever been run, in any mode, for `rasch`,
  `item bank`, `concept inventory`, `spelling test`, `listening
  comprehension`, `knowledge test`, `student assessment`, `classroom
  assessment`, `essay scoring`, `spatial ability`, `reasoning test`,
  `science achievement`, `literacy assessment`, `multiple choice exam`,
  `IPIP`, `SDQ`, `schwartz values`, `emotion recognition`. The 20-term
  English set used for the 2026-08-25 one-off runs is a ready starting list. — **done 2026-08-25**: 25 terms added to `irw_discover_monthly.py`'s `TERM_LIST` (100 -> 125), which `irw_discover_plos_monthly.py` and `irw_discover_pmc_monthly.py` both import as `FULL_TERM_LIST`, so one edit covers all three monthly sweeps. Deliberately NOT added to `HIGH_YIELD_TERMS` (the weekly subset): per the same discipline the SKILL applies to journals, a term earns that list with a measured yield, and the one-off PLOS education run (26 `human_assistance` from 300 candidates) is about par, not proven high-yield.

- [ ] **Review the education-gap runs' output.** PLOS mode gave 8
  `worth_retrying` (`runs/plos_edu_retriage_ha_2026-08-25.csv`) and 5
  `human_review` (archived). Repo mode and PMC mode were still running when
  the audit was written — `runs/candidates_edu_2026-08-25.csv` needs a Step 2
  triage, `runs/pmc_edu_2026-08-25.csv` a Step 2b.

- [x] **`biblio_batch_2026-08-25b.csv` (8 rows) needs uploading/pasting** —
  `alexandrowicz_2018_cesd`, the six `sumner_2022_*` tables, and
  `altman_2020_capq`. 365,409 responses. See the BATCH_LOG entry for the
  per-table coding decisions. — **uploaded/pasted, confirmed 2026-08-25 (ben-domingue)**: the 8 tables (`alexandrowicz_2018_cesd`, six `sumner_2022_*`, `altman_2020_capq`), 365,409 responses. `biblio_batch_2026-08-25b.csv` and the `irw_output/*.csv` files are off disk as expected. `altman_2020_capq` shipped with all 19 items including the three above 93% zeros (`CAPQ6`, `CAPQ8`, `CAPQ10`) — the floor effect is a real property of a problems checklist and all six categories are used on every item.
- [ ] **Item text is cheap for two of the new tables.** `altman_2020_capq`:
  the .sav's variable labels are the full CAPQ item stems and the item ids
  are the source column names, so they join directly. `sumner_2022_*`: the
  source labels are positional ("FTD-SS Item 1"), so those need the
  published instruments instead.

- [ ] **`AMBIGUOUS_TERMS` in `irw_discover_updated.py` is dead code** — the
  relevance-filter header documents it as a tier ("ambiguous terms do NOT
  pass on their own, they only add confidence"), but nothing references it.
  Either implement the tier or delete the list and the paragraph.

- [x] **Cloud routine sandbox is missing `openpyxl` and `pyreadstat`
  (fixed in-repo 2026-08-25)** — `preflight_deps()` added to
  `irw_triage_updated.py` and called as the first statement of `main()` in
  all 8 entry points: it auto-installs the missing readers and aborts the
  run if they are still absent, so a bare sandbox can no longer produce a
  quiet all-`download_failed` result that burns DOIs in the seen ledger.
  Documented in `SKILL.md`'s Prerequisites. Original diagnosis: 10 of
  the 12 `download_failed` rows in the weekly PLOS run (`b9a2fe5`) were
  purely `Import pyreadstat failed` / `Import openpyxl failed`, and one of
  them (`pone.0235154`) is a strong multi-scale candidate. Every scheduled
  cloud run silently drops `.sav`/`.xlsx` Supporting Information this way,
  and the DOIs get written to `plos_seen_dois.csv`, making the false
  negative permanent. Fix: add
  `pip3 install --user --break-system-packages pandas openpyxl pyreadstat pyreadr`
  (or the equivalent env setup) to the routine prompts for all PLOS/PMC/repo
  jobs, and have them assert `python3 -c "import pandas, openpyxl, pyreadstat, pyreadr"`
  before Step 2. Until then, `download_failed` rows from cloud runs need a
  local re-triage pass.

- [ ] **`irw_process_queue.py` is broken on `main`** (found 2026-08-25, not
  caused by that day's changes): it imports `QUEUE_SHEET_URL` from
  `irw_discover_updated.py`, which no longer defines it — the module fails at
  import, so `--help` doesn't even run. Presumably fallout from retiring the
  human-review queue sheet (2026-08-12). Either repoint it at the
  `human_review/*.csv` files or delete the script.

- [x] **`pone.0235154` (medical-student burnout, HK, CC BY) processed
  2026-08-25** — `data/lee_2020_medical_students.py`, 5 tables / 44,941
  responses. See the BATCH_LOG entry for the coding decisions.

- [x] **`biblio_batch_2026-08-25.csv` (5 rows) uploaded/pasted** (confirmed
  2026-08-25, ben-domingue): the 5 `lee_2020_*` tables, 44,941 responses.
  `biblio_batch_2026-08-25.csv` and the `irw_output/lee_2020_*.csv` removed
  from disk.

- [ ] **Item text for the 5 `lee_2020_*` tables** — unusually cheap here: the
  `.sav`'s SPSS variable labels carry the full item stem for every item and the
  value labels carry every response option, so no transcription from the PDF is
  needed. Item ids in the tables (`MBI_1`, `JPSE_1`, `DUSOCS_1`, `PSQI_5A`,
  `Drinking_habit_1`, ...) are the source column names, so they join directly.

- [ ] **`pone.0356791` (young Chinese physicians, N=504 x 69) worth a look** —
  parsed cleanly on the 2026-08-25 re-triage. Note its `S1_File` is captioned
  `(XLSX)` but `.s001` is actually a `.docx`; the real table is a different
  supplement id.

- [x] **3 IRW-eligible datasets recovered from the 2026-08-18..20 scheduled
  runs' `human_assistance` bucket (2026-08-24)** — all three processed the
  same day: `data/gao_2022_covid_stress.py` (PLOS ONE, CC BY, N=1087 → 4
  tables), `data/ren_2024_rural_elderly.py` (Sci Rep, CC BY, N=1587 → 5
  tables), `data/abramson_2026_diaspora.py` (Harvard Dataverse, CC0,
  N=1706 across 2 waves → 4 tables). 13 tables, ~181k responses.

- [x] **`biblio_batch_2026-08-24.csv` (13 rows) uploaded/pasted** (confirmed
  2026-08-24, ben-domingue): the 13 tables from `gao_2022_covid_stress.py`,
  `ren_2024_rural_elderly.py` and `abramson_2026_diaspora.py`, ~181k
  responses. `biblio_batch_2026-08-24.csv` and the `irw_output/` CSVs
  removed from disk. See `BATCH_LOG.md`'s "Step 3 for the three recovered
  datasets" entry.

- [ ] **Item text available for the 4 `gao_2022_*` tables**: the S1 Dataset's
  own column headers are the full Chinese item stems for all 69 items
  (PSS-10, the 28-item stress-response scale, SCSQ, ERQ), and the script's
  positional item numbering (`PSS_1`, `SRQ_1`, ...) follows the numbering
  embedded in those stems, so they join directly on `item`. No PDF parsing
  needed -- worth an `irw-auto-itemtext` pass, including the translated
  text. `ren_2024_*` and `abramson_2026_*` have no comparable in-deposit
  text (Ren ships bare codes like `c65b`; Abramson's README gives only
  short variable descriptions, with full wording in the paper appendix).

- [ ] **4 `human_review` rows from the 2026-08-24 weekly repos re-triage**
  (`human_review/human_review_repo_2026-08-24.csv`): three Mendeley
  deposits (`6by7h52sfg` nurse personality/burnout, `mrcthr8nxf` bedtime
  procrastination/PERMA, `j33ytz7wsx` EFL self-efficacy/anxiety) and one
  Taylor & Francis figshare deposit (article 33307366, ISO 9001 /
  national customer satisfaction). All four resolved to a real tabular
  file; none sub-classified automatically.

- [ ] **`osf.io/47bhk` is the run's only `good` row but has no license**
  (2026-08-24, filed as issue #1678): "Sports Club Membership Value, Satisfaction, Engagement
  and Well-being Dataset (China, 2021)", N=410 x 40 items, 16,400
  responses, density 1.0 — clean, and the largest thing the weekly run
  surfaced. The OSF node is public but `node_license` is null, so under
  the standing rule it cannot be processed. Author email
  (`processing_notes/Licensing.txt` template) is the only way forward.
  Note the triage flag: `license_unknown` is recorded as a soft note in
  `reasons`, not a hard gate, so a `good` row can still be unusable —
  always read the `license` column before queueing.

- [x] **DataCite emits one candidate per DOI version, so datasets triage
  2-3x** (2026-08-24): `10.17632/j33ytz7wsx` and `10.17632/j33ytz7wsx.1`
  are the same Mendeley deposit and each got downloaded and triaged
  separately; the 23 `human_assistance` rows in the weekly re-triage
  collapse to ~9 unique datasets, and 9 `human_review` rows to 4. Worth
  collapsing version suffixes in `irw_discover_updated.py`'s dedupe (and
  in `_key()`) before the next weekly run. — **fixed 2026-08-25**: `canonical_doi()` in `irw_discover_updated.py` collapses Mendeley/figshare/Dryad version suffixes, used by `_key()`, `load_seen_keys()` and the discovery dedupe. Scoped to those prefixes so PLOS-style DOIs ending in `.digits` are untouched.

- [ ] **Mendeley `.zip`-only deposits are still `no_usable_file`**
  (2026-08-24): 6 of the 41 remaining `no_usable_file` rows are Mendeley
  deposits whose only payload is a `.zip` (e.g. `vb5rz5y7x8`,
  `Datasets_Final_040426.zip`). `TABULAR_EXT` has no archive handling
  anywhere in the pipeline; a peek-inside-the-zip resolver would be a
  general win, not a Mendeley-specific one.

- [ ] **`10.1371/journal.pone.0242267` needs a delimiter re-read
  (2026-08-24)**: `S1_Dataset.csv` parsed as one column whose header is
  the tab-joined string `id\tI1\tI2\t...ES1..A1..`. That is a read
  problem, not a content problem — re-read with `sep='\t'` and re-triage.
  Filed as `human_review` in `human_review/human_review_plos_batch30.csv`
  along with `10.1371/journal.pone.0313538`, which still needs eyes.

- [ ] **`download_failed` should not swallow Dataverse access restrictions
  (2026-08-24)**: both `download_failed` rows from the 2026-08-20 repos
  sweep (`DVN/7P3PFB`, `DVN/FG3CCK`) are permanently restricted files, not
  transient errors, so they sit in a retry bucket that will never resolve.
  `_dataverse_files()` in `irw_batch_updated.py` already sees the
  `restricted` field on each file record — flag those at resolve time.

- [x] **`biblio_issue233.csv` (20 rows) uploaded/pasted** (confirmed
  2026-08-18, ben-domingue): GitHub issue #233, Harvard Dataverse
  `DVN/QOO7QX` "PROMIS Pediatric Measure Evaluation" (CC0 1.0). Ten PROMIS
  pediatric item banks x child-report/parent-proxy editions = 20 tables,
  ~1.38M responses, from `data/forrest_2021_promis_peds.py`.
  `biblio_issue233.csv` and the `irw_output/` CSVs removed from disk. See
  `BATCH_LOG.md`'s "GitHub issue #233" entry.

- [ ] **Item text available for all 20 `forrest_2021_*` tables**: the
  `DVN/QOO7QX` deposit ships 20 codebook PDFs (plus `MySQLWorkbench.pdf`,
  which covers the proxy global-health items) carrying the full stem and
  every response-option label for each bank. Item names were kept in source
  form specifically so they join. Worth an `irw-auto-itemtext` pass now that
  the tables are up.

- [x] **`biblio_issue1562.csv` (1 row) uploaded/pasted** (confirmed
  2026-08-18, ben-domingue): GitHub issue #1562 resolved as a mostly-
  duplicate deposit (its HEXACO-24 block shipped 2026-08-01 as
  `dasilva_2019_hexaco24`); its unshipped CRT block shipped as
  `dasilva_2019_crt` — 3 items, 211 respondents, ids joinable to the
  HEXACO table. `biblio_issue1562.csv` and the `irw_output/` CSV removed
  from disk. See `BATCH_LOG.md`'s "GitHub issue #1562" entry.

- [ ] **2 unresolved leads from the PMC backlog-sweep retriage
  (2026-08-16, dangling commit `3167335c`)**: `10.7717/peerj.20180` (TRX
  suspension training study) and `10.7717/peerj.18241` (parental thermal
  conditions/alarm calls study) both have text-coded Likert item columns
  ("Strongly Agree" etc., not numeric codes) and unknown N -- need the
  file downloaded, N checked against the >=100 floor, and the standard
  text-Likert-value recode before a go/no-go call can be made.
- [ ] **1 unresolved `aggregate_continuous` lead**:
  `10.1038/s41598-023-42115-z` ("On the (number of) aversive traits...",
  N=151, 17 cols) -- >50 unique values after melt could be genuine
  continuous per-item trait ratings or a composite/VAS export; needs the
  standard continuous-column verification against the paper text before
  deciding (see memory `feedback_continuous_column_verification`).

- [ ] **5 unresolved leads from the PLOS backlog-sweep retriage
  (2026-08-18)**, all in
  `plos_monthly_retriage_ha_full_2026-08-18.csv`. The run committed its
  95-row candidates CSV on branch `automated/plos-backlog-2026-08-18`
  (commit `3404058`) without running Step 2b, and its message called the 5
  `human_assistance` rows "for human review"; the retriage has now been
  run and **none** of them is `human_review`, so no
  `human_review/human_review_plos_batch30.csv` was warranted. What they
  actually need:
  - `aggregate_continuous` (3) -- confirm resp is a genuine continuous
    per-item response and not a composite/VAS export, per memory
    `feedback_continuous_column_verification`:
    `10.1371/journal.pone.0182956` (burnout/coping, N=1322, 62 items),
    `10.1371/journal.pone.0177240` (construal level & delay discounting,
    N=135, 13 items), and `10.1371/journal.pone.0289027` (emotions during
    numerical problems, N=112, 6 items -- this one is `dup_id_item` at
    ratio 1.0x, so check for a wave column before assuming continuous).
  - `worth_retrying` (2) -- text-coded Likert item columns needing the
    standard recode, and both are **already logged** in
    `human_review/googlesheet_humaneye.csv`, so check that record first:
    `10.1371/journal.pone.0172835` (muscle fatigue / movement coordination)
    and `10.1371/journal.pone.0321423` (medication adherence scoping
    review -- likely not primary item response data at all).

- [ ] **Step 2b backlog: 4 older triage CSVs had never been retriaged**
  (found 2026-08-18 while checking whether the 08-18 PLOS run's skipped
  Step 2b was a one-off -- it was not). Retriage has now been run and the
  outputs committed as `alt_source_retriage_ha_2026-08-14.csv`,
  `monthly_retriage_ha_weekly_2026-08-17.csv`,
  `pmc_monthly_retriage_ha_full_2026-08-16.csv`, and
  `pmc_monthly_retriage_ha_full_2026-08-16-2.csv` (99 `human_assistance`
  rows in total). Outcome:
  - **`human_review` (15 rows) is almost entirely already-known**: 13 were
    already logged in `human_review/googlesheet_humaneye.csv`. Of the 2
    genuinely new, one (`10.6084/m9.figshare.29145239.v1`, N=27) is below
    the N>=100 floor and was skipped outright; the other is archived as
    `human_review/human_review_altsource_batch1.csv`
    (`10.6084/m9.figshare.32887717.v1`, Tinder use / general
    trust-and-wellbeing, N unknown).
  - **`not_item_response` (48 rows)** dropped, per the standard bucket
    handling.
  - **Remaining machine-side leads, after pruning everything below the
    N>=100 floor** -- `aggregate_continuous` needs the continuous-column
    verification (memory `feedback_continuous_column_verification`),
    `worth_retrying` needs a re-download and/or the text-Likert recode:
    - alt-source aggregate: figshare `21070342.v8` (N=262),
      `33090965.v1` (347), `32994878.v1` (204), `33154514.v1` (128),
      `30826265.v1` (1132)
    - alt-source worth_retrying: figshare `33227889.v1` (417),
      `33075128.v1` (142), `33202694.v1` (3244), plus two Frontiers
      supplementary tables with unknown N
      (`10.1371/journal.pone.0318638.t006`,
      `10.3389/fpsyg.2021.762225.s002`). Note
      `10.3389/fpubh.2020.597389.s002` (N=6688) is the same
      pharmacy-preference discrete-choice study already listed in the
      2026-08-13 repo-mode RT item above -- don't double-chase it.
    - repos-weekly aggregate (Dataverse): `10.7910/dvn/x2c2pl` (N=394,
      preoperative anxiety) and `10.7910/dvn/tg1gya` (N=530920,
      wellbeing/race/rurality -- large enough to be worth the check
      even if it turns out to be composite scores).
    - PMC aggregate: `10.7717/peerj.15581` (184), `.20310` (188),
      `.7208` (102), `.13069` (227)
    - PMC worth_retrying: `10.7717/peerj.5185` (N=1731 but only 2 items
      -- check it isn't a 1-item scale in disguise), `.3928` (371),
      `.14740` (1334), `.19127` (101)
  - Everything below N=100 in these four files was dropped outright per
    the flat floor (memory `feedback_min_sample_size`), not carried as a
    lead.

- [x] **Triage script's `good` flag doesn't catch two content-level
  failure modes** -- **fixed 2026-08-17**. Both checks added to
  `irw_triage_updated.py` (not `irw_batch_updated.py` as this item
  originally guessed -- `triage_dataset()`/`run_qc()` is where flags are
  decided): (1) `MIN_PARTICIPANTS = 100` now gates via its own terminal
  `below_min_n` flag rather than a QC failure, since N is not something a
  human can adjudicate or a script can fix -- routing it to
  `human_assistance` would just spend review time re-deriving "too small";
  (2) `composite_items*` flags item labels that name a computed score
  (`Pre`/`Post`, `*_total`, `*_score`, `subscale_*`) -- all of them is a
  `fail`, some is a `warn`. Verified against both PR #1625 false-positive
  shapes plus controls; see `BATCH_LOG.md`'s 2026-08-17 entry.

- [ ] **Two off-construct `worth_retrying` leads from the 2026-08-13
  repo-mode RT search**, not chased since they're not response-time data:
  a discrete-choice pharmacy-preference study, N=6688
  (`frontiersin.figshare.com/.../13351250`, dup_id_item ratio 2.0x --
  check if it's genuinely repeated-choice-task structure before writing a
  script); a heart-rate-complexity/cognitive-task study with text-coded
  Likert item columns (`frontiersin.figshare.com/.../17083529`, needs the
  standard text-Likert-value mapping fix).

- [x] **`automated_finding/biblio_plos28_pmc5.csv`** (25 rows, 13 papers ->
  25 tables, consolidated from `biblio_batch28_group1.csv` (4 rows, 3
  papers) + `biblio_batch28_group2.csv` (11 rows, 8 papers) +
  `biblio_batch28_group3.csv` (10 rows, 2 papers), from 3 parallel review
  passes over PLOS ONE batch 28's `good`+`worth_retrying` pool (48
  candidates) and PMC batch 5's `good`+`worth_retrying` pool (20
  candidates), 2026-08-12) uploaded to Redivis and pasted into the
  dictionary sheet (confirmed 2026-08-13, ben-domingue); file and all 25
  `irw_output/*.csv` files removed as expected. (2026-08-13 note for the
  record: the merged CSV had gone missing pre-confirmation while the
  output files were still present — an inversion of the usual
  post-confirmation pattern — so it was regenerated from the per-table
  scripts/output-file metadata, n/items/resp re-verified against each
  `irw_output/*.csv`, before this upload.) See
  `BATCH_LOG.md`'s "Batch 28, group 1/2/3" entries for full per-DOI detail
  (shipped + all skip reasons). Two candidates deliberately left unshipped
  rather than silently dropped, worth a look if revisiting:
  `10.1371/journal.pone.0311248` (smartphone-use study, only 2 single-item
  continuous measures plus implausible step-count outliers) and
  `10.1371/journal.pone.0208004` (RIKNO 2.0 + MSKQ MS-knowledge
  questionnaires, n=1219, CC-BY — raw items are multiple-choice with
  full answer-text options; scoring requires parsing underline-marked
  correct answers out of a bilingual Word document that doesn't align
  cleanly enough to automate safely, needs a human-built answer key).
  One PMC candidate flagged for a dedicated follow-up pass rather than a
  rushed script: `10.7717/peerj.12040` (dementia schedule, 811 rows x 424
  cols, real item-level data across cognitive/depression/IADL/medical/
  socioeconomic instruments, CC BY, but the true respondent-level `id`
  couldn't be confidently determined without a codebook).

- [x] **`automated_finding/biblio_pmc_batch4.csv`** (41 rows, 18 papers ->
  41 tables, consolidated from all of PMC batch 4's `good` (3 papers) +
  `worth_retrying` (15 papers across 4 parallel review passes) pool,
  2026-08-12) uploaded to Redivis and pasted into the dictionary sheet
  (confirmed 2026-08-12, ben-domingue); file and all 41 `irw_output/*.csv`
  files gone from disk as expected. All 41 output files verified present
  in `irw_output/` before this CSV was assembled. `reuter_2021_campuslife`
  (originally 42nd row) was
  removed post-review, 2026-08-12 (ben-domingue catch) — mixed binary
  Yes/No and 3-point Less/Same/More items under one file with no confirmed
  underlying instrument, same problem as the sheets the script already
  excluded elsewhere in the same workbook. See `BATCH_LOG.md`'s "PMC batch
  4 — full accounting" entry for the full per-paper/per-DOI detail
  (including the 2 repeat known-false-positives from batch 1, all skip
  reasons, and the N/item count corrections the automated pass got wrong
  for several papers).

- [x] **13 PMC batch 4 candidates flagged as an "N=50-99 ask-first band"
  — corrected, this was a policy-application error, not an open item**
  (2026-08-12): `feedback_min_sample_size` was already updated 2026-08-12
  to a flat N>=100 skip floor with no ask-first band (see `SKILL.md`'s
  Step 4), but these 13 got logged as awaiting a ben-domingue go/no-go
  anyway. All are N<100, so all are simply **skipped**, no decision
  needed: `10.7717/peerj.17536` (n=50-63), `10.7717/peerj.19403` (n=63),
  `10.7717/peerj.15582` (n=69), `10.7717/peerj.4443` Exp1 (n=52),
  `10.7717/peerj.19679` (n=94), `10.7717/peerj.2978` (n=52), `10.7717/
  peerj.16065` (n=54), `10.7717/peerj.6988` (n=91), `10.7717/peerj.12078`
  (n=99), `10.7717/peerj.5969` (n=85), `10.7717/peerj.15030` (n=60),
  `10.7717/peerj.14730` (n=81), `10.7717/peerj.20827` (n=91). None had
  content flaws beyond N where checked; if the floor ever moves back down
  these DOIs are the ones to revisit, but no standing list is kept per
  `feedback_min_sample_size` (log-and-move-on, same as any other skip).

- [x] **`automated_finding/biblio_plos_batch27_worthretrying.csv`** (19
  rows, 8 papers -> 19 tables, from manual review of all of PLOS batch 27's
  `good` + `worth_retrying` pool, 2026-08-12) uploaded to Redivis and
  pasted into the dictionary sheet (confirmed 2026-08-12, ben-domingue);
  file and all 19 `irw_output/*.csv` files gone from disk as expected.
  Scripts: `data/schafer_2016_music_
  goals_effects.py`, `data/srivani_2022_education4.py`, `data/liu_2025_
  teacher_support.py`, `data/babaei_2023_oral_health.py`, `data/gholami_
  2017_periodontal_knowledge.py`, `data/wen_2022_pyd.py`, `data/powell_
  2018_empathy.py`. See `BATCH_LOG.md`'s "PLOS ONE batch 27 — full
  accounting" entry (and the two preceding worth_retrying-review entries
  it summarizes) for every skipped DOI and why. Two post-review fixes
  same day (ben-domingue catches): `carus_2021_snowboard_speed.py` deleted
  entirely — its 2 "items" were a GPS-measured actual speed and a
  subjective estimate, a bias/calibration measurement rather than a real
  item-response pair, the same problem class as the previously-rejected
  fish/mouse physiological-measurement candidates; `wen_2022_pyd_s1`/`_s2`
  merged into one `wen_2022_pyd.csv` with a `cov_study` column (same
  instrument, same items, same scale, two independent samples — see memory
  `feedback_collapse_same_instrument`). `plos_batch27_triage.csv`/
  `plos_batch27_retriage.csv` already deleted (done earlier the same day,
  before this upload confirmation).

- [x] **11 PLOS batch 27 candidates flagged as an "N=50-99 ask-first
  band" — corrected, this was a policy-application error, not an open
  item** (2026-08-12): same fix as the PMC batch 4 entry above — all are
  N<100 and simply skipped, no ben-domingue decision needed:
  `10.1371/journal.pone.0260934` (n=83), `10.1371/journal.pone.0141321`
  (n=82), `10.1371/journal.pone.0241721` (n=66), `10.1371/
  journal.pone.0218017` (n=80), `10.1371/journal.pone.0151747` (n=60),
  `10.1371/journal.pone.0117947` (n=86), `10.1371/journal.pone.0241041`
  (n=53), `10.1371/journal.pone.0257274` (n=83), `10.1371/
  journal.pone.0150375` (n=58), `10.1371/journal.pone.0149777` (n=54),
  `10.1371/journal.pone.0203664` (n=61).

- [x] **`liu_2025_ydcy` QC fix** (2026-08-12, ben-domingue catch): the
  shipped table had a constant column (`YDCY1`, resp=1 for all 879
  respondents, zero variance) counted as an item, and 58 zero values
  isolated to a single item (`YDCY3`) with no 0s anywhere else in the
  5-item block — the exact cross-item data-entry-error signature in
  `datastandard.md`. Fixed in `data/liu_2025_teacher_support.py`: dropped
  `YDCY1`, tightened `YDCY`'s valid range to 1-5. Regenerated
  `liu_2025_ydcy.csv` (now 4 items, resp 1-5, was 5 items resp 0-5); biblio
  row updated in `biblio_plos_batch27_worthretrying.csv`.

- [x] **`automated_finding/biblio_pmc_batch1.csv`** (11 rows, 5 papers ->
  11 tables, from the first real `irw_discover_pmc.py` batch, 2026-08-12)
  uploaded to Redivis and pasted into the dictionary sheet (confirmed
  2026-08-12, ben-domingue); file and all 11 `irw_output/*.csv` files gone
  from disk as expected. See `BATCH_LOG.md`'s "Europe-PMC connector batch
  1" entry for full per-paper detail, including the two rejected false
  positives (PCIQ-F, cannabis anxiety/depression) and the three
  multi-scale-split papers (Hospice Comfort Questionnaire, Cloninger
  personality study, spinal cord injury QoL). MBI-SS response scale
  (0=never..6=always) confirmed against the paper's own Methods text,
  2026-08-12 — not a missingness sentinel.

- [x] **`human_review/human_review_pmc_batch1.csv`** (33 rows, PMC
  connector batch 1's `human_review` rows from `irw_retriage_ha.py`,
  2026-08-12) — no longer needs pasting anywhere. The old "human eye" queue
  sheet was deprecated 2026-08-12 (unmanageable at ~4,846 rows); this file
  is already the permanent archived record in its correct location and
  naming, nothing further to do. See `BATCH_LOG.md`'s "Human review sheet
  deprecated" entry.

- [x] **PMC connector batch 1's 31 `worth_retrying` rows — reviewed**
  (2026-08-12). See "worth_retrying review — pmc1/plos26/pmc2" in
  `BATCH_LOG.md` for the full 45-candidate accounting (this batch's rows
  plus plos26/pmc2 below, deduped by DOI). `pmc_batch1_retriage.csv`
  deleted — fully captured elsewhere.

- [x] **PLOS ONE batch 26** (2026-08-12, `plos_batch26_triage.csv`, 497
  candidates): its 1 `good` candidate (LGB medical students mental health
  study) was reviewed and skipped — real participant email addresses in
  the supplementary file, a hard PII violation regardless of the paper's
  CC BY license. See `BATCH_LOG.md`'s "PLOS ONE batch 26" entry.

- [x] **PLOS ONE batch 26's 107 `human_assistance` rows — retriaged**
  (2026-08-12): 41 `human_review` (written to
  `human_review/human_review_plos_batch26.csv`), 32 `aggregate_continuous`
  (dropped), 23 `not_item_response` (dropped), 11 `worth_retrying`
  (reviewed — see the entry above). `plos_batch26_triage.csv` deleted —
  fully captured elsewhere.

- [x] **`automated_finding/biblio_pmc_batch2.csv`** (6 rows, 1 paper -> 6
  tables, from PMC connector batch 2, 2026-08-12) uploaded to Redivis and
  pasted into the dictionary sheet (confirmed 2026-08-12, ben-domingue);
  file and all 6 `irw_output/sun_2024_*.csv` files gone from disk as
  expected. See `BATCH_LOG.md`'s "PMC connector batch 2 — result" entry.
  Its other `good` candidate (nursing profession survey) was skipped per
  the new PII policy (real `date of birth` column).

- [x] **PMC connector batch 2's 43 `human_assistance` rows — retriaged**
  (2026-08-12): 19 `human_review` (written to
  `human_review/human_review_pmc_batch2.csv`), 11 `aggregate_continuous`
  (dropped), 6 `not_item_response` (dropped), 7 `worth_retrying`
  (reviewed — see the entry above). `pmc_batch2_triage.csv` deleted —
  fully captured elsewhere.

- [x] **`automated_finding/biblio_pmc_batch3.csv`** (8 rows, 3 papers ->
  8 tables, from the pmc1/plos26/pmc2 `worth_retrying` review, 2026-08-12)
  uploaded to Redivis and pasted into the dictionary sheet (confirmed
  2026-08-12, ben-domingue); file and all 8 `irw_output/*.csv` files gone
  from disk as expected. `resp=0` in `han_2026_phq9`/`han_2026_gad7` and
  `shu_2024_gad7`/`shu_2024_phq9` double-checked against each paper's own
  pre-computed `*_Score`/`*total` columns (row-wise sum of raw items
  matched exactly for every respondent, zero mismatches) — confirms `0`
  ("not at all") is a genuine response, not a missingness sentinel.
  Scripts: `data/han_2026_gad7.py` / `han_2026_phq9.py` / `han_2026_isi.py`
  (one paper, 3 scales), `data/valdivia_2023_oms.py`,
  `data/geacaballero_2019_pes_nwi.py` (+ `_short` sibling, same paper, 2
  scales), `data/shu_2024_gad7.py` / `shu_2024_phq9.py` (one paper, 2
  scales). See `BATCH_LOG.md`'s "worth_retrying review — pmc1/plos26/pmc2"
  entry for per-paper detail.

- [x] **`automated_finding/biblio_pmc_deferred.csv`** (30 rows, 9 papers ->
  30 tables, from resolving all 14 candidates in the now-deleted
  `pmc_deferred_candidates.csv`, 2026-08-12) uploaded to Redivis and
  pasted into the dictionary sheet (confirmed 2026-08-12, ben-domingue);
  file and all 30 `irw_output/*.csv` files removed. See `BATCH_LOG.md`'s
  "Resolution of the 14 deferred PMC candidates" entry for full per-paper
  detail, including why 5 of the 14 were skipped (3 for the new N<100
  floor, 1 for turning out to be aggregate-only data after a successful
  fetch retry, 1 for real GPS-coordinate PII).

- [x] **`automated_finding/biblio_plos_batch25.csv`** (23 rows, 6 papers ->
  23 tables, from PLOS ONE batch 25's `good` (3 fresh) + `worth_retrying`
  (4 fresh) pool, 2026-08-11) uploaded to Redivis and pasted into the
  dictionary sheet (confirmed 2026-08-11, ben-domingue); file and all 23
  `irw_output/*.csv` files gone from disk as expected. See `BATCH_LOG.md`'s
  "PLOS ONE batch 25" entry for full per-paper detail, including the
  `tsai_2017_treeit` 17-table split (TAM PU/PEOU/BI + Zhang et al.'s 14
  named usability heuristics) and the `grandahl_2017_hpv_beliefs` "do not
  know" treated as non-response.

- [x] **`automated_finding/human_review_plos_batch25.csv`** (87 rows,
  batch 25's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-08-11, ben-domingue); file gone
  from disk as expected.

- [ ] **PLOS ONE batch 25 — 4 `worth_retrying` candidates deferred, not
  shipped**: `10.1371/journal.pone.0242967` (counterfactual-reasoning task,
  N=54, real per-trial data but in the N=50-99 borderline band — needs a
  ben-domingue decision per `feedback_min_sample_size`); `10.1371/journal.
  pone.0151634` (music-listening ESM study, N=967, but "goals"/"effects"
  columns are 1-10 rankings across 6 goal categories per observation —
  structure needs more time to map correctly); `10.1371/journal.pone.
  0138269` (sentence-comprehension reading task — item values are
  response-time-derived scores divided by syllable count, `rt`-column
  semantics unclear); `10.1371/journal.pone.0329483` (Arabic-language
  artistic-skills/academic-engagement questionnaire, N=102, real ~26-item
  1-5 Likert data, CC BY 4.0, but item labels need translation from Arabic
  before shipping). See `BATCH_LOG.md`'s "PLOS ONE batch 25" entry.

- [x] **`automated_finding/biblio_plos_batch24.csv`** (28 rows, merged from
  Groups A/B/C, 12 papers -> 28 tables, from PLOS ONE batch 24's `good`
  (7 fresh) + `worth_retrying` (36 fresh) pool after de-duping 9 already-
  decided DOIs, reviewed in 3 parallel passes, 2026-08-11) uploaded to
  Redivis and pasted into the dictionary sheet (confirmed 2026-08-11,
  ben-domingue); file and all 28 `irw_output/*.csv` files gone from disk
  as expected. See `BATCH_LOG.md`'s "PLOS ONE batch 24" entry for full
  per-paper detail, including the `li_2025_policy_environment` QC fix
  (non-integer/out-of-range Policy Environment items filtered to integer
  1-7 values only) and the `binette_2022_extinction` strain-merge (two
  N<50 strain sheets combined via `cov_strain` since both share an
  identical 3-phase design; non-integer `resp` values confirmed genuine
  by re-checking the raw source Excel directly, per ben-domingue's
  question). A second ben-domingue question confirmed
  `szameitat_2015_occupation_multitask`'s `resp=0` values are a genuine
  "not at all" response category (explicit text->value map, non-matching/
  blank cells dropped before writing), not missingness.

- [x] **`automated_finding/human_review_plos_batch24.csv`** (103 rows,
  batch 24's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-08-11, ben-domingue); file gone
  from disk as expected.

- [x] **PLOS ONE batch 24 — 2 candidates in the N=50-99 borderline band**,
  reviewed but not shipped, awaiting a decision: `10.1371/journal.pone.
  0335166` (nursing literacy practices, Karolinska, N=67, 10 closed
  ordinal 1-4 items) and `10.1371/journal.pone.0229591` (early visual
  language/deaf children, analytic-sample N=56, partly opaque item codes
  mixed with already-scored subtest scores). See `BATCH_LOG.md`'s "PLOS
  ONE batch 24" entry. — **closed 2026-08-25, no decision needed**: the flat N>=100 floor with no ask-first band was settled 2026-08-12 (memory `feedback_min_sample_size`); both are N<100 and simply skipped — the same policy-application error already corrected for PLOS batch 27 and PMC batch 4.

- [ ] **PLOS ONE batch 24 — one candidate needing human follow-up**:
  `10.1371/journal.pone.0286787` (OSCE nursing exam) has real-looking
  response data but opaque uncoded variable names (`V1`/`v4`...) with no
  accessible codebook (Dryad reviewer link 404s, public DOI unresolvable)
  and >=3 instruments apparently bundled with inconsistent naming — too
  much mis-mapping risk to guess at. Worth author contact if pursued.

- [x] **`automated_finding/biblio_plos_batch23.csv`** (28 rows, merged from
  Groups A/B/C, 14 papers -> 28 tables, from PLOS ONE batch 23's full
  `good` (13) + `worth_retrying` (40) pool, reviewed in 3 parallel passes,
  2026-08-11) uploaded to Redivis and pasted into the dictionary sheet
  (confirmed 2026-08-11, ben-domingue); file and all 28 `irw_output/*.csv`
  files gone from disk as expected. See `BATCH_LOG.md`'s "PLOS ONE batch
  23" entries (Groups A/B/C) for full per-paper detail, including the
  "Post-review ordinality fixes" entry (same day, ben-domingue's
  questions): `simard_2018_fgf2_behavior` was cut down to `simard_2018_
  epm_behavior` (EPM-only, 3 items — FST/OF dropped for relying on
  response-time-like latency items to clear the 2-item minimum) and
  `klatt_2016_speed_estimation`'s `resp` was changed from a raw speed
  estimate to signed estimation error against each trial's known true
  speed.
- [x] **`automated_finding/human_review_plos_batch23.csv`** (106 rows,
  batch 23's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-08-11, ben-domingue); file gone
  from disk as expected.
- [ ] **PLOS ONE batch 23 — one candidate flagged for a second look**:
  `10.1371/journal.pone.0242326` (Caprara et al. self-efficacy-in-negative-
  emotions study, N=1695, 3 named scales incl. MNESRES/PANAS/SWLS) — Group
  C found only a codebook + figure-data SI files, no raw-response file, but
  didn't rule out a missed SI attachment. Worth a second check of the
  article's full SI list before writing off.
- [x] **`automated_finding/biblio_plos_batch22.csv`** (38 rows, 15 papers ->
  38 tables, from PLOS ONE batch 22's `good`+`worth_retrying` review, done
  autonomously while ben-domingue was away from the computer 2026-08-10)
  uploaded to Redivis and pasted into the dictionary sheet (confirmed
  2026-08-11, ben-domingue); file and all 38 `irw_output/*.csv` files gone
  from disk as expected. See `BATCH_LOG.md`'s "PLOS ONE batch 22" entry for
  full per-paper detail, including one QC catch (`wekker_2018_mfsq`:
  non-integer imputed cells on an integer 1-7 scale, dropped) and 2
  dup_id_item false-positive fixes resolved by falling back to row-index
  ids (`akrawi_2025_sclc`, `xu_2022_ples_aa`, `roettl_2018_*`). A
  ben-domingue follow-up question confirmed `tomioka_2022_srh_importance`'s
  resp=3 is a genuine "Not very important" response category (codebook:
  1=Very important...4=Not important), not missingness or an error — no
  respondent in the sample happened to pick category 4.

- [x] **`automated_finding/human_review_plos_batch22.csv`** (77 rows, batch
  22's `human_review` rows from `irw_retriage_ha.py`) pasted into the
  "Human eye" sheet (confirmed 2026-08-11, ben-domingue); file gone from
  disk as expected.

- [x] **Batch 22 — one N=50-99 borderline candidate not shipped, no
  ben-domingue decision needed**: `10.1371/journal.pone.0311487` (natural
  soundscapes/mood recovery, N=68) was independently disqualified on
  content grounds (composite-only STAI-S/UWIST-MACL scores, no raw items)
  so it didn't reach a pure N judgment call — logged here only for
  completeness, no action needed. — **closed 2026-08-25**: the item says so itself; N<100 is a flat skip and the candidate was independently disqualified anyway.

- [x] **`automated_finding/biblio_plos_batch21.csv`** (25 rows, 4 papers ->
  25 tables, from PLOS ONE batch 21's `good`-candidate review) uploaded to
  Redivis and pasted into the dictionary sheet (confirmed 2026-08-10,
  ben-domingue); file and all 25 `irw_output/*.csv` files gone from disk
  as expected. See `BATCH_LOG.md`'s "PLOS ONE batch 21" entry for full
  per-paper detail.

- [x] **`automated_finding/human_review_plos_batch21.csv`** (115 rows,
  batch 21's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-08-10, ben-domingue); file gone
  from disk as expected.

- [x] **`automated_finding/biblio_plos_batch21_worthretrying.csv`** (55
  rows, 14 papers -> 55 tables, from PLOS ONE batch 21's `worth_retrying`
  pool) uploaded to Redivis and pasted into the dictionary sheet
  (confirmed 2026-08-10, ben-domingue); file and all 55 `irw_output/*.csv`
  files gone from disk as expected. See `BATCH_LOG.md`'s "PLOS ONE batch
  21 worth_retrying — all 33 non-duplicate candidates resolved" entry for
  full per-paper detail, including the QC fix to `de_vries_2022_hexaco_
  meta` (69 non-integer resp values dropped) prompted by ben-domingue's
  questions and documented in the "QC pass on batch 21 output" entry.

- [ ] **Figshare external lead not yet chased**: `0227877` ("An atlas of
  personality, emotion and behaviour", batch 21 worth_retrying) — the
  PLOS SI has no raw data; the real dataset is at Figshare
  `10.6084/m9.figshare.c.4792323`. Worth a follow-up through the regular
  repo-based pipeline (Step 1/2), not PLOS-specific.

- [x] **`automated_finding/biblio_plos_batch20.csv`** (10 rows, 6 papers ->
  10 tables, from PLOS ONE batch 20's `good`-candidate review) uploaded to
  Redivis and pasted into the dictionary sheet (confirmed 2026-08-10,
  ben-domingue); file and all 10 `irw_output/*.csv` files gone from disk
  as expected. See `BATCH_LOG.md`'s "PLOS ONE batch 20" entry for full
  per-paper detail, including a QC catch/fix the same day: the
  `abukhalaf_2025_*` tables' fractional values were partly mean/constant-
  imputed cells masquerading as raw slider responses (caught by
  ben-domingue's question), fixed to keep only genuine anchor values.

- [x] **`automated_finding/human_review_plos_batch20.csv`** (116 rows,
  batch 20's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-08-10, ben-domingue); file deleted
  from the repo.

- [x] **`automated_finding/biblio_batch20_worthretrying_final.csv`** (30
  rows, 15 papers -> 30 tables, from PLOS ONE batch 20's `worth_retrying`
  review, all 3 groups) uploaded to Redivis and pasted into the dictionary
  sheet (confirmed 2026-08-10, ben-domingue); file and all 30
  `irw_output/*.csv` files gone from disk as expected (already gone before
  cleanup was attempted -- consistent with this directory's known
  Dropbox-sync file-loss pattern, not a script bug). See `BATCH_LOG.md`'s
  "PLOS ONE batch 20 worth_retrying — all 3 groups consolidated" and "QC
  pass on batch 20 worth_retrying output" entries for full per-DOI detail,
  including 2 fixes applied before upload: `abouhashish_2025_chatgpt_
  attitudes`'s `cov_year_of_study` had a stray bullet/tab prefix + case
  inconsistency (cleaned), and 4 of the 5 `gordils_2021_*` tables had a
  corrupted item2 column in their Study-2 source data (identical to the
  scale's own composite mean, not a raw response -- dropped). This closes
  out PLOS ONE batch 20's `worth_retrying` pool end-to-end.

- [x] **`automated_finding/biblio_batch19_good.csv`** (51 rows, 16 papers
  -> 51 tables, from PLOS ONE batch 19's `good`-candidate review) uploaded
  to Redivis and pasted into the dictionary sheet (confirmed 2026-08-04,
  ben-domingue); file and all 51 `irw_output/*.csv` files gone from disk
  as expected.

- [x] **`automated_finding/human_review_plos_batch19.csv`** (148 rows,
  batch 19's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-08-04, ben-domingue); file gone
  from disk as expected.

- [x] **`automated_finding/biblio_batch19_worthretrying.csv`** (70 rows, 23
  papers -> 70 tables, from the batch 19 `worth_retrying` review below)
  uploaded to Redivis and pasted into the dictionary sheet (confirmed
  2026-08-09, ben-domingue); file and all 70 `irw_output/*.csv` files gone
  from disk as expected. Includes a QC spot-check pass (same day) that
  caught and fixed 2 real bugs (`ali_2021_spfi`, `reyes_2022_eheals`) and
  3 scale-range mismatches in `lai_2023_social_adaptability.py`'s
  relationship-scale outputs — see `BATCH_LOG.md`'s "PLOS ONE batch 19 —
  worth_retrying review" and "QC spot-check pass on batch 19
  worth_retrying output" entries (2026-08-09) for full per-paper/per-fix
  detail.

- [x] **PLOS ONE batch 19 — 95 `worth_retrying` rows reviewed** (2026-08-09):
  38 were duplicate DOIs already decided in earlier batches (not
  re-reviewed); the 56 genuinely new DOIs were split into 3 groups and
  reviewed in parallel (fetch full article + all SI files, license/N>=50/
  raw-vs-composite checks). Result: 23 papers -> 70 tables shipped (see
  `biblio_batch19_worthretrying.csv` item above), 23 skipped (content- or
  N-driven), 10 more in the N=50-99 borderline band written off per
  ben-domingue's explicit decision (2026-08-09) rather than shipped. Full
  per-DOI accounting in `BATCH_LOG.md`. `plos_retriage_batch19.csv` deleted
  — this closes out batch 19 end-to-end.

- [x] **`automated_finding/biblio_plos_batch18_full.csv`** (33 rows,
  consolidated from all 4 parallel-agent review passes over batch 18's 18
  `good` candidates: `valverdeberrocoso_2021_sqd`/`_tictip`/
  `_learning_design`, `pietraszkiewicz_2017_leader_eval`,
  `sun_2021_blockchain_loan_adoption`, `matarboumosleh_2017_spai26`/`_phq2`/
  `_gad2`, `zeng_2026_gai_ttf`/`_role_adapt`/`_self_efficacy`/
  `_inst_support`/`_exploration`/`_exploitation`/`_learning_effect`,
  `ordak_2026_vaccine_misreasoning`, `evans_2023_vaccine_hesitancy`/
  `_vaccination_norms`, `choy_2022_affect`/`_extraneous_events`/
  `_intent_career`/`_lifelong_career`/`_resilience`, `nam_2024_khlat`/
  `_selfcare`/`_access`/`_medint`/`_attitude`/`_selfeff`/`_function`,
  `jung_2018_media_use`, `yang_2025_intercultural_contact`/`_aiccs`)
  uploaded to Redivis and pasted into the dictionary sheet (confirmed
  2026-08-03, ben-domingue); file and all 33 `irw_output/*.csv` files gone
  from disk as expected. See `BATCH_LOG.md`'s batch 18 good-candidate
  review entries (2026-08-03) for full per-paper detail. 4 papers were
  reviewed and skipped (aggregate/derived data or a choice-experiment
  structure that doesn't fit the schema); 2 more skipped pre-emptively for
  N<50 before review even started (N=14, N=24).

- [x] **`automated_finding/human_review_plos_batch18.csv`** (116 rows,
  batch 18's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-08-03, ben-domingue); file gone
  from disk as expected.

- [x] **`automated_finding/biblio_batch18_worthretrying.csv`** (16 rows, 13
  papers -> 17 tables, from the batch 18 `worth_retrying` review below)
  uploaded to Redivis and pasted into the dictionary sheet (confirmed
  2026-08-04, ben-domingue); file and all 17 `irw_output/*.csv` files gone
  from disk as expected.

- [x] **PLOS ONE batch 18 — 57 `worth_retrying` rows reviewed** (2026-08-04):
  `plos_retriage_batch18.csv`'s 57 `worth_retrying` rows split into 3 pools
  before review: 7 were exact-DOI duplicates of candidates already
  reviewed/struck in batches 10/11/14 (skipped without re-review — search
  terms across batches keep resurfacing the same PLOS articles, this is
  expected and not a bug); 16 had no resolved n_participants/n_items from
  the automated pass (still open, see item below); the remaining 34 were
  split into 3 groups of ~11-12 and reviewed in parallel by 3 agents, each
  fetching the full article page + ALL Supporting Information files (not
  just the first, which is all `process_one()` inspects) and applying the
  standard license/N>=50/no-single-item/raw-vs-composite checks. Result:
  13 papers processed to 17 tables (`zhou_2025_ehealth_literacy`/
  `_peer_relationship`, `hayek_2022_attitude`/`_subj_norm`/`_self_efficacy`,
  `ribeiro_2024_msk_hq`, `stolz_2015_death_attitudes`/`_authoritarianism`,
  `doustmohammadian_2017_fnlit`, `koo_2016_comm_technique_use`/`_opinion`,
  `mccarlie_2022_ortho_literacy`, `latifi_2026_insect_fear`,
  `teodorini_2020_modafinil_attitudes`, `duong_2025_tbl_experience`/
  `_confidence`), all CC BY 4.0. 21 other candidates skipped, overwhelmingly
  because the only SI file available was pre-computed composite/subscale
  totals rather than raw item-level responses (a recurring pattern this
  batch) — see `BATCH_LOG.md`'s "PLOS ONE batch 18 worth_retrying review"
  entry for the full per-DOI accounting. `plos_retriage_batch18.csv`
  deleted.

- [x] **`automated_finding/biblio_batch18_nancount.csv`** (14 rows, 5
  papers -> 14 tables, from the review of batch 18's 16 unresolved-count
  `worth_retrying` rows below) uploaded to Redivis and pasted into the
  dictionary sheet (confirmed 2026-08-04, ben-domingue); file and all 14
  `irw_output/*.csv` files gone from disk as expected.

- [x] **PLOS ONE batch 18 — 16 `worth_retrying` rows with unresolved
  n_participants/n_items reviewed** (2026-08-04): fetched each article page
  directly and manually inspected every tabular SI file (the automated
  triage pass had failed to parse a clean participant/item count for these
  16, likely a header-offset or non-tabular-shaped file, so they'd been
  held out of the earlier review pass rather than guessed at). Result: 5
  papers processed to 14 tables (`jaracz_2017_temperament`/`_job_stress`,
  `fan_2025_mbi_exhaustion`/`_accomplishment`/`_depersonalization`,
  `weatherspoon_2015_family_physicians_freq`/`_effectiveness`,
  `weatherspoon_2015_pediatricians_freq`/`_effectiveness`,
  `kuczyk_2024_facemask_fba`/`_fbe`, `fukuda_2021_health_literacy`/
  `_info_reliability`/`_withholding_behavior`), all CC BY 4.0. 11 skipped:
  1 systematic-review characteristics table (not item response), 1
  heterogeneous-single-items CGSS extract (not a coherent scale), 2 real
  scales whose actual raw data lives in an external repo not the PLOS SI
  file (Mendeley: `10.1371/journal.pone.0257726`; GitHub/Zenodo
  `10.5281/zenodo.6793420`: `10.1371/journal.pone.0276734` — both logged
  as leads below), 2 aggregate/composite-only files, 1 binary-checkbox
  (not ordinal) file, and 4 below the N=50 minimum (N=18/22/30/`~3
  coaches`). See `BATCH_LOG.md`'s "PLOS ONE batch 18 nan-count review"
  entry for the full per-DOI accounting.

- [ ] **Two batch-18 nan-count leads pointing to external repos, not yet
  chased** (2026-08-04): `10.1371/journal.pone.0257726` ("Specificity of
  spiders among fear- and disgust-eliciting arthropods") says its real
  response data is at Mendeley Data `10.17632/68mkyrb4n3.1` (the PLOS SI
  file itself is only a stimulus-image catalog, not response data);
  `10.1371/journal.pone.0276734` ("The effect of mindfulness...low back
  pain") says its data is at `https://github.com/nirakara-lab/RCT_Minfulness_Chronic_Back_Pain`
  / Zenodo `10.5281/zenodo.6793420` (the PLOS SI file is only a
  descriptive-statistics summary table). Neither has been fetched/opened
  yet — worth a follow-up pass through the regular repo-based pipeline
  (Mendeley/Zenodo/GitHub aren't PLOS's connector, so `irw_discover_plos.py`
  won't find these on its own).

- [x] **`automated_finding/biblio_plos_batch17.csv`** (12 rows:
  `hicks_2020_bioveda`, `stachl_2020_belonging`, `bittencourt_2021_dfs2`,
  `hewei_2022_msva_purchase`, `carney_2023_substance_use`,
  `sun_2026_eap_usage/_difficulty/_content/_methods`, `shen_2020_sas20`,
  `yu_2015_family_environment`, `jelinek_2021_cdi`) uploaded to Redivis and
  pasted into the dictionary sheet (confirmed 2026-08-03, ben-domingue);
  file and `irw_output/plos_batch17/` both gone from disk as expected.
  Note: the original file had a malformed row (`carney_2023_substance_use`'s
  Description field had an unescaped internal comma, breaking CSV
  structure and causing a bad paste) -- fixed before the successful paste.
  See `BATCH_LOG.md`'s "PLOS ONE batch 17" entry for full per-dataset
  detail.

- [x] **`automated_finding/human_review_plos_batch17.csv`** (146 rows)
  pasted into the "Human eye" sheet (confirmed 2026-08-03, ben-domingue);
  file gone from disk as expected.

- [x] **PLOS ONE batch 17 — 2 deferred candidates resolved** (2026-08-03):
  HELMA health-literacy scale (`10.1371/journal.pone.0149202`) -> 7 tables
  (processed); Portuguese preoperative-stress file
  (`10.1371/journal.pone.0263275`) struck (its IDATE-labeled columns
  turned out to be fragments of a novel pooled instrument, not raw
  STAI state/trait scales). See `BATCH_LOG.md`'s "Backlog-resolution
  pass" entry.

- [x] **PLOS ONE batch 17 — 86 of 101 worth_retrying rows** written off
  (2026-08-03), matching the batches-6/9/12/13/16 pattern.
  `plos_retriage_batch17.csv` deleted.

- [x] **`automated_finding/biblio_falih_2026.csv`** (2 rows: `falih_2026_mds16`,
  `falih_2026_dass21`) pasted into the dictionary sheet (confirmed
  2026-08-03, ben-domingue); file gone from disk as expected. See
  `BATCH_LOG.md`'s "First scheduled monthly discovery run + triage" entry.

- [x] **First scheduled monthly discovery run (2026-08-03) — follow-up
  items resolved** (2026-08-03): 4 Dataverse 403s retried once, still
  403 (struck); UTF-8 decode bug fixed generally in `load_table()`
  (latin-1 fallback), the specific file turned out to be a near-duplicate
  of an already-known dataset (not reprocessed); field-count-mismatch CSV
  is genuinely messy free-text, not fixable, struck; of the 4
  `worth_retrying` rows, 1 processed (`nabizadehchianeh_2026_tempsa`), 1
  is license-blocked (logged to `license_blocked_candidates.csv`), 2
  struck; 5 `human_review` rows staged to
  `human_review_monthly_20260803.csv`; of the 3 named-instrument OSF
  `no_usable_file` checks, BDI-II had a real file hiding behind a `.dat`
  extension (processed as `marquezpalacios_2026_bdi2`), the other 2
  confirmed genuinely empty; Bem Sex-Role Inventory confirmed real and
  processed (`holden_2026_bsri`). See `BATCH_LOG.md`'s "Backlog-resolution
  pass" entry for full detail.

- [x] **`automated_finding/biblio_backlog_resolution.csv`** (24 rows: 11
  papers/datasets across the batch17/16/13/12/9/8 deferred-candidate
  backlog and the first monthly-discovery run — see `BATCH_LOG.md`'s
  "Backlog-resolution pass" entry, 2026-08-03) uploaded to Redivis and
  pasted into the dictionary sheet (confirmed 2026-08-03, ben-domingue);
  file and all `irw_output/*.csv` files gone from disk as expected.

- [x] **`automated_finding/human_review_monthly_20260803.csv`** (5 rows,
  from the first monthly discovery run's `irw_retriage_ha.py` pass) pasted
  into the "Human eye" sheet (confirmed 2026-08-03, ben-domingue); file gone
  from disk as expected.

- [x] **PLOS ONE batch 15 — `automated_finding/human_review_plos_batch15.csv`**
  (144 rows) pasted into the "Human eye" sheet (confirmed 2026-08-01,
  ben-domingue); file gone from disk as expected. See `BATCH_LOG.md`'s
  "PLOS ONE batch 15" entry.

- [x] **PLOS ONE batch 15 — `automated_finding/biblio_plos_batch15_final.csv`**
  (146 rows, consolidated from 3 separate staging files at ben-domingue's
  request) uploaded to Redivis and pasted into the dictionary sheet
  (confirmed 2026-08-02, ben-domingue); file and all `irw_output/*.csv`
  files gone from disk as expected. Covers the worth_retrying/
  recoverable_format pool and the previously-deferred candidates:
  `biblio_plos_batch15_deferred.csv` (17 rows: 5 papers -> 17 tables),
  `biblio_plos_batch15_worthretrying.csv` (69 rows post-adjudication: 13
  papers -> tables, 2 duplicates caught, 11 confirmed not-a-fit), and
  `biblio_plos_batch15_worthretrying_round2.csv` (61 rows
  post-adjudication: 24 papers -> tables; a 25th, `0252329`, turned out
  to be a content-validity panel not respondent data, reclassified as
  skip). A same-day adjudication pass (ben-domingue spot-checking
  resp/rt semantics) removed 6 tables (`dasilva_2018_*` x5,
  `dasilva_2019_medicinal_plants`) and 5 more (`hruby_2018_interview_*`)
  before consolidation, and fixed `jiang_2024_*`'s misuse of the `rt`
  column name (now `cov_completion_time_s` -- see memory
  `feedback_rt_column_scope`). See `BATCH_LOG.md`'s "PLOS ONE batch 15"
  entries (worth_retrying resolution, scripting the 25 confirmed-good,
  final resolution of the 7 deferred, user adjudication pass, and
  consolidation) for full DOI-level detail. Two recurring techniques
  worth reusing on future batches: (1) a generic column-prefix
  auto-detector (regex `^([A-Za-z]+)(\d+)$`, group by prefix, require
  >=2 members) for large files with many unlabeled Likert blocks; (2)
  checking each column's own category set rather than trusting a shared
  name prefix, which caught two files (`pecino_2018`, `muir_2025`)
  secretly mixing two different response scales under one numbering
  sequence.

- [x] **`automated_finding/human_review_plos_batch15_final.csv`** (47
  rows, consolidated from `human_review_plos_batch15_deferred.csv` (2
  rows) and `human_review_plos_batch15_worthretrying.csv` (45 rows))
  pasted into the "Human eye" sheet (confirmed 2026-08-02, ben-domingue);
  file gone from disk as expected. Mostly datasets whose numeric columns
  turned out to be derived composite/subscale totals rather than raw
  items, plus a few structurally ambiguous/complex cases.

- [x] **PLOS ONE batch 15 — `automated_finding/biblio_plos_batch15.csv`**
  (53 rows) uploaded to Redivis and pasted into the dictionary sheet
  (confirmed 2026-08-01, ben-domingue); file and all 53
  `irw_output/*.csv` files gone from disk as expected. All 26
  non-duplicate `good` candidates from batch 15 were reviewed in two
  passes: 23 papers processed -> 53 tables total. Includes 1
  non-human-subject table (`muller_2016_dog_inhibition`) included on
  reconsideration since IRW's id/item/resp format doesn't require human
  respondents. Two other non-human candidates were added then removed
  same-day: `fushuku_2023_mouse_temperature` (ben-domingue catch,
  2026-08-01: physiological/biomarker measurement, not a response to any
  item/stimulus) and `gismann_2026_fish_personality` (ben-domingue call,
  2026-08-01: mixed a response-time-like measure -- seconds spent in
  vigorous movement -- into the same resp column as count/index items;
  IRW convention keeps response time in its own `rt` column rather than
  as an item, so dropped rather than restructured, for simplicity). See
  `BATCH_LOG.md`'s "PLOS ONE batch 15" entry (both passes) for full
  per-dataset detail.

- [x] **`biblio_worthretrying_sweep_20260801.csv` (32 rows) uploaded/
  pasted** (confirmed 2026-08-01, ben-domingue): the 10 papers / 32
  tables from the PLOS worth_retrying backlog sweep (see `BATCH_LOG.md`
  entry below) uploaded to Redivis and pasted into the dictionary sheet;
  `biblio_worthretrying_sweep_20260801.csv` and all 32 `irw_output/*.csv`
  files gone from disk as expected.

- [x] **"Human eye" batch — 5 new tables pasted into the dictionary sheet**
  (confirmed 2026-08-01, ben-domingue): `iandolo_2021_asq`,
  `dasilva_2019_hexaco24`, `mendes_2019_snycq`, `tutrin_2020_meq30`,
  `lee_2025_nursing_exam` (combined with the batch 14 rows below into
  `biblio_batch_20260801.csv`, then pasted); `biblio_humaneye_batch1.csv`,
  `biblio_plos_batch14.csv`, `biblio_batch_20260801.csv`, and all
  `irw_output/*.csv` files gone from disk as expected. See
  `BATCH_LOG.md`'s "'Human eye' sheet review follow-through" entry for how
  each was found and what was checked.

- [x] **`yandun2026_language`/`yandun2026_logical_thinking` bug fixed and
  re-uploaded to Redivis** (confirmed 2026-08-02, ben-domingue): `data/
  yandun2026_cognitive.py`'s `SUBSCALES` column ranges were off by one
  (see `BATCH_LOG.md`'s duplicate-dataset entry for the original evidence);
  corrected to language cols 14-17 (4 items) / logical_thinking cols 18-21
  (4 items, was 3), regenerated, and uploaded. `automated_finding/irw_output/cleaned/`
  and `cleaned_index.csv` removed from disk as expected.

- [x] **Nominal/competitions experimental-standard candidates —
  `costa_gine_2023_wpt_matches` (competitions) and `cos101_2026_openended`
  (nominal) uploaded to Redivis** (confirmed 2026-08-02, ben-domingue):
  both `output_noncore/*.csv` files gone from disk as expected. See
  `BATCH_LOG.md`'s "Nominal / competitions experimental-standard search"
  entry, including its dedup-check and conversion-follow-up addenda, for
  full detail; memory `project_alt_data_standards` for the schema
  criteria. Scripts remain in `data/`
  (`costa_gine_2023_wpt_matches.py`, `cos101_2026_openended.py`). A third
  candidate (Boydstun 2021 open-ended poverty-cause survey, DVN/E4AJZF)
  was converted but then ruled out-of-scope by ben-domingue (2026-08-01)
  and removed — don't re-surface it without checking why first.

- [x] **`biblio_comps_padel.csv` / `biblio_nominal_cos101.csv`** (1 row
  each, competitions/nominal Google Sheets — see the two links in memory
  `project_alt_data_standards`) believed pasted (2026-08-02, ben-domingue:
  "I believe these have already been added to the relevant online
  resources" — not independently re-verified; both files are gone from
  disk, consistent with the Dropbox-sync file-loss pattern noted elsewhere
  in this file, discovered 2026-08-02 before confirmation could be
  double-checked). Neither of the two uploaded tables has had a human QC
  pass yet (no established check for `text`-column data, unlike the
  numeric resp-error checks the core standard has — worth a decision on
  what that should look like). `DVN/J9KSHU` remains license-blocked (CC
  BY-NC-SA) and untouched.

- [x] **PLOS ONE batch 14 — `dejesus_2017_{lequesne,sf36,womac,gpm}` pasted
  into the dictionary sheet** (confirmed 2026-08-01, ben-domingue, from the
  continuous/bounded response-scale search): Lopes de Jesus et al. (2017)
  intra-articular ozone knee-OA RCT (10.1371/journal.pone.0179185), CC BY
  4.0, N=98 x up to 4 waves — see the "Human eye" batch entry above for the
  combined biblio file used. See `BATCH_LOG.md`'s "PLOS ONE batch 14" entry
  for full detail.

- [x] **`automated_finding/human_review_merged.csv`** (292 rows) pasted
  into the "Human eye" sheet (confirmed 2026-08-01, ben-domingue): merged
  `human_review` rows from all of `human_review_plos_batch14.csv` +
  `plos_batch{6,9,10,11,12,13,14}_retriage.csv`, deduped internally by
  DOI (412 -> 301) and against the live "Human eye" sheet (301 -> 292
  net-new, 9 already there); file gone from disk as expected.

- [x] **PLOS ONE batch 14 — dairy tie-stall housing survey processed**
  (confirmed 2026-08-01): `robbins_2019_dairy_tiestall` -> 3 tables
  (risk/quality belief, farm-type belief, "has" belief, 3 items each,
  1-7). Item wording wasn't findable in the article text, but the
  column-name structure (b1_*/b2_*/has*) gave a defensible split into 3
  separate scales rather than 1. See `BATCH_LOG.md`'s "PLOS ONE
  worth_retrying backlog sweep" entry (2026-08-01).

- [x] **PLOS ONE batch 14 — Auricular Acupuncture exam-anxiety study
  struck for good** (10.1371/journal.pone.0168338, 2026-08-03): already
  low-priority (N=44); confirmed no new reason to revisit. Row removed
  from `plos_deferred_candidates.csv`.

- [x] **Continuous/bounded-response repo-based discovery (Batch 21) —
  discovered, triaged, retriaged, and hand-reviewed end-to-end** (confirmed
  2026-08-01): 737 English + 378 international candidates merged/deduped to
  1,030 (1,029 after excluding a known OOM-triggering Dataverse file,
  `DVN/EHBGOW`), full `irw_batch_updated.py` triage run (had to be resumed
  twice — see `BATCH_LOG.md`), retriaged with `irw_retriage_ha.py`. **Net
  result: zero immediately-shippable tables this batch** — both promising
  leads need source-paper access before they can be scripted safely (see
  the two items below). See `BATCH_LOG.md`'s "Continuous/bounded-response
  repo-based discovery (Batch 21)" entry for the full per-row accounting.

- [x] **`automated_finding/human_review_continuous.csv`** (21 rows, Batch
  21's `human_review` rows from `irw_retriage_ha.py`) believed pasted into
  the "Human eye" sheet (2026-08-02, ben-domingue: "I believe these have
  already been added to the relevant online resources" — not independently
  re-verified; file is gone from disk, consistent with the Dropbox-sync
  file-loss pattern noted elsewhere in this file).

- [x] **Batch 21 — Romanian teachers' lifelong-learning survey struck**
  (figshare 10.6084/m9.figshare.31836016, N=70, 2026-08-03): genuinely
  real, clean, CC BY 4.0 Likert data but 7 distinct instruments bundled in
  one non-English file, needing per-item reverse-coding judgment calls
  across a non-English instrument — hard-to-recover per steering, struck
  rather than rushed. Not lost, just not pursued: see
  `BATCH_LOG.md`'s "Backlog-resolution pass" entry if revisited later.

- [x] **Batch 21 — visual-impairment functional-mobility kinematics dataset
  struck** (Dataverse `DVN/0LWF5Z`, N=54, 2026-08-03): one fresh WebSearch
  attempt for the source manuscript (title + author-name searches) still
  turned up nothing findable — struck per steering (missing paper blocks
  the NASA-TLX subscale-order mapping, can't guess it).

- [ ] **Large pool of recyclable PLOS search terms still unused** (found
  2026-07-30): batches 1–11 always invented fresh instrument names for
  PLOS ONE discovery without checking whether a term had already proven
  itself against a *different* source (Dataverse/Zenodo/OSF/etc.) in
  `search_terms_log.csv` — those are a different search surface from PLOS,
  so reusing them isn't a duplicate query, and they're already-validated
  real instrument/construct/task names rather than guesses. Filtering
  `search_terms_log.csv` to non-PLOS, English-only rows not yet tried
  against PLOS turned up ~1,200 candidates in one pass; batch 12
  (2026-07-30) used 30, batch 13 (2026-07-31) used 30 more, batch 24
  (2026-08-11) used 30 more (this pass also added a `langdetect` check —
  the earlier plain-ASCII filter had let ASCII-safe non-English terms like
  "Angst"/"dolor"/"Antwortstil" slip through undetected), batch 25
  (2026-08-11) used 30 more (had to hand-filter langdetect's output further
  — several short non-English fragments like "Antwortstil"/"Psychopathie"/
  "Trainingsmotivation" were still mis-tagged `en` on strings this short),
  leaving roughly 1,020-1,050 unused. See `SKILL.md`'s "Alternate discovery source:
  single-journal search (PLOS ONE)" section (term-selection bullet) for
  the exact filtering method. Expect several more batches' worth of
  higher-quality-than-average terms before this pool runs dry — pull from
  it before brainstorming new terms in future PLOS batches.

- [x] **PLOS ONE batch 13 — `biblio_plos_batch13.csv` (7 rows) closed
  out** (confirmed 2026-08-01, ben-domingue): `nelson_2019_ipqrde`,
  `hermans_2015_dm1_rods`, `liu_2025_classroom_interaction`,
  `_willingness_communicate`, `_speaking_selfefficacy`,
  `_foreign_lang_enjoyment`, `wang_2015_donation_decision` (all CC BY
  4.0) uploaded to Redivis and pasted into the dictionary sheet;
  `biblio_plos_batch13.csv` and all 7 `irw_output/*.csv` files gone from
  disk as expected. See `BATCH_LOG.md`'s "PLOS ONE batch 13" entry for
  full per-dataset detail.

- [x] **`automated_finding/human_review_plos_batch13.csv`** (92 rows,
  batch 13's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-08-01, ben-domingue); file deleted
  from the repo.

- [x] **PLOS ONE batches 6/9/12/13 — `worth_retrying` backlog closed
  out** (confirmed 2026-08-01, ben-domingue): full sweep screened all
  ~186 rows at scale; 16 hand-verified and processed to 32 tables (see
  `BATCH_LOG.md`'s "PLOS ONE worth_retrying backlog sweep" entry,
  2026-08-01, for the full list). The remaining 62
  structurally-promising-but-unverified candidates (top 20 by size listed
  in that same `BATCH_LOG.md` entry) were **written off, not pursued**
  (ben-domingue decision, 2026-08-01) — `plos_batch{6,9,12,13}_retriage.csv`
  deleted. If any of those 62 DOIs are wanted later, the scan logs have
  title/DOI/shape but not license — would need re-fetching via
  `irw_discover_plos.py`'s `process_one()` on the DOI.

- [x] **PLOS ONE batch 13 — 3 deferred `good`-flagged datasets processed**
  (2026-08-03): imitation task (`10.1371/journal.pone.0235595`) ->
  `vaporova_2020_imitation`; illusory-body-ownership embodiment
  questionnaire (`10.1371/journal.pone.0277080`) ->
  `preussmattsson_2022_ownership`; situational-motivation EMA
  (`10.1371/journal.pone.0307369`, also resolves the batch-9 entry below)
  -> `strohacker_2024_bmzi_motive`/`_arms_readiness`. See `BATCH_LOG.md`'s
  "Backlog-resolution pass" entry.

- [x] **PLOS ONE batch 12 — `biblio_plos_batch12.csv` (3 rows) closed out**
  (confirmed 2026-07-30, ben-domingue): `page_2025_portrait10.csv`,
  `penningroth_2019_pm_goals.csv`, `penningroth_2019_pm_concerns.csv` (all
  CC BY 4.0) uploaded to Redivis and pasted into the dictionary sheet;
  `biblio_plos_batch12.csv` and all 3 `irw_output/*.csv` files gone from
  disk as expected. See `BATCH_LOG.md`'s "PLOS ONE batch 12" entry for
  full per-dataset detail.

- [x] **PLOS ONE batch 12 — `human_review` rows merged into
  `human_review_merged.csv`; `worth_retrying` backlog closed out**
  (confirmed 2026-08-01): `colomer_perez_2021_self_care`
  (`10.1371/journal.pone.0260827`, from this batch) -> 2 tables
  (Appraisal of Self-Care Agency 24i, SOC-13). See batch 13's entry above
  — remainder written off, `plos_batch12_retriage.csv` deleted.

- [x] **PLOS ONE batch 12 — 2 deferred `good`-flagged datasets resolved**
  (2026-08-03): MnemoCity Task (`10.1371/journal.pone.0161858`) ->
  `rodriguezandres_2016_mnemocity_usability` (processed); children's
  implicit/voluntary attention-in-time study
  (`10.1371/journal.pone.0123625`) struck (62 sheets have 4 different
  column schemas, not a trivial glob+concat). See `BATCH_LOG.md`'s
  "Backlog-resolution pass" entry.

- [x] **PLOS ONE batch 11 — `biblio_plos_batch11.csv` (21 rows) closed
  out** (confirmed 2026-07-30, ben-domingue): 8 papers (`xu_2016_pqb`,
  `fredrickson_2015_mhcsf`, `milavic_2019_psisysf`, `tanck_2021_*` ×2,
  `aguirre_camacho_2021_*` ×2, `conner_2017_*` ×7, `shi_2025_*` ×5,
  `reinwarth_2023_*` ×2, all CC BY 4.0) uploaded to Redivis and pasted
  into the dictionary sheet; `biblio_plos_batch11.csv` and all 21
  `irw_output/*.csv` files gone from disk as expected. Three QC catches
  along the way, see `BATCH_LOG.md`'s "PLOS ONE batch 11" entry:
  `teicher_2015_mace` was **retracted** (ben-domingue caught an odd
  even-number-only response pattern -- the paper confirms MACE severity
  scores are IRT-derived, not raw responses; script and output deleted),
  `aguirre_camacho_2021_*` needed a non-integer filter for EM-imputed
  cells (paper-confirmed), and `shi_2025_maas`/`shi_2025_rrs` had isolated
  single data-entry errors dropped.

- [x] **`automated_finding/human_review_plos_batch11.csv`** (28 rows,
  batch 11's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-07-30, ben-domingue); file deleted
  from the repo.

- [x] **Teicher 2015 MACE S9_File — `biblio_teicher_2015_mace.csv` (12
  rows) closed out** (confirmed 2026-07-31, ben-domingue):
  `teicher_2015_mace_verbal/_nonverbal/_physical/_sexual/_witness_parent/
  _witness_sib/_peer_verbal/_peer_physical/_emot_neglect/_phys_neglect/
  _distress_helpless/_distress_terrified.csv` (all CC BY 4.0) uploaded to
  Redivis and pasted into the dictionary sheet; `biblio_teicher_2015_mace.csv`
  and all 12 `irw_output/*.csv` files gone from disk as expected. See
  `BATCH_LOG.md`'s "Teicher 2015 MACE S9_File raw items" entry for full
  detail, including a list of columns deliberately not shipped (an
  unmapped pilot item, ambiguous peer `Date_*` columns, several unmatched
  household-context columns) that could be revisited if the paper's actual
  survey instrument/codebook
  turns up.

- [x] **PLOS ONE batch 11 — 4 deferred `worth_retrying` datasets resolved**
  (confirmed 2026-08-01): psychological-crisis-coping/physical-activity
  study (`10.1371/journal.pone.0350928`) -> `yang_2026_crisis_coping`, 4
  tables (RRS 22i, PARS-3 3i, Duan coping scale 32i, ERQ 14i);
  `10.1371/journal.pone.0279701`'s q11/q12/q18 -> `reinwarth_2023_domains_wellbeing`,
  3 more tables (the q13/"FLZ" battery turned out to be a derived index,
  not raw items — not shipped). Disordered-eating-in-athletes
  (`10.1371/journal.pone.0257577`) confirmed still too complex to rush
  (~10 bundled instruments across a 665-column file) — remains deferred,
  structure mapped in `BATCH_LOG.md`. See `BATCH_LOG.md`'s "PLOS ONE
  worth_retrying backlog sweep" entry (2026-08-01) for full detail;
  `plos_deferred_candidates.csv` holds this row (consolidated from
  `plos_batch11_retriage.csv`, since deleted).

- [x] **PLOS ONE batch 10 — `biblio_plos_batch10.csv` (19 rows) closed out**
  (confirmed 2026-07-30, ben-domingue): 4 papers (`baudin_2024_static99r`,
  `liu_2022_mice_skills`, `alsyouf_2024_*` ×12, `ozkurt_2026_*` ×5, all
  CC BY 4.0) uploaded to Redivis and pasted into the dictionary sheet;
  `biblio_plos_batch10.csv` and all 19 `irw_output/*.csv` files gone from
  disk as expected. `baudin_2024_static99r` was corrected before upload
  (ben-domingue catch): item 1 ("Age at release") is a polytomous
  person-level attribute, not a repeated behavioral response — moved from
  the item block to `cov_age_at_release`, leaving 9 items. See
  `BATCH_LOG.md`'s "PLOS ONE batch 10" entry for full per-dataset detail.

- [x] **`automated_finding/human_review_plos_batch10.csv`** (53 rows,
  batch 10's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-07-30, ben-domingue); file deleted
  from the repo.

- [x] **PLOS ONE batch 10 — `biblio_plos_batch10_worthretrying.csv` (13
  rows) closed out** (confirmed 2026-07-30, ben-domingue): 5 papers from
  the batch 10 `worth_retrying` pass (`mavromoustakos_2016_*` ×3,
  `burns_2018_*` ×4, `bilotta_2018_*` ×2, `petrowski_2019_sclk9`,
  `schalet_2016_*` ×3, all CC BY 4.0) uploaded to Redivis and pasted into
  the dictionary sheet; `biblio_plos_batch10_worthretrying.csv` and all 13
  `irw_output/*.csv` files gone from disk as expected. See `BATCH_LOG.md`'s
  "PLOS ONE batch 10 worth_retrying pass" entry for full per-dataset
  detail, including the 15 skipped (confirmed aggregate-only/not-item-
  response) and 5 deferred (real items, needs codebook time) candidates
  from the same 26-row pool.

- [x] **PLOS ONE batch 10 — 5 deferred `worth_retrying` datasets, 2
  processed** (confirmed 2026-08-01): chronic fatigue neuromuscular-strain
  study (`10.1371/journal.pone.0159386`) -> `rowe_2016_cfs_strain`, 3
  tables (5 symptoms x 7 waves, BAI 21i, MFI-20); "Lab meets real life"
  thought-sampling study (`10.1371/journal.pone.0184488`) ->
  `kuehner_2017_mw_rumination`, 1 table (resolved the old ambiguous-
  labels note: the t0_* columns are unlabeled composite indices and
  positive/negative_affect are PANAS sums, neither raw items; only
  MW/RUM are genuine raw probe ratings). Remaining 3 confirmed still too
  complex to rush this pass, structure now mapped in `BATCH_LOG.md`:
  French school-subject self-concept study (`10.1371/journal.pone.0230103`,
  richer than originally noted — 5 domain scales x 33 items plus an
  embedded ~32-item Big Five plus grade data), Dutch self/other/meta-
  personality study (`10.1371/journal.pone.0272095`, 1086 cols),
  psychosomatic rehabilitation gender-effects study
  (`10.1371/journal.pone.0256916`, 494 cols). See `BATCH_LOG.md`'s "PLOS
  ONE worth_retrying backlog sweep" entry (2026-08-01);
  `plos_deferred_candidates.csv` holds these 3 rows (consolidated from
  `plos_batch10_retriage.csv`, since deleted).

- [x] **PLOS ONE batch 9 — 25 `worth_retrying`/`recoverable_format` rows
  reviewed** (see below for detail) — resolved 2026-08-01, 3 papers
  processed to 14 tables.

- [x] **PLOS ONE pilot — human_review_plos_batch1.csv (184 rows)** pasted
  into the "Human eye" sheet (confirmed 2026-07-26, ben-domingue); file
  deleted from the repo.

- [x] **PLOS ONE pilot — `good` list fully closed out** (2026-07-26,
  ben-domingue): all 32 originally-flagged candidates hand-reviewed, 21
  processed → 46 tables, all uploaded to Redivis and pasted into the
  dictionary sheet (34 in `biblio_plos_batch1.csv`, 12 in
  `biblio_plos_batch2.csv` — both files deleted, content captured in
  `BATCH_LOG.md`). 11 skipped as confirmed aggregate-only/not-item-
  response/too-small (surgical resident QI and couples synchrony
  explicitly deemed too small by ben-domingue at N=14/N=10). See
  `BATCH_LOG.md` for the full list.

- [x] **PLOS ONE pilot — `biblio_plos_batch3.csv` (82 rows) closed out**
  (confirmed 2026-07-27, ben-domingue): pasted into the dictionary sheet,
  82 tables moved for Redivis upload (includes 4 QC-corrected ones, see
  `BATCH_LOG.md`'s "QC spot-check pass"). See `BATCH_LOG.md`'s
  "worth_retrying pass" entries for the full list of what's in this batch.

- [x] **PLOS ONE pilot — `biblio_plos_batch4.csv` (62 rows) closed out**
  (confirmed 2026-07-27, ben-domingue): pasted into the dictionary sheet,
  62 tables uploaded to Redivis.

- [x] **PLOS ONE pilot — `biblio_plos_batch5.csv` (11 rows) closed out**
  (confirmed 2026-07-27, ben-domingue): pasted into the dictionary sheet,
  11 tables uploaded to Redivis. This closes out the entire N≥100
  `worth_retrying` pool end-to-end.

- [x] **PLOS Mental Health + PLOS Global Public Health discovery run
  completed and retriaged (2026-07-28)** — 168 candidates (100
  `mentalhealth` + 68 `globalpublichealth`), same 22 terms as the PLOS
  ONE pilot. 1 `good`, 17 `human_assistance` → retriaged to 4
  `worth_retrying` + 7 `human_review` (rest dropped). Full run/retriage
  details, the network hiccups hit along the way, and the yield
  comparison to PLOS ONE are in `BATCH_LOG.md`'s "PLOS Mental Health +
  PLOS Global Public Health run" entry (2026-07-28).

- [x] **`automated_finding/human_review_plos_mh_gph.csv`** (7 rows)
  pasted into the "Human eye" sheet (confirmed 2026-07-28, ben-domingue);
  file deleted from the repo.

- [ ] **Decision (ben-domingue, 2026-07-28): backburner PLOS Mental
  Health/Global Public Health, refocus on PLOS ONE.** 1 `good` + 4
  `worth_retrying` candidates from the run above are parked, not
  processed, in favor of returning to the PLOS ONE sub-100
  `worth_retrying` tail below. `plos_mh_gph_triage.csv` (the full
  168-row file) disappeared from disk mid-session (2026-07-28) — same
  Dropbox-sync file-loss pattern as the 2026-07-26 incident noted below,
  not a script bug. DOI/URL/n/items for the 5 parked candidates below are
  preserved here; `plos_mh_gph_retriage_ha.csv` (17 rows, full columns
  incl. license/data_availability) survived and still exists. If the
  full triage file is needed again, DOIs are known and re-running
  `process_one` on them directly is cheap. Parked candidates:
  - **`good`**: "The impact of parkrun on life satisfaction and its
    cost-effectiveness" (`globalpublichealth`, 10.1371/journal.pgph.0003580)
  - **`worth_retrying`**: "Depressive symptoms and its associated
    factors among secondary school..." (271p/5i,
    10.1371/journal.pgph.0002826); "Child maltreatment mediates the
    relationship between HIV/AIDS family..." (285p/228i,
    10.1371/journal.pgph.0001599); "Health care needs survey to improve
    preparedness of community outreach..." (187p/146i,
    10.1371/journal.pgph.0005204); "The effect of biomass smoke exposure
    on quality-of-life among Ugandan..." (1626p/2i,
    10.1371/journal.pgph.0002892)

- [x] **PLOS ONE pilot — entire `worth_retrying` N≥100 pool (81 candidates)
  fully reviewed** (2026-07-27) — every candidate processed or explicitly
  skipped with reasons in `BATCH_LOG.md`. Filtered from 107 to 81 at
  N≥100 per ben-domingue's direction (2026-07-26).

- [x] **PLOS ONE pilot — sub-100 `worth_retrying` tail (26 candidates)
  dropped, not pursued** (ben-domingue, 2026-07-28): too small (N<100
  each) to be worth the review time. `plos_full_triage.csv` /
  `plos_full_retriage.csv` still hold these rows if reconsidered later,
  but no longer block anything. The fresh PLOS ONE discovery pass with
  new search terms this note called for has since run — see batch 6
  below.

- [x] **PLOS ONE batch 6 — `biblio_plos_batch6.csv` (24 rows) closed out**
  (confirmed 2026-07-28, ben-domingue): all 24 tables from the
  15-candidate `good` review — 8 papers (bled_2021 ×2, ruiz_parra_2023
  ×9, najari_2024_bpqsf ×3, odachi_2022 ×3, zhao_2024_erq ×1, li_2021 ×4,
  kang_2015 ×1, ly_2021 ×1) — uploaded to Redivis and pasted into the
  dictionary sheet; `biblio_plos_batch6.csv` and all 24 `irw_output/*.csv`
  files gone from disk as expected.

- [x] **`automated_finding/human_review_plos_batch6.csv`** (89 rows,
  batch 6's `human_review` rows) pasted into the "Human eye" sheet
  (confirmed 2026-07-29, ben-domingue); file deleted from the repo.

- [x] **PLOS ONE batch 6 — `biblio_plos_batch7.csv` (12 rows) closed out**
  (confirmed 2026-07-28, ben-domingue): 12 tables from 8 of the 48
  `worth_retrying` rows (baumgaertner_2018, huang_2016 ×3, grant_2018,
  laksmita_2020, rosharudin_2023 ×2, turner_2022 ×2, gomez_2022,
  yang_2015) uploaded to Redivis and pasted into the dictionary sheet;
  `biblio_plos_batch7.csv` and the 12 `irw_output/*.csv` files gone from
  disk as expected. Before upload, two issues were caught and fixed in
  review (see `BATCH_LOG.md`'s "Retracted after initial processing" and
  the `yang_2015` isolated-data-entry-error fix): a 13th table
  (`stenson_2021_sleep_emotion`) was retracted entirely — its "Rating"
  column was a derived mean/contrast score across trials, not a raw
  per-trial response, per the paper's own Methods text — and
  `yang_2015_ethnic_essentialism` had one isolated non-integer value
  (3.75 on a single item/respondent) dropped as a data-entry error. Both
  findings prompted new standing checks added to `datastandard.md`
  ("Verifying a continuous-looking column is actually a raw response"
  and "Checking for imputed values" — the latter checks the source
  paper's text for imputation language, since non-integer screening alone
  doesn't catch every imputation method).

- [x] **PLOS ONE batch 6 — remaining `worth_retrying` items written off**
  (ben-domingue decision, 2026-08-01): the coping-self-efficacy/sex-
  trafficking study, full-body-mirror-exposure eating-pathology study,
  insight-in-schizophrenia study, Brazilian smoking/FFMQ study, the
  semicolon-delimited PsyCap `recoverable_format` row, and ~26 other
  never-individually-reviewed rows were part of the 62-candidate pool
  from the full batch 6/9/12/13 sweep — not pursued and written off
  (ben-domingue decision, 2026-08-01). `plos_batch6_retriage.csv` and the
  scan logs (`scan_plos_batch{6,9,12,13}_worthretrying.log`) both
  deleted — see `BATCH_LOG.md`'s "PLOS ONE worth_retrying backlog sweep"
  entry (2026-08-01) for the DOI list if reconsidered later.

- [x] **Carver 2017 PUGGS — `biblio_carver_2017_puggs.csv` (8 rows) closed
  out** (confirmed 2026-07-31, ben-domingue): `carver_2017_puggs_pilot1_traits/
  _det_core/_genom_know/_attitudes` and `_pilot2_traits/_det_core/_genom_know/
  _attitudes.csv` (all CC BY 4.0) uploaded to Redivis and pasted into the
  dictionary sheet; `biblio_carver_2017_puggs.csv` and all 8
  `irw_output/*.csv` files gone from disk as expected. See `BATCH_LOG.md`'s
  "Carver 2017 PUGGS genetics-belief questionnaire" entry for full detail,
  including why the two pilots were kept as separate files (different raw
  response formats for the core-ideas items, confirmed from their own
  codebooks) and why pilot 2's true/false items were recoded to
  correct/incorrect while
  pilot 1's Likert items were not.

- [x] **Meloni 2015 disability-representations study —
  `biblio_meloni_2015_disability.csv` (9 rows) closed out** (confirmed
  2026-07-31, ben-domingue): `meloni_2015_deq_oe_parent/_child`,
  `meloni_2015_deq_ce_parent/_child`, `meloni_2015_parent_divers_ed`,
  `meloni_2015_parent_interests`, `meloni_2015_child_disab_knowledge`,
  `meloni_2015_child_ia_satisfaction/_frequency` (all CC BY 4.0) uploaded
  to Redivis and pasted into the dictionary sheet; `biblio_meloni_2015_disability.csv`
  and all 9 `irw_output/*.csv` files gone from disk as expected. The
  fractional (.5) values in `deq_ce_parent`/`_child`/`child_disab_knowledge`
  were checked against the paper's full text (no imputation language found
  anywhere) and confirmed genuine — restricted to exactly the two 1-4
  scales whose own codebook documents a half-point response option, absent
  everywhere else. See `BATCH_LOG.md`'s "Meloni 2015 disability-representations
  study" entry
  for full detail, including why the `DEQ_OE` blocks are raw mention
  counts (0-8) rather than the paper's own published 0/1 presence table,
  and why the misleadingly-named `_TIME` columns are actually a frequency
  scale, not response times.

- [x] **PLOS ONE pilot — all 34 tables from the first pass uploaded and
  biblio-entered** (confirmed 2026-07-26, ben-domingue): first 7
  (muslih_2024_rses, jiang_2021_resilience, kinyanjui_2023_substance_use,
  wilson_2022_kelpie_personality, rashid_2022_mbi, yin_2022_gad7,
  yin_2022_values_importance) plus the remaining 27 (kraft_todd_2017 ×4,
  song_2023 ×3, di_riso_2025 ×2, iwasa_2016 ×4, hui_2024 ×3, liu_2018 ×5,
  uffler_2017 ×2, nabwera_2021 ×1, lu_2017 ×3) all uploaded to Redivis and
  pasted into the dictionary sheet. `biblio_plos_batch1.csv`,
  `biblio_plos_batch1_remaining27.csv`, and all 34 `irw_output/*.csv`
  files deleted from the repo — content fully captured in the sheets and
  in `BATCH_LOG.md`. This first pass of the PLOS ONE pilot is closed out
  end-to-end.

- [x] **Correction on this working directory (2026-08-11, ben-domingue)**:
  earlier entries in this file attributed staging CSVs and
  `irw_output/*.csv` files disappearing from disk to a "Dropbox-sync
  file-loss pattern" (files written here supposedly reverted by a sync
  event from another device). That diagnosis was wrong — ben-domingue
  deletes those files himself, by hand, as part of uploading each table to
  Redivis and pasting its biblio/human_review rows into the sheets. A
  `biblio_*.csv`/`human_review_*.csv`/`irw_output/*.csv` being gone after
  a batch is confirmed is the *expected* end state, not data loss and not
  a `automated_finding/` /Dropbox interaction to route around. Going
  forward: after ben-domingue confirms a batch's rows were pasted, expect
  those files to already be gone — no need to diagnose it, just confirm
  and move on. If a file goes missing *before* confirmation (mid-session,
  before anything was uploaded), that's still worth investigating as a
  real anomaly — this correction only covers the expected post-confirmation
  case. The many "consistent with the Dropbox-sync file-loss pattern"
  notes elsewhere in this file's history are stale explanations for what
  was actually this normal cleanup step; left as-is since they're
  historical log entries, not live guidance.

- [ ] **Gyurkovics/Stafford/Levita conflict-task dataset (osf.io/7vbtr)** —
  by far the strongest find from the batch-18 conflict-task search: trial-
  level Flanker + Simon + SART(go/no-go) data, N=118, fully documented,
  directly relevant to the user's Hedge/Powell/Sumner reliability-paradox
  vignette. Blocked purely on a missing OSF license (no license set on the
  node at all). **ben-domingue emailed the authors 2026-07-17 requesting
  permission — awaiting response.** See `license_blocked_candidates.csv`
  (batch 18 row) for contributor OSF profiles/ORCID. Ready to process the
  moment permission or a license appears.

- [x] **`automated_finding/human_review_conflict.csv`** (1 row: "Stroop test
  dataset", DVN/GINKMU) pasted into the "Human eye" sheet (confirmed
  2026-07-28, ben-domingue); file no longer on disk. CC0, real trial-level
  Stroop latency/accuracy columns appear to be present but buried in a
  ~700-column undocumented Russian-language child-development survey with
  no codebook found — still needs a person to decode the column scheme
  (or locate the source paper) before it can be extracted. See
  `BATCH_LOG.md`'s "Batch 18" entry.

- [ ] **Political Preference China** (`10_7910_dvn_dwplbc.csv`, DVN/dwplbc) — on
  hold: 0-response ambiguity, anchor labels not documented in the source.
  Needs the anchor-label question resolved before it can be processed.

- [x] **SAPA 7 annual releases (2017-2024) pooled into `condon_2024_sapa_personality`
  and uploaded** (confirmed 2026-08-02, ben-domingue): all 7 years share an
  identical 135-item personality item bank (confirmed by hashing headers), so
  pooled into one table with `cov_year` rather than 7 separate tables, per
  ben-domingue's decision. Full pool was ~2.28M respondents/~155.7M rows --
  too large for this pipeline's usual scale -- so a random sample of
  1,000,000 respondents (seed=42) was taken instead; documented in the
  biblio Notes field along with its relationship to the existing
  `sapa_personality`/`icar_sapa` tables (confirmed not redundant with
  either). `irw_output/condon_2024_sapa_personality.csv` and
  `biblio_condon_2024_sapa_personality.csv` gone from disk as expected. See
  `BATCH_LOG.md`'s "Pooled SAPA-Project personality table, 2017-2024" entry
  for full detail.

- [ ] **`human_review` backlog** — several hundred rows accumulated across
  all batches, tracked in the "Automated queue - Human eye" Google Sheet
  (not in this repo). Needs a person to periodically review and either
  process or dismiss entries.

- [ ] **17 OSF candidates blocked only on missing license** (not a content
  problem — see `automated_finding/license_blocked_candidates.csv` for full
  detail: URL, N/items, contributors. Worth an author-permission email per
  `processing_notes/Licensing.txt` if someone wants to pursue them). Three
  are structurally confirmed and ready to process the moment a license
  appears: "The Role of Attentional Bias in Anxiety and Depression"
  (osf.io/ctnaq, N=831, 82 items), "Assessing Creative Self-Efficacy in the
  Spanish Workplace" (osf.io/mksw2, N=405, 4 scales), "Rosenberg Self-Esteem
  Scale in Uruguay" (osf.io/h5g36, N=322, 11 items). The other 14 are
  logged with title/URL/contributors but not yet structurally inspected —
  see the CSV for the full list.

- [ ] **6 items from the English-terms backlog, still needing a person**
  (not another automated attempt) — originally logged to the now-deprecated
  "Human eye" sheet (see `human_review/googlesheet_humaneye.csv` for the
  frozen export): `DVN/HIT56P`
  (no id column, needs cross-file linkage across baseline/followup waves),
  `DVN/S0HEZI` (unredacted PII in every row — real name/email/IP/GPS),
  `figshare 32953286` (mixed item types — usage flags + vignettes +
  derived scores), the Caring Efficacy Scale's unidentified second 13-item
  block (figshare 8177303, alongside the already-processed
  avilesgonzalez2019_ces), `osf.io/zc3pf` (Academic Free License 3.0 — not
  a standard accepted type, needs a call on whether it's acceptable), and
  PIRLS 2023 (University of Pretoria's Figshare instance, bot-blocked,
  needs manual browser access). Full story of how these were found in
  `BATCH_LOG.md`'s "Finishing the 32-candidate backlog" entry.

- [x] **`automated_finding/human_review_lang_pilot.csv`** (1 row: SWAN
  depression/lifestyle data, DVN/HWMJAE) pasted into the "Human eye" sheet
  (confirmed 2026-07-28, ben-domingue); file no longer on disk. See
  `BATCH_LOG.md`'s "Non-English per-language discovery pilot" entry for
  why it couldn't be resolved automatically (real longitudinal item data,
  but the 4 items may span two different SWAN questionnaire modules —
  needs SWAN-codebook access to confirm).

- [x] **Portella 2022 racial-attitudes dictionary/tags fix** believed
  pasted (2026-08-02, ben-domingue: "I believe these have already been
  added to the relevant online resources" — not independently
  re-verified; `dictionary_fix_portella_2022.csv`, `tags_fix_portella_2022.csv`,
  and `irw_output/portella_2022_racial_attitudes.csv` are all gone from
  disk, consistent with the Dropbox-sync file-loss pattern noted elsewhere
  in this file). Replaced the existing
  `racialsocialnormsbrazilianstudents_portella_2022` row (broken processing
  script, never actually live; see `BATCH_LOG.md`'s "User-directed fix"
  entry, 2026-07-16) with a `portella_2022_racial_attitudes` row.

- [x] **Peters 2025 COVID-19 Risk Tool — `biblio_peters_2025_precautions.csv`
  (6 rows) closed out** (confirmed 2026-07-31, ben-domingue):
  `peters_2025_work_precautions`, `_si_current`, `_si_trigger`,
  `_si_intention`, `_hw_frequency`, `_hw_intensity` (all ODbL 1.0) uploaded
  to Redivis and pasted into the dictionary sheet; `biblio_peters_2025_precautions.csv`
  and all 6 `irw_output/*.csv` files gone from disk as expected. See
  `BATCH_LOG.md`'s "Peters 2025 COVID-19 Risk Tool: precaution-checklist
  follow-up" entry for the `*Est`-column decoding mechanism (it's a fixed
  risk-weight/administration flag, not a per-person estimate, despite the
  name). `proximity` (single radiobutton) and `DMQslider.nr.` (single
  slider) remain unshipped — genuinely single-item, can't form their own
  scale.

- [ ] **`tags_fix_peters_2025_precautions.csv` (6 rows) still staged, not
  yet confirmed applied** (2026-07-31) — optional per-table tags entries
  for the 6 precaution tables above, matching the original 16 tables'
  convention. Not yet pasted/applied; file still on disk.

- [ ] **`metadata/tags.csv` missing rows for the existing 16 `peters_2025_*`
  tables** (found 2026-07-31, while adding tags for the 6 new precaution
  tables above): `BATCH_LOG.md`'s 2026-07-17 entry records these 16 rows
  as "written directly into metadata/tags.csv," but none are present now —
  zero case-insensitive matches for "peters" in the file. The corresponding
  `metadata/biblio.csv` rows *are* present and correct (full APA reference/
  DOI/BibTeX confirmed for `peters_2025_att_exp_eval` etc.), so this is
  tags.csv-specific — possibly a metadata-pipeline regeneration overwrote
  the direct edit, or the same Dropbox-sync file-loss pattern documented
  elsewhere in `BATCH_LOG.md`. Not investigated further — worth a look next
  time `metadata/tags.csv` is regenerated or the site-update skill runs.

- [x] **`automated_finding/human_review_cognitive_tasks.csv`** (17 rows,
  from batch 19's cognitive/decision-making-task search) pasted into the
  "Human eye" sheet (confirmed 2026-07-28, ben-domingue); file no longer
  on disk. Included 2 notable cases worth a second look:
  the Nosek & Smyth (2011) math-IAT dataset (DVN/Z3MV4J, N=11,819 — real
  data, needs the paper's PDF codebook to decode 186 cryptic columns safely)
  and the LGBTQ-judges conjoint experiment (DVN/CDLVDH, N=1,249 — a genuine
  conjoint design where the judge-profile attributes are randomized per
  response, conflicting with datastandard.md's itemcov invariance rule; a
  person needs to decide whether to ship a bare id/item/resp file without
  the attribute detail, or treat conjoint designs as out of scope). See
  `BATCH_LOG.md`'s "Batch 19" entry for the full reasoning on all 17 rows.

- [x] **Pipeline improvement: no file-size guard in `irw_batch_updated.py`
  — fixed 2026-08-02.** Batch 19 hit a Dataverse candidate (`DVN/BRCRS5`)
  whose files were six `.dta` files up to 1.4GB each — loading it
  OOM-killed the triage process twice (~21GB RSS on a 30GB machine) before
  it was manually excluded and the run resumed. Batch 20 hit the identical
  failure mode again (`DVN/EHBGOW`, six `.dta` files up to 1.58GB each) —
  two batches in a row. Fixed with a `MAX_FILE_BYTES` (200MB) ceiling in
  `irw_batch_updated.py`, checked two ways: (1) each repo resolver
  (Zenodo/Figshare/Dryad/Dataverse/OSF) now reads the file size the API
  already reports and skips/flags oversized tabular files before ever
  downloading them; (2) `polite_get()` streams the response and aborts
  early (`FileTooLarge`) as a backstop for sources that don't expose size
  upfront (e.g. PLOS supplementary files in `irw_discover_plos.py`).
  Oversized files get a new `file_too_large` flag (distinct from
  `no_usable_file`) so they're visible for manual/future handling rather
  than silently dropped or crashing the run. Verified against the actual
  `DVN/EHBGOW` record: the 1.58GB file and six other >200MB `.dta` files
  are now correctly skipped while two small legitimate `.xlsx` files on
  the same record still get triaged normally. `irw_process_queue.py`
  (retired/stale per `README.md`) updated to match the new
  `resolve_data_files()` 3-tuple return signature for consistency, though
  it was already broken on an unrelated pre-existing import error
  (`QUEUE_SHEET_URL` no longer exists in `irw_discover_updated.py`) and
  wasn't otherwise touched.

- [x] **Pipeline improvement: `coerce_to_irw()`/`load_table()` gave up too
  early on two specific, recurring, recoverable patterns — fixed
  2026-07-30.** Found auditing the "Human eye" queue sheet: every row a
  human has ever marked eligible from it (13/13, including issues
  #1559–#1565) failed triage with the exact same reason, "Could not
  confidently identify item columns," and in every case the file was real,
  usable item-response data defeated by (a) a header row that isn't row 0
  (Qualtrics/journal-supplement exports — also hit repeatedly in past PLOS
  batches, see `cormier_2024_*`/`jordan_2020_*` in `BATCH_LOG.md`) or (b)
  item columns whose headers are the literal (often non-English) question
  text with Likert responses stored as text labels rather than numeric
  codes, which `_ordinalish()` doesn't recognize. Full writeup in
  `README.md`'s Step 1b note. Fixed:
  - `load_table()` now detects a header-offset read (>50% `Unnamed:`
    columns) and retries `header=1..4` before accepting a broken table —
    see `_looks_header_offset()`. Only fires when the default read already
    looks broken, so it can't change a working read.
  - `coerce_to_irw()`'s Case C now checks excluded columns for text-coded
    Likert categories (`_textish_likert()`) before giving up, and notes it
    explicitly rather than folding it into the generic "could not identify
    item columns" message. Detection only, deliberately not auto-recoded —
    category set/direction still needs a human, same as datastandard.md
    already requires for numeric `resp` columns.
  - `irw_retriage_ha.py` gained a rule (before RULE 7) that routes this new
    note to `worth_retrying` instead of the `human_review` catch-all, so
    it surfaces ahead of genuinely ambiguous rows next retriage run.
  Not yet re-run against a live batch to confirm real-world recovery rate —
  worth checking next time `human_assistance` rows come through.

- [ ] **Trusz 2025 NFI dataset (`DVN/DWCBOE`) has unprocessed CFA (N=437)
  and test-retest-stability (N=54) subsamples** beyond the EFA sample
  already processed as `trusz_2025_nfi`. Not picked up because the
  combined N=1097 file mixing all sub-studies has an unreliable id column;
  would need per-file (not per-combined-file) processing. Low priority —
  noted for whoever wants the extra ~500 respondents.

- [x] **`knight_2026_crt`** (2026-07-29, one-off user-supplied lead, not
  from batch discovery) pasted into the dictionary sheet and uploaded to
  Redivis (confirmed 2026-07-29, ben-domingue). Processed from Knight et
  al. (2026, *Psychological Science*) — double-blind RCT of intranasal
  testosterone vs. placebo on the 7-item Cognitive Reflection Test, OSF
  node `37ycj` (`TED_CRT_longdata.csv`), CC0. Script:
  `data/knight_2026_crt.py`. Output was `irw_output/knight_2026_crt.csv`
  (6,993 rows, 999 ids, 7 items, resp 0/1, treat 0/1, rt in seconds —
  back-transformed from the source's natural-log RT via `exp()`, verified
  against Qualtrics `Page Submit` timing elsewhere in the same raw dataset,
  which is natively in seconds). `biblio_knight_2026_crt.csv` deleted from
  the repo.

- [x] **PLOS ONE batch 8 discovered and processed** (confirmed 2026-07-29,
  ben-domingue): fresh discovery run (`irw_discover_plos.py`, 30 new
  instrument/task terms not previously searched, e.g. HEXACO, Cognitive
  Reflection Test, Ultimatum Game; logged in `search_terms_log.csv`).
  1,500 candidates -> 7 `good` + 261 `human_assistance`. Retriage
  (`irw_retriage_ha.py`) on the `human_assistance` bucket gave 42
  `worth_retrying` + 1 `recoverable_format` + 80 `human_review` + 91
  `aggregate_continuous` + 47 `not_item_response`. All 43
  `worth_retrying`/`recoverable_format` rows and all 7 `good` rows were
  downloaded and hand-inspected (see "Batch 8 worth_retrying triage" and
  "Batch 8 good-candidate review" in `BATCH_LOG.md` for the per-row
  calls). 11 papers processed -> 40 tables — `lorenz_2016` (PsyCap
  CPC-12, 7 tables), `sleboda_2021_risk_benefit`, `tiemensma_2018_iesr`,
  `alsuhibani_2022` (conspiracy/paranoia, 3 studies, 10 tables —
  LOC/SERS/GCBS merged across studies confirmed identical by the paper's
  own Methods text, ids offset per study; see `datastandard.md`'s new
  "same instrument administered to multiple sub-studies" edge case, added
  this session), `niazi_2020_moral_foundations` (2 tables),
  `kim_2025_presleep_arousal` (4 tables), `luo_2021_acculturation` (5
  tables), `reinecke_2018_online_vigilance`, `queiros_2018_qcae`,
  `esiason_2024_nmosd` (patients+caregivers merged same way as
  `alsuhibani_2022`, 7 tables), `addy_2021_sdq_ghana`. All 40 output
  files passed the per-item rare-value data-entry-error scan and
  ben-domingue's review; `biblio_plos_batch8.csv` and all 40
  `irw_output/*.csv` files are being removed from disk as expected
  (pasted into the dictionary sheet / uploaded to Redivis).

- [x] **`automated_finding/human_review_plos_batch8.csv`** (80 rows,
  batch 8's `human_review` rows) pasted into the "Human eye" sheet
  (confirmed 2026-07-29, ben-domingue); file deleted from the repo.

- [x] **PLOS ONE batch 8 — 3 deferred datasets resolved** (2026-08-03):
  Clinton-voter activism longitudinal study
  (`10.1371/journal.pone.0221754`) -> `dwyer_2019_clinton_cesd`/
  `_activist` (processed); Chinese EFL learning study
  (`10.1371/journal.pone.0280919`) struck (row mismatch traced to a
  non-unique key with inconsistent demographics, not a clean dedupe);
  emotional-eating chain-mediation study (`10.1371/journal.pone.0280701`)
  -> `yang_2023_emotional_eating_eesr`/`_cesd`/`_uppsp`/`_ders`
  (processed). See `BATCH_LOG.md`'s "Backlog-resolution pass" entry.

- [x] **PLOS ONE batch 8 — VR-empathy and phonological-loop deferred
  datasets resolved** (confirmed 2026-07-29, ben-domingue) — the "second
  closer look" both turned out to be quick once checked against the
  papers' Methods text. `herrera_2018_vr_empathy.py`
  (`10.1371/journal.pone.0204494`) -> 4 tables:
  `herrera_2018_iri`/`_beliefs_about_empathy` (merged across the paper's
  2 studies, confirmed identically administered, ids offset per study),
  `_attitudes_homeless`/`_se_d_items` (Study 2 only). Two more candidate
  tables (`_ios`, `_dehumanization`) were caught in review as single-item
  measures and dropped — IRW does not accept single-item scales
  regardless of data quality (new standing rule, see memory
  `feedback_no_single_item_scales`). `meng_2017_referent_assignment.py`
  (`10.1371/journal.pone.0187368`) -> 1 table: the triage-flagged
  `Base-Assignment`/`Shift`/`Re-Assignment`/`Follow-RA` columns turned
  out to be derived composites (each an AND of two raw scores, per the
  paper's own coding description) rather than raw items — the actual
  5 raw per-trial correctness scores (`EQ`/`AQ`/`EQ2`/`AQ2`/`AQ3`) were
  used instead, with a `wave` column encoding the block/trial order (74
  children x 4 trials). All 5 output files uploaded to Redivis;
  `biblio_plos_batch8_deferred.csv` pasted into the dictionary sheet and
  being removed from disk as expected.

- [x] **PLOS ONE batch 9 discovered, triaged, and 5 of 7 `good` candidates
  processed** (confirmed 2026-07-29): 28 new terms, 1,261 candidates -> 7
  `good` + 184 `human_assistance`. 5 papers processed -> 9 tables
  (`xiong_2025_dass21`, `su_2025_health_behaviors`, `wakui_2023_who5`,
  `liu_2025_mlq`/`_positive_cognition`/`_learning_motivation`,
  `zamzuri_2021_rpap_risk_perception`/`_attitude`/`_practice`); 1 skipped
  (SoroTouch, N=10 derived engagement metrics, not raw items); 1 deferred
  (situational-motivation EMA, ambiguous item structure -- see below). Full
  per-dataset reasoning in `BATCH_LOG.md`'s "PLOS ONE batch 9" entry. All 9
  `irw_output/*.csv` files uploaded to Redivis and removed from disk
  (confirmed 2026-07-29, ben-domingue).

- [x] **`automated_finding/biblio_plos_batch9.csv`** (9 rows) pasted into
  the dictionary sheet (confirmed 2026-07-29, ben-domingue); file deleted
  from the repo. Re-staged as plain comma-delimited CSV after a same-day
  tab-delimited/xlsx detour was tried and reverted -- see `BATCH_LOG.md`
  and memory `feedback_dict_format` for why.

- [x] **`automated_finding/human_review_plos_batch9.csv`** (63 rows,
  batch 9's `human_review` rows from `irw_retriage_ha.py`) pasted into the
  "Human eye" sheet (confirmed 2026-07-29, ben-domingue); file deleted
  from the repo.

- [x] **PLOS ONE batch 9 — 25 `worth_retrying`/`recoverable_format` rows
  hand-reviewed** (confirmed 2026-08-01): `10.1371/journal.pone.0199480`
  (body image/eating/QoL) -> `silva_2018_body_image`, 5 tables;
  `10.1371/journal.pone.0206800` (MSCS validation) -> `trevisan_2018_mscs`,
  2 tables; `10.1371/journal.pone.0169375` (Chinese cancer-patient
  exercise) -> `liu_2017_cancer_exercise`, 7 tables (5 confidently or
  tentatively named instruments, 2 shipped under generic names pending a
  paper-text pass). `0202818` (trust/distress Accra) confirmed too small
  (5 items) to pursue; `0322635` (exercise/eating/body dissatisfaction)
  confirmed all pre-computed composite scores, no raw items. Remaining
  ~19 smaller-N rows + the semicolon-delimited `0263766` not individually
  reverified — see `BATCH_LOG.md`'s "PLOS ONE worth_retrying backlog
  sweep" entry (2026-08-01) for the full disposition and the shared
  62-candidate remaining pool across batches 6/9/12/13.

- [x] **PLOS ONE batch 9 — situational-motivation EMA study resolved**
  (`10.1371/journal.pone.0307369`, 2026-08-03, same DOI as the batch-13
  entry above -- resolved once, closes both) -> `strohacker_2024_bmzi_motive`/
  `_arms_readiness`. See `BATCH_LOG.md`'s "Backlog-resolution pass" entry.

- [x] **PLOS ONE batch 16 — `biblio_plos_batch16.csv` (7 rows, `good`
  candidates) closed out** (confirmed 2026-08-02, ben-domingue):
  `daiku_2021_dirty_dozen`/`_lie_scale`/`_lying_frequency`,
  `horiuchi_2024_attachment`/`_dissociation`/`_rsmsm`,
  `jimenezherrera_2022_moral_sensitivity` (all CC BY 4.0) uploaded to
  Redivis and pasted into the dictionary sheet; `biblio_plos_batch16.csv`
  and its 7 `irw_output/*.csv` files gone from disk as expected. New
  standing min-N rule (`feedback_min_sample_size`) applied for the first
  time: 3 `good` candidates dropped for N<50, 4 in the 50-99 band declined
  by ben-domingue when asked, 1 (`0235595`) was a duplicate of an
  already-deferred batch-13 candidate. `qiang_2025_red_tape` (`0327359`)
  turned out to be an exact duplicate of an already-shipped batch-15 paper
  -- not reprocessed. See `BATCH_LOG.md`'s "PLOS ONE batch 16" entry for
  full per-dataset detail.

- [x] **PLOS ONE batch 16 — `biblio_plos_batch16_worthretrying.csv` (11
  rows) closed out** (confirmed 2026-08-02, ben-domingue): `pavic_2022_
  vaccine_conspiracy`/`_natural_immunity`/`_healthcare_trust`/
  `_science_literacy`, `tuason_2021_covid_coping_enjoy`/
  `_loneliness_emotional`/`_loneliness_social`/`_wellbeing`/
  `_sense_of_agency`, `gumus_2025_dietarian_identity`,
  `machado_2020_cat_separation` (all CC BY 4.0) uploaded to Redivis and
  pasted into the dictionary sheet; `biblio_plos_batch16_worthretrying.csv`
  and all 11 `irw_output/*.csv` files gone from disk as expected. See
  `BATCH_LOG.md`'s "PLOS ONE batch 16" entry for full detail, including 6
  more top-N `worth_retrying` rows that were inspected and skipped
  (confirmed composite/derived data, not raw items) and 2 more deferred to
  `plos_deferred_candidates.csv` (Sierra Leone health-insurance WTP survey
  needing a codebook; trust/proximity vaccine-propensity study, only 4
  heterogeneous items).

- [x] **`automated_finding/human_review_plos_batch16.csv`** (155 rows,
  batch 16's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-08-02, ben-domingue); file gone
  from disk as expected.

- [x] **PLOS ONE batch 16 — ~53 of 66 genuinely-new `worth_retrying` rows
  written off for good** (2026-08-03): confirmed unrecoverable -- the
  DOI/title/N list was already lost with `plos_batch16_retriage.csv`
  (deleted 2026-08-02); reconstructing it means re-running `process_one`
  on the whole pool from scratch, out of scope for a resolution pass. No
  further action possible without a fresh discovery re-run.

- [x] **PLOS ONE batch 16 — Swiss summer camp socio-emotional study
  processed** (`10.1371/journal.pone.0276665`, 2026-08-03) -> 3 tables
  (`gerber_2022_altruism`, `_selfesteem`, `_eas_temperament`). The paper's
  Measures section cleanly mapped every column. See `BATCH_LOG.md`'s
  "Backlog-resolution pass" entry.

- [x] **`automated_finding/biblio_pmc_batch3.csv`** (18 rows, PMC weekly
  batch 3, 2026-08-12) uploaded to Redivis and pasted into the dictionary
  sheet (confirmed 2026-08-12, ben-domingue); file gone from disk as
  expected. See `BATCH_LOG.md`'s "PMC weekly high-yield
  discovery+triage batch 3" entry for full detail.

- [ ] **PMC batch 3 — deferred recoverable candidates** (2026-08-12), not
  processed this pass, each documented in `BATCH_LOG.md`:
  - `10.7717/peerj.13162` (Chilean adolescent mothers, n=79) -- 6 real
    subscales (selfreg, adaptivefunctioning, affect, socialcommunication,
    interaction, socialemotionaldevelopment), each with a `_sum` composite
    to exclude. Straightforward but time-consuming (6 subscales to verify).
  - `10.7717/peerj.1464` (Lee et al. 2015) -- the multi-informant JTCI
    temperament battery (child/mother/father-report, 7 subscales each,
    i-/m-/p- prefixed) in the same file as the already-shipped
    `lee_2015_cbcl`. Needs the paper's Methods text to confirm which
    subscale abbreviation maps to which JTCI dimension per informant.
  - `10.7717/peerj.19326` (executive functioning QoL, Spanish, n=53) --
    SF-12 + a 23-item EPY scale, stored as SPSS labeled-categorical values
    needing decode. N=53 also needs a ben-domingue go/no-go (50-99 band).
  - `10.7717/peerj.19467` (Buteyko asthma) and `10.7717/peerj.16864`
    (medical students cognitive/affective) -- both have real text-Likert
    item columns but no confirmed category order; need the paper's
    response key before recoding.
  - `10.7717/peerj.18378` (parenting styles, NSSI) -- `wrong_file_selected`,
    not actually reviewed: the .xlsx is a codebook, real data is in an
    unopened `.rar`.
  - `10.7717/peerj.10904` (cardiovascular coping, n=42) -- a marginal
    3-item x ~5-timepoint SAM battery, small n/item count, not extracted.

- [x] **`irw_discover_pmc.py` triage bug**: `'int' object has no attribute
  'lower'` on `10.7717/peerj.18828` (COVID-19/children study) during PMC
  batch 3 (2026-08-12) -- real pipeline bug, not yet root-caused or fixed. — **fixed 2026-08-24, closed 2026-08-25**: this is the numeric-spreadsheet-header bug; `load_table()` now coerces column labels to `str` on every read path, which is exactly the `'int' object has no attribute 'lower'` failure. Nothing further to root-cause.

- [ ] **2 `download_failed` rows from PMC batch 3** (`10.7717/peerj.17440`,
  `10.7717/peerj.2421`) -- legacy `.xls` files, sandbox was missing
  `xlrd`. Retry manually with `pip install xlrd`.

- [x] **2 of 3 `worth_retrying` scripts from the 2026-08-15 PLOS monthly
  re-run written and shipped** (see `BATCH_LOG.md` entry same date):
  `data/islam_2022_online_addiction.py` (`10.1371/journal.pone.0279062`,
  N=428) -> 5 tables (`islam_2022_igds9sf/_gdt/_phq9/_gad7/_bsmas`,
  `Sum_*` composite columns dropped); `data/huo_2025_construction_
  partnerships.py` (`10.1371/journal.pone.0334555`, N=230) -> 4 tables
  (`huo_2025_project_uncertainty/_relationship_conflict/
  _relationship_continuity/_political_skill`; item-prefix-to-construct
  mapping confirmed against the paper's own Measures section item counts,
  not just column names -- the prefixes don't literally spell out the
  construct: `u`=uncertainty, `r`=conflict, `c`=continuity, `p`=political
  skill). `biblio_plos_monthly_2026-08-15.csv` (9 rows) uploaded to
  Redivis and pasted into the dictionary sheet (confirmed 2026-08-15,
  ben-domingue); file and all 9 `irw_output/*.csv` files gone from disk
  as expected.
- [ ] **1 of 3 `worth_retrying` candidates from the 2026-08-15 PLOS monthly
  re-run still open**: `10.1371/journal.pone.0341726` (N=385) -- real
  PSS-10/GAD-7/PHQ-9 item-level data confirmed present (0-3/1-4 Likert
  values verified) but buried under extremely verbose full-question-text
  column headers mixed with one-off demographic/yes-no items; needs
  careful column-range identification before a script can be written.

- [ ] **2 CC0 `human_assistance` rows from the 2026-08-17 post-restoration
  Dataverse run** (`monthly_triage_weekly_2026-08-17.csv`). Both were flagged
  solely by the ">50 unique resp values after melt" continuous/aggregate
  heuristic, so both need the usual manual look for real ordinal items:
  - `10.7910/DVN/TG1GYA` "Replication Data for: Wellbeing, Race, Rurality and
    SES" -- N=530,920, 42 items, CC0. The large one; worth doing first.
  - `10.7910/DVN/X2C2PL` preoperative anxiety / gynecologic surgery, Vietnam
    -- N=394, 59 items, CC0.

- [x] **DONE 2026-08-17. Harvard Dataverse WAF block lifted; throttled first
  run (1b) completed and clean -- see BATCH_LOG.md "Throttled first
  post-restoration Dataverse run".** 15-term dataverse-only pass: all terms
  searched live, all log rows recorded `sources=dataverse` with no `blocked=`,
  5 candidates, no WAF signal (the lone 403 was an author-restricted file).
  Normal cadence is cleared to resume -- `--mode full`, full source set,
  scheduled routines. Two CC0 `human_assistance` rows came out of it and are
  tracked as a separate open item below. Original context retained:
  HMDC replied on ticket
  #423164 that scripted API access restrictions have been lifted; they are
  watching traffic and warn it may be re-disabled if load spikes back.
  Verified locally the same day: `/api/info/version` -> 200, and a live
  `/api/search?q=grit+scale` returns real dataset JSON (no challenge).
  Everything self-heals with no code change -- the `--since` window reopens
  from 2026-08-03, the DataCite publisher backfill switches itself off, and
  the retryably-held candidates re-enter triage on the next run. The only
  remaining work is (1b): **make that first pass small and slow.** Their
  warning makes this a courtesy we owe them, not just prudence.
  Historical record of the block follows.

  `dataverse.harvard.edu` had returned
  `x-amzn-waf-action: challenge` / HTTP 202 / 0 bytes on every path,
  from cloud *and* local IPs -- site-wide, not us being flagged, and no
  UA/backoff fix existed. The pipeline was made to degrade honestly rather
  than silently (blocked sources are excluded from the logged `sources=`, and
  DataCite backfills the publisher for *discovery*, and triage now flags
  blocked candidates retryably instead of retiring them), so nothing was
  silently lost. Two things remained:
  (1) **ANSWERED 2026-08-17 -- ticket #423164. Nothing further to ask.**
  Harvard University IT has *deliberately and temporarily* restricted
  non-browser API access site-wide, in response to higher-than-usual traffic
  hurting site performance and availability. They expect to restore API
  access once traffic is under control and a permanent solution is in place.
  So: no allowlist was granted, the restriction is intentional rather than a
  misconfiguration, and it is expected to lift on its own. **Do not escalate
  or chase this** -- pressing for a personal exception while they are
  actively shedding load is both unlikely to work and bad form toward a
  repository IRW depends on. Just wait. (Our own footprint is small enough
  that we are near-certainly not the cause: ~500 discovery requests over
  ~4 minutes at 0.5s spacing, plus triage at 1.5s/domain.)
  Ticket: https://help.hmdc.harvard.edu/Ticket/Display.html?id=423164

  (1b) **Throttle the FIRST run after access is restored** -- see the
  "recovery burst" note in BATCH_LOG.md (2026-08-17). Our self-healing
  design means restoration triggers a compounding spike at exactly the site
  that just asked for relief: the dataverse `--since` window reopens all the
  way back to 2026-08-03 (wider every day it stays blocked), all 100 terms
  are already falling back to a 90-day lookback since datacite joined
  DEFAULT_SOURCES, and every candidate held retryably in the meantime
  re-enters triage at once. Make the first post-restoration pass small and
  slow (subset of terms, reduced `max_pages`, raised `PER_DOMAIN_DELAY`),
  then return to normal cadence.
  (2) ~~Re-probe occasionally~~ **DONE -- cleared 2026-08-17.** Keep the probe
  (`curl -sI https://dataverse.harvard.edu/api/info/version`) in mind as the
  first diagnostic if dataverse yields collapse again; HMDC explicitly said
  they may have to re-disable scripted access if traffic spikes.

  **Do NOT wire up OAI-PMH** (an earlier version of this item recommended
  it -- wrong). `dataverse.harvard.edu/oai` does return 200 and is not
  behind the challenge, but the feed is dead for our purposes: `from=`
  is honored correctly, and `from=2025-06-01` already returns
  `noRecordsMatch`, so nothing newer than ~mid-2025 is in it. It also
  exposes only 42 curated sets (AfricaRice, Bioversity, CGIAR...), not
  Harvard's general holdings. It cannot discover new datasets, which is the
  entire job.

  **Also do not engineer around the challenge** (headless-browser token
  minting, solver services). It circumvents an access control the operator
  deliberately put up, it breaks whenever they retune it, and it puts a
  crawler that identifies itself as Stanford's IRW in an adversarial
  posture with a repository the project depends on long-term. The UA
  already declares itemresponsewarehouse@stanford.edu -- keep asking
  through the front door.
