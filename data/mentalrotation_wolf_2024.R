library(dplyr)
library(tidyr)

df <- read.csv("Combined_Subject_Data.csv")

df <- df %>%
  rename(id = "Participant..",
         cov_age = "Age",
         cov_sex = "Sex",
         cov_year = "Year",
         cov_major = "Major",
         itemcov_cbsheet = "CB.Sheet",
         itemcov_shape = "Shape",
         itemcov_angle = "Angle",
         resp = "Correct",
         resp_raw = "Response..answer.")

df$item <- paste(df$itemcov_cbsheet, df$itemcov_shape, df$itemcov_angle, sep = "--")

df <- df %>%
  select(id, matches("^cov|^itemcov"), item, resp, resp_raw)

df <- df %>%
  mutate(across(starts_with("cov"), ~ tolower(as.character(.))))

write.csv(df, "mentalrotation_wolf_2024.csv", row.names = FALSE)
