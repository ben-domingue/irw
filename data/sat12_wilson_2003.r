# Data: https://philchalmers.github.io/mirt/html/SAT12.html
# Paper: 
library('mirt')
library(haven)
library(dplyr)
library(tidyr)

data(SAT12)
SAT12$id <- seq_len(nrow(SAT12))
SAT12 <- pivot_longer(SAT12, cols=-id, names_to="item", values_to="resp")
SAT12$resp <- ifelse(SAT12$resp == 8, NA, SAT12$resp)

save(SAT12, file="sat12_wilson_2003.rdata")
write.csv(SAT12, "sat12_wilson_2003.csv", row.names=FALSE)