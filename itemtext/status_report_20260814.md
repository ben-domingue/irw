# Itemtext — Status Across Three Threads (2026-08-14)

This rolls up where things stand on `irw-auto-itemtext` work as of this
session, organized into the three threads Ben asked to track separately.

---

## Thread 1: Revision of historic tables (audit mode)

**Status: complete**, unchanged since the last session. Full detail in
[`audit_batch_reports/OMNIBUS.md`](audit_batch_reports/OMNIBUS.md). Summary:

- All ~421 tables with existing curated item text have been checked at
  least once (330 individual checks across the original 100-table eval +
  13 audit batches).
- 275 green (confirmed clean), 1 yellow (documentable caveat, not yet
  pasted into `itemtext_issues.qmd`), 24 red (GitHub issues filed,
  `#1594`/`#1598`-`#1622`), 30 gray (unverifiable, logged for retry).
- Net finding: every real disagreement between a fresh extraction and
  existing curation traced to curation being stale/incomplete/mislabeled,
  never the reverse.
- One new red-adjacent finding this session, outside the original 421-table
  audit scope: `preussmattsson_2022_ownership`'s live response data
  conflates 6 questions with a 4-level experimental condition in the `item`
  code — filed as
  [`#1626`](https://github.com/ben-domingue/irw/issues/1626) (a core
  response-data structure issue, not an item-text-curation issue).

No new work needed here unless Ben wants another audit pass (e.g. after the
next large batch of new itemtext tables lands).

---

## Thread 2: Audit of human-annotated item-text availability (new this session)

**What this checked:** whether the *judgment calls* recorded in the index
workbook's `tables_excluded` (46 rows), `queue` (457 rows, 1 active claim),
`xz_todo`/`nj_todo` tabs hold up — i.e., are tables marked "can't do this" or
"claimed by someone" actually correctly classified? This is distinct from
Thread 1 (which checks *content accuracy* of tables already marked done).

**Sample: 16 tables**, stratified across `tables_excluded`'s five reason
categories, one `queue` claim, and three from the "has item text" bucket as
a sanity check on the other side.

| Result | n | Tables |
|---|---|---|
| ✅ Agree — exclusion/status is correct | 9 | `handwriting_2006`/`2007` ("doesn't exist in irw" — confirmed absent from `irw::irw_list_tables()`), `anunciacao_2024_intelligence_gmi` (nonverbal matrix test, only a response-only `.RData` file exists, no stimuli), `karim2022_tmoca_mci` ("no public access" — MoCA is a certification-gated clinical instrument, correctly excluded), `mclaughlin_samuel_2025_auditory_session_1` (note already explains the prompt is participant-selection-dependent), `idcr_martinez_2023_analogies` (note already flags a genuine format uncertainty), plus 3/3 "has item text" spot-checks (`coach_chen_2022_hdrs`, `psychotools_gratitude_gart`, `gilbert_meta_53` all had 100% non-blank `item_text`) |
| ❌ **Disagree** — exclusion looks wrong | **4** | `himmelstein-impossible_question-2025`, `himmelstein-admc_raw-2025`, `himmelstein-shipley_abstraction-2025`, `himmelstein-shipley_vocabulary-2025` — see below |
| ⚠️ Inconclusive (tooling-blocked or not deep-verified) | 3 | `bafacalo_golino_2013_cis` (Harvard Dataverse WAF-blocked — same tooling limitation hit repeatedly this session, not necessarily true unavailability), `test_taking_much_2025_ao`, `rapm_poulton_2022_timed` |

**The disagreement, in detail:** all four `himmelstein-*` tables cite
`https://github.com/forecastingresearch/fpt/tree/main/data_cognitive_tasks`
directly in the IRW dictionary's own URL field — a fully public GitHub
repo. `data_impossible_question.csv` in that repo has a `question_text`
column with literal item text, and its `id` values (`IQ_3`, `GK_23`, ...)
match the live IRW `item` codes exactly. The sibling files
`data_admc_raw.csv`, `data_shipley_abstraction.csv`,
`data_shipley_vocabulary.csv` are sitting in the same public folder. None
of this required going near Harvard Dataverse (which is what's
WAF-blocked) — the correct source was already the dictionary's own URL.

