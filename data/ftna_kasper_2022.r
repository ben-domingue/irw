# Paper: 
# Data: https://dataverse.harvard.edu/file.xhtml?fileId=5429719&version=1.0
library(haven)
library(dplyr)
library(tidyr)

df <- read_dta("data_ftna_publication.dta")
df2 <- df |>
  select(id = id_ftna, year, female, school_id, private,
         # ftna = secondary
         # psle = primary
         contains("_ftna_num"), contains("_psle_num"),
         # subjects where very few students had grades
         -c(agriculture_ftna_num:theatre_ftna_num)) |>
  # make year a factor
  mutate(year = factor(year)) |>
  # only students with all tests
  drop_na(contains("_num"), female, private, year)

ftna_df <- df2 |>
  select(id, year, female, school_id, private, contains("_ftna_num")) |>
  rename(cov_year=year, cov_female=female, cluster_id=school_id, cov_private=private)
ftna_df <- ftna_df |>
  pivot_longer(contains("ftna"), names_to="item", values_to="resp") |>
  drop_na(resp) 
ftna_df$item <- gsub("_ftna", "", ftna_df$item)
ftna_df$wave <- 1

psle_df <- df2 |>
  select(id, year, female, school_id, private, contains("_psle_num")) |>
  rename(cov_year=year, cov_female=female, cluster_id=school_id, cov_private=private)
psle_df <- psle_df |>
  pivot_longer(contains("psle"), names_to="item", values_to="resp") |>
  drop_na(resp) 
psle_df$item <- gsub("_psle", "", psle_df$item)
psle_df$wave <- 0

f_df <- rbind(ftna_df, psle_df)

save(f_df, file="ftna_kasper_2022.rdata")
write.csv(f_df, "ftna_kasper_2022.csv", row.names=FALSE)