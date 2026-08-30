# Archived — item-text correction workstream (closed 2026-08-25)

**Nothing in here is a pending queue.** These are the working files of the
correction workstream that shipped as `irw_text` **v9.0** on 2026-08-25. All 17
corrections are resolved and every issue is closed except **#1598**. The
authoritative record is `../fixes/HANDOFF.md`.

Archived 2026-08-29 after the directory names — `audit_pending_review`,
`audit_staging` — were read as live work and a reviewer spent a week
re-deciding closed questions. Findings:
`../audit_queue_status_20260829/README.md`.

## What each stage was

| Directory | Stage | Status |
|---|---|---|
| `audit_pending_review/` | The 2026-08-12 batch-01 audit diffs. Each became a GitHub issue. | Spent — all issues closed except #1598. |
| `audit_staging/` | The 2026-08-12 fresh extractions that produced those diffs. **Diagnostic evidence only.** | Never intended for upload. Do not ship these files. |

The corrected files that actually shipped are `../fixes/*__items.csv`. They are
byte-identical to `irw::irw_itemtext()` output today, because they are what was
released.

## `audit_staging/` is deliberately left untracked

It is on disk but **not committed**. `gilbert_meta_80__items.csv` carries all 36
WJ-III Picture Vocabulary target words in `correct_response`, and
`gilbert_meta_78__items.csv` is the PPVT-4 table. This repo is public, and #1606
/ #1607 removed exactly this content from the release on licensing grounds —
committing the diagnostic copies would republish it. Keep it local; do not
`git add` this directory.

## Two things not to re-open from here

- **`gilbert_meta_78` / `gilbert_meta_80`** were removed under #1607 / #1606 as a
  **licensing** decision — they reproduce actual PPVT-4 and WJ-III Picture
  Vocabulary target words. Their absence from the release is not a gap to fill.
- **`political_psychology`** was removed under #1594 (item-to-text mapping
  unverifiable). Reopen that issue rather than rebuilding from these files.
