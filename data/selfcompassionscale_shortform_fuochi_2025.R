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
  pivot_longer(
    cols = c(oi1, sk1, m1, i1, ch1, sk2, m2, i2, oi2, ch2, sj1, sj2),
    names_to = "item",
    values_to = "resp"
  ) %>%
  select(id, item, resp, cov_sample)
#Export Data
write.csv(df_long, "selfcompassionscale_shortform_fuochi_2025.csv", row.names = FALSE)
