# IL-HTE Econ, 46/47: Glatz (2023) PeerJ - Language/Math
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# This study tested two interventions, language and math, but used one control group. I am separating these out. T1 is baseline, T2 is followup.

# the wide file has the intervention info
glatz_wide <- read_csv(glue("{raw}/46 GraphoGame-NL_2015_BehaviouralData.csv")) |> 
  select(s_id = idChild, cluster_id = idClass, treat = Cond,
         cov_country = Country,
         cov_age = T1.AgeF,
         cov_male = Sex,
         cov_bilingual = Lang,
         cov_risk = FamRisk) |> 
  mutate(cov_male = if_else(cov_male == "male", 1, 0),
         cov_risk = if_else(cov_risk == "yes", 1, 0),
         cov_bilingual = if_else(cov_bilingual == "multi", 1, 0))

glatz_app <- read_csv(glue("{raw}/46 GraphoGame-NL_2015_GameData.csv")) |> 
  select(s_id = idChild, session, lvl, correctResponse, result,
         rt = trialRTs) |> 
  mutate(score = if_else(result == "Correct", 1, 0),
         item = glue("{lvl}_{correctResponse}")) |> 
  select(-c(lvl, correctResponse)) |> 
  mutate(word = substr(item, 1, 6),
         test = if_else(word %in% c("Letter", "SoundD", "Lexica"), "Lang.", "Math")) |> 
  # some of the numeric ones are super sparse, just keep ones with enough responses
  # to justify IRT model
  group_by(item) |> 
  mutate(item_n = n()) |> 
  filter(item_n > 200) |> 
  ungroup() |> 
  # get rid of lexical because the items are not labelled, sadly
  filter(word != "Lexica",
         # NumberKnowledge1_2 is all correct, needs to be removed
         item != "NumberKnowledge1_2"
         )

# separate into lang and math
glatz2023_a_p <- glatz_wide |> 
  filter(treat != "Math") |> 
  mutate(treat = if_else(treat == "Passive", 0, 1))

glatz2023_b_p <- glatz_wide |> 
  filter(treat != "Read") |> 
  mutate(treat = if_else(treat == "Passive", 0, 1)) 

# bring in the endline data
glatz2023_i <- glatz_app |> 
  mutate(time = if_else(session == "T2", 1, 0)) |> 
  rename(outcome = test) |> 
  arrange(s_id, item, time) |> 
  select(s_id, item, time, rt, score, outcome)

glatz2023_a <- glatz2023_i |> 
  filter(outcome == "Lang.") |> 
  left_join(glatz2023_a_p, by = "s_id") |> 
  drop_na(treat)

glatz2023_b <- glatz2023_i |> 
  filter(outcome == "Math") |> 
  left_join(glatz2023_b_p, by = "s_id") |> 
  drop_na(treat)

rm(glatz2023_i, glatz2023_b_p, glatz2023_a_p, glatz2023_p,
   glatz_pre, glatz_app, glatz_wide)
