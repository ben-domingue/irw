library(tidyr)
library(dplyr)
library(stringr)

df <- load('CDM_AlcoholApplication_Data.RData')

Q0

Q0$item <- c("arapi01", "arapi02", "arapi03", "arapi04", "arapi05",
             "arapi06", "arapi07", "arapi08", "arapi09", "arapi10", "arapi11",
             "arapi12", "arapi13", "arapi14", "arapi15", "arapi16", "arapi17",
             "arapi18", "arapi19", "arapi20", "arapi21", "arapi22", "arapi23",
             "absi01", "absi02", "absi03", "absi04", "absi05", "absi06", "absi07",
             "absi08", "absi09", "absi10", "absi11", "absi12", "absi13", "absi14",
             "absi15", "absi16", "absi17")
data0$id <- seq(1, nrow(data0))

dt <- data0 %>%
  select(c("id", "arapi01", "arapi02", "arapi03", "arapi04", "arapi05",
           "arapi06", "arapi07", "arapi08", "arapi09", "arapi10", "arapi11",
           "arapi12", "arapi13", "arapi14", "arapi15", "arapi16", "arapi17",
           "arapi18", "arapi19", "arapi20", "arapi21", "arapi22", "arapi23",
           "absi01", "absi02", "absi03", "absi04", "absi05", "absi06", "absi07",
           "absi08", "absi09", "absi10", "absi11", "absi12", "absi13", "absi14",
           "absi15", "absi16", "absi17")) %>%
  pivot_longer(-id,
               names_to = "item",
               values_to = "resp")

fin <- left_join(dt, Q0, by = "item")

fin <- fin %>%
  rename("Qmatrix__AP" = "V1", "Qmatrix__AN" = "V2", "Qmatrix__HO" = "V3", "Qmatrix__DE" = "V4")

fin_rapi <- fin %>%
  filter(!str_starts(item, "absi"))

fin_bsi <- fin %>%
  filter(!str_starts(item, "arapi"))

write.csv(fin_rapi, "cdm_mentalhealth_tan_2023_rapi.csv", row.names=FALSE)
write.csv(fin_bsi, "cdm_mentalhealth_tan_2023_bsi.csv", row.names=FALSE)
