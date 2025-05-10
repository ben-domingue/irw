# Paper: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0317113#sec017
# Data: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0317113#sec017
library(haven)
library(dplyr)
library(tidyr)
library(readxl)

df <-read_excel("journal.pone.0317113.s001.xlsx")
df <- df |>
  rename(id=SLN, cov_age=AGEN, cov_sex=sex, cov_education=educat3, 
         cov_occupation=Occupationnew, cov_live=live3, cov_marital=marital3,
         cov_income_source=incomesourse, cov_socioeconomic=SES) |>
  select(starts_with("QoL"), id, starts_with("cov"))
df <- pivot_longer(df, cols=-c(id, starts_with("cov")), values_to="resp", names_to="item")

save(df, file="qol_islam_2025.Rdata")
write.csv(df, "qol_islam_2025.csv", row.names=FALSE)