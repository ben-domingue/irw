# Audit diff: dumas_organisciak_2022

**Real replace-candidate.** Current curation only has `item_text` = the bare
object name (e.g. "book") and no `instructions`/`option_text` at all --
essentially a placeholder. This extraction adds, from
DumasOrganisciakDoherty2020PACA.pdf (OSF qcmex): task description
(Alternate Uses Task, 2-min generation window, 4 coders rating Originality
0-4) and the two rating-scale endpoint anchors ("totally ordinary" / "maximally
novel" per the paper's exact wording -- p.26). Note the paper states coders
used a **0-4** scale but the live IRW `resp` values are **1-5**; treated as a
+1 shift applied during IRW processing, not verified against the raw data
file itself -- flag this specifically if approving the replace. Interior
points (2,3,4) intentionally left blank; the paper only describes where
responses tend to cluster (around the scale midpoint), not per-point rating
anchors for a rater to apply.

Classification (suggested): **review**

## Summary

- item coverage: OK (missed=0, extra=0)
- resp-set alignment rate: 1
- mean item_text similarity: 1
- mean option_text similarity: 0.4132
- mean context (instructions/section_prompt) similarity: n/a
- instructions/section_prompt swaps detected: 0

## Itemized mismatches

- `book` -- option_text_mismatch (resp=5)
- `book` -- option_text_mismatch (resp=1)
- `bottle` -- option_text_mismatch (resp=5)
- `bottle` -- option_text_mismatch (resp=1)
- `brick` -- option_text_mismatch (resp=5)
- `brick` -- option_text_mismatch (resp=1)
- `fork` -- option_text_mismatch (resp=5)
- `fork` -- option_text_mismatch (resp=1)
- `pants` -- option_text_mismatch (resp=5)
- `pants` -- option_text_mismatch (resp=1)
- `rope` -- option_text_mismatch (resp=5)
- `rope` -- option_text_mismatch (resp=1)
- `shoe` -- option_text_mismatch (resp=5)
- `shoe` -- option_text_mismatch (resp=1)
- `shovel` -- option_text_mismatch (resp=5)
- `shovel` -- option_text_mismatch (resp=1)
- `table` -- option_text_mismatch (resp=5)
- `table` -- option_text_mismatch (resp=1)
- `tire` -- option_text_mismatch (resp=5)
- `tire` -- option_text_mismatch (resp=1)

## Field-level values for mismatched items

### `book` / option_text[resp=5] (similarity 0.4054)
- curated: `maximally novel`
- fresh: `maximally novel (paper coder scale 4)`

### `book` / option_text[resp=1] (similarity 0.4211)
- curated: `totally ordinary`
- fresh: `totally ordinary (paper coder scale 0)`

### `bottle` / option_text[resp=5] (similarity 0.4054)
- curated: `maximally novel`
- fresh: `maximally novel (paper coder scale 4)`

### `bottle` / option_text[resp=1] (similarity 0.4211)
- curated: `totally ordinary`
- fresh: `totally ordinary (paper coder scale 0)`

### `brick` / option_text[resp=5] (similarity 0.4054)
- curated: `maximally novel`
- fresh: `maximally novel (paper coder scale 4)`

### `brick` / option_text[resp=1] (similarity 0.4211)
- curated: `totally ordinary`
- fresh: `totally ordinary (paper coder scale 0)`

### `fork` / option_text[resp=5] (similarity 0.4054)
- curated: `maximally novel`
- fresh: `maximally novel (paper coder scale 4)`

### `fork` / option_text[resp=1] (similarity 0.4211)
- curated: `totally ordinary`
- fresh: `totally ordinary (paper coder scale 0)`

### `pants` / option_text[resp=5] (similarity 0.4054)
- curated: `maximally novel`
- fresh: `maximally novel (paper coder scale 4)`

### `pants` / option_text[resp=1] (similarity 0.4211)
- curated: `totally ordinary`
- fresh: `totally ordinary (paper coder scale 0)`

### `rope` / option_text[resp=5] (similarity 0.4054)
- curated: `maximally novel`
- fresh: `maximally novel (paper coder scale 4)`

### `rope` / option_text[resp=1] (similarity 0.4211)
- curated: `totally ordinary`
- fresh: `totally ordinary (paper coder scale 0)`

### `shoe` / option_text[resp=5] (similarity 0.4054)
- curated: `maximally novel`
- fresh: `maximally novel (paper coder scale 4)`

### `shoe` / option_text[resp=1] (similarity 0.4211)
- curated: `totally ordinary`
- fresh: `totally ordinary (paper coder scale 0)`

### `shovel` / option_text[resp=5] (similarity 0.4054)
- curated: `maximally novel`
- fresh: `maximally novel (paper coder scale 4)`

### `shovel` / option_text[resp=1] (similarity 0.4211)
- curated: `totally ordinary`
- fresh: `totally ordinary (paper coder scale 0)`

### `table` / option_text[resp=5] (similarity 0.4054)
- curated: `maximally novel`
- fresh: `maximally novel (paper coder scale 4)`

### `table` / option_text[resp=1] (similarity 0.4211)
- curated: `totally ordinary`
- fresh: `totally ordinary (paper coder scale 0)`

### `tire` / option_text[resp=5] (similarity 0.4054)
- curated: `maximally novel`
- fresh: `maximally novel (paper coder scale 4)`

### `tire` / option_text[resp=1] (similarity 0.4211)
- curated: `totally ordinary`
- fresh: `totally ordinary (paper coder scale 0)`

