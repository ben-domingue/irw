# Paper: https://osf.io/preprints/psyarxiv/rgy4a
# Data: https://osf.io/rxb5y/
library(dplyr)
library(tidyr)
library(haven)

df <- read.csv("WMDSPLdata.csv")
df <- df[, paste0("WMDS", sprintf("%02d", 1:24))]
df$id <- seq_len(nrow(df))
df <- pivot_longer(df, c=-id, names_to="item", values_to="resp")

save(df, file="WMD_bartczuk_2023.Rdata")
write.csv(df, "WMD_bartczuk_2023.csv", row.names=FALSE)