Caveat worth flagging before treating these as easy wins: Shipley
Institute of Living Scale content is itself a commercially published
instrument (same family as CTOPP/BDI-II/MoCA elsewhere in this session's
work) — the fact that a CSV is publicly hosted doesn't settle whether its
content is free to transcribe into `option_text`/`item_text`. That
judgment call would need to happen per-table if these get reopened.

**Headline finding**: 4 of 16 sampled tables (25%) were excluded, at least
in part, because the *tool* used at the time to check (likely just the
Dataverse mirror) hit a wall — not because the item text was genuinely
unrecoverable. This is a small sample, but it's a real, concrete signal
that the exclusion tabs' "no public access"/"couldn't find item text" tags
aren't fully reliable and are worth periodic re-checking, especially where
GitHub/OSF mirrors exist alongside a blocked Dataverse link.

**Not done in this pass**: didn't re-verify `duolingo_*` (9 rows,
"messy data/difficult") or `idcr_martinez_2023_ravens`/other `idcr_*` rows
beyond the one with a note — flagging as open if Ben wants a deeper pass
on `tables_excluded` specifically.

---

## Thread 3: Building out new item-text tables (queue mode)

**Status: 2 pilot batches done, 16 tables attempted.**

| | n |
|---|---|
| Tables attempted | 16 |
| ✅ Written + validated (`{table}__items.csv`) | 10 |
| Genuine gap logged, no CSV forced | 6 |

Breakdown of the 6 gaps: 2 copyrighted standardized tests declined
(BDI-II, CTOPP — matches this skill's established precedent of declining
to transcribe copyrighted test content), 2 Harvard Dataverse WAF-blocked
(same tooling wall as Thread 2's finding above), 1 partial-disclosure
source (only 1 of 3 items quoted in the paper), 1 unrecoverable/no
freely-published source found (Prenatal Psychosocial Profile self-esteem
subscale).

Every written CSV passed `validate_items.R`'s item-set and resp-set checks
against live `irw::irw_fetch()` data, plus a manual row-count-per-item
check for silent item-code collisions (none found). 12 discrepancy/caveat
notes logged to `pending_index_notes.csv` for tables in both the written
and gap buckets — things like source-language mismatches (item text in
the administered language, response-scale anchors only found in English),
a dictionary correction (`cordova2019_clinical_edu_environment` is PHEEM,
not DREEM as labeled), and one bare-integer item-mapping confidence note.

**Remaining open-candidate pool**: ~2,377 tables (2,381 at the start of
this session, minus the 4 that would move to "done" if the 10 written CSVs
are approved and uploaded — not yet uploaded, per the standing rule that
`upload.py` only runs on Ben's explicit go-ahead).

**Not yet done**: none of the 10 written CSVs have been uploaded to
`bdomingu/IRW_text:next`. Awaiting the spot-check pass currently underway
before that happens.

---

## Suggested next steps (not yet actioned)

1. Finish the spot-check pass on the 10 written CSVs (in progress).
2. Decide whether to reopen the 4 `himmelstein-*` tables flagged above —
   would need the Shipley-copyright judgment call made first.
3. If Thread 2's finding generalizes, consider a systematic re-check of
   `tables_excluded` rows whose dictionary URL points somewhere other than
   Harvard Dataverse's own domain (i.e., cases where a GitHub/OSF mirror
   might exist even if Dataverse itself is cited elsewhere) — this session
   only sampled 16 of 46 excluded rows.
4. Once approved, `python3 upload.py .` from `itemtext/` to push the 10
   validated CSVs (prompts before overwriting).
