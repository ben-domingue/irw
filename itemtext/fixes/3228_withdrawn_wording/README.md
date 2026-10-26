# Wording that stayed in the repo after a rights withdrawal (#3228, review R-40)

A rights withdrawal removes a table's item text from Redivis. It does not
remove the file the text was staged from. Nothing checked, so on **2026-10-26**
thirteen tracked files still carried wording for tables withdrawn on rights
grounds, two of them for withdrawals whose own note reads *"sentence-level
reproduction verified against item text"* -- the wording had been confirmed to
reproduce the instrument, withdrawn for exactly that reason, and left here.

R-40 asked a narrower question and got a different answer. Its worry was
`data/itemtext/`, a staging path proposed in #3016/#3017: that path has never
existed (`git log --all -- 'data/itemtext/*'` is empty), so that exposure is
prospective. Its second half expected the 87 tracked files naming a withdrawn
table to be verification harnesses with no wording. 83 of them are.

## Removed, 2026-10-26

Whole `__items` wording tables:

| file | rows | instrument | withdrawn |
|---|---|---|---|
| `itemtables/batch_205/qi_2025_swls__items.csv` | 35 | Satisfaction With Life Scale (Diener et al.) | 2026-09-27 |
| `itemtables/batch_205/qi_2025_self_construal__items.csv` | 210 | Self-Construal Scale (Singelis 1994) | 2026-10-17 |
| `itemtables/batch_205/teq_novak_2021_spirit__items.csv` | 88 | Daily Spiritual Experience Scale (Underwood & Teresi) | 2026-10-17 |
| `fixes/issue_1618_pezzuti_big5_southkorea/pezzuti_2025_coolpeople_main_big5_southkorea__items.csv` | 70 | BFI-10, Korean | 2026-10-17 |
| `fixes/issue_1618_pezzuti_big5_southkorea/itemtext_before_fix.csv` | 84 | the same, before the #1618 repair | 2026-10-17 |
| `language_backfill/round2/published/ALSECYPIAMH_WU_2022_SDQ__published.csv` | | SDQ | 2026-09-?? |
| `language_backfill/round2/published/almuqbil_2022_epds__published.csv` | | EPDS | |
| `language_backfill/round2/published/altahla_2024_swls__published.csv` | 35 | SWLS | |
| `language_backfill/round2/published/beck_2021_pss10__published.csv` | | PSS-10 | |

Verification harnesses that quote the items they check:

| file | item stems |
|---|---|
| `itemtables/batch_146/verify_ptcichina_zhan_2024.R` | **11** verbatim PTCI stems |
| `itemtables/batch_030/verify_esiason_2024_aaqii.R` | 1 (AAQ-II) |
| `itemtables/batch_041/verify_gomez_2022_qcae.R` | 1 (QCAE) |
| `itemtables/batch_236/verify_yang_2023_emotional_eating_uppsp.R` | 1 (UPPS-P) |

And one prose redaction: `fixes/issue_1618_pezzuti_big5_southkorea/README.md`
quoted the Korean BFI-10 Openness item to explain a misspelled SPSS column. The
explanation stands; the wording is now described instead of quoted.

## History is deliberately not rewritten

Ruled 2026-10-26. These files have been in public history since their batches
landed, so deleting them stops further distribution but does not unpublish
them. A rewrite cannot recall what is already cloned, and it would invalidate
the commit references that `tools/withdrawals/` provenance records cite. The
material is third-party instrument wording that also appears in the originating
papers, and the register's standing treatment of this class is to block the
wording and keep the table.

## The check that makes it unrepeatable

`itemtext/check_withdrawn_wording.py`, run by
`itemtext/tests/test_withdrawn_wording.py` in CI. Two tests, both of which
attribute wording to a table rather than guessing: by file name (with `verify_`
and `__items` stripped), and by a CSV's own `table` column where `item_text`
holds prose. The second is what caught the files whose names say nothing, and
its three-word floor is why `language_backfill/audit_2026-09-01.csv` is not
flagged -- that file stores verdict codes (`ADMIN`, `NEEDS_REVIEW`) in
`item_text`.

## Open, and not acted on

`--broad` reports every tracked file that both names a withdrawn table and
contains item-stem prose, with no attribution between the two: **45 files** on
2026-10-26. It is not a finding. Most are a file naming one withdrawn table
while quoting an item from another, and several quote licence correspondence
rather than items ("I hold the copyright to the BFI and it is not in the public
domain"). Deciding those needs a person reading each file against the
instrument, which is why CI does not run it and nothing here was deleted on its
say-so.
