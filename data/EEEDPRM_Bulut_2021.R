# Paper: https://www.mdpi.com/2624-8611/3/3/23
# Data: https://osf.io/eapd8/
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("./rse_long.csv")
df <- df |>
  select(-country, -wording, -gender2, -agree) |>
  rename(id = person, resp=response)

save(df, file="EEEDPRM_Bulut_2021.Rdata")
write.csv(df, "EEEDPRM_Bulut_2021.csv", row.names=FALSE)
