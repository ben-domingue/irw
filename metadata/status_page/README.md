# The morning status render

`irw-status.html` is the source of the **"Where IRW Stands"** artifact:

    https://claude.ai/code/artifact/0ff3eca2-3ddd-4470-a87d-fc69db787903

A scheduled cloud agent re-renders it every morning. This file is the contract
that render follows. It is written for an agent that starts with *zero* context.

## The rule that matters

**Never write a number this repo cannot show you.** If a figure's source is not
reachable from a clone, carry the last published value forward *unchanged* and
age its freshness stamp. Do not estimate, extrapolate, or infer a number from the
direction of travel. A page that looks fresh while resting on week-old inputs is
the failure this design exists to prevent -- it is the same class of mistake as
reading tag coverage as 75% when seven of eight columns sit at 55%.

## What each section rests on, and whether a render can refresh it

| Section | Source | Refreshable in the cloud? |
|---|---|---|
| 01 Tagging | `metadata/status.json` (tracked) | **Readable, not regenerable.** Its inputs (`metadata/*.csv`) are gitignored. It only moves when Ben runs `metadata/11_status.R` locally and commits. |
| 02 Item text | live Redivis `irw_text` v14.0 | **No.** Needs a Redivis read token, which the cloud environment does not have. Carry forward and age the stamp. |
| 03 Year 3 plan | GitHub issues/PRs (`#1702`) | **Yes.** |
| Commit counts | `git log` in this clone | **Yes.** |

`status.json` currently reports item text at 13.5% / 558 tables while the page
says 14.0% / 579. That is not a bug: section 02 was last counted directly against
Redivis, ahead of the last local `11_status.R` run. Prefer the live figure and
let its stamp age; adopt the `status.json` figure only once it is the larger of
the two, and say so in the note.

## What the render does each morning

1. **Read** the published artifact at the URL above. Build the update from *that*
   HTML, not from this file, which may lag the live page. This file is the
   fallback if the read fails.
2. **Refresh what is refreshable** -- section 03's table, the PR counts and ages,
   and the seven-day commit counts in the section 02 tension box:

       git log --since=7.days --oneline -- itemtext/ | wc -l
       git log --since=7.days --oneline -- tags/ | wc -l
       gh pr list --repo ben-domingue/irw --state open --json number,createdAt,reviews
       # if gh is unauthenticated, the public REST API works: repos/ben-domingue/irw/pulls

3. **Re-read `metadata/status.json`.** If its `generated` timestamp is newer than
   what the live page shows, update section 01's meters, the shard stats, and the
   `n_tables` denominator throughout. If it is not newer, change no number there.
4. **Re-stamp every `.fresh` strip.** Each carries the source, the date that
   source was last measured, and an age chip. Age classes:
   `live` (0-2 days), `aging` (3-6), `stale` (7+). Update the masthead's
   "rendered <date>" line every morning regardless.
5. **Prose only on movement.** The verdicts and the `.tension` paragraphs are
   arguments, not readouts. Rewrite one only when a number it rests on has moved
   enough to change what it claims -- a coverage column crossing a round point, an
   item changing status, a PR backlog clearing. On a quiet morning the prose is
   left *exactly* as it stands. Churning it daily is a defect, not freshness.
6. **Publish to the same URL** so the link stays stable, and keep the favicon.

## Editing the page by hand

Edit `irw-status.html` here, publish it to the same artifact URL, and commit. The
next morning's render will read the published version, so a hand edit survives.
