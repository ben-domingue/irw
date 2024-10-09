library(tidyr)
library(dplyr)

df <- read.csv("Adherence_Measurement_ARV_Rings_Psychometrics.csv")

df <- df %>%
  select(KEY, q_s_001:q_s_112, matches("q_f_ring|q_f_gel|q_f_pill")) %>%
  pivot_longer(c(q_s_001:q_s_112, matches("q_f_ring|q_f_gel|q_f_pill")),
               names_to = "item",
               values_to = "resp") %>%
  filter(!(resp %in% c(99, 0)) & !(is.na(resp)))  %>%
  rename(id = KEY)

write.csv(df, "Adherence_Zissette_2018.csv", row.names=FALSE)


