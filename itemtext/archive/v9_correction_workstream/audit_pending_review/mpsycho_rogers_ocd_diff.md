# Audit diff: mpsycho_rogers_ocd

**Not a replace-candidate -- documented ambiguity.** Item identity/order
confirmed exactly via `MPsychoR::Rogers` package documentation (10 Y-BOCS-SR
items, obsessions then compulsions, matching current curation's item names
1-for-1) and resp range confirmed 0-4. The package docs only give short
variable labels ("Time consumed by obsessions"), not full item wording --
current curation's item_text/option_text uses fuller self-report phrasing
("Questions 1 to 5 are about your obsessive thoughts...") that doesn't match
either the generic public Y-BOCS-adult.pdf or anything else found via web
search in reasonable effort. Rather than guess which published Y-BOCS-SR
variant Rogers Memorial Hospital actually used, item_text/option_text/
section_prompt were left blank. Not evidence the curated text is wrong --
just unverified. Logged to `pending_index_notes.csv`.

Classification (suggested): **review**

## Summary

- item coverage: OK (missed=0, extra=0)
- resp-set alignment rate: 1
- mean item_text similarity: 0
- mean option_text similarity: n/a
- mean context (instructions/section_prompt) similarity: 0
- instructions/section_prompt swaps detected: 0

## Itemized mismatches

- `compcont` -- option_text_presence_mismatch (resp=0)
- `compcont` -- option_text_presence_mismatch (resp=1)
- `compcont` -- option_text_presence_mismatch (resp=2)
- `compcont` -- option_text_presence_mismatch (resp=3)
- `compcont` -- option_text_presence_mismatch (resp=4)
- `compdis` -- option_text_presence_mismatch (resp=0)
- `compdis` -- option_text_presence_mismatch (resp=2)
- `compdis` -- option_text_presence_mismatch (resp=3)
- `compdis` -- option_text_presence_mismatch (resp=4)
- `compdis` -- option_text_presence_mismatch (resp=1)
- `compinterf` -- option_text_presence_mismatch (resp=2)
- `compinterf` -- option_text_presence_mismatch (resp=0)
- `compinterf` -- option_text_presence_mismatch (resp=3)
- `compinterf` -- option_text_presence_mismatch (resp=4)
- `compinterf` -- option_text_presence_mismatch (resp=1)
- `compresis` -- option_text_presence_mismatch (resp=4)
- `compresis` -- option_text_presence_mismatch (resp=2)
- `compresis` -- option_text_presence_mismatch (resp=1)
- `compresis` -- option_text_presence_mismatch (resp=3)
- `compresis` -- option_text_presence_mismatch (resp=0)
- `comptime` -- option_text_presence_mismatch (resp=0)
- `comptime` -- option_text_presence_mismatch (resp=1)
- `comptime` -- option_text_presence_mismatch (resp=4)
- `comptime` -- option_text_presence_mismatch (resp=3)
- `comptime` -- option_text_presence_mismatch (resp=2)
- `obcontrol` -- option_text_presence_mismatch (resp=0)
- `obcontrol` -- option_text_presence_mismatch (resp=4)
- `obcontrol` -- option_text_presence_mismatch (resp=1)
- `obcontrol` -- option_text_presence_mismatch (resp=2)
- `obcontrol` -- option_text_presence_mismatch (resp=3)
- `obdistress` -- option_text_presence_mismatch (resp=0)
- `obdistress` -- option_text_presence_mismatch (resp=3)
- `obdistress` -- option_text_presence_mismatch (resp=2)
- `obdistress` -- option_text_presence_mismatch (resp=1)
- `obdistress` -- option_text_presence_mismatch (resp=4)
- `obinterfer` -- option_text_presence_mismatch (resp=0)
- `obinterfer` -- option_text_presence_mismatch (resp=4)
- `obinterfer` -- option_text_presence_mismatch (resp=2)
- `obinterfer` -- option_text_presence_mismatch (resp=3)
- `obinterfer` -- option_text_presence_mismatch (resp=1)
- `obresist` -- option_text_presence_mismatch (resp=0)
- `obresist` -- option_text_presence_mismatch (resp=2)
- `obresist` -- option_text_presence_mismatch (resp=1)
- `obresist` -- option_text_presence_mismatch (resp=3)
- `obresist` -- option_text_presence_mismatch (resp=4)
- `obtime` -- option_text_presence_mismatch (resp=2)
- `obtime` -- option_text_presence_mismatch (resp=0)
- `obtime` -- option_text_presence_mismatch (resp=1)
- `obtime` -- option_text_presence_mismatch (resp=4)
- `obtime` -- option_text_presence_mismatch (resp=3)
- `compcont` -- item_text_mismatch
- `compdis` -- item_text_mismatch
- `compinterf` -- item_text_mismatch
- `compresis` -- item_text_mismatch
- `comptime` -- item_text_mismatch
- `obcontrol` -- item_text_mismatch
- `obdistress` -- item_text_mismatch
- `obinterfer` -- item_text_mismatch
- `obresist` -- item_text_mismatch
- `obtime` -- item_text_mismatch
- `compcont` -- section_prompt_mismatch
- `compdis` -- section_prompt_mismatch
- `compinterf` -- section_prompt_mismatch
- `compresis` -- section_prompt_mismatch
- `comptime` -- section_prompt_mismatch
- `obcontrol` -- section_prompt_mismatch
- `obdistress` -- section_prompt_mismatch
- `obinterfer` -- section_prompt_mismatch
- `obresist` -- section_prompt_mismatch
- `obtime` -- section_prompt_mismatch

