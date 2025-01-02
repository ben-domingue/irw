# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/YRLEAY
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readxl)

df <- read_excel("no_Names_coding-0623_forupload.xlsx", sheet = "data")
df$id <- seq_len(nrow(df))
df <- df |>
  select(id, starts_with("item"))
df[df == 9999] <- NA
df <- df[!apply(df[, -which(names(df) == "id")], 1, function(row) all(is.na(row))), ]
df <- pivot_longer(df, col=-id, values_to="resp", names_to="item")

save(df, file="CHEXI_Lin_2019.Rdata")
write.csv(df, "CHEXI_Lin_2019.csv", row.names=FALSE)
