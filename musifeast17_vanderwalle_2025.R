setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)
library(haven)

df <- read_csv("M17_raw_data_cleaned.csv")

# convert date to unix time
df$unix_time <- as.numeric(as.POSIXct(gsub("\\.", ":", gsub("h", ":", gsub("_", " ", df$date))), 
                                      format = "%Y-%m-%d %H:%M:%OS", tz = "UTC"))
# select items
binary_items <- c('correct_genre', 'correct_time')
clip_items <- df %>%
  select(starts_with("clip_response.")) %>%
  select(-clip_response.Thoughts, -clip_response.otherThoughts,
         -clip_response.Genre_1, -clip_response.Genre_2,
         -clip_response.Creation_time, -clip_response.Creation_location,
         -clip_response.contextual) %>%
  names()
genre_items <- df %>%
  select(starts_with("genre_exposure.")) %>%
  names()
all_items <- c(clip_items, genre_items, binary_items)

# convert to longformat
df_long <- df %>%
  select(id = PROLIFIC_PID,
         cov_group = group,
         cov_age = demographics.age,
         cov_gender = demographics.gender,
         cov_headphone = demographics.headphones, #reported headphone usage for the study
         cov_HI = demographics.hearingImpariments, #reported hearing impairment
         cov_edu = demographics.education,
         cov_musicianship = demographics.musicianIdentification, #self-reported musicianship level
         date = unix_time,
         all_of(all_items)
         ) %>%
  # recode TRUE/FALSE to 1/0
  mutate(across(all_of(binary_items), ~ as.numeric(.))) %>%
  pivot_longer(
    cols = all_of(all_items),
    names_to = "item",
    values_to = "resp"
  )

write_csv(df_long, "musifeast17_vanderwalle_2025.csv")