## Field-level values for mismatched items

### `compcont` / item_text (similarity 0)
- curated: `How strong is the drive to perform the compulsive behavior? How much control do you have over the compulsions?`
- fresh: `NA`

### `compdis` / item_text (similarity 0)
- curated: `How would you feel if prevented from performing your compulsion(s)? How anxious would you become?`
- fresh: `NA`

### `compinterf` / item_text (similarity 0)
- curated: `How much do your compulsive behaviors interfere with your work, school, social, or other important role functioning? Is there anything that you don’t do because of the compulsions?`
- fresh: `NA`

### `compresis` / item_text (similarity 0)
- curated: `How much of an effort do you make to resist the compulsions?`
- fresh: `NA`

### `comptime` / item_text (similarity 0)
- curated: `How much time do you spend performing compulsive behaviors? How much longer than most people does it take to complete routine activities because of your rituals? How frequently do you do rituals?`
- fresh: `NA`

### `obcontrol` / item_text (similarity 0)
- curated: `How much control do you have over your obsessive thoughts? How successful are you in stopping or diverting your obsessive thinking? Can you dismiss them?`
- fresh: `NA`

### `obdistress` / item_text (similarity 0)
- curated: `How much distress do your obsessive thoughts cause you?`
- fresh: `NA`

### `obinterfer` / item_text (similarity 0)
- curated: `How much do your obsessive thoughts interfere with your work, school, social, or other important role functioning? Is there anything that you don’t do because of them?`
- fresh: `NA`

### `obresist` / item_text (similarity 0)
- curated: `How much of an effort do you make to resist the obsessive thoughts? How often do you try to disregard or turn your attention away from these thoughts as they enter your mind?`
- fresh: `NA`

### `obtime` / item_text (similarity 0)
- curated: `How much of your time is occupied by obsessive thoughts?`
- fresh: `NA`

### `compcont` / section_prompt (similarity 0)
- curated: `The next several questions are about your compulsive behaviors. Compulsions are urges that people have to do something to lessen feelings of anxiety or other discomfort. Often they do repetitive, purposeful, intentional behaviors called rituals. The behavior itself may seem appropriate but it becomes a ritual when done to excess. Washing, checking, repeating, straightening, hoarding and many other behaviors can be rituals. Some rituals are mental. For example, thinking or saying things over and over under your breath.`
- fresh: `NA`

