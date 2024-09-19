# Paper: https://osf.io/h6vj4/
# Data: https://osf.io/h6vj4/
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("CBI Data 2080 Cases.csv")
df <- df[, paste0("cbi", 1:28)]
df$id <- seq_len(nrow(df))
df <- pivot_longer(df, cols=-id, names_to = "item", values_to = "resp")

save(df, file="CBI_Rodriguez_2021.Rdata")
write.csv(df, "CBI_Rodriguez_2021.csv", row.names=FALSE)
