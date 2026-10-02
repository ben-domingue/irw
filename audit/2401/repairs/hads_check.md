# jablonska_2020_hads: are the item codes the HADS? (irw#2401, round 3)

Ben's round-3 decision: if the 14 codes are the licensed HADS wording, recode them to
`hads_1`-`hads_14`; if they are a paraphrase, leave them. No item wording is reproduced here.

## Verdict: they are the HADS. Recoded.

## Evidence

- **The paper says so.** Measures section: anxiety and depression were assessed using
  the 14-item Hospital Anxiety and Depression Scale (Zigmond & Snaith 1983, ref. 42),
  alpha = 0.81. The only change it reports is to the response format: every scale was
  moved to a 7-point agree/disagree Likert scale. The questionnaire (S3 Appendix) is
  in English and Polish. The sample is Polish women.
- **The register's reference text did not help.** Its `match_item_text` is one German
  HADS-D stem (item A1), so it cannot be matched against English headers. The
  register notes say that translations are covered ("in all languages").
- **In-script comparison.** Each source header was compared, inside a script, with short content keys (4 words or fewer) for each
  HADS item in its published order. Nothing was printed except codes and scores.
  - Source columns 36-49 follow the HADS order one-to-one, and no column matches a
    different item better.
  - Key share by column (36 to 49): 1/3, 4/4, 1/4, 4/4, 1/4, 0/1, 2/3, 0/2, 2/3, 1/3,
    1/2, 2/4, 1/2, 3/4. Overall that is 23/43 = 0.53.
  - Four items are near-verbatim: 2, 4, 9 and 14. The HADS's distinctive idioms survive
    in items 4, 9, 12, 13 and 14.
  - The rest carry the same item content, reworded. The reworded headers read like an
    English rendering of the Polish HADS.
- **Why the rewording still counts.** An English rendering of a translated HADS is a
  derivative of the licensed text. That is the same standard already applied to the
  SWLS codes in this same file ("English renderings of the SWLS", rights_translated.md).

## Recode

- **Mapping:** source column 36+k-1 becomes `hads_k`, for k = 1..14. This is the identity
  in published order, so no reordering was needed.
- **Staged file:** `/home/ben/irw-stage/2401-audit/rights_recode/jablonska_2020_hads.csv`
  holds 13,636 rows, 974 ids, 14 items and resp 1-7.
- **Checked against live:** `item_response_warehouse_3`, version="current", queried with
  an aggregate query. Every live item maps to a code. For all 14 items, the per-item count
  (974) and sum match. Totals match too: 13,636 rows and 974 ids.
- **Validation:** `irw_validate.cli --profile upload` reports that the file conforms and
  the gate passes. Its one WARN is `rights_register`: the new codes match `^hads`. That is
  expected, because the codes are no longer wording.
- **Script:** the `_ship` call in `data/jablonska_2020_instagram.py` now passes
  `codes=`, as the SWLS call does.
- **table_changes:** a row was appended to `rights_recode_table_changes.csv`.
- **Not done:** no upload was made.

## Item text

`jablonska_2020_hads` has **no** live item text: it is not in
`metadata/itemtext_metadata.csv`. The availability audit marked it UNAVAILABLE
(copyrighted). No item-text withdrawal is needed.
