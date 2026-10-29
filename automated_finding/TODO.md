# IRW Automated Finding — TODO

## RELEASED 2026-10-29 (ben-domingue) — both of the day's uploads are live

86 tables and 885,864 responses: the 64-table 2026-10-28b/c batch and the
22-table 2026-10-29 leads batch. Plus the `gries_2011_moral_foundations`
replace that dropped `cov_state`. Nothing from 2026-10-29 is awaiting upload or
release any more.

- [ ] **FIRST THING NEXT SESSION, and it is cheap: refresh `live_tables.csv`,
  then run `check_issues_page.R`.** The five `itemtext_issues.qmd` entries owed
  for this batch could not be written before the release, because a note is DUE
  only once the table is live and the checker reads liveness from
  `itemtext/live_tables.csv` -- a committed snapshot last taken 2026-10-28,
  which predates it. `itemtext/refresh_live_tables.py` updates the snapshot;
  the checker then reports the five as DUE and they can be drafted with
  `draft_issues_qmd.R` and pasted, the way the 15 `batch_742` entries were on
  2026-10-29 (datapages/irw#405). The five: `senge_2025_disposal_frequency`,
  `marsalek_2026_ai_attitudes`, `lotfi_bejestani_2023_moral_distress`,
  `andreu_sanchez_2023_information_sources` and `_lifestyle`.

  Apply the bar to each rather than pasting all five. Two look likely to fail
  it: `lotfi_bejestani_2023_moral_distress`'s note is about a DATA oddity
  (responses coded 7 against a documented 0-6 scale) on a table that ships no
  item text at all, and the two `andreu_sanchez_2023_*` notes describe a normal
  bilingual administration where the deposit published both languages -- no
  IRW-generated text and no mismatch. A note dropped as below the bar goes in
  `itemtext/fixes/issues_page_dropped.csv` with a reason, so it stops being
  re-reported.

- [ ] **The covariate-label harvest is now unblocked** for `galanis_2025_*` and
  `aksin_2023_*` x `cov_department`, which was waiting on this release.

## Connector changes 2026-10-29 — two open questions, one deadline

Full write-up in `BATCH_LOG.md` (2026-10-29b), PR #3303. `surf` and `scholars_portal`
are out of the default source set (0.4% / 0.8% shipped rate), and
`from_psycharchives` is in.

- [x] **The relevance gate was widened rather than bypassed (2026-10-29c).**
  Ben took the vocabulary option. Found underneath it: `_matcher()` wrapped
  every term in `\b...\b`, so a dozen entries written as stems had never
  matched anything -- a trailing `*` now marks a stem. With the es/de/fr/nl
  raw/primary-data words added, 148 of 258 PsychArchives records pass where
  124 did, nothing that passed before fails, and over all 3,434 historical
  lead titles the change admits 2 more. No per-source exemption was built;
  revisit only if a later sweep still shows this bleeding.

- [ ] **Email the Wharton Credibility Lab about ResearchBox API access.**
  `researchbox.org` returns ModSecurity 406 to the scout UA, so there is
  nothing to measure and no connector to write; it mints no DOIs of its own
  and backs up to Zenodo, so part of it may already arrive. Template in
  `processing_notes/Licensing.txt` is the wrong one — this is an access
  request, not a licence request.

- [ ] **OSF Projects closes: no new projects from 2026-11-16, read-only from
  2027-02-19.** Confirmed against UW Libraries and Duke, not just the blog.
  Public projects keep their DOIs; private ones may be removed later on 12
  months' notice. Registries and Preprints unaffected. Two consequences for
  this pipeline: any OSF-hosted candidate still sitting in a leads file should
  be worked before February rather than after, and the standing "check
  `public:` before trusting a `?view_only=` node" rule
  (`project_pmc_prolific_private_osf`) has a shelf life now.

- [ ] **The 2026-10-29 sweep now running predates both changes** (it loaded
  the old module): it will return `surf`/`scholars_portal` rows, which are to
  be filtered out of the candidate file before triage rather than triaged, and
  it queried no psycharchives. A psycharchives-only pass over the same 135
  terms is worth running after it (~6s/query/field).

## NEXT UP, at Ben's request (2026-10-29)

- [ ] **Work `10.5683/sp3/wcun0s` first: 23,781 respondents x 38 items.** A
  Borealis deposit, `cc-by-nc`, `recoverable_format`, file `gpo-ai_data.csv`.
  **No decision is owed on it** -- NC proceeds under `datastandard.md`'s
  2026-10-01 ruling, with the restriction propagating through
  `Derived_License`. It is the largest row in
  `leads/nc_licence_pending_ruling_2026-10-18.csv`, and bigger than anything in
  the 2026-10-29 batch.

  That file's other 55 rows are the same shape and the same non-decision: its
  own `status` column reads "todo: NC is a lead -- the filter was aligned with
  datastandard.md's 2026-10-01 ruling on 2026-10-19". 27,697 respondents in
  total, 54 of 56 plainly `cc-by-nc` or `cc-by-nc-sa`. They were being carried
  in this file as if they needed a ruling; they need working.

- [ ] **Before asking Ben for a licence or rights ruling, check whether one
  already exists.** Searched 2026-10-29 after several questions were put to him
  that his own written rules answered. The rules live in four places:

  1. `datastandard.md` ss "Before you start" -- the data-licence decision table
     (ruled 2026-10-01), the flat N>=100 floor and the >=3-item floor (ruled
     2026-10-19).
  2. `itemtext/instrument_rights_register.csv`, the `rule` column -- 379 rows
     carrying prior rulings as citable precedent.
  3. `irw_validate/rights.py` -- the write-path enforcement, whose docstring
     holds the "a hit is a lead, a miss is not an all-clear" rules.
  4. `processing_notes/Licensing.txt` -- the permission-request template for
     the no-licence branch.

  Three questions that had been carried as open were already governed:

  - **Third-party data inside a permissively licensed replication package.**
    `datastandard.md`: "Scraped or relabelled third-party data ... **do not
    host**, even under a permissive licence. The re-uploader's licence does not
    clear data they did not own; the originator's terms govern." That is the
    Afrobarometer / ESS / PISA / Caucasus Barometer case, and the four
    closures on 2026-10-29 were correct by rule, not by judgement.
  - **A named third-party instrument with no located grant.** The 2026-10-15
    ruling (counsel 2026-10-08 plus the Stanford library reply) already makes
    it a `hold`, not a permission. So the CSES, Neff's SCS, the SPIN and the
    other instruments listed in this file as "needs a rights call" do not need
    one -- `hold` IS the ruled outcome, and writing the row is agent work. A
    call is only wanted to move one off `hold`.
  - **A 4-item table.** The item floor is 3, so 4 clears it; `dvn/vidgon` and
    `zenodo.22035093` were deferred on thinness against a rule that permits
    them.

  What is NOT covered by a written rule, and so is genuinely Ben's: whether to
  correct an already-published table (corpus trust), and any case
  `datastandard.md` ends with -- "Anything that fits none of these goes to
  ben-domingue."

## ALL SHARDS RELEASED 2026-10-20 (ben-domingue)

Ben released every shard on 2026-10-20, after the 87-table repos batch and its
7 item text tables went up. So **every item in this file written as "after the
release", "at upload" or "release is owed" is now DUE, not pending** -- there
are at least eight such bullets below, dating back several batches, and they
were all waiting on this one event.

The one that gated the others is **done**:

- [x] **`metadata/covariate_labels/build.py` run 2026-10-21, merged as PR
  #3153.** One run covered every batch's pending harvest: +8,198 rows, none
  removed, for 14,604 rows over 836 tables and 3,496 table x covariate pairs,
  with `coverage.csv` recording all 3,710 pairings (3,480 included, 214
  excluded, 16 withheld). The ~8,000-line estimate was right. Seven reviewed
  `covariate_labels/institutions.csv` lines went in with it, cutting the
  build's unreviewed-institution warnings from 22 to 2; the two that remain
  (`hernandez_martinez_2025_math_attitudes` cov_institution,
  `yang_2026_appreciative_education` cov_school_runs_ae) are unruled on purpose
  -- their source column could not be identified in the harvest logs, so they
  stay withheld by default and keep warning. This stays a manual stage (#1775):
  no scheduled job will ever run it, so the NEXT release owes it again.

- [ ] **36 of the 499 covariate-label harvests produced an EMPTY log, so those
  tables have no covariate labels and nothing said so.** Found while running
  `build.py` on 2026-10-21. The list is
  `metadata/covariate_labels/harvest_empty.tsv` (script, recorded exit, why).
  32 of the 36 failed because the raw source file was not on disk when the
  harvest ran -- the scripts read from `automated_finding/runs/.../raw/`, which
  is gitignored and disposable, so re-running needs the raw files re-downloaded
  first. Three things make this invisible rather than loud:
    * `build.py` cannot tell "no labelled source" from "the harvest crashed" --
      a script with an empty log simply contributes no pairs, and no coverage
      row either, so it is absent from `coverage.csv` as well.
    * **The exit code does not reveal it for 10 of the 36**, which
      `harvest_status.tsv` records as `exit 0`: those scripts handle a missing
      input by printing an error and returning 0 (e.g. `ders_valencia_2021`
      "Error reading file", `sadism_west_2026` "File raw_data/SadismLR.sav does
      not exist!", `xue_2024_covid_study` "No COVID data found"). A TODO entry
      saying "all N exit 0" is therefore not evidence the harvest worked.
    * 8 of the 36 are not in `harvest_status.tsv` at all.
  So several per-batch TODO items below that read "harvest.py has been run for
  this batch" are true and still produced nothing. The cheap fix for the next
  run is for `harvest.py` to fail loudly on an empty log, and for `build.py`
  to report scripts whose log is empty rather than skipping them silently.

Also now due rather than pending, each detailed in its own section below: the
issues-page entries owed by the 10-18 d/e/j/k batches and by
`gerou_2023_dass21` / `kembara_2026_civic_agency`, and the `irw_version` cells
left blank in `metadata/table_changes.csv` for the three `kemp_2019_mss_*`
repairs (derive the version from the manifest -- do not ask Ben for it).

Nothing in THIS session's batch is owed at the release any more: its
dictionary rows, tag rows, provenance and mapping rows are all written and
merged, and the 552-row `tags/tags_auto.csv` merge is PR #3133.

Currently open action items only. For the full batch-by-batch history and
context behind these (and everything already resolved), see `BATCH_LOG.md`.

## Leads pass 2026-10-29 — 22 tables + 3 item text tables, UPLOADED 2026-10-29

Full write-up in `BATCH_LOG.md` (2026-10-29). Ben asked for the 195 `unworked`
leads of the two 2026-10-28 batches; **104 now carry a durable verdict, 91
remain.** Seven deposits shipped.

- [x] **22 response tables (295,681 responses) + 3 item text tables uploaded by
  Ben, 2026-10-29.** `uploaded=2026-10-29` is stamped on the 3 shipped
  `itemtext_provenance.csv` rows and the 3 `itemtext/mapping_verification.csv`
  rows. If any individual table did not in fact go up, that stamp is the thing
  to correct. 22 dictionary rows and 22 tag rows were staged with them, so
  nothing needed pasting. The staging folders are now empty and the manifest is
  archived as `irw_output/MANIFEST_2026-10-29_uploaded_22tables.txt`.

  **A release is owed** -- DONE 2026-10-29, see the top of this file; before these reach `metadata.csv` -- the same release
  the 64-table batch of earlier the same day is waiting on.

  Original: **22 response tables + 3 item text tables need uploading.**
  `automated_finding/irw_output/` (with a MANIFEST) and `itemtext_output/`.
  **Response tables first.** All 22 passed `irw-validate --profile upload` with
  zero failures; all 3 item text tables passed `normalize_nulls.R` ->
  `validate_items.R --resp-csv` -> `audit_batch.R --resp-dir` ->
  `irw-validate`.

- [ ] **91 unworked leads remain**, in `leads/repos_leads_2026-10-28.csv` and
  `...-28c.csv` with their flags. Mostly `recoverable_format` rows under about
  8,000 responses each, which each need their own processing script; plus the 8
  parse failures and one HTTP 504 described below. The 2026-10-29 screening
  output lived in the session scratchpad, so a later pass re-downloads -- the
  DOIs and flags in the leads files are what survive.

- [ ] **A Dataverse GUESTBOOK gate is a nameable class the triage reports as a
  plain download failure.** Five of the 55 retried downloads return HTTP 400
  with `"You may not download this file without the required Guestbook
  response for guestbookID N"`. Unlike the other 19 dataverse refusals this one
  **a person can clear by filling the form**, so it deserves its own flag
  rather than being pooled with dead links. Worth a `doi_hygiene`-style
  detector so the reason reaches the leads file by itself.

- [ ] **An API listing is not proof the bytes exist.** 15 figshare records are
  live in `api.figshare.com/v2/articles/<id>` with files listed, and every
  download path returns S3 `NoSuchKey`. The standing rule is that a figshare
  202 means nothing and the API is the test; the API is the *better* test and
  still not sufficient. If the resolver can cheaply HEAD one file before
  reporting a deposit as resolvable, that is 15 wasted triage slots back.

- [ ] **8 parse failures that download fine**, left unworked rather than
  claimed fixed: 4 ragged CSVs (`Expected 17 fields in line 11, saw 21`, i.e. a
  multi-block file with more than one table stacked in it), 2 truncated `.sav`s,
  1 bad `.RData`, 1 undeclared encoding. Each is recoverable with a per-deposit
  reader. One of the `.sav`s, `10.7910/DVN/IFV44M`, is also the 10-28 sweep's
  verified name/email PII skip and stays closed on that ground.

- [ ] **One HTTP 504** (`10.4121/20763007`, 4TU.ResearchData) is genuinely
  transient and is the one row in that bucket worth retrying in a later sweep.

- [x] **The `10.7910/DVN/HGTS9H` deferral is CLOSED.** It holds
  `afrobarometer r9.tab` (3,392 x 400) plus `experimental data.tab` (360 x 40).
  The Afrobarometer half is third-party survey data that a CC0 replication
  package cannot relicense; the experimental half is a public-goods game, not
  an item battery. Neither ships. The same reading closed three siblings in this
  batch: the ESS (`DVN/YVMPNW`), PISA (`DVN/UVLSIY`) and Caucasus Barometer
  (`DVN/0K34R2`).

- [ ] **One register row was written and one rights answer is owed on it.** The
  CSES (Core Self-Evaluations Scale, Judge, Erez, Bono & Thoresen 2003) had no
  row; this batch wrote one with verdict `hold`, because the originating article
  is paywalled and no statement from the authors or publisher was located. The
  row quotes all 12 stems from the Polish `.sav` and names the one thing to
  check: the SJDM/UBC DMIDI database describes the CSES as nonproprietary, which
  is a secondary summary rather than the rights holder, and its page refused the
  connection on 2026-10-29. One confirmation turns `kopczynski_2021_core_self_
  evaluations` into an item text table with no further extraction work.

- [ ] **Two item text tables are one identification away, not one extraction
  away.** `karahan_kaplan_2024_mindfulness` has all twelve Turkish stems as its
  column headers; the article describes a 12-item scale whose attention /
  awareness / present-focus / acceptance facets and item count match the CAMS-R
  (Feldman et al. 2007), but never names it, and no register row was written on
  a resemblance. Confirming the instrument is the whole job. Likewise
  `arciniegas_romero_2026_math_anxiety` holds all 12 Spanish stems and is held
  only because the register's existing Fennema-Sherman row says `hold` -- it is
  now a SECOND table waiting on that one answer.

- [ ] **13 items x 429 respondents deliberately left unshipped** from
  `10.3389/fpsyg.2024.1432328.s001`. The article splits emotional exhaustion and
  emotional demands 7 and 6; the file's block order is not the article's
  presentation order, and the content does not settle the boundary (two items
  that read as exhaustion are plausibly demands). Any split would halve one
  instrument or merge two. What unlocks it: the article's measurement-model
  table, which is absent from the HTML full text, or a word from the authors.
  Noted also that the same article describes "5-point" measures while all 34 of
  its Likert columns hold 1-6 -- the file is what shipped.

## Repos sweep 2026-10-28 (mode 3) — 134 terms, 8 tables, UPLOADED 2026-10-29

Discovery done: **1,204 candidates** in 100 minutes over 8 connectors (zenodo
450, dataverse 316, figshare 239, scholars_portal 87, datacite 58, openaire 36,
mendeley 14, dryad 4). 134 term variants, all verified absent from
`search_terms_log.csv` before the run and all 134 logged after it. 5,197 further
hits were dropped by `_UNREACHABLE_DOI_PREFIXES` (ICPSR, SRDA) and 6 as
supplementary-file DOIs of papers already accounted for. Triage with `--retriage` is
done and all three `good` rows are worked; the write-up is `BATCH_LOG.md`
2026-10-28c. **The 8 tables are staged in the SAME folders as the 2026-10-28b
leads batch, so one upload covers both** -- 64 response tables and 590,183
responses in total.

- [x] **Triage done: 388 triaged of the 1,204 (816 already in the ledger).**
  3 good, 116 human_assistance -> 48 `recoverable_format`, 39
  `not_item_response`, 18 `worth_retrying`, 6 `human_review`, 5
  `aggregate_continuous`, 0 `conj`. **Both bookkeeping lines appeared and were
  checked**: 116 refined flags recorded in `repo_triage_seen_keys.csv`, 6
  `human_review` rows archived to
  `human_review/human_review_figshare_2026-10-28.csv`. All 387 distinct rows
  carry a verdict in `leads/repos_leads_2026-10-28c.csv`.

- [x] **All three `good` rows worked, 8 tables and 80,310 responses** (see
  `BATCH_LOG.md` 2026-10-28c). They are staged in the SAME folders as the
  2026-10-28b leads batch, so the single upload covers both: the MANIFEST now
  reads 64 response tables and 590,183 responses.

- [x] **The three `pii_suspected` rows were each verified by opening the file
  and all three are skips.** `zenodo.22800681` (three identifier columns, all
  350 rows: email, name, email-or-WhatsApp), `10.17632/dn9djfbj4r` (302
  children's names plus their schools) and `zenodo.20790` (40 children's names,
  also below the N floor). Name/email tier, which the 2026-10-20 narrowing did
  not touch. No standing file by design.

- [ ] **57 of the 388 triaged candidates were article tables, and the fix for it
  landed the same day but too late for this run.** A `.tNNN`/`.gNNN` DOI is an
  article's own table or figure; `is_article_object()` now drops that shape at
  discovery, but this sweep had already loaded the old module. **The next sweep
  should show ~15% more of its triage budget going on real candidates** -- worth
  checking that it does, since it is the cheapest confirmation the fix works.

- [ ] **128 `unworked` leads** in `leads/repos_leads_2026-10-28c.csv`: 61
  retryable download failures, 48 `recoverable_format`, 12 `worth_retrying`, 5
  `aggregate_continuous`, 2 `error`. The `recoverable_format` rows are the shape
  the leads pass learned to work -- a questionnaire carrying several
  instruments, needing one processing script per deposit rather than a reader
  fix.

- [ ] **Four register rows owed from the Ibaceta deposit** (`zenodo.23498072`,
  whose five response tables shipped): the FFMQ, the **25-item** Spanish DERS,
  the mind-wandering content measure (whose published instrument is not even
  identified -- the deposit names the construct only) and the Daydreaming
  Frequency Scale. Ryff is already `hold` and its gate fires. **Careful on the
  DERS**: the register's existing DERS row is the *28-item* Spanish adaptation
  of Hervás & Jódar, a different instrument whose `block` cannot simply be read
  onto this 25-item one, and whose `match_item_code` is empty so the gate stays
  silent here.

- [ ] **openaire answered only 7 of 134 queries, and the failures are three
  different problems.** Counted from the run log:
  - **69 read timeouts** at the connector's 30s limit. Over half the queries.
    Worth deciding whether to raise the timeout, retry once, or drop openaire
    from multi-language sweeps; it is opt-in only (not in `SOURCES`), so this
    costs nothing unless a run asks for it.
  - **29 HTTP 409 Conflict**, every one on a non-Latin-script query (the
    Chinese, Japanese, Arabic and Korean variants). Looks like OpenAIRE
    rejecting the request rather than anything about the term.
  - **28 `'NoneType' object has no attribute 'get'` — FIXED this batch.** That
    was ours: `{}.get(k, {})` only substitutes its default when the key is
    MISSING, and OpenAIRE reports an empty result set as an explicit
    `null` (`{"response": {"results": null}}`). The crash became a
    `SourceUnavailable`, so a query OpenAIRE answered with "nothing found" was
    recorded as "source not searched" — a wrong account of the run's own
    coverage rather than lost candidates. `_dig()` now treats an explicit null
    as absent, a single unwrapped hit is handled too, and
    `tests/test_openaire_null_results.py` covers both plus "a real outage still
    raises". Suite 285 passing.

  The 7 queries openaire did answer returned 36 candidates — about 5 per query,
  against roughly 9 per query across all eight connectors — so it is not a low
  yielder, it is an unreliable one.

- [ ] **`surf`/DataverseNL was omitted from this sweep** via `--sources`, on the
  measurement recorded in the 2026-10-27 section. Nothing owed; noted so the
  candidate counts are comparable with earlier sweeps.

## Leads pass 2026-10-28b — 56 tables + 7 item text tables, UPLOADED 2026-10-29

Full write-up in `BATCH_LOG.md` (2026-10-28b). The 83 unworked leads of 10-27
and the 28 of 10-21 were re-triaged together; **39 of the 106 were worked to a
decision and 18 of those shipped** -- 56 tables, 509,873 responses. 16 were
rejected on content (eleven of them as one class) and 2 are below the N floor.

- [x] **64 response tables (590,183 responses) + 8 item text tables uploaded by
  Ben, 2026-10-29.** This covers BOTH the 2026-10-28b leads pass and the
  2026-10-28c sweep, which shared the staging folders.
  `uploaded=2026-10-29` is stamped on the 8 shipped `itemtext_provenance.csv`
  rows and the 8 `itemtext/mapping_verification.csv` rows. If any individual
  table did not in fact go up, that stamp is the thing to correct. 64
  dictionary rows and 64 tag rows were staged with them, so nothing needed
  pasting. **A release is owed** -- DONE 2026-10-29, see the top of this file; before these reach `metadata.csv` -- and with
  it the covariate-label harvest for `galanis_2025_*` and `aksin_2023_*`
  recorded below.

  Original: **64 response tables + 8 item text tables need uploading.**
  `automated_finding/irw_output/` (with a MANIFEST) and `itemtext_output/`.
  **Response tables first.** All 64 passed `irw-validate --profile upload`; all
  8 item text tables passed `normalize_nulls.R` -> `validate_items.R
  --resp-csv` -> `audit_batch.R --resp-dir` and were clean on `irw-validate`.

  Two of the eight item text tables --
  `andreu_sanchez_2023_information_sources__items.csv` and
  `_lifestyle__items.csv` -- are for response tables that are **already live**
  (uploaded 2026-10-21). They go up with the rest of `itemtext_output/` and no
  response upload is owed for them.

- [ ] **Three `itemtext_issues.qmd` entries owed, in the datapages/irw repo.**
  The `public_note` text is already written in `itemtext_provenance.csv`; it
  just needs pasting into the YAML list in that file.
  1. `lotfi_bejestani_2023_moral_distress` -- the paper documents the scale as
     0-6 and the data hold 266 responses of 7, with the depositor's own total
     running past the 0-6 maximum. This is the page's canonical case.
  2. `andreu_sanchez_2023_information_sources` and 3. `_lifestyle` -- 25 of the
     333 respondents answered the English version of a questionnaire whose
     Spanish is in `item_text`, which the 2026-09-11 multi-language ruling says
     must be stated publicly.
  (These are *in addition to* the `senge_2025_disposal_frequency` and
  `marsalek_2026_ai_attitudes` entries the 10-27 section still owes. One trip to
  that repo clears all five.)

- [ ] **Three register rows and one fallback decision would ship four more
  item text tables from a file already in hand** (`galanis_2025_*`,
  `10.6084/m9.figshare.28868615.v1`). The text is not the problem: every item's
  SPSS variable label IS its full Greek stem and 51 variables carry value
  labels, so this is a cheap-gate `data_labels` extraction whose only blocker is
  rights. Of the five instruments the register carries two — PHQ/GAD family
  `ship`, UWES `block` — so:
  - `galanis_2025_work_engagement` is **decided**: UWES wording never ships.
    Nothing owed.
  - `galanis_2025_phq4` needs only the translated-adaptation call (2026-09-08
    ruling): does the Greek ship, or does the English ship as a
    `translated_substitute` with the PHQ's own terms quoted?
  - `galanis_2025_gaslighting_work`, `_resilience` and `_quiet_quitting` each
    need a **register row written, verdict included**. Starting points:
    the depositor (Petros Galanis) is the Quiet Quitting Scale's own author; the
    resilience stems read as Smith et al.'s Brief Resilience Scale but were not
    confirmed verbatim; and the gaslighting scale's two numbering groups imply a
    longer published form the deposit never names, so that one needs identifying
    before it can be ruled on.

- [ ] **A covariate-label harvest IS owed for `galanis_2025_*`** after the next
  release: all five tables ship `cov_gender`, `cov_education`,
  `cov_turnover_intention` and `cov_burnout_single_item_0_10` as the `.sav`'s
  numeric codes, and the `.sav` labels every one of them (in Greek).
  `harvest.py --commit HEAD galanis_2025_gaslighting_work` then `build.py`.

- [ ] **No covariate-label harvest is owed by the other five scripts.** Two of them
  read a `.sav`/`.dta` (`kubilay_2023_*` reads Stata,
  `aksin_2023_*` reads SPSS), so check this before the next release rather than
  taking it on trust: `kubilay`'s covariates are coded and the deposit labels
  them in an .xlsx codebook rather than in the .dta, and `aksin`'s .sav carries
  exactly one value-label set, for `cov_department`. So there is **one**
  harvestable table-x-covariate pairing in the batch, `aksin_2023_*` x
  `cov_department`, which is worth one `harvest.py --commit HEAD` run when the
  tables are live.

- [ ] **Four more item text tables are blocked on register rows**
  (`aghaei_2025_*`, `10.5281/zenodo.15346545`). Same shape as the
  `galanis_2025_*` item above and worth doing in the same sitting: every item's
  Persian stem is in the .sav's variable labels, but none of the four
  instruments (Young's IAT, a WLEIS-shaped EI scale, a CAMS-R-shaped
  mindfulness scale, five impulse-buying items) has a register row. **Second
  blocker specific to this deposit:** the value-label level is empty for every
  variable, so even a cleared extraction ships stems with no `option_text` --
  worth deciding whether that is acceptable here before spending the rights
  effort.

- [ ] **67 `unworked` leads remain** in `leads/repos_leads_2026-10-28.csv`: 36
  `recoverable_format`, 8 `worth_retrying`, 8 `aggregate_continuous`, 12
  `download_failed` and 3 `error`. The `worth_retrying` bucket is now the thin
  one: its eleven article-table rows were rejected as a class and its four
  repeated-measures rows were worked, so what is left there is mostly
  text-coded-Likert files that still need a reader pass. Each `recoverable_format` row carries its own
  diagnosis from the retriage, and the diagnoses are specific — the common shape
  is a questionnaire carrying several instruments, so the work is one processing
  script per deposit, not a reader fix. **Do not re-run the reader on them**;
  2026-10-28b already proved that changes nothing.

- [ ] **`elhai_2025_smartphone_addiction`'s item text is now extractable and
  was not extracted.** The SAS-SV is registered `ship` as of this batch (its
  originators published the items under CC BY in PLoS ONE 8(12):e83558). The one
  remaining step is reading WHICH ten of the 33-item pool became the short
  version off that paper -- its Table 1 is the full pool's content-validity
  table, so the order is not the answer. Worth doing: the SAS-SV is common, so
  this unblocks future tables too.

- [ ] **The SPIN has no register row.** `elhai_2025_social_phobia` ships its
  responses; its wording is owed a ruling. Connor et al. (2000), British Journal
  of Psychiatry; the starting point is whether Duke University publishes terms.

- [x] **RULED 2026-10-29 (ben-domingue): drop `cov_state` and re-upload
  `gries_2011_moral_foundations`.** The table is live in shard 8 having shipped
  2026-10-21 with `cov_state`, one day after the 2026-10-20 geographic ruling.
  The script had KEPT the state deliberately, arguing a state is standard survey
  demography at 50-6,000x the population of a county while the ruling's concern
  was block-to-county locating; that reading was put to Ben and he ruled the
  other way.

  `data/gries_2011_moral_foundations.py` now drops it, and the corrected table
  is staged in `irw_output/` -- 12,000 rows, 1,000 ids, 12 items, identical in
  every respect but the one column, and clean on `irw-validate --profile
  upload`.

- [x] **The gries replace was done by Ben, 2026-10-29.** `cov_state` is off
  the live table. Not re-verified against Redivis -- Ben's confirmation is the
  record. The staged file is cleared and its manifest archived as
  `irw_output/MANIFEST_2026-10-29_uploaded_gries_replace.txt`, which still
  carries the append hazard and the `SELECT COUNT(*)` check in case the count
  ever needs re-reading.

- [ ] **One further call the gries ruling did not reach:** `cov_region_4`,
  `cov_region_9` and `cov_south` are still on that table. A census region is
  coarser again than a state, and the question put to Ben was about the state,
  so they were left. If regions should go too it is the same one-line change.

- [ ] **`n_participants` in a triage row is a resolver's GUESS. Check
  `nunique()` on the id column before ranking a repeated-measures lead by
  size.** Found twice on 2026-10-28b, both in the `worth_retrying` bucket:
  `10.17026/ss/nidsij` reported 494 participants and has **10** (749 ESM beeps),
  and `10.5061/dryad.ksn02v73p` reported 151 and has **64** (249 trials). In
  both cases the real count decided the verdict, and the shape filter this
  pipeline ranks leads with (100 <= N <= 50,000) was being applied to a number
  wrong by up to 50x. It is specifically the trial-level/ESM bucket where the
  rows are occasions rather than people; worth a resolver fix, or at minimum a
  rule in the lead-working routine.

- [ ] **Four deferrals with named blockers, each worth one answer rather than
  more work:**
  - `10.17632/s73vjz6wss` -- 259 respondents, 76 clean columns = nineteen
    four-item blocks with no labels at all. Eight are reversed duplicates and
    would be dropped, leaving 17 constructs x 4 items. **Four are identifiable**
    — OPT, INNO, DISC and INSE are the Technology Readiness Index's optimism,
    innovativeness, discomfort and insecurity — but the other thirteen (TC, AW,
    EFF, AIL, ETH, PS, RISK, AP, COMP, EXP, REG, TMC, AUDR) are bare
    abbreviations and the title says only "through TAM3". Shipping would mean
    naming thirteen constructs on a guess. One look at the paper settles it.
  - `10.5281/zenodo.22276576` -- Aldosari, 377 graduate students, four clean
    integer blocks (`AI1-17`, `HP1-12`, `OP1-10`, `SS1-23`), ~23,000 responses,
    everything else about it clean. The deposit's description names exactly
    three constructs (AI attitudes, the Dualistic Model of Passion, academic
    stress), so the obvious reading is AI = AI attitudes, HP/OP = harmonious and
    obsessive passion, SS = academic stress — but that is inferred from the
    FILE NAME and it does not fit, because Vallerand's Passion Scale is 6 + 6
    items and this is 12 + 10. Shipping would mean naming four constructs on a
    guess the item counts contradict. One look at the paper settles it.
  - `10.7910/DVN/HGTS9H` -- a CC0 replication package whose data file is
    `afrobarometer r9.tab`, i.e. **Afrobarometer Round 9** redistributed inside
    it. 3,392 respondents x 135 Q-prefixed items, so it is a large, real
    candidate. The depositor's CC0 covers the depositor's material, not
    Afrobarometer's survey data, and Afrobarometer publishes its own terms.
    Does IRW take third-party survey data from a CC0 replication package?
  - `10.6084/m9.figshare.31217140.v2` -- 500 Iranian women, 129 clean integer
    columns, 115 value-label sets, zero variable labels. The column prefixes
    **contradict** the numbering (`MD1..MD27` then `Perfectionism28..30` run
    1-30; `POS1..36` then `Psychological_F37..60` run 1-60), so the prefix is
    not the instrument boundary and splitting on it would invent scales that
    are not there. Needs the paper to say which items belong to which
    instrument.

## Repos sweep 2026-10-27 (mode 3) — UPLOADED; follow-ups open

Discovery, triage and the `good`-row processing pass all ran overnight
2026-10-27. Full numbers in `BATCH_LOG.md`'s 2026-10-27 and 2026-10-27b
entries. The five `good` rows are **done**: four shipped, one rejected on
content (MOFWaste, `10.5281/zenodo.14999619` — nominal canteen multiple-choice,
no item battery).

- [x] **PR #3264 merged** (both commits: the sweep's standing records and the
  18 tables). Ben started the Redivis upload on 2026-10-28.
- [x] **18 response tables (68,802 responses) + 8 item text tables uploaded**
  by Ben on 2026-10-28, response tables first.
  `irw_output/` and `itemtext_output/`.
  `irw_output/MANIFEST.txt` lists them. Costa 2020 x2 (CC0), Marsalek 2026 x1,
  Senge 2025 x11, Rumangkit 2026 x4 (all CC BY 4.0). 19 `dictionary_auto.csv`
  rows are staged for them and reach biblio on the first pipeline run after
  release.
- [x] **`uploaded` stamped `2026-10-28`** in `itemtext_provenance.csv` for the
  8 shipped item text tables (bytes edited in place, CRLF rows preserved).
- [ ] **One issues-page entry owed, in the datapages/irw repo:**
  `senge_2025_disposal_frequency` — the deposit's questionnaire documents the
  five options on a -2..2 scale and the data codes them 1..5, so the labels are
  attached to the table's own 1-5 in order. `marsalek_2026_ai_attitudes` also
  carries a `public_note` (its English item text is IRW-generated and the Czech
  response anchors are unpublished), which forces a callout.
- [ ] **No covariate-label harvest is owed by this batch** — none of the four
  scripts reads a `.sav` or `.dta`; the labelled covariates were mapped from
  published codebooks inside the scripts.
- [x] **The 83 `unworked` leads are re-triaged and 7 of them worked**
  (2026-10-28b). They moved, with the 28 from 10-21, into
  `leads/repos_leads_2026-10-28.csv`, which is now the one live place for them;
  the rows here carry a note pointing at it. 5 deposits shipped 16 tables, 2
  were rejected on content, 2 deferred with a named blocker. The re-triage
  itself resolved nothing -- same buckets as before -- so the open work is
  reading the remaining 99 rows' diagnoses, not re-running the reader.
- [x] **Measured and answered 2026-10-28: stop querying `surf`.** 314
  `10.34894` keys have ever been triaged and produced **one** `good`, **zero**
  `worth_retrying`, one shipped table and 263 `no_usable_file` -- a ~0.3% good
  rate against a corpus rate nearer 1%, and the failure mode is access (403 on
  file download), not relevance. The 2026-10-28 sweep ran with `--sources`
  naming the other eight connectors. Left as a per-run choice rather than a
  code change, so one flag brings it back; if Ben wants it permanent, drop
  `from_surf` from `_CONNECTORS` in `irw_discover_updated.py`.
- [ ] **Dryad file downloads 401 (6 rows incl. datacite).** Dryad needs no
  auth for file downloads, so this is a resolver defect, not a permission.
  Noted on 2026-10-21 as well and still unfixed.

## Repos sweep 2026-10-21 — 13 tables staged, AWAITING UPLOAD

Full write-up in `BATCH_LOG.md` (2026-10-21 and 2026-10-21b). All ten `good`
rows worked to a decision; seven shipped, three did not.

- [x] **13 response tables + 5 item text tables uploaded by Ben, 2026-10-21.**
  `uploaded=2026-10-21` is stamped on the 5 shipped rows of
  `itemtext_provenance.csv` and the 5 `itemtext/mapping_verification.csv` rows.
  If any individual table did not in fact go up, that stamp is the thing to
  correct -- the staged copies are in `automated_finding/irw_output/` and
  `itemtext_output/` with a MANIFEST until Ben clears them.
- [x] **Supplementary-file DOIs no longer re-surface an ingested paper**
  (done 2026-10-21). `is_excluded()` in `irw_discover_updated.py` now tries a
  candidate in both forms and `_load_auto_exclusions()` carries the article DOI
  behind every supplement DOI in the set, so the match works whichever form
  each side recorded; all three discovery modes use it. The suffix rule itself
  is `doi_hygiene.strip_supplement_suffix()` -- one definition, not two.
  Verified against the live exclusion set: `10.3389/fpsyt.2022.827519.s001`
  now returns "supplement". 9 tests in
  `tests/test_supplement_doi_exclusion.py`; full suite 216 passing.
  A "supplement" match is deliberately coarser than an exact one -- it also
  hides a *different* attached file of an ingested paper, e.g. an `.s002`
  holding a second instrument -- so repos mode prints the count rather than
  dropping them silently.
- [ ] **`automated_finding/itemtext_provenance.csv` has no
  `translation_source` column**, which the schema requires of a
  `translated_substitute` row (`check_provenance.R` fails a blank one). The two
  `li_2023_*` rows carry it as a labelled sentence inside `note` because the
  column does not exist. `check_provenance.R` only walks
  `itemtext/itemtables/**/provenance.csv`, so nothing failed -- but the batch
  file cannot express the field, and it should get the column.
- [ ] **ONE item text table still owes a translation pass:
  `saputra_2025_fomo_consumer`** (Indonesian). The other two are **done**
  (2026-10-28b): `andreu_sanchez_2023_information_sources` and `_lifestyle` are
  staged in `itemtext_output/`, gated and clean. The premise of the deferral was
  wrong and clearing it cost nothing -- the deposit carries the whole
  questionnaire in BOTH languages ("QUESTIONNAIRE IN SPANISH" and
  "QUESTIONNAIRE IN ENGLISH" sheets), so the English is the source's own
  published translation and **no IRW-generated content ships**. Both response
  tables are already live (10-21), so only the item text needs uploading. They
  do still owe an `itemtext_issues.qmd` line, but for a different reason: 25 of
  the 333 respondents answered the English version, which the 2026-09-11
  multi-language ruling says `public_note` must state. Worth checking whether
  `saputra_2025_fomo_consumer`'s deposit has the same both-languages shape
  before treating it as expensive.
- [x] **The 8 `worth_retrying`, 40 retryable `download_failed`, 2
  `pii_suspected` and 3 `aggregate_continuous` rows are worked** (2026-10-21d,
  see below). **The 28 `recoverable_format` rows are re-triaged** (2026-10-28b)
  and now live in `leads/repos_leads_2026-10-28.csv`; two of them shipped.
- [x] **The `surf` (DataverseNL) question is answered** -- see the 2026-10-27
  section above: measured 2026-10-28, ~0.3% lifetime good rate over 314 keys,
  and the 2026-10-28 sweep omitted it.

## Repos sweep 2026-10-21, leads pass (2026-10-21d) — 35 tables staged, AWAITING UPLOAD

Full write-up in `BATCH_LOG.md` (2026-10-21d). Jobs 1, 3 and 4 of
`leads/repos_leads_2026-10-21.csv` worked to a decision: 53 rows, 8 deposits
shipping 35 response tables and 218,354 responses, 4 item text tables.

- [x] **35 response tables + 4 item text tables uploaded by Ben, 2026-10-21.**
  `uploaded=2026-10-21` is stamped on the 4 shipped `itemtext_provenance.csv`
  rows and the 4 `itemtext/mapping_verification.csv` rows. If any individual
  table did not in fact go up, that stamp is the thing to correct -- the staged
  copies are in `automated_finding/irw_output/` and `itemtext_output/` with a
  MANIFEST until Ben clears them. **A release is owed** -- DONE 2026-10-29, see the top of this file; before these reach
  `metadata.csv`, and with it the first `covariate_labels/build.py` run that
  can pick up `cassidy_2024_*` (see the note below).

  Original: **35 response tables + 4 item text tables need uploading.**
  `automated_finding/irw_output/` (with a MANIFEST) and
  `itemtext_output/`. Response tables first. All 35 pass `irw-validate`'s
  upload profile; the 4 item text tables PASS `normalize_nulls.R` ->
  `validate_items.R --resp-csv` -> `audit_batch.R --resp-dir` and are clean on
  `irw-validate`. 35 dictionary rows and 35 tag rows are already staged, so
  nothing needs pasting. Stamp `uploaded=` on the 4 shipped
  `itemtext_provenance.csv` rows and the 4 `mapping_verification.csv` rows
  only after Ben confirms (3 provenance rows and 3 mapping_verification rows:
  the two kubilay tables, the two andreu_sanchez tables and
  teriba_2026_self_compassion).
- [x] **The 28 `recoverable_format` rows were re-triaged 2026-10-28b** and
  the hope recorded here is **disproven**: none of them "simply read now". The
  encoding x delimiter and BIFF2 `.xls` fixes change nothing for this bucket --
  all 28 came back `recoverable_format` again. What they actually need is a
  processing script per deposit, because the diagnosis
  ("keeping only the N columns that share one small integer domain, the file
  triages as good") is the signature of a questionnaire carrying several
  instruments, not of a reader bug. Two of the 28 shipped this way; the rest are
  in `leads/repos_leads_2026-10-28.csv`. Nobody needs to try the reader route
  again.

- [ ] **Re-run `metadata/covariate_labels/build.py` after the next pipeline
  stage 01, and commit the diff. Expect ~558 new rows.** Ben released
  everything on 2026-10-21 and `build.py` was run immediately after: it was a
  **no-op**, correctly. `build.py` gates on `metadata/metadata.csv` ("live
  tables only"), and that file is a repo SNAPSHOT that only stage 01
  regenerates -- it was last written 16:32, before the upload, so all 35 new
  tables were skipped as not-live. Releasing makes a table live on Redivis; it
  does not refresh the snapshot. So the order is stage 01 -> `build.py`, and
  nothing is wrong until that has happened.

  The expected result, computed from the cached harvest log rather than
  guessed: **10 of `cassidy_2024_*`'s 11 covariates are eligible** and should
  produce **~558 rows** (~62 per table x 9 tables; the per-table count varies
  a little because a different subset of respondents answered each
  instrument). `cov_age` is the one exclusion and it is correct -- `Age` is a
  free numeric with no value labels, so it fails the "at least half the codes
  carry a source label" rule. `cov_ethnicity` is a near-miss worth a glance
  when the diff lands: 2 shipped codes against 3 source labels with only 1
  matching, which clears the half rule by exactly nothing.

  The confirmation that it worked is also automatic now: the #3159 ratchet
  will report those 9 tables as **closed** rather than as gaps.

- [ ] **`build.py` writes a nondeterministic exclusion message into
  `coverage.csv`.** Running it twice on identical inputs flips the `reason`
  on four `sahin_2026_*` rows between "gelir_inkcome is unlabelled or labelled
  differently in another file the script read" and "the script also feeds
  income into cov_income, and it is not labelled like gelir_income". Both
  describe the same exclusion, and the pair of candidate messages presumably
  comes out of set or dict iteration order over the several source columns the
  script read. It is cosmetic in effect but not harmless: `coverage.csv` is a
  committed record, so every `build.py` run produces a 4-line diff that is
  pure noise, and noise in a committed record is what trains people to stop
  reading its diffs. Seen twice on 2026-10-21 (and reverted both times rather
  than committed). One-line fix for whoever owns `build.py`: sort the
  candidate source columns before choosing the message.

- [ ] **(superseded by the two items above, kept for the record)
  `cassidy_2024_*`'s covariate labels land on the next `build.py` run,
  not before.** The 2026-10-21d entry wrongly said no harvest was owed; it is,
  because ten of the eleven `cov_*` columns ship the .sav's numeric codes and
  the .sav labels all of them. The harvest has been run (exit 0, cached log)
  and the script fixed so it can be harvested at all, but
  `metadata/covariate_labels/build.py` includes only tables present in
  `metadata/metadata.csv` -- so these nine tables need to be live first. No
  action until then; this is a note so the next release's owed `build.py` run
  is known to cover them.

### Two credential requests. Neither is a code change, and between them they
### unblock 9 rows here plus a share of every future sweep.

- [ ] **A Dryad API bearer token.** Measured 2026-10-21:
  `datadryad.org/api/v2/files/<id>/download` answers 401 "Unauthorized, must
  have current bearer token" for a public CC0 file, and the unauthenticated
  `/downloads/file_stream/<id>` path now sits behind an Anubis proof-of-work
  challenge (a "Validating..." page to a browser UA, 403 to curl). Every
  variant behaves the same, and no Zenodo mirror exists for the 16 Dryad rows
  checked. The previous entry's "Dryad needs no auth, so a 401 is a resolver
  defect" was an inference, not a measurement, and it was wrong. Metadata and
  file listings stay open, so content triage still works without the token --
  13 of the 16 were rejected that way. The 3 that want the file are
  `10.5061/dryad.dv41ns2db` (Turkish yoga consumers' motivation, **a scale
  development study** -- the most valuable row behind the gate),
  `10.5061/dryad.vx0k6dk33` (driver-vehicle interface questionnaire) and
  `10.5061/dryad.h44j0zpv3` (vision-related quality of life).
- [ ] **A Harvard Dataverse API token.** The 8 `download_failed` HTTP 400s were
  not malformed requests: Harvard answers each with "You may not download this
  file without the required Guestbook response for guestbookID *n*". The
  depositor attached a guestbook and the API honours it only for a
  token-carrying request (`?gbrecs=true` does not bypass it). A guestbook is an
  access control, not a rights restriction -- these are CC0 and CC BY-NC-SA
  deposits -- so they are recorded `blocked_access` and a token reopens 6 at
  once: `10.7910/DVN/{Y8ICVZ,SV2OY4,WE0LSW,P6C98Y,V47G7M,26244}`.

### Rulings wanted (none blocks anything already staged)

- [ ] **The Italian IUS-R: `hold` -> `ship`?** Written as a `hold` row in
  `itemtext/instrument_rights_register.csv` because the IUS FAMILY already
  carries a `block` (2026-10-15 counsel ruling), and overriding a standing
  block is Ben's call. The fact that would settle it: the complete 12-item
  Italian IUS-R with all five anchors is published as the S1 File of a CC BY
  4.0 PLOS ONE article (`10.1371/journal.pone.0211929`) whose co-authors
  include **Mark H. Freeston, the originator of the IUS itself**, whose own
  1994 terms the block row records as never located; the Italian version is by
  the same group. That is the shape ruled `ship` for the MFQ-2 (rights bank
  R10: originators' own CC BY release). A `ship` releases the item text for
  `bottesi_2019_ius_r` (stems and anchors already in hand) and, by the same
  family block, for `cassidy_2024_ius_12`.
- [ ] **Seven instruments with no register row at all**, each holding item text
  that is already in hand: the ECR-R, OCI-R, PSWQ, Family Accommodation Scale,
  and the RSS and ReSQ reassurance-seeking batteries (all six in the .sav's own
  variable labels for `cassidy_2024_*`, 177 item columns, verbatim), plus
  Borsci et al.'s BUS-11 and Davis's TAM as adapted for
  `leppla_2026_smokechem_*` (German + the depositors' English in the workbook's
  Items sheet). The Leppink Cognitive Load Scale in the same deposit is already
  `hold` (2026-10-18). The BUS-11/TAM pair is specifically the shape of class
  ruling R16 (study-authored adaptation of items from a closed article stating
  no terms, `ship`) -- but R16 is deliberately non-sweeping and wants a
  per-table upstream triage, which has not been done.

### Smaller things

- [ ] **`10.7910/DVN/IFV44M` leaks respondent identities and is public and
  CC0.** An "Intercultural Proficiency Questionnaire" deposit on Harvard
  Dataverse whose Qualtrics export carries 33 real German names and email
  addresses, 80 IP addresses and 79 pairs of GPS coordinates. Skipped here
  under the name/email tier. Telling the depositor is Ben's call, not a
  script's.
- [ ] **The three `huebner_2021_weightlifting_*` rows in
  `itemtext/mapping_verification.csv` still WARN on `lint_verification.R`**
  ("VERIFIED but its evidence hedges (does not establish)"). It is not a real
  hedge -- what the sentence scopes is whether the depositor's own codebook is
  right about her survey, which no route could settle -- but the rows do not
  assert separation in any of the phrases `SEPARATION` lists, so the warning
  cannot clear. A one-line rewording of each evidence string fixes it; this
  batch's four rows were written that way and pass.
- [ ] **`rimisp_2021_household_services` and `_care_work` join the queue for
  the deferred translation pass**, bringing it to five tables:
  `saputra_2025_fomo_consumer` (Indonesian),
  `andreu_sanchez_2023_information_sources` and `_lifestyle` (Spanish), and
  these two (Spanish). All are rights-clear with the wording in hand; shipping
  means an English gloss in the `_translated` fields, which is IRW-generated
  content and owes an `itemtext_issues.qmd` line.
- [ ] **A cheap triage filter nobody has written: a PLOS `.tNNN` DOI suffix is
  an article TABLE, not a dataset.** Four of the eight `worth_retrying` rows
  were a paper's own Table *n* deposited as a plos.figshare record, and the
  triage reason quotes column names containing `<b>`/`<i>` HTML. The `.sNNN`
  supplementary-file rule fixed in 2026-10-21c covers `.s` only; `.t` is the
  same shape and never worth a download.

## Blotner people-pleasing deposit: 5 tables UPLOADED, pipeline run owed (2026-10-21)

Found by Ben from a Behavior Research Methods preprint (`~/Downloads/Preprint IRT
PPS.pdf`); the preprint's own OSF node (osf.io/b4adh) is private, but 1,894 of its
2,538 respondents come from the CC BY 4.0 validation paper
(10.1007/s12144-026-09519-2) whose node, osf.io/4n8sk, is public. Five response
tables built by `data/blotner_2026_people_pleasing.py`, **230,741 responses**, all
passing `irw-validate --profile upload`, uploaded by Ben in-session 2026-10-21:

| table | rows | persons | items | resp |
|---|---|---|---|---|
| `blotner_2026_people_pleasing` | 28,395 | 1,894 | 15 | 1-5 |
| `blotner_2026_hexaco60` | 133,550 | 3,131 | 60 | 1-5 |
| `blotner_2026_lsrp` | 34,398 | 1,323 | 26 | 1-4 |
| `blotner_2026_bes` | 26,460 | 1,323 | 20 | 1-5 |
| `blotner_2026_svo` | 7,938 | 1,323 | 6 | 1-9 |

**Where they live, corrected 2026-10-21.** All five are in
**`item_response_warehouse_8`'s draft**, 230,741 responses, release owed. The
first upload put four of them in shard 7's draft and `people_pleasing` in
shard 8, and every one of those copies was the **pre-age-filter** build
(26,500 / 133,730 / 34,450 / 7,950 / 28,440) -- `age.between(18, 100)` is
False for `NaN`, so three respondents with missing age survived. The shard-7
copies were deleted and `people_pleasing` was replaced, so the warehouse now
matches the figures in the table above, which is also what the script produces
today.

Written and committed: 5 dictionary rows (`dictionary_auto.csv`), 5 tag rows
(`tags/tags_auto.csv`), 5 `codebook_at_ingest.csv` rows (all `none` -- the deposit
ships no codebook file), 4 `metadata/covariate_labels/manual.csv` rows for
`cov_study`, a `not_harvestable.tsv` row, one `itemtext_provenance.csv` row and one
`itemtext/instrument_rights_register.csv` row (PPS -> `ship`).

Owed:

- [ ] **Weekly pipeline run** picks up metadata/biblio/tags/column_docs for the
  five tables. Nothing to do by hand -- do NOT run `run_pipeline.sh` ad hoc.
- [x] **Item text UPLOADED 2026-10-21.**
  `blotner_2026_people_pleasing__items`, 75 rows, is in **`irw_text_3`'s
  draft** -- `red_up.drafts --dataset irw_text_3 --verbose` lists it as
  `added`, and the staged CSV has been cleared from `itemtext_output/`.
  `itemtext_provenance.csv`'s `uploaded` cell is now stamped. The release is
  Ben's; note that `irw_text_3`'s draft also carries the licensing session's
  withdrawals, so publishing it ships both.
- [x] **Row-level overlap check DONE 2026-10-21: one shared respondent, needs
  a ruling.** Both tables carry all 20 BES items under identical labels, so the
  comparison is well posed. Complete 20-item response vectors (527 of 535 in
  2025, 1,323 of 1,323 in 2026) give 6 vectors present in both deposits, 71
  cross pairs. Five of the six are degenerate response styles rather than
  shared people -- all-3 straight-lining (12 persons in 2025, 5 in 2026) and
  perfect reverse-key mirroring at 5/1 and 4/2, where the low values fall
  exactly on the `_R` items -- and those same vectors recur *within* each table
  (16 duplicate vectors inside 2025, 14 inside 2026), which is what rules them
  out.

  **The exception: `autism_blotner_2025_s1_bes` id `100` and
  `blotner_2026_bes` id `s2_1082` are almost certainly the same person.**
  Identical on all 20 items with 5 distinct response values used (not a
  straight-line: `4|2|2|4|5|4|2|1|5|2|4|4|2|4|4|3|4|4|2|2`), unique in both
  tables rather than part of a cluster, and matching on age 33, female, and
  university education. The only covariate that disagrees is the 2025 table's
  unlabelled `cov_student_status` (1, against `cov_student = no` in 2026), and
  its coding direction is not documented, so it is not evidence either way.

  **RULED 2026-10-21, Ben: one shared respondent is acceptable, both tables
  stay as they are.** The shape is narrow -- 1 respondent out of 535 and
  1,323, one instrument, no duplicated table and no duplicated response row --
  and it reads as incidental panel overlap, since Blotner recruits both samples
  from German online panels, rather than a redeposit. Nothing to withdraw, and
  this item is closed.

  Noticed in passing, not a defect in either table: `autism_blotner_2025_s1_bes`
  carries raw covariate codes (`cov_sex` = 2, `cov_education` = 5) where
  `blotner_2026_bes` carries labels (`female`, `university`) -- a covariate
  value-label gap on the 2025 table.
- [ ] **osf.io/b4adh** adds only ~644 respondents on the 10 retained items and is
  private. Not worth waiting on; Blotner is a repeat contributor if we want it.

## Repos batch 2026-10-20: 87 tables UPLOADED, release owed (2026-10-20)

Six parallel agents; full write-up in `BATCH_LOG.md`. **87 response tables /
1,104,108 responses** in `irw_output/` (+ `MANIFEST.txt`), 7 item text tables in
`itemtext_output/`, all passing `irw-validate --profile upload` with zero
failures. 87 dictionary rows and 87 tag rows staged. **Five collisions** were
caught and dropped into `runs/dropped_2026-10-20/` -- including eight
already-committed `henderson_2023_la_covid_*` tables that proved to be the
wave-1 slice of a 5-wave superset (100% identical on 10,997/10,997 cells), now
in `runs/dropped_2026-10-20/superseded_by_lapanel/`. Read the BATCH_LOG entry
before touching that folder or re-adding anything from it.

- [x] **`zheng_2018_hfmd_eq5d` mobility level 4: RESOLVED 2026-10-20**, settled
  from the data rather than the paper (96.8% of the level-4 cells are
  pre-ambulatory infants; a severity level would track severity, not age). The
  567 cells are dropped as not-applicable, all 3,500 ids retained, all four
  dimensions now 1-3. Not confirmed against the source paper, which was never
  reached -- revisit if it documents level 4 as something else.
- [x] **UPLOADED 2026-10-20**, confirmed by ben-domingue: all 87 response
  tables and all 7 item text tables. 86 of the 87 verified on row count in the
  first run; `zheng_2018_hfmd_eq5d` failed `red_up`'s row-count check and was
  re-uploaded on its own, which is a true replace (`push_one` deletes any
  existing table of the name first). No stray uploads reported. The cause was
  mine: I rewrote that CSV in `irw_output/` at 15:40 to drop the mobility
  level-4 cells, after having told Ben the folder was ready, so `red_up`'s
  row count and its file stream straddled the edit. **Lesson: once the upload
  folder is handed over, do not edit it -- stage the fix elsewhere and say so.**
  `itemtext_provenance.csv` stamped `uploaded=2026-10-20` for the 7 shipped item
  text tables. Dictionary and tag coverage verified 87/87 each, with the item
  text flag agreeing with what shipped.
- [x] **Released 2026-10-20, and the build that followed it is done** --
  everything had landed on the unreleased draft of shard 7 and `irw_text`.
  `metadata/covariate_labels/build.py` ran 2026-10-21 (PR #3153) and covered
  this batch's harvest along with every other pending one.
- [ ] **`metadata/data_notes.csv` rows are owed for this batch** and have not
  been written. Several tables carry a caveat a user would want on the table
  page: `wu_2025_flow_state` (`id` rests on a positional pretest/posttest
  pairing, no respondent key in either file), `yang_2026_vocabulary_size`
  (scored against a key derived from the responses, verified to reproduce the
  deposit's own total for 275/275), `yang_2021_butterfly_knowledge` (the scale
  midpoint 3 is an explicit "unknown", 34% of responses -- a real trap for
  anyone treating it as ordinal), `zheng_2018_hfmd_eq5d` (567 mobility
  not-applicable cells dropped), `choi_2021_job_satisfaction` (two rows share an
  MTurk id, so `id` is the row index and does not identify a person in 2 cases),
  and the `vezhodulu_2025_yabis_a` positional actual/ideal read.
- [x] **Tag rows written for all 87**, in `automated_finding/tags_auto_2026-10-20.csv`
  (`Rater=claude-auto`). Deliberately a separate file: merging into
  `tags/tags_auto.csv` is a reviewed step, same as the 10-18 batch.
  **Do NOT merge `runs/worklist_2026-10-20/tagrows_s5.jsonl`** -- its 9 rows are
  free text, not vocabulary-compliant (`Age Range: "Adult"`,
  `Construct type: "Non-cognitive"`), and would halt `03_tags.R` on `TAG_VOCAB`.
  The 87-row file supersedes them. Known gaps in it: `Age Range` blank on 19 rows
  (not inferred from "college students" or a country; several carry `cov_age`, so
  the computed rule gets them later) and `Child Age` blank on 81.
- [ ] **Item text for the five author-written COVID batteries is SHIPPED** (7
  tables), but `henderson_2023_lapanel_racial_resent` and
  `henderson_2023_lapanel_tipi` are HELD for want of register rows -- Kinder &
  Sanders and TIPI (Gosling, Rentfrow & Swann). Their response tables ship. Both
  holds have provenance rows saying so.
- [ ] **`codebook_url` is missing for the 9 discovery-slice tables.** Their
  dictionary rows staged without it, so nothing reached
  `codebook_at_ingest.csv`. The other 76 recorded `"none"`. Needs a pass over
  those 9 deposits rather than a guessed value.
- [x] **8 rights-register rows written**, all append-only (`git diff --numstat`
  = 8/0), 360 data rows now. Three rest on a located clause: the **Flow Scales
  suite** is `block` on Mind Garden's ToS SS3/SS5(d) prohibition on reproducing or
  circulating assessment items (not the fee model, which is only corroborative) --
  and per the 2026-09-29 #2401 ruling that a block covers every language, this
  reaches the **Chinese CDFS-2** too, so `wu_2025_flow_state`'s Chinese stems
  (sitting in its SPSS variable labels) stay unshipped. **ATI is `ship`** on the
  authors' own "The scale is free to use" grant at ati-scale.org, and the grant
  reaches its 13 published translations. **The VST is `hold`** on a located
  near-miss: Nation's page grants permission for the *Updated VLT* alone, which
  is a different instrument -- quoted in the row so nobody re-finds it and
  misreads it. Five holds for want of terms: FSS-1 Portuguese, Ryff originals,
  MUIS, Kinder & Sanders, BESAA.
- [ ] **Two corrections that came out of that research, both worth acting on:**
  - **`data/shan_2024_bfi_s.py` needs checking against register line 307.** The
    BFI-10 row already blocks "any other short form built from BFI-44 or BFI-2
    items, all translations", and your 2026-10-17 ruling (a short form of a
    blocked long form is blocked) reaches the Gerlitz & Schupp BFI-S by that
    row's own wording. If that script shipped BFI-S item text, it is live and
    needs review.
  - **`abu_tabar_2021_muis` is live and the MUIS is now `hold`.** Its deposit has
    the English stems in SPSS variable labels, so confirm no MUIS item text was
    ever staged rather than assuming it. Nothing appears to need withdrawing.
- [ ] **`schadelbauer_2023_ati` item text is now unblocked and cheap** -- ATI is
  `ship`, and the 9 verbatim stems are in the deposit's `DATA_CODING.txt`. This
  is the single cheapest item-text job outstanding. Note the deposit's "[1-5]"
  annotation is wrong: 6 is observed on all nine items and the table ships 1-6.
- [ ] **Register rows still owed** (the earlier list, minus what was written):
  the **Spanish DASS-21** translation row on the Greek pattern (still open --
  the agent spent its box on the three-table Flow row instead), CaMir-R, BVAQ-B,
  Celebrity Attitude Scale, YABIS, B-POHW, **BarOn EQ-i:YV / ICE:NA** (commercial,
  MHS -- likely a quick located `block`), and PHC-PSQ (study-authored, likely
  `ship`).
- [ ] **The Kinder & Sanders hold has a concrete next step.**
  electionstudies.org returns HTTP 403 behind a Cloudflare JS interstitial to an
  agent, so the ANES terms were never actually read -- only search summaries,
  and nothing was quoted. Fetch those pages from a real browser session, or read
  the terms inside an ANES study's own documentation PDF, which travels with the
  data and is not Cloudflare-fronted. Separate question: ANES terms would govern
  the ANES fielding, but authorship is Kinder & Sanders (1996, *Divided by
  Color*), so book-sourced wording is its own ask. This holds back
  `henderson_2023_lapanel_racial_resent`.
- [ ] **Ryff: a trap is recorded in the row.** The Wisconsin page's "Use of
  scoring code is granted under CC BY-SA 4.0" covers the **scoring code only**;
  its actual statement is "We do not have copyright authority over these
  measures and cannot grant permission for use." Because the original is held,
  no stand-in exists under irw#2121, so `ramirezparedes_2026_ryff` ships nothing
  in either language.
- [ ] **BESAA has an unresolved citation question**: a secondary source dates the
  adult/adolescent form to 2011 rather than 2001, which could mean the row points
  at the wrong article.
- [ ] **15 rights-register rows are owed**, each with a located clause rather
  than an asserted one. None blocks a response table; all block item text.
  Stated by the agents, not written, because a defensible row needs terms
  quoted and I ran out of box:
  - **Flow State Scale / FSS-2 / DFSS-2** (Jackson & Marsh 1996; Jackson &
    Eklund 2002) -- distributed under licence by Mind Garden, a located fact.
    Proposed `hold`. Touches `borges_2026_flow_musicians`, `wu_2025_flow_state`.
  - Chinese FSS-2/DFSS-2 ("CDFS-2") as administered by Wu 2025 -- translation,
    own terms unestablished. Proposed `hold`. 33 stems sit in the .sav labels,
    so cheap the moment the original clears.
  - Portuguese FSS-1 adaptation (figshare 30166636 / 32995919) -- publisher
    unlocated. Proposed `hold`.
  - Ryff Scales of Psychological Well-Being + its Spanish adaptation (42 stems
    present in the xlsx headers). Proposed `hold`. The register has no row for
    the *original* Ryff either.
  - Kinder & Sanders racial-resentment battery -- proposed `hold`; a permission
    would live in the ANES terms if one exists.
  - DASS-21 **Spanish** translation -- parallel to the existing Greek row; ship
    the public-domain English as `translated_substitute` under irw#2121.
  - BESAA / BESAA-S (Mendelson, Mendelson & White 2001) -- no row; the
    register's only body-esteem row is a different instrument (Franzoi &
    Shields, `block`).
  - CaMir-R (Balluerka et al. Spanish adaptation) -- no row.
  - MUIS (Mishel 1981/1988) -- stems in hand in the CC0 deposit; proposed
    `hold`. Also relevant to the already-live `abu_tabar_2021_muis`.
  - McKnight et al. technology-trust scales -- proposed `note`.
  - BFI short form (Rammstedt & John / Gerlitz & Schupp) -- proposed `note`; a
    citation-only `ship` is plausible but was not verified.
  - ATI scale (Franke, Attig & Wessel 2019) -- proposed `ship`, published CC BY
    with a free-use statement, but **fetch the statement before shipping**.
  - Celebrity Attitude Scale and YABIS (parts A and B) -- proposed `note`.
  - BVAQ-B; BarOn EQ-i:YV / ICE:NA (commercial); Vocabulary Size Test (Nation &
    Beglar 2007); B-POHW and its English original; adapted L2MSS stems -- no
    rows. PHC-PSQ is study-authored and could be registered `ship`.
- [ ] **`covariate_labels/harvest.py --commit HEAD <stem>`** is owed for the
  scripts in this batch that read `.sav`/`.dta` and ship `cov_*`. Not run for
  any of them.
- [ ] **Henderson waves 2-5 are ~4x the shipped volume and need a design call
  first.** Only wave 1 shipped (8 tables, 1,000 ids). The five wave files are
  **cumulative**, not parallel: wave 1 is 191 columns, wave 5 is 1,120, each
  adding that wave's batteries with a `_wN` suffix. The wave-5 file carries all
  five waves wide and its `caseid_w5` is complete for 1,000 respondents, but
  **only 359 of them have a `caseid_w1`** -- the panel was refreshed, so wave 5
  is NOT a superset of wave 1. A correct 5-wave build merges all five files on
  their per-wave `caseid_wN` and would **replace** the eight wave-1 tables
  rather than add to them. Wave 2's id column is `caseid_w2`, not `caseid`,
  which is what made the naive read fail.
- [x] **Triage of the 2026-10-20b sweep is closed (2026-10-21).** The resume ran
  clean and downloaded nothing new: of the 1,174 candidates, 1,081 were already
  in `repo_triage_seen_keys.csv` with real flags from earlier batches (406 from
  the 10-20 run itself, the rest from 10-06/10-07/08-13 and others), so the 780
  rows `leads/repos_leads_2026-10-20.csv` recorded as `origin_flag=untriaged`
  were duplicate deposits the new terms resurfaced, not unseen work. Final roll-up:
  3 good, 103 human_assistance, 260 no_usable_file, 73 download_failed, 23
  not_item_response, 7 below_min_n, 1 license_restricted, 3 error. Step 2b on the
  103: 45 not_item_response, 20 worth_retrying, 18 recoverable_format, 18
  human_review, 2 aggregate_continuous, 0 conj. `[step 2b] 0 refined flag(s)
  recorded` is benign here -- 100 of the 103 keys already carry a `refined_flag`
  from 10-20 and 3 are not in the ledger at all. The 18 human_review rows are in
  `human_review/human_review_zenodo_2026-10-21.csv` (**uncommitted**).
  Still open from it: regenerate `leads/repos_leads_2026-10-20.csv` so its
  `untriaged` rows carry the ledger verdicts, and work the 3 `good` + 20
  `worth_retrying` rows.

- [ ] **`sadish_2021_covid_beliefs`: the live table has 6 items, this batch
  built 7** over the same 913 ids (9,398 rows vs 8,056). The new build was
  dropped rather than shipped, because uploads append. If the 7th item is
  right, this is a delete-then-recreate replace, not an upload.
- [ ] **Widen the pre-write duplicate check.** `grep -rl "DOI: <doi>"
  ../data/*.py` misses a script whose `# DOI:` line holds the *paper* DOI while
  the data DOI sits on `# Source:`/`# Data:`. That is how `10.7910/DVN/VWRTAW`
  was built twice (caught and withdrawn mid-batch) and how `sadish` reached
  consolidation. Grep the whole header.
- [ ] **Fold the Step 2b checkpoint-subset trick into the pipeline.**
  `--retriage` only chains after the whole input finishes, so an interrupted run
  yields no Step 2b at all. A candidates file restricted to already-checkpointed
  rows reaches it in seconds; helper is in the discovery agent's scratchpad.
- [ ] **Three leads worth one retry, not rejected**: Mendeley
  `10.17632/3ffkvnzypc` (152 ids / 39 items, CC BY) -- the only blocker was
  Mendeley's file-listing API returning `{"error":400}` for `folder_id=root`.
  `zenodo.8401390` (119 ids x 10 items, 0-2 half steps, CC BY) -- clean on every
  gate, but the deposit cannot tell you which instrument the ten columns are, so
  shipping means guessing the construct. OSF `v4jqw` (HSPS Czech, ~1,143
  respondents) and `zenodo.13133336` (~400 diabetic patients) are
  **licence-blocked with no licence at all** and are in
  `license_blocked_candidates.csv` with contributors -- both worth an email.

## Uploaded: one table + its item text (2026-10-19j, confirmed 2026-10-20)

- [x] `olmos_gomez_2026_ai_mathematics` (7,677 rows, 853 x 9) + its
  `__items.csv` (45 rows) went up by path on 2026-10-20 and are **confirmed in
  the drafts**, read back off Redivis rather than inferred from the uploader's
  own report: `item_response_warehouse_7:next` holds 840 tables (839 before)
  with the response table at exactly 7,677 rows, and `irw_text_3:next` holds
  884 (883 before) with the item table at exactly 45. Single `NEW` adds, no
  doubling. `uploaded` is stamped 2026-10-20 in `itemtext_provenance.csv` and
  `itemtext/mapping_verification.csv`.

  Both still sit in **unreleased drafts** -- `irw_7` at 79 pending since v1.3,
  `irw_text_3` at 1 pending since v5.2 -- so the table is not public yet and
  the release is Ben's.
- [x] **The two staging directories are cleared, and that was safe** --
  checked against Redivis on 2026-10-20, not inferred. The openESM files in
  them (marian / nepal / neubauer / ryvkina / scharbert / tammilehto) are all
  in RELEASED versions: 40 response tables in `item_response_warehouse_5`
  v9.0 and 36 `__items` in `irw_text_3` v5.2, spot-checked non-empty
  (`scharbert_2024_esm_affect` 566,136 rows; its item table 36). All eight
  generating scripts are tracked in `data/` as well, so the staging copies
  were redundant twice over.

  **The earlier bullet here was wrong and is worth the correction.** It said to
  hold off "until `irw_text_3` is released" -- but it already was, at v5.2, and
  the note had been carried forward from when those drafts were genuinely
  unreleased. `red_up.drafts` reporting "N pending, Xd since v5.2" means v5.2
  SHIPPED and the draft sits on top of it; reading that as "unreleased" is what
  kept a dead hazard alive. Check the release state before repeating a
  clearance warning -- see [[irw-clear-uploaded-itemtables-hazard]], which is
  about `itemtext/itemtables/` and files pending RE-upload, a different thing
  from these staging dirs.

## Repos batch 2026-10-19: 8 tables staged, 70 leads unworked (2026-10-20)

Discovery, triage and a processing pass are done; standing records are written
(`search_terms_log.csv` +135, `human_review/human_review_zenodo_2026-10-19.csv`,
refined flags in `repo_triage_seen_keys.csv`, `BATCH_LOG.md`, 8 dictionary + 8
tag + 2 provenance + 2 mapping + 2 rights-register rows). Leads and their
verdicts are in `leads/repos_leads_2026-10-19.csv`.

- [x] **Uploaded 2026-10-20**, confirmed by ben-domingue: the 8 response
  tables (67,374 responses) into the newest shard and the 2 item text tables
  into `irw_text`. `itemtext_provenance.csv` stamped `uploaded=2026-10-20` for
  `feng_2023_fas` and `byrne_2026_health_info_sources`. **Both are in a draft
  and still need releasing** -- as does everything ahead of them in this file.
- [x] **The concurrent-session sweep is resolved.** Commit `f08d6007` on
  `claude/olmos-gomez-2026-ai-mathematics` had swept in this batch's three
  `data/*.py` scripts and its two new `instrument_rights_register.csv` rows
  (FAS, HLQ). That session backed all five out itself in `5110f23d`, so each
  now exists once, here. Nothing is owed at merge. `5110f23d` was still
  unpushed as of 2026-10-20, so PR #3121 will show the fix only once that
  session pushes.
- [ ] **70 leads still unworked**: 53 `recoverable_format` (mostly "keep only
  the N columns sharing one small integer domain, re-read"), 8
  `worth_retrying`, 7 `aggregate_continuous`, 2 `pii_suspected` that still
  need the structural-vs-incidental column check (zenodo 22749041, 20809).
- [ ] **`zenodo.15254212` (reading engagement) was rejected on my judgement**
  and is worth a second opinion if anyone disagrees: 1 never used by any of
  260 respondents across 71 items, and every respondent uses at most 2
  distinct values across a whole scale. Diagnostic is in the leads CSV.

## The 2026-10-19 upload happened: 78 tables are in the draft (2026-10-19)

ben-domingue uploaded the 2026-10-19c and 2026-10-19d slices on 2026-10-19 --
**78 tables, 557,054 responses**, from `automated_finding/irw_output`. Both
sections in `BATCH_LOG.md` are stamped accordingly, because a stale "nothing
uploaded" is the costly direction of wrong here: it invites a second upload and
**Redivis uploads APPEND**.

- [ ] **Release is still owed**, and so is the preceding draft: shard 7 held
  374 tables before this upload, all unreleased, and `irw_text` holds the two
  item-text tables from 2026-10-19b. The issues-page entry for
  `gerou_2023_dass21` / `kembara_2026_civic_agency` is owed at that item-text
  release.
- [ ] **Item text for the five rights-clear tables of the 10-19 slices** is now
  a second round rather than the same one: `kam_2016_ad_emotions` (5 items,
  stems in the Stata labels plus the deposit's questionnaire and codebook
  PDFs), `wei_2026_destination_image` (16 Chinese stems as column headers,
  anchors printed in the first one) and the three `sirovica_2022_*` tables (21
  items, deposit ships its own survey PDF). All study-own instruments, no
  rights question.
- [ ] The 2026-10-19f slice (#3103 group 2 tranche 1, 18 tables) is **not**
  uploaded.

## The 2026-10-18 release happened; eight sections below were stale (2026-10-19)

Reconciled against the corpus, because a stale "nothing uploaded" is the most
expensive kind of wrong record in this file: it invites a second upload, and
**Redivis uploads APPEND** -- delete-then-recreate is the only true replace,
and that mistake has doubled tables three times.

Eight 2026-10-18 batches (d, e, f, h, i, j, k, l) each said their tables were
staged and nothing was uploaded. All eight went up: 32 + 44 + 17 + 8 + 96 + 86
+ 21 + 29 = **333**, which is exactly what `item_response_warehouse_7` holds,
and both it and `irw_text_3` were released by ben-domingue on 2026-10-18. Each
of those sections is now marked `[x]`.

- Every uploaded table's row count was verified against its staged CSV: 334
  matched exactly, so nothing appended and nothing was missed.
- **`ghosh_2020_cas_ocs` was withdrawn** before release (334 -> 333). It is a
  byte-identical union of `ghosh_2020_cas` and `ghosh_2020_ocs`, found by a
  content scan of all 334 -- `red_up`'s collision check cannot see it, because
  the names do not collide. The CSV is kept at
  `irw_output/withdrawn_2026-10-18/`.
- **Item text: 17 of the 35 staged `__items` tables shipped**, 18 were removed
  from the `irw_text_3` draft before release under the 2026-10-15 silence rule.
  `automated_finding/itemtext_hold_2026-10-18.csv` is the per-table record and
  the 15 instruments behind them are now in
  `itemtext/instrument_rights_register.csv`. The batch sections below still
  count the staged item text, not the shipped item text; each now says which
  of its own were held.
- `hung_2026c_academic_self_efficacy__items` was held in ERROR -- it ships
  under the MSLQ register row -- and is the one re-upload owed from this round.

Because the release has happened, every item below written as "after the
release" or "at upload" is **due now, not pending**:

- [x] `metadata/covariate_labels/build.py` -- run 2026-10-21, PR #3153. One run
  covered all of it, including batches d, e, f, i, j and k whose `harvest.py`
  had already been run at their data commits.
- [ ] The issues-page entries owed by batches d, e, j and k -- per-batch lists
  in each section below and in the matching BATCH_LOG entries.
- [ ] `automated_finding/tags_auto_2026-10-18.csv` (301 rows) is written but is
  deliberately a separate file; merging it into `tags/tags_auto.csv` is a
  reviewed step.

## The staging folders were holding three batches at once (2026-10-20)

`irw_output/` held 33 response CSVs and `itemtext_output/` 28 `__items.csv`
that belonged to three different destinations, so `red_up irw_output` was not a
safe command for any of them. Split by destination into `runs/`, described in
`runs/STAGING.md`, with a per-file `MANIFEST.txt` (rows / ids / items / columns)
in each:

- `runs/uploaded_2026-10-20_nc11/` (was `stage_2026-10-19h/`) -- this batch,
  26 + 5, all uploaded 2026-10-20.
- `runs/uploaded_2026-10-19_openesm/` -- 30 PACO/STECCO/Ryvkina response tables
  and their 28 `__items`, **already released in `irw_5` v9.0** and live in
  `metadata.csv` / `itemtext_metadata.csv`. Kept as the record, never to be
  uploaded again.
- [x] **`kemp_2019_mss_*` uploaded** (ben-domingue, confirmed 2026-10-20), a
  REPLACE into `irw_4`; the three `metadata/table_changes.csv` rows are written
  (#3110, `irw_version` blank until a manifest carries the release). Files kept
  as the record in `runs/uploaded_2026-10-20_kemp_date_fix/`. It had been **a
  pending repair nobody was tracking as staged**: The three `kemp_2019_mss_*` rebuilds carry correct dates
  (2017-10-11 to 2017-11-29); the LIVE tables in `irw_4` still read January
  1970, because irw_4 v14.0 was built from output staged ten minutes before
  #3100's fix landed. Commit 790384df says as much and deliberately left them
  out of `table_changes.csv` ("their rows go in once a corrected upload is
  released"). This is a REPLACE into `irw_4`, so red_up will flag them
  `ELSEWHERE`; the three `table_changes.csv` rows are owed at that release.

Also worth knowing: the 2026-10-19f slice's 18 tables were **not** among those
33 files, so wherever that slice is staged, it is not `irw_output/`.

## From the 11 NC leads #3104 reopened (2026-10-19h, #3077)

**26 tables / 282,482 responses, uploaded 2026-10-20** (ben-domingue
confirmed the 5 item-text tables and then the 26 response tables). Files kept
as the record in `automated_finding/runs/uploaded_2026-10-20_nc11/`. All 26 passed
`irw-validate --profile upload` with zero failures and zero errors. (23 at first writing, plus the three the 3-item floor
ruled the same day unblocked: `jones_2026_agi`, `jones_2026_tech_worry`,
`baseke_2026_besaa3`.) 4 of the 11 leads carried data; the other 7 are
closed with reasons in their leads files. Every `todo` row across the
`repos_ledger_remine_2026-10-18_*` files is gone again (0 remaining).

- [x] **Uploaded in full** (ben-domingue, confirmed 2026-10-20): 26 response
  tables and 5 item-text tables. `uploaded=2026-10-20` stamped on the five
  `itemtext_provenance.csv` rows, the batch's 26 `metadata/data_notes.csv` rows
  written (`baseke_2026_css11` among them), dictionary and tag rows staged. The
  files are kept as the record in `runs/uploaded_2026-10-20_nc11/` -- do not
  point `red_up` at them, uploads append. See `runs/STAGING.md` and the
  2026-10-20a BATCH_LOG entry for what else that folder had been holding.
- [ ] **Release is owed** -- everything landed on the unreleased draft. After
  it: `metadata/covariate_labels/build.py` (the standing item at the top of this
  file; `harvest.py` has already run for this batch) and nothing else from this
  batch.
- [ ] **`gilbert_2026_dep_symptoms` is HELD on provenance, and one message
  closes it.** The deposit (`10.7910/DVN/G68C5Y`, CC BY-NC-SA 4.0) redistributes
  a psychotherapy RCT's depression data that it never names -- the analysis
  script says only "per McNeish, limit to C group only" -- so the originating
  trial's redistribution terms are unknown. The table is built and passes the
  upload gate (256 patients x 9 dichotomous DSM-5 items x up to 28 sessions,
  49,598 responses, with `wave` and `treat`) and sits in
  `automated_finding/held_provenance_2026-10-19/`. **Asked in #3120**
  (assigned to @joshgilbert1994, 2026-10-19): either he names the source trial
  and its terms, or he confirms redistribution is fine. The table moves into
  a fresh staging folder unchanged if the answer is clean, and the script stays as the
  record if it is not.
- [x] **Item text: 4 of the 8 candidate tables are STAGED** in
  `automated_finding/runs/uploaded_2026-10-20_nc11/items/` (179 rows; 5 tables and 200
  rows after the 3-item ruling added `jones_2026_agi`), all four through
  `normalize_nulls.R` -> `validate_items.R --resp-csv` -> `audit_batch.R
  --resp-dir` (4/4 PASS, no anomalies) and `irw-validate` (ok, nothing to
  report), with provenance and `mapping_verification.csv` rows written:
  - `baseke_2026_phq8` and `baseke_2026_gad7` -- stems and all four 0-3 anchors
    PARSED out of the deposit's Survey D codebook, which prints each stem
    beside its item code. The register's "PHQ and GAD screener family" row is
    verdict **`ship`** (phqscreeners.com: no permission required), read by name
    rather than discovered through the gate.
  - `jones_2026_tech_familiarity` and `jones_2026_ai_fear_2021` -- the
    administered prompt is a column of the response file, and the item codes
    come from the same function/dict the response script used. Stems searched
    verbatim and match no published scale; study-authored under the deposit's
    CC BY-NC-SA. `option_text` is blank on all seven points because the deposit
    publishes no anchor labels at all.
- [ ] **The other four Kenya tables need a rights ruling before their text can
  ship, and that is the remaining work here.** Their stems are all in the
  codebooks, so extraction is minutes; what is missing is a register row for
  each third-party instrument, none of which has one: the **Climate Change
  Anxiety Scale** (Clayton & Karazsia 2020, J. Environ. Psychol.), the
  **COVID-19 Stressors Scale**, the **Social Media Disorder Scale** (van den
  Eijnden, Lemmens & Valkenburg 2016) and the **EPV index adapted from the
  Political Life Events scale**. Silence does not ship (2026-10-15), so each
  needs its terms located and quoted. Note `BESAA` is already registered
  `block`, which is one reason its 3-item table is deferred anyway.
- [ ] **`jones_2026_ai_fear_2023` has no text of its own and is one deliberate
  cross-file mapping from having it:** its seven item codes are exactly the
  2021 table's seven prompts, on a -3..+3 scale instead of 1-7. Not cheap by
  the Step 3.5 test, so it was not taken here.
- [x] **`covariate_labels/harvest.py --commit HEAD platte_2026_mindset`: run**
  (the one script in this batch that reads an SPSS file and ships `cov_*`
  columns). Its labels are in the harvest cache -- school 1-15, gender
  1=Female/2=Male, class 6/7/8, achievement 1-5 -- but **not committed**:
  `build.py` only emits rows for tables that are live in the corpus, so these
  seven appear on the next build after the release, and running it now would
  have swept 8,084 lines of other batches' pending harvests into this PR. That
  build is the standing item at the top of this file, not a new one.
- [x] **The `baseke_2026_css11` caveat is written, as a data note** (2026-10-20):
  the paper and the deposit codebook both document five options "rated from 0
  (not stressful at all) to 4 (extremely stressful)", while the shared data holds
  exactly three distinct values on all eleven items, coded 1, 3 and 5. Shipped as
  recorded; the anchor-to-code mapping is what is unknown. It went to
  `metadata/data_notes.csv`, **not** `itemtext_issues.qmd`: that page takes
  concrete text-vs-table mismatches, and this is a source caveat about response
  coding, which is what data notes are for (#2529). The same append covers all
  26 tables of the batch -- one row each, which this batch had been owing and no
  earlier write-up had listed.
- [ ] **`tags_auto_2026-10-19d.csv` (23 rows), `tags_auto_2026-10-19e.csv`
  (3 rows) and `tags_auto_2026-10-19j.csv` (1 row)** are written and, like
  their predecessors, deliberately separate; merging them into
  `tags/tags_auto.csv` is a reviewed step. The `j` file was `d` until
  2026-10-20: two concurrent batches off the same base both picked `d` and git
  caught it as an `add/add` conflict on merge (see BATCH_LOG 2026-10-19j).
- [x] **The item-count floor is ruled: 3 ships, 2 does not** (ben-domingue,
  2026-10-19, now in `datastandard.md` "Before you start"). Three of this
  batch's four thin candidates are built and staged -- `jones_2026_agi` (the
  AGI block, three samples pooled, 1,963 respondents, item text shipped too),
  `jones_2026_tech_worry` and `baseke_2026_besaa3`. Kenya's OAC-2 stays out at
  2 items. Of the two older deferrals the ruling reached: **`dvn/vidgon` is
  unblocked and is a ready lead again** (4 items on 0-8 over 1,746 respondents,
  in `leads/human_review_recheck_batch5_2026-10-18.csv`, now statused `todo`),
  while `zenodo.22035093` is sharpened rather than closed -- one 4-item
  instrument or two 2-item ones decides whether it ships at all, and that needs
  the paper.
- [ ] **`10.25442/hku.30959672` is embargoed until 2032-12-28**, not dead: 236
  Hong Kong gifted adolescents, mindfulness/self-compassion/perfectionism. Worth
  a diary note rather than a lead. **The pipeline defect behind it:** the
  resolver reported it as "no resolvable tabular file on landing page", so an
  embargo and a dead deposit read identically. `api.figshare.com/v2/articles/<id>`
  returns `is_embargoed`, `embargo_type` and `embargo_date`; reading them in
  `_figshare_files` would turn a sticky wrong verdict into a dated one. Same
  family as the figshare-202 lesson.
- [ ] **The other half of #3104's ruling is still unworked:** 56 rows at
  `pending_ruling` in `leads/nc_licence_pending_ruling_2026-10-18.csv`,
  27,697 respondents, the largest a 23,781 x 38 Borealis deposit.

## Auto-tagging reads the construct's name as if it were the sample (2026-10-19)

Found by spot-checking `tags_auto_2026-10-18.csv` (301 rows) against the
dictionary descriptions they were derived from, three samples of sixteen. The
rows are fixed; the defects are general and belong in whatever tags the next
batch, `irw-auto-tag` included.

- **A keyword matched anywhere in a description is attributed to this table.**
  A deposit's description often names several scales and only the first is the
  one the table holds: `auerswald_2024_online_learning` came out
  Affective/mental health because *PHQ* appears two sentences later, describing
  a different scale in the same deposit. Construct type must read the leading
  clause only. Sample, age and language can read the whole description --
  those describe the study, which siblings share.
- **Every word of a description that is not the respondent clause is about the
  instrument.** `nguyen_2026_teacher_responsibility` ("13 teacher-responsibility
  items ... from 1,558 higher-education students") came out Workplace on the
  word *teacher*; the Clinical Perfectionism Questionnaire came out Clinical.
  Read the sample from the clause that names who answered, and where that
  clause names no known population leave it General/non-specific rather than
  re-reading the construct's wording.
- **A child topic is not a child sample.** `zara_2024_opd_sqs` -- a
  representative German sample of 5,041 *adults* in a study of child
  maltreatment -- came out Child (<18y).
- **`\b(...|adolescen|...)\b` can never match "adolescents"**: the trailing
  boundary falls between the n and the t. It was suppressing 14 of the batch's
  22 child samples, `osorio_2025_dsi`'s 6,845 twelve-to-seventeen-year-olds
  among them. Worth grepping the other keyword lists for a stem inside a
  bounded group.
- **A qualifier cannot be excluded with a lookbehind**, because a lookbehind
  has to anticipate every spelling of it. `(?<!organizational )resilien` missed
  both ways the batch writes it -- "organizational-resilience" in the
  description and `_org_resilience` in the table name. Veto on the phrase.
- **An unevidenced default is worse than a blank.** 120 of the 301 rows were
  asserting `Primary Language(s)` = `eng` with nothing in the record to support
  it. They are blank now: a blank is a question a human can answer and a wrong
  language code is not.

## Rights-register patterns that are too broad (2026-10-18m)

Found by running both rights surfaces over the 334 response tables and 35
`__items` tables staged for the 2026-10-18 upload, which is the first batch
where item text and response data went up together. **Nothing in that batch
was blocked** — every code-surface hit is an opaque code, and the one item-text
hit is a false positive — but three register defects surfaced that affect the
whole corpus, not just this batch. These are the mirror image of
`itemtext/register_gaps_2026-10-18.csv` (rows that match nothing): rows that
match far too much.

- **PSS stem `nervous and`** is a two-word fragment. It fired on
  `yang_2026_flsaq`'s Q14, "I get nervous and confused when I am speaking in
  English classes" — a Foreign Language Speaking Anxiety item with no relation
  to the Perceived Stress Scale. A stem this short will fire on a large share
  of any anxiety instrument in the corpus. It wants `^` anchoring or more
  words ("felt nervous and stressed").
- **CD-RISC code pattern `^C[0-9]{1,2}$`** matches the codes `c1`..`c99` that
  any study may pick for any reason. It fired on three unrelated tables in one
  batch: `tantia_2024_ats_course` (Attitudes Toward Statistics, Wise 1985),
  `cahyadi_2025_concern` and `oner_2026_basic_needs`. A single generic letter
  plus a number cannot identify an instrument.
- **BMQ code pattern `B`** — one unanchored letter, matched case-insensitively
  with `re.search`, so it matches any code containing a b. It is inert today
  only by accident: `check_item_codes` skips rows whose verdict is `escalate`,
  and BMQ's is. Any future verdict change on that row turns it on corpus-wide.

A register-wide scan for the same shape found six rows whose `match_item_code`
matches a plausibly generic code (IRI `^pts?[0-9]{1,2}$`, DASS `^item[0-9]{1,2}$`,
CD-RISC, BMQ, HAM-A `^a[0-9]{2}$`, RMET). The IRI and DASS ones are the next
most likely to misfire: `PT1`-`PT4` fired on `binus_2025_perceived_trust` and
`septiani_2026_trust`, where PT is plainly "perceived trust".

Decision wanted: these are warnings, by design (`rights.py`'s rule 1, a hit is
a lead not a verdict), so none of this is urgent. But a check that cries wolf
on generic codes trains people to skip reading it, which is exactly how
`gillman_2023_pss` shipped. Worth one pass tightening the six patterns.

Also noted, under `rights.py`'s rule 2 (a miss is not an all-clear): **FLCAS /
the Foreign Language Classroom Anxiety Scale (Horwitz, Horwitz & Cope 1986) is
not in the register at all**, and `yang_2026_flsaq`'s 18 Chinese items are an
FLCAS-family instrument. Its wording went up in this batch. Not a
contradiction of any ruling — there is no ruling — but if FLCAS should have a
register row, that table is the one to check first.


## From the #3077 figshare re-mine slice, worked (2026-10-19a)

The 20 `todo` rows of `leads/repos_ledger_remine_2026-10-18_figshare.csv`,
worked end to end; that file is now closed (0 `todo`). 13 of 20 deposits
shipped. Full write-up in BATCH_LOG 2026-10-19a.

- [x] **41 tables (190,707 responses) UPLOADED 2026-10-19** by ben-domingue
  (`red_up`, so into the unreleased `item_response_warehouse_7` draft --
  release is a separate step). All 41 passed `irw-validate --profile upload`
  with zero failures beforehand, and all 41 names were new, so nothing
  appended to an existing table. Dictionary rows (41) and
  `codebook_at_ingest.csv` rows (41) are on main in #3097; tags are in
  `automated_finding/tags_auto_2026-10-19.csv` (41 rows, every atom checked
  against `TAG_VOCAB`), deliberately a separate file as on 2026-10-18.
  `item_response_warehouse_7` held 333 tables before this batch, so **374
  after**, against the 1,000-table shard cap.
  Per-table staged counts (`rows`/`ids`/`items`) were snapshotted before the
  staging folder was cleared, at
  `runs/figshare_slice_2026-10-19_staged_counts.csv` -- gitignored, so it is a
  session artifact, not a standing record: the authoritative counts are the
  table list in BATCH_LOG 2026-10-19a.
  **Do not upload this batch again** -- Redivis appends, and
  delete-then-recreate is the only true replace.
- [ ] **Covariate labels:** owed for the four `.sav` scripts shipping `cov_*`
  (`jiao_2024_ehealth_literacy`, `galanis_2025_miss`,
  `bulgay_2026_technology_use`, `gerou_2023_humility_quiet_ego`). Harvested at
  this batch's data commit (`042113c6`, squash-merged as `e18521bf`); the
  upload has happened, so `python3 metadata/covariate_labels/build.py` and a
  commit of `covariate_labels.csv` are due at the next release.
- [ ] **Issues-page entries owed by this batch: none.** No table ships item
  text, so there is no text-vs-table mismatch to publish. Re-check if the two
  item-text candidates below ship.

### Item text: both ready tables are now STAGED (2026-10-19b)

- [x] **`gerou_2023_dass21__items.csv` (84 rows) and
  `kembara_2026_civic_agency__items.csv` (30 rows) UPLOADED 2026-10-19** by
  ben-domingue into the `irw_text` draft (release is a separate step);
  `uploaded=2026-10-19` is stamped on both rows of
  `itemtext_provenance.csv` and `itemtext/mapping_verification.csv`.
  Both table names were new in `irw_text`, so nothing appended.
  Before upload, the full gate chain was run
  against the staged response CSVs: `normalize_nulls.R`,
  `validate_items.R --resp-csv` (item and resp sets match exactly on both),
  `audit_batch.R --resp-dir` (2 of 2 PASS, no anomalies), `irw-validate` (both
  clean) and `check_provenance.R` against the live issues page (exit 0).
  Provenance and `mapping_verification.csv` rows are written; the folder holds
  nothing but the two `*__items.csv`. Write-up: BATCH_LOG 2026-10-19b.
- [ ] **An issues-page entry is owed for `gerou_2023_dass21` at publish**,
  forced by its `public_note`: the shipped wording is the DASS-21's official
  English, while the study administered a Greek translation that is withheld.
  The page lives in the datapages/irw repo. `kembara_2026_civic_agency` earns
  no entry (author-supplied translation, no text-vs-table mismatch).
- [x] **No ruling is needed for what shipped: #2121 already governs it.**
  Corrected 2026-10-19 after this was first written up as a pending ruling.
  `itemtext_standard.md`'s 2026-09-08 ruling (irw#2121) says that when a study
  administers a translated adaptation and IRW ships the original-language
  wording as a stand-in, two instruments are in play and the test is the terms
  of **the thing you actually copied**. IRW copied the public-domain English
  DASS-21, so it ships; Lyrakos & Arvaniti's Greek governs the Greek wording
  only, and its terms could not be located, so the Greek is held. Both of the
  ruling's limits are met -- a straight translation rather than a revision, and
  the originator's terms quoted rather than asserted. The structural twin is
  `li_2024_bdyz`.
- [ ] **What IS open is only the upgrade**, and nothing is blocked on it: could
  the Greek wording itself move into the base fields? That needs the
  translators' terms, or a ruling that the DASS site's "copied without
  restriction" reaches the translations it hosts. Recorded as a register row
  ("DASS-21 GREEK translation, Lyrakos & Arvaniti", verdict `hold`) with both
  clauses quoted. A `ship` answer is re-run-and-replace, never a withdrawal.
- [x] **The reason this got re-derived from scratch is now fixed.** The #2121
  ruling was cited nowhere outside its own section -- not from the fallback
  paragraph in the same file, not from this pipeline's own SKILL.md, not from
  the DASS-21 register row, which is every place a batch actually looks. All
  three now point at it, and the English DASS row names the Greek row.
- Held on an existing verdict, no work to do: `jiao_2024_eheals` and
  `hernandezencuentra_2026_eheals` (eHEALS `hold`),
  `gerou_2023_hexaco_honesty_humility` (HEXACO-PI-R `block`).
- Held on a row this batch WROTE (six new `hold` rows, register now 349):
  `hernandezencuentra_2026_ehlq` (eHLQ), `jaber_2025_epds` (EPDS),
  `gerou_2023_quiet_ego` (Quiet Ego Scale),
  `sadiyah_2026_financial_self_efficacy` (Lown's FSES),
  `jiao_2024_vaccine_conspiracy` (VCBS), and the MAI as an instrument.
  **A ruling on any of them releases an extraction-solved table.** Four of the
  six carry deliberately empty matchers, with the reason in the row: check
  them by name.

### A one-character defect was hiding 18% of `mapping_verification.csv`

- [x] **Fixed 2026-10-19b.** `lint_verification.R` -- the only check that
  catches a status claiming more than its evidence supports -- reported 423
  ERRORs over 2,123 rows of a 2,585-row file. One malformed field on line 1705
  (`""PARTIAL"` for `"PARTIAL"` in `ritzel_2020_farmer_burden`'s `status`)
  desynchronises R's CSV parser, so **462 rows, every one written since
  2026-09-26, were invisible to the lint**; Python's `csv` reads the file
  fine, which is why nothing noticed. Repaired byte-wise; the lint now reports
  2,585 rows and 1 ERROR.
- [ ] **That remaining ERROR is a real one to adjudicate**:
  `prasetiyo_2022_act` carries `status=FAILED`, which is not in the enum
  `VERIFIED/PARTIAL/NO_ROUTE/NOT_NEEDED`. Left exactly as found -- it is
  someone's verdict to interpret, not a parse defect.

### Worth fixing in the pipeline, not in this batch

- [ ] **A duplicate DEPOSIT is invisible to every check we have.**
  `figshare 14705967` and `14711232` are the same study, the same
  byte-identical `PPD full.sav` (20,941 bytes) and the same two `.spv` files,
  differing only in one co-author on the record. Both are separate ledger keys
  and both were leads. `check_shipped.py` cannot see it (the table names would
  not collide either -- the `ghosh_2020_cas_ocs` blind spot one level up), and
  it cost two independent reviews here. A content hash, or even
  size-plus-filename, over the resolved data file would catch both shapes;
  `oversized_candidates.csv` already shows the resolver can see size.
- [ ] **A lead's `n_participants` is a row count three times in 20 rows**
  (figshare 30826265, 24777858, 30426739). The brief's "rank by instrument
  shape, not response count" rule exists for this, but the leads files still
  print the raw number as if it were N; a ratio of rows to distinct id in the
  triage would make it visible at ranking time rather than at download time.


## From the #3077 zenodo_rest batch B, worked (2026-10-18i)

- [x] **96 tables (267,363 responses) + 6 item text tables uploaded and released 2026-10-18**
  (ben-domingue; `uploaded=2026-10-18` stamped). 18 of 26 deposits shipped.
  All 198 tables passed `irw-validate --profile upload` with no failures
  before upload, and every uploaded row count was verified against its staged
  CSV afterwards.
- [ ] **51 leads still `todo`** in `leads/repos_ledger_remine_2026-10-18_zenodo_rest.csv`
  for a batch C. All 26 of this batch's rows carry a status.
- [ ] **Covariate labels:** harvested at `0f50eb3a` for the nine `.sav` scripts
  (hung_2026c_cognitive_load, peng_2026_mental_health_literacy,
  xue_2026_admin_ai_acceptance, mairean_2024b_time_trauma,
  mairean_2024c_childhood_dissociation, mairean_2023c_emergency_personnel,
  estevespairazaman_2022_self_medication, gonzalezrobles_2018_oasis,
  yang_2024c_online_film_festival), all exit 0. Run `build.py` after the
  release and commit `covariate_labels.csv`.
- [ ] **Issues-page entries: none owed by this batch.** Both item-text deposits
  are `data_labels` with no text-vs-table mismatch, which is below the bar.

### Register-row requests (rights)

- [ ] **ProQOL (Professional Quality of Life Scale, Stamm / proqol.org) has no
  register row.** `mairean_2023c_proqol` (30 items, 372 respondents) ships
  because its item codes are the deposit's positional `pro1`-`pro30` and no
  item text is shipped, so no wording is exposed -- but if a ruling blocks the
  ProQOL, that table is what a withdrawal targets. Its own terms allow free
  unmodified use with credit but not sale.
- [ ] **CTQ** (Childhood Trauma Questionnaire, Pearson) and **PAI-BOR**
  (Personality Assessment Inventory Borderline Features, PAR) have no register
  rows. Both withheld from `mairean_2024c` on the conservative reading. The CTQ
  was flagged independently by the mendeley batch the same day.
- [ ] **ZTPI's matcher does not reach its own codes.** The register's pattern is
  `^ZTPIQ[0-9]+R?$`; the deposit spells them `ZTPI_1`..`ZTPI_18`, so the block
  was caught by reading the items. One more instance of the 154-inert-rows
  finding in BATCH_LOG 2026-10-18g.

### Smaller things

- [ ] `automated_finding/itemtext_provenance.csv` has no `translation_source`
  column, so the two `translated_substitute` rows this batch adds join the 72
  rows already in `check_provenance.R`'s `sub_nocol` class. The remedy is to
  add the column repo-wide and backfill, not to patch these rows.
- [ ] `automated_finding/oversized_candidates.csv` has one uncommitted appended
  row (`10.17632/pv7y6kmg86.1`, a 267MB `.rds`) written by the concurrent
  mendeley run, not by this batch. It is a standing record and wants committing
  by whoever owns that run.
- [ ] A ruling would help on whether an 8-construct PLS-SEM battery of 3-item
  scales should ship as 8 tables (what `septiani_2026` does here, following
  datastandard.md's one-file-per-scale rule) or as one 24-item table. Six of
  this batch's deposits have that shape; the choice was made consistently but
  it is a convention question, not a data one. Nothing is blocked either way.

## From the #3077 mendeley leads, worked (2026-10-18h)

- [x] **8 tables (132,575 responses) + 5 item text tables uploaded and released 2026-10-18**
  (ben-domingue; `uploaded=2026-10-18` stamped).
  zara_2024_opd_sqs, zara_2024_phq4, yang_2026_flsaq,
  yang_2026_appreciative_education, tantia_2024_ats_{field,course},
  shehayeb_2024_math_{anxiety,teacher}. Item text for all but the two zara
  tables and yang_2026_appreciative_education. NOTE: the item text for
  yang_2026_flsaq, tantia_2024_ats_{field,course} and
  shehayeb_2024_math_anxiety was HELD before release -- see the 2026-10-18
  itemtext hold list -- so of this batch's 5 item text tables only
  shehayeb_2024_math_teacher shipped.

### Rulings wanted (none blocks what is staged)

- [ ] **Three instruments want a rights-register row**, all found by reading
  stems because none has one: **CTQ** (Childhood Trauma Questionnaire,
  Bernstein & Fink / Pearson -- 28 items withheld by hand from the otherwise
  shipped `rkw2g38rjp`), **CARS2-ST** (WPS -- `yj5drfdzht` closed), **RS-25**
  (Wagnild & Young Resilience Scale -- `dytvjkmv9z` deferred). This is the
  concrete half of the 154-inert-block-rows finding in BATCH_LOG 2026-10-18g.
- [ ] **The SDQ row exists and cannot fire.** `hp6y7cj9r2` carries the
  Strengths and Difficulties Questionnaire under subscale names (`pconsid`,
  `prestles`, `psomatic`, `ptantrum`, `ploner`, `pobeys`, `pworries`,
  `pcaring`, `phyper`, `ppeer`, `pshares`, `pbullied`); the block row's
  `match_item_code` is `SDQ1|SDQ_1|sdq1|SDQ_Pro1` and matches none of them.
- [ ] **Two documented rights FALSE positives shipped anyway**, both read
  rather than inferred, both recorded in `itemtext_provenance.csv`. Confirm
  the readings stand: `tantia_2024_ats_course` c1-c9 vs the CD-RISC matcher
  `^C[0-9]{1,2}$` (the stems are Wise's ATS course items), and
  `yang_2026_flsaq` Q14 vs the PSS row on the substring "nervous and" (FLSAQ
  Q14 is about speaking English in class). `irw-validate` says "do not ship
  its item text without a ruling", so this is that ruling request.

### Leads still to work from this file (33 deferred, each with its blocker)

`leads/repos_ledger_remine_2026-10-18_mendeley.csv` carries a per-row reason.
The highest-value ones, with what they need:

- [ ] **`6bhr52dc5v`** (1,198) and **`wcszkbp9z8`** (524): the `T2S*` and
  `_M1`/`_M2` suffixes are SECOND WAVES -- both want a `wave` column, not
  extra tables. Both have English stems, so item text is cheap.
- [ ] **`9dcs5nvwtw`** (918): MTAS + RCADS, English stems. Shares all 16 MTAS
  codes with `6bhr52dc5v` but only 14 of 835 response vectors, so they are
  different samples -- consider one merged MTAS table with `cov_study`.
- [ ] **`dpcc2wms6h`** (1,317) TMMS-24 + ERQ, full Spanish stems.
  **`j5zjb46tr7`** (1,092) UEF-1, value labels only so no item text.
  **`5tjkv36r3s`** (916) AQ/BVAQ/PAQ -- drop the EQ (register block) and
  handle a source labelling error where AQ value labels give both 1 and 4 as
  "Acord total".
- [ ] **`fwgxbt4pjr`** (229 + 435): CDAT_1-20 is identical across both
  samples, so those merge with `cov_study`, offsetting sample 2's id past
  sample 1's observed max. Full Polish stems.
- [ ] **`zvj6cz68sc`** (545): `SUJETO` is a WITHIN-CENTRE serial -- 451 unique
  over 545 rows, 94 repeats with different `CURSO`/`EDAD`/answers -- so `id`
  must be prefixed by centre. Drop STAI (register block).
- [ ] **Four offset-header workbooks**: `4n5x4ffzn5`, `wwccx5cx4z`,
  `3cgh2fsgn4`, and `nd6nxj4y8t` (which has clean `.sav` files beside the
  workbook -- use those; its 28- and 29-item files are nested subsets of the
  31).
- [ ] **`ry2dvfydjd`**: 300 rows over 259 patients with a date-of-admission
  column -- repeated measures, needs a wave or date column.
- [ ] **`zktjjx93sv`**: human_review. 563 x 300, 132 binary checkbox columns,
  22 constant-zero, possible HLS-EU. Needs a person to map the instrument.
- [ ] Remainder: `vptj28s8pk`, `tnkv5z3byg`, `4vkrzxjtwf` (note `Age` is a
  BIRTH YEAR), `m7k8638rmc`, `9pzs3y5f82` (no person id, so pre/post cannot
  be linked), `x49yj8588t`, `xfrvh9tkwk`, `n69rdbph73`, `m85v5s7gx2`,
  `zb62c5snkm`, `kdw549kj22`, `v7kdvzcrns`, `sngb8z87tw` (-999 sentinels),
  `kprdr35gwb`, `rj6t9w4v2j`, `hp6y7cj9r2`, `dytvjkmv9z`, `9h8p47sk8w`,
  `ctg7km2fkr`.

### Non-English item text already identified as cheap

Adds to the deferred translation round already in TODO: `dpcc2wms6h` and
`zb62c5snkm` (Spanish), `fwgxbt4pjr` (Polish), `m85v5s7gx2` and `dytvjkmv9z`
(Persian). `x49yj8588t` needs no translation -- the deposit ships its own
English questionnaire.

## From the #3077 zenodo_rest batch C (2026-10-18j)

86 tables (147,644 responses) + 4 item text tables uploaded and released 2026-10-18
(ben-domingue; `uploaded=2026-10-18` stamped). The leads file
`leads/repos_ledger_remine_2026-10-18_zenodo_rest.csv` is **closed** -- all 77
of its leads carry a status across batches A, B and C, 0 `todo`.

### Rulings wanted (none blocks anything staged)

- [x] **A university NetID: PII or not?** ANSWERED 2026-10-19 by the
  structural/incidental narrowing (#3113, BATCH_LOG 2026-10-19g): `Username` is
  a column whose job is to hold an identifier and it holds one for every
  respondent, which is STRUCTURAL, so the whole-candidate skip stands and the
  carve-out is not widened. The deposit stays skipped; its other file is the
  PSS and was blocked anyway. Original note follows.
- [ ] **A university NetID: PII or not?** `zenodo.5217991` was skipped because
  `Username` holds 236 NetIDs (`bdz0311`, `btr3574`) for identifiable students
  at one university. The narrowed carve-outs cover a platform participant ID
  (2026-09-20) and a clinic register number (2026-09-26); a NetID that encodes
  initials is neither, so the blanket rule was applied rather than the carve-out
  widened. If it counts as an institutional serial, the remedy is the row index
  and the deposit ships one 22-item table over 236 respondents (its other file
  is the PSS and stays blocked either way). Third PII edge case in two days --
  the other two are in BATCH_LOG 2026-10-18f.
- [ ] **Register rows wanted**, every one found by reading stems because no
  matcher could reach it: UTAUT/UTAUT2 generally (four deposits in this batch
  ship UTAUT response tables); servant leadership other than van Dierendonck's
  30-item SLS; organizational justice; OCB; Netemeyer's Work-Family Conflict
  scale; the COPSOQ job-demand and social-support blocks; DES; BFI-10;
  LPFS-BF. Adding to batch B's list (CTQ, PAI-BOR, ProQOL) and the mendeley
  batch's (CARS2-ST, RS-25, SDQ-by-subscale).
- [ ] **PLS-SEM 3-item construct batteries**: still one file per scale, as
  batch B. Four more deposits with that shape here (binus_2025 x7,
  cahyadi_2025 x9, rumangkit_2026_dm x6, triana_2025 x6). One ruling settles
  all of them.

### Bugs for whoever owns the file

- [ ] **`remine_ledger.licence_ok` rejects `cc-zero`.** Zenodo's licence id for
  CC0 1.0 is `cc-zero`, which fails the `startswith("cc0")` test and reads as
  non-open. Three CC0 deposits in this batch carry it (zenodo.20844, 22609,
  21054). No harm done here -- the leads file was built from the triage CSV's
  `license` column, which normalises to `cc0` -- but a batch resolving the
  licence from the Zenodo API directly would drop every CC0 Zenodo deposit.
- [ ] `ghosh_2020_cas_ocs` is staged in `irw_output/` with no row in
  `dictionary_auto.csv`. Not mine -- it belongs to the concurrent mendeley
  batch -- but it is the only staged table of the 284 without one.

### Owed after the next release

- [ ] **Covariate labels:** `harvest.py --commit HEAD` for the three `.sav`
  scripts in this batch that ship `cov_*` -- `baruah_2026_fake_news`,
  `yu_2025_asian_american_coping`, `walton_2023_remote_work` -- then
  `build.py` and commit `covariate_labels.csv`.

### 29 deferred leads, each naming the blocking fact

In the leads file with a per-row reason. The ones worth picking up first:

- [ ] **zenodo.10942726** -- ERQ 10 and SWLS 5 are register `block`, but the
  workbook also ships a **`dictionary` sheet** beside several study-authored
  blocks. Separate the blocked instruments and the rest is a good item-text
  case, which is rare in this pool.
- [ ] **zenodo.7736935** -- 156 x 75 with **73 variable labels present** and no
  ordinal block the profiler could identify. Another likely item-text case once
  the item columns are picked out by hand.
- [ ] **zenodo.4007786** -- TB knowledge/perception/adherence, three clean
  blocks (perc 10 on 1-5, know 14 on 1-5, adh 8 on 0-1), deferred only for
  time. The cheapest remaining win.
- [ ] **zenodo.6625347** -- VisAWI 18 + SUS 10 + UEQ 6; SUS and UEQ are named
  third-party usability instruments and want a rights read first.
- [ ] **zenodo.3866196 / zenodo.3866225** -- adjacent record ids, one author;
  check for a shared sample before shipping either (the 22089166/21522509 pair
  in this batch is why).
- [ ] **zenodo.2667331** -- 100 x 220 with twelve `e1`/`e2` blocks spanning
  ranges from 0-1 to 0-9; needs its blocks mapped before any range is asserted.
- [ ] **zenodo.6844831** -- multi-sheet Chinese workbook (部屬 / 主管 / 績效);
  the sheets may be different units of observation, so the respondent mapping
  has to be settled first.

## From human_review re-check batch 5 (2026-10-18k, #3077 item 2)

21 tables + 1 item text table uploaded and released 2026-10-18 (ben-domingue;
`uploaded=2026-10-18` stamped).

- [ ] **Recommendation, needs a yes: stop selecting from the human_review
  archive as a queue.** Shipped-per-25 ran 21, 19, 14, **9** across batches
  2-5. Batch 5's misses are structural, not luck: aggregate-only files (3 of
  25), unlabelled matrix blocks whose instruments cannot be named so rights
  cannot be verified (4 of 25), and blocked instruments carrying the whole
  deposit (2 of 25). If more is wanted from the remaining 6,171 rows, select
  on "has a label level" — the triage already records it and the filter
  already ignores it — rather than on shape.
- [ ] **PII screen, third surface: it does not read SPSS variable labels.**
  `zenodo.13913289` holds 1,472 real dates of birth in a column named `Q009`,
  with "Date of birth? (dd/mm/yyyy)" in the variable label. `screen_for_pii`
  reads names and values, never labels, so every opaque-coded SPSS deposit is
  invisible to the label tier. One-line fix: run the existing label tier over
  `meta.column_names_to_labels` too. Not applied — `irw_triage_updated.py` was
  owned by a concurrent session. (Related: the deposit's Italian twin screens
  clean because its label reads "Data di nascita".)
- [ ] **Issues-page entry owed at publish:** `antunez_2015_lotr` (LOT-R is
  verdict `ship_with_note`).
- [ ] **Five register verdicts wanted**, now in
  `itemtext/register_gaps_2026-10-18.csv` (30 instruments): three rows that
  BLOCK but cannot match anything (KIDSCREEN-27 — refused a 2,936-row deposit
  entire; the English Jackson & Eklund flow scale; CD-RISC-10 under `CDR*`
  codes), and two instruments with NO row that this batch SHIPPED — the
  Differentiation of Self Inventory (22 items, 6,845 respondents) and the
  reduced Morningness-Eveningness Questionnaire.
- [ ] **Covariate labels:** harvest owed for the eight `.sav`/`.dta` scripts
  in this batch (osorio_2025_parenting_differentiation,
  antunez_2015_circadian_optimism, chaple_gil_2021_gad7,
  fecker_2026_mansplaining, wang_2026_pmpu_diary,
  vila_lopez_2023_brand_attachment, turska_kawa_2025_religiosity_conspiracy,
  green_2025_ai_job_expectations), then `build.py` after the release.
- [ ] **10 deferred rows, each naming the fact that blocks it** — see the
  leads file. The two cheapest: `zenodo.5090519` (1,000 respondents, 22
  blocks, Latvian, no blocker found — just needs block-to-construct mapping)
  and `zenodo.17367532` (1,000 respondents, Polish CATI, same shape).
  `zenodo.16777938` is the highest-value: drop its blocked UCLA and RRS
  blocks and the MSPSS + CES-D blocks are shippable from 69 labelled Chinese
  columns.
- [ ] `dvn/vidgon` and `zenodo.22035093` are deferred only on thinness — a
  4-item table each. A ruling on whether 4-item tables are worth shipping
  would close both.

## From the #3077 blank-flag batch, non-dataverse (2026-10-18l)

29 tables / 220,891 responses uploaded and released 2026-10-18 (ben-domingue). All 35 leads carry
a status. No item text shipped.

### Decisions wanted

- [ ] **PII screen, fourth gap: `_looks_like_person_names` is Latin-alphabet
  only.** `figshare 27635013` has 455 distinct real Chinese names in a column
  called `name` and screened CLEAN. The regex `^[A-Za-zÀ-ɏ]...`
  fails every CJK, Cyrillic, Greek, Arabic, Hebrew, Thai and Devanagari
  roster, and the bare label `name` is exactly the case the content check
  exists for. Skipped by hand. `irw_triage_updated.py` is the parent
  session's file, so not fixed here.
- [ ] **IGD ruling — the biggest prize left in #3077.** `figshare 25123145` is
  **8,662 respondents x 27 binary items with a deposited 27x9 q-matrix**. The
  register blocks IGDS9-SF (9 items); this is a 27-item pool across the 9
  DSM-5 criteria and the deposit ships **no item wording**, so it cannot be
  shown not to be the blocked instrument. Deferred on that alone.
- [ ] **Technology Readiness Index** (figshare 20071678, deferred): no
  register row and commercially licensed. Wants a ruling before that deposit
  is worked.
- [ ] 10 new rows in `itemtext/register_gaps_2026-10-18.csv` (now 40, of which
  22 have no register row at all), including FoMO under `TF`/`SF` whose item
  text **would have shipped** on a clean `rights.py` run, and SDRS-5 whose
  matcher columns are both empty.

### Leads still to work from this slice

- [ ] **48 `noflag_dataverse` leads** — untouched, a separate batch.
- [ ] **15 deferred**, each naming its blocking fact in the leads file. Best
  first: `figshare 30178486` (961 + 152, English stems in labels, Body
  Appreciation Scale has no register row); `mendeley 5ywv53yyd3` (306 x 117,
  nine clean blocks); `figshare 31077850` (499 x 86, Spanish COVID survey,
  every stem in its labels, confirmed NOT HLS-EU-Q16); `figshare 13951619`
  (344, two 30-item blocks behind an offset header).

### Owed after the next release

- [ ] `metadata/covariate_labels/build.py` and commit `covariate_labels.csv`.
  `harvest.py --commit HEAD` run for contreras_valdez_2026,
  deleon_villagran_2026, meule_2019, le_2026 and hung_2026d — all five exit 0,
  so none of them reads a gitignored cache.

### Item text owed on a ruling

- [ ] **All five `hung_2026d` tables** have their item text held: FoMO and
  SDRS-5 are register block rows and the 16-item burnout battery could not be
  pinned to a row. Both label levels carry full English stems, so all five are
  extraction-solved and ship the day a ruling lands.
- [ ] `deleon_villagran_2026_tmms24` and `contreras_valdez_2026_*`: full
  Spanish stems in the variable labels, no author English, so the English
  would be IRW-generated and owes a `translation_source` plus an issues-page
  callout. Same deferred round as the eight deposits in 2026-10-18f.

## From the #3077 ledger characterisation (2026-10-18g)

Nothing here is uploaded. Ben held PR #3089 and all uploads deliberately on
2026-10-18; 94 tables and 19 item text tables sit staged in
`automated_finding/irw_output/` and `itemtext_output/`.

### Decisions wanted (none blocks anything already staged)

- [ ] **Do not reopen `no_usable_file`** — recommendation, needs a yes. 2,311
  keys re-mined returned 10 leads (0.4%) against `human_assistance`'s 18%, and
  the resolver demonstrably ran. Item 4 of #3077 proposes
  `seen_ledger.py drop --flag no_usable_file`; it would cost a day of
  downloads for ten leads. Say no and the issue's item 4 closes.
- [ ] **Rights register: 154 of 243 `block` rows can match nothing** on either
  surface (`itemtext/check_register_coverage.py` for the breakdown; includes
  NEO-FFI, MBI-HSS, PSQI, SCL-90-R, HADS, BDI-II, ISI, PERMA-Profiler, the
  Ages & Stages family). Which get matchers is a rights ruling, so it is
  yours. Deliberately not fixed here: a matcher has real false-positive cost.
- [ ] **PII edge cases from the `good`-keys batch — one is now workable, one
  is still open.** The structural/incidental narrowing (#3113, BATCH_LOG
  2026-10-19g) resolves the first and does not reach the second:
  - `10.17632/4fp3nxmcgs` **REOPENS as a workable lead.** One respondent of 382
    typed their own name into a free-text `school` field (376 gave the
    university). The column collects a school name, not identifiers, so this is
    incidental: null the cell and ship. Otherwise a clean 382x47 five-block
    AI-literacy instrument. NOT YET PROCESSED — it needs a normal pass.
  - `zenodo.21121992` **stays open.** Its name column holds the three deposit
    AUTHORS' own names (an enumerator tag published on the record), not data
    subjects'. The narrowing is about identifying respondents and says nothing
    about a self-named author, so this still wants a ruling rather than an
    inference.
- [ ] **`zenodo.20550197`** duplicates live data: 200 of its 201 distinct
  OSTES response vectors already exist in `gonzalezros_2025_ostes`. Supersede
  the live table, ship only the ~425 new respondents, or skip?
- [x] **RULED 2026-10-29 (ben-domingue): SKIP `zenodo.20475015`.** The naming question is closed by closing the deposit. 860 respondents x 30 AIOAS items, clean, would have been one table -- but its Zenodo creators are literally "Anonymous, Anonymous" with no linked paper, so `authorname_year_construct` has no author to use and there is no citation to give. Ben was offered a repository-stub name (`zenodo_20475015_aioas`), `anonymous_2025_aioas` and an instrument-first name, and chose to skip. **This is a precedent, not a one-off: a deposit with no attributable author and no paper does not ship, however clean its data.** Original note below.

  **`zenodo.20475015`** (860x30 AIOAS, clean) held only because the
  creators are literally "Anonymous, Anonymous" with no paper, so there is no
  author name for the file-naming convention. Same question as DVN/YB5PVO;
  one ruling settles both.

### Leads still to work

**Recounted against the files on 2026-10-19, because the numbers below had
gone stale in two directions.** The `status` column is free text, so count it
rather than trusting a remembered figure — and a slice can be closed without
this list saying so.

- [x] **0** zenodo_rest, `leads/repos_ledger_remine_2026-10-18_zenodo_rest.csv`
      — CLOSED. All 421 rows carry a status across batches A/B/C (143 of them
      `deferred`); the "77" above was never a `todo` count.
- [x] **0** mendeley, `leads/repos_ledger_remine_2026-10-18_mendeley.csv` — no
      `todo` rows. The open work there is **57 `deferred`**, each naming its
      blocker in the file; see the 2026-10-18h section above.
- [x] **0** figshare, `leads/repos_ledger_remine_2026-10-18_figshare.csv` —
      CLOSED 2026-10-19a: all 20 `todo` worked, 13 shipped, 41 tables.
      15 `deferred` remain in that file, listed in the 2026-10-18l section.
- [ ] **48** `noflag_dataverse`, `leads/repos_ledger_remine_2026-10-18_noflag_dataverse.csv`
      — the largest genuinely unopened slice, and not previously listed here.
- [ ] **57** human_review pool remainder, statused `unworked` in
      `leads/human_review_recheck_batch5_2026-10-18.csv`. Batch 5's own 25 are
      worked; 32 further rows are `deferred` to the zenodo_rest and dvinst
      files that own them.
- [ ] **13** dataverse installations, `leads/repos_ledger_remine_2026-10-18_dvinst.csv`;
      **3** `ha_dvportals`, **1** osf, **1** `ha_portals2`, **1** tail, and
      4 singletons across the `nuf_*` files.
- [ ] **16** deferred rows across batches A/f needing a derivation rule
      (Google Form exports whose headers are stems with no item code)
- [ ] **10** from the `no_usable_file` sweep — low priority, that is the whole
      0.4%
- [ ] **557** blank-flag keys triaging as of 2026-10-18g; leads file owed

### Item text

- [ ] **Eight deposits from the `good`-keys batch carry stems in their own
  headers but were administered in Indonesian, Turkish or Chinese with no
  author English.** Shipping them means IRW-generated translations, each owing
  a `translation_source` and a public issues-page callout. That is one
  deliberate round, not a bolt-on. **`zenodo.20017889` is the best candidate
  in the backlog** — it deposits its questionnaire in both Chinese and
  English, so it needs no IRW translation at all.
- [ ] Issues-page entries owed at publish for the 2026-10-18d/e/f batches —
  per-batch lists in those BATCH_LOG entries.

### Owed after the next release

- [ ] `metadata/covariate_labels/build.py` and commit `covariate_labels.csv`.
  `harvest.py --commit HEAD` has been run three times today (batch d, batch A
  at HEAD for 12 `.sav` scripts, batch f at `c603adc2` for
  `yang_2024_teacher_wellbeing`).

### Housekeeping

- [ ] `irw_batch_updated.py` exposes no `--no-archive`, so `--retriage` on a
  re-mine archives `human_review` rows the rule forbids (#3073). Either add
  the flag or make `--ignore-seen-keys` imply it. Today's workaround was to
  call `irw_retriage_ha.py --no-archive` directly, and the 112 rows the first
  chain wrote are parked in
  `runs/human_review_archive_side_effect/` (gitignored) rather than deleted.
- [ ] `itemtext/sweep_instrument_rights.py` compiles `_code_re` (line 98) and
  never uses it; its item-code surface is an explicit stub. Harmless, but it
  reads as coverage that does not exist.

## From the #3077 zenodo re-mine leads, worked (2026-10-18d)

- [x] **32 tables (1,015,867 responses) + 13 item text tables uploaded and released 2026-10-18**
  (ben-domingue; `uploaded=2026-10-18` stamped). 14 of the 18 unworked leads shipped;
  see BATCH_LOG 2026-10-18d for the table list and the four that did not. NOTE: several
  of this batch's 13 item text tables were HELD before release under the 2026-10-15
  silence rule; `automated_finding/itemtext_hold_2026-10-18.csv` is the per-table
  record of which.
- [ ] **Issues-page entries at upload** (9 tables with a `public_note`): nguyen_2024_helia,
  nguyen_2024_eheals, nguyen_2024_sleep_hygiene, hung_2026_growth_mindset,
  markova_2025_gaais, markova_2025_mails (English-only wording for a non-English
  administration), karas_2022_cetscale_pl and valenciano_2022_paqc (IRW English
  translations), maharani_2025_ecommerce_uiux (English stems for an Indonesian
  administration plus IRW English option labels).
- [ ] **Covariate labels:** harvested 2026-10-18 at the data commit for
  premkumar_2020_schizotypy, hung_2026_grit_mindset, karas_2022_cetscale,
  valenciano_2022_paqc. Run `python3 metadata/covariate_labels/build.py` after the release
  and commit covariate_labels.csv.
- [x] **RULED 2026-10-29 (ben-domingue): SKIP `zenodo.20475015`.** The naming question is closed by closing the deposit. 860 respondents x 30 AIOAS items, clean, would have been one table -- but its Zenodo creators are literally "Anonymous, Anonymous" with no linked paper, so `authorname_year_construct` has no author to use and there is no citation to give. Ben was offered a repository-stub name (`zenodo_20475015_aioas`), `anonymous_2025_aioas` and an instrument-first name, and chose to skip. **This is a precedent, not a one-off: a deposit with no attributable author and no paper does not ship, however clean its data.** Original note below.

  **`zenodo.20475015` needs a naming ruling, not work.** 860 respondents x 30 AIOAS
  items, 1-5, clean, would be one table with `cov_study`. Deposit creators are
  "Anonymous, Anonymous" and no published paper exists, so there is no author name. Same
  question as the 2026-10-10 DVN/YB5PVO lead -- resolve both together.
- [ ] **Rulings wanted** (none blocks upload): see BATCH_LOG 2026-10-18d -- the
  white_2022 table names carrying question numbers instead of a construct; the rights
  register's code matchers missing seven blocked instruments in one batch; blank
  `option_text` on premkumar_2020_bpaq and hung_2026_growth_mindset; the excluded
  `PSQIC` column in hu_2026_psqi.
- [ ] **Widen `instrument_rights_register.csv`'s code matchers, or accept manual
  identification.** `^swls` misses `LS1`, `^s?wemwbs` misses `D1`, `^uwes` misses
  `VE1`/`DE7`/`AE12`, and the Grit and O-LIFE rows carry no matcher at all. All seven
  blocked instruments in this batch were caught by hand; only `^r?cesd[_ ]?[0-9]` fired.
- [ ] **The 30 `deferred` rows of `leads/repos_ledger_remine_2026-10-18_zenodo.csv` are
  still unopened** -- N is blank because the file has not been parsed yet, so the leads
  filter dropped them on the N test. They are the obvious next slice of this pool before
  the untouched 511 zenodo keys.
- [x] The 49 `todo` rows were re-checked against the corpus first: 20 already in the IRW,
  11 already closed, 18 genuinely unworked. Every future re-mine batch should run
  `check_shipped.py` over its own leads file before working it.

## From the #3077 zenodo_rest batch A (2026-10-18e)

- [x] **44 tables + 6 item text tables uploaded and released 2026-10-18** (ben-domingue;
  `uploaded=2026-10-18` stamped). 44 dictionary rows and 44 `codebook_at_ingest`
  rows went with them.
- [ ] **Rulings wanted** (none blocks the 44):
  - **zenodo.20550197** is a cross-sectional superset of the live
    `gonzalezros_2025_ostes` — 200 of that table's 201 distinct OSTES response vectors
    reappear in it. Supersede the live 202-respondent table, ship only the ~425 new
    respondents, or skip? Not shipped either way until this is answered.
  - **zenodo.20110159's HS block** (HS5/HS8/HS10/HS15) differs between the deposit's
    two files for 323-417 of the 512 shared respondents. Dropped for now; the four
    items are an adaptive-perfectionism discrepancy subscale, not the happiness scale
    the code suggests.
  - **Item text held on rights with the wording already in hand** — CCAS, OSTES, SWLS,
    UWES-S, Grit, De Jong Gierveld, EQ-i, APS-R Order, Subjective Happiness, and the
    unidentifiable 42-item social-support battery in zenodo.14200089. Each is
    extraction-solved, so a ruling ships them without re-reading a deposit.
- [ ] **Three deferred leads worth a follow-up pass**, all statused in
  `leads/repos_ledger_remine_2026-10-18_zenodo_rest.csv`:
  zenodo.15082823 (923 x ~145 items, full English stems in the headers — needs
  splitting into one table per bundled instrument, and item text is cheap once split);
  zenodo.14577475 (600 x ~140 labelled columns in Q-numbered blocks, needs the same);
  zenodo.11083220 (EMA, no obvious respondent id — the N>=100 floor turns on reading
  the linked paper, zenodo.10594764).
- [ ] **77 leads still `todo`** in the same file, for batch B onwards.
- [ ] **Covariate labels:** harvest run 2026-10-18 at HEAD for the 12 `.sav`-reading
  scripts (hartmann_2026_ai_climate, chukwu_2026_help_seeking, oner_2026_pe_motivation,
  lischer_2021_phq4, erdemir_2026_digital_burnout,
  diazgarcia_2018_emotional_disorders, auerswald_2024_online_learning,
  guerra_2010_teacher_resilience, sanchezmoreno_2024_ageing_loneliness,
  hung_2026b_learning_engagement, hung_2026_parental_warmth,
  hung_2026_short_form_video), all exit 0. Run `build.py` after the release and commit
  `covariate_labels.csv`.
- [ ] **Issues-page entries at publish:** `auerswald_2024_online_learning` — the
  deposit reverses the response anchors on two of its four items (0 = "does not apply"
  on Corona_1/3, 0 = "applies" on Corona_2/4) so that a high code always means a worse
  experience. The numeric scale is comparable across items but the wording attached to
  each code is not, which is a text-vs-table fact a reader needs.
- [ ] **A PII-scan lesson worth folding into whatever scans next:** scan VALUES with an
  email regex rather than header names, and treat pandas `StringDtype` ("str") as a
  string dtype. Both gaps let a column of 3,130 real email addresses
  (zenodo.10069489, `Nombredeusuario`) pass two scans before it was caught.

## From item 1 of #3077 — the ledger's unworked `good` keys (2026-10-18f)

- [x] **17 tables (213,442 responses) uploaded and released 2026-10-18** (ben-domingue). All 94 tables
  staged at that point (these 17 plus batch A's 77) passed
  `irw-validate --profile upload` with no failures. No item text accompanies them.
- [ ] **Covariate labels:** harvested at `c603adc2` for `yang_2024_teacher_wellbeing`
  (Chinese value labels for gender, teaching years, degree, academic title, salary
  band). Run `python3 metadata/covariate_labels/build.py` after the release and
  commit `covariate_labels.csv`.
- [ ] **One ruling wanted** (the other was answered 2026-10-19):
  - `10.17632/4fp3nxmcgs` — ANSWERED. Incidental under the structural/incidental
    narrowing (#3113): the free-text `school` column collects a school name, so
    the one self-typed personal name is nulled and the deposit ships. It is a
    workable lead now, tracked above; it has not been processed yet.
  - `10.5281/zenodo.21121992` — STILL OPEN. Its name column holds the three
    **deposit authors'** own names (the enumerator tag), published on the record,
    not data subjects'. The narrowing speaks to identifying respondents and does
    not reach an author's self-name, so this one still wants a ruling.
- [ ] **One deliberate item-text translation round** covers eight deposits in this
  batch whose stems are already in hand in their own column headers but were
  administered in Indonesian, Turkish or Chinese with no author English. Each would
  need a `translation_source` and a public issues-page callout, which is why none
  shipped here. Start with `10.5281/zenodo.20017889`: it deposits its questionnaire
  in **both** Chinese and English, so it needs no IRW translation at all — just PDF
  extraction and an alignment of 21 and 25 stems to the LSitem numbering.
- [ ] **Seven deferred deposits**, each with its reason in
  `leads/repos_ledger_goodkeys_2026-10-18_worked.csv`: zenodo.14903363, 21802067,
  18993680, 14768211, 15547217, 18373473, 18890328 (plus 21121992 above). The common
  shape is a Google Form export whose headers are full stems with no item code, so
  the code needs a documented derivation rule. Two are messier: 18373473 has banner
  text leaking into its data rows, and 14768211 has two sheets whose row counts
  differ by one.
- [ ] `zenodo.20734378`'s 10 climate-knowledge items are a **nominal-standard**
  candidate, not core: raw unordered MC option codes. Do not retry recovering the
  answer key from `awareness_score` — an exhaustive search over all 691,200
  single-correct-option keys finds none that reproduces it (BATCH_LOG 2026-10-18f).

## From the 2026-10-16 PMC monthly re-triage (2026-10-18, #3059)

- [ ] **Seven candidates want a human read** — listed in BATCH_LOG 2026-10-18 with
  `runs/pmc_monthly_retriage_2026-10-18.csv`. PMC13295900 (247 x 17) and PMC10991279
  (183 x 38, QC `dup_id_item`) are the two with counts already in hand.
- [ ] **Six OSF deposits are private (401), not retryable** — r3xfy, 87ew5, e2xsr,
  sm4cd, 6nt2s, 3s6ze. Each article says the data are openly available in OSF. Author
  emails wanted; the permission template is in `processing_notes/Licensing.txt`.
- [ ] Consider a distinct flag for "repository says 401/403" so a private deposit stops
  reading as a dead link in future runs.

## From the 2026-10-15 repos mode-3 batch (15 new terms x 9 languages)

- [x] **153 tables (1,571,458 responses) + 35 item text tables uploaded as drafts** by Claude on
  ben-domingue's instruction (2026-10-15; response tables to `item_response_warehouse_7`, item text
  to `irw_text_3`; `uploaded=2026-10-15` stamped). ben-domingue publishes the drafts. Table list in
  `runs/batch_tables_2026-10-15.txt`. All 77 leads carry a status; none unworked.
- [ ] **Issues-page entries at publish:** zhang_2025_parent_literacy_beliefs, zhang_2025_child_preliteracy.
- [ ] **Covariate labels:** `build.py` after the release and commit covariate_labels.csv (harvest run for
  the 18 .sav/.dta scripts).
- [ ] **Rulings wanted** (none blocks publishing): see BATCH_LOG 2026-10-15d.
- [ ] Seven OSF nodes with `unknown` licence sit outside the leads file pending a lookup via
  `api.osf.io/v2/licenses/` (named in BATCH_LOG 2026-10-15c).
- [x] The "arg must be a list, tuple, 1-d array, or Series" reader fault is **fixed**
  (2026-10-18, branch `fix/pmc-triage-dupcols-osf-retry`): not `load_table()` but
  `_alternative_reads`' `header=[0,1]` flattening, which gives every column the same
  label when row 1 is a banner spanning the sheet. See BATCH_LOG 2026-10-18. The 45
  rows it cost across the 2026-10-10/11/14/15 runs are re-triageable, but those run
  CSVs are not in the repo — only the PMC monthly 2026-10-16 rows were re-run.

## From the 2026-10-14 repos mode-3 batch (15 new terms x 9 languages)

- [x] **191 tables (1,607,513 responses) + 82 item text tables uploaded** (ben-domingue, confirmed
  2026-10-15; response tables to the new `item_response_warehouse_7`, item text to `irw_text_3`;
  `uploaded=2026-10-15` stamped on the 82 `itemtext_provenance.csv` rows). Table list in
  `runs/batch_tables_2026-10-14.txt`. The 40 + 36 openESM files parked in
  `runs/openesm_pending_2026-10-13/` are a separate stream, not uploaded by this batch.
- [ ] **Issues-page entries at upload:** 39 tables with public_note set, listed in BATCH_LOG 2026-10-14b.
- [ ] **Covariate labels:** `build.py` after the release and commit covariate_labels.csv (harvest run at
  db501a7c for the 25 .sav/.dta scripts).
- [ ] **Rulings wanted** (none blocks upload): see BATCH_LOG 2026-10-14b. ben-domingue ruled 2026-10-15
  that the 16 opaque-block tables (yao x6, li_2026_vocational x4, li_2026_efl_listening x6) ship as-is.
- [ ] `prasetiyo_2022_act` item text held at `itemtext/fixes/repos_2026-10-14_A/` (verify FAIL:
  nine reversed items). All 77 leads carry a status; none unworked.
- [ ] The "arg must be a list, tuple, 1-d array, or Series" reader fault hit 12 more `error` rows
  (36 across the 2026-10-10/11/14 runs); worth a look at `load_table()`.

## From the 2026-10-11 repos mode-3 batch (15 new terms x 9 languages)

- [x] **83 tables (2,006,984 responses) + 32 item text tables uploaded** (ben-domingue, confirmed 2026-10-11; `uploaded=2026-10-11` stamped) from
  `automated_finding/irw_output/` and `itemtext_output/` (response tables first). All 83 are new.
  The already-uploaded 2026-10-10 files were moved to `runs/uploaded_2026-10-10/`. Stamp
  `uploaded=` in `itemtext_provenance.csv` only after ben-domingue confirms.
- [ ] **Issues-page entries at upload:** esteves x2, bi x4, hou x4, izquierdo_lopez (IRW English
  translations), kassas_2021_covid_mitigation (blank `cleaning` stem), petrovici_2025_culture_appreciation
  (1/2 vs codebook 1/0).
- [ ] **Covariate labels:** `build.py` after the release and commit covariate_labels.csv (harvest run
  at commit for the 15 .sav/.dta scripts, see BATCH_LOG 2026-10-11d).
- [ ] **Rulings wanted** (none blocks upload): see BATCH_LOG 2026-10-11d.
- [ ] 1 unworked lead in `leads/repos_leads_2026-10-11.csv`: DVN/G7EOGT (Ciuk TESS 2002/2010, needs the TESS codebook).

## From the 2026-10-10 repos mode-3 batch (15 new terms x 9 languages)

- [x] **107 tables (2,042,413 responses) + 33 item text tables uploaded** (ben-domingue, confirmed 2026-10-11; `uploaded=2026-10-11` stamped) from
  `automated_finding/irw_output/` and `itemtext_output/` (response tables first). All 107 are new
  (the `perez_hernandez_2021_*` tables were written and extended within this batch; nothing is
  live yet). Stamp `uploaded=` in `itemtext_provenance.csv` only after ben-domingue confirms.
- [x] **Issues-page entries:** 25 entries in datapages/irw#342 (fox_2023_gad7 dropped as below the bar).
- [ ] **Covariate labels:** after commit run `python3 metadata/covariate_labels/harvest.py --commit HEAD`
  for meden_2026_podcast, kacovsky_2022_imi, jarbin_2020_mfq, spasovski_2020_perma,
  asadollahi_2022_fesi, perez_hernandez_2021_encovid, wendel_2022_rfq, stecula_2020_antivax,
  schoen_2007_neoffi, stapleton_2021_optimism, lee_2022_social_trust,
  deilkas_2019_saq_nursing_homes, van_beveren_2019_youth_emotion, cwalina_2023_covid_framing,
  deryahanoglu_2024_exercise_personality; then `build.py` after the release and commit
  covariate_labels.csv.
- [ ] **Rulings wanted** (none blocks upload): see BATCH_LOG 2026-10-10b (PLS-SEM small blocks as
  one table, stapleton CCAP/CCES as own data, schoen_2007, hatemi_2017 content, jarbin dx covariates,
  kahraman 19-item ZBI, montana_blasco unkeyed statements, lee_2022 treat collapse, blank option_text
  tables, YB5PVO anonymous deposit).
- [ ] 2 unworked leads in `leads/repos_leads_2026-10-10.csv`: DVN/YB5PVO (needs an author name),
  DVN/IZKSL7 (Swiss AV panel, heavy recoding).
- [ ] 11 `error` rows share one reader fault ("arg must be a list, tuple, 1-d array, or
  Series"); check `load_table()` before the next run or those candidates are retried blind.

## From the 2026-10-08 repos mode-3 discovery (15 new terms x 9 languages)

- Ruled 2026-10-09 (ben-domingue): the five decisions on the 2026-10-09 batch stand (karrot split, CAQ as one table, CYRM-12 item text held, AMTB item text shipped, bland/nguyen block-based constructs).
- [ ] **Covariate labels: harvested 2026-10-09** at 54cacc4b for 20 scripts (abu_tabar_2021_copd,
  blumel_2018_mrs, wang_2026_moral_models_psm, nicholson_crotty_2021_psm, favero_2020_covid_prosocial,
  mullinix_2015_political_knowledge, dey_2017_mistreatment_childbirth, sadish_2021_covid_beliefs,
  khan_2023_ethical_leadership, fischer_2018_promis29, wolbers_2017_oral_language, cuttler_2017_cannabis,
  galindo_2025_chatgpt_dependence, lin_2023_smartphone_addiction, wenzke_2025_carbon_offsetting,
  lei_2024_learning_motivation, chen_2026_entrepreneurship, salomon_2014_essentialism,
  arista_2010_achievement_motivation, vasquez_2013_reading_comprehension). Run
  `python3 metadata/covariate_labels/build.py` after the next pipeline run and commit covariate_labels.csv.
- Ruled 2026-10-09 (ben-domingue) on the 2026-10-09c batch: 5-digit ZIP + birth year is PII
  (RAPID DVN/QIEEJU, 1IWRQA stay skipped); birth month + year is not a birthdate (keep year or
  age only; RMUJNX still skipped, no codebook); the four data-noted tables, the conj routing and
  the purnama issues entries stand.
- Ruled 2026-10-09 (ben-domingue): third-party re-deposits (KLIPS DVN/RWPOMI, TEDS 2024-T
  DVN/QIGM1P) stay rejected; an uploader's CC0 cannot relicense a panel its institute distributes.
- [x] The Canada GSS 2010 files and `10.7910/dvn/crpaa8` added to the seen ledger as
  `file_too_large` by hand (2026-10-10).

## From the 2026-10-09 PLOS monthly run (full sweep, 125 terms x plosone)

- [x] **2 `good` + 1 `worth_retrying` worked (PR #2940, 2026-10-10):** `pone.0237626` ->
  `ding_2020_covid_knowledge` + `ding_2020_covid_risk_perception` (item text shipped);
  `pone.0356524` -> `panth_2026_bipq` + `panth_2026_cdrisc10` (the `dup_id_item` was one
  duplicated serial number). `pone.0200483` (Garden Cafés) rejected again: values 2-8 vs the
  paper's 1-7 scale, no codebook. See BATCH_LOG 2026-10-10.
- [ ] **15 `recoverable_format` leads** (one deposit, several bundled instruments —
  needs splitting into one table per scale) — see BATCH_LOG entry for the full list
  and DOIs.
- [x] **5 `human_review` rows** (includes one RETRACTED article, `pone.0297868` —
  confirm skip) — titles/DOIs/reasons listed in this batch's BATCH_LOG.md entry.
  The on-disk `human_review/human_review_plos_2026-10-09.csv` the run generated was
  never committed (pushing it fell outside this task's explicit scope and was
  declined by the permission layer) and was deleted rather than left stranded —
  safe to do because its dedup purpose is already served by `plos_seen_dois.csv`
  (all 5 DOIs are already in it, pushed to main) and its row detail is already in
  BATCH_LOG.md. If a human-readable `human_review/*.csv` copy is still wanted for
  this batch, it can be regenerated from the BATCH_LOG entry.
- Raw triage output (`runs/plos_monthly_candidates_full_2026-10-09.csv` and its
  `.retriage_ha.csv` sibling) is on disk in this session's container only — not
  committed anywhere (per `.gitignore`/SKILL.md; see BATCH_LOG). Every DOI above is
  reachable again from its URL, and all 121 triaged DOIs are now in
  `plos_seen_dois.csv` so a future run won't re-surface them by accident.

## From the 2026-10-07 repos mode-3 batch (15 new terms x 9 languages)

- [x] **168 tables (1,897,483 responses) + 37 item text tables uploaded** (ben-domingue,
  confirmed 2026-10-07; response tables to `item_response_warehouse_5`; item text
  `uploaded=2026-10-07` stamped).
- [x] **Issues-page entries:** 30 entries in datapages/irw#329 (24 IRW-written English,
  useche x2, takacs x4 English substitute for a Hungarian administration).
- [ ] **Covariate labels: harvested 2026-10-07** at 3935e416 for dassean_2025_bsmas,
  ali_2026_gses, fernandez_prados_2025_ai_attitudes, blaszyk_2023_ptps,
  kolanska_stronka_2026_climate_anxiety, kermen_2019_attentional_control,
  mclean_2022_perfectionism, islam_2021_covid_mental_health. `build.py` labels only
  tables in metadata.csv, so run `python3 metadata/covariate_labels/build.py` after the
  next pipeline run and commit covariate_labels.csv.
- [ ] **Rulings wanted (none blocks upload):**
  - PII calls that could be overruled:
    - Malay home-address column (zenodo 21318421/21126480)
    - name initials (3hvsgx2sbv)
    - self-generated initials + digits + month ids (DVN/WI6EWW)
  - galindo_2026: adolescents' free-text emotional disclosures were dropped and
    the deposit was not treated as PII. Confirm.
  - rexand_galais_2022_ipo: Study 1 sample 2 has odd distributions (bimodal; RT items
    pile at 1). It ships pooled.
  - crysdale_2020_big5 has 61 items where BFI-2 has 60; the extra one is unidentified.
  - hlado_2025 is named after the dataset contact (the record author is anonymised).
  - kasparek_2025_audit item text is held under the AUDIT rights question.
- [ ] **Cheap item text not built:** galindo_2026 (Spanish .sav labels), song_2026
  (Chinese .sav labels), blaszyk_2023 (Polish .sav labels). All need IRW English.
- [ ] **101 unworked leads** in `leads/repos_leads_2026-10-07.csv`. Two were worked and
  stalled on a missing codebook: zenodo 10535997 (floral sector, N=1272) and
  zenodo 18993680 (teacher AI readiness).
- [ ] **`dictionary_auto.csv` rows 1441-1443** (`fullscaleiq_*_options`, already on main)
  have 18 fields against a 16-column header; `pandas.read_csv` fails on the file.
  `stage_dict_row.py --force` appends instead of replacing.

## From the 2026-10-05/06 repos mode-3 batch (15 new terms x 9 languages)

- [x] **31 tables (122,477 responses) uploaded** (ben-domingue, confirmed 2026-10-06; no item text in this batch).
  `irw_output/`: sauerbronn_2025 x4, khan_2018 x6,
  yan_2023 x5, weber_2026_name_interaction, cordova_2026 x3,
  morales_2025_ehealth_much, atik_2025 x3, bado_2018_ohla_b, lane_2020_pss,
  heriyati_2026 x6. Dictionary/codebook/tags/provenance rows are staged.
- [ ] **`tang_2026_rmet_c` HELD** (ben-domingue, 2026-10-06): items keyed by raw
  column; the deposit's column-to-image tie does not reproduce its own 30-item
  file. Script kept (`data/tang_2026_rmet_c.py`, marked HELD), output moved to
  `runs/held/`, staged dictionary/codebook/tags/data-note rows removed. Ships only
  once the mapping is resolved.
- [ ] **Covariate labels for `khan_2018_*` after the release.** Harvested
  2026-10-06 at 38634ddd (the log is in ~/.cache/irw/covariate_labels/logs). `build.py` only
  labels tables that are in metadata.csv, so run `python3 metadata/covariate_labels/build.py`
  once the khan tables are live, then commit covariate_labels.csv.
- Ruled 2026-10-06: `heriyati_2026_*` ships (N=100, ceiling accepted).
- [ ] **106 unworked leads** are in `leads/repos_leads_2026-10-05.csv`, all with a
  licence-ok `worth_retrying`/`recoverable_format` status and in the N/item
  shape band. Notable ones:
  - SQJFVA / Zenodo 13859254/8 (9,775 x 66, health literacy and mental health)
  - FVEQHE (7,992 x 584)
  - ZLFLRT (5,818 x 444)
  - Social Reward Questionnaire-A (Zenodo 4944935, 568 x 60)
  - DASS-16 (Zenodo 19896978)
  - WM7IXF (authoritarian personality national surveys, 1,080 x 56)
  - Yoruba Oswestry (plos.figshare 11554833, 136 x 17)
  - DVN/U6YTI5 (good by triage)
- [x] SURF timeout: reachable again 2026-10-07 (240 hits that run).
- **Two licence-blocked rows added** (Borealis 10.7939/DVN/10732 and 10302). Email
  for permission if wanted.

## From the 2026-10-05 PMC sweep (last 208 backlog terms, PeerJ + Sci Rep only)

- [x] **18 tables (817,775 responses) + 10 item text tables uploaded** (ben-domingue, confirmed 2026-10-05; item text `uploaded=2026-10-05` stamped).
  `irw_output/`: wu_2022_dcep x6, lyu_2024 x9, sung_2026_marital_quality,
  elshafie_2020_edsc, scheerhagen_2019_reproq. `itemtext_output/`: lyu_2024 x9,
  elshafie_2020_edsc.
- [x] **Issues-page entry for `elshafie_2020_edsc`:** datapages/irw#319, merged.
- [x] **Covariate labels built 2026-10-05** after the release: elshafie_2020_edsc and
  scheerhagen_2019_reproq are in `covariate_labels.csv`. matsaid reads an xlsx, so it has no labels.
- [x] **4 matsaid_2022_abcdm tables (4,408 responses) uploaded** (ben-domingue, confirmed 2026-10-05).
- **The PMC term backlog is exhausted:** no scored term in
  `pmc_term_backlog_2026-09-25.csv` is left unrun. A further PMC pass needs a new
  term ranking.

## From the 2026-10-04 PMC scout-2 sweep (ranks 101-300 + owed pairs)

- [x] **46 tables (647,006 responses) + 25 item text tables uploaded** (ben-domingue, confirmed 2026-10-04; item text `uploaded=2026-10-04` stamped). Original:
  `irw_output/` (fong_2023 ×5, kanwal_2024 ×4, strojny_2026 ×4, przybylski_2016_igd,
  fang_2021 ×4, makovi_2021 ×3, usmani_2024 ×3, shen_2025 ×4, clemente_2024 ×4,
  li_2026_psmus, kramer_2023 ×2, yamagishi_2016_pd, yuan_2024 ×3, mohamed_2021 ×2,
  rzeszutek_2023 ×5).
  Then upload `itemtext_output/` (25 `__items.csv`). Response tables go up first.
  Dictionary, tag, codebook and data-note rows are staged. Stamp `uploaded=` in
  `itemtext_provenance.csv` and `itemtext/mapping_verification.csv` only after
  ben confirms.

- [ ] **Issues-page entries owed in datapages/irw once live**. The text is drafted
  in each `public_note` of `itemtext_provenance.csv`:
  - IRW-written translations: `strojny_2026_gmi`, `clemente_2024_sd4`,
    `clemente_2024_pmd`.
  - English substitutes for a Chinese administration: `fang_2021_{pbc,pn,peb}`,
    `shen_2025_{dass21,bsmas,sabas}`, `yuan_2024_{ucla,contact,trust}`,
    `li_2026_psmus`.
  - Label mismatch on item 9: `clemente_2024_attitude_{father,mother}`.
  - Truncated stem CSRN3: `kanwal_2024_csr`.

- [x] **Covariate labels built 2026-10-05:** shen_2025, clemente_2024 and yuan_2024
  are in `covariate_labels.csv`. strojny_2026 and usmani_2024 ship text-label
  covariates, so they have no codes to label.


## From the 2026-10-02 human_review re-check batch 4 (25 rows, 14 shipped)

- [x] **69 tables + 9 item text tables uploaded** (ben-domingue, confirmed
  2026-10-02). `alqerem_2025_gina_control` failed once in `red_up`
  (AttributeError inside the upload call, no partial table left) and went up
  on a single-file re-run, row count verified.
- [ ] **Licence call (Ben):** HRQoL/musculoskeletal pain in health-science
  students (`10.5281/zenodo.7782495`): Zenodo API says CC BY 4.0, the deposit
  readme says CC BY-NC-ND. Treated as blocked (in
  `license_blocked_candidates.csv`); if the repository licence governs, CSI-25
  + NMQ x 338 ship.
- [ ] **Open questions on batch-4 tables (none blocks upload):**
  - `mellat_2022_*` (15 tables): instruments named only in the paywalled
    paper; identities from composite labels, no permitted sets, a few stray
    codes kept as stored. Hold until the paper is read?
  - `gonzalezros_2025_eqi`: paper says 30 items 1-4; file has 51 items 1-5.
    Shipped with no permitted set.
  - `mairean_2024_panas` / `_das`: two administrations shipped as wave 1-2;
    what separates them is undocumented.
  - `cao_2024_mbi`: file 1-5, the author's (different-sample) paper says 1-7.
    No permitted set.
  - `alqerem_2025_anq`: scored from raw answers by the key; the deposit's own
    scored column disagrees in 30/1,600 cells.
  - `olajubu_2024_srh_hlq`: 40 of 44 items (HLQ41-44 are column copies in the
    deposit).
- [ ] **Papers behind paywalls/bot walls, if Ben can supply them:** Mellat et
  al. 2023 (10.1080/19349637.2022.2121239; names all 15 instruments); Macovei &
  Mairean 2025 (10.1177/13591053251341191; PANAS/DAS administrations, HSCM
  format); Al-Qerem et al. 2025 J Asthma (10.1080/02770903.2025.2519100);
  Luttenberger et al. 2022 BJCP (10.1111/bjc.12347; FERUS items, timepoints).
- [ ] **Item text leads from batch 4 (not built):** olajubu HLQ (full English
  stems + value labels; waits on the HLQ rights call); thiessen BFI-10/SCS/SAS/
  CSIA (English stems + anchors; no register rows); ahmed PCL-5/coping (English
  labels, administered language undocumented); gonzalezros (Spanish stems; EQ-i
  is a block, TMMS-24/TSES unregistered); alqerem PedsQL/MARS-5 (Arabic +
  English at both levels, licensed instruments); luttenberger SPHQ (German
  PHQ-9 stems, one mislabelled).
- [ ] **Next step of the re-check, when wanted:** batch 5, the next 25 of the
  remaining shape-qualified `resp_scale_mixed` rows in pool (b) (about 121
  left after batch 4's 25 picks and 18 skips; skip list in
  `leads/human_review_recheck_batch4_2026-10-02.csv`). At most two agents at
  a time.

## From the 2026-10-02 human_review re-check batch 3 (25 rows, 19 shipped)

- [x] **64 tables + 5 item text tables uploaded** (ben-domingue, confirmed
  2026-10-02): the batch-3 `irw_output/` set, then the 5 `__items.csv`
  (gopal_2021_cas, garciabacete_2023_victimization, suyato_2023_cbq,
  wu_2015_cias, wu_2015_bsrs5). `uploaded` stamped in `itemtext_provenance.csv`
  and `mapping_verification.csv`.
- [ ] **Open questions on batch-3 tables (none blocks upload):**
  - `wu_2015_mpi_*`: stored codes 0<1<2 shipped against the file's own value
    labels (0=?, 1=Yes, 2=No); the file's Nscore/SDSscore sums, the paper's
    direction and standard MPI scoring (No/?/Yes) all agree. Hold?
  - `suyato_2023_democracy`: codebook codes -1..2, but the printed
    questionnaire has 5 options. Hold?
  - `wisniewski_2021_nihss`: `rater` is the assessment slot (1-3), not a
    stable person (the file doesn't record who).
- [ ] **The CBQ paper (10.26418/jppkn.v6i1.92523) is bot-walled** and not
  confirmed to use these data; only worth a PDF if Ben wants it cited.
- [ ] **Rights calls before cheap item text can ship:** CAS (Lee 2020; gopal
  item text is built and shipping — add a register row); MQOL-E / QOLLTI-F
  (sawatzky: full English stems in the variable labels); CERQ (domaradzka:
  English labels, Polish administered -> translated_substitute).
- [ ] **Item text leads from batch 3 (not built):** mendezlopez_2023 full
  Spanish stems + value labels (PHQ-9/GAD-7/RSES are rights `ship`; needs
  English for `_translated` or language-only shipping); CBF-PI-15 S3.docx
  (15 of 40 cbfpi_b items, paper_explicit); CSTI 71-item pool in the paper's
  S4 File (paper_order); bekteshi ERI bilingual stems in the deposit docx
  (positional); PL-NIHSS in the paper's S1 Table; talayero flood (3 tables):
  English variable labels as a translated_substitute (the paper has no
  Spanish either), same class as wu_2015_cias.
## From the 2026-10-02 human_review re-check batch 2 (25 rows, 21 shipped)

- [ ] **62 tables + 5 item text tables need uploading**, from the worktree
  `/home/ben/irw-wt/hr-recheck-batch2/automated_finding/`: all of
  `irw_output/` (62 tables), then `itemtext_output/` (5 `__items.csv`:
  garciabacete_2023_loneliness, mendezhinojosa_2026_ebea,
  turpochaparro_2026_{procrastination,workload,teacher_self_efficacy}).
  Dictionary/tag rows are staged; `uploaded` is unstamped in
  `itemtext_provenance.csv` and `mapping_verification.csv`.
- [ ] **Open questions on batch-2 tables (none blocks upload):**
  - `kalani_2026_uwes`: coding undocumented (UWES8 sits about a point below
    the other eight; published UWES is 0-6). Shipped as stored, no permitted
    set. Hold it?
  - `delacruzvaldiviano_2024_djgls`: `cov_sex`/`cov_residence` are unlabelled
    1/2 codes. Keep or drop?
  - `garciabacete_2023_loneliness` / `sun_2018_greed`: `rights_register`
    matches the codes to DJG / LBUS; both look like false positives
    (Cassidy & Asher; positional G1-G7).
  - `neivasantos_2026_*`: no paper, so what separates wave 1 from wave 2 is
    undocumented.
  - `summart_2025_whoqol_bref`: q14 and q25 are identical in every row, so
    both were dropped.
- [ ] **Papers behind bot walls, if Ben can supply them:** Sahin 2026 IJHCI
  (10.1080/10447318.2026.2719186; sahin_2026_* have no permitted sets until
  read), Stripp 2023 J Relig Health (10.1007/s10943-022-01533-5), Sandoz 2022
  Psychol Trauma (10.1037/tra0001068). The greed paper was supplied and read.
- [ ] **Item text leads from batch 2 (not built):** DGSC G1-G7 printed in
  Liu 2019 Table 1 (paper_explicit, needs verify); bertani_2024_afccq English
  variable labels (Italian administered; AFCCQ-IT in the paper's supplement);
  sandoz_2021_cbts/pcl5/epds French stems in the deposit codebook;
  tabordabarata_2024_hls_eu_q47/bsi and neivasantos_2026_bes/oeq full
  Portuguese labels at both levels (no English source); delacruzvaldiviano
  Spanish stems in the deposit's results docx.
## From the 2026-10-02 human_review re-check batch 1 (9 pilot datasets)

- [x] **22 tables + 1 item text table uploaded** (ben-domingue, confirmed
  2026-10-02): the batch-1 `irw_output/` set, then
  `alqerem_2024_mhls__items.csv` (to text_3). GAS naming (`usc_2026_*`) kept;
  the MTS 1-5 range confirmed from the paper.

## From the 2026-09-29 JPSP 131(4) batch (Lu 2026 + Zhang 2026)

- [x] **25 tables + 6 item text tables uploaded** (ben-domingue, confirmed 2026-09-29). Original:: `irw_output/lu_2026_*`
  (8) and `irw_output/zhang_2026_{mcq,moral,bfi2,courage,tcs,hexaco,wisdom,ipip,
  virtue,episode}*` (17), then `itemtext_output/zhang_2026_ipip_*`,
  `_virtue_states`, `_episode_affect` (6). Dictionary/tag rows are already staged.
- [ ] **Item text rights rulings, if wanted**: the wording for 19 tables is in
  the deposits, but the instruments are not in `instrument_rights_register.csv`
  (Spielberger Trait-Anger, FSS-II, Mood Survey, Adult Hope Scale, Weinstein
  1980 events, MCQ, Moral Attentiveness, courage/TCS/wisdom items). STAI,
  BFI-2 and HEXACO are already `block`.

## From the 2026-10-19f deferred-residue slice (#3103)

- [ ] **Mendeley 6bhr52dc5v's 20-item S* block** — 1,198 English students at
  two waves, and the coding is not consistent: the deposit's value labels
  define four categories (0 Never .. 3 Almost Always), wave 1 holds 1-4, wave
  2 holds 0-4, and 184 of 1,093 respondents use both 0 and 4 within the same
  twenty items. Two tables (or one with `wave`) once someone establishes what
  each wave's coding is; the paper may say. The deposit's other four blocks
  shipped as `putwain_2022_*`.
- [ ] **A register `block` does not stop response data, and the group-2
  write-ups assumed it did.** Several #3103 rows carry a note like "UWES_1-24
  must be DROPPED (register block)" or "the EQ is a register BLOCK row and
  must be dropped". That is wrong as a rule: `irw_validate/rights.py` says
  response data from a blocked instrument ships and only its wording cannot,
  and the 2026-10-18 ERQ withdrawal removed item-text rows, not response
  tables. Worth re-reading those rows before working them — at least
  5tjkv36r3s (EQ), vptj28s8pk (UWES) and tnkv5z3byg (UWES) have items that
  were going to be dropped for no reason.

## From the 2026-10-19d tail slice (#3077)

- [ ] **DANS SS/PVQ66Y's Adaptive Expertise Inventory** — BC1 (4 columns),
  BC2 (4) and BC3 (3), each at two waves, are item responses, but the
  deposit's Databeschrijving.pdf describes that instrument as two domains of
  five items, and prints its response options with a duplicated "1." so the
  number of points is ambiguous too. Three tables once the domain mapping is
  known; the nine D-ADAPT and Adaptability tables shipped.
- [ ] **DANS Z7Q-7ATH's EDE-Q block** — 28 columns in each of two studies,
  mixing 0-6 band ratings with raw day counts (247 and 288 cells above 6, up
  to 15 and beyond). The deposit ships a codebook PDF; splitting the block by
  item metric needs it read item by item. The other six blocks shipped.
- [ ] **Add institutional figshare instances to `_HOST_RESOLVERS`** —
  `orda.shef.ac.uk` (Sheffield ORDA) is a figshare instance, and the
  DOI-fallback path sent it to `_dataverse_files`, which raised its AWS-WAF
  `SourceBlocked` message naming **dataverse.harvard.edu** for a site it never
  called. Two fixes, both small: dispatch `*.figshare.com` and known
  institutional instances to `_figshare_files` (the public figshare API
  resolves ORDA ids fine), and make that WAF message name the host it
  actually requested.
- [ ] **A deposit can keep both copies of a reverse-scored item, and name the
  ADMINISTERED one `*R`** — Mendeley x8zvbjv6p2 has `Differ3R` inside its
  block and plain `Differ3` later as the scored copy (= 6 - R twin for all
  1,387 rows). Taking the plain name because it looks unmodified ships
  reverse-scored items among administered ones. Worth a line in the data
  standard's "one file per scale" section: identify the administered copy by
  position in the block and by arithmetic, not by the name.
## From the 2026-10-19c noflag_dataverse slice (#3077)

- [ ] **DVN/EEPE1L** — 275 students x 15 items at 1-7 in five clean 3-item
  blocks, codes `TSI`, `ACP`, `TTF`, `CSI`, `PSE`. Deferred only because the
  blocks cannot be named: no SPSS labels, no codebook, and a search for the
  paper ("Understanding the Roles of Grit and Generative AI Alignment in
  Academic Performance", Oh 2026) found nothing. Five tables the moment a
  construct list turns up; only `TTF` (task-technology fit) is guessable, and
  guessing five of five is not acceptable.
- [ ] **DVN/IGFCET** — 2,415 PhD graduates with four 1-5 job-attribute
  importance ratings (autonomy, pay, managerial activities, commercialization)
  whose shared stem the deposit never states (a .dta plus one .do file, no
  questionnaire). One four-item table if the paper confirms the stem.
- [ ] **DVN/226PMX's other blocks** — DE05/DE06/DE07/DE08 (36 columns at 1-7),
  PL05 (10 at 1-5), PL06 (8) and TE06 (8) are item responses, and the
  deposit's questionnaire PDF names its blocks, but the counts do not line up:
  one "DE5 Conceptions of democracy" entry listing 21 statements against four
  data blocks totalling 36; 8 data columns against 7 listed statements, twice;
  and PL05 is not in the PDF's overview at all. Needs the German original or
  the paper's appendix to resolve which column is which. The three blocks
  whose counts DID match are shipped.
- [ ] **Count the category marginals before shipping a large block** — a
  method item, not a dataset. DVN/D6WWCK was rejected because 138 of its 140
  items have all five Likert categories within 140-180 of the 159.8 expected
  under exact uniformity, with within-block r of 0.83-0.89 and every
  cross-block pair at 0.33-0.40: a simulated file, not a questionnaire.
  Nothing in `run_qc` looks at marginals — `imputed_values*` fires on
  CONCENTRATION, so a perfectly flat item is precisely what it cannot flag.
  Worth considering as a check in `irw_validate` or in the triage.
- [ ] **The PII screen cannot see a free-typed numeric field** — DVN/VSFCVG
  (853 students, 9 AI-in-mathematics items at 1-5, Spanish stems as headers)
  was skipped whole because one respondent typed an email address into the
  free-text `Edad` (age) column. `screen_for_pii` content-checks only
  generically-named columns, so `Edad` was never read and the deposit screened
  clean. Either content-check every string column or treat any free-text
  demographic field as a screening surface.

## From the 2026-09-28 repos weekly batch

- [x] **DVN/GJOBOS** — CLOSED 2026-10-19c: the deposit is an IPUMS/NHGIS
  census microdata build (county and individual census variables, IPEDS
  records, a county gazetteer). No item responses in any of its 57 files, so
  there was no column mapping to confirm. `rejected_content`.
- [ ] **figshare 10.6084/m9.figshare.33980614** (Activities of Daily Living
  Inventory (ADLI), French older adults) — `download_failed` (proxy/connection
  error reaching `ndownloader.figshare.com`). Retryable; left out of
  `repo_triage_seen_keys.csv` so a later run picks it up automatically. No
  action needed unless it keeps failing.

## From the 2026-09-21 repos weekly batch

- [ ] **DVN/QQ369L** (Vietnam 2026 National Assembly Election voter survey,
  cc0) — `human_assistance`, unclassified by this routine. No column met the
  id heuristic; row position was used as a fallback person id. Needs a human
  to confirm one row per respondent before it's trusted.
- [x] **DVN/OHBD3D** — CLOSED 2026-10-19c on PII, before the
  continuous-`resp` question was reached: Study1_Baseline_Demographics.sav
  carries `IPAddress`, and Study3.sav carries `RecipientFirstName`,
  `RecipientLastName` and email addresses in Q85. Whole candidate skipped
  under `feedback_pii_skip_entirely`.
- [ ] **Dryad 10.5061/dryad.hx3ffbgvs** (gaming motivation among college
  students) — `download_failed` (401 Unauthorized). Retryable; left out of
  `repo_triage_seen_keys.csv` so a later run picks it up automatically. No
  action needed unless it keeps failing.

## From the 2026-09-20 recycled-term PMC sweep

- [x] **25 actionable leads triaged into `pmc_leads_2026-09-20.csv`**
  (tracked). 4 shipped, 1 blocked on licence, 1 skipped on PII, 1 rejected on
  content, 18 unworked -- the unworked ones are the open item further up this
  file. Superseded as a task; kept for the counts. Original: 1 `good` + 12
  `recoverable_format` + 12 `worth_retrying`. Rank by
  instrument shape before response count — several of the largest are
  Scientific Reports rows that may be trial-level or single-item panels.
  See BATCH_LOG.md 2026-09-20 for the four largest by shape.

- [x] **`10.3390/bs15020224` licence verified CC BY 4.0** (Crossref + Europe
  PMC core), and so are the other 33 `unknown` rows — the `unknown` was a
  connector defect, now fixed. See BATCH_LOG.md 2026-09-20b. All 25
  actionable leads are CC BY; no licence question is outstanding.

- [ ] **Re-check past PMC rows ledgered under the old licence bug.**
  `pmc_seen_dois.csv` predates the `license_lookup_failed` fix, so some
  already-retired DOIs will say `license_unknown*` where the record says
  CC BY. Cheap: the same 34-row re-check loop, pointed at the ledger.

## From the 2026-09-24 PMC sweep (batch 5)

- [x] **8 tables (95,438 responses) uploaded** (ben-domingue, confirmed 2026-09-24). Original: `irw_output/depue_2023_cfq`,
  `_gds15`, `_pwi`, `_subjcog`, `_hads_a`, `_cerq`, `depue_2021_lsns6`, `_brs`.
  No item text this batch (`itemtext_output/` is empty). Dictionary and tag rows
  are staged in `dictionary_auto.csv` / `tags/tags_auto.csv`.

- [ ] **Decision if wanted: CENSOPAS-COPSOQ (`10.1186/s12889-022-13328-0`)** held on
  trust per the Chen 2023 ruling -- 67 exact-duplicate rows plus a 137-row
  near-duplicate network in rows 600-1000 of a 1,707 x 69 file (BATCH_LOG
  2026-09-24). A script that drops the exact copies (1,640 ids) is parked,
  unmerged, on branch `ben-domingue/held-copsoq`; say the word if this one
  should ship trimmed.

- [x] **`pmc_term_backlog.csv` exhausted** (2026-09-24): the last 41 terms ran,
  20 candidates, 2 leads, nothing shipped. See BATCH_LOG 2026-09-24 final sweep.

## From the 2026-09-23 PMC sweep (batch 4)

- [x] **4 tables (42,116 responses) uploaded** (ben-domingue, confirmed 2026-09-24). Original:: `irw_output/`
  `rogowska_2023_maia2`, `kabir_2023_snaq`, `kabir_2023_bms10`, `kabir_2023_sidas`.
  No item text this batch (`itemtext_output/` is empty). Dictionary and tag rows are
  staged in `dictionary_auto.csv` / `tags/tags_auto.csv`.

- [x] **`rogowska_2023_maia2__items.csv` uploaded** (ben-domingue, confirmed 2026-09-24; `uploaded=2026-09-24` stamped). Original: (`red_up itemtext_output`;
  the response table is already live). Shipped partial: anchors withheld on items
  5-12 and 15. Stamp `uploaded=` in `itemtext_provenance.csv` and
  `itemtext/mapping_verification.csv` only after ben confirms.

- [x] **Issues-page entry for `rogowska_2023_maia2` in datapages/irw#241** (2026-09-24). Original: once live: the
  `public_note` in `itemtext_provenance.csv` (9 reverse-keyed items carry no
  option labels because their stored direction is unconfirmed).

- [ ] **Decision if wanted: Al Mamun 2023 green skincare (`10.1016/j.heliyon.2023.e16765`)**
  rejected for fill-down corruption in 4 of 10 blocks; the other 6 (ECT/ECP/ECD/ECE
  1-5, SCPI/WPPP 1-7, N=778) check out against the deposit's composites. Left out
  per the Chen 2023 ruling unless ben-domingue says otherwise.

## From the 2026-09-23 PMC sweep (batch 3)

- [x] **8 tables (32,469 responses) + 8 item text tables uploaded** (ben-domingue,
  confirmed 2026-09-23; `uploaded=2026-09-23` stamped). Original:
  `irw_output/`: `sison_2022_hiv_testing_stigma`, `sison_2022_provider_mistrust`,
  `zhang_2024_smoking_rationalisation`, `zhang_2024_ftcd`, `che_mood_2024_pvhs`,
  `abdulkader_mohamed_2022_exer_knowledge`, `_exer_attitude`, `_exergame_exp`;
  the same 8 as `itemtext_output/*__items.csv`. Response tables first. Dictionary
  and tag rows are staged in `dictionary_auto.csv` / `tags/tags_auto.csv`. Stamp
  `uploaded=` in `itemtext_provenance.csv` and `itemtext/mapping_verification.csv`
  only after ben confirms. Also in `irw_output/`: the three `ge_2021_*` tables
  from #2384 (57,061 responses) -- upload them with this batch unless they
  already went up; they have no item text (see BATCH_LOG 2026-09-23).

- [x] **Issues-page entries added in datapages/irw#239** (2026-09-23; Sison
  kept: the paper says questions were in English AND Tagalog, Tagalog unpublished). Original: once live
  (`public_note` is set in `itemtext_provenance.csv`): `zhang_2024_smoking_rationalisation`,
  `zhang_2024_ftcd` (English substitute, Chinese administration), and
  `sison_2022_hiv_testing_stigma`, `sison_2022_provider_mistrust` (English/Tagalog
  offered, English only published) -- for Sison, check first whether the form was
  side-by-side bilingual ("Yes/ Oo"), in which case blank the public_note instead.

- [x] **Chen 2023 left out** (ben-domingue, 2026-09-23: "if there is a problem
  let's leave it out"). Stays `rejected_content` in `pmc_leads_2026-09-23.csv`. Original: **`10.1016/j.heliyon.2023.e15742` (Chen 2023, work
  design).** Rejected because the final 50 of 804 rows duplicate earlier
  respondents (5 with altered demographics) and the paper counts them. Rows
  0-753 are clean and ready if you want the prefix shipped. See BATCH_LOG
  2026-09-23.

- [ ] **91 scouted terms remain ranked and unrun** in `pmc_term_backlog.csv`
  (`run_2026_09_23b` marks batch 4's 50; projected yield is down to 5 new DOIs
  per term or fewer). A fifth batch starts from that file.

## From the 2026-09-22 PMC sweep (batch 2)

- [x] **7 tables + 3 item text tables uploaded** (ben-domingue, confirmed
  2026-09-22): 27,195 responses. The three shipped item text tables are stamped
  `uploaded=2026-09-22` in both `itemtext_provenance.csv` and
  `itemtext/mapping_verification.csv`; the four not-shipped provenance records
  stay unstamped. Dictionary and tag rows reach the sheet via
  `metadata/02_biblio.R` and `03_tags.R` on the next pipeline run. Original: Beyond the Pilch four below: `bate_2019_srq` (8,300),
  `kaigaishi_2024_primate_cognition` (6,356), `maes_2020_ospaq` (1,537) --
  27,195 responses in total across the batch. All 7 dictionary rows and 7 tag
  rows are staged. Item text ships for three of the Pilch tables only.

- [x] **The Pilch four** (peerj.11263, Pilch 2021) -- uploaded with the batch:
  `pilch_2021_fcv19s_validation` (2,275), `pilch_2021_ipip20_validation` (6,220),
  `pilch_2021_preventive_behavior` (1,532), `pilch_2021_preventive_vas` (975) --
  11,002 responses. Item text ships for all but `fcv19s_validation`. Response
  tables first (`red_up irw_output`), then `red_up itemtext_output`. Dictionary
  and tag rows are already staged; stamp `uploaded=` in
  `itemtext_provenance.csv` and `itemtext/mapping_verification.csv` only after
  ben confirms.

- [x] **FCV-19S rights call -- cleared, item text shipped** (2026-09-23).
  The hold was wrong on the standing rule: a missing register row is silence,
  and silence does not block. Better than silence, Ahorsu et al. 2020 print
  all seven items in the Appendix of their own CC BY 4.0 article
  (PMC7100496), so the rights holders published it openly. Register row
  `FCV-19S` added (verdict `ship`); it also covers, after the fact, the five
  FCV-19S item text tables that were already live (`fcv19s_hossain_2022_fear`,
  `fcv19s_hossain_2022__fear`, `kfcovid_fear_li2020`,
  `odachi_2022_fear_covid19`, `pilch_2021_fear_covid19`) -- the old note here
  saying the sibling was "in the same position" was wrong, it was published.
  `pilch_2021_fcv19s_validation__items` (35 rows) is in the `irw_text_2`
  draft, COUNT(*) 35 / 7 items / 5 resp verified; release is Ben's. Mapping
  VERIFIED against Table 1 (28/28 values, `verify_pilch_2021_fcv19s_validation.R`).

- [ ] **Lead, not worked: the live `pilch_2021_fear_covid19` item text may not
  be the administered wording.** It carries the paper's Table 1 Polish; the
  deposit's Materials sheet -- the questionnaire for both samples, and the
  source the new table ships -- differs on items 5-7, and it also prints all
  five Polish anchors, which that table's public note says "are not
  published". Same sample 1 respondents. Logged, not swept
  (retroactive audits paused); fixing it is a replace in `irw_text_2` plus a
  rewrite of its issues-page entry.

- [x] **Issues-page entry for `pilch_2021_fcv19s_validation`** (items 5-7
  differ from Table 1) -- added in datapages/irw#227.

- [x] **All 14 leads worked, batch closed** (2026-09-22): 4 shipped, 4
  blocked on licence, 5 rejected on content, 1 skipped on PII. Every row of
  `pmc_leads_2026-09-22.csv` carries a terminal status and a reason. Superseded
  as a task; kept for the counts. Original text follows.

- [ ] **`dup_id_item` disagrees with the upload gate on `trial_*` keys.**
  `run_qc`'s check decides fail-vs-note from `("wave", "timepoint", "date")`
  alone (`irw_validate/_checks.py` ~line 404), so it hard-fails a table keyed by
  `trial_number` -- which `datastandard.md` says is exactly what distinguishes
  repeated responses, and which the same module's own `occasion_columns()`
  already counts for the rescue path. The upload profile passes such a table;
  `compat.run_qc` fails it. Reproducible on a 4-column synthetic frame. Wants
  its own change with tests rather than a drive-by patch.

- [x] **9 actionable leads unworked**, all in the tracked
  `pmc_leads_2026-09-22.csv`. Ranked by instrument shape, not response count.
  Largest by shape: `10.7717/peerj.6672` (4,485x21),
  `10.1038/s41598-024-77912-7` (3,024x31), `10.7717/peerj.15826` (328x30).
  `10.7717/peerj.11263` is done -- shipped 2026-09-22. Most `recoverable_format` rows are
  `resp_scale_mixed` -- re-read by block prefix, one file per scale.

- [x] **The `unknown` licences are correct, not a defect** (checked
  2026-09-22). They arrive via Data Availability links, so the *deposit's*
  licence governs, not the article's: `osf.io/s4kwv` and `osf.io/zkwna` are
  public with no licence set, `osf.io/zjnsb` 404s without a token. All three
  are now in `license_blocked_candidates.csv`. Do not "fix" this by falling
  back to the article licence -- that is the laundering the source-licence
  rule forbids.

- [x] **Manual connectors now chain Step 2b** (fixed 2026-09-22). Both
  `irw_discover_pmc.py` and `irw_discover_plos.py` call
  `chain_step2b(args.out, run=True)` at end of `main()`, the same call the
  `_monthly` wrappers make; `chain_step2b`'s docstring records why the manual
  path was missed. `irw_discover_monthly.py` deliberately does not chain it --
  it is discovery-only, emits no `flag` column, and its candidates reach Step
  2b via `irw_batch_updated --retriage`.

- [x] **191 scouted terms remain ranked and unrun** -- batch 3 swept the next
  50 on 2026-09-23; superseded by the 141-term item in the batch 3 section.

- [x] **241 scouted terms ranked and unrun** -- batch 2 swept the top 50 on
  2026-09-22; superseded by the 191-term item above. The scout's 500-hit
  cross-journal cap is still unfixed, so treat its counts as a ranking only,
  never a volume estimate (see BATCH_LOG.md 2026-09-20).

## From the 2026-09-20 lead-working pass

- [x] **18 tables / 269,737 responses + 1 item text table uploaded**
  (ben-domingue, confirmed 2026-09-20). All 18 `irw_output/` CSVs went to the
  newest warehouse shard and
  `amiot_2022_ucla_loneliness__items.csv` to **`irw_text_2`**, not `irw_text`
  -- item text is sharded the same way the warehouse is, and `red_up` picks
  the newest shard itself, so that is expected rather than a misroute (the
  corpus already splits UCLA tables across both shards). The
  `itemtext_provenance.csv` row is stamped `uploaded=2026-09-20`. Biblio needs
  no action: the 18 `dictionary_auto.csv` rows are on main and
  `metadata/02_biblio.R` unions them on its next run.

- [ ] **`amiot_2022_ucla_loneliness` owes an issues-page entry -- it is now
  live.**
  Its `public_note` is non-empty, which forces a public callout: 418 of the
  2,424 respondents (17.2%) answered in French and the deposit carries only
  the English wording, so the shipped item text is not what those respondents
  read. The page lives in the datapages/irw repo
  (`irw_site/itemtext_issues.qmd`) and is edited there, not here.

- [x] **Prolific IDs: replaced, not disqualifying** (ben-domingue,
  2026-09-20). A platform participant ID is a pure identifier, so it is
  swapped for the row index -- never a hash, which is a re-linkable
  pseudonym -- and the candidate ships. All other PII still skips the whole
  candidate. Recorded in the skill's PII section and BATCH_LOG.md 2026-09-20d.
  The candidate that prompted it, `10.1038/s41598-023-33749-0`, still did not
  ship: its data sits on a PRIVATE, unlicensed OSF node reachable only
  through the review link the paper publishes, so it is a licence skip and is
  logged in `license_blocked_candidates.csv`. No author email, per
  ben-domingue.

- [x] **UCLA Loneliness Scale: verdict is `ship`** (2026-09-20). The quote
  test found nothing to quote -- Fetzer's own UCLA pages reproduce the scale
  with no permission, copyright or distribution statement, unlike the DSES
  copy in the same collection, and SPARQtools publishes all 20 items with no
  terms. Registered in `itemtext/instrument_rights_register.csv`.
  `amiot_2022_ucla_loneliness__items.csv` is extracted and gated (80 rows,
  `data_labels`); both tatala tables are unparked below.

- [ ] **`li_2025_icf_rs17` item text is one table away.** The 17 ICF category
  names are printed in the paper's Tables 3-4 (`paper_explicit`, so it needs
  a Step 5b `verify_li_2025_icf_rs17.R`, not the cheap gate). The item codes
  are ICF codes, so the mapping is unambiguous -- this is the most tractable
  itemtext follow-up the batch produced.

- [x] **`lopezodar_2025` ERQ stays held, no author query** (ben-domingue,
  2026-09-20: not worth one at this stage). The paper documents the Peruvian
  ERQ as 7-point; the deposited ERQ1-ERQ10 hold five levels (0-4) across all
  403 respondents, so the responses cannot be mapped to the documented
  anchors. The reason is recorded in `data/lopezodar_2025_berq.py` and the
  dictionary Notes, which is the durable part. 4,030 responses if anyone
  reopens it.

- [ ] **18 of the sweep's 25 leads are unworked**, now in the tracked
  `pmc_leads_2026-09-20.csv` (was only in a gitignored `runs/` CSV -- see
  BATCH_LOG.md 2026-09-20e). Every row carries `status`, the flag, n, items,
  the data file and the external link, so a lead can be opened without
  re-running anything. Rank by instrument shape, not response count: the two
  largest by nominal count (21,343 x 23 and 20,415 x 12, both `.RDS` behind
  OSF links) are social-network and VR-trial data and were deliberately left
  for last.

## From the 2026-09-20 PLOS recycled-term sweep

- [ ] **Permissions outreach is now a tracked programme: irw#2331.** The four
  rights calls and the author-query items scattered through this file are
  folded into it -- Class A (instrument wording, 72 blocked register rows),
  Class B (data licensing, the 28 standing `license_blocked_candidates.csv`
  rows + 17 OSF rows + ANES follow-up), Class C (data clarification: Roy,
  Enders, Sanchez, zenodo.16310936, the two anonymous-author deposits),
  Class D (the zenodo.10069489 PII disclosure, which should not queue behind
  the rest). Templates and the standing `outreach_log.csv` are in
  `processing_notes/outreach/`. Next concrete step is the by-hand triage of the
  72 block/escalate rows into commercial / controlled / academic, then
  `sweep_instrument_rights.py` for a tables-gated count to rank by.

- [ ] **The second PSS-4 administration in `enders_2022_*` is unexplained.**
  The Qualtrics export carries the PSS-4 block twice; the copies genuinely
  disagree (44-83% of rows per item, item-wise correlations
  +0.64/-0.54/-0.58/+0.75), so it is two real administrations rather than a
  duplicated upload. Nothing in the README, `Analyses.do` or the article says
  what the second one is, so only the first shipped. If it is a retest it is a
  free second `wave` on 2,054 respondents. Worth one author email.

- [ ] **Rights call needed on two instruments before their item text can ship
  (Ben).** Neff's Self-Compassion Scale and Judge et al.'s Core Self-Evaluations
  Scale have no entry in `itemtext/instrument_rights_register.csv`, and
  `coroiu_2018_scs` / `coroiu_2018_cses` are now live candidates. Note this is
  moot until the German wording is obtained anyway -- the deposit's labels are
  English glosses -- so it is not blocking the response tables.

- [x] **21 tables + 1 item text table uploaded** (ben-domingue, confirmed
  2026-09-20): `simo_sanz_2018_spai` (76,908), `bentall_2021_over_purchasing`
  (27,594), three `coroiu_2018_*` (114,775) and sixteen `enders_2022_*`
  (213,468) -- 432,745 responses. `bentall_2021_over_purchasing__items.csv`
  went up with them and is stamped `uploaded=2026-09-20` in both
  `itemtext_provenance.csv` and `itemtext/mapping_verification.csv`. The other
  20 provenance rows are not-shipped records and stay unstamped. The 21
  `dictionary_auto.csv` rows reach the sheet via `metadata/02_biblio.R` on the
  next pipeline run.

- [x] **Tags staged for all 35 tables of this batch** (2026-09-20). This was
  missed on both the 21-table and 14-table handoffs -- the dictionary rows went
  in and the tag rows did not -- and was caught only when ben asked. 35
  `claude-auto` rows in `tags/tags_auto.csv`, filling the four columns that
  currently publish per `tags/scoring/results_comparison_2026-09-03.txt`
  (`primary language(s)`, `item format`, `measurement tool`, and the SETTING
  facet of `sample`); the held columns are left blank. `Rscript
  tests/test_tags_union.R` passes. Recruitment channel was read from each
  paper's Methods rather than guessed: Qualtrics panels for `bentall`/`enders`
  (`Internet-based`), health-insurance + chronic-condition recruitment for
  `nolte` (`Clinical`), students for `li`/`graves`/`roy` (`Educational`), and
  blank for `simo_sanz` and `coroiu_2018_*` -- the latter was face-to-face
  interviewing in participants' homes by a survey institute, which no SETTING
  atom names.

- [ ] **14 tables need uploading** (a second batch, after the 21 already up):
  nine `nolte_2017_hlq_*` (45,338), `li_2026_sas_sv` (18,420),
  `graves_2021_pss10` + `graves_2021_brief_cope` (38,011), `roy_2024_phq9` +
  `roy_2024_sas_sv` (19,361) -- 121,130 responses. All 14 dictionary rows are
  staged in `dictionary_auto.csv`. No item text ships with this batch, so
  `irw_output/` alone goes up and no provenance row gets stamped.

- [ ] **HLQ item text is one rights call away from being free (Ben).** The
  Nolte deposit carries all 44 HLQ items in the administered German wording in
  its SPSS variable labels, plus both anchor sets in German -- the cheap case,
  and it would satisfy the administered-language columns with no translation
  step. The HLQ is licensed by Deakin University and has no entry in
  `itemtext/instrument_rights_register.csv`. This is the highest-value item
  text blocked on rights in this batch; the SCS/CSES call below is worth less
  because that deposit's labels are English glosses anyway.

- [ ] **Two author queries worth sending from the Roy deposit**
  (`10.1371/journal.pone.0315687`): its PSS-4 block cannot be reconciled with
  the score the paper analysed (see BATCH_LOG.md 2026-09-20 cont. 4), and its
  ISI block is entirely empty in the deposit. Both would be recoverable data.

- [ ] **29 of the 38 open-licensed leads still unworked** (cc-by/cc0, N>=100) out of the
  98-row `human_assistance` bucket — 44 `recoverable_format` + 14
  `worth_retrying` before the license and N gates. The full ranked list is in
  `BATCH_LOG.md` (2026-09-20), because `runs/` is gitignored. Worked so far: `pone.0205389` and
  `pone.0246339` shipped, `pone.0167571` rejected as aggregate-only (see
  BATCH_LOG.md). `pone.0190771` (3 tables) and `pone.0276082` (16 tables) also shipped.
  Also worked: `pone.0172340` (9 tables), `pone.0349016` (1),
  `pone.0255634` (2), `pone.0315687` (2). Next unworked by size:
  `pone.0256686` (CAPE-P15, 1,594 x 72) and `pone.0284383` -- for both, the
  triage row's SI file index is wrong (`s001` is a TIFF figure and a PDF
  respectively), so enumerate `extract_si_files()` before downloading --
  then `pone.0323124` (parental rejection / cyberbullying, 1,567 x 82). Most are RULE 10b
  `resp_scale_mixed`, i.e. one questionnaire carrying several instruments —
  re-read by block prefix and ship one file per scale.

- [ ] **24 `aggregate_continuous` rows need a composite-vs-continuous call.**
  Not yet adjudicated; some will be genuine per-item continuous responses and
  some will be subscale totals. All 24 are listed in `BATCH_LOG.md`
  (2026-09-20 cont. 3), so this no longer depends on anything in `runs/`.

## From the 2026-09-19 PMC tail measurement

- [x] **The unaudited PMC seen-DOI tail is closed, measured not skipped.**
  2,809 ledger DOIs had no recorded verdict; a seeded 100-row probe found 3
  naming a repository against #2203's 17%, 35% licence-blocked, and 44 of 47
  statements saying "available from the author on request". ~21 hours of
  network for a projected 10 leads. See BATCH_LOG.md 2026-09-19. Reopen only
  if the connector changes — `pmc_tail_probe.py` re-runs the measurement.

- [ ] **One live lead from the probe: `10.1038/s41598-026-57813-7`**
  (Scientific Reports), whose Data Availability statement names OSF `s2hfg`.
  Triaged `human_assistance` — worth a look when a PMC batch is next worked.
  Cheap: the deposit is already resolved, nothing needs re-discovering.
## From the 2026-09-16 PMC batch (written up 2026-09-19)

- [x] **9 item text tables uploaded** to `irw_text` (ben-domingue, confirmed
  2026-09-19) and stamped `uploaded=2026-09-19` on the nine
  `itemtext_provenance.csv` rows and the nine
  `itemtext/mapping_verification.csv` rows. They sit on the draft until the
  next version release, so `check_issues_page.R` reads their page entries as
  orphans; that is acknowledged in `itemtext/fixes/issues_page_orphans_ack.csv`
  and resolves on release.

- [x] **Four issues-page entries applied 2026-09-19** to
  `irw_site/itemtext_issues.qmd` (868 entries now), for the four of the nine
  carrying a non-empty `public_note`:
  - `codella_2020_school_efficacy` — "Item text is the study's administered
    Italian wording, but the 1-5 scale anchors and the shared stem 'How well
    can you' are recorded in English: the source publishes those two only in
    English."
  - `qi_2024_phq9`, `qi_2024_mspss` — "The item text is the study's own
    English-language codebook; the questionnaire was administered in Chinese,
    so this is not the wording respondents read."
  - `qi_2024_somatic` — the same, plus "The source instrument has 20 items and
    this IRW table carries 15."

- [ ] **`qi_2024_somatic` is missing 5 of the instrument's 20 items, and they
  are recoverable.** The deposit's SSS block has 20 columns; five carry stray
  PHQ/GAD names and were excluded when the table was built. They are the
  missing SSS items — `SSS Total score` equals sum(SSS1..SSS15) + those five
  for 293/293 respondents and equals the 15-item sum for none. What is not
  settled is which of `SSS16`..`SSS20` each stray column is: they are
  interleaved among the labelled ones (positions 2, 3, 4, 6, 8 of the block),
  so column order does not identify them, and the item texts (sweating and
  trembling; worry about illness; breathing and sighing; throat blockage;
  urinary frequency) would have to be matched some other way. Adding them
  means reshipping the table, so it is a decision, not a fix.

- [ ] **`fitz_2024_numeracy` item 2 disagrees with the published proportion
  correct.** Table SM2 reports 0.64 for the BIG BUCKS item; the shipped table
  gives 0.514, and the other ten items match the supplement to ±0.01. The
  scoring applies the authors' own replication `.do` key exactly, so this is
  the released key disagreeing with the published table, not a processing
  error. Counting the 304 respondents who answered "100" as correct reproduces
  ~0.62. Worth an author email if anything is done about it at all.

- [ ] **`aziz_2020_bmq` item text is held pending a rights call (Ben).** All 18
  BMQ items are in hand — the deposit's Questionnaire S1 prints the survey in
  Malay and English under CC BY — but no clause reserving a right could be
  quoted from the originator; what is findable says only that the copyright is
  Rob Horne's and that the questionnaire is obtained from him. Escalated per
  SKILL.md rather than decided either way; the register row is `escalate`.

## From the 2026-09-14 repos weekly batch

- [x] **DR-NTU 10.21979/N9/P5WUGI** — taken on Ben's NC approval
  (2026-09-15): six `nguyen_2026_factcheck_*` tables, PR #2186, uploaded to
  the Redivis draft, not released.

- [x] **UK Data Service ReShare 858431 (The Great Friendship Project)** —
  skipped: 56 respondents, below datastandard.md's flat 100-id floor.

- [ ] **Science Data Bank 10.57760/sciencedb.0103e** (personality,
  resilience, social support in Chinese college students) — `no_usable_file`
  unverified because the file API needs a login; check the landing page by
  hand.

- [ ] **All 14 `HIGH_YIELD_TERMS` still owe an OSF pass** — OSF timed out on
  every query this run (`api.osf.io` read timeouts, not per-term false
  positives). Watermarks did not advance, so the next weekly/monthly repos
  run re-covers them automatically; no action needed unless OSF is still
  down next time. See BATCH_LOG.md 2026-09-14.

## From the 2026-09-08 PLOS weekly batch

- [ ] **Sánchez 2020 (`10.1371/journal.pone.0236940`) is held on one
  question: what do the `PS*` codes 0/1/2 mean?** Structurally the strongest
  candidate in the batch -- 1,662 unique student ids, 17 Blood-module
  multiple-choice items, two cohorts, and a `QPS*` block that is constant per
  column (`EXCELENTE`/`BUENA`/`POBRE`) and so is a clean `itemcov_`. The
  article talks about "incorrectly or blank answers", which makes
  `0 = blank, 1 = incorrect, 2 = correct` the likely reading -- and if that is
  right, `0` is a non-response inside the valid range and must be filtered,
  not scored. The alternative (`0` incorrect / `1` partial / `2` correct)
  makes dropping the zeros wrong. It decides the meaning of 1,174 responses.
  The deposit's only other supplementary file is the rebuttal letter, so
  there is no codebook: this needs an author email
  (`processing_notes/Licensing.txt` has the template shape). See BATCH_LOG.md
  2026-09-08b.

- [x] **Tatala 2023 item text: ALREADY RULED, no call needed** (noticed
  2026-09-20). `instrument_rights_register.csv` carries "Religious Experience
  Scale (RES, 17 items), Tatala et al." as `verdict=ship`, and the UCLA
  Loneliness Scale as `ship` too. Both tables can be extracted whenever an
  itemtext pass picks them up; this was queued as an open question for
  ben-domingue in error.

## From the 2026-09-02 monthly repos sweep

- [ ] **Score the 2026-10-02 repos monthly run against its prediction.** The
  routine (`trig_01NT4fqYRrf7nRemLN3fAZm4`) fires 21:06 UTC 2026-10-02 with a
  rewritten prompt and opens `automated/repos-monthly-2026-10-02`. Prediction,
  written before it ran: **0 `good` from triage; 0-3 tables shipped once its
  leads are worked by hand, best guess 1.** Basis: the 09-02 monthly triaged
  150 of 1,998 with 0 `good`, and the four weekly runs (09-07 to 09-28) had 0
  `good` each, with one deposit (`nguyen_2026_factcheck`) found by hand among
  `no_usable_file` rows. A 12-term local start found 246 raw candidates, so
  expect ~1,500-2,000, of which the 150-row triage cap sees a fraction.
  Decision thresholds: >=5 tables -> it earns its cost, consider raising the
  cap; 1-4 -> keep, but the yield is in hand-worked leads; 0 -> third straight
  empty repo-mode result, evidence for thinning it in favour of PMC/PLOS-style
  sweeps (the two late-September PMC scout sweeps shipped 59 tables).

- [ ] **`automated/repos-monthly-2026-09-02` is waiting for review, and only
  150 of its 1,998 candidates were triaged -- none `good`.** The scheduled
  run hit a container restart, 88 of 125 terms came back with a false "0
  candidates" when the outbound proxy went down, and `9a11fbb` reran those 88
  honestly. The candidates (1,998, no `scholars_portal` -- 403 in that
  environment) and a 150-row triage landed on the branch; `de97257` put 97
  dedup keys on `main`. The triage's flag mix is worth a look before working
  it: 67 `no_usable_file`, 53 `download_failed` (transient, deliberately not
  ledgered, so a rerun retries them), 19 `human_assistance`, 5 `below_min_n`,
  3 `not_item_response`, 3 `license_restricted`, **0 `good`**. Whether the
  other ~1,850 candidates were prefiltered out or the triage was simply cut
  short by the same outage is the first thing to establish.

- [ ] **The watermark reached `main` hours before the candidates reached a
  branch.** `9a11fbb` pushed the 88 `search_terms_log.csv` rows -- which
  advance those terms' `--since` to 2026-09-02 -- at 23:49 UTC; the candidate
  CSV was not committed anywhere until `7201016` at 00:21, and it lives in
  `runs/`, which is gitignored precisely so scheduled runs stop committing per-
  run CSVs. Had the container died in that half hour, all 88 terms would have
  been permanently marked searched with 1,998 candidates recorded nowhere. It
  did not, so no harm this time -- but this is the identical shape to the open
  PLOS item below, now on a second routine, and the fix is the same: either
  the ledger append moves to a post-merge step, or both commits go on the
  branch together.

## From the 2026-09-01 PLOS weekly batch

- [ ] **9 item text tables still need uploading** to `irw_text` — `red_up
  <dir>` takes `irw_text` as its default for a directory of `*__items.csv`. The response side is done: ben-domingue moved the 21
  `irw_output/` tables for upload and imported the 21
  `biblio_2026-09-01.csv` rows into the dictionary (both confirmed
  2026-09-01, and both files are off disk as expected). Item text goes second
  because a `__items.csv` referencing a table that isn't live yet is a dangling
  reference. Once it lands, stamp `uploaded=<date>` on the 9 new
  `itemtext_provenance.csv` rows -- they are blank until then.

- [ ] **The weekly PLOS routine writes its seen-DOI ledger to `main` before its
  candidates are reviewed.** The 2026-09-01 run pushed `de13a15` (58 DOIs into
  `plos_seen_dois.csv` + a `search_terms_log.csv` row) straight onto `main` as
  a fast-forward, while the candidate CSV went to a branch and waited in
  `#1783`. Merged this time, so no harm -- but had the PR been closed unmerged,
  all 58 DOIs would have stayed permanently marked seen with the 11 actionable
  rows recorded nowhere, which is the same permanent-false-negative shape as
  the old openpyxl bug. Either both commits should go on the branch, or the
  ledger append should move to a post-merge step.

- [x] **`resp_scale_mixed` + `multi_scale` no longer sends multi-instrument
  questionnaires to `human_review`** (done 2026-09-01). 7 of the 9
  `human_assistance` rows this week landed in `human_review` with "no clear
  automated classification"; 5 were simply questionnaires carrying several
  instruments on different response scales, which `datastandard.md` already
  answers with "one file per scale", and all 5 became shipped tables. Added as
  RULE 10b in `irw_retriage_ha.py`: `resp_scale_mixed` with
  `n_participants >= 100` now routes to `recoverable_format` -- the file is
  fine, the automatic single melt is what needs redoing -- with a note to
  re-read by block prefix and check each block's range against the paper rather
  than the pooled min/max. Re-run on this week's rows: 6 `recoverable_format`,
  1 `worth_retrying`, 2 `human_review`, which is exactly the hand adjudication.
  No change on `pmc_monthly_candidates_weekly_2026-08-26.csv`. Also fixed a
  `ZeroDivisionError` in the summary when a run has no `human_assistance` rows
  at all (hit on `plos_monthly_candidates_weekly_2026-08-25.csv`).

## From the 2026-08-29 batch

- [x] **44 tables / 281,705 responses uploaded, biblio imported, and 21 item
  text tables uploaded** (confirmed 2026-08-29, ben-domingue). The four CC BY
  4.0 Zenodo deposits -- `soderberg_2024_*` (8), `estevez_2021_*` (8),
  `chen_2024_*` (16), `torok_2025_*` (12) -- are in
  `item_response_warehouse_4`, the 44 `biblio_2026-08-29b.csv` rows are in the
  dictionary, and the 20 new `__items.csv` plus the previously orphaned
  `altman_2020_capq` are in `irw_text:07b6`. All 21 rows of
  `itemtext_provenance.csv` are stamped `uploaded=2026-08-29`. `irw_output/`,
  `itemtext_output/` and the biblio CSV are off disk as expected. No
  `itemtext_issues.qmd` entry was needed for any of the 20 -- checked per-item,
  not just at table level: no observed response lacks an option row, no blank
  or duplicated item_text.

- [x] **`altman_2020_capq__items.csv` orphan cleared** (2026-08-29). It went up
  with this batch's item text and is stamped in `itemtext_provenance.csv`.
  The lesson stands for next time: an `__items.csv` left in `itemtext_output/`
  after its response table ships has no CSV to gate against and ERRORs every
  `audit_batch.R --resp-dir` run until it is uploaded -- ship item text in the
  same pass as its response table, or it strands.

- [ ] **ANES 2016 feeling thermometers — permission requested 2026-08-29.**
  `doi:10.7910/DVN/OHRGWV` (Brensinger & Sotoudeh, *ASR*, "Party, Race, and
  Neutrality") is a Harvard Dataverse replication package labelled CC0 whose
  only data file is the ANES 2016 Time Series (`anes_timeseries_2016_Stata13.tab`,
  4,270 respondents, 1,842 variables) — downloadable with one unauthenticated
  curl, no registration. The CC0 label is the depositors', who could only
  license their own R code, so the governing terms are ANES's, which gate
  access behind registration. **ben-domingue emailed anes@electionstudies.org
  2026-08-29 requesting permission — awaiting response.** Draft at
  `irw_site/.claude/worktrees/response-style-vignette-edits/scouting/outreach/05_anes_2016_permission.md`;
  it closes the question left UNRESOLVED in `02_anes_2012_note.md` in the same
  directory. If granted: post-election group/institution thermometers
  V162095-V162113 plus CASI racial-group V162310-V162314, with pre-election
  V161086-V161096 as a second `wave`; continuous 0-100 with ~3,600 valid per
  item, sentinels -9/998/999 dropped. Ask also covers whether the answer
  extends to other public-use Time Series waves.

- [ ] **145 SRDA + 33 openICPSR records are mislabelled `dataverse` and fail
  forever.** All 180 `resolve_error:FileListUnreachable` rows of the 2026-08-29
  non-Latin prefilter are this: `10.6141` resolves to `srda.sinica.edu.tw`
  (Taiwan's Survey Research Data Archive, Academia Sinica) and `10.3886` to
  openICPSR, neither of which is a Dataverse. The DataCite sweep labels them
  `dataverse`, so `_dataverse_files()` derives the installation from the
  landing host, finds no Dataverse API, and returns FileListUnreachable --
  the third instance of "a real failure wearing a nothing-here label" in this
  log. Two separate things to decide: (a) the resolver should verify the
  derived host actually serves a Dataverse API and return a terminal
  `wrong_repository` rather than a retryable error; (b) whether SRDA is worth
  a connector at all -- it is Taiwan's national survey archive (Taiwan Social
  Change Survey, TEPS) and surfaced only because we searched in Chinese, but
  access is likely registration-gated, which would make it license-blocked.
  Check the access terms before building anything. Rows are in
  `runs/prefilter_nonlatin_2026-08-29.csv`.

  **Partly handled 2026-08-31:** both prefixes are now dropped at discovery
  via `_UNREACHABLE_DOI_PREFIXES` in `irw_discover_updated.py`, so they no
  longer consume triage slots. This was prompted by the 2026-08-31 weekly
  repos run, where 49 of the 60 triaged candidates (82%) were `10.3886` and
  every one came back `no_usable_file` -- a verdict about the connector, not
  the datasets, now permanently in `repo_triage_seen_keys.csv`. Still open:
  (a) the resolver fix, which matters for any *other* non-Dataverse host the
  DataCite sweep mislabels, and (b) the SRDA connector decision. Reversing the
  drop is a one-line edit and the candidates return, since nothing filtered at
  discovery reaches the seen-keys ledger.

- [ ] **`--limit` silently discards the untriaged remainder of a run, and the
  scheduled routines lose them for good.** `run_batch()` in
  `irw_batch_updated.py` does `rows = rows[:limit]` after the seen-key filter,
  and `discover()` neither scores nor sorts -- so the triaged subset is just
  whichever search terms happened to come first, not the best candidates. The
  remainder exists only in the run's `runs/*.csv`, which is gitignored and, on
  a cloud routine, on a machine that goes away. The weekly repos routine uses a
  rolling `--since` window (2026-08-31 ran `--since 2026-08-24`), so next
  week's `--since 2026-08-31` will never re-surface them. Measured on
  2026-08-31: 182 candidates found, 60 triaged, **122 dropped without a
  record** -- and that is a normal week, not an outlier. Three ways out, cheapest
  first: (1) the `_UNREACHABLE_DOI_PREFIXES` drop above frees most of the
  budget on its own and may make this moot -- re-measure on the next weekly run
  before building anything; (2) raise `--limit` in the routine; (3) append the
  untriaged remainder to a tracked backlog CSV, the way
  `plos_deferred_candidates.csv` already works, and have the next run read it
  before the fresh candidates. Do not do (3) until (1) has been measured.

- [x] **Non-Latin-script re-run CLOSED** (2026-08-29/30). 955 terms -> 1,871
  hits -> 690 unique deposits -> 112 keeps -> 38 tier A+B leads -> 27 triaged
  -> **0 good**, 3 worth_retrying, 12 human_review. See `BATCH_LOG.md`
  (2026-08-29c) for the full accounting and the three findings. The surface is
  not a second Zenodo backlog; size any Spanish/German/French/Dutch follow-up
  against this result rather than against the 2026-07-15 English re-discovery.

- [ ] **3 `worth_retrying` leads from the non-Latin sweep, unworked.**
  `mendeley 4xtjnbwjt8` (人工智能与抑郁水平, 10,671 x 456 -- much the largest
  thing the sweep found, flagged only for duplicate (id,item) keys consistent
  with repeated measures), `zenodo.6844831` (supervisor-subordinate dyads,
  249 x 52, only issue is a low-confidence id column), and `zenodo.19912968`,
  which is already deferred above on its "Anonymous, Anonymous" author field.
  Rows in `runs/retriage_nonlatin_2026-08-29.csv`.

- [ ] **The seen-keys ledger records no verdict, so a fixed connector never
  un-blocks what it buried.** `repo_triage_seen_keys.csv` is `key,date` only.
  11 of the 38 non-Latin leads were skipped as already-seen, including the five
  highest-scoring in the batch; five of those were seen before the 2026-08-27
  connector fixes and four are `10.34894/*` (DataverseNL, triaged while the
  Dataverse resolver could only reach Harvard). Two separable things: release
  and re-triage those five keys (the 2026-08-28 Zenodo release is the
  precedent, backup + released-list in `runs/`), and decide whether the ledger
  should carry a verdict and connector epoch. Neither done -- both mutate a
  standing record. **Deliberately not escalated to #1702**: item 16 of that
  write-up says acquisition is not the Year 3 constraint. 955 terms, all default repo
  sources, chunked into `runs/candidates_nonlatin_NN_2026-08-29.csv`
  (~4.7h, log at `runs/discover_nonlatin_2026-08-29.log`). When it finishes:
  concatenate the chunks, prefilter with `prefilter_candidates.py`, rank with
  `rank_leads.py`, triage tier A+B. Early rate is ~4.6 candidates/term against
  **Results**: 1,871 hits -> 690 unique deposits (63% duplicate rate across
  translated terms, so the real yield is 0.72 unique deposits/term, not the
  ~4.6 candidates/term the running log suggested). Prefilter: 112 keeps, 363
  no_tabular_file, 35 license_unclear, 180 resolve errors (see above). Ranked
  to 38 tier A+B leads in `runs/leads_nonlatin_2026-08-29.csv`; triage running
  to `runs/triage_nonlatin_2026-08-29.csv`. The 955 terms are logged.
  Note the Spanish/German/French/Dutch terms hit the same English-only gate and
  are a further pool on top of these 955.

- [ ] **`api.figshare.com/v2/articles/search` returns 422 on some queries**
  in the non-Latin run. Distinct from the known 403-under-concurrency issue
  below; may be the non-Latin payload. Not diagnosed.

- [ ] **Teach `screen_for_pii()` the Wenjuanxing column names.** Raw 问卷星
  exports carry `来自IP` (IP address annotated to city) and `提交答卷时间`
  by default, exactly the way raw Google Forms exports carry a name column.
  `zenodo.17947681` triaged clean and was caught only by eye. The existing
  `name|email|phone|address|birth` pattern is ASCII-only.

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

- [x] **THE BIG ONE: full Zenodo backlog sweep -- DONE** (2026-08-28/29).
  2,458 terms, zenodo only, 4h44m, exit 0. 6,081 candidates -> 4,485
  genuinely new -> 1,563 open-licensed keeps -> 451 tier A+B triaged ->
  **110 shippable leads, 8,356,581 responses**. The 140-term sample projected
  ~800 new deposits and 15 leads; the real numbers were 5.6x and 7.3x that.
  See `BATCH_LOG.md` for the full table and the two size-term costs.

- [x] **24 tables / 689,621 responses uploaded and in biblio** (confirmed
  2026-08-29, ben-domingue), 7 deposits, all CC BY 4.0, all creates not
  replaces. The `irw_output/` CSVs are off disk as expected and the
  `biblio_zenodo_backlog_2026-08-29.csv` rows are in the dictionary. Lint was
  clean (0 errors, 0 warnings) and the scale encodings were verified before
  upload: `resp=0` is a labelled anchor in `osorio_2023_dos` ("Nada cierto",
  with refusals on a separate non-numeric code) and a real level in
  `baekgaard_2023_*` (no user-missing declared, the authors' own composites
  average over it, smooth unimodal distribution); `resp=5` is the top
  substantive anchor in all nine `skarzauskiene_2026_*` tables, with the 9
  "don't know" sentinel dropped. See `BATCH_LOG.md` for per-deposit coding
  decisions.

- [ ] **~95 of the 110 backlog leads still unworked.** Worked so far: the
  largest 7 shippable deposits, plus 4 more on 2026-08-29 (Soderberg, Estevez,
  Chen, Torok -- 44 tables / 281,705 responses) and 3 rejected the same day
  (`zenodo.15710961` not item data, `zenodo.17947681` PII, `zenodo.19912968`
  anonymous author). The remaining tail is in `runs/leadwork_2026-08-29.csv`
  (rank-ordered by response count) alongside
  `runs/triage_zenodo_backlog_2026-08-28.csv` and
  `runs/retriage_zenodo_backlog_2026-08-28.csv`. Next unworked by size:
  `zenodo.17109143` (Mehrotra, rural India gender-discrimination lab games --
  check whether it is trials or an instrument), then the long 20k-50k tail.

- [ ] **The sweep's headline total was inflated by a third.** The top lead
  (2,776,192 responses) turned out to be a firm-year accounting panel, not
  item response data, and three of the next four largest were rejected for PII
  or imputed values. Realistic remaining yield is well under the 8.36M
  figure -- `n_responses` from triage counts columns, not instruments, so
  leads should be opened before being counted.

- [ ] **Two emails worth sending.** (a) `zenodo.10069489` publishes 3,130 real
  personal email addresses in a public CC BY deposit -- the depositors should
  be told regardless of whether IRW ever uses it. (b) `zenodo.16310936` has an
  excellent two-wave instrument battery that is unusable only because the
  posted values are partially imputed; the raw file would be worth ~590k
  responses.

- [x] **In-memory size guard added** (2026-08-29). `FORMAT_MAX_BYTES` /
  `format_ceiling()` in `irw_batch_updated.py` put a tighter, per-format
  ceiling on top of `MAX_FILE_BYTES`: `.rdata`/`.rda`/`.rds` are capped at
  25MB, since pyreadr materialises the whole gzipped object and the 79.7MB
  `.RData` that SIGKILLed the backlog triage sat comfortably inside the 200MB
  download cap. Checked against the API-reported size before downloading, and
  against the received bytes when the API reports none. Verified end to end on
  10.5281/zenodo.7070556, the deposit that caused the kill: it now returns
  `file_too_large` without downloading, and normal candidates are unaffected.
  Because that verdict is sticky, capped candidates are also appended to
  `oversized_candidates.csv` so they stay recoverable by hand.

- [x] **`irw_process_queue.py` no longer crashes on import** (2026-08-29). It
  imported `QUEUE_SHEET_URL`, removed from `irw_discover_updated` when the
  queue sheet was deprecated, so the module raised ImportError -- an error
  that read like a missing dependency rather than "this stage no longer
  exists". The URL is defined locally so the module imports, and `main()` now
  exits 2 with an explanation pointing at the current flow. The stale
  "add candidates to the queue sheet, then run irw_process_queue.py" footer
  printed after every triage run is replaced with the real next step.

- [ ] **98 prefilter `resolve_error:FileListUnreachable` rows worth a retry.**
  Transient failures from the backlog sweep, deliberately excluded from the
  keeps rather than retired, in
  `runs/prefilter_zenodo_backlog_2026-08-28.csv`. Plus 8 `download_failed`
  triage rows kept out of the seen-keys ledger for the same reason.

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

- [x] **Lead ranker now sees dataset size** (2026-08-29, `cf4f307`). The
  premise needed correcting first: `resolve_data_files()` returned sizes only
  for files it SKIPPED as oversized, so every resolver computed each file's
  size for the `MAX_FILE_BYTES` check and then discarded it. It now returns
  `(url, name, size_bytes)` triples. The per-batch rank/prefilter scripts in
  `runs/` had drifted apart and were folded into reusable `rank_leads.py` and
  `prefilter_candidates.py`; the size term moves `tu_2022` from 7 (tier B) to
  10 (tier A) -- its `data.sav` is 6,095,027 bytes against 18k-41k for the
  tier-A deposits ranked above it. On the backlog sweep it moved 307 rows up
  and 5 down, 46 of them from tier B into tier A.

  Two costs, both on record in `BATCH_LOG.md`: it also promotes large
  non-instrument deposits (a 196MB Fitbit set, a 132MB ENCODE RNA-seq set
  reached tier B -- `T_NEG` blocks "sequencing" but not "RNA-seq"), and it
  promotes exactly the deposits that OOM triage, which is what forced the
  `FORMAT_MAX_BYTES` guard above.

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

- [x] **Open a separate issue for `DOI (for paper)` column hygiene.** Opened as
  **#1690**. The mechanical half is done: `doi_hygiene.py` normalises the wrappers
  (resolver URLs, `data doi: ` prefixes, journal `.sNNN` supplement suffixes) and
  `stage_dict_row.py` applies it on write, so no new automated row can carry those
  forms. `dictionary_doi_corrections.csv` is the paste list for the 83 cells
  already in the sheet.

- [x] **#1690's open half: the 979 rows holding a data DOI.** Counted over the
  whole dictionary rather than the automated rows alone (`doi_hygiene.py`, run it
  for the current figures) and excluding preprint DOIs, which are the paper and
  are not a defect. **Ben chose a distinct `DOI (for data)` column on 2026-09-06,
  and chose to add it without touching the sheet.** So it is an auto-only column:
  it lives in `dictionary_auto.csv` and in the merged export, `union_dict()`
  creates it, and where it equals the sheet's `DOI (for paper)` the paper cell is
  cleared in the export only. `backfill_data_dois.py` wrote the 979 rows; 971
  land now, 8 are held for tables absent from metadata.csv.

- [ ] **BLOCKING, before the next `irw_meta` publish: `irw_merge` groups tables
  by `DOI__for_paper_`.** `Rpkg/R/merge.R:59` splits biblio on that column, and
  826 rows across 147 groups currently group by a DEPOSIT DOI. Clearing those
  cells is correct for citation and wrong for merging: those tables stop being
  discoverable as siblings. The fix is a fallback -- group on the paper DOI
  where there is one, the data DOI otherwise -- in `Rpkg/R/merge.R` and the
  Python package's equivalent, both of which can read `DOI__for_data_` as soon
  as biblio.csv carries it. Nothing uploads automatically, so the ordering is
  controllable: land the package change first, publish second.

- [ ] **The 8 held backfill rows.** They name tables the dictionary has and
  metadata.csv does not, so they are held rather than dropped and land on the
  first run after the table is published. One is not a table at all: the sheet
  has a row whose `table` value is a whole citation string, `Canham L, Salamh P
  et al. (2018). Evaluation of non-cognitive traits of doctor of physical therapy
  learners in the United States. Harvard Dataverse.` -- a sheet defect needing a
  human, not a pipeline bug. The others are `mtf`, `fryback_2009_health_pwbs`,
  `fryback_2009_health_pwbp`, `fryback_2009_health_discrm`,
  `fryback_2009_health_sf`, `diaz-narvaez_2024_dental_students` and
  `anthropomorphism_health_Voropaeva_2026`.

- [ ] **#1690's remaining tail, which needs a lookup rather than a rule.** 21
  free-text cells (`not yet published`, `No DOI`, an OSF landing page) and 2
  holding several DOIs (`condon_2024_sapa_personality` has seven, `imps2025_hf`
  two, written on two lines). `stage_dict_row.py` refuses all of these on write
  now, so the set cannot grow; clearing it means finding the paper for each.

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

- [x] **RULED 2026-10-19: Qualtrics geo-IP coordinates disqualify the
  candidate.** ben-domingue: "what the skill says is fine. no tables whose
  origin had pii" -- the blanket rule stands and dropping the column is not an
  option, so `10.7910/DVN/JC6F9O` stays skipped and its ~132,000 responses are
  not available. Original note kept below for the record.
- [ ] ~~**Decide whether Qualtrics geo-IP coordinates count as PII**~~
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
  `TERM_LIST` is 125 terms. **Blocked on routine IDs, and re-confirmed 2026-09-08 (#1940)**:
  the `RemoteTrigger` `list` action returns the newest 20 with `has_more: true`, and
  passing the `next_cursor` it hands back returns *the identical page* — the cursor
  is accepted and ignored, so this is not a matter of asking correctly. The oldest
  routine visible was created 2026-08-25 and the standing ones date from ~2026-08-13/14,
  so they fall outside the window and cannot be listed, confirmed or denied from a
  session. Get their IDs from https://claude.ai/code/routines and hand them over, or
  edit them there. The two enabled routines that ARE visible are recorded in
  `ARCHITECTURE.md` section 6.
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
  — **`altman_2020_capq` done 2026-08-29, awaiting upload**: written to
  `itemtext_output/altman_2020_capq__items.csv` (19 items x 6 anchors = 114
  rows) as the first end-to-end exercise of the new Step 3.5 integration.
  Gates PASS against both the staged CSV and live data, with identical
  reports. `instructions` left blank — the CAPQ stems are noun phrases
  hanging off a shared prompt the deposit never records, and inventing it is
  not allowed. Provenance row in `itemtext_provenance.csv`, `uploaded`
  unstamped. The `sumner_2022_*` half stands: positional labels fail the
  cheapness gate, so they still need the published FTD-SS.

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

- [x] **`irw_process_queue.py` import fixed** (2026-08-29, `ca67872`). It
  imported `QUEUE_SHEET_URL` from `irw_discover_updated.py`, which no longer
  defines it, so the module died at import with an error that read like a
  missing dependency rather than "this stage was retired". Neither option in
  the original note was right: repointing it at `human_review/*.csv` would
  resurrect a stage eliminated 2026-06-24, and deleting it would lose a
  reference the README still cites. Instead the URL is defined locally so the
  module imports, and `main()` exits 2 naming the current flow. The footer
  `irw_batch_updated.py` printed after every triage run, still telling people
  to use the retired queue sheet, was fixed at the same time.

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
  **Superseded 2026-10-07 (#2887):** neither. Conjoints now go to their own
  source, `irw_conjoint` (`data/conjoint/README.md`), and the pipeline routes
  them to `data/conjoint/candidates.csv` (README, "Conjoint experiments").
  DVN/CDLVDH is not in that ledger yet.

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

## From the 2026-09-25 PMC scout-2 sweep

- [x] **29 tables (202,976 responses) uploaded** (ben-domingue, confirmed 2026-09-26).
  No item text this batch.
  Dictionary and tag rows are staged in `dictionary_auto.csv` / `tags/tags_auto.csv`.
- [ ] **3 tables need uploading** (`irw_output/`): `csibra_2025_dafrs_symptoms`,
  `csibra_2025_dafrs_function`, `atalay_2024_pozqol` (the held pair, released
  2026-09-26). No item text.
- [ ] **51 `out_of_range` leads unworked** in `leads/pmc_leads_2026-09-25.csv`
  (all 77 `in_range` rows are terminal).
- [ ] **Cheap item text for 16 tables**: csibra (Appendix A), atalay (s003.pdf), fredborg (Data Legend sheet), ge (.sav
  labels), guo (xlsx header), jie (.sav labels), todor (s001.docx).
- [x] ~~458 scouted terms unrun~~ -- 50 more ran 2026-09-28; the open count
  is carried in the 2026-09-28 section below.

## From the 2026-09-28 PMC scout-2 sweep (terms 51-100)

- [x] **30 tables (353,632 responses) in `irw_output/` uploaded 2026-09-28**, and
  the 1 item text table (`dorsch_2025_ai_tam__items.csv`) uploaded the same day.
  Tables: `modzelewska_2021_*` (4), `iwanicka_2017_*` (4), `tao_2026_mpai`,
  `turcsan_2020_dog_dpq`, `pajnkihar_2017_cnpi`, `martindelcampo_2020_*` (5),
  `herreromontes_2022_audit`, `putro_2024_*` (4), `wang_2023_*` (3),
  `li_2025_*` (4), `dorsch_2025_ai_*` (2). Dictionary and tag rows are staged;
  `itemtext_provenance.csv` rows are unstamped. Response tables first.
- [ ] **98 (term, journal) pairs never searched** (Europe PMC 503s + the run
  killed in psychometrika): 64 failed queries across 36 terms, plus
  psychometrika for terms 17-50. Listed per term in
  `pmc_term_backlog_2026-09-25.csv` (`run_2026_09_28=partial`,
  `unrun_journals_2026_09_28`). Re-run those terms with `--journals <list>`,
  not the whole set.
- [ ] **408 scouted terms still unrun** in `pmc_term_backlog_2026-09-25.csv`.
- [ ] **Decision: Alharbi 2024 nursing simulation (peerj.18150) held on trust.**
  86 of 201 rows sit in exact-copy groups on 92 items (47 later copies).
  The script is in the gitignored `runs/held/`; say whether to ship it
  deduplicated (about 154 ids) or drop it.
- [ ] **Decision: AUDIT item text for `herreromontes_2022_audit`.** The deposit
  codebook has it, but the rights register says `ship_with_note`.
- [ ] **Item text deferred, not cheap-gate:** `pajnkihar_2017_cnpi`
  (Slovenian stems in the `.sav`, no English), `martindelcampo_2020_*` and
  `modzelewska_2021_*` (English labels on Spanish/Polish administrations =
  `translated_substitute`), `dorsch_2025_ai_vignettes` (wording differs by arm).

## From the 2026-10-17 Dataverse re-mine (#3051; BATCH_LOG.md 2026-10-15 to 2026-10-17d)

- [ ] Confirm the table-name years against the papers (none is verified yet; names kept as shipped): stiglic_2019_wemwbs (file timestamp), espinoza_2024_dass21 (deposit year), sekowski_2023_* (citation), christensen_2017_* (file name), karim_2022_phq9 (deposit year), wicki_2021_av_concern (deposit year), delapena_2026_fscale (deposit year; preliminary paper).
- [x] Item text: nothing is missing (checked 2026-10-18). No item text was extracted anywhere in this round -- the 17 "available in the source" notes are tags on the source deposit, not built files. The two files that read as missing, gambin_2020_phq9.csv and gambin_2020_pandemic_diff.csv, sit in fork N's gitignored runs/leads_fork_N_2026-10-16/out/, and they are id,item,resp response tables, not __items files; both tables are in dictionary_auto.csv and are built by data/gambin_2020_covid_poland.py on main. Item text for Gambin would be new work off the deposit.
- [ ] Item-text holds for named scales are recorded as blocks in itemtext/instrument_rights_register.csv (Eichmeier x6, Amornsriwatanakul x2, Mesaric SAQ-AV, Delapena F-scale, Munoz-Troncoso VI-GEC). Revisit only if a grant turns up.
- [ ] TEIQue-SF: blocked (LPL terms cl.6, 7.3, 8). pavey_2021_teique withdrawn from Redivis by Ben, 2026-10-17. Re-ship only with a grant from LPL.
- [ ] Remove the fork worktrees under .claude/worktrees once nothing else needs them (all fork branches are merged to main). The count of 29 is stale: 19 remain there, and `git worktree list` shows 35 in all, so some belong to other sessions (the itemtext rounds work out of worktrees too). Ask before removing any, and note fork N's runs/ output is the only copy of a few build artifacts (see the item-text entry above).
- [ ] Main working tree has uncommitted changes from the separate itemtext session (pending_index_notes.csv, batch_dv_remine provenance, tools/withdrawals/withdraw_3017_tranche2). Not from this round; don't commit them with this work.
- [ ] Queue closed: no 'todo' leads left in leads/repos_ledger_remine_2026-10-16_dataverse_rest.csv (26 shipped, 201 skipped with reasons).
- [x] The recurrence is fixed (2026-10-18): chain_step2b writes each row's refined_flag back into the seen ledger, on all five entry points (irw_batch_updated.py, the two manual connectors, the two scheduled wrappers). --ignore-seen-keys / --ignore-seen-dois skips the write-back, which is the re-mine case. `python seen_ledger.py drop <ledger> --refined-flag <bucket> --apply` reopens a bucket.
- [ ] Backfill candidate: the ~500 Dataverse keys re-mined in 2026-10 have a refined flag in leads/repos_ledger_remine_2026-10-16_dataverse_rest.csv but a blank refined_flag in the ledger -- that run was --ignore-seen-keys, so nothing was written back, by design. Worth filling from the leads file. The remaining human_assistance keys have no recorded refinement to backfill; it was never written down anywhere.
- [x] The Zenodo `no_usable_file` verdicts were a resolver bug, fixed 2026-10-18 (BATCH_LOG 2026-10-18b): a candidate carrying only a DOI reached no resolver. 30-key sample, 30/30 no_usable_file before, 0/30 after, 17 of 30 pass the leads filter.
- [ ] **The rest of the pool is issue #3077**, the standing re-mine backlog: the 36 unworked `good` keys, human_review batch 5, and the 1,035 repo-resolvable `human_assistance` keys (zenodo 632, mendeley 179, figshare 117, dryad 86, osf 21). Recommended first step, not yet run: one ~100-key zenodo batch to test the sampled 57% lead rate at scale. Of the 652 `other` keys, 553 are article-SI DOIs that belong to the PLOS/PMC path, not a repos re-mine, and 76 are Dataverse installations (10.5683 Scholars Portal, 10.34894 DANS/SURF).
- [x] Zenodo rate check done 2026-10-18 (BATCH_LOG 2026-10-18c, #3077): 100 keys -> 99 resolved, 49 leads in leads/repos_ledger_remine_2026-10-18_zenodo.csv, plus 30 deferred rows whose N is unknown until the file is read. 49% matches the 30-key sample's 57% and Dataverse's 53%.
- [ ] **Work the 49 zenodo leads** (#3077): forks of ~26, one at a time, the #3048 way, when Ben says so. Then decide the remaining 511 zenodo keys and the mendeley 179 / figshare 117 / dryad 86 / osf 21 from that yield.
- [ ] The 2,223 ledger rows keep their stale `no_usable_file`/`human_assistance` flags. `python seen_ledger.py drop repo_triage_seen_keys.csv --flag no_usable_file --before 2026-10-18 --apply` is the documented way to reopen them -- but that is 2,639 `no_usable_file` keys across all sources, so scope it to zenodo/figshare/mendeley/osf and agree the scope first (#3077).
- [x] Cross-check the 128 `good` keys (done 2026-10-18, BATCH_LOG 2026-10-18): 69 shipped, 23 closed with a reason, 36 unworked. Per-key result in leads/repos_ledger_good_keys_2026-10-18.csv; re-runnable with `python check_shipped.py --out ...`.
- [ ] **Work the 36 `good`-key leads** -- item 1 of #3077, the standing re-mine backlog. Forks of ~26, one at a time, the #3048 way. 6 are in no leads file at all, 25 are the unworked tail of the 2026-08-27/28 Zenodo backlog sweep, 5 are `unworked` in repos_leads_2026-10-07.csv.
- [ ] **Dictionary gap found by the same pass:** four live tables have no dictionary row carrying their data DOI -- yang2026_efl_learner_perspective, tang_2026_rmet_c, mcdermott_2014_roadmaps_expert_ratings, political_preference_china. Separate from #3051.

## From Luettgau 2026 (uploaded 2026-10-22, #3174; BATCH_LOG.md 2026-10-22)

- [x] `luettgau_2026_source_trust__items.csv` uploaded 2026-10-22 and stamped
  in `itemtext_provenance.csv`. The two gate steps skipped on the first pass
  were run retrospectively against a rebuilt response CSV:
  `normalize_nulls.R` changed quoting only (the NA tokens were already bare,
  so the uploaded copy is byte-equivalent in content and needs no re-upload),
  `audit_batch.R` PASS with no anomalies, `irw-validate` ok. The staged copy
  is still in `automated_finding/itemtext_output/` for Ben to clear.
- [ ] **Ask the authors two questions; both unpark 64 items of item text.**
  The deposit publishes an issue tracker
  (`github.com/UKGovernmentBEIS/dhi1-analysis-public`). (a) Which statement is
  which question index — ideally the instrument as fielded. The article's
  appendix prints 8 true then 8 false statements per topic and the data
  confirms the block boundary at 8, but nothing ties the listing order to the
  index *within* a block. (b) The seven Likert point labels and their numeric
  coding, which are published nowhere; the column is stored agree-first, so
  guessing them would invert `option_text` against the responses half the
  time. All 64 statements are already transcribed in
  `itemtext/fixes/luettgau_2026_political_knowledge__items.PARKED.csv`.
- [ ] **Decision: can `wave` be recovered for the trust and private-belief
  batteries** (10 items each, same deposit, not shipped)? Both hold one row
  per (subject, topic, question) with `presented` labelling it pre or post, so
  the same subject-question reads "pre" under one topic and "post" under
  another — either the battery was re-administered at four timepoints or the
  rows are an artefact of the analysis table's topic join. Needs a human read
  of the article's supplement. Their item text is in the same appendix as the
  statements above, so wording is not the blocker.
