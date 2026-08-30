# Audit diff: political_psychology

**Already filed and actioned**: [ben-domingue/irw#1594](https://github.com/ben-domingue/irw/issues/1594)
(7/37 items mismapped in the pre-existing Redivis entry, confirmed against both
`data/political_psychology.R`'s recoding logic and a fresh `irw::irw_fetch()` pull).
No further review needed here — kept as the audit-mode pilot's regression example.

Classification (suggested): **review**

## Summary

- item coverage: OK (missed=0, extra=0)
- resp-set alignment rate: 0.8108
- mean item_text similarity: 0.3949
- mean option_text similarity: 0.4965
- mean context (instructions/section_prompt) similarity: 0.2652
- instructions/section_prompt swaps detected: 0

## Itemized mismatches

- `30` -- resp_set_mismatch (curated={} fresh={1,2,3,4,5,6,7})
- `14` -- resp_set_mismatch (curated={1,2,3,4,5,6,7} fresh={1,2,3,4})
- `14` -- option_text_presence_mismatch (resp=3)
- `14` -- option_text_presence_mismatch (resp=2)
- `14` -- option_text_mismatch (resp=1)
- `14` -- option_text_mismatch (resp=4)
- `12` -- resp_set_mismatch (curated={1,2,3,4,5,6} fresh={1,2,3,4,5,6,7})
- `12` -- option_text_mismatch (resp=4)
- `12` -- option_text_mismatch (resp=1)
- `12` -- option_text_presence_mismatch (resp=3)
- `12` -- option_text_presence_mismatch (resp=2)
- `12` -- option_text_presence_mismatch (resp=6)
- `12` -- option_text_presence_mismatch (resp=5)
- `29` -- option_text_mismatch (resp=1)
- `29` -- option_text_mismatch (resp=7)
- `29` -- option_text_mismatch (resp=4)
- `32` -- option_text_mismatch (resp=1)
- `32` -- option_text_mismatch (resp=4)
- `32` -- option_text_mismatch (resp=7)
- `11` -- option_text_mismatch (resp=1)
- `11` -- option_text_mismatch (resp=4)
- `11` -- option_text_mismatch (resp=7)
- `33` -- option_text_mismatch (resp=7)
- `33` -- option_text_presence_mismatch (resp=2)
- `33` -- option_text_mismatch (resp=1)
- `33` -- option_text_presence_mismatch (resp=6)
- `33` -- option_text_presence_mismatch (resp=5)
- `33` -- option_text_presence_mismatch (resp=3)
- `33` -- option_text_mismatch (resp=4)
- `20` -- option_text_presence_mismatch (resp=4)
- `20` -- option_text_presence_mismatch (resp=3)
- `20` -- option_text_mismatch (resp=1)
- `20` -- option_text_presence_mismatch (resp=5)
- `20` -- option_text_presence_mismatch (resp=2)
- `20` -- option_text_presence_mismatch (resp=6)
- `20` -- option_text_mismatch (resp=7)
- `22` -- option_text_mismatch (resp=4)
- `22` -- option_text_mismatch (resp=1)
- `22` -- option_text_mismatch (resp=7)
- `31` -- option_text_mismatch (resp=7)
- `31` -- option_text_mismatch (resp=1)
- `31` -- option_text_mismatch (resp=4)
- `13` -- option_text_mismatch (resp=7)
- `13` -- option_text_presence_mismatch (resp=4)
- `13` -- option_text_mismatch (resp=1)
- `34` -- option_text_presence_mismatch (resp=4)
- `34` -- option_text_presence_mismatch (resp=7)
- `34` -- option_text_presence_mismatch (resp=1)
- `36` -- option_text_presence_mismatch (resp=7)
- `36` -- option_text_presence_mismatch (resp=4)
- `36` -- option_text_presence_mismatch (resp=1)
- `35` -- option_text_presence_mismatch (resp=7)
- `35` -- option_text_presence_mismatch (resp=1)
- `35` -- option_text_presence_mismatch (resp=4)
- `28` -- resp_set_mismatch (curated={1,2,3,4,5,6,7} fresh={1,2,3})
- `28` -- option_text_presence_mismatch (resp=3)
- `28` -- option_text_presence_mismatch (resp=2)
- `28` -- option_text_mismatch (resp=1)
- `26` -- option_text_presence_mismatch (resp=6)
- `26` -- option_text_presence_mismatch (resp=2)
- `26` -- option_text_presence_mismatch (resp=5)
- `26` -- option_text_presence_mismatch (resp=4)
- `26` -- option_text_mismatch (resp=1)
- `26` -- option_text_presence_mismatch (resp=3)
- `26` -- option_text_mismatch (resp=7)
- `27` -- resp_set_mismatch (curated={1,2,3,4,5,6,7} fresh={1,2,3})
- `27` -- option_text_presence_mismatch (resp=2)
- `27` -- option_text_mismatch (resp=1)
- `27` -- option_text_presence_mismatch (resp=3)
- `25` -- option_text_mismatch (resp=1)
- `25` -- option_text_presence_mismatch (resp=2)
- `25` -- option_text_mismatch (resp=7)
- `25` -- option_text_presence_mismatch (resp=5)
- `25` -- option_text_presence_mismatch (resp=6)
- `25` -- option_text_presence_mismatch (resp=3)
- `25` -- option_text_presence_mismatch (resp=4)
- `24` -- option_text_mismatch (resp=7)
- `24` -- option_text_mismatch (resp=1)
- `24` -- option_text_presence_mismatch (resp=4)
- `15` -- option_text_presence_mismatch (resp=4)
- `15` -- option_text_mismatch (resp=7)
- `15` -- option_text_mismatch (resp=1)
- `16` -- option_text_mismatch (resp=1)
- `16` -- option_text_presence_mismatch (resp=4)
- `16` -- option_text_mismatch (resp=7)
- `37` -- option_text_presence_mismatch (resp=7)
- `37` -- option_text_presence_mismatch (resp=1)
- `37` -- option_text_presence_mismatch (resp=4)
- `10` -- option_text_mismatch (resp=7)
- `10` -- option_text_mismatch (resp=4)
- `10` -- option_text_mismatch (resp=1)
- `18` -- option_text_mismatch (resp=7)
- `18` -- option_text_mismatch (resp=1)
- `18` -- option_text_presence_mismatch (resp=4)
- `17` -- option_text_mismatch (resp=7)
- `17` -- option_text_mismatch (resp=1)
- `17` -- option_text_presence_mismatch (resp=4)
- `19` -- option_text_presence_mismatch (resp=5)
- `19` -- option_text_presence_mismatch (resp=6)
- `19` -- option_text_presence_mismatch (resp=4)
- `19` -- option_text_presence_mismatch (resp=3)
- `19` -- option_text_presence_mismatch (resp=2)
- `19` -- option_text_mismatch (resp=7)
- `19` -- option_text_mismatch (resp=1)
- `7` -- resp_set_mismatch (curated={1,2,3,4,5,6} fresh={1,2,3,4})
- `21` -- resp_set_mismatch (curated={1,2,3,4,5,6} fresh={1,2,3,4,5,6,7})
- `21` -- option_text_mismatch (resp=4)
- `21` -- option_text_presence_mismatch (resp=6)
- `21` -- option_text_presence_mismatch (resp=3)
- `21` -- option_text_mismatch (resp=1)
- `21` -- option_text_presence_mismatch (resp=2)
- `21` -- option_text_presence_mismatch (resp=5)
- `30` -- item_text_mismatch
- `14` -- item_text_mismatch
- `12` -- item_text_mismatch
- `29` -- item_text_mismatch
- `32` -- item_text_mismatch
- `11` -- item_text_mismatch
- `33` -- item_text_mismatch
- `20` -- item_text_mismatch
- `22` -- item_text_mismatch
- `31` -- item_text_mismatch
- `13` -- item_text_mismatch
- `34` -- item_text_mismatch
- `36` -- item_text_mismatch
- `35` -- item_text_mismatch
- `28` -- item_text_mismatch
- `26` -- item_text_mismatch
- `27` -- item_text_mismatch
- `25` -- item_text_mismatch
- `24` -- item_text_mismatch
- `23` -- item_text_mismatch
- `15` -- item_text_mismatch
- `16` -- item_text_mismatch
- `37` -- item_text_mismatch
- `10` -- item_text_mismatch
- `18` -- item_text_mismatch
- `17` -- item_text_mismatch
- `19` -- item_text_mismatch
- `21` -- item_text_mismatch
- `30` -- instructions_mismatch
- `14` -- instructions_mismatch
- `12` -- instructions_mismatch
- `29` -- instructions_mismatch
- `32` -- instructions_mismatch
- `11` -- instructions_mismatch
- `33` -- instructions_mismatch
- `20` -- instructions_mismatch
- `22` -- instructions_mismatch
- `31` -- instructions_mismatch
- `13` -- instructions_mismatch
- `34` -- instructions_mismatch
- `36` -- instructions_mismatch
- `35` -- instructions_mismatch
- `28` -- instructions_mismatch
- `26` -- instructions_mismatch
- `27` -- instructions_mismatch
- `25` -- instructions_mismatch
- `24` -- instructions_mismatch
- `23` -- instructions_mismatch
- `15` -- instructions_mismatch
- `16` -- instructions_mismatch
- `37` -- instructions_mismatch
- `2` -- instructions_mismatch
- `4` -- instructions_mismatch
- `8` -- instructions_mismatch
- `1` -- instructions_mismatch
- `5` -- instructions_mismatch
- `3` -- instructions_mismatch
- `10` -- instructions_mismatch
- `9` -- instructions_mismatch
- `6` -- instructions_mismatch
- `18` -- instructions_mismatch
- `17` -- instructions_mismatch
- `19` -- instructions_mismatch
- `7` -- instructions_mismatch
- `21` -- instructions_mismatch

## Field-level values for mismatched items

### `14` / option_text[resp=1] (similarity 0.1875)
- curated: `Fully disagree`
- fresh: `Strongly approve`

### `14` / option_text[resp=4] (similarity 0.3077)
- curated: `Neither agree nor disagree`
- fresh: `Strongly disapprove`

### `12` / option_text[resp=4] (similarity 0.25)
- curated: `Strongly disapprove`
- fresh: `Neither favor nor oppose`

### `12` / option_text[resp=1] (similarity 0.125)
- curated: `Strongly approve`
- fresh: `Favor strongly`

### `29` / option_text[resp=1] (similarity 0.1613)
- curated: `Favor strongly`
- fresh: `Doing more about climate change`

### `29` / option_text[resp=7] (similarity 0.1613)
- curated: `Oppose strongly`
- fresh: `Doing less about climate change`

### `29` / option_text[resp=4] (similarity 0.1667)
- curated: `Neither favor nor oppose`
- fresh: `Doing the right amount`

### `32` / option_text[resp=1] (similarity 0.1)
- curated: `Favor strongly`
- fresh: `Very unlikely to sign petition`

### `32` / option_text[resp=4] (similarity 0.3333)
- curated: `Neither favor nor oppose`
- fresh: `Neither likely nor unlikely to sign the petition`

### `32` / option_text[resp=7] (similarity 0.125)
- curated: `Oppose strongly`
- fresh: `Very likely to sign the petition`

### `11` / option_text[resp=1] (similarity 0.1458)
- curated: `Favor strongly`
- fresh: `Greatly decrease spending on immigration control`

### `11` / option_text[resp=4] (similarity 0.2353)
- curated: `Neither favor nor oppose`
- fresh: `Keep spending on immigration control about the same`

### `11` / option_text[resp=7] (similarity 0.1458)
- curated: `Oppose strongly`
- fresh: `Greatly increase spending on immigration control`

### `33` / option_text[resp=7] (similarity 0.1458)
- curated: `Oppose strongly`
- fresh: `Very likely to vote for the Republican candidate`

### `33` / option_text[resp=1] (similarity 0.125)
- curated: `Favor strongly`
- fresh: `Very likely to vote for the Democratic candidate`

### `33` / option_text[resp=4] (similarity 0.1594)
- curated: `Neither favor nor oppose`
- fresh: `Equally likely to vote for the Democratic as the Republican candidate`

### `20` / option_text[resp=1] (similarity 0.2273)
- curated: `Strongly Democrat`
- fresh: `I absolutely would not`

### `20` / option_text[resp=7] (similarity 0.1053)
- curated: `Strongly Republican`
- fresh: `I absolutely would`

### `22` / option_text[resp=4] (similarity 0.1538)
- curated: `Doing the right amount`
- fresh: `Neither agree nor disagree`

### `22` / option_text[resp=1] (similarity 0.129)
- curated: `Doing more about climate change`
- fresh: `Fully disagree`

### `22` / option_text[resp=7] (similarity 0.1613)
- curated: `Doing less about climate change`
- fresh: `Fully agree`

### `31` / option_text[resp=7] (similarity 0.2812)
- curated: `Very concerned`
- fresh: `Very likely to sign the petition`

### `31` / option_text[resp=1] (similarity 0.2)
- curated: `Not at all concerned`
- fresh: `Very unlikely to sign petition`

### `31` / option_text[resp=4] (similarity 0.1458)
- curated: `Somewhat concerned`
- fresh: `Neither likely nor unlikely to sign the petition`

### `13` / option_text[resp=7] (similarity 0.2632)
- curated: `Very interested`
- fresh: `Make it much easier`

### `13` / option_text[resp=1] (similarity 0.1852)
- curated: `Very uninterested`
- fresh: `Make it much more difficult`

### `28` / option_text[resp=1] (similarity 0.1818)
- curated: `I absolutely would not`
- fresh: `Donald Trump`

### `26` / option_text[resp=1] (similarity 0.2273)
- curated: `I absolutely would not`
- fresh: `Strongly Democrat`

### `26` / option_text[resp=7] (similarity 0.1053)
- curated: `I absolutely would`
- fresh: `Strongly Republican`

### `27` / option_text[resp=1] (similarity 0.1818)
- curated: `I absolutely would not`
- fresh: `Donald Trump`

### `25` / option_text[resp=1] (similarity 0.1818)
- curated: `I absolutely would not`
- fresh: `Strongly liberal`

### `25` / option_text[resp=7] (similarity 0.0476)
- curated: `I absolutely would`
- fresh: `Strongly conservative`

### `24` / option_text[resp=7] (similarity 0.2222)
- curated: `I absolutely would`
- fresh: `Fully agree`

### `24` / option_text[resp=1] (similarity 0.1818)
- curated: `I absolutely would not`
- fresh: `Fully disagree`

### `15` / option_text[resp=7] (similarity 0.2667)
- curated: `Fully agree`
- fresh: `Very interested`

### `15` / option_text[resp=1] (similarity 0.2941)
- curated: `Fully disagree`
- fresh: `Very uninterested`

### `16` / option_text[resp=1] (similarity 0.1818)
- curated: `Fully disagree`
- fresh: `I absolutely would not`

### `16` / option_text[resp=7] (similarity 0.2222)
- curated: `Fully agree`
- fresh: `I absolutely would`

### `10` / option_text[resp=7] (similarity 0.1458)
- curated: `Greatly increase spending on immigration control`
- fresh: `Oppose strongly`

### `10` / option_text[resp=4] (similarity 0.2353)
- curated: `Keep spending on immigration control about the same`
- fresh: `Neither favor nor oppose`

### `10` / option_text[resp=1] (similarity 0.1458)
- curated: `Greatly decrease spending on immigration control`
- fresh: `Favor strongly`

### `18` / option_text[resp=7] (similarity 0.0526)
- curated: `Make it much easier`
- fresh: `I absolutely would`

### `18` / option_text[resp=1] (similarity 0.1481)
- curated: `Make it much more difficult`
- fresh: `I absolutely would not`

### `17` / option_text[resp=7] (similarity 0.2222)
- curated: `Fully agree`
- fresh: `I absolutely would`

### `17` / option_text[resp=1] (similarity 0.1818)
- curated: `Fully disagree`
- fresh: `I absolutely would not`

### `19` / option_text[resp=7] (similarity 0.0476)
- curated: `Strongly conservative`
- fresh: `I absolutely would`

### `19` / option_text[resp=1] (similarity 0.1818)
- curated: `Strongly liberal`
- fresh: `I absolutely would not`

### `21` / option_text[resp=4] (similarity 0.2692)
- curated: `I did not vote`
- fresh: `Neither agree nor disagree`

### `21` / option_text[resp=1] (similarity 0.0714)
- curated: `Donald Trump`
- fresh: `Fully disagree`

### `30` / item_text (similarity 0.1339)
- curated: `2016 vote choice according to Prolific's records (only collected wave1, missing values are from subsequent waves`
- fresh: `increase aid to the poor`

### `14` / item_text (similarity 0.2)
- curated: `At this moment, I feel tense.`
- fresh: `Do you approve or disapprove of the job Donald Trump is doing as president?`

### `12` / item_text (similarity 0.2941)
- curated: `Do you approve or disapprove of the job Donald Trump is doing as president?`
- fresh: `Do you favor or oppose laws that require parents to vaccinate their children using common vaccines (e.g., polio, tetanus, measles, flu)?`

### `29` / item_text (similarity 0.2937)
- curated: `Do you favor or oppose laws that prevent gay or lesbian couples from adopting children, or haven't you thought much about it?`
- fresh: `Do you think the federal government should be doing more about climate change, should be doing less, or is it currently doing the right amount?`

### `32` / item_text (similarity 0.1554)
- curated: `Do you favor or oppose laws that prohibit travel to and from regions in the United States with coronavirus (COVID-19) outbreaks (i.e. a quarantine)?`
- fresh: `increase spending on healthcare`

### `11` / item_text (similarity 0.2426)
- curated: `Do you favor or oppose laws that require parents to vaccinate their children using common vaccines (e.g., polio, tetanus, measles, flu)?`
- fresh: `Should federal spending to control immigration be increased, decreased, or kept the same?`

### `33` / item_text (similarity 0.2538)
- curated: `Do you favor or oppose laws that would require all businesses to pay for their employee's sick leave?`
- fresh: `In the next Presidential election, how likely are you to vote for the candidate from the Democratic Party or the Republican Party?`

### `20` / item_text (similarity 0.0826)
- curated: `Do you think of yourself as a Republican, a Democrat, an Independent, or haven’t you thought much about this?`
- fresh: `Democrats`

### `22` / item_text (similarity 0.1678)
- curated: `Do you think the federal government should be doing more about climate change, should be doing less, or is it currently doing the right amount?`
- fresh: `I have an intense fear of death`

### `31` / item_text (similarity 0.2182)
- curated: `How concerned are you about the coronavirus (COVID-19)?`
- fresh: `increase spending to stimulate the economy`

### `13` / item_text (similarity 0.1359)
- curated: `How interested are you in politics?`
- fresh: `Should the federal government make it more difficult for people to buy a gun than it is now, make it easier for people to buy a gun, or keep these rules about the same as they are now?`

### `34` / item_text (similarity 0.2762)
- curated: `How likely would you be to sign a petition in support of the following issues? --increase aid to the poor`
- fresh: `How concerned are you about the coronavirus (COVID-19)?`

### `36` / item_text (similarity 0.2143)
- curated: `How likely would you be to sign a petition in support of the following issues? --increase spending on healthcare`
- fresh: `Do you favor or oppose laws that would require all businesses to pay for their employee's sick leave?`

### `35` / item_text (similarity 0.2162)
- curated: `How likely would you be to sign a petition in support of the following issues? --increase spending to stimulate the economy`
- fresh: `Do you favor or oppose laws that prohibit travel to and from regions in the United States with coronavirus (COVID-19) outbreaks (i.e. a quarantine)?`

### `28` / item_text (similarity 0.2326)
- curated: `How willing would you be to be friends with people from the following group: Democrats`
- fresh: `2016 vote choice according to Prolific's records`

### `26` / item_text (similarity 0.2407)
- curated: `How willing would you be to be friends with people from the following group: Moderates`
- fresh: `Do you think of youself as a Republican, a Democrat, an Independent, or haven't you thought much about this?`

### `27` / item_text (similarity 0.2955)
- curated: `How willing would you be to be friends with people from the following group: Republicans`
- fresh: `Who did you vote for in the 2016 presidential election?`

### `25` / item_text (similarity 0.2441)
- curated: `How willing would you be to be friends with people from the following groups? --Conservatives`
- fresh: `When it comes to politics, do you think of yourself as liberal, conservative, moderate, or haven't you thought much about this?`

### `24` / item_text (similarity 0.2386)
- curated: `How willing would you be to be friends with people from the following groups? --Liberals`
- fresh: `The values in our country has gone seriously off track`

### `23` / item_text (similarity 0.2474)
- curated: `I find it important to celebrate the 4th of July.`
- fresh: `I worry that I myself or someone from my family will be worse off financially in the near futures`

### `15` / item_text (similarity 0.2059)
- curated: `I have an intense fear of death`
- fresh: `How interested are you in politics`

### `16` / item_text (similarity 0.0722)
- curated: `I worry that I myself or someone from my family will be worse off financially in the near future.`
- fresh: `Liberals`

### `37` / item_text (similarity 0.2385)
- curated: `In the next Presidential election, how likely are you to vote for the candidate from the Democratic Party or the Republican Party?`
- fresh: `I find it important to celebrate the 4th of July`

### `10` / item_text (similarity 0.256)
- curated: `Should federal spending to control immigration be increased, decreased, or kept the same?`
- fresh: `Do you favor or oppose laws that prevent gay or lesbian couples from adopting children, or haven't you thought much about it?`

### `18` / item_text (similarity 0.0489)
- curated: `Should the federal government make it more difficult for people to buy a gun than it is now, make it easier for people to buy a gun, or keep these rules about the same as they are now?`
- fresh: `Moderates`

### `17` / item_text (similarity 0.125)
- curated: `The values in our country have gone seriously off track.`
- fresh: `Conservatives`

### `19` / item_text (similarity 0.0698)
- curated: `When it comes to politics, do you think of yourself as a liberal, conservative, moderate, or haven't you thought much about this?`
- fresh: `Republicans`

### `21` / item_text (similarity 0.2364)
- curated: `Who did you vote for in the 2016 presidential election?`
- fresh: `At this moment, I feel tense`

### `30` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `14` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `12` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `29` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `32` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `11` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `33` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `20` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `22` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `31` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `13` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `34` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `36` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `35` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `28` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `26` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `27` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `25` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `24` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `23` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `15` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `16` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `37` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `2` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `4` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `8` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `1` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `5` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `3` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `10` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `9` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `6` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `18` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `17` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `19` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `7` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

### `21` / instructions (similarity 0.2652)
- curated: `This is part of our multipart study to better understand people's feelings, experiences, and attitudes. Thank you for participating!`
- fresh: `This survey consists of one section where you will complete items about your political attitudes.`

