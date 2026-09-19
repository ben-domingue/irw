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
| 01 Tagging | `metadata/status.json` (tracked) | **Readable, not regenerable here** -- but no longer stale. Since #1940 (2026-09-08) `11_status.R` is stage 11 of the weekly pipeline, so it refreshes every Monday in the same run that writes its inputs. A render still cannot regenerate it; it can now trust that it is at most a week old, and `generated` says exactly how old. |
| 02 Item text | live Redivis `irw_text` **and `irw_text_2`** | **No.** Needs a Redivis read token, which the cloud environment does not have. Carry forward and age the stamp. |
| 03 Year 3 plan | GitHub issues/PRs (`#1702`) | **Yes.** |
| Commit counts | `git log` in this clone | **Yes.** |

## Item text lives in more than one dataset

Redivis caps a dataset at 1000 tables, so item text was split on 2026-09-05:
`irw_text` holds the first 718 tables and `irw_text_2` everything since. **Never
count against `irw_text` alone.** It is a third of the corpus' item text short
today and the shortfall grows with every batch, because new tables only ever go
to the newest shard. A count that reads one dataset does not fail -- it returns a
smaller number, which reads as item text having lost tables overnight.

The dataset list is `IRW_TEXT_DATASETS` in `metadata/redivis_config.R`, which is
authoritative (ARCHITECTURE.md section 5). Enumerate it rather than naming a
dataset here, so the next shard is picked up without editing this file:

    python3 - <<'EOF'
    from red_up.auth import authenticate
    from red_up.targets import load_registry, text_shards
    import redivis
    authenticate()
    owner, targets = load_registry()
    names = set()
    for shard in text_shards(targets):
        ds = redivis.user(owner).dataset(shard.name, version="current").get()
        names |= {t.name for t in ds.list_tables()}
    print(len(names))
    EOF

Two things to get right when turning that into a coverage figure. The shards hold
`<table>__items`, so strip the suffix before joining to the corpus; and the join
must be case-insensitive, or the ~300 tables whose names are not lowercase drop
out silently (#1704). On 2026-09-10 that was 1,055 item-text tables, 1,052 of
which matched a row in `metadata/metadata.csv`.

The rule for reconciling section 02 with `status.json`: section 02 is counted
directly against Redivis and `status.json` from the committed CSVs, so the two
drift apart between runs. Prefer the live figure and let its stamp age; adopt the
`status.json` figure only once it is the larger of the two, and say so in the
note. (Until 2026-09-08 `status.json` was the laggard by construction, reporting
13.5% / 558 against a page saying 14.0% / 579. It is now the fresher of the two
-- 17.8% / 755 -- which is the case that rule was written to handle.)

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
