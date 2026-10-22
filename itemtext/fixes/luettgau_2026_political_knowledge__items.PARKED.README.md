# `luettgau_2026_political_knowledge__items` — parked, not shipped

Built 2026-10-22 alongside `data/luettgau_2026_political_ai.py`. All 64 statements are
transcribed and the item set matches the response table exactly. It is parked on two
things, either of which alone would be enough.

## 1. The statement → question-index mapping is unverified

The response table's items are `<topic>_01` … `<topic>_16`, and `ground_truth` splits
them in a perfect block: 1–8 true, 9–16 false, in all four topics. The article's
appendix ("The statements presented were the following") lists exactly 8 TRUE then 8
FALSE statements per topic, in that order. So the obvious reading — question *k* ∈ 1..8
is the *k*-th TRUE statement listed, question 8+*k* the *k*-th FALSE one — is what this
file encodes.

The block boundary at 8 is confirmed by the data. **The order *within* each block is
not.** Nothing ties the appendix's listing order to the survey's question index: the
deposit's `data/statement_sourcing.csv` lists the true statements in the same order as
the appendix (same four climate statements, same sequence), which is corroboration that
both were generated from one ordered list, but both are post-hoc artefacts and neither
carries a question number. A wrong order inside a block would silently attach the wrong
text to 8 items per block while passing every gate — the item and resp sets would still
match perfectly.

## 2. The 7-point scale's point labels are not published

Neither the article nor the deposit gives the anchors; the article says only "a 7-point
Likert scale, ranging from disagree to agree". So `option_text`/`resp` cannot be filled,
and `validate_items.R` reports `FAIL: no resp values at all` (item set: PASS, 64/64).

This is not a cosmetic gap here. The response column is stored **agree-first** (1 =
agree, 7 = disagree — see the script header for how that was established), so inventing
plausible labels would have a one-in-two chance of inverting the option text against the
responses it joins to.

## What would unpark it

One message to the authors, who publish an issue tracker on the deposit
(`github.com/UKGovernmentBEIS/dhi1-analysis-public`), asking for (a) the statement →
question-index mapping, ideally the survey instrument as fielded, and (b) the seven
scale point labels and their numeric coding. Both are a single lookup for them.

## Also in that appendix, if the sibling tables are ever shipped

The same section carries the trust/distrust statements, the private-belief statements
(listed per topic as Progressive / Conservative) and the five compliance questions per
topic. So item text for `Ztable_trust_combined` and `Ztable_private_combined` is
available too — the blocker on those tables is their ambiguous pre/post structure, not
their wording. See `automated_finding/BATCH_LOG.md`, 2026-10-22.
