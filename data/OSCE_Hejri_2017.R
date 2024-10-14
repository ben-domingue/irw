library(readxl)
library(dplyr)

df <- read_xlsx("Jeehp-14-19_raw data.xlsx")

df <- df %>%
  select(code, q1:q10) %>%
  pivot_longer(c(q1:q10),
               names_to = "item",
               values_to = "resp") |>
  filter(!is.na(resp)) |>
  rename(id = code)

write.csv(df, "OSCE_Hejri_2017.csv", row.names=FALSE)