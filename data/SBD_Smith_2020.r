# Paper: https://www.sciencedirect.com/science/article/pii/S0165032719302046
# Data: https://osf.io/c4v7g/
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)

df <- read.table("bpses_pre_for_factor.dat", header = TRUE, sep = ",", stringsAsFactors = FALSE)
colnames(df) <- paste0("MBDS", 1:22)
df$id <- seq_len(nrow(df))
df <- pivot_longer(df, cols=-id, values_to = "resp", names_to = "item")
df$resp[df$resp == 999] <- NA

save(df, file="SBD_Smith_2020.Rdata")
write.csv(df, "SBD_Smith_2020.csv", row.names=FALSE)

