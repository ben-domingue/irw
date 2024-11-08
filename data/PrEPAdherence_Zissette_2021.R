library(tidyr)
library(dplyr)

df <- read.table("Screening and adherence monitoring for oral PrEP.tab", header=TRUE, sep="\t")

df$id <- seq(1, nrow(df))

df_final <- df %>%
  select(id, starts_with("q_s_"), matches("^q_m_.*ftp"), matches("^q_m_.*ntp")) %>%
  pivot_longer(-id,
               names_to = 'item',
               values_to = 'resp') %>%
  filter(!is.na(resp))


write.csv(df_final, "PrEPAdherence_Zissette_2021.csv", row.names=FALSE)
