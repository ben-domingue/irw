setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)

load("us1890s_votes.rda")
df <- us1890s_votes
votes52 <- df$H52 %>%
  mutate(wave = "H52")
votes53 <- df$H53 %>%
  mutate(wave = "H53")
votes54 <- df$H54 %>%
  mutate(wave = "H54")

votes52_long <- votes52 %>%
  rownames_to_column(var = "id") %>%
  pivot_longer(
    cols = 2:305,
    names_to = "item",
    values_to = "resp"
  ) %>%
  select(id, wave, item, resp)

votes53_long <- votes53 %>%
  rownames_to_column(var = "id") %>%
  pivot_longer(
    cols = 2:374,
    names_to = "item",
    values_to = "resp"
  ) %>%
  select(id, wave, item, resp)
  
votes54_long <- votes54 %>%
  rownames_to_column(var = "id") %>%
  pivot_longer(
    cols = 2:163,
    names_to = "item",
    values_to = "resp"
  ) %>%
  select(id, wave, item, resp)

df_long <- bind_rows(votes52_long, votes53_long, votes54_long) %>%
  mutate(resp = ifelse(resp == 2, NA, resp))
write_csv(df_long, "issueirt_votes_shin_2024.csv")
