library(haven)
library(dplyr)
library(tidyr)

df <- read_sav("SSD12 Validation Data.sav")

colnames(df) <- tolower(colnames(df))

df$id <- seq(1, nrow(df))

df <- df %>%
  select(id, group, age, gender, socioeconomicstatus, maritalstatus, education, a1:a12) %>%
  rename(cov_age = age,
         cov_gender = gender,
         cov_socioeconomicstatus = socioeconomicstatus,
         cov_maritalstatus = maritalstatus,
         cov_education = education) %>%
  pivot_longer(-c(id, group, cov_age, cov_gender, cov_socioeconomicstatus, cov_maritalstatus, cov_education),
               names_to = "item",
               values_to = "resp") %>%
  select(id, group, cov_age, cov_gender, cov_socioeconomicstatus, cov_maritalstatus, cov_education, item, resp)

table(df$resp)

write.csv(df, "ssd12_habib_2025.csv", row.names=FALSE)
