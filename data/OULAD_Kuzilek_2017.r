# Data: https://analyse.kmi.open.ac.uk/open_dataset
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("studentAssessment.csv")
df <- df |>
  select(-date_submitted, -is_banked) |>
  rename(item=id_assessment, id=id_student, resp=score)

save(df, file="OULAD_Kuzilek_2017.Rdata")
write.csv(df, "OULAD_Kuzilek_2017.csv", row.names=FALSE)