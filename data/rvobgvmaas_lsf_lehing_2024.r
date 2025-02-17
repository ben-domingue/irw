# Paper: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0316374#sec025
# Data: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0316374#sec025
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

data_df <- read.xlsx("journal.pone.0316374.s002.xlsx")
data_df <- data_df|>
  mutate(id= row_number()) |>
  rename(cov_age=age_t1, cov_child_number=child_number_t1) |>
  mutate(cov_age = na_if(cov_age, -77), cov_child_number = na_if(cov_child_number, -77))

maas_t1_df <- data_df %>%
  select(id, cov_age, cov_child_number, starts_with("maas") & ends_with("t1")& !contains("sum")&!contains("r"))
maas_t1_df  <- remove_na(maas_t1_df)
maas_t1_df <- pivot_longer(maas_t1_df, cols=-c(id, cov_age, cov_child_number), names_to="item", values_to="resp")

maas_t1r_df <- data_df %>%
  select(id, cov_age, cov_child_number, starts_with("maas") & ends_with("t1")& !contains("sum")&contains("r"))
maas_t1r_df  <- remove_na(maas_t1r_df)
maas_t1r_df <- pivot_longer(maas_t1r_df, cols=-c(id, cov_age, cov_child_number), names_to="item", values_to="resp")

mass1_df <- rbind(maas_t1_df,maas_t1r_df)

maas_t2_df <- data_df %>%
  select(id, cov_age, cov_child_number, starts_with("maas") & ends_with("t2")& !contains("sum")&!contains("r"))
maas_t2_df  <- remove_na(maas_t2_df)
maas_t2_df <- pivot_longer(maas_t2_df, cols=-c(id, cov_age, cov_child_number), names_to="item", values_to="resp")

maas_t2r_df <- data_df %>%
  select(id, cov_age, cov_child_number, starts_with("maas") & ends_with("t1")& !contains("sum")&contains("r"))
maas_t2r_df  <- remove_na(maas_t2r_df)
maas_t2r_df <- pivot_longer(maas_t2r_df, cols=-c(id, cov_age, cov_child_number), names_to="item", values_to="resp")

mass2_df <- rbind(maas_t2_df,maas_t2r_df)

mass1_df $wave <- 0
mass2_df $wave <- 1

maas_df <- rbind(mass1_df,mass2_df)

save(maas_df, file="rvobgvmaas_lsf_lehing_2024.Rdata")
write.csv(maas_df, "rvobgvmaas_lsf_lehing_2024.csv", row.names=FALSE)