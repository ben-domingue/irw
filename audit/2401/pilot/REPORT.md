# irw#2401 pilot: 10 tables, 2026-09-29

This pilot tested the audit workflow on 10 hand-picked tables: 9 carried a known problem and 1 was a control with none. It was read-only against the corpus. Per-table evidence is in `dossiers/`, the combined results are in `worklist.csv`, and each agent's notes on the rules are in `fragments/*_notes.md`.

## Results

| table | strand | outcome | conf. | one line |
|---|---|---|---|---|
| `tuason_2021_covid_coping_enjoy` | data | **fix** | high | 322 of 938 ids answer 0 on all 23 items, all in the middle well-being group. Rebuilding from the `Emjoy` pick string matches 610 of 616 rows. The item-text public_note needs an edit afterwards |
| `bitew_2020_lte` | claim | **fix** | high | The shipped text is the study's English variable labels, but the questionnaire was administered in Amharic. Set `language=Amharic` and `translated_substitute`. The same fix applies to `_osss3`, `_phq9` and `_self_efficacy` |
| `beck_2021_iesr` | rights | **needs_ruling** | high | The German IES-R is free to use (Maercker). But `item_text_translated` carries all 22 Weiss & Marmar English items verbatim (from the language backfill), which falls under the IES-R block row. Decide together with `ali_2021_iesr` |
| `movac_pakpour2022` | control | **data_note** | medium | All four checks passed. But the deposit is imputed: 45 people's answers are all the item mean. Live data correctly leaves them out, and the committed script doesn't, so the script doesn't reproduce the live table |
| `rmet_higgins_2022_rmet` | rights | no_action | high | Already withdrawn (ruled 09-28, gone from v28.0). Its records are only in open PR #2539 |
| `cormier_2024_personality` | rights | no_action | high | Already withdrawn 09-10 (v21.0). The `released` cell in the withdrawals ledger is blank |
| `gilbert_meta_35` | claim | no_action | high | The callout was already rewritten 08-25 and holds on live data. **The drafted wording in `itemtext_issues_suggestions.md` names the wrong items. Don't paste it** |
| `trevisan_2018_mscs` | data | no_action | high | The live table is right. Only a script comment is wrong |
| `sokolovskii_2021_tfeq` | data | no_action | high | The `i_n` codes carry no wording, and no item text is live |
| `4thgrade_math_sirt` | format | no_action | high | A false alarm: the items are 0/1 and MA1 is an easy item (88.6% correct) |

Total: 2 fixes (5 tables counting bitew's siblings), 1 needs a ruling, 1 data note, 6 no action.

## What the pilot changes about the full audit

1. **Many of the logged problems are already dealt with.** Three of the nine had been remedied after they were logged. The full audit needs a cheap first step before any investigation: is the table still live, and has the claim already changed? That step can be scripted from the release manifest, `withdrawals.csv` and the website's git log.

2. **Drop the format strand.** Every error from the 2026-09-02 legacy sweep was already handled (#1842/#1856, #1779, name_length, the PISA files lost from the local archive). What's left is warnings. `imputed_values*` fired on 65% of the tables opened and on 83% of 0/1-scored tables. Only about 6 of its 557 hits are on tables where a mean fill is even plausible.

3. **A problem the checks can't see: scripts that don't reproduce the live table.** The control passed every automated check, and the problem only showed up when the agent opened the source file. Looking for this class means rebuilding tables, which is the most expensive thing the audit could do. **It needs an in-or-out decision.** Recommendation: out of this audit. Record it as its own later project, possibly sampled.

4. **A rights surface nobody has checked: the `*_translated` columns.** The language backfill (#1807) wrote canonical English wording into `_translated`. `sweep_instrument_rights.py` checks `item_text` only. The #1954 rights check has to cover both columns, and this is probably the rights strand's largest new risk.

5. **Grouping works.** bitew is one decision for 4 tables, and the IES-R is one decision for 2. The full audit should bring Ben group decisions, not tables.

## Rule changes for RULES.md (to make before the full audit)

- **New outcome codes:** `already_remedied` (with a pointer to the release or commit that dealt with it), and `script_drift` (live is right, but the script doesn't reproduce it).
- **One row per *finding*, not per table.** tuason needs a fix plus a claim edit, and beck has two wording layers that may need different outcomes.
- **Evidence:**
  - a cached raw source file counts as evidence if its hash or URL is recorded;
  - a ruling Ben has made counts at the freeze even if its records are only in an unmerged PR.
- **Live validation:** tables over about 200k rows get aggregate checks only (no full upload-profile run). That makes explicit a conflict the agents ran into.
- **Claims:** check the website's edit history before assuming a callout is stale.
- **Register:** it needs a way to scope a pattern to specific tables (the TFEQ, PROMIS and DIENER-NC gaps).
- **`redivis_reads`:** allow compound values (`aggregate+rows:N`).
- **A tool bug:** `irw_validate.rights.check_*` crashes unless the register is passed in explicitly. Fix it before any scripted sweep.

## Cost

The agents' own time estimates totalled about 190 minutes for 10 tables, roughly 19 minutes each. The range was 10 minutes for a stale lead to 35 for the control's source dig. Four agents in parallel finished in about 12 minutes of wall time. Redivis use was small: aggregates plus about 72k rows in all, most of it the control table.

Projected full audit, assuming the rights and translated-column strands dominate:
- **Size:** roughly 300–400 findings.
- **Agent time:** about 100 hours.
- **Wall time:** a few days at 4–6 agents in parallel.
- **Ben's time:** mostly group rulings, estimated at 20–40 decisions.

The cheap first step (point 1) should cut the investigated set by around a third.

## Decisions for Ben

1. **IES-R (`beck_2021_iesr`, `ali_2021_iesr`):** may `item_text_translated` carry the canonical English IES-R wording?
2. **Should the tuason rebuild and the bitew language fix (4 tables) go now,** or wait for the full audit? Both are high confidence.
3. Drop the format strand?
4. Keep script-reproducibility out of this audit?
5. Is the `movac_pakpour2022` data note wanted?
