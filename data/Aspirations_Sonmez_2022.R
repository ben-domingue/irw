library(haven)
library(dplyr)
library(tidyr)

df <- read_sav('Aspirations_CFA.sav')
df <- df |>
  rename(id=ParticipantNo) |>
  select(id, starts_with("Asp"))
df <- pivot_longer(df, cols=-id, values_to = "resp", names_to="item")

save(df, file="Aspirations_Sonmez_2022.Rdata")
write.csv(df, "Aspirations_Sonmez_2022.csv", row.names=FALSE)