# Paper: https://link.springer.com/article/10.1007/s12144-021-02497-7#Sec2
# Data: https://osf.io/4jb6k/
library(readxl)
library(dplyr)
library(tidyr)
library(haven)

df <- read_excel("lshse_complete_database.xlsx")
df <- df |>
  select(id, starts_with("alu"))
df <- pivot_longer(df, cols=-id, names_to = "item", values_to = "resp")

save(df, file="LSHS-E_Quidaja_2022.Rdata")
write.csv(df, "LSHS-E_Quidaja_2022.csv", row.names=FALSE)
