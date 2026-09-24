# Naming audit — evidence file

`naming_audit_suspects.csv` is the per-row output of the table-name audit run for
[issue #1686](https://github.com/ben-domingue/irw/issues/1686) on **2026-08-27**.

## Read this before acting on anything in the CSV

**Renaming was considered and declined.** The `proposed_name` column documents what
each table's name *would* be under the `authorname_year_construct` convention. It is
**not a work queue**, and no one should pick it up as one.

The reasoning, from #1686: a table name is an opaque identifier carried across the
dictionary, the biblio sheet, the tags sheet, Redivis, `__items`, processing scripts
and issue history, with no transaction spanning those surfaces. Any rename is
guaranteed to be non-atomic, and a consistent non-compliant name is better than an
inconsistent compliant one. The convention is a guideline, not a rule.

The factual claim about *who did the work* lives in the dictionary's `Reference`
column, not in the table name — and every wrong `Reference` has been corrected (see
below). The names stand as they are.

One rename was carried out: `alomari_2025_student_questionnaire` ->
`xie_2026_student_questionnaire`, already agreed on #1651 and unusually cheap. It is
complete across IRW3, `irw_text` and the dictionary. **Nothing else moves.** The CSV
still lists the table under its audited (pre-rename) name, with a note on that row.

## What was found

Of **1,945** rows with `Contributor == "automated"` (dictionary read 2026-08-27,
4,140 data rows total), **16 tables are named for someone who is not the source's
first author**:

- **15** with verdict `name_absent_from_authors` — the surname appears nowhere in the
  resolved author list.
- **1** with verdict `given_name_used` — `divia_2025_tiktok_fomo_shopping`, where the
  figshare creator is "Arifin, Divia Indira" and the *given* name was used.

Those 16 are exactly the rows carrying a `proposed_name`. They trace to roughly 8 bad
lookups, because two are clusters: five `kern_2021_*` (actually Yang et al.) and two
`kilic_2024_*` (actually Özsarı et al.).

**The critical half is already fixed.** 10 of the 16 had a `Reference` naming the
wrong researcher and 2 had none at all; `metadata/02_biblio.R` reads `Reference`
straight into `biblio.csv`, so the site was publishing false citations. All 12 have
been corrected from their DOIs, along with two corrupted titles (`burgess_2025_soas`,
`gizaw_2023_phq9`).

## Verdict vocabulary

| verdict | n | meaning |
|---|---|---|
| `name_absent_from_authors` | 15 | surname appears nowhere in the resolved author list — real errors |
| `given_name_used` | 1 | named for the author's given name |
| `non_first_author` | 7 | a real author of the paper, just not first — convention question, not a defect |
| `named_for_corpus_pi` | 17 | `goldberg_2018_*`, the Eugene-Springfield corpus; deliberate and consistent |
| `name_order_ambiguous` | 2 | `duong_2025_*`; Crossref mis-splits Vietnamese name order — name is probably right |
| `year_mismatch` | 55 | year in name vs year on the record; nearly all are dataset-deposit-year artifacts |
| `no_doi_unverifiable` | 6 | **could not be checked** — no registered DOI. Not "clean". |
| `not_author_named` | 80 | earlier batches use topic naming (`dass21_*`, `conspiracy_asd__*`) — a different convention |

Rows with verdict `ok` (1,762) are not included in the file.

The 6 that could not be checked at all: `marquezpalacios_2026_bdi2`, `opladen2025_edeq`,
`opladen2025_wi`, `opladen2025_fkg`, `opladen2025_fks`, `schoepp2022_test_anxiety`.

## Two traps for anyone building the naming gate

Both produced real false positives during the audit and are carved out in #1686:

1. **Compound and particled surnames.** Matching only the Crossref `family` field
   falsely flags `van Teffelen`, `Lopes de Jesus`, `Makowska-Tłomak`, `von Hippel` and
   ~35 others. Match every contiguous run of surname words joined without separators,
   absorb trailing nobiliary particles from `given`, and map Turkish dotless `ı`
   explicitly — it has no NFKD decomposition.
2. **Dataverse lists only the depositor.** `cavojova_2017_cfc` and `cosenza_2015_cfc`
   look fabricated against the creator list but are correct per the record's linked
   publication. A gate reading only creators will produce confident false accusations.

## Caveat

The dictionary sheet is live and grew ~200 automated rows on the day it was read, so
this is a snapshot. Rows added after 2026-08-27 are unaudited.
