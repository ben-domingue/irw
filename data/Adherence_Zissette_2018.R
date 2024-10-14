library(tidyr)
library(dplyr)

df <- read.csv("Adherence_Measurement_ARV_Rings_Psychometrics.csv")

df <- df %>%
  select(KEY, matches("SDB")) %>%
  pivot_longer(c(matches("SDB")),
               names_to = "item",
               values_to = "resp") %>%
  filter(!(resp %in% c(99, 0)) & !(is.na(resp)))  %>%
  rename(id = KEY)


write.csv(df, "Adherence_Zissette_2018_SDB.csv", row.names=FALSE)
