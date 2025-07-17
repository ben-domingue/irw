library(dplyr)
library(tidyr)

df <- read.delim("Database_Jahan et al.tab", header = TRUE, sep = "\t")

df <- df %>%
  rename(id = serialno) %>%
  pivot_longer(-id,
               names_to = "item",
               values_to = "resp")


df_fear <- df %>%
  filter(grepl("^fear", item))

df_dep <- df %>%
  filter(grepl("^de", item))

df_anx <- df %>%
  filter(grepl("^anx", item))

write.csv(df_fear, "fcv19s_hossain_2022_fear.csv", row.names = FALSE)
write.csv(df_dep, "fcv19s_hossain_2022_depression.csv", row.names = FALSE)
write.csv(df_anx, "fcv19s_hossain_2022_anxiety.csv", row.names = FALSE)