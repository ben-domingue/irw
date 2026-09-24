# Audit diff: florida_twins_friends

**Not a replace-candidate -- this is a documented ambiguity.** 19/21 items
(`friends1`-`friends19`) matched the current curation exactly, confirmed blind
against the W1_Child codebook LDBase.docx (Florida Twin Project, LDbase doc
4d4acbc5-f07b-4282-9da3-5692ffacc8b0). Items `friends20`
("My friends attend the same school as me.") and `friends21` ("My friends are
older than me.") are in the live data and in the current curation, but are
**not documented anywhere in that codebook** -- left blank in this fresh
extraction rather than guessed. This isn't evidence the curated text for
those two items is wrong, only that this one source doesn't cover them; a
different/later-wave codebook may. Logged to `pending_index_notes.csv`
instead of queued for replace.

Classification (suggested): **review**

## Summary

- item coverage: OK (missed=0, extra=0)
- resp-set alignment rate: 1
- mean item_text similarity: 0.9022
- mean option_text similarity: 0.9722
- mean context (instructions/section_prompt) similarity: 0.9856
- instructions/section_prompt swaps detected: 0

## Itemized mismatches

- `friends20` -- option_text_presence_mismatch (resp=1)
- `friends20` -- option_text_presence_mismatch (resp=2)
- `friends20` -- option_text_presence_mismatch (resp=3)
- `friends20` -- option_text_presence_mismatch (resp=4)
- `friends21` -- option_text_presence_mismatch (resp=1)
- `friends21` -- option_text_presence_mismatch (resp=2)
- `friends21` -- option_text_presence_mismatch (resp=3)
- `friends21` -- option_text_presence_mismatch (resp=4)
- `friends20` -- item_text_mismatch
- `friends21` -- item_text_mismatch

## Field-level values for mismatched items

### `friends20` / item_text (similarity 0)
- curated: `My friends attend the same school as me.`
- fresh: `NA`

### `friends21` / item_text (similarity 0)
- curated: `My friends are older than me.`
- fresh: `NA`

