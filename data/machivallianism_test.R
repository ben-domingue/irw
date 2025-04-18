library(dplyr)
library(tidyr)

df <- read.csv("datacsv_imported.csv")


df <- df %>%
  mutate(id = seq(1, n())) %>%
  rename(cov_country = country, cov_education = education, cov_urban = urban,
         cov_gender = gender, cov_engnat = engnat, cov_age = age, cov_hand = hand,
         cov_religion = religion, cov_orientation = orientation, cov_race = race,
         cov_voted = voted, cov_married = married, cov_familysize = familysize,
         cov_major = major)

dfQ_resp <- df %>%
  select(id, matches("^Q.*A$"), starts_with("cov")) %>%
  pivot_longer(cols = matches("^Q.*A$"),
               names_to = "item",
               values_to = "resp") %>%
  mutate(item = substr(item, 1, nchar(item) - 1))
  

dfQ_rt <- df %>%
  select(id, matches("^Q.*E$")) %>%
  pivot_longer(cols = matches("^Q.*E$"),
               names_to = "item",
               values_to = "rt") %>%
  mutate(item = substr(item, 1, nchar(item) - 1))

dfQ <- dfQ_resp %>%
  left_join(dfQ_rt, by = c("id", "item")) %>%
  mutate(
    rt = na_if(rt, ""),
    rt = as.numeric(gsub(",", "", rt)) / 1000
  )

df_tipi <- df %>%
  select(id, starts_with("TIPI"), starts_with("cov")) %>%
  pivot_longer(cols = starts_with("TIPI"),
               names_to = "item",
               values_to = "resp")

df_vcl <- df %>%
  select(id, starts_with("VCL"), starts_with("cov")) %>%
  pivot_longer(cols = starts_with("VCL"),
               names_to = "item",
               values_to = "resp")

write.csv(dfQ, "machivallianism_test_main.csv", row.names = FALSE)
write.csv(df_tipi, "machivallianism_test_tipi.csv", row.names = FALSE)
write.csv(df_vcl, "machivallianism_test_vcl.csv", row.names = FALSE)
