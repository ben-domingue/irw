library(dplyr)
library(tidyr)

df <- read.csv("data.csv")

df$id <- seq(1, nrow(df))

df_vs <- df %>%
  select(id, matches("^V.*s$")) %>%
  pivot_longer(cols = matches("^V.*s$"),
               names_to = "item",
               values_to = "resp") %>%
  mutate(item = substr(item, 1, nchar(item) - 1))

df_va <- df %>%
  select(id, matches("^V.*a$")) %>%
  pivot_longer(cols = matches("^V.*a$"),
               names_to = "item",
               values_to = "raw_resp") %>%
  mutate(item = substr(item, 1, nchar(item) - 1))

df_ve <- df %>%
  select(id, matches("^V.*e$")) %>%
  pivot_longer(cols = matches("^V.*e$"),
               names_to = "item",
               values_to = "rt") %>%
  mutate(item = substr(item, 1, nchar(item) - 1)) %>%
  mutate(rt = as.numeric(rt) / 1000)

df_v <- df_vs %>%
  left_join(df_va, by = c("id", "item")) %>%
  left_join(df_ve, by = c("id", "item"))



df_rs <- df %>%
  select(id, matches("^R.*s$")) %>%
  pivot_longer(cols = matches("^R.*s$"),
               names_to = "item",
               values_to = "resp") %>%
  mutate(item = substr(item, 1, nchar(item) - 1))

df_ra <- df %>%
  select(id, matches("^R.*a$")) %>%
  pivot_longer(cols = matches("^R.*a$"),
               names_to = "item",
               values_to = "raw_resp") %>%
  mutate(item = substr(item, 1, nchar(item) - 1))

df_re <- df %>%
  select(id, matches("^R.*e$")) %>%
  pivot_longer(cols = matches("^R.*e$"),
               names_to = "item",
               values_to = "rt") %>%
  mutate(item = substr(item, 1, nchar(item) - 1)) %>%
  mutate(rt = as.numeric(rt) / 1000)

df_r <- df_rs %>%
  left_join(df_ra, by = c("id", "item")) %>%
  left_join(df_re, by = c("id", "item"))




df_ms <- df %>%
  select(id, matches("^M.*s$")) %>%
  pivot_longer(cols = matches("^M.*s$"),
               names_to = "item",
               values_to = "resp") %>%
  mutate(item = substr(item, 1, nchar(item) - 1))

df_ma <- df %>%
  select(id, matches("^M.*a$")) %>%
  pivot_longer(cols = matches("^M.*a$"),
               names_to = "item",
               values_to = "raw_resp") %>%
  mutate(item = substr(item, 1, nchar(item) - 1))

df_me <- df %>%
  select(id, matches("^M.*e$")) %>%
  pivot_longer(cols = matches("^M.*e$"),
               names_to = "item",
               values_to = "rt") %>%
  mutate(item = substr(item, 1, nchar(item) - 1)) %>%
  mutate(rt = as.numeric(rt) / 1000)

df_m <- df_ms %>%
  left_join(df_ma, by = c("id", "item")) %>%
  left_join(df_me, by = c("id", "item"))



write.csv(df_v, "fullscaleiq_vocab.csv", row.names = FALSE)
write.csv(df_r, "fullscaleiq_mentalrotation.csv", row.names = FALSE)
write.csv(df_m, "fullscaleiq_memory.csv", row.names = FALSE)
