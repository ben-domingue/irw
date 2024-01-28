library(tidyverse)
library(readr)
library(janitor)

df <- read_csv('IAT_data_imported.csv')

df <- df |>
  clean_names(case = 'snake') |>
  select(-internet_usg,
         -internet_add,
         -gender,
         -age_grp,
         -level_study,
         -yr_study,
         -discipline,
         -filter,
         -sqr_total,
         -new_sqr_total,
         -sqr_catg) |>
  mutate(id = as.numeric(id)) |>
  mutate(stay_online = if_else(stay_online == 99 | stay_online == 0, NA, stay_online),
         neglect_chores = if_else(neglect_chores == 99 | neglect_chores == 0, NA, neglect_chores),
         excitement = if_else(excitement == 99 | excitement == 0, NA, excitement),
         relationships = if_else(relationships == 99 | relationships == 0, NA, relationships),
         life_complaint = if_else(life_complaint == 99 | life_complaint == 0, NA, life_complaint),
         school_work = if_else(school_work == 99 | school_work == 0, NA, school_work),
         email_socialmedia = if_else(email_socialmedia == 99 | email_socialmedia == 0, NA, email_socialmedia),
         job_performance = if_else(job_performance == 99 | job_performance == 0, NA, job_performance),
         defensive_secretive = if_else(defensive_secretive == 99 | defensive_secretive == 0, NA, defensive_secretive),
         disturbing_thoughts = if_else(disturbing_thoughts == 99 | disturbing_thoughts == 0, NA, disturbing_thoughts),
         online_anticipation = if_else(online_anticipation == 99 | online_anticipation == 0, NA, online_anticipation),
         life_no_internet = if_else(life_no_internet == 99 | life_no_internet == 0, NA, life_no_internet),
         act_annoyed = if_else(act_annoyed == 99 | act_annoyed == 0, NA, act_annoyed),
         late_night_logins = if_else(late_night_logins == 99 | late_night_logins == 0, NA, late_night_logins),
         feel_preoccupied = if_else(feel_preoccupied == 99 | feel_preoccupied == 0, NA, feel_preoccupied),
         online_glued = if_else(online_glued == 99 | online_glued == 0, NA, online_glued),
         time_cutdown = if_else(time_cutdown == 99 | time_cutdown == 0, NA, time_cutdown),
         hide_online = if_else(hide_online == 99 | hide_online == 0, NA, hide_online),
         more_online_time = if_else(more_online_time == 99 | more_online_time == 0, NA, more_online_time),
         feel_depressed = if_else(feel_depressed == 99 | feel_depressed == 0, NA, feel_depressed),
         headache = if_else(headache == 7, NA, headache),
         appetite = if_else(appetite == 7, NA, appetite),
         sleep = if_else(sleep == 7, NA, sleep),
         fear = if_else(fear == 7, NA, fear),
         shaking = if_else(shaking == 7, NA, shaking),
         nervous = if_else(nervous == 7, NA, nervous),
         digestion = if_else(digestion == 7, NA, digestion),
         troubled = if_else(troubled == 7, NA, troubled),
         unhappy = if_else(unhappy == 7, NA, unhappy),
         cry = if_else(cry == 7, NA, cry),
         enjoyment = if_else(enjoyment == 7, NA, enjoyment),
         decisions = if_else(decisions == 7, NA, decisions),
         work = if_else(work == 7, NA, work),
         play = if_else(play == 7, NA, play),
         interest = if_else(interest == 7, NA, interest),
         worthless = if_else(worthless == 7, NA, worthless),
         suicide = if_else(suicide == 7, NA, suicide),
         tiredness = if_else(tiredness == 7, NA, tiredness),
         uncomfortable = if_else(uncomfortable == 7, NA, uncomfortable),
         easily_tired = if_else(easily_tired == 7, NA, easily_tired)) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T)

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  # drop character item variable
  select(id, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="mental_health_malawi.Rdata")
