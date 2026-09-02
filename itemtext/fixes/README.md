# `fixes/` — archive, not a queue

**Nothing in this directory is pending upload.** It is the record of the item
text correction workstream, which completed and shipped. Files are kept for
provenance; deleted ones remain in git history.

Do **not** point `red_up` at this directory. It holds spot-check files, audit
reports and response data alongside item text; `red_up` would exclude the
non-`__items` files and say so, but it would still re-publish two tables that
were deliberately withdrawn.

## What is still here, and why

| file | status |
|---|---|
| `gilbert_meta_78__items.csv` | **Never uploaded — licensing.** Reproduces PPVT-4 target words (#1607). Commercial instrument. |
| `gilbert_meta_80__items.csv` | **Never uploaded — licensing.** Reproduces WJ-III Picture Vocabulary target words (#1606). |
| `dumas_organisciak_2022__items.csv` | Was uploaded, then the table was removed from IRW. Absent from `irw_text` as of v11.0. #1598 remains open. |
| `*_spotcheck.csv`, `audit_report.csv`, `itemtext_name_mismatches.csv` | Evidence, not item text tables. |
| `diffs_vs_published/` | Per-table audit diffs against what was live at correction time. |
| `*_NOTE.md`, `itemtext_issues_*.md`, `*.patch` | Notes and drafts for the issues page. |
| `HANDOFF.md` | Workstream history. **Stale in places** — it reports the corpus at v9.0 and says `gilbert_meta_35`'s table is being pulled; as of 2026-08-30 `current` is v11.0 and that table is live at 32 rows. |

The 15 corrected `__items.csv` that shipped were deleted 2026-08-30 once
confirmed live in `irw_text`, matching the convention in
`extraction_batches/round_log.md`: delete the item text file on upload
confirmation, keep the sidecars.

## Verifying a correction actually landed

`numRows` lies — it reported stale values throughout the 2026-08-24 duplication
incident. Query the table:

```sql
SELECT COUNT(*) AS n_rows, COUNT(DISTINCT item) AS n_items FROM <table>__items
```

Redivis uploads **append** — `replace_on_conflict` replaces an upload of the
same name, not rows inherited from the prior version — so the target table has
to be deleted from the draft before an existing table is re-uploaded. `red_up`
does this itself, and verifies the resulting row count with a `count(*)`.