### `compdis` / section_prompt (similarity 0)
- curated: `The next several questions are about your compulsive behaviors. Compulsions are urges that people have to do something to lessen feelings of anxiety or other discomfort. Often they do repetitive, purposeful, intentional behaviors called rituals. The behavior itself may seem appropriate but it becomes a ritual when done to excess. Washing, checking, repeating, straightening, hoarding and many other behaviors can be rituals. Some rituals are mental. For example, thinking or saying things over and over under your breath.`
- fresh: `NA`

### `compinterf` / section_prompt (similarity 0)
- curated: `The next several questions are about your compulsive behaviors. Compulsions are urges that people have to do something to lessen feelings of anxiety or other discomfort. Often they do repetitive, purposeful, intentional behaviors called rituals. The behavior itself may seem appropriate but it becomes a ritual when done to excess. Washing, checking, repeating, straightening, hoarding and many other behaviors can be rituals. Some rituals are mental. For example, thinking or saying things over and over under your breath.`
- fresh: `NA`

### `compresis` / section_prompt (similarity 0)
- curated: `The next several questions are about your compulsive behaviors. Compulsions are urges that people have to do something to lessen feelings of anxiety or other discomfort. Often they do repetitive, purposeful, intentional behaviors called rituals. The behavior itself may seem appropriate but it becomes a ritual when done to excess. Washing, checking, repeating, straightening, hoarding and many other behaviors can be rituals. Some rituals are mental. For example, thinking or saying things over and over under your breath.`
- fresh: `NA`

### `comptime` / section_prompt (similarity 0)
- curated: `The next several questions are about your compulsive behaviors. Compulsions are urges that people have to do something to lessen feelings of anxiety or other discomfort. Often they do repetitive, purposeful, intentional behaviors called rituals. The behavior itself may seem appropriate but it becomes a ritual when done to excess. Washing, checking, repeating, straightening, hoarding and many other behaviors can be rituals. Some rituals are mental. For example, thinking or saying things over and over under your breath.`
- fresh: `NA`

### `obcontrol` / section_prompt (similarity 0)
- curated: `Questions 1 to 5 are about your obsessive thoughts. Obsessions are unwanted ideas, images or impulses that intrude on thinking against your wishes and efforts to resist them. They usually involve themes of harm, risk and danger. Common obsessions are excessive fears of contamination; recurring doubts about danger, extreme concern with order, symmetry, or exactness; fear of losing important things.`
- fresh: `NA`

### `obdistress` / section_prompt (similarity 0)
- curated: `Questions 1 to 5 are about your obsessive thoughts. Obsessions are unwanted ideas, images or impulses that intrude on thinking against your wishes and efforts to resist them. They usually involve themes of harm, risk and danger. Common obsessions are excessive fears of contamination; recurring doubts about danger, extreme concern with order, symmetry, or exactness; fear of losing important things.`
- fresh: `NA`

### `obinterfer` / section_prompt (similarity 0)
- curated: `Questions 1 to 5 are about your obsessive thoughts. Obsessions are unwanted ideas, images or impulses that intrude on thinking against your wishes and efforts to resist them. They usually involve themes of harm, risk and danger. Common obsessions are excessive fears of contamination; recurring doubts about danger, extreme concern with order, symmetry, or exactness; fear of losing important things.`
- fresh: `NA`

### `obresist` / section_prompt (similarity 0)
- curated: `Questions 1 to 5 are about your obsessive thoughts. Obsessions are unwanted ideas, images or impulses that intrude on thinking against your wishes and efforts to resist them. They usually involve themes of harm, risk and danger. Common obsessions are excessive fears of contamination; recurring doubts about danger, extreme concern with order, symmetry, or exactness; fear of losing important things.`
- fresh: `NA`

### `obtime` / section_prompt (similarity 0)
- curated: `Questions 1 to 5 are about your obsessive thoughts. Obsessions are unwanted ideas, images or impulses that intrude on thinking against your wishes and efforts to resist them. They usually involve themes of harm, risk and danger. Common obsessions are excessive fears of contamination; recurring doubts about danger, extreme concern with order, symmetry, or exactness; fear of losing important things.`
- fresh: `NA`

