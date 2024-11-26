# Poster: https://www.researchgate.net/profile/Rossella-Caliciuri/publication/382182050_Psychometric_Properties_of_the_Scientific_Reasoning_Scale/links/6690f2a1b15ba55907539c5a/Psychometric-Properties-of-the-Scientific-Reasoning-Scale.pdf 
# Data: https://osf.io/jk9dp/
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)

df <- read_sav("3. CFA&IRT_SRS (n=337).sav")
df <- df |>
  select(ID, starts_with("SRS")) |>
  rename(id=ID)
df <- pivot_longer(df, cols=-id, names_to = "item", values_to="resp")

save(df, file="PPSRS_Caliciuri_2024.Rdata")
write.csv(df, "PPSRS_Caliciuri_2024.csv", row.names=FALSE)