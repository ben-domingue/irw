library(tidyverse)
library(haven)

df <- read_delim('Total data 6 samples.csv', delim = ';')

#standardize column names
names(df) <- tolower(names(df))
# Covert to long format
df_long <- df %>%
  mutate(cov_sample = case_when(
    studio == 100 ~ "A",
    studio == 200 ~ "B",
    studio == 300 ~ "C",
    studio == 400 ~ "D",
    studio == 500 ~ "E",
    studio == 600 ~ "F",
    TRUE ~ NA_character_
  )) %>%
  # `id` restarts inside each of the six samples, so one id meant several
  # people: 3,024 excess id+item rows (irw#1842 block E). The sample is what
  # separates them and it stays a column.
  #
  # 300 excess rows survive this and are a second, smaller problem: within a
  # single sample the source file still repeats an id. That needs the source
  # to resolve -- do not dedupe it, the responses conflict.
  mutate(id = paste0(cov_sample, "_", id)) %>%
  pivot_longer(
    cols = c(oi1, sk1, m1, i1, ch1, sk2, m2, i2, oi2, ch2, sj1, sj2),
    names_to = "item",
    values_to = "resp"
  ) %>%
  select(id, item, resp, cov_sample)
#Export Data
write.csv(df_long, "selfcompassionscale_shortform_fuochi_2025.csv", row.names = FALSE)
