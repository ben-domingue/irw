library(tidyr)
library(dplyr)
library(stringr)

df <- read.csv("data.csv")

df_gcbs <- df %>%
  mutate(id = row_number()) %>%
  select(id, education,	urban, gender, engnat, age, hand, religion, orientation,
         race, voted, married, familysize, major, starts_with("Q")) %>%
  pivot_longer(
    cols = starts_with("Q"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  mutate(item_num = str_remove(item, "Q"),
         rt_col = paste0("E", item_num)) %>%
  left_join(
    df %>% mutate(id = row_number()) %>%
      select(id, starts_with("E")) %>%
      pivot_longer(cols = starts_with("E"),
                   names_to = "rt_col",
                   values_to = "rt"),
    by = c("id", "rt_col")
  ) %>%
  rename(cov_education = education, cov_urban = urban, cov_gender = gender,
         cov_engnat = engnat, cov_age = age, cov_hand = hand, cov_religion = religion,
         cov_orientation = orientation, cov_race = race, cov_voted = voted,
         cov_married = married, cov_familysize = familysize, cov_major = major) %>%
  select(id, item, resp, rt, starts_with("cov"))

df_tipi <- df %>%
  mutate(id = row_number()) %>%
  select(id, education,	urban, gender, engnat, age, hand, religion, orientation,
         race, voted, married, familysize, major, starts_with("TIPI")) %>%
  pivot_longer(
    cols = starts_with("TIPI"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  rename(cov_education = education, cov_urban = urban, cov_gender = gender,
         cov_engnat = engnat, cov_age = age, cov_hand = hand, cov_religion = religion,
         cov_orientation = orientation, cov_race = race, cov_voted = voted,
         cov_married = married, cov_familysize = familysize, cov_major = major)
  

df_vcl <- df %>%
  mutate(id = row_number()) %>%
  select(id, education,	urban, gender, engnat, age, hand, religion, orientation,
         race, voted, married, familysize, major, starts_with("VCL")) %>%
  pivot_longer(
    cols = starts_with("VCL"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  rename(cov_education = education, cov_urban = urban, cov_gender = gender,
         cov_engnat = engnat, cov_age = age, cov_hand = hand, cov_religion = religion,
         cov_orientation = orientation, cov_race = race, cov_voted = voted,
         cov_married = married, cov_familysize = familysize, cov_major = major)

write.csv(df_gcbs, "gcbs_brotherton_2013.csv", row.names=FALSE)
write.csv(df_tipi, "gcbs_brotherton_2013_tipi.csv", row.names=FALSE)
write.csv(df_vcl, "gcbs_brotherton_2013_vcl.csv", row.names=FALSE)
