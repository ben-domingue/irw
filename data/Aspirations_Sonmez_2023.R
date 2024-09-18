# Paper: https://www.inderscienceonline.com/doi/abs/10.1504/IJHD.2023.131527
# Data: https://osf.io/psgk8/
library(haven)
library(dplyr)
library(tidyr)

df <- read_sav('Aspirations_CFA.sav')
df <- df |>
  rename(id=ParticipantNo) |>
  select(id, starts_with("Asp"))
df <- pivot_longer(df, cols=-id, values_to = "resp", names_to="item")

save(df, file="Aspirations_Sonmez_2023.Rdata")
write.csv(df, "Aspirations_Sonmez_2023.csv", row.names=FALSE)