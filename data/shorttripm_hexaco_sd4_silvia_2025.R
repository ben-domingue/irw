setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)

df <- read_csv("tripm_data_osf.csv")

# Short TriPM
df_tripm <- df %>%
  select(id, starts_with("tripm_"), cov_age=age, cov_gender=gender, cov_edu=ed_level) %>%
  pivot_longer(cols = starts_with("tripm_"),
               names_to = "item",
               values_to = "resp")
write_csv(df_tripm, "shorttripm_silvia_2025.csv")

# HEXACO personality traits
df_hexaco <- df %>%
  filter(dataset=="Vulgar_Humor") %>%
  select(id, starts_with("hxco_"), cov_age=age, cov_gender=gender, cov_edu=ed_level) %>%
  pivot_longer(cols = starts_with("hxco_"),
               names_to = "item",
               values_to = "resp")
write_csv(df_hexaco, "hexaco_silvia_2025.csv")

# Short Dark Tetrad Scale (SD4)
df_sd4 <- df %>%
  filter(dataset=="Vulgar_Humor") %>%
  select(id, starts_with("sd4_"), cov_age=age, cov_gender=gender, cov_edu=ed_level) %>%
  pivot_longer(cols = starts_with("sd4_"),
               names_to = "item",
               values_to = "resp")
write_csv(df_sd4, "sd4_silvia_2025.csv")
