library(haven)
library(rstudioapi)
library(tidyverse)
setwd(dirname(getActiveDocumentContext()$path))


df_clinic<- read_sav("CFAClinic.sav")

df_cleaned <- df_clinic %>% 
  mutate(id = row_number()) %>%
  pivot_longer(
    cols = matches("^i\\d{2}$"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  rename(cov_gender = sex) %>%
  select(id, item, resp, cov_gender)

write.csv(df_cleaned, "scs_2025_cfaclinic.csv", row.names=FALSE)


df_nonclinic<- read_sav("CFANonClinic.sav")

df_cleaned <- df_nonclinic %>% 
  mutate(id = row_number()) %>%
  pivot_longer(
    cols = matches("^i\\d{2}$"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  rename(cov_gender = sex) %>%
  select(id, item, resp, cov_gender)

write.csv(df_cleaned, "scs_2025_cfanonclinic.csv", row.names=FALSE)

library(haven)
library(rstudioapi)
library(tidyverse)
setwd(dirname(getActiveDocumentContext()$path))


df_usatr <- read_sav("MIUSATR.sav")

df_cleaned <- df_usatr %>% 
  mutate(id = row_number()) %>%
  pivot_longer(
    cols = matches("^SCS\\d{2}$"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  rename(cov_country = country) %>%
  select(id, item, resp, cov_country)

write.csv(df_cleaned, "scs_2025_cfausatr.csv", row.names=FALSE)

