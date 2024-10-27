# Paper:
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/LUUDQC
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)

df <- read.xlsx("Qaslu.xlsx")
df <- df |>
  mutate(id=row_number()) |>
  select(starts_with("Item"), id)
df <- pivot_longer(df, cols=-id, names_to="item", values_to="resp")

save(df, file="QaSLU_Prado_2024.Rdata")
write.csv(df, "QaSLU_Prado_2024.csv", row.names=FALSE)