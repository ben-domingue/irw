# `audit_pending_review/` is a resolved queue — do not sign off on it

Generated 2026-08-29, replacing an earlier draft of this file that got the
framing wrong.

## What these 13 tables actually are

`audit_pending_review/*_diff.md` are the **inputs** to the item-text correction
workstream — the diffs produced by the batch-01 audit pilot on **2026-08-12**.
That workstream **completed and shipped as `irw_text` v9.0 on 2026-08-25**. See
`fixes/HANDOFF.md`, which records all 17 corrections as resolved and all issues
closed except #1598.

The three directories are three stages of finished work, not competing drafts:

| Path | Stage |
|---|---|
| `audit_staging/<table>__items.csv` | The 2026-08-12 fresh extraction — **diagnostic evidence** that found the defects. Never intended for upload. |
| `audit_pending_review/<table>_diff.md` | The diff that turned each finding into a GitHub issue. |
| `fixes/<table>__items.csv` | The corrected file that was **uploaded and released in v9.0**. Byte-identical to `irw::irw_itemtext()` today, because it *is* what shipped. |

So a reviewer asked to sign off on the queue is being asked to re-decide
questions that were closed two weeks ago, against staging files that were only
ever meant to demonstrate the problem.

## Every flag raised in the last review round is already resolved

| Flag | Resolution |
|---|---|
| `dumas_organisciak_2022` — 0–4 vs 1–5, missing `(paper coder scale N)` | #1598. `instructions` added and uploaded. The issue stays open only on a separate decision: whether the *response table* is removed from IRW entirely. |
| `gilbert_meta_78` — "missing 3 items" | #1607, **closed by removing the table**. It reproduces actual PPVT-4 target words. Commercial instrument — a **licensing** call, not a data call. It must not be re-added. |
| `gilbert_meta_80` — "missing 8 items" | #1606, same, WJ-III Picture Vocabulary. |
| `threat_isler_2024_exp4_cog_crt` — CRT1 wording, missing option labels | #1605, **closed 2026-08-25**. `option_text` for all three items and `correct_response` were verified against the study's own Qualtrics `.qsf` (OSF `grafm`, Experiment 4). Already adjudicated against the primary source. |
| `florida_twins_friends` — "correctly left blank" | Correct. Graded Yellow in the pilot: 19/21 items confirmed against the Florida Twin Project W1_Child codebook, `friends20`/`friends21` undocumented. Curation kept, website callout drafted. |
| `mpsycho_rogers_ocd` — "correctly left blank" | Correct. Graded Gray: item identity confirmed via package docs, the specific self-report wording variant is not confirmable from public sources. Not evidence of a defect. |

## Still genuinely open

Only `dumas_organisciak_2022` (#1598), and it is a data-side question about
removing the response table — not an item-text question.

## The one real process gap

`audit_pending_review/` and `audit_staging/` were left on disk after the
workstream closed, with nothing marking them as spent. Their filenames read as
a live queue. A reviewer with no other context reasonably concluded there were
13 tables awaiting sign-off, and reviewed `fixes/` — the shipped output —
believing it was the proposal.

The fix is retirement, not another validation gate: archive both directories,
or add a status line to each pointing at `fixes/HANDOFF.md`. The two existing
published-comparison reports also disagree with each other
(`gilbert_meta_78` scores item_text similarity 1.0 in `fixes/diffs_vs_published/`
and 0.0 in `audit_pending_review/`) purely because they read different stages
of the same finished pipeline — which is harmless once the stages are labeled.
