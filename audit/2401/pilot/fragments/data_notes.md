# Data strand: notes on RULES.md from the pilot (3 tables)

## Where the rules were ambiguous or did not fit

1. **§1 says the data strand runs "irw_validate's upload profile on live data". The pilot brief says aggregate SQL only, with row reads capped at a few thousand.** These conflict. The validator needs the rows. trevisan_2018_mscs alone is 90,703 rows, and sokolovskii is 10,863. I did not run the validator on any table. RULES should say one of:
   - (a) the validator runs only on tables under N rows;
   - (b) the validator's checks get SQL equivalents (as live_dup and live_cov_range already did for two of them);
   - (c) the lead-specific aggregate replaces the validator for lead-driven rows.

   As written, every data row either breaks the export rule or skips a mandated check.

2. **§3 "Live data, never data/pub alone" is silent on local copies of the source's raw inputs.** Two of the three verdicts needed the raw file, because live data can't show a column IRW dropped:
   - tuason: `Emjoy` and `Well_being_3groups`;
   - trevisan: the fractional cells.

   Both were in `~/irw-queue-runner/itemtext/.cache/` with sha256s, and the tuason file matches a fresh PLOS download (round log). Suggested rule: a cached raw input is admissible alongside live aggregates if its sha256 is recorded. It never stands in for the live check.

3. **No outcome covers a script-comment-only correction** (trevisan). It isn't a `fix` (no rebuild), and it isn't a `data_note`: the table already shows the cells as missing. I used `no_action` plus a housekeeping line. Suggestions:
   - allow a `no_action` row to carry a "hygiene" free-text field; or
   - state that comment errors which change no value are out of scope.

4. **A `fix` that invalidates a live item-text public_note** (tuason) needs two outcomes: `fix` plus a later `claim_edit`. §2 allows "exactly one per finding". RULES should either say that dependent follow-ons are implied, or allow a `then:` column.

5. **`register` vs `no_action` for a register *notes* update** (sokolovskii). The TFEQ row's notes say "LEAD, unchecked" about this very table. Updating that text is neither a pattern change nor a table action. Please say whether a notes-only edit is `register` or is housekeeping.

6. **The register has no table-scoping column.** Its code patterns can't reach opaque codes (`i_n`, `q1`), and its text strings are English-only. So a translated instrument with opaque codes passes both automated surfaces, and only instrument-name triage catches it. This has come up for TFEQ, PROMIS and DIENER-NC. It needs one ruling for the group, e.g. an optional `match_table` column, and not a wider regex.

7. **Group keys are free text.** I invented `data:rebuild-from-source-variable`, `data:script-comment-only` and `rights:register-code-pattern-gap`. Without a seeded vocabulary, parallel agents will coin synonyms and grouping will fail. A short starter list in §4 would help.

8. **Round-log line numbers drift**, because the log is appended to. `round_log:L<line>` should pin a commit hash or quote the anchor heading (e.g. `round_log:batch_197`).

9. **`redivis_reads` can't record local raw reads.** I wrote `aggregate` and put the local read in the dossier. Consider a value like `aggregate+local_raw`.

## Scriptable vs human

**Scriptable:**
- Resolving live refs (`shard_index`).
- Row/id/item/resp-range counts, and the non-integer count.
- The per-id sum histogram, as a general "all-zero respondent" detector for binary tables. It is worth adding to live_* as a sweep: a block of ids with all-zero rows on a checklist is a signature.
- Missing-(id,item) localisation.
- Joins across sibling tables on id.
- Running `rights.check_item_codes` on the live distinct-code set: it needs no rows, and should be a standard aggregate step.
- Checking `itemtext/live_tables.csv` and `reaudit/triage_results.csv` for a table.
- Re-hashing cached raw files.
- Drafting the worklist row from the dossier fields.

**Needs judgement (agent or human):**
- Finding the source variable that holds the truth (tuason `Emjoy`).
- Recognising mean imputation from keyed person-means, which needed the reverse-keying from the `_R` columns.
- Reading the paper's instruction ("select 5") to decide which source variable is authoritative.
- Choosing rebuild over dropping a group.
- Applying #2529's bar ("can the table express it?").

**Needs Ben:** none of the three tables. Items 1, 3, 5 and 6 above are policy questions for RULES itself.

## Cost
About 35 agent-minutes in total. There were about 9 aggregate queries plus one shard-index build, with no row downloads. The two local raw reads used caches that already existed.
