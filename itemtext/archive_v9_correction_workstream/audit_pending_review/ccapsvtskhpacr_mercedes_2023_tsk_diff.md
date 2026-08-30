# Audit diff: ccapsvtskhpacr_mercedes_2023_tsk

**Mostly a real improvement, one caveat.** Item identity/order/resp-range
fully confirmed via the literal Spanish item wording + value labels in the
source .sav file (OSF 8t4fp, Data/TSK_ES_231202.sav -- the same file behind
the `ccapsvtskhpacr_mercedes_2023_physical` table-name-mismatch case this
eval found earlier; that file's separate tsk1-tsk17 variables are exactly
this table). item_text mismatches (0.70 mean similarity) are my own
independent English translation of the Spanish source phrased differently
from the existing curated English translation -- not necessarily evidence
either is wrong, both are legitimate translations of the same Spanish
original; a bilingual reviewer should judge which reads better, this isn't
a mechanical fix. **option_text is a genuine improvement**: current curation
only has resp=1/4 labeled ("Totally disagree"/"Totally agree"); the source
.sav file's value labels give all 4 points (disagree=2, agree=3 added here)
-- this part is a clean, low-risk addition.

Classification (suggested): **review**

## Summary

- item coverage: OK (missed=0, extra=0)
- resp-set alignment rate: 1
- mean item_text similarity: 0.7019
- mean option_text similarity: 1
- mean context (instructions/section_prompt) similarity: n/a
- instructions/section_prompt swaps detected: 0

## Itemized mismatches

- `tsk10` -- option_text_presence_mismatch (resp=2)
- `tsk10` -- option_text_presence_mismatch (resp=3)
- `tsk3` -- option_text_presence_mismatch (resp=2)
- `tsk3` -- option_text_presence_mismatch (resp=3)
- `tsk4` -- option_text_presence_mismatch (resp=2)
- `tsk4` -- option_text_presence_mismatch (resp=3)
- `tsk12` -- option_text_presence_mismatch (resp=2)
- `tsk12` -- option_text_presence_mismatch (resp=3)
- `tsk13` -- option_text_presence_mismatch (resp=2)
- `tsk13` -- option_text_presence_mismatch (resp=3)
- `tsk5` -- option_text_presence_mismatch (resp=2)
- `tsk5` -- option_text_presence_mismatch (resp=3)
- `tsk16` -- option_text_presence_mismatch (resp=2)
- `tsk16` -- option_text_presence_mismatch (resp=3)
- `tsk11` -- option_text_presence_mismatch (resp=2)
- `tsk11` -- option_text_presence_mismatch (resp=3)
- `tsk9` -- option_text_presence_mismatch (resp=2)
- `tsk9` -- option_text_presence_mismatch (resp=3)
- `tsk2` -- option_text_presence_mismatch (resp=2)
- `tsk2` -- option_text_presence_mismatch (resp=3)
- `tsk15` -- option_text_presence_mismatch (resp=2)
- `tsk15` -- option_text_presence_mismatch (resp=3)
- `tsk6` -- option_text_presence_mismatch (resp=2)
- `tsk6` -- option_text_presence_mismatch (resp=3)
- `tsk14` -- option_text_presence_mismatch (resp=2)
- `tsk14` -- option_text_presence_mismatch (resp=3)
- `tsk1` -- option_text_presence_mismatch (resp=2)
- `tsk1` -- option_text_presence_mismatch (resp=3)
- `tsk7` -- option_text_presence_mismatch (resp=2)
- `tsk7` -- option_text_presence_mismatch (resp=3)
- `tsk8` -- option_text_presence_mismatch (resp=2)
- `tsk8` -- option_text_presence_mismatch (resp=3)
- `tsk17` -- option_text_presence_mismatch (resp=2)
- `tsk17` -- option_text_presence_mismatch (resp=3)
- `tsk10` -- item_text_mismatch
- `tsk3` -- item_text_mismatch
- `tsk11` -- item_text_mismatch
- `tsk14` -- item_text_mismatch
- `tsk8` -- item_text_mismatch

## Field-level values for mismatched items

### `tsk10` / item_text (similarity 0.2062)
- curated: `By being careful with unnecessary movements I can prevent my heart problems from worsening.`
- fresh: `I can prevent my heart problems from getting worse by being careful with inappropriate movements.`

### `tsk3` / item_text (similarity 0.4667)
- curated: `My body is telling me that I have something seriously wrong.`
- fresh: `The symptoms I feel are telling me I have something serious.`

### `tsk4` / item_text (similarity 0.7531)
- curated: `My heart problem would probably be relieved if I was physically active/exercised.`
- fresh: `My heart problem would improve if I were physically active/exercised.`

### `tsk12` / item_text (similarity 0.6667)
- curated: `Even if I have a heart problem I would manage better if I was physically active/exercised.`
- fresh: `Despite having a heart problem, I would feel better if I were physically active.`

### `tsk13` / item_text (similarity 0.6964)
- curated: `My heart problem tells me when I should stop being physically active/exercising, so that I do not injure myself.`
- fresh: `My heart problem tells me when I should stop exercising so as not to injure myself.`

### `tsk5` / item_text (similarity 0.8)
- curated: `People are not taking my medical condition seriously enough.`
- fresh: `People do not take my health condition seriously enough.`

### `tsk16` / item_text (similarity 0.8081)
- curated: `Even though something causes me a lot of heart problems, I do not think it is actually dangerous.`
- fresh: `Even though something causes me a lot of cardiac discomfort, I do not think it is really dangerous.`

### `tsk11` / item_text (similarity 0.5978)
- curated: `I would not have my heart problems if there was not something dangerous going on in my body.`
- fresh: `I would not have heart problems if something serious were not happening in my body.`

### `tsk9` / item_text (similarity 0.6452)
- curated: `I am afraid that I might injure myself accidentally.`
- fresh: `I am afraid of the possibility of hurting myself accidentally.`

### `tsk15` / item_text (similarity 0.6634)
- curated: `I cannot do the same things as others because there is too big a risk that I will get heart problems.`
- fresh: `I cannot do the same things as other people because I am at greater risk of heart problems.`

### `tsk14` / item_text (similarity 0.4762)
- curated: `It is really not safe for a person in my condition to be physically active/exercise.`
- fresh: `It is not very safe for someone in my health condition to exercise.`

### `tsk7` / item_text (similarity 0.8033)
- curated: `In general, heart problem is always due to body injury.`
- fresh: `In general, heart problems are always due to physical injury.`

### `tsk8` / item_text (similarity 0.5909)
- curated: `Just because something causes discomfort in my chest does not mean that it is dangerous.`
- fresh: `Even if I notice discomfort in my chest, it does not mean it is serious.`

### `tsk17` / item_text (similarity 0.7711)
- curated: `No one should have to be physically active/exercise when he/she has heart problems.`
- fresh: `No one should be physically active/exercise if they have heart problems.`

