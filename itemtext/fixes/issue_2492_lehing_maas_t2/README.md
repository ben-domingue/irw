# rvobgvmaas_lsf_lehing_2024: wave-1 reverse-keyed items (#2492)

`data/rvobgvmaas_lsf_lehing_2024.r` built the T2 reverse-keyed block with
`ends_with("t1")`, so the 11 reverse items' wave-1 rows were copies of wave 0
(2,024 of 2,024 identical). The script now selects `t2`.

**Response table, before → after** (source: PLOS ONE S2 File, `journal.pone.0316374.s002.xlsx`):

- rows 6,992 → 6,992, ids 184 → 184, items 27 → 38
- wave 0 byte-identical (id, item, resp)
- wave 1: the 2,024 reverse rows now carry `maas_<N>r_t2` with the study's T2
  answers (range 1-5, no NA) instead of `maas_<N>r_t1` copies
- irw-validate `--profile upload`: conforms, gate passes (three warnings, all
  already true of the live table)

**Item text.** `rvobgvmaas_lsf_lehing_2024__items.csv` here is the batch_530
upload (135 rows, from `itemtext/queue-rounds` commit 3f13a577) unchanged, plus
55 rows: each `maas_<N>r_t1` item's five option rows copied under
`maas_<N>r_t2`. It is the same questionnaire at a second time point, so the
wording is identical. Its item set equals the rebuilt table's exactly.

**Provenance `public_note`** (batch_530 row, on `itemtext/queue-rounds`).
Replace the sentence about the duplication with nothing. The note becomes:

> Items are shown in the administered German (Wittich et al. 2009) with
> Condon's original English alongside, which is the source instrument rather
> than a translation of the German.
