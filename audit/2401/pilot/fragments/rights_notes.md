# Rights strand: notes on RULES.md from the pilot (3 tables)

## Where RULES was ambiguous or didn't fit

1. **"Already remedied" has no outcome code.** Two of the three leads (RMET, cormier) had already been withdrawn
   and released before the audit reached them. I used `no_action`, but RULES defines that code as "checked,
   nothing wrong", and something *was* wrong. It was fixed under an in-force ruling. Proposal: add
   `already_done` (or `no_action` with a required `remedied_by` pointer) so the worklist doesn't imply a clean
   table.
2. **Records can lag Redivis.** The RMET withdrawal was released in irw_text v28.0 on 2026-09-29, the freeze date.
   Its ledger row, register row and script exist only in open PR #2539. RULES says the register "as of the freeze
   date" governs, so it is unclear whether a register row in an unmerged PR counts. I treated a ruling Ben had
   made (09-28) as in force. Proposal: the freeze covers *rulings made*, whether or not their bookkeeping has
   merged.
3. **"Live" moves under you.** `live_tables.csv` in my checkout (09-28) listed RMET as published. It had been
   removed ~4 hours earlier. RULES should say that "live" means the current Redivis version tag, read at review
   time, and that the tag (e.g. `irw_text v28.0`) goes in the dossier.
4. **Prior version tags still serve withdrawn wording.** RMET is readable at v10.0–v27.0 and cormier at
   v16.0–v20.0. Every withdrawal so far accepts this. RULES should state that "withdrawn" means "not in the current
   version", so that no reviewer re-opens it.
5. **One outcome per finding, one row per table.** beck_2021_iesr has two wording layers with different rights
   positions. The English `*_translated` column is Weiss verbatim, so a partial `withdraw` at high confidence.
   The German `item_text` depends on policy (`needs_ruling`). I had to collapse both into one row. Proposal:
   allow a row per wording layer (`table#column`), or a `partial:` qualifier on the outcome.
6. **Language backfill is its own rights surface.** beck was cleared (implicitly) on its German source. The
   2026-09-01 backfill then added the rights holder's *English* original as `official_instrument_english`.
   Any table whose source is a translation may have gained originator wording this way. RULES §1 names wording but
   not which columns. It should say that all text columns are in scope, including `*_translated`.
7. **"Response table not at issue" is not always true.** PR #2540 (Wilmer RMET/MRMET) found ARC option words
   stored in response-table `resp_raw`. The register's `match_item_code` column also exists because item codes
   can carry wording (luu_2024_stai6, holden_2026_bsri). RULES §1 should read: "not at issue unless a response
   column stores the wording".
8. **A scoped grant is neither silence nor restriction.** UZH says the German IES-R "can be freely used in research
   and clinical practice". The text has no "only" and no NC. #1897 (silence) and HEXACO/#1891 (stated restriction)
   don't cleanly decide a positive grant with an enumerated purpose. This needs a ruling that covers the class,
   not just beck.
9. **Translator versus originator.** The register's IES-R row covers "translations/derivatives" based on Weiss's
   third-party-reported refusal. The German holder's own free-use statement then conflicts with it. The 09-08
   originator ruling points one way. Ben's 09-11 instruction ("research that rights holder's terms before
   deciding") points the other. This belongs in one decision, together with ali_2021_iesr (same group, its partial
   withdrawal still owed).
10. **Evidence-bar wording.** "Quote the clause and give its URL" works for a block. For a *permissive* finding
    (UZH) or a silence finding, the dossier should also give the hash and a Wayback capture, since a grant can
    later be withdrawn. I did this, but RULES only asks for it on changed pages.
11. **Hashes aren't stable.** The ARC index hashed differently today (b2aa5818…) than on 09-11 (d4bc4a00…) while
    the clause text was unchanged. Berkeley's hash was identical. Hash comparison should fall back to a clause-text
    comparison, and not flag a change on a hash mismatch alone.

## What can be scripted

- **Live presence by version.** List every text shard at each version tag. Report first/last version carrying the
  table and whether it's in the current tag. I did this ad hoc in ~20 lines. It should be one helper that
  outputs the tag.
- **Record consistency.** Cross-check current Redivis against `withdrawals.csv` (ledger row present, `released`
  filled) and against open PRs touching the ledger. This would have caught both the RMET "released without record"
  and the cormier blank `released` cell.
- **Clause re-fetch.** Fetch each register `source_url`, confirm the quoted clause text is still present, and
  record hash plus Wayback. Mechanical, except for Cloudflare-blocked hosts.
- **Wording match.** Match register `match_item_text` stems against *all* text columns, `*_translated` included.
  `sweep_instrument_rights.py` checks only `item_text`, so it would miss beck's English layer. It also doesn't use
  item codes on the text side. cormier's Q20_n codes show that code patterns alone miss tables.
- **Backfill exposure query.** List tables whose backfill text_source is `official_instrument_english`, joined to
  the register families. This is a candidate list for item 6 above.

## What needs a human ruling

- Whether a scoped positive grant ("free for research and clinical practice") counts as a restriction (item 8).
- Whether an originator's block reaches a translation whose translator publishes it freely (item 9). This decides
  beck and part of ali_2021_iesr.
- Whether the audit adds an `already_done` code, and whether unmerged-PR rulings count at the freeze (items 1–2).
- Whether option words and other wording stored in response columns are in scope for this audit (item 7).
