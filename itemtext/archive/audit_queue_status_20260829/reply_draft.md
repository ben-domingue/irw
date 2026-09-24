Subject: Re: the 13 audit_pending_review tables — my fault, that queue was already closed

Glad you're feeling better, and sorry — you spent that week on a queue I
should have retired. `audit_pending_review/` isn't live work. It's the input
to the item-text correction workstream, which finished and shipped as
`irw_text` v9.0 on 2026-08-25. The record is in `fixes/HANDOFF.md`: all 17
corrections resolved, every issue closed except #1598.

The directory names are what did it. There are three stages sitting side by
side, and nothing said which was which:

- `audit_staging/` — the 2026-08-12 pilot extractions. These were diagnostic
  evidence, the thing that *found* the defects. Never meant to be uploaded.
- `audit_pending_review/` — the diffs that turned each finding into an issue.
- `fixes/` — the corrected files that actually shipped. They're byte-identical
  to what `irw::irw_itemtext()` returns today, because they are what was
  released. Despite the name, they aren't proposals.

So when you opened the files, you were reading the finished output and
comparing it to write-ups that describe the diagnostic input. That's why the
details didn't line up — the "(paper coder scale N)" note is in the staging
extraction, not in what shipped; the bat/ball wording likewise.

Your four flags all trace to closed decisions:

1. **dumas_organisciak_2022** — #1598. The `instructions` field was added and
   uploaded. The 0-4 vs 1-5 point is real and it's documented in the file as a
   +1 shift. The issue stays open only on a separate question: whether that
   response table leaves IRW entirely.
2. **gilbert_meta_78** — #1607, closed by *removing* the table. It reproduces
   actual PPVT-4 target words, so this was a licensing call, not a data call.
   The 192-item version you were comparing against is pre-v9.0 and is gone on
   purpose.
3. **gilbert_meta_80** — #1606, same thing for WJ-III Picture Vocabulary.
4. **threat_isler_2024_exp4_cog_crt** — #1605, closed 2026-08-25. The option
   labels and correct_response for all three CRT items were verified against
   the study's own Qualtrics .qsf (OSF grafm, Experiment 4). You were right
   that the wording needed adjudicating; it had been, against the primary
   source.

Both of your "correctly left blank" calls were right, and for the right
reasons. `florida_twins_friends` was graded Yellow in the pilot — 19 of 21
items confirmed against the Florida Twin Project W1_Child codebook, with
friends20/friends21 undocumented and a website callout drafted.
`mpsycho_rogers_ocd` was graded Gray — item identity confirmed via the package
docs, but the specific self-report wording variant isn't confirmable from
public sources. Neither is a defect.

On your two suggestions. The check comparing a candidate against what's
published already exists and did its job — it's what produced these diffs in
the first place. What was missing is the other end: nothing retires a stage
once it's done. I've archived both directories under
`itemtext/archive_v9_correction_workstream/` with a README saying what each
was and that neither should be shipped, and put a pointer at the top of
`fixes/HANDOFF.md`.

Which is also why I'd hold off on automating the review queue for now.
Automation over directories that don't say whether they're live would have
produced this same week, just faster. Worth doing once each stage carries its
own status.

The only genuinely open item from your list is dumas (#1598), and that one is
a data-side call about removing the response table rather than anything to do
with item text.
