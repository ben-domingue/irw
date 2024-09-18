# Paper: https://osf.io/ztycp/
# Data: https://osf.io/ztycp/
library(dplyr)
library(tidyr)
library(haven)

df <- read.csv("SAmb_R.csv")
df <- df |>
  select(id, starts_with("samb"), -SAmb_tot)
df <- pivot_longer(df, cols=-id, names_to="item", values_to="resp")

save(df, file="SAS_Deters_2022.Rdata")
write.csv(df, "SAS_Deters_2022.csv", row.names=FALSE)
