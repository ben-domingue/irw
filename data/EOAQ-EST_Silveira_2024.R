library(readxl)
library(tidyr)
library(dplyr)

df <- read_xlsx('data.xlsx')

df <- df %>%
  select(ID, Q1:Q14) %>%
  rename(id = ID)

df <- df %>%
  pivot_longer(Q1:Q14,
               names_to = "item",
               values_to = "resp")

write.csv(df, 'EOAQ-EST_Silveira_2024.csv')
