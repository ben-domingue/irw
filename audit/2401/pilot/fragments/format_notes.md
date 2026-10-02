# format strand: pilot notes (4thgrade_math_sirt and movac_pakpour2022)

## 1. Ambiguities in RULES.md

1. **The worklist has one row per table, but a table can have several findings.** 4thgrade carried three legacy warnings (`imputed_values*`, `multi_scale*`, `column_order`). The control produced four clean checks plus one note. §2 says "exactly one outcome per finding", and §5 has no `finding_id`. I collapsed each table to one row and put the minor findings in `evidence`.
   - *Proposal:* make it one row per (table, finding).
2. **A control has no strand.** A table picked as a control goes through every strand. Its row needs either `strand=control` or one row per strand that was run.
   - I used `strand=note`, because the only positive result was a note. With that choice, the clean rights and data checks leave no trace in the worklist.
3. **`data_note` vs "the table is fine but its script is not".** For movac, the live table is correct. The 45 mean-filled rows were dropped by hand at build time, but the committed script does not drop them.
   - None of the §2 codes covers "script does not reproduce the live table". It is not a `fix` (the data is right), not a `known_issue`, and not a `waive`.
   - *Proposal:* add a `provenance` code, or allow a script-only `fix`.
4. **The confidence rule covers only `withdraw` and `fix`.** A `data_note` whose facts are certain, but whose need is a judgement call, has no guidance. I used `medium`.
   - *Suggestion:* score confidence on the *facts* only. Send "is this worth a note?" to `needs_ruling` in batches.
5. **"Live data" does not cover a source re-download.** §3 requires live IRW data. It says nothing about fetching the *source deposit*, and that fetch was the only thing that found anything on the control. The rules should say when this is required. My suggestion: whenever the script or the deposit file name signals imputation, filtering or a hand edit.
6. **`redivis_reads` does not separate the response table from the item text.** I wrote `rows:72180` (72,096 response rows plus 84 item-text rows). Separate fields, or a documented sum, would be clearer.
7. **The §1 format row says "unless the warning changes an analysis", but the legacy messages are too thin to judge that from.** They carry no value and only the first item (`_checks.py` used to break after the first hit). Every `imputed_values*` lead therefore needs a live query before it can be dismissed. That is exactly the cost the strand is meant to avoid.

## 2. Should the `format` strand exist?

**Not as a per-table review of legacy warnings.** The pilot's evidence:

- **`imputed_values*` is not specific.**
  - It fired on 557 of the 852 tables opened (65%). By construction it fires on 83% of dichotomous tables.
  - 222 of the 557 (40%) are dichotomous tables. On those, a modal integer cannot be a mean fill, so they are false alarms by construction.
  - #1728 had already sampled 30 of these messages and supported none (`_checks.py:521-532`). #2314 then rewrote the check to drop the causal claim and to name the dominant value.
  - The 2026-09-02 CSV predates that rewrite. Auditing its messages means auditing a check that no longer exists.
- **It is also not sensitive.** The control's source deposit contains a real mean imputation: 45 whole-person rows set to the item means. That is 0.7% of rows, so a ">60% of an item" concentration test could never have caught it.
- **Recommendation:** drop `imputed_values*` (and `column_order`, `name_charset`, `multi_scale*`) from the audit. Record the 222 dichotomous hits as tuning evidence. If needed, re-run a *better* check as a corpus sweep rather than a strand (§3). Only the remaining warnings that can change an analysis belong in the audit:
  - `cov_range`, already done by #1779;
  - `sample_floor`, which is a policy question and not a format one.

## 3. What is scriptable

Everything in the control except the note judgement. The whole checklist could run as one driver per table:

| step | how | cost |
|---|---|---|
| live resolve + count vs `metadata.csv` | `live_dup.shard_index` + `SELECT COUNT(*), COUNT(DISTINCT id/item), COUNTIF(resp IS NULL)` | 1 aggregate |
| upload profile | small tables: shim read then `irw_validate.cli --profile upload`. Large tables: need a live loader (`validate_file` only reads files) | rows |
| rights | `rights.load_register()`, then `check_item_text(itemtext_df, t, reg)` and `check_item_codes(resp_df, t, reg)`. **Gotcha:** both crash with `TypeError` if `register` is not passed; the default is `None`, not the loaded register | ~100 rows |
| per-item value counts | `GROUP BY item, CAST(resp AS STRING)` | 1 aggregate |
| **real** mean-imputation signature | per item, count non-integer `resp` values and the share of the modal non-integer value; per id, flag rows where all `resp` are non-integer. Pure SQL, and it would have flagged the movac deposit | 1 aggregate |
| script-header data-note lead | grep `data/<script>` for `imput|missing|drop|filter|na.omit` and for raw file names containing `imput` | none |
| licence | Dataverse `/api/datasets/:persistentId`, Europe PMC `search?resultType=core` gives the `license` field | network |

**Not scriptable:** deciding whether a correctly handled source quirk deserves a public note, and reading an adaptation clause ("with the kind permission of...").

**Timing:** the four standard checks took about 10 minutes on the clean table. The source follow-up took about 25 more. At that rate, a full checklist on every table is expensive unless it is scripted. A scripted run should produce near-zero noise on a clean table: 0 of 4 automated checks fired here.
