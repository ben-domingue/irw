# What to work on

Set 2026-09-02 by ben-domingue. Advisory: he overrules it, and a direct request
always wins. This file exists so a session can place a new piece of work without
asking, not to override judgment.

**The problem it solves.** There are ~390 open issues, 207 of them labelled
`data queue`, and 17 roadmap items. A list that long does not tell anyone what
matters, and re-deriving a priority order every morning is itself the cost. So
this ranks *kinds* of work rather than listing issues, and the list below will
still be right when every issue number in it is closed.

**Where the issue list is.** Ranking without a way to *find* the ranked work is
half a tool, so as of 2026-09-06 the categories below exist as labels:
`p1-trust`, `p2-gate`, `p3-reach`, `p4-volume`, `p5-later`, one per open issue
across all three code repos. Two queries do most of the work:

- **`label:wrong-now`** — the narrow class from `ARCHITECTURE.md` §4: the
  released data would give a *wrong* answer, not merely an incomplete one. This
  is the one worth opening daily.
- **milestone `Queue: one-offs`** — self-contained fixes, one session or less
  each, no decision needed, no dependency on anything else. Pull from the top.

For *what to start next* rather than what exists, read **Project 4** filtered to
`Status: Todo`: its `Depends on` column carries the ordering, and the structural
issues with no roadmap number (#2001, #1955, #1342, #1942, #1856) are on it
alongside the seventeen items. The ordering deliberately lives there rather than
in a document — a work order written as prose is stale the week after it is
written, which is `ARCHITECTURE.md`'s rule 2.

`metadata/build_issue_triage.py` holds the assignment and
`metadata/apply_issue_labels.py` applies it, so the next pass edits a list instead
of re-reading 400 issues. Both are idempotent; the CSV between them is a derived
artifact and is not committed.
`data queue` issues are deliberately unlabelled — acquisition is not-now as a
*class*, and 207 identical labels would say nothing.

## The order

**1. Corpus trust — the warehouse is serving something wrong.**

Outranks everything. The distinguishing question is not "is this broken" but
"is a user getting a wrong answer right now". A missing table means the corpus
is *incomplete*; a doubled table, a `cov_age` of 1999, an item text that is not
what respondents read all mean it is *wrong*, and wrong is worse than incomplete
at any size.

This is the same distinction the draft-release policy turns on (`ARCHITECTURE.md`
§4): a late addition may wait a week, a late correction may not.

**2. Gates — stop the class, not the instance.**

Work that prevents a defect recurring beats work that fixes one occurrence of
it, even when the occurrence is louder. Roadmap item 1 (#1703) is the type case:
the same Redivis append bug was found and fixed three separate times in whichever
copy of the uploader was in hand, while the other twelve copies stayed broken.

The test for whether something belongs here: if you fix the instance and nothing
changes about how the next one is caught, it was category 1 work, not category 2.

**3. Reach — items 4 and 5, and the gate on them is gone.**

Reworked 2026-09-03. **Item 6 is retired**: its intent was user-contributed
vignettes, which never materialised. Its one live sub-action — give the
dictionary the same write path as tags (#1732) — was promoted to item 6b and
shipped on 2026-09-06 (PR #2000).

**Correction, 2026-09-06.** This section used to postpone items 4 (findability)
and 5 (the packages) behind item 3, the version manifest, on the grounds that a
landing page which cannot name its version is indexed against data that moves and
that the package cache worth having (5.5) is keyed by table *and* version. Both
arguments were right and **item 3 closed on 2026-09-03** (#1705). The
postponement therefore has no reason left. The standing answer to the export cap
— **manifest → cache → quota relief** — is now one built step and two unbuilt
ones, not three unbuilt ones.

This category still receives no time. That was defensible while item 3 gated it
and is not defensible now, which makes it the strongest argument for raising it.

**4. Volume — coverage of tags and item text.**

Item text is at ~14% of tables and tags at ~55% per column — quote
`metadata/status.json` **per column**, never the row-coverage headline, which is
carried by derived `age range` rows and reads ~75%. This is where effort actually
goes — 484 file-touches in `itemtext/` in the week to 2026-09-02, against 100 in
`tags/` and 56 in `metadata/` — so the point of ranking it fourth is not to stop
it but to stop it crowding out 1–3 by default.

**Volume means the untagged and the unextracted** (ruled 2026-09-03): tagging
tables that have no tags (1,427 reachable) and extracting item text for tables
that have none (1,164 queued). It does *not* mean improving tags or item text
that already exist. Corrections are worth making insofar as they fall out of
building a good automated tagger or extractor; a standing workstream of small
fixes to published rows is the thing that has been crowding out the goal.

This is an ordering *within* item 4 and does not lift volume above corpus trust.
A wrong table still beats a missing tag.

**5. Not now.** Say so rather than quietly deferring:

- The blue-sky roadmap items (8–15). Three were picked as worth eventual
  investment — 8 (a derived-parameter layer), 11 (an MCP server), 9 (tasks and a
  leaderboard) — and none is this year's work until 1–7 are further along.
- New vignettes, per item 16's stop-doing list.
- Any acquisition *sprint*. **Correction, 2026-09-03**: this bullet used to say
  "intake has already stopped on its own". That is true of the GitHub `data
  queue` issues — the newest is 2026-08-11 — but **not** of the automated
  connectors, which produced 58 PLOS candidates on 2026-09-01 and 60 PMC
  candidates on 2026-09-02. The corpus grew by roughly 500 tables a fortnight
  through the connectors in late August, which is what drove tag coverage down
  six points while tagged tables rose.

  **That growth is accepted and is not to be managed** (ruled 2026-09-03). The
  connectors keep running; coverage percentages get diluted by new tables; report
  absolute progress alongside the percentage rather than trying to hold the
  denominator still. What stays out of scope is a deliberate *sprint* on
  acquisition. `CLAUDE.md` says it directly — "the goal is not to empty the queue
  — it's to maximize data in the IRW."

## What the ranking assumes

It only holds under the scoping choices made when the Year 3 roadmap was written
(#1702, 2026-08-29). If any of these change, re-rank:

| | |
|---|---|
| Horizon | Grant Year 3, May 2026 – April 2027 (IES R305D240025) |
| Labour | Claude Code agents plus RAs — explicitly *not* a hired engineer, so nothing requiring a hosted backend |
| Lenses | Corpus trust, reach, community self-sustainability |

The lens deliberately **not** chosen was "research output from the data", which is
where effort had been going. That omission is the reason items 8–15 rank where
they do; it is a choice, not an oversight.

## Where the detail lives

This file ranks; it does not enumerate. For the actual work:

- **The 17 numbered proposals and their sub-items** — ben-domingue/irw#1702, and
  one issue per item at #1703–#1719. Check there before starting anything in a
  numbered area; several already carry a ruling. Items 2, 3 and 6 are closed;
  items 8–10 and 12–15 and 17 are marked `Deferred` on Project 4 and have no
  attached issues, which is what not-this-year looks like on the board.
- **Which issues are in a category** — the `p1`–`p5` labels, and
  `metadata/build_issue_triage.py`, which assigns them. That script is the
  enumeration this file refuses to be.
- **Which dataset to process next** — `CLAUDE.md` §Processing Priorities and
  `processing_notes/DataProcessingInstructions.md`. Different question, different
  answer: that is about picking among candidates, this is about picking among
  *kinds of work*.
- **Which document wins when two disagree** — `ARCHITECTURE.md` §5.
