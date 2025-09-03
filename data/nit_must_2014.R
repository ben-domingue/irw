setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)

df <- read_delim("FE_1933_2006_data.csv", delim = ";", col_names = FALSE)

df <- df %>%
  mutate(id=row_number()) %>%
  rename(cov_group=X1, cov_gender=X3, cov_grade=X4, cov_age=X5) %>%
  mutate(cov_age = na_if(cov_age, -9)) %>%
  mutate(across(all_of(names(.)[6:105]),  ~ na_if(.x, -9))) %>%
  mutate(across(all_of(names(.)[109:292]), ~ na_if(.x, -9))) %>%
  select(-all_of(names(df)[106:108]), -X2)

df_long <- df %>%
  pivot_longer(cols = all_of(names(df)[5:288]),
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = ifelse(resp == 9, NA, resp)) %>%
  select(id, everything())

write_csv(df_long, "nit_must_2014.csv")
