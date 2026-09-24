# Audit diff: eammi_grahe_2018_socmedia

Classification (suggested): **review**

## Summary

- item coverage: OK (missed=0, extra=0)
- resp-set alignment rate: 0.9167
- mean item_text similarity: 0.9196
- mean option_text similarity: 1
- mean context (instructions/section_prompt) similarity: 0.7413
- instructions/section_prompt swaps detected: 11

## Itemized mismatches

- `SocMedia_1` -- option_text_presence_mismatch (resp=2)
- `SocMedia_1` -- option_text_presence_mismatch (resp=3)
- `SocMedia_1` -- option_text_presence_mismatch (resp=4)
- `SocMedia_7` -- option_text_presence_mismatch (resp=3)
- `SocMedia_7` -- option_text_presence_mismatch (resp=4)
- `SocMedia_7` -- option_text_presence_mismatch (resp=2)
- `SocMedia_6` -- option_text_presence_mismatch (resp=2)
- `SocMedia_6` -- option_text_presence_mismatch (resp=4)
- `SocMedia_6` -- option_text_presence_mismatch (resp=3)
- `SocMedia_2` -- option_text_presence_mismatch (resp=3)
- `SocMedia_2` -- option_text_presence_mismatch (resp=2)
- `SocMedia_2` -- option_text_presence_mismatch (resp=4)
- `SocMedia_10` -- option_text_presence_mismatch (resp=4)
- `SocMedia_10` -- option_text_presence_mismatch (resp=3)
- `SocMedia_10` -- option_text_presence_mismatch (resp=2)
- `SocMedia_9` -- option_text_presence_mismatch (resp=4)
- `SocMedia_9` -- option_text_presence_mismatch (resp=3)
- `SocMedia_9` -- option_text_presence_mismatch (resp=2)
- `SocMedia_3` -- option_text_presence_mismatch (resp=2)
- `SocMedia_3` -- option_text_presence_mismatch (resp=3)
- `SocMedia_3` -- option_text_presence_mismatch (resp=4)
- `SocMedia_4` -- option_text_presence_mismatch (resp=3)
- `SocMedia_4` -- option_text_presence_mismatch (resp=4)
- `SocMedia_4` -- option_text_presence_mismatch (resp=2)
- `SocMedia_8` -- option_text_presence_mismatch (resp=3)
- `SocMedia_8` -- option_text_presence_mismatch (resp=4)
- `SocMedia_8` -- option_text_presence_mismatch (resp=2)
- `SocMedia_5` -- option_text_presence_mismatch (resp=3)
- `SocMedia_5` -- option_text_presence_mismatch (resp=2)
- `SocMedia_5` -- option_text_presence_mismatch (resp=4)
- `SocMedia_11` -- option_text_presence_mismatch (resp=3)
- `SocMedia_11` -- option_text_presence_mismatch (resp=4)
- `SocMedia_11` -- option_text_presence_mismatch (resp=2)
- `SocMedia_bias_dummy` -- resp_set_mismatch (curated={} fresh={1})
- `SocMedia_bias_dummy` -- item_text_mismatch
- `SocMedia_1` -- instructions_section_prompt_swap_suspected
- `SocMedia_7` -- instructions_section_prompt_swap_suspected
- `SocMedia_6` -- instructions_section_prompt_swap_suspected
- `SocMedia_2` -- instructions_section_prompt_swap_suspected
- `SocMedia_10` -- instructions_section_prompt_swap_suspected
- `SocMedia_9` -- instructions_section_prompt_swap_suspected
- `SocMedia_3` -- instructions_section_prompt_swap_suspected
- `SocMedia_4` -- instructions_section_prompt_swap_suspected
- `SocMedia_8` -- instructions_section_prompt_swap_suspected
- `SocMedia_5` -- instructions_section_prompt_swap_suspected
- `SocMedia_11` -- instructions_section_prompt_swap_suspected
- `SocMedia_bias_dummy` -- instructions_mismatch

## Field-level values for mismatched items

