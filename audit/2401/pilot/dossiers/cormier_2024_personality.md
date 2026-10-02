# cormier_2024_personality (item text) — rights

**Lead, as stated** (round_log.md ~L16500–16515): "The BFI-2 block reaches four LIVE tables — an irw#1954
re-audit lead" (cormier_2024_personality is one of them. It shipped 2026-09-04 because the Colby page was
Cloudflare-blocked and "no clause could be quoted".)

## What was checked independently

1. **The clause.** Re-fetched https://www.ocf.berkeley.edu/~johnlab/bfi.html on 2026-09-29. It was 13,537 bytes
   with sha256 281322e0…a9499, which is byte-identical to the hash in `tools/withdrawals/withdraw_bfi2.py`. Both
   sentences are present:
   > "Christopher J. Soto and I hold the copyright to the BFI-2 and it is not in the public domain per se. However,
   > it is freely available for researchers to use for non-commercial research purposes."
   > "At this time, the BFI-2 is for non-commercial uses only."

   This is a stated non-commercial restriction, so it blocks under #1891. Register row `BFI-2` has verdict
   `block` and was ruled by Ben on 2026-09-10.
2. **The wording.** Read the table from irw_text **v20.0**, the last version that carried it (80 rows). It has 16
   items, Q20_1..Q20_16, with instrument "Big Five Inventory-2 Extra-Short Form (BFI-2-XS), with one embedded
   attention-check item". Fifteen are BFI-2-XS stems (e.g. "tends to be quiet", "is compassionate, has a soft
   heart", "tends to be disorganized"). Q20_8 is an attention check. It is the BFI-2, not the BFI-44. The
   register's code pattern `^BFI…|^bfi2` does **not** match Q20_n, so only a wording read finds this table.
3. **Live status.** The table is present in irw_text v16.0–v20.0 and **absent from v21.0 (released 2026-09-10)
   onward**, including current v28.0. It is absent from irw_text_2 and irw_text_3, current and draft. It is not in
   `live_tables.csv` (2026-09-28/29).
4. **Ledger.** `itemtext/withdrawals.csv` has `cormier_2024_personality__items,irw_text,whole,2026-09-10,rights,
   BFI-2,#1954,…,tools/withdrawals/withdraw_bfi2.py`. Its `released` cell is blank, although Redivis shows the
   release was v21.0.

## Verdict

The lead is stale. The table was withdrawn under the BFI-2 row on 2026-09-10 and the withdrawal was released in
irw_text v21.0. The clause still holds today, verbatim and with an unchanged hash. The live corpus no longer
carries this wording. As with every withdrawal, it is still served at prior version tags (v16.0–v20.0).

- **proposed_outcome:** `no_action`. Optional bookkeeping: fill `released=v21.0` on the ledger row.
- **confidence:** high
- **group:** `rights:BFI-2`
- **minutes:** ~12 · **redivis_reads:** rows:80 (v20.0), plus version listings

Open, and outside this table: the withdraw_bfi2.py docstring records that Ben ruled *against* a full-corpus BFI-2
wording sweep on 2026-09-10. Exposure outside the sun_2025/cormier families is therefore unestablished, and the
code pattern would miss any table keyed like Q20_n. The `rights:BFI-2` group should hold a wording sweep (the
register's `match_item_text` stems) rather than this one table.
