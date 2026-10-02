# bitew_2020_lte (claim strand, administered language)

**Lead:** issue #1801 (tier C of the #1777 language backfill). In `itemtext/language_backfill/audit_2026-09-01.csv` L272, the classifier rated the table INDETERMINATE ("pure-ASCII, not provably English or not"). The tags sheet says `amh`, which the backfill README says is not evidence on its own.

## Claim as stated publicly
- The live item-text table has **no `language` column**. It predates the 2026-09-01 schema. So the public record makes no language claim, and the gap is itself the finding.
- The `instrument` field (live, and in `metadata/itemtext_metadata.csv`) reads: *"List of Threatening Experiences (LTE), 12-item version as administered in Amharic"*.
- There is no issues-page entry.

## Independently checked
1. **Shipped wording** (`irw_itemtext`, 24 rows). There are 12 items (LTE1-12) × no/yes (0/1). The `item_text` values are English fragments: "self illness", "accident on relatives", ..., "intimate partner violence". `instructions` and `section_prompt` are empty. **The shipped text is English.**
2. **Where that English comes from.** I re-downloaded S1 File from PLOS (the `.sav`). The variable labels are `'1 self illness'` ... `'12 intimate partner violence'`, which is exactly the shipped text with the numbers removed. There are 0 Ethiopic and 0 non-ASCII characters across all variable and value labels. S2 (docx) is the response to reviewers, also with 0 Ethiopic characters. So the English is the study's own descriptors (`study_supplied`), and the deposit holds no Amharic.
3. **Administered language.** The paper, PLOS ONE 10.1371/journal.pone.0240914 (CC BY), says in its Methods: *"We compiled the data collection tools in a form of self-administered Amharic version of questionnaires"*. **Administered: Amharic.**
4. **Live response table** (aggregate SQL, `item_response_warehouse_3:v10_0`). The same 12 items appear, resp 0/1, about 655-664 ids per item. The join keys match the item text.
5. The round log (L776-791) and the provenance row say the canonical LTE-Q wording was deliberately not substituted (this is a modified, reordered 12-item version, and item 12 is not an LTE-Q item). That is consistent with the above and does not change anything.

## Verdict
This is a textbook case of the skill's "fallback" (SKILL.md §core model: *"In the fallback, `language` still names the administered language"*). The administered wording cannot be recovered from the deposit or the supplements, and English from the study's own labels sits in the base fields. The table should read `language=Amharic` with empty `_translated` columns. Provenance should read `text_source=translated_substitute` and `translation_source=study_supplied`. Because the English is study-supplied, the 2026-09-02 ruling means no issues-page line is owed. The `instrument` string's "as administered in Amharic" can stay, since it is true.

- **proposed_outcome:** `fix` (item-text rebuild: add `language=Amharic`, plus provenance `text_source`/`translation_source`. `item_text` is unchanged.)
- **confidence:** high (the paper states the language outright, and the deposit was checked for script)
- **group:** `lang_fallback:bitew_2020`. All four bitew_2020 item-text tables (`_lte`, `_osss3`, `_phq9`, `_self_efficacy`) come from the same paper, the same Amharic administration and the same `.sav`. The other three sit in tier B (#1777) and should get the same fix in one rebuild. More broadly, the group is `lang_fallback:study_supplied_english`.
- **minutes:** ~15
- **redivis_reads:** aggregate (1 query) + rows:24 (the item-text table)