### `SocMedia_6` / item_text (similarity 0.9302)
- curated: `Find out more about someone Iâ€™ve just met`
- fresh: `Find out more about someone I've just met`

### `SocMedia_4` / item_text (similarity 0.9231)
- curated: `Let friends know what Iâ€™ve been up to`
- fresh: `Let friends know what I've been up to`

### `SocMedia_bias_dummy` / item_text (similarity 0.1813)
- curated: `response bias coded, 1 = all same answer`
- fresh: `Derived response-bias indicator (not an administered item): computed flag equal to 1 when a respondent gave the identical rating to all 11 SocMedia items (straight-lining detection).`

### `SocMedia_1` / instructions_or_section_prompt(swap-detected) (similarity 0.8108)
- curated: `instr=Think of the social media platform (e.g., Facebook, Instagra | sp=NA`
- fresh: `instr= | sp=Think of the social media platform (e.g., Facebook, Instagra`

### `SocMedia_7` / instructions_or_section_prompt(swap-detected) (similarity 0.8108)
- curated: `instr=Think of the social media platform (e.g., Facebook, Instagra | sp=NA`
- fresh: `instr= | sp=Think of the social media platform (e.g., Facebook, Instagra`

### `SocMedia_6` / instructions_or_section_prompt(swap-detected) (similarity 0.8108)
- curated: `instr=Think of the social media platform (e.g., Facebook, Instagra | sp=NA`
- fresh: `instr= | sp=Think of the social media platform (e.g., Facebook, Instagra`

### `SocMedia_2` / instructions_or_section_prompt(swap-detected) (similarity 0.8108)
- curated: `instr=Think of the social media platform (e.g., Facebook, Instagra | sp=NA`
- fresh: `instr= | sp=Think of the social media platform (e.g., Facebook, Instagra`

### `SocMedia_10` / instructions_or_section_prompt(swap-detected) (similarity 0.8108)
- curated: `instr=Think of the social media platform (e.g., Facebook, Instagra | sp=NA`
- fresh: `instr= | sp=Think of the social media platform (e.g., Facebook, Instagra`

### `SocMedia_9` / instructions_or_section_prompt(swap-detected) (similarity 0.8108)
- curated: `instr=Think of the social media platform (e.g., Facebook, Instagra | sp=NA`
- fresh: `instr= | sp=Think of the social media platform (e.g., Facebook, Instagra`

### `SocMedia_3` / instructions_or_section_prompt(swap-detected) (similarity 0.8108)
- curated: `instr=Think of the social media platform (e.g., Facebook, Instagra | sp=NA`
- fresh: `instr= | sp=Think of the social media platform (e.g., Facebook, Instagra`

### `SocMedia_4` / instructions_or_section_prompt(swap-detected) (similarity 0.8108)
- curated: `instr=Think of the social media platform (e.g., Facebook, Instagra | sp=NA`
- fresh: `instr= | sp=Think of the social media platform (e.g., Facebook, Instagra`

### `SocMedia_8` / instructions_or_section_prompt(swap-detected) (similarity 0.8108)
- curated: `instr=Think of the social media platform (e.g., Facebook, Instagra | sp=NA`
- fresh: `instr= | sp=Think of the social media platform (e.g., Facebook, Instagra`

### `SocMedia_5` / instructions_or_section_prompt(swap-detected) (similarity 0.8108)
- curated: `instr=Think of the social media platform (e.g., Facebook, Instagra | sp=NA`
- fresh: `instr= | sp=Think of the social media platform (e.g., Facebook, Instagra`

### `SocMedia_11` / instructions_or_section_prompt(swap-detected) (similarity 0.8108)
- curated: `instr=Think of the social media platform (e.g., Facebook, Instagra | sp=NA`
- fresh: `instr= | sp=Think of the social media platform (e.g., Facebook, Instagra`

### `SocMedia_bias_dummy` / instructions (similarity 0)
- curated: `Think of the social media platform (e.g., Facebook, Instagram, Twitter, etc.) you use most often. How often do you use it for the following reasons? Never (1) Rarely (2) Sometimes (3)`
- fresh: ``

