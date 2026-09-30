# rmet_higgins_2022_rmet (item text) — rights

**Lead, as stated** (round_log.md L18285, 2026-09-11, banked at the audit pause):
"`rmet_higgins_2022_rmet` (live; the same ARC clause covers the Eyes Test)".

## What was checked independently

1. **The clause.** Autism Research Centre, downloadable-tests index,
   https://www.autismresearchcentre.com/research/tests/ (fetched 2026-09-29, sha256 b2aa5818…ab04a94; the
   register's AQ row recorded d4bc4a00… on 2026-09-11, so the page is not byte-stable):
   > "You can download them below provided that they are used for research purposes and not for commercial use,
   > and that due acknowledgement of ARC as the source is given. You may not adapt or modify any of these tests,
   > unless permission has been given by the Autism Research Centre."

   The same index lists **"Eyes Test (Adult)"** among the tests it governs. The test page
   https://www.autismresearchcentre.com/tests/eyes-test-adult/ (sha256 2fb7099e…3f288) cites Baron-Cohen et al.
   2001 and offers the Instructions and Parts 1–2 as downloads. It has no more permissive term. The clause is
   a stated non-commercial restriction plus a no-adaptation bar, so it falls under the #1891 rule. It is the
   same clause the AQ row already applies.
2. **What the table served.** Read `rmet_higgins_2022_rmet__items` from irw_text **v27.0** (148 rows). It holds
   37 items (R01–R36 plus RPrac), each with the ARC four-word option set (e.g. R01 "playful / irritated /
   comforting / bored"; RPrac "jealous / arrogant / panicked / hateful"). Every item carries the image placeholder
   "[pic: eyes looking into the camera]" and a near-verbatim copy of the ARC instructions. The option words are
   the test's verbal content, so this is ARC wording.
3. **Live status. It is no longer live.** Listing irw_text by version shows the table present in v10.0–v27.0 and
   **absent from v28.0, released 2026-09-29 14:04 UTC**. It is also absent from irw_text_2 and irw_text_3, both
   current and draft. Today's automated refresh of `live_tables.csv` (f5b8bfc8) dropped it.
4. **Where the removal is recorded.** Ben ruled "rmet: withdraw" on 2026-09-28 in the #2513 walk-through.
   **PR #2539** (open, not merged) has the three records: `tools/withdrawals/withdraw_rmet_itemtext_2026_09_28.py`,
   a new RMET row in the register, and a row in `withdrawals.csv`. On `origin/main`, none of the three exists yet.
   The withdrawal was released before its records landed.

## Verdict

The lead holds. The ARC clause covers the Eyes Test, and the table served its wording. The remedy has already
happened: Ben ruled it on 09-28 and it was released in irw_text v28.0. This audit has nothing new to do on the
table. The only thing owed is merging #2539 so that the ledger and register match Redivis. As with every
withdrawal, the text is still served at prior version tags (v10.0–v27.0).

- **proposed_outcome:** `no_action`. It was already withdrawn under the in-force ruling, and the bookkeeping
  sits in open PR #2539.
- **confidence:** high
- **group:** `rights:ARC` (with the AQ row; the other ARC tests, such as EQ, SQ and Faux Pas, have not been swept)
- **minutes:** ~25 · **redivis_reads:** rows:148 (v27.0), plus table listings over 3 shards and 34 irw_text versions

Side lead, not in this strand: PR #2540 applies the same ARC reading to option *words* stored in response-table
`resp_raw` (Wilmer RMET/MRMET). RULES §1 says "the response table itself is not at issue", and that PR shows the
statement does not hold when a response column stores the wording.
