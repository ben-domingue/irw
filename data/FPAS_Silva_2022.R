library(dplyr)
library(tidyr)

df <- read.csv("DATA_FPAS_2022.csv")

df <- df %>%
  select(record_id, fpas_1:fpas_18) %>%
  rename(id = record_id)

df <- df %>%
  pivot_longer(fpas_1:fpas_18,
               names_to = "item",
               values_to = "resp")

write.csv(df, "FPAS_Silva_2022.csv", row.names=FALSE)
