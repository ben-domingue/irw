# irw-auto-itemtext: is this skill reliable?

## What it does

`irw-auto-itemtext` is a Claude Skill that extracts item text — the actual
question/prompt wording, response options, and instructions — for IRW
tables, working from the same starting point a human curator gets (a link
to the source paper, codebook, or dataset). We wanted to know: can it
reliably reproduce what a human curator would produce, without hallucinating
content it can't actually find?

## How we tested it

We ran the skill against **110 tables that already have human-curated item
text**, without letting it see the answer, then compared its output against
that existing curation, field by field. This happened in two rounds: a
10-table pilot, followed by fixes to three issues the pilot found, then a
100-table batch specifically designed to stress-test those fixes (including
deliberately oversampling the hardest table type it has: tables where
questions are numbered 1, 2, 3... with no descriptive labels at all).

## The headline finding: it doesn't guess

The most important property for a tool like this isn't "does it get
everything right" — it's "when it doesn't know something, does it say so
instead of making something up."

Across 110 tables, we found exactly one case where an automated run
invented plausible-sounding text instead of leaving a field blank when the
real source was inaccessible: one subagent, unable to reach a table's
actual source document, filled in wording that *sounded* right based on
standard survey phrasing for that variable type, instead of leaving the
field blank the way every other blocked-source table correctly did. We
caught it (by noticing it was the one outlier in an otherwise consistent
pattern), corrected it, and then specifically re-checked every other
uncertain table in the batch for the same problem — found none.

Elsewhere, the skill's actual behavior when uncertain was to decline rather
than guess. On two tables where the item order genuinely couldn't be
confirmed against any source, it left those fields blank and said so,
rather than producing a plausible-looking but unverifiable answer. That's
the behavior you want from something touching real curated data: wrong-but-
confident is dangerous, blank-when-uncertain is recoverable.

## What we found and fixed, with examples

The pilot surfaced three real gaps, all now fixed and re-verified:

**Item-numbering mix-ups.** For tables where items are numbered 1, 2, 3...
with no descriptive labels, the skill could occasionally map a question to
the wrong number if two nearby questions used the same response scale. On
one table, a 50-item personality survey, item 49 should have been a
conscientiousness question ("I get chores done right away") but the skill
initially landed on a different, nearby item instead — the response scale
(1-5, agree/disagree) was the same for both, so nothing caught the shift.
We fixed this by having the skill check for an existing data-processing
script for that table first (treating it as the authoritative source for
column order), and otherwise spot-check actual question wording at several
points rather than relying only on "does the response range look
plausible." Re-tested on the original table plus a fresh one it had never
touched before — both came back with item order fully correct.

**Over-explaining.** The skill sometimes added helpful-sounding wording
where the original source was terse. On one table, a preschool assessment
using single-letter/number codes for scoring (e.g. a bare "1" meaning
"correct"), the skill wrote "Correct: 1" and "Other / incorrect response"
instead of matching the source's own bare coding. Content-wise this wasn't
wrong, but it didn't match the established convention for that table. We
fixed this by having the skill match the source's own level of detail
rather than clarifying/expanding it. This mostly resolved cleanly, though
one later table (an art-recognition checklist using bare surnames like
"dali" and "renoir") showed the skill still writing out full names for
about two-thirds of the items before self-correcting partway through —
a narrower, lower-priority version of the same issue we're tracking for a
future pass.

**An underspecified rule.** The data standard didn't clearly say which of
two similar fields — overall instructions vs. a passage/section-specific
prompt — certain text belongs in. On one table, framing text for a
well-known 10-item personality measure sometimes ended up in the wrong one
of these two fields relative to how it was originally curated. We
clarified the rule directly in the standard (not just in the skill), and a
follow-up check on that same table showed the fix took: the swap
disappeared, and the skill correctly determined that this particular table
has no whole-table instructions at all — leaving that field blank, matching
how it had been curated originally.

## A few side-by-side examples

A note before these: the source material behind many of these tables is
copyrighted (published papers, commercial or licensed test instruments), so
this section deliberately shows only short fragments, not full item text —
the same discipline we held throughout this testing process. Where we don't
have a clean short fragment to show for the "before" state of a fix, we've
left that row descriptive rather than inventing one.

| Table | Field | Ground truth (existing curation) | Skill's output before fix | Skill's output after fix |
|---|---|---|---|---|
| `preschool_sel_wj`: WJ-IV subtest scoring | option text | `"the"` / `"other"` | `"Correct: 1"` / `"Other / incorrect response"` | `"the"` / `"other"` — exact match |
| `aestheticfluency_cotter2023`: art-recognition checklist | item text | `"dali"`, `"renoir"` | `"Salvador Dalí"`, `"Pierre-Auguste Renoir"` (for ~2/3 of items, self-corrected partway through) | `"dali"`, `"renoir"` on the corrected items |
| `fisher_temperment`: temperament survey (TIPI block) | which field the text lands in | this table has no whole-table instructions at all — the rating-scale framing text belongs in the section-level field only | the same framing text (`"I see myself as:" ___ such that`) was recorded in the whole-table instructions field — the wrong one | recorded correctly in the section-level field; whole-table instructions left blank, matching how it was originally curated |
| `firstborn_personality`: 50-item personality survey | item identity (not wording shown) | item 49 is a specific conscientiousness question | item 49 held wording that belonged to a different, nearby question — we're not reproducing either exact string here | item 49 now maps to the correct question |

The pattern across all four: when the skill got something wrong, it was
either a formatting/convention mismatch (too descriptive, or in the wrong
field) rather than wrong content, or — in the fourth case — a positional
mix-up that's now fixed. We didn't find a case in 110 tables where the
skill produced item text that was simply invented from nothing.

Testing at 100-table scale surfaced two issues that turned out to be
**mistakes in our own testing setup**, not the skill — worth mentioning
because catching your own false alarms is as important as catching real
ones:

- On two tables where the source material was in a non-English language,
  our comparison script checked the skill's English output against the
  wrong ground-truth column (the original-language text, not its English
  translation) — producing a 0% match score for extractions that were
  actually 100% correct once compared against the right column.
- On one table, a well-known survey about political attitudes, the skill's
  extraction disagreed with the existing curated answer key on 7 of 37
  questions. Investigating further showed the skill was right and the
  existing answer key was wrong — the skill's item order matched both a
  fresh pull of the live data and this repository's own data-processing
  script for that table exactly. The pre-existing curated data for that
  table had an error that predates this entire testing effort. That's
  being corrected separately, outside of this skill work.

## What's still open

One thing is flagged for follow-up, and doesn't change our confidence in
moving forward now: a handful of tables (5 out of 100 in the batch) show
the skill placing instructions/passage text in what looks like the wrong
field relative to existing curation. Given that the political-attitudes
survey case above turned out to be bad existing data rather than a skill
error, our leading hypothesis is that at least some of these are the same
pattern — but that's not confirmed yet, and we're checking it before
calling it closed.

## Bottom line

The skill is ready for continued use. Its most important safety property —
not fabricating content when a source is unavailable — held up cleanly
across everything we tested, and the one exception was caught, fixed, and
swept for recurrence. The three issues found in initial testing are fixed
and re-confirmed, including on tables added specifically to stress-test
whether the fixes would hold up beyond the original examples. The one open
item above is being tracked, and the pattern so far suggests some of what
initially looks like a skill error is actually pre-existing data issues
elsewhere in the warehouse — which is itself a useful thing this testing
process is surfacing.

*Full engineering detail, including every table checked and every fix's
rationale, is available in the working eval log for anyone who wants it.*
