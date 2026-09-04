# concretewords — parked, NOT for upload (batch_016, 2026-09-03)

**SUPERSEDED 2026-09-04 by the fix for issue #1876.** `data/concretewords.R` now sets
`item <- x$Expression` and `id <- x$Participant`, which is the right way round. Once the
corrected table is re-derived and uploaded, this parked file must **not** be promoted:
its item axis is the old, wrong one. See "What survives the fix" below.

## Why it was parked

`concretewords__items.PARKED.csv` (9155 rows = 1831 items x 5 resp) was built and
gated but deliberately **not** promoted to `itemtables/batch_016/`.

Reason: the IRW `item` axis was the **rater**, not the rated expression.
`data/concretewords.R` set `item <- x$Participant` and `id <- x$Expression`, and all
1831 live item values match the Qualtrics ResponseID pattern `^R_[A-Za-z0-9]{15,17}$`
with zero containing a space — impossible for a corpus of 62,000 English *multiword*
expressions. So `item_text` was blank for every row and no future pass could fill it: an
anonymous respondent ID has no stem.

By the #1770 test ("does a row we ship carry the item's referent?") the answer was no for
every row, so shipping it would have made `concretewords` count as "has item text" in the
corpus figures while carrying no item-level information at all.

## What survives the fix

The three shared fields are unchanged by the axis swap and can be reused verbatim when
the items CSV is regenerated:

- `instructions` — verbatim from OSF `ksypa` / *Multiword expression rating instructions
  Final.docx* (the only file at that node's root).
- `option_text` — `1 = Abstract (language based)`, `5 = Concrete (experience based)`;
  2–4 are unlabelled in the source and are left blank, not padded with their own number.
- `instrument` — Muraki, Abdalla, Brysbaert & Pexman (2023), *Behavior Research Methods*
  55(5):2522–2531.

What does **not** survive is the item axis itself. After the fix each `item` value is the
rated expression, so the item code carries its own wording and `item_text` is the
expression — the same self-describing pattern as `kushnir2017_anrt`. The regenerated file
is one row per (expression, resp level) rather than the 1831 x 5 here.

Regenerating it needs `Ratings_RawData.csv`, which is not cached in this repo, and it
should not be built until the corrected table has actually been uploaded — the item set
has to match what ships.

Also of note: the source's rating scale had a sixth option, "I don't know the meaning of
this expression"; `data/concretewords.R` drops it (`x$Rating %in% 1:5`, plus `x$Filter==1`).
That is unchanged by the fix.

See `itemtables/batch_016/notes_concretewords.csv` and `verify_concretewords.R`. Note that
`verify_concretewords.R` asserts the **old**, broken orientation (it was written to make the
defect re-runnable) and will correctly start failing once the corrected table is live.
