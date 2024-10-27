# Paper:
# Data: https://osf.io/zn4fd/

library(haven)
library(dplyr)
library(tidyr)

df <- read_sav("2021_sample 687.sav")
df[] <- lapply(df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})
df <- df |>
  mutate(id=row_number()) |>
  select(id, starts_with("OCDQ"), -ends_with("R"))

save(df, file="QCDQES_Oliveira_2022.Rdata")
write.csv(df, "QCDQES_Oliveira_2022.csv", row.names=FALSE)
