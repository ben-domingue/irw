setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)
library(jmvReadWrite)

df <- read_omv("Dataset.omv")
df <- df %>%
  mutate(id=row_number())
df_long <- df %>%
  pivot_longer(cols = 1:38,
               names_to = "item",
               values_to = "resp"
               ) %>%
  select(id, item, resp)

write_csv(df_long, "wellbeing_kocar_2025.csv")
