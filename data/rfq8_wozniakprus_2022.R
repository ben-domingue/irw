setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)

df <- read_tsv("Wozniak-Prus_et_al_RFQ-8_study[76389].tab")
df_long <- df %>% 
  mutate(id=row_number()) %>%
  pivot_longer(
    cols = RFQ1:RFQ8,
    names_to = "item",
    values_to = "resp"
  ) %>%
  select(id, cov_gender=Gender, cov_age=Age, item, resp)
write_csv(df_long, "rfq8_wozniakprus_2022.csv")
